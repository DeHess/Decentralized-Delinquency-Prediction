import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

traindata = pd.read_csv("../Data/cs-training.csv")

X = traindata.drop("SeriousDlqin2yrs", axis=1)
X = X.drop("Id", axis= 1)
y = traindata["SeriousDlqin2yrs"]


X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y, 
    test_size=0.2,     
    random_state=42
)


best_params = {
    "learning_rate": 0.02915,         
    "max_depth": 5,               
    "min_child_weight": 5,        
    "subsample": 0.8,            
    "colsample_bytree": 0.8,    
    "objective": "binary:logistic", 
    "n_estimators": 261,
    "eval_metric": 'error',    
    "lambda": 0.5,
    "scale_pos_weight": 0.757,
    "updater": "grow_quantile_histmaker",
    "grow_policy": "lossguide"
}

model = xgb.XGBClassifier(**best_params)

evals_result = {}
model.fit(
    X_train, 
    y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False
)

evals_result = model.evals_result()

train_errors = evals_result["validation_0"]["error"]
test_errors  = evals_result["validation_1"]["error"]

min_test_error = min(test_errors)
best_epoch = test_errors.index(min_test_error)

for epoch, error in enumerate(test_errors):
    print(f"Epoch {epoch+1}: Test Error = {error}")

print(f"\nLowest Test Error: {min_test_error} at Epoch {best_epoch + 1}")

model.save_model("model.json")

