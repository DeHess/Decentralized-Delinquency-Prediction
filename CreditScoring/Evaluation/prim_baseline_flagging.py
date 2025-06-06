import os
import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)


EVAL_CSV   = 'Data/eval.csv'
MODEL_FILE = 'Model/model.json'
OUTPUT_DIR = 'prim_baseline'  
os.makedirs(OUTPUT_DIR, exist_ok=True)


FLAG_LOWER = 0.2  
FLAG_UPPER = 0.8 
POT_LB     = 0.5  
POT_UB     = 0.5  


df     = pd.read_csv(EVAL_CSV)
y_true = df['SeriousDlqin2yrs'].copy()
X      = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)


y_submitted = y_true.copy()


booster = xgb.Booster()
booster.load_model(MODEL_FILE)
proba = booster.predict(xgb.DMatrix(X))


proba_0 = proba[y_true == 0]
proba_1 = proba[y_true == 1]


bins_0 = [0.0, 0.2, 0.5, 1.0]
labels_0 = ['0 - 0.2', '0.2 - 0.5', '0.5 - 1.0']
counts_0 = pd.cut(proba_0, bins=bins_0, labels=labels_0, include_lowest=True).value_counts().sort_index()

plt.figure(figsize=(6, 4))
colors = ['#1f77b4', 'orange', 'red']
bars = plt.bar(counts_0.index, counts_0.values, color=colors)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 3, '%d' % int(height), ha='center')
plt.title('Bucket Counts for Non-Defaulters (y = 0)')
plt.xlabel('Predicted probability bucket')
plt.ylabel('Number of non-defaulters')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/buckets_serious0.png")
plt.close()


bins_1 = [0.0, 0.5, 0.8, 1.0]
labels_1 = ['0 - 0.5', '0.5 - 0.8', '0.8 - 1.0']
counts_1 = pd.cut(proba_1, bins=bins_1, labels=labels_1, include_lowest=True).value_counts().sort_index()

plt.figure(figsize=(6, 4))
colors = ['red', 'orange', '#1f77b4']
bars = plt.bar(counts_1.index, counts_1.values, color=colors)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 3, '%d' % int(height), ha='center')
plt.title('Bucket Counts for True Defaulters (y = 1)')
plt.xlabel('Predicted probability bucket')
plt.ylabel('Number of true defaulters')
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/buckets_serious1.png")
plt.close()

print(f"Probability bucket plots saved to {OUTPUT_DIR}/buckets_serious0.png and buckets_serious1.png")


flags = []
for y_hat, p in zip(y_submitted, proba):
    review = (y_hat == 0 and p > FLAG_LOWER) or (y_hat == 1 and p < FLAG_UPPER)
    pot_manip = (y_hat == 0 and p > POT_LB) or (y_hat == 1 and p < POT_UB)
    flags.append(int(pot_manip))

flags = np.array(flags)


cm = confusion_matrix(y_true != y_submitted, flags)
tn, fp, fn, tp = cm.ravel()

accuracy  = accuracy_score(y_true != y_submitted, flags)
precision = precision_score(y_true != y_submitted, flags, zero_division=0)
recall    = recall_score(y_true != y_submitted, flags, zero_division=0)
f1        = f1_score(y_true != y_submitted, flags, zero_division=0)

print("=== Baseline Detection Metrics (no manipulation present) ===")
print(f"Accuracy : {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall   : {recall:.3f}")
print(f"F1 Score : {f1:.3f}")
print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")

df_out = df.copy()
df_out['y_submitted'] = y_submitted
df_out['p_sec']       = proba
df_out['detected']    = flags
df_out['mode']        = 'baseline'
df_out.to_csv(f'{OUTPUT_DIR}/detection_results.csv', index=False)
print(f"\nFull per-sample results saved to {OUTPUT_DIR}/detection_results.csv")
