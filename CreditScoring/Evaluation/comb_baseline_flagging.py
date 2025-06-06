import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb

from post_processing import postprocess_prediction
from pre_processing import pre_processing          


output_dir = "combined_score_Flagging"
os.makedirs(output_dir, exist_ok=True)


df = pd.read_csv('Data/eval.csv')
y_true = df['SeriousDlqin2yrs']
X = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)
means = X.mean()
X = X.fillna(means)

booster = xgb.Booster()
booster.load_model('Model/model.json')

def extract_scalar(val):
    """Ensures extraction of scalar from DataFrame/Series/list/array."""
    if isinstance(val, (pd.DataFrame, pd.Series, list, np.ndarray)):
        if hasattr(val, 'values'):
            val = val.values
        return float(val[0])
    return float(val)

results = []
for idx, row in X.iterrows():
    print(idx)
    row_df = pd.DataFrame([row])

    pre_result = pre_processing(row_df)
    pre_z = float(pre_result["z_score"].iloc[0])

    post_result = postprocess_prediction(row_df)
    post_anom = float(post_result["anomaly_score"])

    dmat = xgb.DMatrix([row.values], feature_names=X.columns.tolist())
    pred_prob = booster.predict(dmat)[0]

    combined_score = (pre_z + post_anom) / 2

    results.append({
        "true_label": y_true.iloc[idx],
        "pred_proba": pred_prob,
        "pre_score": pre_z,
        "post_score": post_anom,
        "combined_score": combined_score
    })

anomaly_df = pd.DataFrame(results)

def categorize_flag(row):
    y = row["true_label"]
    p = row["pred_proba"]
    if y == 0:
        if p <= 0.2:
            return "not flagged"
        elif p <= 0.5:
            return "review"
        else:
            return "potential manipulation"
    else:
        if p >= 0.8:
            return "not flagged"
        elif p >= 0.5:
            return "review"
        else:
            return "potential manipulation"

anomaly_df["flag_category"] = anomaly_df.apply(categorize_flag, axis=1)


grouped = (
    anomaly_df
    .groupby(["true_label", "flag_category"])["combined_score"]
    .mean()
    .unstack(0)
    .round(3)
)
grouped.to_csv(f"{output_dir}/avg_combined_score_by_flag.csv")
print("\nAverage combined score by flag category and class:")
print(grouped)


grouped.plot(kind="bar", figsize=(7, 4))
plt.title("Average Combined Anomaly Score by Flagging Category")
plt.ylabel("Combined Score (Pre + Post) / 2")
plt.xlabel("Flag Category")
plt.legend(title="Class (True Label)")
plt.tight_layout()
plt.savefig(f"{output_dir}/avg_combined_score_by_flag.png")
plt.close()

print(f"📁 Results saved in: {output_dir}/")
