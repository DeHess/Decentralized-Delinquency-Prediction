import pandas as pd
import numpy as np

# Number of random data points to generate
num_samples = 1000

# Generate pure noise
data = {
    'SeriousDlqin2yrs': np.random.randint(0, 1, size=num_samples),
    'RevolvingUtilizationOfUnsecuredLines': np.random.uniform(0, 1, size=num_samples),
    'age': np.random.randint(0, 300, size=num_samples),
    'NumberOfTime30-59DaysPastDueNotWorse': np.random.randint(0, 6, size=num_samples),
    'DebtRatio': np.random.uniform(0, 1, size=num_samples),
    'MonthlyIncome': np.random.randint(0, 9999999, size=num_samples),
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

#using the following data point [0.01879812,51,0,0.53152876,6501,7,0,2,0,2]: 
# For each column make a csv. Each csv should
# have between 50 to a 1000 entries: each entry should basically be the complete entry from above,
# except for the column were currently working on. The values in this column should fluctuate from min to max
# for every entry
# RevolvingUtilizationOfUnsecuredLines    0-1 (float, 100 entries)
# age: 10,11,12... 110 (100 entries)
# 'NumberOfTime30-59DaysPastDueNotWorse' 0-50 (50 entries)
# DebtRatio 0-1 ()float 100 entries
# Monthlyincome 0-1000000 (1000 entries)
# All remaining NumberOFTimeslate 0-50 (50 entries)
# NumberOfDependentens 0-20 (20 entries)


# Base data point
base_point = {
    'SeriousDlqin2yrs': 0,
    'RevolvingUtilizationOfUnsecuredLines': 0.01879812,
    'age': 51,
    'NumberOfTime30-59DaysPastDueNotWorse': 0,
    'DebtRatio': 0.53152876,
    'MonthlyIncome': 6501,
    'NumberOfOpenCreditLinesAndLoans': 7,
    'NumberOfTimes90DaysLate': 0,
    'NumberRealEstateLoansOrLines': 2,
    'NumberOfTime60-89DaysPastDueNotWorse': 0,
    'NumberOfDependents': 2,
}

def generate_varying_csv(column, values, filename):
    df = pd.DataFrame([base_point.copy() for _ in range(len(values))])
    df[column] = values
    df.to_csv(filename, index=False)

# Generate each file
generate_varying_csv('RevolvingUtilizationOfUnsecuredLines', np.linspace(0, 1, 100), 'vary_RevolvingUtilization.csv')
generate_varying_csv('age', np.arange(10, 110), 'vary_age.csv')
generate_varying_csv('NumberOfTime30-59DaysPastDueNotWorse', np.arange(0, 50), 'vary_30_59_days_late.csv')
generate_varying_csv('DebtRatio', np.linspace(0, 1, 100), 'vary_DebtRatio.csv')
generate_varying_csv('MonthlyIncome', np.linspace(0, 1_000_000, 1000, dtype=int), 'vary_MonthlyIncome.csv')
generate_varying_csv('NumberOfTimes90DaysLate', np.arange(0, 50), 'vary_90_days_late.csv')
generate_varying_csv('NumberOfTime60-89DaysPastDueNotWorse', np.arange(0, 50), 'vary_60_89_days_late.csv')
generate_varying_csv('NumberOfDependents', np.arange(0, 20), 'vary_Dependents.csv')
generate_varying_csv('NumberRealEstateLoansOrLines', np.arange(0, 50), 'vary_RealEstateLoansOrLines.csv')
generate_varying_csv('NumberOfOpenCreditLinesAndLoans', np.arange(0, 50), 'vary_OpenCreditLinesAndLoans.csv')