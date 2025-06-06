# Evaluation Scripts

This folder contains the scripts used to evaluate the model’s performance and robustness against adversarial manipulation. The evaluation covers both the classifier's baseline behavior and the anomaly detection mechanisms (pre- and postprocessing), under clean and manipulated input conditions.

## File Overview

### Primary Classifier Evaluation
- `Prim_baseline.py`: Evaluates the primary XGBoost model on unmanipulated data using standard metrics (accuracy, precision, recall, F1, ROC/PR curves, etc.).
- `prim_baseline_flagging.py`: Assigns predictions into flagging buckets based on threshold logic and evaluates classification behavior across them.

### Preprocessor (Autoencoder) Evaluation
- `comb_pre_baseline.py`: Computes baseline z-score anomalies from the autoencoder for unmanipulated inputs.
- `comb_pre_manipulated.py`: Simulates feature-wise manipulations to measure their impact on z-scores.

### Postprocessor (SHAP-based) Evaluation
- `comb_post_baseline.py`: Applies SHAP-based anomaly detection to clean evaluation data, calculating z-scores and Mahalanobis distances.

### Combined Anomaly Evaluation
- `comb_baseline_flagging.py`: Combines the pre- and postprocessing scores, assigns final flag categories, and evaluates average scores per class and bucket.
- `comb_baseline.py`: Sweeps through combinations of thresholds to analyze how well manipulated inputs evade detection under various settings.
- `comb_man_bucketchanges.py`: Analyzes how manipulated inputs change bucket categories (e.g., from "potential manipulation" to "not flagged") and visualizes how many of these transitions are successfully detected by the anomaly scoring system. Produces a stacked bar plot showing caught vs. uncaught instances for each transition type based on a fixed anomaly score threshold (default 1.75).

### Feature-Wise Manipulation Impact Test
- `column_attack_test.py`: Evaluates the effect of individual feature manipulations on both the model prediction and the combined anomaly detection score. For each entry and each manipulable feature, this script searches for values that reduce the prediction score while monitoring how the anomaly score responds. Results are cached to `improvement_results5.pkl` and visualized in scatter and bar plots.

## Dependencies and Assumptions

- Requires the trained model at `Model/model.json`
- Assumes evaluation data is available at `Data/eval.csv`
- Uses additional artifacts for the autoencoder (model, scaler, stats) in `ae_artifacts/`

## Output

Each script creates a separate output directory containing relevant result files (e.g., CSVs, plots). These outputs are used to analyze prediction performance and manipulation detection coverage across the pipeline.
