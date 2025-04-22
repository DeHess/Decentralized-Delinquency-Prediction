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
"""
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

# --- Plot 5: DebtRatio ---
df_debt = pd.read_csv("vary_DebtRatio.csv")
x_debt = []
raw_scores_debt = []

for _, row in df_debt.iterrows():
    raw_score, _, _ = test(row)
    x_debt.append(row['DebtRatio'])
    raw_scores_debt.append(raw_score)

# --- Plot 6: Dependents ---
df_dep = pd.read_csv("vary_Dependents.csv")
x_dep = df_dep['NumberOfDependents'].tolist()
y_dep = [test(row)[0] for _, row in df_dep.iterrows()]



# --- Plot 7: MonthlyIncome ---
df_income = pd.read_csv("vary_MonthlyIncome.csv")
x_income = df_income['MonthlyIncome'].tolist()
y_income = [test(row)[0] for _, row in df_income.iterrows()]



# --- Plot 8: OpenCreditLinesAndLoans ---
df_open_credit = pd.read_csv("vary_OpenCreditLinesAndLoans.csv")
x_open = df_open_credit['NumberOfOpenCreditLinesAndLoans'].tolist()
y_open = [test(row)[0] for _, row in df_open_credit.iterrows()]

# --- Plot 9: RealEstate ---
df_realestate = pd.read_csv("vary_RealEstateLoansOrLines.csv")
x_realestate = df_realestate['NumberRealEstateLoansOrLines'].tolist()
y_realestate = [test(row)[0] for _, row in df_realestate.iterrows()]
"""
# --- Plot 10: RevolvingUtilisation ---
df_util = pd.read_csv("vary_RevolvingUtilization.csv") 
x_util = df_util['RevolvingUtilizationOfUnsecuredLines'].tolist()
y_util = [test(row)[0] for _, row in df_util.iterrows()]

# --- Visualization ---
"""
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

#DebtRatio
plt.subplot(1, 5, 5)
plt.plot(x_debt, raw_scores_debt, marker='o', color='red', linestyle='-')
plt.xlabel('DebtRatio')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. DebtRatio')
plt.grid(True)

#dependents
plt.subplot(1, 6, 6)
plt.plot(x_dep, y_dep, marker='o', color='brown', linestyle='-')
plt.xlabel('Number of Dependents')
plt.ylabel('Raw Score')
plt.title('vs. Dependents')
plt.grid(True)

#Monthly Income
plt.subplot(1, 7, 7)
plt.plot(x_income, y_income, marker='o', color='teal', linestyle='-')
plt.xlabel('Monthly Income')
plt.title('vs. Monthly Income')
plt.grid(True)

# 8: Open Credit Lines & Loans
plt.subplot(1, 8, 8)
plt.plot(x_open, y_open, marker='o', color='navy', linestyle='-')
plt.xlabel('Open Credit Lines')
plt.title('vs. Open Credit Lines')
plt.grid(True)

# 9: Real Estate Loans
plt.subplot(1, 9, 9)
plt.plot(x_realestate, y_realestate, marker='o', color='darkgreen', linestyle='-')
plt.xlabel('Real Estate Loans')
plt.title('vs. Real Estate Loans')
plt.grid(True)

plt.subplot(1, 10, 10)
plt.plot(x_util, y_util, marker='o', color='gold')
plt.xlabel('Revolving Utilization')
plt.title('Utilization (0–1)')
plt.grid(True)

plt.tight_layout()
plt.show()
"""

plt.figure(figsize=(6, 5))
plt.plot(x_util, y_util, marker='o', color='red', linestyle='-')
plt.xlabel('Revolving Utilisation')
plt.ylabel('Raw Score')
plt.title('Raw Score vs. Revolving Utilisation')
plt.grid(True)
plt.tight_layout()
plt.show()