import os
import pandas as pd
import matplotlib.pyplot as plt

from pre_processing import pre_processing

output_dir = "preprocessor_zscore_baseline2"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv('Data/eval.csv')
y_true = df['SeriousDlqin2yrs']
X = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)

anomaly_df = pre_processing(X)
anomaly_df["true_label"] = y_true

anomaly_df[["z_score", "true_label"]].to_csv(
    f"{output_dir}/zscore_baseline.csv", index=False
)

print("Z-Score Summary (All):")
print(anomaly_df["z_score"].describe())

print("\nZ-Score Summary by Class:")
summary_by_class = anomaly_df.groupby("true_label")["z_score"].describe()
print(summary_by_class)

summary_by_class.to_csv(f"{output_dir}/zscore_summary_by_class.csv")


plt.figure(figsize=(6, 4))
plt.hist(anomaly_df["z_score"][anomaly_df["true_label"] == 0], bins=50, alpha=0.7, label="Class 0")
plt.hist(anomaly_df["z_score"][anomaly_df["true_label"] == 1], bins=50, alpha=0.7, label="Class 1")
plt.xlabel("Max Z-Score (from Autoencoder)")
plt.ylabel("Count")
plt.title("Z-Score Distribution by Class")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/zscore_histogram_by_class.png")
plt.close()


plt.figure(figsize=(6, 4))
anomaly_df.boxplot(column="z_score", by="true_label")
plt.title("Z-Score Boxplot by True Label")
plt.suptitle("")
plt.xlabel("True Label")
plt.ylabel("Max Z-Score")
plt.tight_layout()
plt.savefig(f"{output_dir}/zscore_boxplot_by_class.png")
plt.close()


print(f"All results saved to: {output_dir}/")
