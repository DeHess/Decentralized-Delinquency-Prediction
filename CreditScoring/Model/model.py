import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

traindata = pd.read_csv("Data/cs-training.csv")
X = traindata.drop(["SeriousDlqin2yrs", "Id"], axis=1)
y = traindata["SeriousDlqin2yrs"]


X_train, X_test, y_train, y_test = train_test_split(
    X, 
    y, 
    test_size=0.2,     
    random_state=42
)


ratio = (y_train == 0).sum() / (y_train == 1).sum()
print("Calculated scale_pos_weight:", ratio)


best_params = {
    "learning_rate": 0.02915,         
    "max_depth": 5,               
    "min_child_weight": 5,        
    "subsample": 0.8,            
    "colsample_bytree": 0.8,    
    "objective": "binary:logistic", 
    "n_estimators": 261,
    "eval_metric": "auc",   
    "lambda": 0.5,
    "scale_pos_weight": ratio,  
    "updater": "grow_quantile_histmaker",
    "grow_policy": "lossguide"
}

model = xgb.XGBClassifier(**best_params)
model.fit(
    X_train, 
    y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False
)

model.save_model("model.json")

