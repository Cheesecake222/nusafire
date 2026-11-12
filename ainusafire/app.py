import os
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NusaFire - Engine Prediksi Kebakaran Hutan",
    page_icon="🔥",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ai_engine", "model_nusafire.json")

@st.cache_resource
def load_model():
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    return model

try:
    model = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False

st.title("🔥 NusaFire: Engine Prediksi Risiko Kebakaran Hutan")
st.markdown("Sistem Peringatan Dini Kebakaran Hutan & Lahan Berbasis Machine Learning")

st.sidebar.header("⚙️ Input Parameter Lokasi & Cuaca")

lat = st.sidebar.number_input("Latitude", value=-2.5000, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=111.5000, format="%.4f")

prectotcorr = st.sidebar.slider("Curah Hujan (mm/hari)", 0.0, 100.0, 2.0)
t2m = st.sidebar.slider("Suhu Rata-rata (°C)", 15.0, 45.0, 33.0)
t2m_max = st.sidebar.slider("Suhu Maksimum (°C)", 15.0, 45.0, 36.0)
t2m_min = st.sidebar.slider("Suhu Minimum (°C)", 15.0, 45.0, 26.0)
rh2m = st.sidebar.slider("Kelembapan Udara (%)", 10.0, 100.0, 45.0)
ws10m = st.sidebar.slider("Kecepatan Angin (m/s)", 0.0, 20.0, 5.0)

landcover = st.sidebar.selectbox(
    "Tutupan Lahan (Landcover)",
    options=[(0, "Lainnya / Default"), (1, "Hutan"), (2, "Perkebunan/Pertanian"), (3, "Lahan Gambut / Semak")],
    format_func=lambda x: x[1]
)[0]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Analisis Prediksi Risiko")
    
    if st.button("Jalankan Prediksi Risiko", type="primary"):
        if model_loaded:
            input_data = pd.DataFrame([{
                'PRECTOTCORR': prectotcorr,
                'T2M': t2m,
                'T2M_MAX': t2m_max,
                'T2M_MIN': t2m_min,
                'RH2M': rh2m,
                'WS10M': ws10m,
                'LATITUDE': lat,
                'LONGITUDE': lon,
                'landcover_class': landcover
            }])
            
            prob = model.predict_proba(input_data)[0][1]
            prob_percent = prob * 100
            
            st.metric(label="Skor Probabilitas Kebakaran", value=f"{prob_percent:.2f}%")
            
            if prob_percent >= 35.0:
                st.error("🚨 RISIKO TINGGI: Potensi Kebakaran Hutan Sangat Tinggi!")
            elif prob_percent >= 20.0:
                st.warning("⚠️ RISIKO SEDANG: Perlu Pengawasan Area.")
            else:
                st.success("✅ RISIKO RENDAH: Kondisi Area Aman.")
        else:
            st.error("File model gagal dimuat. Pastikan model_nusafire.json tersedia.")

with col2:
    st.subheader("🗺️ Peta Lokasi Pemantauan")
    m = folium.Map(location=[lat, lon], zoom_start=6)
    folium.Marker(
        [lat, lon],
        popup=f"Lokasi: {lat}, {lon}",
        tooltip="Titik Pemantauan NusaFire",
        icon=folium.Icon(color="red" if 'prob_percent' in locals() and prob_percent >= 35 else "blue", icon="fire" if 'prob_percent' in locals() and prob_percent >= 35 else "info-sign")
    ).add_to(m)
    st_folium(m, width=500, height=400)