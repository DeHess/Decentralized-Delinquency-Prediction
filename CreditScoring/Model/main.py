import xgboost as xgb
import pandas as pd
import joblib
import numpy as np
import shap

scaler = joblib.load("outlier_scaler.pkl")
model_outlier = joblib.load("outlier_model.pkl")
model = xgb.Booster()
model.load_model("model.json")


data = pd.read_csv("../Data/cs-test.csv")
data = data.drop("SeriousDlqin2yrs" , axis=1)
data = data.drop("Id" , axis=1)
first_entry = data.iloc[0:1]
print(data.columns)
#print(first_entry)
#print(type(first_entry))
dmatrix_first = xgb.DMatrix(first_entry)

#

entry_np = first_entry.to_numpy()
entry_np = np.nan_to_num(entry_np, nan=0.0)
entry_scaled = scaler.transform(entry_np)
is_outlier = model_outlier.predict(entry_scaled)[0]
# 1 true 0 false
#print(f"This data is an outlier: {is_outlier}")


shaptrain = pd.read_csv("../Data/cs-test.csv")
shaptrain = shaptrain.drop("SeriousDlqin2yrs" , axis=1)
shaptrain = shaptrain.drop("Id" , axis=1)
X_shap = np.nan_to_num(shaptrain, nan=0.0)
X_shap_scaled = scaler.transform(X_shap)

background = X_shap_scaled[np.random.choice(X_shap_scaled.shape[0], 100, replace=False)]

def anomaly_score(x):
    return model_outlier.decision_function(x)


explainer = shap.KernelExplainer(anomaly_score, background)
shap_values = explainer.shap_values(entry_scaled)


#print("Anomaly score: ", anomaly_score(entry_scaled)[0])
#print(shap_values)

tree_dumps = model.get_dump(with_stats=True)

num_trees = len(tree_dumps)
"""
for i in range(num_trees):
    tree_pred = model.predict(dmatrix_first, iteration_range=(i, i+1))
    print(f"Prediction from tree {i}: {tree_pred}")
"""

