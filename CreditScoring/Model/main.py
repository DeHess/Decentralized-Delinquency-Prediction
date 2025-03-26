import xgboost as xgb
import pandas as pd

# Load the data and remove the target column (if necessary)
data = pd.read_csv("Data/cs-test.csv")
print(data.iloc[0:1])
data = data.drop("SeriousDlqin2yrs", axis=1)
with open("Data/cs-test.csv", "r") as f:
    print(f.readline())  # Print the header
    print(f.readline())  # Print the first data row

# Load the model
model = xgb.Booster()
model.load_model("model.json")

# Select the first 100 entries
first_100_entries = data.iloc[:100]

for i in range(100):
    entry=data.iloc[i:i+1]


"""

# 1. Print out the structure of each tree
tree_dumps = model.get_dump(with_stats=True)
for idx, tree in enumerate(tree_dumps):
    print(f"Tree {idx} structure:")
    print(tree)
    print("-" * 40)
"""