import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np
import pickle
import os

from pre_processing import pre_processing
from post_processing import postprocess_prediction

# Load the model
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Column names
columns = [
    'RevolvingUtilizationOfUnsecuredLines', 'age',
    'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio',
    'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans',
    'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
    'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
]

skip_columns = [
    'NumberOfTime30-59DaysPastDueNotWorse',
    'NumberOfTime60-89DaysPastDueNotWorse',
    'NumberOfTimes90DaysLate'
]

# Load data
df = pd.read_csv("Data/high_score_predictions2.csv")

# Value ranges for features
value_ranges = {
    'NumberOfTime30-59DaysPastDueNotWorse': list(range(21)),
    'NumberOfTime60-89DaysPastDueNotWorse': list(range(21)),
    'NumberOfTimes90DaysLate': list(range(21)),
    'age': list(range(18, 70)),
    'DebtRatio': [round(x * 0.05, 2) for x in range(21)],
    'RevolvingUtilizationOfUnsecuredLines': [round(x * 0.05, 2) for x in range(21)],
    'MonthlyIncome': list(range(0, 70000, 1000)),
    'NumberOfDependents': list(range(10)),
    'NumberOfOpenCreditLinesAndLoans': list(range(21)),
    'NumberRealEstateLoansOrLines': list(range(11)),
}

results_file = "Data/improvement_results5.pkl"

# Define helper functions
def get_prediction_score(data):
    dmatrix = xgb.DMatrix(pd.DataFrame([data], columns=columns))
    return booster.predict(dmatrix)[0]

def get_anomaly_score(data, pred_score):
    prediction = 1 if pred_score > 0.4 else 0
    df_entry = pd.DataFrame([list(data)], columns=columns)
    postproc_results = postprocess_prediction(booster, df_entry, predicted=prediction)
    post_anomaly_score = postproc_results.get("anomaly_score", 0)
    preproc_results = pre_processing(df_entry)
    pre_anomaly_score = preproc_results.get("z_score").values[0]
    return (post_anomaly_score + pre_anomaly_score) / 2

# Load if exists
if os.path.exists(results_file):
    with open(results_file, "rb") as f:
        saved_data = pickle.load(f)
    improvements = saved_data['improvements']
    anomaly_score_changes = saved_data['anomaly_score_changes']
    manipulated_scores = saved_data['manipulated_scores']
    scores = saved_data['scores']
    anomaly_scores = saved_data['anomaly_scores']
    print("Loaded previous results.")
else:
    improvements = {col: [] for col in columns if col not in skip_columns}
    anomaly_score_changes = {col: [] for col in columns if col not in skip_columns}
    manipulated_scores = []
    scores = []
    anomaly_scores = []

    for idx, row in df.iterrows():
        original_data = row.tolist()
        original_score = get_prediction_score(original_data)
        original_anomaly = get_anomaly_score(original_data, original_score)

        scores.append(original_score)
        anomaly_scores.append(original_anomaly)

        for col in columns:
            if col in skip_columns:
                continue

            col_idx = columns.index(col)
            best_data = original_data.copy()
            best_score = original_score

            for val in value_ranges[col]:
                temp_data = original_data.copy()
                temp_data[col_idx] = val
                score = get_prediction_score(temp_data)
                if score < best_score:
                    best_score = score
                    best_data = temp_data.copy()

            best_anomaly = get_anomaly_score(best_data, best_score)

            score_improvement = original_score - best_score
            anomaly_change = best_anomaly - original_anomaly

            improvements[col].append(score_improvement)
            anomaly_score_changes[col].append(anomaly_change)

            print(f"Processed row {idx}, feature '{col}'")

    with open(results_file, "wb") as f:
        pickle.dump({
            "improvements": improvements,
            "anomaly_score_changes": anomaly_score_changes,
            "manipulated_scores": manipulated_scores,
            "scores": scores,
            "anomaly_scores": anomaly_scores
        }, f)
    print("Saved results to pickle.")

# Plot
for col in improvements:
    x = improvements[col]
    y = anomaly_score_changes[col]
    plt.figure()
    plt.scatter(x, y, alpha=0.6)
    plt.xlabel("Score Improvement")
    plt.ylabel("Anomaly Score Change")
    plt.title(f"{col}: Score Improvement vs Anomaly Change")
    plt.grid(True)
    plt.show()
