import numpy as np
import pandas as pd
import shap
from scipy.spatial.distance import mahalanobis
import xgboost as xgb

def postprocess_prediction(
    booster: xgb.Booster,
    entry_df: pd.DataFrame,
    prediction: float,
    data_path: str = "Data/cs-training2.csv",
    background_size: int = 200,
    background_tol: float = 0.1,
    random_state: int = 42
) -> dict:

    df = pd.read_csv(data_path)

    if "PredictedRisk" not in df.columns:
        raise ValueError("Column 'PredictedRisk' not found in dataset.")

    features = df.drop(["SeriousDlqin2yrs", "Id"], axis=1, errors="ignore").dropna()


    mask = np.abs(df["PredictedRisk"] - prediction) <= background_tol
    bg = features[mask]
    if len(bg) > background_size:
        bg = bg.sample(n=background_size, random_state=random_state)
        
    entry = entry_df[bg.columns]

    explainer = shap.TreeExplainer(booster, data=bg)
    shap_vals = explainer.shap_values(entry)

    instance_shap = shap_vals[0]
    base_value = explainer.expected_value

    def z_anomaly(inst, background_vals):
        m = background_vals.mean(axis=0)
        s = background_vals.std(axis=0) + 1e-8
        return np.mean(np.abs((inst - m) / s))

    bg_shap = explainer.shap_values(bg)
    z_score = z_anomaly(instance_shap, bg_shap)

    cov = np.cov(bg_shap, rowvar=False)
    inv_cov = np.linalg.inv(cov + 1e-8 * np.eye(cov.shape[0]))
    mean_shap = bg_shap.mean(axis=0)
    m_score = mahalanobis(instance_shap, mean_shap, inv_cov)

    return {
        "shap_values": instance_shap,
        "base_value": base_value,
        "anomaly_score_z": z_score,
        "anomaly_score_m": m_score,
        "anomaly_score": (z_score + m_score) / 2,
    }
