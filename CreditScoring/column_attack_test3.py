import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np

from pre_processing import pre_processing
from post_processing import postprocess_prediction

booster = xgb.Booster()
booster.load_model("Model/model.json")

def get_prediction_score(data):
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

def get_scores(data):
    score = get_prediction_score(data)
    prediction = 1 if score > 0.4 else 0
    postproc_results = postprocess_prediction(
        booster=booster,
        entry_df=df,
        predicted=prediction
    )
    anomaly_score = postproc_results.get("anomaly_score", 0)

    return score, anomaly_score

def get_values_around(val, radius, min_val, max_val, step=1):
    values = list(range(max(val - radius, min_val), min(val + radius + 1, max_val + 1), step))
    return values

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

df = pd.read_csv("Data/high_score_predictions.csv")

results = df.apply(lambda row: get_scores(row), axis=1)
scores = results.apply(lambda x: x[0])       
anomaly_scores = results.apply(lambda x: x[1])  

manipulated_scores = pd.DataFrame(index=df.index, columns=value_ranges.keys())
improvements = {col: [] for col in value_ranges.keys()}

for i, row in df.iterrows():
    original_score = scores[i]
    # TODO instead of going through ranges 0-X, test in a 5% range around the datapoint in 1% intervals
    for column, values in value_ranges.items():
        min_score = original_score
        for val in values:
            modified_row = row.copy()
            modified_row[column] = val
            score = get_prediction_score(modified_row)
            
            if score < min_score:
                min_score = score
        manipulated_scores.loc[i, column] = min_score
        
        if min_score < original_score:
            improvement = original_score - min_score
            improvements[column].append(improvement)
    


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

feature_names = []
avg_improvement_list = []
std_dev_list = []

for column in improvements:
    if improvements[column]:
        feature_names.append(column)
        avg_improvement_list.append(np.mean(improvements[column]))
        std_dev_list.append(np.std(improvements[column]))

# Sort by avg improvement descending
sorted_indices = np.argsort(avg_improvement_list)[::-1]
feature_names_sorted = [feature_names[i] for i in sorted_indices]
avg_improvement_sorted = [avg_improvement_list[i] for i in sorted_indices]
std_dev_sorted = [std_dev_list[i] for i in sorted_indices]

# Plot bar chart
plt.figure(figsize=(12, 7))
plt.bar(feature_names_sorted, avg_improvement_sorted, yerr=std_dev_sorted, capsize=5, color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.ylabel("Average Score Improvement")
plt.title("Average Score Improvement by Feature (with Std Deviation)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
