import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from skopt import BayesSearchCV
from skopt.space import Real, Integer

# Load data
data = pd.read_csv("Data/cs-training.csv")
X = data.drop('SeriousDlqin2yrs', axis=1)
y = data['SeriousDlqin2yrs']

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Define search space for hyperparameters
search_spaces = {
    'max_depth': Integer(3, 6),
    'learning_rate': Real(0.01, 0.3, prior='log-uniform'),
    'n_estimators': Integer(100, 500),
    'min_child_weight': Integer(1, 5),
    'subsample': Real(0.8, 1.0),
    'colsample_bytree': Real(0.8, 1.0)
}

# Initialize XGBoost classifier
model = xgb.XGBClassifier(
    objective='binary:logistic',
    random_state=42,
    eval_metric='error'
)

# Set up BayesSearchCV
bayes_search = BayesSearchCV(
    estimator=model,
    search_spaces=search_spaces,
    scoring='accuracy',
    cv=5,
    n_jobs=-1,
    n_iter=50,       # Number of parameter settings sampled
    verbose=1,
    random_state=42
)

# Perform Bayesian hyperparameter optimization
bayes_search.fit(X_train, y_train)
print("Best parameters found:", bayes_search.best_params_)
print("Best cross-validation accuracy:", bayes_search.best_score_)

# Evaluate the final model on the test set
y_pred = bayes_search.predict(X_test)
test_accuracy = accuracy_score(y_test, y_pred)
print("Test set accuracy:", test_accuracy)




#{'colsample_bytree': 0.8, 'learning_rate': 0.01, 'max_depth': 5, 'min_child_weight': 3, 'n_estimators': 500, 'subsample': 0.8}
#0.937625 With CVGrid
#{'colsample_bytree': 0.8, 'learning_rate': 0.03919426631536563, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 228, 'subsample': 0.8})
# 0.9376416666666667 Bayesian testyset -> 0.9370666666666667