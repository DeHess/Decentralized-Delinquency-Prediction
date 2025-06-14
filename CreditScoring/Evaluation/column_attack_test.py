import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np
import pickle
import os

from pre_processing import pre_processing
from post_processing import postprocess_prediction

import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)


booster = xgb.Booster()
booster.load_model("Model/model.json")


columns = [
    'age',
    'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio',
    'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans',
    'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
    'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
]

skip_columns = [
    'NumberOfTime30-59DaysPastDueNotWorse',
    'NumberOfTime60-89DaysPastDueNotWorse',
    'NumberOfTimes90DaysLate',
    'RevolvingUtilizationOfUnsecuredLines'
]


df = pd.read_csv("Data/high_score_predictions2.csv")


value_ranges = {
    'NumberOfTime30-59DaysPastDueNotWorse': list(range(21)),
    'NumberOfTime60-89DaysPastDueNotWorse': list(range(21)),
    'NumberOfTimes90DaysLate': list(range(21)),
    'age': list(range(18, 90)),
    'DebtRatio': [round(x * 0.05, 2) for x in range(21)],
    'RevolvingUtilizationOfUnsecuredLines': [round(x * 0.05, 2) for x in range(21)],
    'MonthlyIncome': list(range(0, 70000, 1000)),
    'NumberOfDependents': list(range(10)),
    'NumberOfOpenCreditLinesAndLoans': list(range(21)),
    'NumberRealEstateLoansOrLines': list(range(11)),
}

results_file = "Data/improvement_results.pkl"


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
        print("")
        print("Working on entry: ", idx)
        original_data = row.tolist()
        original_score = get_prediction_score(original_data)
        original_anomaly = get_anomaly_score(original_data, original_score)

        scores.append(original_score)
        anomaly_scores.append(original_anomaly)

        for col in columns:
           
            if col in skip_columns:
                continue

            print("Working on column: ", col)

            col_idx = columns.index(col)
            best_data = original_data.copy()
            best_score = original_score

            for val in value_ranges[col]:
                
                temp_data = original_data.copy()
                temp_data[col_idx] = val
                print("+", end="", flush=True)
                score = get_prediction_score(temp_data)
                if score < best_score:
                    best_score = score
                    best_data = temp_data.copy()

            best_anomaly = get_anomaly_score(best_data, best_score)

            score_improvement = original_score - best_score
            anomaly_change = best_anomaly - original_anomaly

            improvements[col].append(score_improvement)
            anomaly_score_changes[col].append(anomaly_change)

            print("")


    with open(results_file, "wb") as f:
        pickle.dump({
            "improvements": improvements,
            "anomaly_score_changes": anomaly_score_changes,
            "manipulated_scores": manipulated_scores,
            "scores": scores,
            "anomaly_scores": anomaly_scores
        }, f)
    print("Saved results to pickle.")


for col in improvements:
    x = anomaly_score_changes[col]
    y = improvements[col]
    

    left_count = sum(1 for val in x if val < 0)
    right_count = sum(1 for val in x if val >= 0)
    
    plt.figure()
    plt.scatter(x, y, s=10, alpha=0.6)
    plt.xlabel("Anomaly Score Change")
    plt.ylabel("Score Improvement")
    plt.title(f"{col}: Anomaly Change vs Score Improvement")
    plt.xlim(-2.5, 4)
    plt.ylim(0, 0.6)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=1)

    plt.text(-2.4, 0.55, f"< 0: {left_count}", color='red', ha='left', fontsize=10)
    plt.text(2.5, 0.55, f"≥ 0: {right_count}", color='red', ha='right', fontsize=10)

    plt.grid(True)
    plt.show()

    features = [col for col in columns if col not in skip_columns]


features = [col for col in columns if col not in skip_columns]


mean_improvements = [np.mean(improvements[feat]) for feat in features]


sorted_indices = np.argsort(mean_improvements)[::-1]
sorted_features = [features[i] for i in sorted_indices]
sorted_improvements = [mean_improvements[i] for i in sorted_indices]

plt.figure(figsize=(12, 6))
bars = plt.bar(sorted_features, sorted_improvements, color='skyblue', alpha=0.7)
plt.ylabel('Average Score Improvement')
plt.title('Average Score Improvement per Feature (Sorted Descending)')

plt.xticks(rotation=45, ha='right')  

plt.tight_layout()
plt.show()