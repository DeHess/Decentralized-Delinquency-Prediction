import pandas as pd
import joblib
import numpy as np

scaler = joblib.load("Model/outlier_scaler.pkl")
model_outlier = joblib.load("Model/outlier_model.pkl")


def pre_processing(datapoint):
    datapoint = datapoint.to_numpy()
    datapoint_np = np.nan_to_num(datapoint, nan=0.0)
    datapoint_scaled = scaler.transform(datapoint_np)
    return model_outlier.predict(datapoint_scaled)[0]
    

