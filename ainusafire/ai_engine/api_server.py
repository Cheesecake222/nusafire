
import os

import pandas as pd
import xgboost as xgb

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# =========================================================
# KONFIGURASI API
# =========================================================

app = FastAPI(
    title="NusaFire Engine API",
    description=(
        "API prediksi risiko kebakaran dan penyedia "
        "data historis untuk dashboard NusaFire."
    ),
    version="1.3.0",
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


# =========================================================
# PATH DAN KONSTANTA
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model_nusafire.json",
)

DATA_PATH = os.path.normpath(
    os.path.join(
        BASE_DIR,
        "..",
        "data",
        "processed_dataset.csv",
    )
)

FEATURE_COLS = [
    "PRECTOTCORR",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "WS10M",
    "LATITUDE",
    "LONGITUDE",
    "landcover_class",
]

CUSTOM_THRESHOLD = 0.35


# =========================================================
# STATUS MODEL DAN DATASET
# =========================================================

model = xgb.XGBClassifier()

model_ready = False
model_error = None

dataset = None
dataset_ready = False
dataset_error = None


# =========================================================
# MEMUAT MODEL XGBOOST
# =========================================================

try:
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(
            f"File model tidak ditemukan: {MODEL_PATH}"
        )

    model.load_model(MODEL_PATH)

    classes = list(model.classes_)

    if 0 not in classes or 1 not in classes:
        raise ValueError(
            "Model harus memiliki kelas 0 dan 1."
        )

    model_ready = True

    print("Model XGBoost berhasil dimuat.")

except Exception as exc:
    model_error = str(exc)
    print(f"Gagal memuat model: {model_error}")


# =========================================================
# MEMUAT DATASET HISTORIS
# =========================================================

try:
    if not os.path.isfile(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {DATA_PATH}"
        )

    dataset = pd.read_csv(DATA_PATH)

    required_columns = [
        "DATE",
        "REGION",
        "LATITUDE",
        "LONGITUDE",
        "hotspot_count",
        "is_fire",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom dataset tidak ditemukan: {missing_columns}"
        )

    # Konversi tipe data.
    dataset["DATE"] = pd.to_datetime(
        dataset["DATE"],
        errors="coerce",
    )

    dataset["hotspot_count"] = pd.to_numeric(
        dataset["hotspot_count"],
        errors="coerce",
    ).fillna(0)

    dataset["is_fire"] = pd.to_numeric(
        dataset["is_fire"],
        errors="coerce",
    ).fillna(0)

    dataset["LATITUDE"] = pd.to_numeric(
        dataset["LATITUDE"],
        errors="coerce",
    )

    dataset["LONGITUDE"] = pd.to_numeric(
        dataset["LONGITUDE"],
        errors="coerce",
    )

    # Hapus record tanpa tanggal yang valid.
    dataset = dataset.dropna(
        subset=["DATE"]
    ).copy()

    dataset_ready = True

    print("Dataset historis berhasil dimuat.")
    print(f"Jumlah baris: {len(dataset):,}")
    print(
        "Jumlah wilayah:",
        dataset["REGION"].nunique(),
    )

except Exception as exc:
    dataset_error = str(exc)
    print(
        f"Gagal memuat dataset historis: {dataset_error}"
    )


# =========================================================
# MODEL INPUT PREDIKSI
# =========================================================

class FireRiskRequest(BaseModel):
    PRECTOTCORR: float
    T2M: float
    T2M_MAX: float
    T2M_MIN: float
    RH2M: float
    WS10M: float

    LATITUDE: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    LONGITUDE: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    landcover_class: int


# =========================================================
# HELPER DATASET
# =========================================================

def require_dataset():
    """Memastikan dataset tersedia sebelum endpoint dijalankan."""

    if not dataset_ready or dataset is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Dataset historis belum siap.",
                "error": dataset_error,
            },
        )


def get_filtered_dataset(
    start_date=None,
    end_date=None,
    region=None,
):
    """
    Memfilter dataset berdasarkan tanggal dan wilayah.
    Dataset utama tidak diubah.
    """

    require_dataset()

    result = dataset

    start = None
    end = None

    if start_date:
        try:
            start = pd.to_datetime(
                start_date,
                errors="raise",
            ).normalize()

        except Exception:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Format start_date tidak valid. "
                    "Gunakan YYYY-MM-DD."
                ),
            )

    if end_date:
        try:
            end = pd.to_datetime(
                end_date,
                errors="raise",
            ).normalize()

        except Exception:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Format end_date tidak valid. "
                    "Gunakan YYYY-MM-DD."
                ),
            )

    if start is not None and end is not None:
        if start > end:
            raise HTTPException(
                status_code=400,
                detail=(
                    "start_date tidak boleh melewati end_date."
                ),
            )

    if start is not None:
        result = result[
            result["DATE"] >= start
        ]

    if end is not None:
        result = result[
            result["DATE"] < end + pd.Timedelta(days=1)
        ]

    if region:
        result = result[
            result["REGION"].astype(str).str.contains(
                region,
                case=False,
                regex=False,
                na=False,
            )
        ]

    return result


def records_for_json(frame):
    """
    Mengubah tanggal menjadi string dan nilai NaN menjadi null
    agar respons dapat dikirim sebagai JSON.
    """

    output = frame.copy()

    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(
            output[column]
        ):
            output[column] = output[column].dt.strftime(
                "%Y-%m-%d"
            )

    output = output.astype(object).where(
        pd.notna(output),
        None,
    )

    return output.to_dict(
        orient="records"
    )


# =========================================================
# STATUS API
# =========================================================

@app.get("/")
def root():
    return {
        "service": "NusaFire Engine API",
        "version": "1.3.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": (
            "ready"
            if model_ready and dataset_ready
            else "not_ready"
        ),
        "model_loaded": model_ready,
        "dataset_loaded": dataset_ready,
        "model_error": model_error,
        "dataset_error": dataset_error,
        "dataset_rows": (
            int(len(dataset))
            if dataset_ready
            else 0
        ),
        "threshold": CUSTOM_THRESHOLD,
    }


# =========================================================
# PREDIKSI RISIKO KEBAKARAN
# =========================================================

@app.post("/predict")
def predict_fire_risk(data: FireRiskRequest):
    if not model_ready:
        raise HTTPException(
            status_code=503,
            detail="Model AI belum siap.",
        )

    try:
        if hasattr(data, "model_dump"):
            input_values = data.model_dump()
        else:
            input_values = data.dict()

        input_data = pd.DataFrame(
            [input_values],
            columns=FEATURE_COLS,
        )

        probabilities = model.predict_proba(
            input_data
        )[0]

        classes = list(model.classes_)

        probability_safe = float(
            probabilities[classes.index(0)]
        )

        probability_fire = float(
            probabilities[classes.index(1)]
        )

        prediction = int(
            probability_fire >= CUSTOM_THRESHOLD
        )

        return {
            "status": "success",
            "prediction": prediction,
            "probability_safe": round(
                probability_safe,
                4,
            ),
            "probability_fire": round(
                probability_fire,
                4,
            ),
            "threshold": CUSTOM_THRESHOLD,
            "risk_level": (
                "High" if prediction == 1 else "Low"
            ),
        }

    except Exception as exc:
        print(f"Kesalahan prediksi: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan prediksi: {str(exc)}",
        )


# =========================================================
# STATISTIK DATASET
# =========================================================

@app.get("/stats")
def get_stats(
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
):
    df = get_filtered_dataset(
        start_date,
        end_date,
        region,
    )

    return {
        "status": "success",
        "total_records": int(len(df)),
        "total_hotspot_count": int(
            df["hotspot_count"].sum()
        ),
        "fire_records": int(
            (df["is_fire"] == 1).sum()
        ),
        "non_fire_records": int(
            (df["is_fire"] == 0).sum()
        ),
        "region_count": int(
            df["REGION"].nunique()
        ),
        "start_date": (
            df["DATE"].min().strftime("%Y-%m-%d")
            if not df.empty
            else None
        ),
        "end_date": (
            df["DATE"].max().strftime("%Y-%m-%d")
            if not df.empty
            else None
        ),
    }


# =========================================================
# DATA HOTSPOT: FIRE DAN NON-FIRE
# =========================================================

@app.get("/hotspots")
def get_hotspots(
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
    status: str = Query(
        default="all",
        pattern="^(all|fire|non-fire)$",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    """
    Mengambil record dataset dengan koordinat valid.

    status=all      : semua record fire dan non-fire
    status=fire     : hanya record berlabel fire
    status=non-fire : hanya record berlabel non-fire

    limit dan offset digunakan untuk pagination.

    Catatan:
    Record yang dikembalikan merupakan record dataset,
    bukan selalu deteksi hotspot individual.
    """

    df = get_filtered_dataset(
        start_date,
        end_date,
        region,
    )

    # Pastikan kolom penting tersedia.
    required_columns = [
        "DATE",
        "REGION",
        "LATITUDE",
        "LONGITUDE",
        "hotspot_count",
        "is_fire",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Kolom dataset tidak lengkap.",
                "missing_columns": missing_columns,
            },
        )

    # Gunakan salinan supaya dataset utama tidak berubah.
    df = df.copy()

    # Pastikan koordinat dan label berupa angka.
    df["LATITUDE"] = pd.to_numeric(
        df["LATITUDE"],
        errors="coerce",
    )

    df["LONGITUDE"] = pd.to_numeric(
        df["LONGITUDE"],
        errors="coerce",
    )

    df["is_fire"] = pd.to_numeric(
        df["is_fire"],
        errors="coerce",
    )

    df["hotspot_count"] = pd.to_numeric(
        df["hotspot_count"],
        errors="coerce",
    ).fillna(0)

    # Hanya record dengan koordinat dan label valid.
    df = df.dropna(
        subset=[
            "LATITUDE",
            "LONGITUDE",
            "is_fire",
        ]
    )

    df = df[
        df["LATITUDE"].between(-90, 90)
        & df["LONGITUDE"].between(-180, 180)
        & df["is_fire"].isin([0, 1])
    ].copy()

    # Jumlah per label sebelum filter status.
    # Tetap mengikuti filter tanggal dan wilayah.
    total_fire = int(
        (df["is_fire"] == 1).sum()
    )

    total_non_fire = int(
        (df["is_fire"] == 0).sum()
    )

    # Filter status yang diminta.
    if status == "fire":
        df = df[
            df["is_fire"] == 1
        ].copy()

    elif status == "non-fire":
        df = df[
            df["is_fire"] == 0
        ].copy()

    # Urutkan tanggal terbaru dan hotspot_count terbesar.
    df = df.sort_values(
        ["DATE", "hotspot_count"],
        ascending=[False, False],
    )

    # Total hasil filter sebelum pagination.
    total = int(len(df))

    # Ambil halaman sesuai limit dan offset.
    page = df.iloc[
        offset:offset + limit
    ].copy()

    # Kolom yang dikirim ke frontend.
    columns = [
        column
        for column in [
            "DATE",
            "GRID_ID",
            "LOCATION",
            "REGION",
            "LATITUDE",
            "LONGITUDE",
            "hotspot_count",
            "is_fire",
        ]
        if column in page.columns
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


# =========================================================
# DATA GRAFIK TREN
# =========================================================

@app.get("/charts")
def get_charts(
    period: str = Query(
        default="monthly",
        pattern="^(daily|monthly)$",
    ),
    start_date: str | None = None,
    end_date: str | None = None,
    region: str | None = None,
):
    df = get_filtered_dataset(
        start_date,
        end_date,
        region,
    )

    if df.empty:
        return {
            "status": "success",
            "period": period,
            "data": [],
        }

    # Salinan agar tidak mengubah dataset utama.
    df = df.copy()

    if period == "daily":
        df["period"] = df["DATE"].dt.strftime(
            "%Y-%m-%d"
        )
    else:
        df["period"] = (
            df["DATE"]
            .dt.to_period("M")
            .astype(str)
        )

    chart = (
        df.groupby(
            "period",
            as_index=False,
        )
        .agg(
            hotspot_count=(
                "hotspot_count",
                "sum",
            ),
            fire_records=(
                "is_fire",
                lambda values: (values == 1).sum(),
            ),
            non_fire_records=(
                "is_fire",
                lambda values: (values == 0).sum(),
            ),
        )
        .sort_values("period")
    )

    return {
        "status": "success",
        "period": period,
        "data": records_for_json(chart),
    }


# =========================================================
# RINGKASAN PER WILAYAH
# =========================================================

@app.get("/regions")
def get_regions(
    start_date: str | None = None,
    end_date: str | None = None,
):
    df = get_filtered_dataset(
        start_date,
        end_date,
    )

    regions = (
        df.groupby(
            "REGION",
            as_index=False,
        )
        .agg(
            total_records=(
                "REGION",
                "size",
            ),
            total_hotspots=(
                "hotspot_count",
                "sum",
            ),
            fire_records=(
                "is_fire",
                lambda values: (values == 1).sum(),
            ),
        )
        .sort_values(
            "total_hotspots",
            ascending=False,
        )
    )

    return {
        "status": "success",
        "total_regions": int(len(regions)),
        "data": records_for_json(regions),
    }
