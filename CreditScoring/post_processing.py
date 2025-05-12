import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from scipy.spatial.distance import mahalanobis


def calculate_zscore_anomaly(instance, background):
    bg_means = np.mean(background, axis=0)
    bg_stds = np.std(background, axis=0) + 1e-8
    z_scores = (instance - bg_means) / bg_stds
    return np.mean(np.abs(z_scores))


def postprocess_prediction(
    booster,
    entry_df,
    predicted,
    data_path="Data/cs-training.csv",
    background_size=200,
    positive_class=0,
    random_state=42,
):
    
    exclude_features = [
        "NumberOfTime30-59DaysPastDueNotWorse",
        "NumberOfTime60-89DaysPastDueNotWorse",
        "NumberOfTimes90DaysLate",
    ]

    
    df = pd.read_csv(data_path)
    bg_data = df[df["SeriousDlqin2yrs"] == predicted]
    bg_data = bg_data.drop(["SeriousDlqin2yrs", "Id"], axis=1, errors="ignore")
    bg_data.dropna(axis=0, how='any', inplace=True)

    
    bg_data = bg_data.drop(columns=exclude_features, errors='ignore')

    
    background_data = bg_data.sample(n=background_size, random_state=random_state)
    entry_df = entry_df.drop(columns=exclude_features, errors='ignore')
    entry_df = entry_df[background_data.columns]

    
    explainer = shap.TreeExplainer(
        booster,
        data=background_data,
        feature_perturbation='interventional'
    )
    shap_values_all = explainer.shap_values(entry_df)

    
    if isinstance(shap_values_all, list):
        instance_shap = shap_values_all[positive_class][0]
        base_value = (
            explainer.expected_value[positive_class]
            if isinstance(explainer.expected_value, list)
            else explainer.expected_value
        )
        bg_shap_vals_all = explainer.shap_values(background_data)
        bg_shap_vals = (
            bg_shap_vals_all[positive_class]
            if isinstance(bg_shap_vals_all, list)
            else bg_shap_vals_all
        )
    else:
        instance_shap = shap_values_all[0]
        base_value = explainer.expected_value
        bg_shap_vals = explainer.shap_values(background_data)

    
    anomaly_score_z = calculate_zscore_anomaly(instance_shap, bg_shap_vals)

    cov_matrix = np.cov(bg_shap_vals, rowvar=False)
    reg = 1e-8 * np.eye(cov_matrix.shape[0])
    inv_cov_matrix = np.linalg.inv(cov_matrix + reg)
    mean_bg_shap = np.mean(bg_shap_vals, axis=0)
    anomaly_score_m = mahalanobis(instance_shap, mean_bg_shap, inv_cov_matrix)

    
    anomaly_score = (anomaly_score_z + anomaly_score_m) / 2

    
    abs_bg_shap_vals = np.abs(bg_shap_vals)
    mean_abs_shap = np.mean(abs_bg_shap_vals, axis=0)
    feature_names = background_data.columns.tolist()
    sorted_idx = np.argsort(mean_abs_shap)[::-1]
    global_importance_ranking = [
        (feature_names[i], mean_abs_shap[i]) for i in sorted_idx
    ]

    return {
        "shap_values": instance_shap,
        "base_value": base_value,
        "anomaly_score": anomaly_score,
        "anomaly_score_z": anomaly_score_z,
        "anomaly_score_m": anomaly_score_m,
        "global_importance_ranking": global_importance_ranking
    }
