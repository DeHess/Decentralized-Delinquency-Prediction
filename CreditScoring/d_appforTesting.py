import pandas as pd
import xgboost as xgb
from pre_processing import pre_processing
from post_processing import postprocess_prediction

booster = xgb.Booster()
booster.load_model("model.json")

def listen_for_incoming_requests(data):
    
    data_list = list(data)
    columns = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents']
    
    df = pd.DataFrame(data_list, columns=columns)
    print(df)
    
    # Preprocessing
    is_outlier = pre_processing(df)


    ##Post Processing
    postproc_results = postprocess_prediction(
                booster=booster,
                entry_df=df,
                prediction = 1 #Prediction aus dem Model TODO: Das die Model prediction genommen wird und nicht 1 
            )
    
    print(postproc_results)

    print("Values:", data_list)
    print("Outlier?:", is_outlier)
    print("========")
    

if __name__ == "__main__":
    data = [
        [0.983824929, 55, 0, 0.064116496, 4600, 2, 1, 0, 0, 6]
    ]
    listen_for_incoming_requests(data)