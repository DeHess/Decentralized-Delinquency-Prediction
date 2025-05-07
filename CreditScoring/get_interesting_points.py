import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np

from pre_processing import pre_processing
from post_processing import postprocess_prediction

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
    
    df = pd.DataFrame([data_list], columns=columns)
    dmatrix = xgb.DMatrix(df)
    score = booster.predict(dmatrix)[0]
    return score

# Load the original CSV
df = pd.read_csv("Data/cs-test2.csv")

# Drop unwanted columns
df = df.drop(columns=["Id", "SeriousDlqin2yrs"])

# Filter out rows with RevolvingUtilizationOfUnsecuredLines > 1.0
df = df[df["RevolvingUtilizationOfUnsecuredLines"] <= 1.0]

# Store qualifying entries
accepted_entries = []

# Iterate through filtered rows
for _, row in df.iterrows():
    data = row.tolist()
    score = test(data)

    if score > 0.3:
        accepted_entries.append(row)

    if len(accepted_entries) == 500:
        break

# Write to new CSV
pd.DataFrame(accepted_entries).to_csv("accepted_entries.csv", index=False)