import pandas as pd
import matplotlib.pyplot as plt
from pre_processing import pre_processing
from post_processing import get_post_anomaly_score
import xgboost as xgb
import numpy as np

# Load booster
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Test function
def test(data):
    data_list = list(data)
    columns = [
        'RevolvingUtilizationOfUnsecuredLines', 'age', 
        'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 
        'MonthlyIncome','NumberOfOpenCreditLinesAndLoans', 
        'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines', 
        'NumberOfTime60-89DaysPastDueNotWorse','NumberOfDependents'
    ]
    
    df = pd.DataFrame([data_list], columns=columns)
    
    pre_processing(df)  # modifies df in-place
    dmatrix = xgb.DMatrix(df)
    raw_score = booster.predict(dmatrix)[0]
    prediction = 1 if raw_score > 0.4 else 0
    
    postproc_results = get_post_anomaly_score(
        booster=booster,
        entry_df=df,
        predicted=prediction
    )
    
    anomaly_score = postproc_results.get("anomaly_score", 0)
    return raw_score, prediction, anomaly_score

# Load dataset
df_data = pd.read_csv("random_credit_data.csv")

# Apply test function only to the first 100 entries
results = df_data.iloc[:100].apply(test, axis=1, result_type='expand')
results.columns = ["raw_score", "prediction", "anomaly_score"]

# Combine results with the first 100 rows of the original data
df_combined = df_data.iloc[:100].copy()
df_combined[results.columns] = results

# Extract anomaly scores
scores = df_combined["anomaly_score"].values

# Plotting 1D scatter of anomaly scores as x-values
plt.figure(figsize=(10, 2))
y_jitter = np.random.normal(0, 0.01, size=len(scores))  # small jitter to avoid overlap
plt.scatter(scores, y_jitter, color='black', s=20)
plt.yticks([])
plt.xlabel("Anomaly Score")
plt.title("1D Scatter of Anomaly Scores (First 100 Entries)")
plt.grid(True, axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
