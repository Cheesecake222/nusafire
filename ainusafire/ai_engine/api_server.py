import os
import io
import csv
import json
import math
import ssl
import time
import socket
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import pandas as pd
import xgboost as xgb
from shapely.geometry import Point, shape, mapping
from shapely.prepared import prep
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Muat otomatis variabel dari .env lokal maupun .env root Laravel (tanpa paket tambahan)
_CURRENT_DIR = Path(__file__).resolve().parent
for _env_file in (_CURRENT_DIR / ".env", _CURRENT_DIR.parent / ".env"):
    if _env_file.is_file():
        for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

API_VERSION = "2.6.2"

app = FastAPI(
    title="NusaFire Engine API",
    description=(
        "API prediksi risiko kebakaran real-time, integrasi titik panas satelit NASA FIRMS, "
        "fusi akurasi satelit-meteorologi-tutupan lahan, dan penyedia data historis geospasial NusaFire."
    ),
    version=API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_nusafire.json")
DATA_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "..", "data", "processed_dataset.csv")
)
GEOJSON_PATH = os.path.join(
    BASE_DIR, "geo_data", "indonesia_provinsi.geojson"
)
DISTRICT_GEOJSON_PATH = os.path.join(
    BASE_DIR, "geo_data", "indonesia_kabupaten.geojson"
)

NASA_FIRMS_MAP_KEY = os.getenv(
    "NASA_FIRMS_MAP_KEY", "6fead044d8f6f25064686861119a90a3"
).strip()
INDONESIA_BBOX = "95,-11,141,6"  # west, south, east, north

MAX_NEAREST_PROVINCE_DISTANCE = 0.05
MAX_NEAREST_DISTRICT_DISTANCE = 0.05

FEATURE_COLS = [
    "PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS10M",
    "LATITUDE", "LONGITUDE", "landcover_class",
]
CUSTOM_THRESHOLD = 0.35

# Faktor kerentanan bahan bakar (fuel flammability multiplier) berdasarkan kelas MapBiomas
LANDCOVER_VULNERABILITY: dict[int, float] = {
    3: 0.85,   # Hutan Alam / Primer (kanopi rapat & lembap, lebih tahan api)
    4: 0.95,   # Hutan Sekunder / Savana Pohon
    9: 1.15,   # Hutan Tanaman / HTI (monokultur, lebih mudah terbakar)
    11: 1.25,  # Padang Rumput / Sabana (bahan bakar halus cepat kering)
    12: 1.40,  # Semak Belukar / Lahan Gambut (risiko kebakaran bawah permukaan sangat tinggi)
    15: 1.20,  # Padang Rumput / Pastura
    21: 1.10,  # Pertanian & Perkebunan
    24: 0.05,  # Kawasan Perkotaan Padat (non-vegetasi)
    25: 1.30,  # Lahan Terbuka / Kering (paparan radiasi langsung)
    33: 0.00,  # Badan Air / Sungai / Danau
}

SSL_CONTEXT = ssl._create_unverified_context()

DEFAULT_38_PROVINCES = [
    {"code": "11", "province": "Aceh", "island": "Sumatra", "lat": 4.6951, "lon": 96.7494, "landcover_class": 3},
    {"code": "12", "province": "Sumatera Utara", "island": "Sumatra", "lat": 2.1154, "lon": 99.5451, "landcover_class": 3},
    {"code": "13", "province": "Sumatera Barat", "island": "Sumatra", "lat": -0.7399, "lon": 100.8000, "landcover_class": 3},
    {"code": "14", "province": "Riau", "island": "Sumatra", "lat": 0.2933, "lon": 101.7068, "landcover_class": 3},
    {"code": "15", "province": "Jambi", "island": "Sumatra", "lat": -1.6101, "lon": 103.6131, "landcover_class": 3},
    {"code": "16", "province": "Sumatera Selatan", "island": "Sumatra", "lat": -3.3194, "lon": 103.9144, "landcover_class": 3},
    {"code": "17", "province": "Bengkulu", "island": "Sumatra", "lat": -3.5778, "lon": 102.3464, "landcover_class": 3},
    {"code": "18", "province": "Lampung", "island": "Sumatra", "lat": -4.5586, "lon": 105.4068, "landcover_class": 3},
    {"code": "19", "province": "Kepulauan Bangka Belitung", "island": "Sumatra", "lat": -2.7411, "lon": 106.4406, "landcover_class": 3},
    {"code": "21", "province": "Kepulauan Riau", "island": "Sumatra", "lat": 3.9457, "lon": 108.1429, "landcover_class": 3},
    {"code": "31", "province": "DKI Jakarta", "island": "Jawa, Bali & Nusa Tenggara", "lat": -6.2088, "lon": 106.8456, "landcover_class": 24},
    {"code": "32", "province": "Jawa Barat", "island": "Jawa, Bali & Nusa Tenggara", "lat": -6.9175, "lon": 107.6191, "landcover_class": 4},
    {"code": "33", "province": "Jawa Tengah", "island": "Jawa, Bali & Nusa Tenggara", "lat": -7.1510, "lon": 110.1403, "landcover_class": 4},
    {"code": "34", "province": "DI Yogyakarta", "island": "Jawa, Bali & Nusa Tenggara", "lat": -7.8754, "lon": 110.4262, "landcover_class": 4},
    {"code": "35", "province": "Jawa Timur", "island": "Jawa, Bali & Nusa Tenggara", "lat": -7.5361, "lon": 112.2384, "landcover_class": 4},
    {"code": "36", "province": "Banten", "island": "Jawa, Bali & Nusa Tenggara", "lat": -6.4058, "lon": 106.0640, "landcover_class": 4},
    {"code": "51", "province": "Bali", "island": "Jawa, Bali & Nusa Tenggara", "lat": -8.4095, "lon": 115.1889, "landcover_class": 4},
    {"code": "52", "province": "Nusa Tenggara Barat", "island": "Jawa, Bali & Nusa Tenggara", "lat": -8.6529, "lon": 117.3616, "landcover_class": 4},
    {"code": "53", "province": "Nusa Tenggara Timur", "island": "Jawa, Bali & Nusa Tenggara", "lat": -8.6574, "lon": 121.0794, "landcover_class": 4},
    {"code": "61", "province": "Kalimantan Barat", "island": "Kalimantan", "lat": -0.2788, "lon": 111.4753, "landcover_class": 3},
    {"code": "62", "province": "Kalimantan Tengah", "island": "Kalimantan", "lat": -1.6815, "lon": 113.3824, "landcover_class": 3},
    {"code": "63", "province": "Kalimantan Selatan", "island": "Kalimantan", "lat": -3.0926, "lon": 115.2838, "landcover_class": 3},
    {"code": "64", "province": "Kalimantan Timur", "island": "Kalimantan", "lat": 0.5387, "lon": 116.4194, "landcover_class": 3},
    {"code": "65", "province": "Kalimantan Utara", "island": "Kalimantan", "lat": 3.0731, "lon": 116.0414, "landcover_class": 3},
    {"code": "71", "province": "Sulawesi Utara", "island": "Sulawesi", "lat": 0.6247, "lon": 123.9750, "landcover_class": 3},
    {"code": "72", "province": "Sulawesi Tengah", "island": "Sulawesi", "lat": -1.4300, "lon": 121.4456, "landcover_class": 3},
    {"code": "73", "province": "Sulawesi Selatan", "island": "Sulawesi", "lat": -3.6688, "lon": 119.9741, "landcover_class": 3},
    {"code": "74", "province": "Sulawesi Tenggara", "island": "Sulawesi", "lat": -4.1449, "lon": 122.1746, "landcover_class": 3},
    {"code": "75", "province": "Gorontalo", "island": "Sulawesi", "lat": 0.6999, "lon": 122.4467, "landcover_class": 3},
    {"code": "76", "province": "Sulawesi Barat", "island": "Sulawesi", "lat": -2.8441, "lon": 119.2321, "landcover_class": 3},
    {"code": "81", "province": "Maluku", "island": "Maluku", "lat": -3.2385, "lon": 130.1453, "landcover_class": 3},
    {"code": "82", "province": "Maluku Utara", "island": "Maluku", "lat": 1.5709, "lon": 127.8088, "landcover_class": 3},
    {"code": "91", "province": "Papua", "island": "Papua", "lat": -2.5916, "lon": 140.6690, "landcover_class": 3},
    {"code": "92", "province": "Papua Barat", "island": "Papua", "lat": -1.3361, "lon": 133.1747, "landcover_class": 3},
    {"code": "93", "province": "Papua Selatan", "island": "Papua", "lat": -8.4932, "lon": 140.4018, "landcover_class": 4},
    {"code": "94", "province": "Papua Tengah", "island": "Papua", "lat": -3.6687, "lon": 136.5065, "landcover_class": 3},
    {"code": "95", "province": "Papua Pegunungan", "island": "Papua", "lat": -4.0846, "lon": 138.9531, "landcover_class": 3},
    {"code": "96", "province": "Papua Barat Daya", "island": "Papua", "lat": -0.9242, "lon": 131.2913, "landcover_class": 3},
]

PROVINCE_ALIASES = {
    "di yogyakarta": "daerah istimewa yogyakarta",
    "daerah istimewa yogyakarta": "daerah istimewa yogyakarta",
    "dki jakarta": "daerah khusus ibukota jakarta",
    "daerah khusus ibukota jakarta": "daerah khusus ibukota jakarta",
    "kepulauan bangka belitung": "kepulauan bangka belitung",
    "bangka belitung": "kepulauan bangka belitung",
    "nanggroe aceh darussalam": "aceh",
    "aceh": "aceh",
}

PROVINCE_TO_ISLAND = {
    "Aceh": "Sumatra",
    "Sumatera Utara": "Sumatra",
    "Sumatera Barat": "Sumatra",
    "Riau": "Sumatra",
    "Kepulauan Riau": "Sumatra",
    "Jambi": "Sumatra",
    "Sumatera Selatan": "Sumatra",
    "Bengkulu": "Sumatra",
    "Lampung": "Sumatra",
    "Kepulauan Bangka Belitung": "Sumatra",
    "Banten": "Jawa, Bali & Nusa Tenggara",
    "DKI Jakarta": "Jawa, Bali & Nusa Tenggara",
    "Daerah Khusus Ibukota Jakarta": "Jawa, Bali & Nusa Tenggara",
    "Jawa Barat": "Jawa, Bali & Nusa Tenggara",
    "Jawa Tengah": "Jawa, Bali & Nusa Tenggara",
    "DI Yogyakarta": "Jawa, Bali & Nusa Tenggara",
    "Daerah Istimewa Yogyakarta": "Jawa, Bali & Nusa Tenggara",
    "Jawa Timur": "Jawa, Bali & Nusa Tenggara",
    "Bali": "Jawa, Bali & Nusa Tenggara",
    "Nusa Tenggara Barat": "Jawa, Bali & Nusa Tenggara",
    "Nusa Tenggara Timur": "Jawa, Bali & Nusa Tenggara",
    "Kalimantan Barat": "Kalimantan",
    "Kalimantan Tengah": "Kalimantan",
    "Kalimantan Selatan": "Kalimantan",
    "Kalimantan Timur": "Kalimantan",
    "Kalimantan Utara": "Kalimantan",
    "Sulawesi Utara": "Sulawesi",
    "Gorontalo": "Sulawesi",
    "Sulawesi Tengah": "Sulawesi",
    "Sulawesi Barat": "Sulawesi",
    "Sulawesi Selatan": "Sulawesi",
    "Sulawesi Tenggara": "Sulawesi",
    "Maluku": "Maluku",
    "Maluku Utara": "Maluku",
    "Papua": "Papua",
    "Papua Barat": "Papua",
    "Papua Selatan": "Papua",
    "Papua Tengah": "Papua",
    "Papua Pegunungan": "Papua",
    "Papua Barat Daya": "Papua",
}

REGION_TO_ISLAND = {
    "Sumatra": "Sumatra",
    "Kalimantan": "Kalimantan",
    "Sulawesi": "Sulawesi",
    "Maluku": "Maluku",
    "Papua": "Papua",
    "Java-Bali-Nusa Tenggara": "Jawa, Bali & Nusa Tenggara",
    "Jawa-Bali-Nusa-Tenggara": "Jawa, Bali & Nusa Tenggara",
    "Jawa-Bali-Nusa Tenggara": "Jawa, Bali & Nusa Tenggara",
    "Java": "Jawa, Bali & Nusa Tenggara",
}

OVERVIEW_CACHE = {"timestamp": 0.0, "payload": None}
OVERVIEW_CACHE_TTL = 900  # 15 menit

FIRMS_CACHE: dict = {}
FIRMS_CACHE_TTL = 600  # 10 menit

model = xgb.XGBClassifier()
model_ready = False
model_error = None

dataset = None
dataset_ready = False
dataset_error = None

province_boundaries = []
geojson_ready = False
geojson_error = None

district_boundaries = []
district_geojson_ready = False
district_geojson_error = None


def normalize_name(name) -> str:
    if name is None:
        return ""
    return " ".join(str(name).strip().casefold().split())


def canonical_province_key(name) -> str:
    norm = normalize_name(name)
    return PROVINCE_ALIASES.get(norm, norm)


def canonical_display_province(name: str) -> str:
    """Menyeragamkan penamaan provinsi agar sinkron dengan dropdown frontend."""
    key = canonical_province_key(name)
    if key == "daerah istimewa yogyakarta":
        return "DI Yogyakarta"
    if key == "daerah khusus ibukota jakarta":
        return "DKI Jakarta"
    if key == "kepulauan bangka belitung":
        return "Kepulauan Bangka Belitung"
    if key == "aceh":
        return "Aceh"
    return str(name).strip()


# --- 1. Muat Model XGBoost ---
try:
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"File model tidak ditemukan: {MODEL_PATH}")

    model.load_model(MODEL_PATH)
    classes = list(model.classes_)
    if 0 not in classes or 1 not in classes:
        raise ValueError("Model harus memiliki kelas 0 dan 1.")

    model_ready = True
    print("Model XGBoost berhasil dimuat.")
except Exception as exc:
    model_error = str(exc)
    print(f"Gagal memuat model: {model_error}")


# --- 2. Muat Dataset Historis ---
try:
    if not os.path.isfile(DATA_PATH):
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATA_PATH}")

    dataset = pd.read_csv(DATA_PATH)
    required_columns = [
        "DATE", "REGION", "LATITUDE", "LONGITUDE", "hotspot_count", "is_fire"
    ]
    missing_columns = [c for c in required_columns if c not in dataset.columns]
    if missing_columns:
        raise ValueError(f"Kolom dataset tidak ditemukan: {missing_columns}")

    dataset["DATE"] = pd.to_datetime(dataset["DATE"], errors="coerce")
    for column in ["hotspot_count", "is_fire", "LATITUDE", "LONGITUDE"]:
        dataset[column] = pd.to_numeric(dataset[column], errors="coerce")

    dataset["hotspot_count"] = dataset["hotspot_count"].fillna(0)
    dataset = dataset.dropna(subset=["DATE"]).copy()
    dataset_ready = True
    print("Dataset historis berhasil dimuat.")
    print(f"Jumlah baris: {len(dataset):,}")
    print("Jumlah wilayah:", dataset["REGION"].nunique())
except Exception as exc:
    dataset_error = str(exc)
    print(f"Gagal memuat dataset historis: {dataset_error}")


# --- 3. Muat GeoJSON Provinsi (Skema KODE_PROV, PROVINSI, _prov) ---
try:
    if not os.path.isfile(GEOJSON_PATH):
        raise FileNotFoundError(f"GeoJSON provinsi tidak ditemukan: {GEOJSON_PATH}")

    with open(GEOJSON_PATH, "r", encoding="utf-8") as file:
        geojson_data = json.load(file)

    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry_data = feature.get("geometry")
        province_name = properties.get("PROVINSI")
        province_code = properties.get("KODE_PROV") or feature.get("id")
        province_slug = properties.get("_prov")

        if not province_name or not geometry_data:
            continue

        geometry = shape(geometry_data)
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        if not geometry.is_empty:
            clean_name = canonical_display_province(str(province_name).strip())
            clean_code = str(province_code).strip() if province_code is not None else None
            clean_slug = (
                str(province_slug).strip()
                if province_slug
                else clean_name.replace(" ", "_")
            )
            province_boundaries.append({
                "code": clean_code,
                "name": clean_name,
                "slug": clean_slug,
                "geometry": geometry,
                "prepared": prep(geometry),
                "bounds": geometry.bounds,
                "area": geometry.area,
            })

    if not province_boundaries:
        raise ValueError("GeoJSON tidak memiliki geometri provinsi valid.")

    geojson_ready = True
    print("Batas provinsi berhasil dimuat:", len(province_boundaries))
except Exception as exc:
    geojson_error = str(exc)
    print(f"Gagal memuat GeoJSON provinsi: {geojson_error}")


# --- 4. Muat GeoJSON Kabupaten/Kota ---
try:
    if not os.path.isfile(DISTRICT_GEOJSON_PATH):
        raise FileNotFoundError(
            f"GeoJSON kabupaten/kota tidak ditemukan: {DISTRICT_GEOJSON_PATH}"
        )

    with open(DISTRICT_GEOJSON_PATH, "r", encoding="utf-8") as file:
        district_geojson_data = json.load(file)

    for feature in district_geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry_data = feature.get("geometry")
        district_name = properties.get("WADMKK")
        province_name = properties.get("WADMPR")
        if not district_name or not province_name or not geometry_data:
            continue

        geometry = shape(geometry_data)
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        if geometry.is_empty:
            continue

        district_boundaries.append({
            "district": str(district_name).strip(),
            "province": canonical_display_province(str(province_name).strip()),
            "province_key": canonical_province_key(province_name),
            "geometry": geometry,
            "prepared": prep(geometry),
        })

    if not district_boundaries:
        raise ValueError("GeoJSON tidak memiliki geometri kabupaten/kota valid.")

    district_geojson_ready = True
    print("Batas kabupaten/kota berhasil dimuat:", len(district_boundaries))
except Exception as exc:
    district_geojson_error = str(exc)
    print(f"Gagal memuat GeoJSON kabupaten/kota: {district_geojson_error}")


# --- Pydantic Models ---
class FireRiskRequest(BaseModel):
    PRECTOTCORR: float
    T2M: float
    T2M_MAX: float
    T2M_MIN: float
    RH2M: float = Field(..., ge=0, le=100)
    WS10M: float = Field(..., ge=0)
    LATITUDE: float = Field(..., ge=-90, le=90)
    LONGITUDE: float = Field(..., ge=-180, le=180)
    landcover_class: int


class RealtimeLocationRequest(BaseModel):
    LATITUDE: float = Field(..., ge=-90, le=90)
    LONGITUDE: float = Field(..., ge=-180, le=180)
    landcover_class: int | None = None


# --- Fungsi Helper Network (IPv4-safe) ---
def fetch_url_text(url: str, timeout: int = 25) -> str:
    old_getaddrinfo = socket.getaddrinfo

    def ipv4_getaddrinfo(*args, **kwargs):
        responses = old_getaddrinfo(*args, **kwargs)
        return [r for r in responses if r[0] == socket.AF_INET] or responses

    socket.getaddrinfo = ipv4_getaddrinfo
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"NusaFire-AI/{API_VERSION}"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
            return response.read().decode("utf-8", errors="ignore")
    finally:
        socket.getaddrinfo = old_getaddrinfo


def fetch_json(url: str):
    return json.loads(fetch_url_text(url, timeout=15))


# --- Fungsi Helper Model, Geodesik & Cuaca ---
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def classify_risk(prob_fire: float) -> tuple[int, str]:
    prediction = int(prob_fire >= CUSTOM_THRESHOLD)
    if prob_fire >= CUSTOM_THRESHOLD:
        level = "High"
    elif prob_fire >= 0.15:
        level = "Moderate"
    else:
        level = "Low"
    return prediction, level


def get_landcover_factor(lc_class: int) -> float:
    return LANDCOVER_VULNERABILITY.get(int(lc_class), 1.0)


def fuse_with_nasa_firms(
    base_pred: dict,
    lat: float,
    lon: float,
    province: str | None,
    firms_hotspots: list[dict],
    landcover_class: int = 3,
) -> dict:
    """
    Meningkatkan akurasi deteksi risiko kebakaran dengan memadukan prediksi
    meteorologi XGBoost, kerentanan tutupan lahan, dan deteksi termal aktif
    satelit NASA FIRMS (VIIRS 375m).
    """
    lc_factor = get_landcover_factor(landcover_class)
    if lc_factor <= 0.05:
        return {
            "prediction": 0,
            "probability_safe": 0.96,
            "probability_fire": 0.04,
            "threshold": CUSTOM_THRESHOLD,
            "risk_level": "Low",
            "firms_active_hotspots": 0,
            "firms_max_frp": 0.0,
            "landcover_factor": lc_factor,
            "calibration_applied": False,
        }

    nearby = []
    prov_key = canonical_province_key(province) if province else ""

    for hs in firms_hotspots:
        dist_km = haversine_km(lat, lon, hs["latitude"], hs["longitude"])
        same_prov = (
            bool(prov_key)
            and bool(hs.get("province"))
            and canonical_province_key(hs["province"]) == prov_key
        )
        if dist_km <= 35.0 or same_prov:
            nearby.append((dist_km, hs))

    if not nearby:
        return {
            **base_pred,
            "firms_active_hotspots": 0,
            "firms_max_frp": 0.0,
            "landcover_factor": lc_factor,
            "calibration_applied": False,
        }

    nearby_count = len(nearby)
    max_frp = max(item[1].get("frp", 0.0) for item in nearby)
    closest_km = min(item[0] for item in nearby)

    proximity_factor = 1.0 if closest_km <= 15.0 else 0.65
    density_boost = min(0.38, (0.14 + math.log1p(nearby_count) * 0.08) * proximity_factor)
    frp_boost = min(0.15, (max_frp / 100.0) * 0.12)

    # Kalibrasi gabungan probabilitas meteorologi dan hotspot aktif berdasarkan kerentanan tutupan lahan
    calibrated_prob = min(
        0.99,
        round((base_pred["probability_fire"] + (density_boost + frp_boost) * lc_factor), 4),
    )
    pred_label, risk_level = classify_risk(calibrated_prob)

    return {
        "prediction": pred_label,
        "probability_safe": round(1.0 - calibrated_prob, 4),
        "probability_fire": calibrated_prob,
        "threshold": CUSTOM_THRESHOLD,
        "risk_level": risk_level,
        "firms_active_hotspots": nearby_count,
        "firms_max_frp": round(max_frp, 2),
        "landcover_factor": lc_factor,
        "calibration_applied": True,
    }


def infer_wmo_code(rain_mm: float, humidity: float) -> int:
    if rain_mm >= 5.0:
        return 63  # Hujan
    if rain_mm >= 0.5:
        return 80  # Hujan Ringan
    if humidity >= 82.0:
        return 3   # Berawan
    if humidity >= 70.0:
        return 2   # Cerah Berawan
    return 0       # Cerah


def resolve_landcover_class(lat: float, lon: float, provided: int | None) -> int:
    if provided is not None:
        return int(provided)

    # Wilayah DKI Jakarta merupakan kawasan urban padat (MapBiomas kelas 24)
    if -6.45 <= lat <= -6.05 and 106.65 <= lon <= 107.00:
        return 24

    if dataset_ready and dataset is not None and "landcover_class" in dataset.columns:
        valid_lc = dataset.dropna(subset=["LATITUDE", "LONGITUDE", "landcover_class"])
        if not valid_lc.empty:
            dist = (valid_lc["LATITUDE"] - lat) ** 2 + (valid_lc["LONGITUDE"] - lon) ** 2
            nearest_idx = dist.idxmin()
            return int(valid_lc.loc[nearest_idx, "landcover_class"])
    return 3


def run_xgb_inference(input_values: dict) -> dict:
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model AI belum siap.")

    lc = int(input_values.get("landcover_class", 3))
    lc_factor = get_landcover_factor(lc)

    # Kawasan perkotaan padat (24) & badan air (33) tidak berisiko karhutla
    if lc_factor <= 0.05:
        return {
            "prediction": 0,
            "probability_safe": 0.96,
            "probability_fire": 0.04,
            "threshold": CUSTOM_THRESHOLD,
            "risk_level": "Low",
            "landcover_factor": lc_factor,
        }

    input_data = pd.DataFrame([input_values], columns=FEATURE_COLS)
    probabilities = model.predict_proba(input_data)[0]
    classes = list(model.classes_)
    raw_fire_prob = float(probabilities[classes.index(1)])

    # Kalibrasi probabilitas meteorologi terhadap kerentanan jenis tutupan lahan
    probability_fire = min(0.99, max(0.01, raw_fire_prob * lc_factor))
    probability_safe = 1.0 - probability_fire
    prediction, risk_level = classify_risk(probability_fire)

    return {
        "prediction": prediction,
        "probability_safe": round(probability_safe, 4),
        "probability_fire": round(probability_fire, 4),
        "threshold": CUSTOM_THRESHOLD,
        "risk_level": risk_level,
        "landcover_factor": lc_factor,
    }


def get_fallback_weather(lat: float, lon: float) -> dict:
    if dataset_ready and dataset is not None:
        required = ["LATITUDE", "LONGITUDE", "PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS10M"]
        if all(col in dataset.columns for col in required):
            valid = dataset.dropna(subset=required)
            if not valid.empty:
                dist = (valid["LATITUDE"] - lat) ** 2 + (valid["LONGITUDE"] - lon) ** 2
                row = valid.loc[dist.idxmin()]
                return {
                    "PRECTOTCORR": float(row["PRECTOTCORR"]),
                    "T2M": float(row["T2M"]),
                    "T2M_MAX": float(row["T2M_MAX"]),
                    "T2M_MIN": float(row["T2M_MIN"]),
                    "RH2M": float(row["RH2M"]),
                    "WS10M": float(row["WS10M"]),
                }
    return {
        "PRECTOTCORR": 0.4,
        "T2M": 31.5,
        "T2M_MAX": 34.2,
        "T2M_MIN": 24.8,
        "RH2M": 64.0,
        "WS10M": 2.8,
    }


def fetch_realtime_weather(lat: float, lon: float) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"relative_humidity_2m_mean,wind_speed_10m_max"
        f"&wind_speed_unit=ms&timezone=Asia%2FJakarta&forecast_days=7"
    )
    try:
        res = fetch_json(url)
        current = res["current"]
        daily = res["daily"]

        today_weather = {
            "PRECTOTCORR": float(daily["precipitation_sum"][0] or 0.0),
            "T2M": float(current["temperature_2m"]),
            "T2M_MAX": float(daily["temperature_2m_max"][0]),
            "T2M_MIN": float(daily["temperature_2m_min"][0]),
            "RH2M": float(current["relative_humidity_2m"]),
            "WS10M": float(current["wind_speed_10m"]),
        }

        daily_rh = daily.get("relative_humidity_2m_mean", [])
        daily_ws = daily.get("wind_speed_10m_max", [])

        forecast_7_days = []
        for i in range(len(daily["time"])):
            t_max = float(daily["temperature_2m_max"][i])
            t_min = float(daily["temperature_2m_min"][i])
            rh_val = (
                float(daily_rh[i])
                if i < len(daily_rh) and daily_rh[i] is not None
                else float(current["relative_humidity_2m"])
            )
            ws_val = (
                float(daily_ws[i])
                if i < len(daily_ws) and daily_ws[i] is not None
                else float(current["wind_speed_10m"])
            )
            forecast_7_days.append({
                "date": daily["time"][i],
                "PRECTOTCORR": float(daily["precipitation_sum"][i] or 0.0),
                "T2M": round((t_max + t_min) / 2, 2),
                "T2M_MAX": t_max,
                "T2M_MIN": t_min,
                "RH2M": rh_val,
                "WS10M": ws_val,
            })

        return {"today": today_weather, "forecast_7_days": forecast_7_days, "live": True}
    except Exception:
        base = get_fallback_weather(lat, lon)
        forecast_7_days = [
            {
                "date": (pd.Timestamp.now(tz="Asia/Jakarta") + pd.Timedelta(days=i)).strftime("%Y-%m-%d"),
                **base,
            }
            for i in range(7)
        ]
        return {"today": base, "forecast_7_days": forecast_7_days, "live": False}


def build_province_monitoring_points() -> list[dict]:
    """Gunakan seluruh 38 provinsi dari GeoJSON jika lengkap, jika tidak gunakan DEFAULT_38_PROVINCES."""
    if geojson_ready and len(province_boundaries) >= 38:
        points = []
        for item in province_boundaries:
            rep_pt = item["geometry"].representative_point()
            prov_name = item["name"]
            is_jakarta = "jakarta" in prov_name.lower()
            points.append({
                "code": item.get("code"),
                "province": prov_name,
                "island": get_island_from_province(prov_name) or "Indonesia",
                "lat": round(float(rep_pt.y), 4),
                "lon": round(float(rep_pt.x), 4),
                "landcover_class": 24 if is_jakarta else None,
            })
        points.sort(key=lambda x: str(x["code"] or x["province"]))
        return points
    return DEFAULT_38_PROVINCES


def fetch_batch_province_weather(points: list[dict]) -> list[dict]:
    """Ambil cuaca real-time & prakiraan 7 hari untuk seluruh 38 provinsi dalam 1 batch."""
    lats = ",".join(str(pt["lat"]) for pt in points)
    lons = ",".join(str(pt["lon"]) for pt in points)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lats}&longitude={lons}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"relative_humidity_2m_mean,wind_speed_10m_max"
        f"&wind_speed_unit=ms&timezone=Asia%2FJakarta&forecast_days=7"
    )
    try:
        res = fetch_json(url)
        items = res if isinstance(res, list) else [res]

        results = []
        for item in items:
            current = item["current"]
            daily = item["daily"]
            today = {
                "PRECTOTCORR": float(daily["precipitation_sum"][0] or 0.0),
                "T2M": float(current["temperature_2m"]),
                "T2M_MAX": float(daily["temperature_2m_max"][0]),
                "T2M_MIN": float(daily["temperature_2m_min"][0]),
                "RH2M": float(current["relative_humidity_2m"]),
                "WS10M": float(current["wind_speed_10m"]),
            }

            daily_rh = daily.get("relative_humidity_2m_mean", [])
            daily_ws = daily.get("wind_speed_10m_max", [])
            forecast_7_days = []
            for i in range(len(daily["time"])):
                t_max = float(daily["temperature_2m_max"][i])
                t_min = float(daily["temperature_2m_min"][i])
                forecast_7_days.append({
                    "date": daily["time"][i],
                    "PRECTOTCORR": float(daily["precipitation_sum"][i] or 0.0),
                    "T2M": round((t_max + t_min) / 2, 2),
                    "T2M_MAX": t_max,
                    "T2M_MIN": t_min,
                    "RH2M": float(daily_rh[i]) if i < len(daily_rh) and daily_rh[i] is not None else today["RH2M"],
                    "WS10M": float(daily_ws[i]) if i < len(daily_ws) and daily_ws[i] is not None else today["WS10M"],
                })

            results.append({"today": today, "forecast_7_days": forecast_7_days})
        return results
    except Exception as exc:
        print(f"Fallback cuaca batch provinsi digunakan: {exc}")
        fallback_list = []
        for pt in points:
            base = get_fallback_weather(pt["lat"], pt["lon"])
            fc = [
                {
                    "date": (pd.Timestamp.now(tz="Asia/Jakarta") + pd.Timedelta(days=i)).strftime("%Y-%m-%d"),
                    **base,
                }
                for i in range(7)
            ]
            fallback_list.append({"today": base, "forecast_7_days": fc})
        return fallback_list


# --- Fungsi Helper Dataset & Spasial ---
def require_dataset():
    if not dataset_ready or dataset is None:
        raise HTTPException(
            status_code=503,
            detail={"message": "Dataset historis belum siap.", "error": dataset_error},
        )


def get_filtered_dataset(start_date=None, end_date=None, region=None):
    require_dataset()
    result = dataset
    start = None
    end = None

    if start_date:
        try:
            start = pd.to_datetime(start_date, errors="raise").normalize()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Format start_date tidak valid. Gunakan YYYY-MM-DD.",
            )
    if end_date:
        try:
            end = pd.to_datetime(end_date, errors="raise").normalize()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Format end_date tidak valid. Gunakan YYYY-MM-DD.",
            )
    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=400,
            detail="start_date tidak boleh melewati end_date.",
        )
    if start is not None:
        result = result[result["DATE"] >= start]
    if end is not None:
        result = result[result["DATE"] < end + pd.Timedelta(days=1)]
    if region:
        result = result[
            result["REGION"].astype(str).str.contains(
                region, case=False, regex=False, na=False
            )
        ]
    return result


def records_for_json(frame):
    output = frame.copy()
    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(output[column]):
            output[column] = output[column].dt.strftime("%Y-%m-%d")
    output = output.astype(object).where(pd.notna(output), None)
    return output.to_dict(orient="records")


def validate_coordinates(frame):
    result = frame.copy()
    for column in ["LATITUDE", "LONGITUDE"]:
        if column not in result.columns:
            raise HTTPException(status_code=500, detail=f"Kolom {column} tidak ditemukan.")
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = result.dropna(subset=["LATITUDE", "LONGITUDE"])
    result = result[
        result["LATITUDE"].between(-90, 90)
        & result["LONGITUDE"].between(-180, 180)
    ].copy()
    return result


def normalize_region(region):
    if region is None:
        return None
    return str(region).strip()


def get_island_from_region(region):
    normalized = normalize_region(region)
    if not normalized:
        return "Tidak diketahui"
    normalized_key = normalize_name(normalized)
    for region_name, island in REGION_TO_ISLAND.items():
        if normalize_name(region_name) == normalized_key:
            return island
    return "Tidak diketahui"


def get_island_from_province(province_name):
    if not province_name:
        return None
    normalized = normalize_name(province_name)
    for province, island in PROVINCE_TO_ISLAND.items():
        if normalize_name(province) == normalized:
            return island
    return None


def province_matches_region(province_name, region):
    province_island = get_island_from_province(province_name)
    region_island = get_island_from_region(region)
    return (
        province_island is not None
        and region_island != "Tidak diketahui"
        and province_island == region_island
    )


@lru_cache(maxsize=8192)
def locate_grid_province_cached(lat_round: float, lon_round: float, region: str | None):
    if not geojson_ready or not province_boundaries:
        return None, "geojson_unavailable", None, None

    point = Point(lon_round, lat_round)

    # 1. Cek cepat dengan bounding box + prepared geometry
    containing = []
    for item in province_boundaries:
        minx, miny, maxx, maxy = item["bounds"]
        if minx <= lon_round <= maxx and miny <= lat_round <= maxy:
            if item["prepared"].covers(point):
                containing.append(item)

    if containing:
        best = min(containing, key=lambda item: item["area"])
        method = (
            "inside_boundary_region_mismatch"
            if (region and not province_matches_region(best["name"], region))
            else "inside_boundary"
        )
        return best["name"], method, best["code"], best["slug"]

    # 2. Fallback poligon terdekat (untuk titik pesisir/pulau kecil)
    nearest = min(
        province_boundaries,
        key=lambda item: item["geometry"].distance(point),
    )
    distance = nearest["geometry"].distance(point)
    if distance <= MAX_NEAREST_PROVINCE_DISTANCE:
        method = (
            "nearest_boundary_region_mismatch"
            if (region and not province_matches_region(nearest["name"], region))
            else "nearest_boundary"
        )
        return nearest["name"], method, nearest["code"], nearest["slug"]

    return None, "unmatched", None, None


def locate_grid_province(latitude, longitude, region=None):
    try:
        lat_val = round(float(latitude), 5)
        lon_val = round(float(longitude), 5)
    except (TypeError, ValueError):
        return None, "invalid_coordinates", None, None

    return locate_grid_province_cached(lat_val, lon_val, region)


def locate_grid_district(latitude, longitude, province_name=None):
    if not district_geojson_ready or not district_boundaries:
        return None, "geojson_unavailable", None
    if not province_name:
        return None, "province_unmatched", None

    try:
        point = Point(float(longitude), float(latitude))
    except (TypeError, ValueError):
        return None, "invalid_coordinates", None

    province_key = canonical_province_key(province_name)
    candidates = [
        item for item in district_boundaries
        if item["province_key"] == province_key
    ]
    if not candidates:
        return None, "province_mismatch", None

    for item in candidates:
        if item["prepared"].covers(point):
            return item["district"], "inside_boundary", item["province"]

    nearest = min(candidates, key=lambda item: item["geometry"].distance(point))
    distance = nearest["geometry"].distance(point)
    if distance <= MAX_NEAREST_DISTRICT_DISTANCE:
        return nearest["district"], "nearest_boundary", nearest["province"]

    return None, "unmatched", None


# --- Fungsi Helper NASA FIRMS API (Real-Time Multi-Sensor 2026) ---
def fetch_nasa_firms_hotspots(days: int = 2, sensor: str = "VIIRS_SNPP_NRT") -> dict:
    days = max(1, min(int(days), 10))
    cache_key = f"multi_{sensor}_{days}"
    now = time.time()
    cached = FIRMS_CACHE.get(cache_key)
    if cached and (now - cached["timestamp"]) < FIRMS_CACHE_TTL:
        return cached["payload"]

    # Gabungkan sensor utama dengan konstelasi satelit VIIRS aktif (SNPP, NOAA-20, NOAA-21)
    sensors_to_query = [sensor]
    for extra_sensor in ("VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"):
        if extra_sensor not in sensors_to_query:
            sensors_to_query.append(extra_sensor)

    hotspots = []
    province_counts: dict[str, int] = {}
    seen_points = set()
    any_sensor_succeeded = False
    last_error = None

    for active_sensor in sensors_to_query:
        url = (
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{NASA_FIRMS_MAP_KEY}/{active_sensor}/{INDONESIA_BBOX}/{days}"
        )
        try:
            raw_csv = fetch_url_text(url, timeout=25)
            stripped = raw_csv.strip()
            if not stripped:
                continue
            if stripped.startswith("Invalid") or "latitude,longitude" not in stripped[:120]:
                last_error = stripped[:160]
                continue

            any_sensor_succeeded = True
            reader = csv.DictReader(io.StringIO(raw_csv))

            for row in reader:
                try:
                    lat = float(row.get("latitude", 0))
                    lon = float(row.get("longitude", 0))
                    acq_date = str(row.get("acq_date", "")).strip()
                    acq_time_raw = str(row.get("acq_time", "")).strip().zfill(4)

                    dedup_key = (round(lat, 3), round(lon, 3), acq_date, acq_time_raw)
                    if dedup_key in seen_points:
                        continue
                    seen_points.add(dedup_key)

                    frp = float(row.get("frp") or 0.0)
                    bright = float(row.get("bright_ti4") or row.get("brightness") or 0.0)
                    conf_raw = str(row.get("confidence", "nominal")).strip()
                    acq_time = (
                        f"{acq_time_raw[:2]}:{acq_time_raw[2:]} UTC"
                        if len(acq_time_raw) == 4
                        else acq_time_raw
                    )

                    province, _, province_code, _ = locate_grid_province(lat, lon)
                    district, _, _ = locate_grid_district(lat, lon, province)
                    island = get_island_from_province(province) if province else "Indonesia"

                    if province:
                        province_counts[province] = province_counts.get(province, 0) + 1

                    hotspots.append({
                        "latitude": lat,
                        "longitude": lon,
                        "province": province,
                        "province_code": province_code,
                        "district": district,
                        "island": island,
                        "brightness": round(bright, 1),
                        "frp": round(frp, 2),
                        "confidence": conf_raw,
                        "acq_date": acq_date,
                        "acq_time": acq_time,
                        "satellite": str(row.get("satellite") or active_sensor).strip(),
                        "daynight": str(row.get("daynight") or "D").strip(),
                    })
                except (ValueError, TypeError):
                    continue
        except Exception as exc:
            last_error = str(exc)
            continue

    if any_sensor_succeeded:
        hotspots.sort(key=lambda x: (x["acq_date"], x["frp"]), reverse=True)
        top_provinces = [
            {"province": k, "count": v}
            for k, v in sorted(province_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        payload = {
            "status": "success",
            "live": True,
            "source": "NASA FIRMS Real-Time API (VIIRS SNPP/NOAA-20/NOAA-21)",
            "sensor": sensor,
            "days": days,
            "total_hotspots": len(hotspots),
            "province_summary": top_provinces,
            "data": hotspots[:1500],
        }
        FIRMS_CACHE[cache_key] = {"timestamp": now, "payload": payload}
        return payload

    # Fallback jika koneksi sedang offline / API NASA FIRMS tidak terjangkau
    print(f"Fallback NASA FIRMS digunakan (offline/API gagal): {last_error}")
    fallback_hotspots = []
    province_counts = {}
    now_utc = datetime.now(timezone.utc)

    if dataset_ready and dataset is not None:
        fire_df = dataset[dataset["is_fire"] == 1].copy()
        fire_df = validate_coordinates(fire_df)
        fire_df = fire_df.sort_values(["DATE", "hotspot_count"], ascending=[False, False]).head(150)

        for idx, (_, row) in enumerate(fire_df.iterrows()):
            lat = float(row["LATITUDE"])
            lon = float(row["LONGITUDE"])
            province, _, province_code, _ = locate_grid_province(lat, lon, row.get("REGION"))
            district, _, _ = locate_grid_district(lat, lon, province)
            island = get_island_from_province(province) if province else get_island_from_region(row.get("REGION"))

            if province:
                province_counts[province] = province_counts.get(province, 0) + 1

            # Proyeksikan ke tanggal tahun berjalan (2026) agar konsisten dengan jendela pengamatan
            current_year_date = (now_utc - timedelta(days=idx % days)).strftime("%Y-%m-%d")

            fallback_hotspots.append({
                "latitude": lat,
                "longitude": lon,
                "province": province,
                "province_code": province_code,
                "district": district,
                "island": island,
                "brightness": 325.0,
                "frp": round(float(row.get("hotspot_count", 1)) * 12.5, 2),
                "confidence": "nominal",
                "acq_date": current_year_date,
                "acq_time": "06:00 UTC",
                "satellite": "NusaFire Baseline",
                "daynight": "D",
            })

    top_provinces = [
        {"province": k, "count": v}
        for k, v in sorted(province_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "status": "success",
        "live": False,
        "source": "NusaFire Baseline Hotspot Dataset (Offline Fallback)",
        "sensor": sensor,
        "days": days,
        "total_hotspots": len(fallback_hotspots),
        "province_summary": top_provinces,
        "data": fallback_hotspots,
    }


# --- Endpoints ---
@app.get("/")
def root():
    return {
        "service": "NusaFire Engine API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ready" if model_ready and dataset_ready else "not_ready",
        "version": API_VERSION,
        "model_loaded": model_ready,
        "dataset_loaded": dataset_ready,
        "model_error": model_error,
        "dataset_error": dataset_error,
        "geojson_loaded": geojson_ready,
        "geojson_error": geojson_error,
        "province_count": len(province_boundaries),
        "district_geojson_loaded": district_geojson_ready,
        "district_geojson_error": district_geojson_error,
        "district_count": len(district_boundaries),
        "dataset_rows": int(len(dataset)) if dataset_ready else 0,
        "nasa_firms_configured": bool(NASA_FIRMS_MAP_KEY),
        "threshold": CUSTOM_THRESHOLD,
    }


@app.get("/firms-hotspots")
def get_firms_hotspots(
    days: int = Query(default=2, ge=1, le=10),
    sensor: str = Query(default="VIIRS_SNPP_NRT", pattern="^(VIIRS_SNPP_NRT|VIIRS_NOAA20_NRT|VIIRS_NOAA21_NRT|MODIS_NRT)$"),
    province: str | None = None,
):
    """Mengambil titik panas aktif real-time dari NASA FIRMS API untuk wilayah Indonesia."""
    result = fetch_nasa_firms_hotspots(days=days, sensor=sensor)

    if province:
        target_key = canonical_province_key(province)
        filtered = [
            item for item in result["data"]
            if item.get("province") and canonical_province_key(item["province"]) == target_key
        ]
        return {
            **result,
            "filtered_province": province,
            "total_hotspots": len(filtered),
            "data": filtered,
        }

    return result


@app.get("/weather-history")
def get_weather_history(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    days: int = Query(default=10, ge=7, le=14),
):
    """Mengambil cuaca saat ini + riwayat harian Open-Meteo dengan fallback dataset historis jika offline."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,is_day"
        f"&daily=weather_code,temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        f"relative_humidity_2m_mean,precipitation_sum,wind_speed_10m_mean"
        f"&wind_speed_unit=ms&past_days={days}&forecast_days=1&timezone=Asia%2FJakarta"
    )
    try:
        res = fetch_json(url)
        return {
            "status": "success",
            "source": "Open-Meteo Real-Time API",
            "live": True,
            "current": res.get("current"),
            "daily": res.get("daily"),
        }
    except Exception as exc:
        print(f"Fallback weather-history digunakan (offline/DNS gagal): {exc}")
        base = get_fallback_weather(latitude, longitude)
        now_jkt = pd.Timestamp.now(tz="Asia/Jakarta")
        total_days = days + 1

        dates = [
            (now_jkt - pd.Timedelta(days=(days - i))).strftime("%Y-%m-%d")
            for i in range(total_days)
        ]

        daily_records = []
        if dataset_ready and dataset is not None:
            req_cols = [
                "DATE", "LATITUDE", "LONGITUDE", "PRECTOTCORR",
                "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS10M",
            ]
            if all(col in dataset.columns for col in req_cols):
                valid = dataset.dropna(subset=req_cols)
                if not valid.empty:
                    dist = (valid["LATITUDE"] - latitude) ** 2 + (valid["LONGITUDE"] - longitude) ** 2
                    nearest_idx = dist.idxmin()
                    nearest_lat = valid.loc[nearest_idx, "LATITUDE"]
                    nearest_lon = valid.loc[nearest_idx, "LONGITUDE"]

                    series = (
                        valid[
                            (valid["LATITUDE"] == nearest_lat)
                            & (valid["LONGITUDE"] == nearest_lon)
                        ]
                        .sort_values("DATE")
                        .tail(total_days)
                    )
                    for _, row in series.iterrows():
                        rain_v = float(row["PRECTOTCORR"])
                        rh_v = float(row["RH2M"])
                        daily_records.append({
                            "t": float(row["T2M"]),
                            "tmax": float(row["T2M_MAX"]),
                            "tmin": float(row["T2M_MIN"]),
                            "rh": rh_v,
                            "rain": rain_v,
                            "ws": float(row["WS10M"]),
                            "code": infer_wmo_code(rain_v, rh_v),
                        })

        default_code = infer_wmo_code(base["PRECTOTCORR"], base["RH2M"])
        while len(daily_records) < total_days:
            daily_records.append({
                "t": base["T2M"],
                "tmax": base["T2M_MAX"],
                "tmin": base["T2M_MIN"],
                "rh": base["RH2M"],
                "rain": base["PRECTOTCORR"],
                "ws": base["WS10M"],
                "code": default_code,
            })

        latest_day = daily_records[-1]
        return {
            "status": "success",
            "source": "NusaFire Baseline Dataset (Offline Fallback)",
            "live": False,
            "current": {
                "time": now_jkt.strftime("%Y-%m-%dT%H:%M"),
                "temperature_2m": latest_day["t"],
                "relative_humidity_2m": latest_day["rh"],
                "precipitation": latest_day["rain"],
                "wind_speed_10m": latest_day["ws"],
                "weather_code": latest_day["code"],
                "is_day": 1 if 6 <= now_jkt.hour < 18 else 0,
            },
            "daily": {
                "time": dates,
                "weather_code": [d["code"] for d in daily_records],
                "temperature_2m_mean": [d["t"] for d in daily_records],
                "temperature_2m_max": [d["tmax"] for d in daily_records],
                "temperature_2m_min": [d["tmin"] for d in daily_records],
                "relative_humidity_2m_mean": [d["rh"] for d in daily_records],
                "precipitation_sum": [d["rain"] for d in daily_records],
                "wind_speed_10m_mean": [d["ws"] for d in daily_records],
            },
        }


@app.post("/predict")
def predict_fire_risk(data: FireRiskRequest):
    try:
        input_values = data.model_dump() if hasattr(data, "model_dump") else data.dict()
        result = run_xgb_inference(input_values)
        return {
            "status": "success",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Kesalahan prediksi: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat melakukan prediksi.",
        )



def build_synchronized_weekly_forecast(
    base_prob: float,
    forecast_days: list[dict],
    lat: float,
    lon: float,
    lc_class: int,
) -> list[dict]:
    """
    Menghasilkan proyeksi risiko kebakaran 7 hari yang 100% sinkron dengan
    probabilitas aktif (base_prob) dan berfluktuasi secara dinamis mengikuti
    ramalan cuaca harian Open-Meteo (hujan, suhu, kelembapan, angin).
    """
    if not forecast_days:
        return []

    results = []
    today_w = forecast_days[0]
    base_temp = today_w.get("T2M_MAX", 31.0)
    base_rh = today_w.get("RH2M", 65.0)
    base_ws = today_w.get("WS10M", 3.0)

    for i, day in enumerate(forecast_days[:7]):
        date_str = day.get("date", "")
        t_max = day.get("T2M_MAX", base_temp)
        t_min = day.get("T2M_MIN", t_max - 5.0)
        t_mean = day.get("T2M", round((t_max + t_min) / 2, 1))
        rh = day.get("RH2M", base_rh)
        rain = day.get("PRECTOTCORR", 0.0)
        ws = day.get("WS10M", base_ws)

        if i == 0:
            final_p = round(base_prob, 4)
        else:
            # Modulasi cuaca: hujan menekan api, cuaca panas & kering menaikkan risiko
            rain_suppression = min(0.35, (rain / 15.0) * 0.30) if rain > 0.5 else 0.0
            rh_delta = (base_rh - rh) / 100.0 * 0.16
            temp_delta = (t_max - base_temp) / 10.0 * 0.09
            wind_delta = (ws - base_ws) / 10.0 * 0.05

            weather_factor = rh_delta + temp_delta + wind_delta - rain_suppression
            decay_factor = 0.90 ** i
            synoptic_noise = math.sin(i * 1.3) * 0.03

            projected_p = (base_prob * decay_factor) + (0.18 * (1.0 - decay_factor)) + weather_factor + synoptic_noise
            final_p = round(max(0.02, min(0.98, projected_p)), 4)

        _, rl = classify_risk(final_p)
        results.append({
            "date": date_str,
            "probability_fire": final_p,
            "risk_level": rl,
            "temperature": t_mean,
            "humidity": round(rh),
            "rainfall": round(rain, 1),
            "wind_speed": round(ws, 1),
        })

    return results


def generate_hourly_diurnal_forecast(
    today_weather: dict, lat: float, lon: float, lc_class: int
) -> list[dict]:
    """Menghitung proyeksi risiko kebakaran per jam (24 jam) berdasarkan siklus diurnal meteorologi tropis."""
    t_min = today_weather.get("T2M_MIN", 24.0)
    t_max = today_weather.get("T2M_MAX", 34.0)
    rh_mean = today_weather.get("RH2M", 65.0)
    ws_mean = today_weather.get("WS10M", 3.0)
    precip_daily = today_weather.get("PRECTOTCORR", 0.0)

    now_hour = pd.Timestamp.now(tz="Asia/Jakarta").hour
    hourly_points = []

    for i in range(24):
        h = (now_hour + i) % 24
        day_offset = (now_hour + i) // 24
        angle = ((h - 5) / 24.0) * 2.0 * math.pi
        diurnal_factor = -math.cos(angle)

        temp = t_min + (t_max - t_min) * ((diurnal_factor + 1.0) / 2.0)
        rh = max(20.0, min(98.0, rh_mean - 18.0 * diurnal_factor))
        ws = max(0.5, ws_mean * (0.7 + 0.6 * max(0.0, diurnal_factor)))
        precip = (precip_daily * 0.4) if (14 <= h <= 17) else 0.0

        day_pred = run_xgb_inference({
            "PRECTOTCORR": precip,
            "T2M": round(temp, 2),
            "T2M_MAX": t_max,
            "T2M_MIN": t_min,
            "RH2M": round(rh, 1),
            "WS10M": round(ws, 1),
            "LATITUDE": lat,
            "LONGITUDE": lon,
            "landcover_class": lc_class,
        })

        time_str = f"{h:02d}:00"
        day_label = "Hari ini" if day_offset == 0 else "Besok"

        hourly_points.append({
            "hour": h,
            "date": f"{day_label} {time_str}",
            "time": time_str,
            "label": time_str,
            "full_label": f"{day_label}, {time_str} WIB",
            "probability_fire": day_pred["probability_fire"],
            "risk_level": day_pred["risk_level"],
            "temperature": round(temp, 1),
            "humidity": round(rh, 1),
            "wind_speed": round(ws, 1),
        })

    return hourly_points


@app.post("/predict-realtime")
def predict_realtime_fire_risk(loc: RealtimeLocationRequest):
    try:
        weather_data = fetch_realtime_weather(loc.LATITUDE, loc.LONGITUDE)
        firms_data = fetch_nasa_firms_hotspots(days=2)
        today = weather_data["today"]
        lc_class = resolve_landcover_class(
            loc.LATITUDE, loc.LONGITUDE, loc.landcover_class
        )
        province, _, province_code, province_slug = locate_grid_province(
            loc.LATITUDE, loc.LONGITUDE
        )
        district, _, _ = locate_grid_district(
            loc.LATITUDE, loc.LONGITUDE, province
        )

        features = {
            **today,
            "LATITUDE": loc.LATITUDE,
            "LONGITUDE": loc.LONGITUDE,
            "landcover_class": lc_class,
        }
        raw_pred = run_xgb_inference(features)
        result = fuse_with_nasa_firms(
            raw_pred,
            loc.LATITUDE,
            loc.LONGITUDE,
            province,
            firms_data.get("data", []),
            landcover_class=lc_class,
        )

        weekly_trend = build_synchronized_weekly_forecast(
            result["probability_fire"],
            weather_data.get("forecast_7_days", []),
            loc.LATITUDE,
            loc.LONGITUDE,
            lc_class,
        )

        hourly_trend = generate_hourly_diurnal_forecast(
            today, loc.LATITUDE, loc.LONGITUDE, lc_class
        )

        return {
            "status": "success",
            "source": "Open-Meteo + NASA FIRMS VIIRS + NusaFire XGBoost",
            "coordinates": {
                "latitude": loc.LATITUDE,
                "longitude": loc.LONGITUDE,
                "province_code": province_code,
                "province": province,
                "province_slug": province_slug,
                "district": district,
                "landcover_class": lc_class,
            },
            "weather_realtime": today,
            **result,
            "forecast_24_hours": hourly_trend,
            "forecast_7_days": weekly_trend,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Kesalahan prediksi real-time: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memprediksi cuaca real-time: {str(exc)}",
        )


@app.get("/realtime-overview")
def get_realtime_overview(force_refresh: bool = False):
    now = time.time()
    if (
        not force_refresh
        and OVERVIEW_CACHE["payload"] is not None
        and (now - OVERVIEW_CACHE["timestamp"]) < OVERVIEW_CACHE_TTL
    ):
        return OVERVIEW_CACHE["payload"]

    try:
        points = build_province_monitoring_points()
        batch_weather = fetch_batch_province_weather(points)
        firms_data = fetch_nasa_firms_hotspots(days=2)
        firms_list = firms_data.get("data", [])

        province_results = []
        high_risk_count = 0
        moderate_risk_count = 0
        total_prob = 0.0

        for pt, w_data in zip(points, batch_weather):
            today = w_data["today"]
            lc_class = resolve_landcover_class(
                pt["lat"], pt["lon"], pt.get("landcover_class")
            )
            features = {
                **today,
                "LATITUDE": pt["lat"],
                "LONGITUDE": pt["lon"],
                "landcover_class": lc_class,
            }
            raw_pred = run_xgb_inference(features)
            pred = fuse_with_nasa_firms(
                raw_pred,
                pt["lat"],
                pt["lon"],
                pt["province"],
                firms_list,
                landcover_class=lc_class,
            )

            if pred["risk_level"] == "High":
                high_risk_count += 1
            elif pred["risk_level"] == "Moderate":
                moderate_risk_count += 1

            total_prob += pred["probability_fire"]

            weekly_trend = build_synchronized_weekly_forecast(
                pred["probability_fire"],
                w_data.get("forecast_7_days", []),
                pt["lat"],
                pt["lon"],
                lc_class,
            )

            hourly_trend = generate_hourly_diurnal_forecast(
                today, pt["lat"], pt["lon"], lc_class
            )

            province_results.append({
                "province_code": pt.get("code"),
                "province": pt["province"],
                "region": pt["province"],
                "location": f"{pt['province']} ({pt['island']})",
                "island": pt["island"],
                "latitude": pt["lat"],
                "longitude": pt["lon"],
                "landcover_class": lc_class,
                "weather": today,
                **pred,
                "forecast_24_hours": hourly_trend,
                "forecast_7_days": weekly_trend,
            })

        province_results.sort(key=lambda x: x["probability_fire"], reverse=True)
        count_monitored = len(province_results)
        avg_prob = round((total_prob / count_monitored) * 100, 2) if count_monitored else 0.0

        payload = {
            "status": "success",
            "firms_live": firms_data.get("live", False),
            "firms_total_hotspots": firms_data.get("total_hotspots", 0),
            "summary": {
                "high_risk_zones": high_risk_count,
                "moderate_risk_zones": moderate_risk_count,
                "average_fire_probability_pct": avg_prob,
                "monitored_regions": count_monitored,
                "monitored_provinces": count_monitored,
                "active_satellite_hotspots": firms_data.get("total_hotspots", 0),
            },
            "regions": province_results,
            "provinces": province_results,
        }

        OVERVIEW_CACHE["timestamp"] = now
        OVERVIEW_CACHE["payload"] = payload
        return payload

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Kesalahan realtime-overview: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat overview real-time provinsi: {str(exc)}",
        )


@app.get("/stats")
def get_stats(
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
):
    df = get_filtered_dataset(start_date, end_date, region)
    return {
        "status": "success",
        "total_records": int(len(df)),
        "total_hotspot_count": int(df["hotspot_count"].sum()),
        "fire_records": int((df["is_fire"] == 1).sum()),
        "non_fire_records": int((df["is_fire"] == 0).sum()),
        "region_count": int(df["REGION"].nunique()),
        "start_date": df["DATE"].min().strftime("%Y-%m-%d") if not df.empty else None,
        "end_date": df["DATE"].max().strftime("%Y-%m-%d") if not df.empty else None,
    }


@app.get("/hotspots")
def get_hotspots(
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
    status: str = Query(default="all", pattern="^(all|fire|non-fire)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    df = get_filtered_dataset(start_date, end_date, region).copy()
    required_columns = [
        "DATE", "REGION", "LATITUDE", "LONGITUDE", "hotspot_count", "is_fire"
    ]
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail={"message": "Kolom dataset tidak lengkap.", "missing_columns": missing_columns},
        )

    df = validate_coordinates(df)
    df["is_fire"] = pd.to_numeric(df["is_fire"], errors="coerce")
    df["hotspot_count"] = pd.to_numeric(df["hotspot_count"], errors="coerce").fillna(0)
    df = df.dropna(subset=["is_fire"])
    df = df[df["is_fire"].isin([0, 1])].copy()

    total_fire = int((df["is_fire"] == 1).sum())
    total_non_fire = int((df["is_fire"] == 0).sum())
    if status == "fire":
        df = df[df["is_fire"] == 1].copy()
    elif status == "non-fire":
        df = df[df["is_fire"] == 0].copy()

    df = df.sort_values(["DATE", "hotspot_count"], ascending=[False, False])
    total = int(len(df))
    page = df.iloc[offset:offset + limit].copy()
    columns = [
        c for c in [
            "DATE", "GRID_ID", "LOCATION", "REGION", "LATITUDE", "LONGITUDE",
            "hotspot_count", "is_fire",
        ] if c in page.columns
    ]
    return {
        "status": "success",
        "total": total,
        "total_fire": total_fire,
        "total_non_fire": total_non_fire,
        "limit": limit,
        "offset": offset,
        "filter_status": status,
        "returned": int(len(page)),
        "has_more": offset + len(page) < total,
        "data": records_for_json(page[columns]),
    }


@app.get("/charts")
def get_charts(
    period: str = Query(default="monthly", pattern="^(daily|monthly)$"),
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
):
    df = get_filtered_dataset(start_date, end_date, region)
    if df.empty:
        return {"status": "success", "period": period, "data": []}

    df = df.copy()
    if period == "daily":
        df["period"] = df["DATE"].dt.strftime("%Y-%m-%d")
    else:
        df["period"] = df["DATE"].dt.to_period("M").astype(str)

    chart = (
        df.groupby("period", as_index=False)
        .agg(
            hotspot_count=("hotspot_count", "sum"),
            fire_records=("is_fire", lambda values: (values == 1).sum()),
            non_fire_records=("is_fire", lambda values: (values == 0).sum()),
        )
        .sort_values("period")
    )
    return {"status": "success", "period": period, "data": records_for_json(chart)}


@app.get("/regions")
def get_regions(start_date: str | None = None, end_date: str | None = None):
    df = get_filtered_dataset(start_date, end_date)
    regions = (
        df.groupby("REGION", as_index=False)
        .agg(
            total_records=("REGION", "size"),
            total_hotspots=("hotspot_count", "sum"),
            fire_records=("is_fire", lambda values: (values == 1).sum()),
        )
        .sort_values("total_hotspots", ascending=False)
    )
    return {
        "status": "success",
        "total_regions": int(len(regions)),
        "data": records_for_json(regions),
    }


@app.get("/provinces")
def get_province_stats(start_date: str | None = None, end_date: str | None = None):
    """Agregasi statistik historis per provinsi (sinkron dengan KODE_PROV & PROVINSI)."""
    df = get_filtered_dataset(start_date, end_date).copy()
    df = validate_coordinates(df)
    if df.empty:
        return {"status": "success", "total_provinces": 0, "data": []}

    unique_coords = df[["LATITUDE", "LONGITUDE", "REGION"]].drop_duplicates().copy()
    coord_map = {}
    for _, row in unique_coords.iterrows():
        prov_name, _, prov_code, prov_slug = locate_grid_province(
            row["LATITUDE"], row["LONGITUDE"], row["REGION"]
        )
        coord_map[(row["LATITUDE"], row["LONGITUDE"])] = (prov_code, prov_name, prov_slug)

    mapped = [
        coord_map.get((lat, lon), (None, None, None))
        for lat, lon in zip(df["LATITUDE"], df["LONGITUDE"])
    ]
    df["province_code"] = [m[0] for m in mapped]
    df["province"] = [m[1] for m in mapped]
    df["province_slug"] = [m[2] for m in mapped]

    valid_df = df.dropna(subset=["province"]).copy()
    if valid_df.empty:
        return {"status": "success", "total_provinces": 0, "data": []}

    grouped = (
        valid_df.groupby(["province_code", "province", "province_slug"], as_index=False, dropna=False)
        .agg(
            total_records=("province", "size"),
            total_hotspots=("hotspot_count", "sum"),
            fire_records=("is_fire", lambda v: (v == 1).sum()),
        )
        .sort_values("total_hotspots", ascending=False)
    )
    grouped["island"] = grouped["province"].apply(get_island_from_province)

    return {
        "status": "success",
        "total_provinces": int(len(grouped)),
        "data": records_for_json(grouped),
    }


@app.get("/geojson/provinces")
def get_provinces_geojson(
    simplify: float = Query(default=0.005, ge=0.0, le=0.1),
    province: str | None = None,
):
    """Mengembalikan GeoJSON batas provinsi (dapat disederhanakan untuk peta web)."""
    if not geojson_ready or not province_boundaries:
        raise HTTPException(
            status_code=503,
            detail={"message": "GeoJSON provinsi belum siap.", "error": geojson_error},
        )

    target_key = canonical_province_key(province) if province else None
    features = []

    for item in province_boundaries:
        if target_key and canonical_province_key(item["name"]) != target_key and item["code"] != province:
            continue

        geom = item["geometry"]
        if simplify > 0:
            geom = geom.simplify(tolerance=simplify, preserve_topology=True)

        features.append({
            "type": "Feature",
            "id": item["code"],
            "properties": {
                "KODE_PROV": item["code"],
                "PROVINSI": item["name"],
                "_prov": item["slug"],
                "ISLAND": get_island_from_province(item["name"]),
            },
            "geometry": mapping(geom),
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@app.get("/locations")
def get_locations(region: str | None = None):
    df = get_filtered_dataset(region=region).copy()
    required_columns = ["REGION", "LATITUDE", "LONGITUDE"]
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail={"message": "Kolom lokasi tidak lengkap.", "missing_columns": missing_columns},
        )

    df = validate_coordinates(df)
    df["REGION"] = df["REGION"].astype("string").str.strip()
    df = df[df["REGION"].notna() & df["REGION"].ne("")].copy()

    identity_columns = ["REGION"]
    for column in ["LOCATION", "GRID_ID"]:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()
            identity_columns.append(column)
    identity_columns.extend(["LATITUDE", "LONGITUDE"])

    aggregations = {"total_records": ("REGION", "size")}
    if "hotspot_count" in df.columns:
        df["hotspot_count"] = pd.to_numeric(df["hotspot_count"], errors="coerce").fillna(0)
        aggregations["total_hotspots"] = ("hotspot_count", "sum")

    locations = df.groupby(
        identity_columns,
        as_index=False,
        dropna=False,
        observed=True,
    ).agg(**aggregations)

    province_values = []
    province_code_values = []
    province_slug_values = []
    island_values = []
    province_match_values = []
    district_values = []
    district_match_values = []
    district_province_values = []

    for _, row in locations.iterrows():
        region_name = str(row["REGION"]).strip()
        province, province_method, province_code, province_slug = locate_grid_province(
            row["LATITUDE"], row["LONGITUDE"], region_name
        )
        district, district_method, district_province = locate_grid_district(
            row["LATITUDE"], row["LONGITUDE"], province
        )
        island = (
            get_island_from_province(province)
            if province
            else get_island_from_region(region_name)
        )

        province_values.append(province)
        province_code_values.append(province_code)
        province_slug_values.append(province_slug)
        island_values.append(island)
        province_match_values.append(province_method)
        district_values.append(district)
        district_match_values.append(district_method)
        district_province_values.append(district_province)

    locations["province_code"] = province_code_values
    locations["province"] = province_values
    locations["province_slug"] = province_slug_values
    locations["island"] = island_values
    locations["province_match"] = province_match_values
    locations["district"] = district_values
    locations["district_match"] = district_match_values
    locations["district_province"] = district_province_values

    def make_label(row):
        for column in ["LOCATION", "GRID_ID"]:
            if column not in locations.columns:
                continue
            value = row[column]
            if pd.notna(value) and str(value).strip():
                return f"{row['REGION']} — {value}"
        return f"{row['REGION']} ({row['LATITUDE']:.4f}, {row['LONGITUDE']:.4f})"

    locations["label"] = locations.apply(make_label, axis=1)
    locations["LATITUDE"] = locations["LATITUDE"].astype(float)
    locations["LONGITUDE"] = locations["LONGITUDE"].astype(float)
    locations = locations.sort_values(
        ["island", "province", "district", "REGION", "label"],
        kind="stable",
        na_position="last",
    ).reset_index(drop=True)

    province_match_counts = locations["province_match"].value_counts(dropna=False).to_dict()
    district_match_counts = locations["district_match"].value_counts(dropna=False).to_dict()

    return {
        "status": "success",
        "total_locations": int(len(locations)),
        "total_provinces_mapped": int(locations["province"].notna().sum()),
        "total_provinces_unmatched": int(locations["province"].isna().sum()),
        "total_districts_mapped": int(locations["district"].notna().sum()),
        "total_districts_unmatched": int(locations["district"].isna().sum()),
        "province_match_summary": {str(k): int(v) for k, v in province_match_counts.items()},
        "district_match_summary": {str(k): int(v) for k, v in district_match_counts.items()},
        "geojson_loaded": geojson_ready,
        "district_geojson_loaded": district_geojson_ready,
        "data": records_for_json(locations),
    }