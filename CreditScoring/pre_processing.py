import pandas as pd
import joblib
import numpy as np

scaler = joblib.load("outlier_scaler.pkl")
model_outlier = joblib.load("outlier_model.pkl")


def pre_processing(datapoint):
    datapoint = datapoint.to_numpy()
    datapoint_np = np.nan_to_num(datapoint, nan=0.0)
    datapoint_scaled = scaler.transform(datapoint_np)
    is_outlier = model_outlier.predict(datapoint_scaled)[0]
    1 if is_outlier == 1 else 0

