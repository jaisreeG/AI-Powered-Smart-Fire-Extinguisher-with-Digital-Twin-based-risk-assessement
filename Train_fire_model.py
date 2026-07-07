import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("fire_risk_data.csv")
df["risk"] = ((df["smoke"] > 400) | (df["flame"] == 1)).astype(int)
X = df[["temperature", "humidity", "smoke", "flame", "tempspike"]]
y = df["risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"Final Rule-based Accuracy: {acc * 100:.2f}%")

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
