import numpy as np
from sklearn.dummy import DummyClassifier
import pandas as pd

data = pd.read_csv("Data/cs-training.csv")

X = data.drop('SeriousDlqin2yrs', axis = 1)
y = data['SeriousDlqin2yrs']

dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X, y)


dummy.predict(X)
score = dummy.score(X, y)

print(score) # 0.93316  

