import os
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="NusaFire Engine API",
    description="API Service untuk Prediksi Risiko Kebakaran Hutan berbasis Machine Learning",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_nusafire.json")

model = xgb.XGBClassifier()
try:
    model.load_model(MODEL_PATH)
except Exception as e:
    print(f"Gagal memuat model: {e}")

class FireRiskRequest(BaseModel):
    PRECTOTCORR: float
    T2M: float
    T2M_MAX: float
    T2M_MIN: float
    RH2M: float
    WS10M: float
    LATITUDE: float
    LONGITUDE: float
    landcover_class: int


@app.post("/predict")
def predict_fire_risk(data: FireRiskRequest):
    try:
       
        input_data = pd.DataFrame([data.dict()])

        prediction = int(model.predict(input_data)[0])
        probabilities = model.predict_proba(input_data)[0].tolist()

        return {
            "status": "success",
            "prediction": prediction, 
            "probability_safe": round(probabilities[0], 4),
            "probability_fire": round(probabilities[1], 4),
            "risk_level": "High" if prediction == 1 else "Low",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Terjadi kesalahan prediksi: {str(e)}"
        )