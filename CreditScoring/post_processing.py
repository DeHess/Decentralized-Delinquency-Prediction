import pandas as pd
import numpy as np
import shap


def anomaly_score(model, entry):
    
    shaptrain = pd.read_csv("Data/cs-training.csv")
    shaptrain = shaptrain.drop(["SeriousDlqin2yrs", "Id"], axis=1)
    background = shaptrain.iloc[np.random.choice(shaptrain.shape[0], 100, replace=False)]


    explainer = shap.TreeExplainer(model, data=background)
    shap_values = explainer.shap_values(entry)
    
    def calculate_anomaly_score(instance_shap, background_shap_values):
        bg_means = np.mean(background_shap_values, axis=0)
        bg_stds = np.std(background_shap_values, axis=0)
        epsilon = 1e-8
        z_scores = (instance_shap - bg_means) / (bg_stds + epsilon)
        abs_z_scores = np.abs(z_scores)
        anomaly_score = np.mean(abs_z_scores)
        return anomaly_score

    instance_shap = np.array(shap_values[0])
    background_shap_values = np.array(explainer.shap_values(background))
 

    anomaly_score = calculate_anomaly_score(instance_shap, background_shap_values)
    return anomaly_score
