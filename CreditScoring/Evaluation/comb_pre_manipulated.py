import os
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb

from pre_processing import pre_processing


output_dir = "preprocessor_manipulations"
os.makedirs(output_dir, exist_ok=True)


df = pd.read_csv('Data/eval.csv')
ids = df['Id']
y_true = df['SeriousDlqin2yrs']
X = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)


booster = xgb.Booster()
booster.load_model('Model/model.json')

anomaly_full = pre_processing(X)
X['baseline_z_score'] = anomaly_full['z_score'].values


value_ranges = {
    'age': list(range(18, 90)),
    'DebtRatio': [round(x * 0.05, 2) for x in range(21)],
    'MonthlyIncome': list(range(0, 70000, 1000)),
    'NumberOfDependents': list(range(10)),
    'NumberOfOpenCreditLinesAndLoans': list(range(21)),
    'NumberRealEstateLoansOrLines': list(range(11)),
}

results = []
for idx, row in X.iterrows():
    print(idx)
    base_df = row.drop('baseline_z_score').to_frame().T
    dmat_base = xgb.DMatrix(base_df)
    baseline_pred = booster.predict(dmat_base)[0]
    baseline_z = row['baseline_z_score']
    best_drop = 0.0
    best_feature = None
    best_value = None
    best_new_pred = baseline_pred
    new_z = None

    for feat, candidates in value_ranges.items():
        if feat not in base_df.columns:
            continue
        orig_val = row[feat]
        for v in candidates:
            if v == orig_val:
                continue
            mod_df = base_df.copy()
            mod_df.at[base_df.index[0], feat] = v
            dmat_mod = xgb.DMatrix(mod_df)
            new_pred = booster.predict(dmat_mod)[0]
            drop = baseline_pred - new_pred
            if drop > best_drop:
                best_drop = drop
                best_feature = feat
                best_value = v
                best_new_pred = new_pred

    if best_feature is not None:
        mod_row = row.drop('baseline_z_score').copy()
        mod_row[best_feature] = best_value
        anomaly_df = pre_processing(pd.DataFrame([mod_row]))
        new_z = anomaly_df['z_score'].iloc[0]

    results.append({
        'Id': ids.iloc[idx],
        'true_label': y_true.iloc[idx],
        'baseline_pred': baseline_pred,
        'baseline_z_score': baseline_z,
        'best_feature': best_feature,
        'best_value': best_value,
        'new_pred': best_new_pred,
        'drop': best_drop,
        'new_z_score': new_z
    })

df_out = pd.DataFrame(results)
df_out.to_csv(f"{output_dir}/feature_manipulation_results.csv", index=False)
print(f"✅ Manipulation complete. Results saved to {output_dir}/feature_manipulation_results.csv")

plt.figure(figsize=(8, 6))
plt.hist(df_out['baseline_z_score'].dropna(), bins=50, alpha=0.7, label='Baseline')
plt.hist(df_out['new_z_score'].dropna(), bins=50, alpha=0.7, label='Manipulated')
plt.xlabel('Z-Score')
plt.ylabel('Count')
plt.title('Anomaly Score Distribution: Baseline vs. Manipulated')
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/zscore_comparison_histogram.png")
plt.close()

print(f"Comparison histogram saved to {output_dir}/zscore_comparison_histogram.png")
