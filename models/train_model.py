import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("dataset/financial_dataset.csv")

X = df.drop(
    ["Category", "Target_Category"],
    axis=1
)

y = df["Category"]

goal_encoder = LabelEncoder()
risk_encoder = LabelEncoder()

X["Goal"] = goal_encoder.fit_transform(X["Goal"])
X["Risk"] = risk_encoder.fit_transform(X["Risk"])

category_encoder = LabelEncoder()
y = category_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("Accuracy:", accuracy)

joblib.dump(
    model,
    "models/financial_model.pkl"
)

joblib.dump(
    goal_encoder,
    "models/goal_encoder.pkl"
)

joblib.dump(
    risk_encoder,
    "models/risk_encoder.pkl"
)

joblib.dump(
    category_encoder,
    "models/category_encoder.pkl"
)

print("All Models Saved Successfully!")