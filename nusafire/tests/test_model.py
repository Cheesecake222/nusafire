import os
import pandas as pd
import xgboost as xgb

# Mengambil lokasi absolut direktori root proyek NusaFire
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ai_engine", "model_nusafire.json")

# 1. Load model
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

# 2. Sample data uji (9 fitur)
sample_data = pd.DataFrame(
    [
        {
            "PRECTOTCORR": 0.5,
            "T2M": 29.5,
            "T2M_MAX": 33.0,
            "T2M_MIN": 25.0,
            "RH2M": 75.0,
            "WS10M": 3.2,
            "LATITUDE": -2.5,
            "LONGITUDE": 118.0,
            "landcover_class": 1,
        }
    ]
)

# 3. Prediksi
prediction = model.predict(sample_data)
probability = model.predict_proba(sample_data)

print(f"Hasil Prediksi: {prediction[0]}")
print(f"Probabilitas: {probability[0]}")