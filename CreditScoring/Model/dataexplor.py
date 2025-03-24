import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("Data/cs-training.csv")

# Basic statistics and missing value check
print(df.info())
print(df.isnull().sum())


