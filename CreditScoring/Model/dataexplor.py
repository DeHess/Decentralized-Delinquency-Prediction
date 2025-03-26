import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("Data/cs-training.csv")

print(df.info())
print(df.isnull().sum())


