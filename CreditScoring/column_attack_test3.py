import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np
import pickle
import os
from scipy.stats import linregress

from pre_processing import pre_processing
from post_processing import postprocess_prediction

# Configuration
PERCENTAGE_RANGE = 0.50  # 50% range
RECALCULATE = True  # Set to True to re-run the full loop and overwrite cached results
RESULTS_PATH = "Data/score_analysis_results.pkl"

# Load the model
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Prediction functions
def get_prediction_score(data):
    data_list = list(data)
    columns = [
        'RevolvingUtilizationOfUnsecuredLines', 'age',
        'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio',
        'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
    ]
    df = pd.DataFrame([data_list], columns=columns)
    dmatrix = xgb.DMatrix(df)
    score = booster.predict(dmatrix)[0]
    return score

def get_scores(data):
    score = get_prediction_score(data)
    prediction = 1 if score > 0.4 else 0
    postproc_results = postprocess_prediction(
        booster=booster,
        entry_df=pd.DataFrame([data]),  # Pass row as DataFrame
        predicted=prediction
    )
    anomaly_score = postproc_results.get("anomaly_score", 0)
    return score, anomaly_score

# Value ranges for features
value_ranges = {
    'NumberOfTime30-59DaysPastDueNotWorse': list(range(21)),
    'NumberOfTime60-89DaysPastDueNotWorse': list(range(21)),
    'NumberOfTimes90DaysLate': list(range(21)),
    'age': list(range(18, 101)),
    'DebtRatio': [round(x * 0.05, 2) for x in range(21)],
    'RevolvingUtilizationOfUnsecuredLines': [round(x * 0.05, 2) for x in range(21)],
    'MonthlyIncome': list(range(0, 100001, 1000)),
    'NumberOfDependents': list(range(21)),
    'NumberOfOpenCreditLinesAndLoans': list(range(31)),
    'NumberRealEstateLoansOrLines': list(range(11)),
}

# Load dataset
df = pd.read_csv("Data/high_score_predictions.csv")

# Get original scores
print("Calculating Original Scores")
results = df.apply(get_scores, axis=1)
scores = results.apply(lambda x: x[0])
anomaly_scores = results.apply(lambda x: x[1])

# Main loop (cached)
if RECALCULATE or not os.path.exists(RESULTS_PATH):
    manipulated_scores = pd.DataFrame(index=df.index, columns=value_ranges.keys())
    improvements = {col: [] for col in value_ranges.keys()}
    anomaly_score_changes = {col: [] for col in value_ranges.keys()}

    print("Original Scores Done, Beginning Loop")
    for i, row in df.iterrows():
        original_score = scores[i]
        original_anomaly_score = anomaly_scores[i]
        print("Working on Entry:", i)
        for column, _ in value_ranges.items():
            original_value = row[column]
            lower_bound = max(original_value * (1 - PERCENTAGE_RANGE), 0)
            upper_bound = original_value * (1 + PERCENTAGE_RANGE)
            values_to_test = np.linspace(lower_bound, upper_bound, num=21)

            min_score = original_score
            min_anomaly_score = original_anomaly_score
            for val in values_to_test:
                modified_row = row.copy()
                modified_row[column] = val
                score = get_prediction_score(modified_row)
                anomaly_score = get_scores(modified_row)[1]

                if score < min_score:
                    min_score = score
                    min_anomaly_score = anomaly_score

            manipulated_scores.loc[i, column] = min_score
            if min_score < original_score:
                improvement = original_score - min_score
                improvements[column].append(improvement)
                anomaly_score_change = min_anomaly_score - original_anomaly_score
                anomaly_score_changes[column].append(anomaly_score_change)

    # Save results
    with open(RESULTS_PATH, "wb") as f:
        pickle.dump({
            "manipulated_scores": manipulated_scores,
            "improvements": improvements,
            "anomaly_score_changes": anomaly_score_changes
        }, f)

else:
    print("Loading previously saved results...")
    with open(RESULTS_PATH, "rb") as f:
        saved = pickle.load(f)
        manipulated_scores = saved["manipulated_scores"]
        improvements = saved["improvements"]
        anomaly_score_changes = saved["anomaly_score_changes"]


for column in value_ranges.keys():
    x = improvements[column]
    y = anomaly_score_changes[column]

    if x and y and len(x) == len(y):
        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, alpha=0.6, color='teal', label="Data Points")

        # Linear regression
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        x_vals = np.array(x)
        y_vals = intercept + slope * x_vals
        plt.plot(x_vals, y_vals, color='darkred', label=f"y={slope:.2f}x+{intercept:.2f}\n$R^2$={r_value**2:.2f}")

        plt.title(f"Feature: {column}")
        plt.xlabel("Score Improvement")
        plt.ylabel("Anomaly Score Change")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()
    else:
        print(f"Skipping {column} — insufficient data.")

# Tidy layout
plt.tight_layout()
plt.show()


"""
# Print improvement stats
for column in value_ranges:
    if improvements[column]:
        avg_improvement = np.mean(improvements[column])
        std_improvement = np.std(improvements[column])
        print(f"Feature: {column}")
        print(f"  Average Improvement: {avg_improvement:.6f}")
        print(f"  Std Deviation of Improvement: {std_improvement:.6f}")
    else:
        print(f"Feature: {column}")
        print("  No improvement possible.")

# Prepare bar plot data
feature_names = []
avg_improvement_list = []
std_dev_list = []

for column in improvements:
    if improvements[column]:
        feature_names.append(column)
        avg_improvement_list.append(np.mean(improvements[column]))
        std_dev_list.append(np.std(improvements[column]))

# Sort data by average improvement
sorted_indices = np.argsort(avg_improvement_list)[::-1]
feature_names_sorted = [feature_names[i] for i in sorted_indices]
avg_improvement_sorted = [avg_improvement_list[i] for i in sorted_indices]
std_dev_sorted = [std_dev_list[i] for i in sorted_indices]

# Bar plot: Average improvement by feature
plt.figure(figsize=(12, 7))
plt.bar(feature_names_sorted, avg_improvement_sorted, yerr=std_dev_sorted, capsize=5, color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.ylabel("Average Score Improvement")
plt.title("Average Score Improvement by Feature (with Std Deviation)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Prepare scatter plot data
avg_anomaly_changes = []
for column in anomaly_score_changes:
    if anomaly_score_changes[column]:
        avg_anomaly_changes.append(np.mean(anomaly_score_changes[column]))
    else:
        avg_anomaly_changes.append(0)

avg_anomaly_changes_sorted = [avg_anomaly_changes[feature_names.index(col)] for col in feature_names_sorted]

# Scatter plot: Score improvement vs anomaly score change
plt.figure(figsize=(12, 7))
plt.scatter(avg_improvement_sorted, avg_anomaly_changes_sorted, color='purple', alpha=0.7)
for i, txt in enumerate(feature_names_sorted):
    plt.annotate(txt, (avg_improvement_sorted[i], avg_anomaly_changes_sorted[i]), fontsize=8, alpha=0.7)
plt.xlabel("Average Score Improvement")
plt.ylabel("Average Anomaly Score Change")
plt.title("Score Improvement vs Anomaly Score Change")
plt.grid(linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
"""