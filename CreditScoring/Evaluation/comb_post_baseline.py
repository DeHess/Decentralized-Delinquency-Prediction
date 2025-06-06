import os
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb

from post_processing import postprocess_prediction


output_dir = "postprocessor_shap_eval_New2"
os.makedirs(output_dir, exist_ok=True)

booster = xgb.Booster()
booster.load_model("Model/model.json")

df = pd.read_csv('Data/eval.csv')
y_true = df['SeriousDlqin2yrs']
X = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)

means = X.mean()
X = X.fillna(means)


results = []
for idx, row in X.iterrows():
    print(idx)
    dmat = xgb.DMatrix([row.values], feature_names=X.columns.tolist())
    pred_prob = booster.predict(dmat)[0]
    pred = int(pred_prob > 0.5)
    post_result = postprocess_prediction(booster, pd.DataFrame([row]), predicted=pred)
    results.append({
        "anomaly_score": post_result["anomaly_score"],
        "anomaly_score_z": post_result["anomaly_score_z"],
        "anomaly_score_m": post_result["anomaly_score_m"],
        "true_label": y_true.iloc[idx],
        "predicted_class": pred,
        "predicted_probability": pred_prob,
    })

anomaly_df = pd.DataFrame(results)


anomaly_df.to_csv(f"{output_dir}/shap_postprocessed.csv", index=False)


for col in ['anomaly_score', 'anomaly_score_z', 'anomaly_score_m']:
    print(f"\nSummary of {col} (All):")
    print(anomaly_df[col].describe())
    anomaly_df[col].describe().to_csv(f"{output_dir}/{col}_summary_all.csv")


for col in ['anomaly_score', 'anomaly_score_z', 'anomaly_score_m']:
    print(f"\nSummary of {col} by Class:")
    summary_by_class = anomaly_df.groupby("true_label")[col].describe()
    print(summary_by_class)
    summary_by_class.to_csv(f"{output_dir}/{col}_summary_by_class.csv")

for col in ['anomaly_score_z', 'anomaly_score_m']:
    plt.figure(figsize=(6, 4))
    for cls in [0, 1]:
        plt.hist(anomaly_df[col][anomaly_df['true_label'] == cls], bins=50, alpha=0.7, label=f"Class {cls}")
    plt.xlabel(col.replace('_', ' ').title())
    plt.ylabel('Count')
    plt.title(f"Distribution of {col.replace('_', ' ').title()} by Class")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{col}_histogram_by_class.png")
    plt.close()

plt.figure(figsize=(6, 4))
plt.hist(anomaly_df['anomaly_score_z'], bins=50, alpha=0.6, label='Z-Score')
plt.hist(anomaly_df['anomaly_score_m'], bins=50, alpha=0.6, label='M-Score')
plt.xlabel('Score Value')
plt.ylabel('Count')
plt.title('Combined Histogram of Z-Score and M-Score')
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/combined_z_m_histogram.png")
plt.close()


plt.figure(figsize=(7, 4))
plt.hist(anomaly_df['anomaly_score'], bins=50, alpha=0.6, label='anomaly_score')
plt.hist(anomaly_df['anomaly_score_z'], bins=50, alpha=0.6, label='anomaly_score_z')
plt.hist(anomaly_df['anomaly_score_m'], bins=50, alpha=0.6, label='anomaly_score_m')
plt.xlabel('Score Value')
plt.ylabel('Frequency')
plt.title('Histogram of Anomaly Scores')
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/anomaly_score_combined_histogram.png")
plt.close()


plt.figure(figsize=(6, 6))
plt.scatter(anomaly_df['anomaly_score_z'], anomaly_df['anomaly_score_m'],
            c=anomaly_df['true_label'], alpha=0.6, cmap='coolwarm')
plt.xlabel('Z-Score')
plt.ylabel('M-Score')
plt.title('Scatter of Z-Score vs M-Score (colored by True Label)')
plt.tight_layout()
plt.savefig(f"{output_dir}/z_vs_m_scatter.png")
plt.close()


print(f"📁 All results saved to: {output_dir}/")
