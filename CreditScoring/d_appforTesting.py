import pandas as pd
import xgboost as xgb
from pre_processing import pre_processing
from post_processing import get_post_anomaly_score

booster = xgb.Booster()
booster.load_model("Model/model.json")

def test(data):
    data_list = list(data)
    columns = [
        'RevolvingUtilizationOfUnsecuredLines', 'age', 
        'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 
        'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 
        'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 
        'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents'
    ]
    
    df = pd.DataFrame(data_list, columns=columns)
    print("DataFrame:")
    print(df)
    

    outlier_flag = pre_processing(df)
    
            
    dmatrix = xgb.DMatrix(df)
    prediction = booster.predict(dmatrix)
    pred_score = prediction
    if prediction > 0.4:
        prediction = 1
        
    else: prediction = 0
    
    postproc_results = get_post_anomaly_score(
        booster=booster,
        entry_df=df,
        predicted =  prediction
    )
    
    anomaly_score = postproc_results["anomaly_score"]
    
    anomaly_threshold = 2
    
    if outlier_flag == 1 or anomaly_score > anomaly_threshold:
        manipulation_status = "Manipulated (Bad)"
    else:
        manipulation_status = "Not Manipulated (Good)"
    
    print("Raw Values:", data_list)
    print("Exact Prediction", pred_score)
    print("Prediction", prediction)
    print("Outlier Flag:", outlier_flag)
    print("Anomaly Score:", anomaly_score)
    print("Manipulation Status:", manipulation_status)
    #print("Post Processing Results:")
    #print(postproc_results)
    print("========")

#data = [
#    [0.964672555,40,3,0.382964747,13700,9,3,1,1,2]
#]

#test(data)