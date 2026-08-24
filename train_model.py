import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from joblib import dump
import os

dataset_path = os.path.join(os.path.dirname(__file__), 'expanded_dataset_v3.xlsx')
df = pd.read_excel(dataset_path)

df['Symptoms'] = df['Symptoms'].apply(lambda x: str(x).split(','))

mlb = MultiLabelBinarizer()
X = mlb.fit_transform(df['Symptoms'])
y = df['Disease']

model = RandomForestClassifier()
model.fit(X, y)

# create model folder if not exists
os.makedirs("model", exist_ok=True)

dump(model, "model/random_forest.joblib")
dump(mlb, "model/mlb.joblib")

print("✅ Model trained and saved successfully")