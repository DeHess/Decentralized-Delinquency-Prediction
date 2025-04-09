import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer
import xgboost as xgb

booster = xgb.Booster()
booster.load_model("model.json")

def calculate_anomaly_score(instance, background):
    bg_means = np.mean(background, axis=0)
    bg_stds = np.std(background, axis=0)
    epsilon = 1e-8
    z_scores = (instance - bg_means) / (bg_stds + epsilon)
    return np.mean(np.abs(z_scores))



def postprocess_prediction(
    entry_df,
    data_path="Data/cs-training.csv",
    background_size=100,
    positive_class=0,
    random_state=42,
    predicted = 1
):
    
    
    df = pd.read_csv(data_path)
    bg_data = df[df["SeriousDlqin2yrs"] == predicted]
    bg_data = bg_data.drop(["SeriousDlqin2yrs", "Id"], axis=1, errors="ignore")    
    bg_data.dropna(axis=0, how='any', inplace=True)

    background_data = bg_data.sample(n=background_size, random_state=random_state)
    entry_df = entry_df[background_data.columns]
    
    explainer = shap.TreeExplainer(booster, data=background_data, feature_perturbation='interventional')
    shap_values_all = explainer.shap_values(entry_df)



    if isinstance(shap_values_all, list):
        instance_shap = shap_values_all[positive_class][0]
        if isinstance(explainer.expected_value, list):
            base_value = explainer.expected_value[positive_class]
        else:
            base_value = explainer.expected_value
        bg_shap_vals_all = explainer.shap_values(background_data)
        if isinstance(bg_shap_vals_all, list):
            bg_shap_vals = bg_shap_vals_all[positive_class]
        else:
            bg_shap_vals = bg_shap_vals_all
    else:
        instance_shap = shap_values_all[0]
        base_value = explainer.expected_value
        bg_shap_vals = explainer.shap_values(background_data)

    anomaly_score = calculate_anomaly_score(instance_shap, bg_shap_vals)
    abs_bg_shap_vals = np.abs(bg_shap_vals)
    mean_abs_shap = np.mean(abs_bg_shap_vals, axis=0)
    feature_names = background_data.columns.tolist()
    sorted_idx = np.argsort(mean_abs_shap)[::-1]
    global_importance_ranking = [(feature_names[i], mean_abs_shap[i]) for i in sorted_idx]



    def predict_proba_booster(data_array):
        dmat = xgb.DMatrix(data_array, feature_names=background_data.columns.tolist())
        raw_pred = booster.predict(dmat)
        prob_class1 = raw_pred
        prob_class0 = 1 - prob_class1
        return np.column_stack([prob_class0, prob_class1])

    lime_explainer = LimeTabularExplainer(
        training_data=background_data.values,
        feature_names=background_data.columns.tolist(),
        discretize_continuous=True,
        random_state=random_state
    )
    lime_exp = lime_explainer.explain_instance(
        data_row=entry_df.iloc[0].values,
        predict_fn=predict_proba_booster,
        labels=(positive_class,)
    )

    return {
        "shap_values": instance_shap,
        "base_value": base_value,
        "anomaly_score": anomaly_score,
        "lime_explanation": lime_exp,
        "global_importance_ranking": global_importance_ranking
    }
