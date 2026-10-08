import pandas as pd
import joblib
import json

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv("dataset/financial_dataset.csv")

print("Dataset Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# ==========================================
# SELECT FEATURES AND TARGET
# ==========================================

# Use original financial attributes for prediction.
# Health_Score and other derived scores are NOT given
# directly to the model.

X = df[
    [
        "Age",
        "Income",
        "Expenses",
        "Savings",
        "Goal",
        "Risk"
    ]
].copy()

y = df["Category"]

# ==========================================
# ENCODE CATEGORICAL FEATURES
# ==========================================

goal_encoder = LabelEncoder()
risk_encoder = LabelEncoder()
category_encoder = LabelEncoder()

X["Goal"] = goal_encoder.fit_transform(X["Goal"])
X["Risk"] = risk_encoder.fit_transform(X["Risk"])

y = category_encoder.fit_transform(y)

# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# ==========================================
# RANDOM FOREST CLASSIFIER
# ==========================================

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)

# ==========================================
# TRAIN MODEL
# ==========================================

model.fit(X_train, y_train)

# ==========================================
# PREDICTION
# ==========================================

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

# ==========================================
# MODEL EVALUATION
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print("\n========== MODEL PERFORMANCE ==========")

print(f"Accuracy :  {accuracy:.4f}")
print(f"Precision:  {precision:.4f}")
print(f"Recall   :  {recall:.4f}")
print(f"F1 Score :  {f1:.4f}")

print("\n========== CLASSIFICATION REPORT ==========")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=category_encoder.classes_,
        zero_division=0
    )
)

print("\n========== CONFUSION MATRIX ==========")
print(confusion_matrix(y_test, y_pred))

# ==========================================
# CROSS VALIDATION
# ==========================================

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

print("\n========== 5-FOLD CROSS VALIDATION ==========")
print("Scores:", cv_scores)
print(f"Mean CV Accuracy: {cv_scores.mean():.4f}")

# ==========================================
# FEATURE IMPORTANCE
# ==========================================

feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(
    by="Importance",
    ascending=False
)

print("\n========== FEATURE IMPORTANCE ==========")
print(feature_importance)

# ==========================================
# SAVE MODEL
# ==========================================

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

joblib.dump(
    category_encoder.classes_.tolist(),
    "models/category_classes.pkl"
)

# ==========================================
# SAVE METRICS
# ==========================================

metrics = {
    "accuracy": round(float(accuracy), 4),
    "precision": round(float(precision), 4),
    "recall": round(float(recall), 4),
    "f1_score": round(float(f1), 4),
    "cross_validation_accuracy": round(float(cv_scores.mean()), 4)
}

with open("models/model_metrics.json", "w") as file:
    json.dump(metrics, file, indent=4)

feature_importance.to_csv(
    "models/feature_importance.csv",
    index=False
)

print("\n========================================")
print("MODEL TRAINING COMPLETED SUCCESSFULLY")
print("Model and encoders saved in /models")
print("Evaluation metrics saved")
print("Feature importance saved")
print("========================================")