import os
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

PATH_GEOJSON = os.path.join(DATA_DIR, "indonesia-province.json")
PATH_MAPBIOMAS = os.path.join(DATA_DIR, "mapbiomas_landcover2024.tif")
PATH_NASA_POWER = os.path.join(DATA_DIR, "nasa_power.csv")
PATH_FIRMS = os.path.join(DATA_DIR, "firms_hotspots.csv")
PATH_OUTPUT = os.path.join(DATA_DIR, "processed_dataset.csv")

START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

print("=== STARTING SPATIAL PREPROCESSING ===")

print("\n[1/4] Loading NASA POWER Climate Data...")
df_power = pd.read_csv(PATH_NASA_POWER)

if 'DATE' in df_power.columns:
    df_power['DATE'] = pd.to_datetime(df_power['DATE'])
elif 'date' in df_power.columns:
    df_power['DATE'] = pd.to_datetime(df_power['date'])

df_power = df_power[(df_power['DATE'] >= START_DATE) & (df_power['DATE'] <= END_DATE)].copy()
df_power['date_str'] = df_power['DATE'].dt.strftime('%Y-%m-%d')
print(f"Data iklim terfilter ({START_DATE} s/d {END_DATE}): {len(df_power)} baris.")

print("\n[2/4] Loading NASA FIRMS Hotspot Data...")
df_firms = pd.read_csv(PATH_FIRMS)

date_col = 'acq_date' if 'acq_date' in df_firms.columns else 'DATE'
df_firms[date_col] = pd.to_datetime(df_firms[date_col])

df_firms = df_firms[(df_firms[date_col] >= START_DATE) & (df_firms[date_col] <= END_DATE)].copy()

gdf_firms = gpd.GeoDataFrame(
    df_firms,
    geometry=gpd.points_from_xy(df_firms.longitude, df_firms.latitude),
    crs="EPSG:4326"
)
print(f"Data hotspot terfilter ({START_DATE} s/d {END_DATE}): {len(gdf_firms)} titik.")

print("\n[3/4] Performing Spatial Join & Target Labeling...")

gdf_power = gpd.GeoDataFrame(
    df_power,
    geometry=gpd.points_from_xy(df_power.LONGITUDE, df_power.LATITUDE),
    crs="EPSG:4326"
)

gdf_firms['acq_date_str'] = gdf_firms[date_col].dt.strftime('%Y-%m-%d')

gdf_power_buffered = gdf_power.copy()
gdf_power_buffered['geometry'] = gdf_power_buffered.geometry.buffer(0.1)

joined = gpd.sjoin(gdf_firms, gdf_power_buffered, how="inner", predicate="within")
joined_matched = joined[joined['acq_date_str'] == joined['date_str']]
fire_counts = joined_matched.groupby(['GRID_ID', 'date_str']).size().reset_index(name='hotspot_count')

df_merged = pd.merge(df_power, fire_counts, on=['GRID_ID', 'date_str'], how='left')
df_merged['hotspot_count'] = df_merged['hotspot_count'].fillna(0).astype(int)
df_merged['is_fire'] = (df_merged['hotspot_count'] > 0).astype(int)

print("\n[4/4] Extracting Landcover Class from MapBiomas Raster...")

try:
    with rasterio.open(PATH_MAPBIOMAS) as src:
        coords = zip(df_merged['LONGITUDE'], df_merged['LATITUDE'])
        df_merged['landcover_class'] = [x[0] for x in src.sample(coords)]
    print("Ekstraksi tutupan lahan berhasil.")
except Exception as e:
    print(f"Gagal membaca raster MapBiomas ({e}). Mengisi nilai default 0.")
    df_merged['landcover_class'] = 0

df_merged.to_csv(PATH_OUTPUT, index=False)
print(f"\n=== PREPROCESSING COMPLETED ===")
print(f"Dataset terproses disimpan di: {PATH_OUTPUT}")
print(f"Total baris dataset: {len(df_merged)}")
print(f"Distribusi Target (is_fire):\n{df_merged['is_fire'].value_counts()}")