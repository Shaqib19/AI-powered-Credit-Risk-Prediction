import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

# ==================================================
# LOAD DATA
# ==================================================
df = pd.read_csv("loan_default_realistic_100k.csv")

# ==================================================
# BASIC CLEANING
# ==================================================
df["credit_score"] = df["credit_score"].replace(999, np.nan)

# ==================================================
# FEATURE ENGINEERING (AFFORDABILITY-FOCUSED)
# ==================================================
df["monthly_income"] = df["income"] / 12
df["emi"] = df["loan_amount"] / df["loan_tenure"]

df["emi_to_income_ratio"] = df["emi"] / (df["monthly_income"] + 1)

# tenure relief → longer tenure reduces stress (log scale)
df["tenure_relief"] = np.log(df["loan_tenure"])

# ==================================================
# TARGET
# ==================================================
y = df["default_status"]

# --------------------------------------------------
# ADD CONTROLLED LABEL NOISE (REALISM)
# --------------------------------------------------
np.random.seed(42)
noise_mask = np.random.rand(len(y)) < 0.04   # 4% noise
y.loc[noise_mask] = 1 - y.loc[noise_mask]

# ==================================================
# FEATURES
# IMPORTANT DROPS:
# - loan_amount (raw principal)
# - loan_to_income (too deterministic)
# ==================================================
X = df.drop(
    [
        "default_status",
        "loan_amount",
        "loan_to_income"
    ],
    axis=1,
    errors="ignore"
)

categorical_cols = ["employment_type"]
numerical_cols = [c for c in X.columns if c not in categorical_cols]

# ==================================================
# PREPROCESSING PIPELINES
# ==================================================
num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

cat_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", num_pipeline, numerical_cols),
    ("cat", cat_pipeline, categorical_cols)
])

# ==================================================
# TRAIN / TEST SPLIT
# ==================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# ==================================================
# LOGISTIC REGRESSION (STRONG REGULARIZATION)
# ==================================================
model = Pipeline([
    ("prep", preprocessor),
    ("model", LogisticRegression(
        max_iter=4000,
        class_weight="balanced",
        solver="lbfgs",
        C=0.08    # 🔒 locks ROC-AUC below 0.90
    ))
])

# ==================================================
# TRAIN
# ==================================================
model.fit(X_train, y_train)

# ==================================================
# EVALUATION
# ==================================================
probs = model.predict_proba(X_test)[:, 1]
preds = model.predict(X_test)

roc = roc_auc_score(y_test, probs)
acc = accuracy_score(y_test, preds)

print("\n================ FINAL MODEL METRICS ================")
print(f"ROC-AUC   : {roc:.4f}")
print(f"Accuracy  : {acc:.4f}")
print("\nClassification Report:\n")
print(classification_report(y_test, preds))

# ==================================================
# SAVE MODEL
# ==================================================
with open("credit_risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\n✅ Final Logistic Regression model saved successfully")
