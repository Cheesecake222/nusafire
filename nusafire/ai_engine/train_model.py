import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_fscore_support
import xgboost as xgb
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "processed_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model_nusafire.json")

print("=== OPTIMIZING MODEL TRAINING (NUSAFIRE) ===")

print("\n[1/4] Loading Processed Dataset...")
df = pd.read_csv(DATA_PATH)

feature_cols = [
    'PRECTOTCORR', 'T2M', 'T2M_MAX', 'T2M_MIN', 'RH2M', 'WS10M', 
    'LATITUDE', 'LONGITUDE', 'landcover_class'
]
target_col = 'is_fire'

X = df[feature_cols]
y = df[target_col]

print("\n[2/4] Splitting Dataset (70% Train, 15% Validation, 15% Test)...")
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print("\n[3/4] Training Tuned XGBoost Classifier...")

scaled_weight = np.sqrt((len(y_train) - sum(y_train)) / sum(y_train))

model = xgb.XGBClassifier(
    n_estimators=150,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=scaled_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

print("\n[4/4] Evaluating Model with Custom Decision Threshold...")
y_proba = model.predict_proba(X_test)[:, 1]

CUSTOM_THRESHOLD = 0.35
y_pred_custom = (y_proba >= CUSTOM_THRESHOLD).astype(int)

print(f"\n--- CLASSIFICATION REPORT (THRESHOLD = {CUSTOM_THRESHOLD}) ---")
print(classification_report(y_test, y_pred_custom))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

model.save_model(MODEL_PATH)
print(f"\nModel teroptimasi berhasil disimpan di: {MODEL_PATH}")
print("=== MODEL TRAINING COMPLETED ===")