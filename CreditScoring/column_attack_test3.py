import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
import numpy as np

from pre_processing import pre_processing
from post_processing import postprocess_prediction

# Load model
booster = xgb.Booster()
booster.load_model("Model/model.json")

# Test function
def get_score(data):
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

def get_anomaly_score(prediction, dataframe):
    postproc_results = postprocess_prediction(
        booster=booster,
        entry_df=dataframe,
        predicted=prediction
    )
    
    anomaly_score = postproc_results.get("anomaly_score", 0)
    return anomaly_score


# Define value ranges
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

# Load data
df = pd.read_csv("Data/high_score_predictions.csv")

# Get original scores
scores = df.apply(lambda row: get_score(row), axis=1)
# TODO Also calculate anomaly scores for each point in variable anomaly_scores
manipulated_scores = pd.DataFrame(index=df.index, columns=value_ranges.keys())
improvements = {col: [] for col in value_ranges.keys()}

# Manipulate each feature
# TODO Only manipulate around the feature in a "radius" of +T, and -T is passed as a commandline param
for i, row in df.iterrows():
    original_score = scores[i]
    
    for column, values in value_ranges.items():
        min_score = original_score
        for val in values:
            modified_row = row.copy()
            modified_row[column] = val
            score = get_score(modified_row)
            if score < min_score:
                min_score = score
        manipulated_scores.loc[i, column] = min_score
        
        # Record improvements
        if min_score < original_score:
            improvement = original_score - min_score
            improvements[column].append(improvement)
        
        # TODO Once optimal score in Range has been found (lowest score), calculate anomaly score of the manipuated point
        
# TODO I need a second plot for increase of anomaly score for each feature

# Also print average improvement and std deviation
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
