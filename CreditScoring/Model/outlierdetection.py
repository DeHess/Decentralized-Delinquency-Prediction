import joblib
from sklearn.preprocessing import StandardScaler
from pyod.models.iforest import IForest  
import numpy as np
import pandas as pd


traindata = pd.read_csv("Data/cs-training.csv")
traindata = traindata.drop("Id", axis=1)
X_train = traindata.drop("SeriousDlqin2yrs", axis=1)

X_train = np.nan_to_num(X_train, nan=0.0)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = IForest(contamination=0.05, random_state=42)
model.fit(X_train_scaled)

joblib.dump(model, "outlier_model.pkl")
joblib.dump(scaler, "outlier_scaler.pkl")

