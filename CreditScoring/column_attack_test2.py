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

# Get scores for each row using the test function
scores = df.apply(lambda row: test(row), axis=1)

manipulated_scores = pd.DataFrame(index=df.index, columns=value_ranges.keys())

# To store improvements
improvements = {col: [] for col in value_ranges.keys()}

for i, row in df.iterrows():
    original_score = scores[i]
    
    for column, values in value_ranges.items():
        min_score = original_score
        for val in values:
            modified_row = row.copy()
            modified_row[column] = val
            score = test(modified_row)
            if score < min_score:
                min_score = score
        manipulated_scores.loc[i, column] = min_score
        
        # Only consider actual improvements
        if min_score < original_score:
            improvement = original_score - min_score
            improvements[column].append(improvement)

# Calculate and print average and std deviation for each feature
for column in value_ranges:
    if improvements[column]:  # If there was any improvement
        avg_improvement = np.mean(improvements[column])
        std_improvement = np.std(improvements[column])
        print(f"Feature: {column}")
        print(f"  Average Improvement: {avg_improvement:.6f}")
        print(f"  Std Deviation of Improvement: {std_improvement:.6f}")
    else:
        print(f"Feature: {column}")
        print("  No improvement possible.")

# Now plot original vs manipulated scores
for column in value_ranges:
    plt.figure(figsize=(10, 6))
    
    # Create a sorted index based on original scores
    sorted_indices = np.argsort(scores)

    # Sort original and manipulated scores
    sorted_original_scores = np.array(scores)[sorted_indices]
    sorted_manipulated_scores = manipulated_scores[column].astype(float).values[sorted_indices]

    # Plot
    plt.scatter(range(len(df)), sorted_original_scores, color='blue', alpha=0.6, label='Original')
    plt.scatter(range(len(df)), sorted_manipulated_scores, color='red', alpha=0.6, label='Manipulated')
    plt.xlabel("Data Point Index (sorted by original score)")
    plt.ylabel("Score")
    plt.title(f"Effect of Manipulating {column} on Score")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    input("Press Enter to see the next plot...")
