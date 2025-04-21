import pandas as pd
import numpy as np

# Number of random data points to generate
num_samples = 100

# Generate the data
data = {
    'SeriousDlqin2yrs': np.random.randint(0, 1, size=num_samples),
    'RevolvingUtilizationOfUnsecuredLines': np.random.uniform(0, 1, size=num_samples),
    'age': np.random.randint(0, 300, size=num_samples),
    'NumberOfTime30-59DaysPastDueNotWorse': np.random.randint(0, 6, size=num_samples),
    'DebtRatio': np.random.uniform(0, 1, size=num_samples),
    'MonthlyIncome': np.random.randint(0, 999999, size=num_samples),
    'NumberOfOpenCreditLinesAndLoans': np.random.randint(0, 100, size=num_samples),
    'NumberOfTimes90DaysLate': np.random.randint(0, 100, size=num_samples),
    'NumberRealEstateLoansOrLines': np.random.randint(0, 100, size=num_samples),
    'NumberOfTime60-89DaysPastDueNotWorse': np.random.randint(0, 100, size=num_samples),
    'NumberOfDependents': np.random.randint(0, 100, size=num_samples),
}

# Create the DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("random_credit_data.csv", index=False)

# Print sample
print(df.head())
