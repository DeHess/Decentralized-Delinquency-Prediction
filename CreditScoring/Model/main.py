import xgboost as xgb
import pandas as pd

# Load the data and remove the target column (if necessary)
data = pd.read_csv("Data/cs-test.csv")
data = data.drop("SeriousDlqin2yrs", axis=1)

# Select the first entry and convert to DMatrix
first_entry = data.iloc[0:1]
dmatrix_first = xgb.DMatrix(first_entry)

# Load the model
model = xgb.Booster()
model.load_model("model.json")

# 1. Print out the structure of each tree
tree_dumps = model.get_dump(with_stats=True)
for idx, tree in enumerate(tree_dumps):
    print(f"Tree {idx} structure:")
    print(tree)
    print("-" * 40)
