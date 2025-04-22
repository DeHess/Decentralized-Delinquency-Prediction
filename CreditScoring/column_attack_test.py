import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np

# Import custom preprocessing and postprocessing
from pre_processing import pre_processing
from post_processing import postprocess_prediction

# Load the trained XGBoost booster model
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Define the test function
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
    
    outlier_flag = pre_processing(df)
    dmatrix = xgb.DMatrix(df)
    raw_score = booster.predict(dmatrix)[0]
    prediction = 1 if raw_score > 0.4 else 0

    postproc_results = postprocess_prediction(
        booster=booster,
        entry_df=df,
        predicted=prediction
    )
    
    anomaly_score = postproc_results.get("anomaly_score", 0)
    return raw_score, prediction, anomaly_score

# --- Plot 1: 30-59 Days Late ---
df_30_59 = pd.read_csv("vary_30_59_days_late.csv")
x_30_59 = []
raw_scores_30_59 = []

for _, row in df_30_59.iterrows():
    raw_score, _, _ = test(row)
    x_30_59.append(row['NumberOfTime30-59DaysPastDueNotWorse'])
    raw_scores_30_59.append(raw_score)

# --- Plot 2: 60-89 Days Late ---
df_60_89 = pd.read_csv("vary_60_89_days_late.csv")
x_60_89 = []
raw_scores_60_89 = []

for _, row in df_60_89.iterrows():
    raw_score, _, _ = test(row)
    x_60_89.append(row['NumberOfTime60-89DaysPastDueNotWorse'])
    raw_scores_60_89.append(raw_score)

# --- Plot 3: 90+ Days Late ---
df_90 = pd.read_csv("vary_90_days_late.csv")
x_90 = []
raw_scores_90 = []

for _, row in df_90.iterrows():
    raw_score, _, _ = test(row)
    x_90.append(row['NumberOfTimes90DaysLate'])
    raw_scores_90.append(raw_score)

# --- Plot 4: Age ---
df_age = pd.read_csv("vary_age.csv")
x_age = []
raw_scores_age = []

for _, row in df_age.iterrows():
    raw_score, _, _ = test(row)
    x_age.append(row['age'])
    raw_scores_age.append(raw_score)

# --- Visualization ---
plt.figure(figsize=(20, 5))

# Subplot 1: 30-59
plt.subplot(1, 4, 1)
plt.plot(x_30_59, raw_scores_30_59, marker='o', linestyle='-')
plt.xlabel('NumberOfTime30-59DaysPastDueNotWorse')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. 30-59 Days Late')
plt.grid(True)

# Subplot 2: 60-89
plt.subplot(1, 4, 2)
plt.plot(x_60_89, raw_scores_60_89, marker='o', color='orange', linestyle='-')
plt.xlabel('NumberOfTime60-89DaysPastDueNotWorse')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. 60-89 Days Late')
plt.grid(True)

# Subplot 3: 90+
plt.subplot(1, 4, 3)
plt.plot(x_90, raw_scores_90, marker='o', color='green', linestyle='-')
plt.xlabel('NumberOfTimes90DaysLate')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. 90+ Days Late')
plt.grid(True)

# Subplot 4: Age
plt.subplot(1, 4, 4)
plt.plot(x_age, raw_scores_age, marker='o', color='purple', linestyle='-')
plt.xlabel('Age')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. Age')
plt.grid(True)

plt.tight_layout()
plt.show()
