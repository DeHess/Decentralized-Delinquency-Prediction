from __future__ import annotations
from pathlib import Path
from typing import Union

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

model_path = "ae_artifacts/ae_model.h5"
scaler_path = "ae_artifacts/ae_scaler.pkl"
stats_path = "ae_artifacts/ae_residual_stats.npz"

threshold_z: float = 2.0
batch_size: int = 512

def pre_processing(
    df: pd.DataFrame,
) -> pd.DataFrame:
    
    model = tf.keras.models.load_model(model_path, compile=False)
    scaler = joblib.load(scaler_path)
    stats = np.load(stats_path, allow_pickle=True)

    mu = stats["mu"] 
    sigma = stats["sigma"]
    features = stats["features"].tolist()
    
    p95 = stats.get("thresh_p95")
    thresholds_pf = p95 if p95 is not None else None

    X = df[features].fillna(df[features].median())
    X_scaled = scaler.transform(X)
    
    recon = model.predict(X_scaled, batch_size=batch_size, verbose=0)
    resid = np.abs(recon - X_scaled)

    eps = 1e-8
    pos_dev = np.maximum(resid - mu, 0.0)
    z = pos_dev / (sigma + eps)

    
    idx = np.argmax(z, axis=1)
    max_z = z[np.arange(len(z)), idx]
    suspect = [features[i] for i in idx]

    if thresholds_pf is not None:
        thresh = thresholds_pf[idx]
    else:
        thresh = np.full_like(max_z, threshold_z)

    is_anomaly = max_z > thresh

    return pd.DataFrame(
        {
            "suspect_feature": suspect,
            "z_score": max_z,
            "threshold": thresh,
            "is_anomaly": is_anomaly,
        },
        index=df.index,
    )
