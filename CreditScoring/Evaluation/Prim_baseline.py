import os
import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    roc_curve, auc,
    precision_recall_curve,
    confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)


output_dir = "prim_base2"
os.makedirs(output_dir, exist_ok=True)


df = pd.read_csv('Data/eval.csv')
y_true = df['SeriousDlqin2yrs']
X = df.drop(['Id', 'SeriousDlqin2yrs'], axis=1)


booster = xgb.Booster()
booster.load_model('Model/model.json')
dtest = xgb.DMatrix(X)

y_proba = booster.predict(dtest)
y_pred = (y_proba >= 0.5).astype(int)


accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)
tn, fp, fn, tp = cm.ravel()


print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")
print(f"TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")



plt.figure(figsize=(6, 4))
plt.hist(y_proba[y_true == 0], bins=50, alpha=0.7, label='Actual 0')
plt.hist(y_proba[y_true == 1], bins=50, alpha=0.7, label='Actual 1')
plt.xlabel('Predicted Probability')
plt.ylabel('Count')
plt.title('Histogram of Predicted Probabilities')
plt.legend()
plt.tight_layout()
plt.savefig(f'{output_dir}/hist_pred_probs.png')
plt.close()


plt.figure(figsize=(6, 4))
plt.boxplot([y_proba[y_true == 0], y_proba[y_true == 1]], labels=['Actual 0', 'Actual 1'])
plt.ylabel('Predicted Probability')
plt.title('Boxplot of Predicted Probabilities')
plt.tight_layout()
plt.savefig(f'{output_dir}/boxplot_pred_probs.png')
plt.close()


fpr, tpr, _ = roc_curve(y_true, y_proba)
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(6, 4))
plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
plt.plot([0, 1], [0, 1], '--', color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(f'{output_dir}/roc_curve.png')
plt.close()

precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_proba)
plt.figure(figsize=(6, 4))
plt.plot(recall_vals, precision_vals)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision–Recall Curve')
plt.tight_layout()
plt.savefig(f'{output_dir}/pr_curve.png')
plt.close()


cm_df = pd.DataFrame(cm, index=['Actual 0', 'Actual 1'], columns=['Predicted 0', 'Predicted 1'])
cm_df.to_csv(f'{output_dir}/confusion_matrix.csv')
print("\nConfusion matrix saved to:", f'{output_dir}/confusion_matrix.csv')

bin_count = 10
prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=bin_count, strategy='uniform')

plt.figure(figsize=(6, 4))
plt.plot(prob_pred, prob_true, marker='o', label='Model Calibration')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfectly Calibrated')
plt.xlabel('Mean Predicted Probability')
plt.ylabel('Fraction of Positives')
plt.title('Calibration Curve (Reliability Plot)')
plt.legend()
plt.tight_layout()
plt.savefig(f'{output_dir}/calibration_curve.png')
plt.close()
