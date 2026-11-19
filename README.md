# 🔥 NusaFire — AI-Powered Forest Fire Early Warning & Risk Intelligence System

[![Laravel](https://img.shields.io/badge/Laravel-12.x-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)](https://laravel.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Engine-EB6E00?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)

---

## 📌 Ringkasan Proyek

**NusaFire** adalah website intelijen dan sistem peringatan dini kebakaran hutan dan lahan (Karhutla) terintegrasi untuk seluruh wilayah Indonesia (38 Provinsi). Sistem ini menggabungkan telemetri satelit observasi bumi secara *real-time* dari **NASA FIRMS (VIIRS 375m)**, data cuaca meteorologi terperinci dari **Open-Meteo**, klasifikasi spasial tutupan lahan dari **MapBiomas Indonesia**, serta model prediksi berbasis kecerdasan buatan (**Machine Learning XGBoost**) untuk menghasilkan estimasi risiko kebakaran hutan yang presisi, adaptif, dan akuntabel.

Platform ini dirancang untuk mendukung para pengambil kebijakan, otoritas penanggulangan bencana (BNPB/BPBD) serta pemangku kepentingan kehutanan dalam mendeteksi ancaman api sedini mungkin sebelum eskalasi bencana terjadi.

---

## Fitur Utama Sistem

1. **Observasi Satelit Aktif & Pemetaan Hotspot (Hotspot Mapping)**
   - Deteksi titik panas (*hotspot*) aktif multi-sensor dari konstelasi satelit NASA FIRMS VIIRS (Suomi NPP, NOAA-20, dan NOAA-21) resolusi 375m secara *near real-time*.
   - Filter spasial dan temporal (rentang waktu 24 jam hingga 7 hari) untuk 38 provinsi di Indonesia.
   - Pengelompokan intensitas termal berbasis *Fire Radiative Power* (FRP, Satuan Megawatt).
   - Ekspor data hasil filter ke format CSV untuk analisis lanjutan.

2. **Dashboard Peringatan Dini & Ringkasan Risiko Nasional (Overview)**
   - Peta status risiko kebakaran 38 provinsi secara agregat (Tinggi, Sedang, Rendah).
   - Proyeksi tren risiko 7 hari yang tersinkronisasi langsung dengan parameter cuaca mingguan.
   - Visualisasi kurva diurnal 24 jam untuk memantau fluktuasi puncak risiko saat suhu udara mencapai titik maksimum.
   - Metrik telemetri satelit aktif dan indikator kesiapan sistem (*live status*).

3. **Analisis Meteorologi Real-Time (Weather Analysis)**
   - Pemantauan parameter cuaca tingkat lanjut per grid observasi: Suhu udara, Kelembapan relatif (*RH*), Curah hujan akumulatif, Kecepatan dan Arah angin, *Vapor Pressure Deficit* (VPD), dan Estimasi kelembapan tanah.
   - Deteksi parameter iklim ekstrem untuk mengevaluasi tingkat kekeringan bahan bakar vegetasi.

4. **Prediksi Spasial AI & Simulasi Tutupan Lahan (AI Prediction)**
   - Model klasifikasi *Extreme Gradient Boosting* (XGBoost) yang dilatih menggunakan dataset historis kebakaran hutan nasional.
   - Simulasi interaktif pengaruh tutupan lahan (*land cover simulator*): Hutan alam primer/sekunder, perkebunan kelapa sawit, lahan gambut, tanaman semusim, dan area terbangun.
   - *Feature importance breakdown* untuk transparansi alasan penentuan skor risiko oleh AI.

5. **Forest Watch & Spesifikasi Arsitektur Sistem (Forest Watch)**
   - Dokumentasi alur komputasi *end-to-end* (akuisisi data satelit $\rightarrow$ prapemrosesan geodesik $\rightarrow$ inferensi XGBoost $\rightarrow$ fusi probabilitas $\rightarrow$ visualisasi interaktif).
   - Matriks 9 fitur utama, spesifikasi model kecerdasan buatan, dan katalog sumber daya spasial terbuka.

6. **Antarmuka Responsif & Living Theme (Dark/Light Mode)**
   - Desain modern bernuansa *Natural Deep Forest* (`#111914`, `#19231c`, `#2b3a2e`) untuk mode gelap dan palet kontras ramah mata untuk mode terang.
   - Visualisasi interaktif globe 3D atmosferik pada halaman utama (*Welcome Page*).
   - Responsivitas penuh untuk perangkat desktop, tablet, dan ponsel pintar.

---

## Arsitektur Sistem & Alur Data

```
 [ NASA FIRMS VIIRS Satellite API ]      [ Open-Meteo Weather API ]      [ MapBiomas Indonesia GeoTIFF ]
                 │                                   │                                  │
                 └───────────────────┬───────────────┴──────────────────────────────────┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   Python AI Engine (FastAPI)  │
                     │  - Geodesic & Spatial Filter  │
                     │  - XGBoost Inference Model    │
                     │  - Land Cover Risk Multiplier │
                     │  - Multi-Sensor Satellite Hub │
                     └───────────────┬───────────────┘
                                     │ (JSON REST API - Port 8001)
                                     ▼
                     ┌───────────────────────────────┐
                     │   Backend Gateway (Laravel)   │
                     │  - Inertia.js Bridge          │
                     │  - Authentication & Session   │
                     │  - Reverse Proxy & Caching    │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │   Frontend Client (Vue 3)     │
                     │  - Composition API + TS       │
                     │  - Leaflet Map Rendering      │
                     │  - Tailwind CSS + Living UI   │
                     └───────────────────────────────┘
```

---

## Deklarasi Transparansi Penggunaan Aset, Library, & AI

> **Catatan Kepatuhan:** Seluruh penggunaan template, library pihak ketiga, dataset terbuka (*open-source assets*), dan asisten koding berbasis kecerdasan buatan dicantumkan secara transparan di bawah ini sesuai ketentuan proyek dan kompetisi.

### 1. Penggunaan Template & Starter Kit
* **Laravel Vue Starter Kit (Laravel Breeze with Inertia & Vue 3):** Digunakan sebagai fondasi *scaffolding* awal untuk arsitektur autentikasi, routing terintegrasi Inertia.js, serta integrasi Vite.
* **Shadcn-Vue / Radix Vue Component Primitives:** Digunakan sebagai dasar komponen aksesibilitas UI tanpa gaya (*unstyled headless primitives*) seperti dialog, dropdown menu, avatar, dan tooltip. Seluruh tampilan, warna, tipografi, dan tema disesuaikan secara khusus (*custom styling*) untuk NusaFire.

### 2. Penggunaan Library & Framework

#### Frontend (NusaFire / Web App)
* **Vue.js 3 (v3.5.13):** Framework reaktif antarmuka pengguna berbasis *Composition API* dan TypeScript.
* **Inertia.js (v2.0):** Jembatan *monolith modern* yang menghubungkan Laravel backend dengan Vue 3 tanpa perlunya REST API CRUD manual untuk halaman antarmuka.
* **Vite (v6.0.3):** Alat *build tool* dan *bundler* performa tinggi untuk frontend TypeScript dan Vue SFC.
* **Tailwind CSS (v3.4.1) & Tailwind Animate:** Framework utilitas CSS untuk penataan tata letak responsif dan animasi transisi.
* **Leaflet.js (v1.9.4) & @types/leaflet:** Library pemetaan interaktif open-source untuk visualisasi titik koordinat hotspot dan layer batas wilayah Indonesia.
* **Lucide Vue Next (v0.468.0):** Kumpulan ikon vektor open-source yang bersih dan konsisten.
* **VueUse (@vueuse/core v12.0.0):** Koleksi fungsi utilitas komposisi Vue 3.
* **Ziggy (v2.4.2):** Generator rute Laravel yang dapat dipanggil langsung dari kode JavaScript/TypeScript.

#### Backend (Laravel API Gateway)
* **Laravel Framework (v12.0):** Framework backend utama untuk manajemen sesi pengguna, middleware keamanan, perutean web, dan proxy permintaan API.
* **PHP (v8.2+):** Lingkungan runtime backend.
* **SQLite / MySQL:** Basis data penyimpanan akun pengguna dan preferensi sesi.
* **Guzzle / Laravel HTTP Client:** Klien HTTP untuk komunikasi asinkron antara Laravel Gateway dan Python AI Engine.

#### AI Engine & Komputasi Spasial (FastAPI / ainusafire)
* **FastAPI (v0.115+):** Framework mikro berkecepatan tinggi berbasis ASGI untuk melayani inferensi model AI dan agregasi data geospasial.
* **Uvicorn (v0.32+):** Server HTTP ASGI untuk eksekusi FastAPI.
* **XGBoost (v2.0+):** Library *gradient boosting* yang dioptimalkan untuk inferensi klasifikasi tingkat bahaya kebakaran.
* **Scikit-learn (v1.3+):** Prapemrosesan data, penskalaan fitur, dan metrik evaluasi model.
* **Shapely (v2.0+):** Manipulasi dan komputasi objek geometri planar dan poligon spasial wilayah.
* **Rasterio (v1.3+):** Pengolahan dan pembacaan data geospasial raster (peta tutupan lahan GeoTIFF).
* **Pandas (v2.0+) & NumPy (v1.24+):** Manipulasi data tabular dan komputasi array numerik berkecepatan tinggi.
* **Pydantic (v2.9+):** Validasi tipe data dan skema request/response payload API.

### 3. Penggunaan Aset & Data Terbuka (Open-Source / Open-Data Assets)
* **NASA FIRMS (Fire Information for Resource Management System):** API data telemetri satelit sensor VIIRS 375m (SNPP, NOAA-20, NOAA-21) dari NASA Earth Science Data and Information System (ESDIS) Project.
* **Open-Meteo Weather Forecast & Historical API:** Layanan API cuaca terbuka berbasis model cuaca nasional (ECMWF, GFS, DWD) tanpa kunci lisensi komersial berbayar.
* **MapBiomas Indonesia (Koleksi Tutupan Lahan 2024):** Peta klasifikasi tutupan lahan geospasial Indonesia untuk menentukan koefisien kerentanan bahan bakar vegetasi (*fuel flammability multiplier*).
* **NASA POWER Project (Prediction Of Worldwide Energy Resources):** Dataset historis agro-klimatologi dan meteorologi permukaan untuk pelatihan model XGBoost.
* **OpenStreetMap (OSM) Tiles:** Peta dasar kartografi dunia open-source yang digunakan pada layer visual Leaflet.
* **Batas Wilayah Geospasial BPS & Badan Informasi Geospasial (BIG):** Data batas administratif GeoJSON 38 Provinsi dan 514 Kabupaten/Kota di Indonesia.
* **Instrument Sans Font:** Font tipografi open-source dari Bunny Fonts (Google Fonts alternative berfokus pada privasi).

### 4. Penggunaan AI Coding Assistant
* **Model / Asisten yang Digunakan:** ChatGPT (OpenAI GPT-4), Claude (Anthropic) dan Google Gemini (Gen-AI)
* **Ruang Lingkup Pemanfaatan AI Assistant dalam Pengembangan:**
  1. *Refactoring & Component Styling:* Membantu penyusunan komponen antarmuka Vue 3 (`AiPrediction.vue`, `HotspotMap.vue`, `WeatherAnalysis.vue`, `ForestWatch.vue`, `Welcome.vue`) agar responsif dan bersih.
  2. *Sinkronisasi Data Fusi AI:* Membantu formulasi logika kalibrasi probabilistik fusi multi-sumber antara skor XGBoost, telemetri satelit FIRMS, dan anomali parameter cuaca Open-Meteo.
  3. *Sistem Tema Adaptif:* Membantu implementasi transisi variabel CSS untuk tema gelap natural forest dan tema terang tanpa kedipan layar (*zero layout shift / no-flash*).
  4. *Optimasi Komputasi & Pembersihan:* Membantu profiling kinerja rendering titik Leaflet, normalisasi penanganan status loading interaktif, serta pembersihan catatan non-kode untuk menjaga keterbacaan kode produksi.

---

## Struktur Direktori Repositori

```
NusaFire/
├── ainusafire/                       # Modul AI Engine & Pemrosesan Spasial (Python)
│   ├── ai_engine/
│   │   ├── api_server.py             # Server FastAPI (Inference, Telemetry, Geocoding)
│   │   ├── model_nusafire.json       # Bobot Model XGBoost Terlatih
│   │   ├── train_model.py            # Script Pelatihan Model Machine Learning
│   │   ├── spatial_preprocessing.py  # Utilitas Prapemrosesan Raster & Koordinat
│   │   └── geo_data/                 # Berkas Batas Wilayah GeoJSON
│   │       ├── indonesia_provinsi.geojson
│   │       └── indonesia_kabupaten.geojson
│   ├── data/                         # Sumber Data Pelatihan (FIRMS, POWER, MapBiomas)
│   ├── requirements.txt              # Dependensi Python
│   └── tests/                        # Pengujian Unit Model AI
│
├── NusaFire/                         # Aplikasi Web Full-Stack (Laravel + Vue 3)
│   ├── app/
│   │   └── Http/Controllers/Api/
│   │       └── NusaFireAiController.php  # Controller Gateway Proxy ke AI Engine
│   ├── config/                       # Konfigurasi Layanan Laravel
│   ├── database/                     # Migrasi & Database SQLite
│   ├── resources/
│   │   ├── css/                      # Konfigurasi Tailwind & Global CSS
│   │   ├── js/
│   │   │   ├── components/           # Komponen Vue Reusable (AppSidebar, dll.)
│   │   │   ├── composables/          # Vue Composables (useTheme, useAppearance)
│   │   │   ├── layouts/              # Layout Master Aplikasi
│   │   │   └── pages/                # Halaman Aplikasi
│   │   │       ├── Welcome.vue       # Landing Page (3D Globe Visual)
│   │   │       ├── Dashboard.vue     # Dashboard Overview Risiko
│   │   │       ├── HotspotMap.vue    # Pemetaan Satelit NASA FIRMS
│   │   │       ├── WeatherAnalysis.vue # Analisis Cuaca Real-Time
│   │   │       ├── AiPrediction.vue  # Prediksi AI & Simulator Lahan
│   │   │       ├── ForestWatch.vue   # Spesifikasi Pipeline Arsitektur
│   │   │       └── auth/Login.vue    # Halaman Masuk Akun
│   │   └── views/                    # Blade Template Root (app.blade.php)
│   ├── routes/
│   │   ├── web.php                   # Rute Navigasi Web & Endpoint Proxy AI
│   │   └── auth.php                  # Rute Autentikasi Pengguna
│   ├── package.json                  # Dependensi Frontend (npm)
│   ├── composer.json                 # Dependensi Backend (composer)
│   └── vite.config.ts                # Konfigurasi Vite Bundler
│
└── README.md                         # Dokumentasi Resmi Repositori
```

---

## Panduan Instalasi & Menjalankan Proyek

### Prasyarat Sistem
Pastikan perangkat Anda telah terpasang perangkat lunak berikut:
* **PHP** $\ge$ 8.2 (dengan ekstensi `pdo_sqlite`, `curl`, `mbstring`, `fileinfo`)
* **Composer** $\ge$ 2.5
* **Node.js** $\ge$ 18.x dan **npm** $\ge$ 9.x
* **Python** $\ge$ 3.10 dan **pip**

---

### Langkah 1: Kloning Repositori
```bash
git clone https://github.com/Cheesecake222/nusafire.git
cd nusafire
```

---

### Langkah 2: Menyiapkan dan Menjalankan Python AI Engine
Buka terminal pertama untuk menjalankan service AI Engine:

```bash
cd ainusafire

# Buat virtual environment (opsional namun disarankan)
python -m venv .venv
# Aktivasi di Windows:
.venv\Scripts\activate
# Aktivasi di Linux/macOS:
source .venv/bin/activate

# Pasang dependensi
pip install -r requirements.txt

# Jalankan server FastAPI pada port 8001
uvicorn ai_engine.api_server:app --host 127.0.0.1 --port 8001 --reload
```
> Server AI akan aktif dan dapat diakses pada `http://127.0.0.1:8001`. Dokumentasi interaktif Swagger UI tersedia di `http://127.0.0.1:8001/docs`.

---

### Langkah 3: Menyiapkan Backend Laravel
Buka terminal kedua untuk konfigurasi Laravel:

```bash
cd NusaFire

# Pasang dependensi PHP
composer install

# Salin berkas lingkungan
cp .env.example .env

# Generate application key
php artisan key:generate

# Migrasi basis data
php artisan migrate

# Jalankan server backend Laravel (Port 8000)
php artisan serve --port=8000
```

---

### Langkah 4: Menyiapkan dan Menjalankan Frontend Vue 3
Buka terminal ketiga untuk kompilasi frontend:

```bash
cd NusaFire

# Pasang dependensi npm
npm install

# Jalankan development server dengan HMR (Hot Module Replacement)
npm run dev

# ATAU jika ingin membuat build produksi siap pakai:
npm run build
```

---

### Langkah 5: Mengakses Aplikasi
Buka peramban (*web browser*) Anda dan akses:
* **Aplikasi NusaFire:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Halaman Peringatan Dini / Overview: `http://127.0.0.1:8000/dashboard`
* Halaman Peta Satelit Hotspot: `http://127.0.0.1:8000/hotspot-map`
* Halaman Analisis Cuaca: `http://127.0.0.1:8000/weather-analysis`
* Halaman Prediksi Spasial AI: `http://127.0.0.1:8000/ai-prediction`
* Halaman Arsitektur Forest Watch: `http://127.0.0.1:8000/forest-watch`

---

## 📡 Dokumentasi Endpoint API Utama

Aplikasi Laravel bertindak sebagai gerbang terpadu (*API Gateway*) yang memvalidasi otorisasi dan meneruskan permintaan ke AI Engine:

| Metode | Endpoint Laravel | Target AI Engine | Deskripsi |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/ai/health` | `GET /health` | Cek status kesehatan server inferensi AI |
| `GET` | `/api/ai/firms-hotspots` | `GET /firms-hotspots` | Mengambil titik hotspot satelit VIIRS aktif (24-48 jam) |
| `GET` | `/api/ai/realtime-overview` | `GET /realtime-overview` | Agregasi risiko Karhutla nasional di 38 provinsi |
| `GET` | `/api/ai/weather-history` | `GET /weather-history` | Observasi parameter cuaca historis & prakiraan Open-Meteo |
| `POST` | `/api/ai/predict-realtime` | `POST /predict-realtime` | Prediksi risiko koordinat spesifik berbasis fusi cuaca lokal |
| `POST` | `/api/ai/predict` | `POST /predict` | Inferensi manual parameter fitur model XGBoost |
| `GET` | `/api/ai/hotspots` | `GET /hotspots` | Riwayat hotspot terfilter dengan klasifikasi FRP |
| `GET` | `/api/ai/locations` | `GET /locations` | Daftar hierarki wilayah (Provinsi & Kabupaten/Kota) |

---

## 🧪 Pengujian & Jaminan Mutu

* **Uji Kompilasi Aset:** Diverifikasi dengan `npm run build` menggunakan Vite (100% lulus tanpa error).
* **Uji Sintaks Server AI:** Diverifikasi dengan modul `py_compile` pada seluruh skrip Python engine.
* **Uji Responsivitas:** Diverifikasi pada resolusi desktop, tablet, dan smartphone dengan fluid layout.

---

## Tim Pengembang & Lisensi

Proyek **NusaFire** dikembangkan dengan dedikasi untuk pelestarian hutan Indonesia, mitigasi bencana berbasis sains dan teknologi, serta transparansi keterbukaan kode.

* **Lisensi Kode Sumber:** [MIT License](https://opensource.org/licenses/MIT)
* **Lisensi Data:** Hak cipta data satelit NASA FIRMS dimiliki oleh NASA Earth Science Data System. Data cuaca oleh Open-Meteo di bawah lisensi Non-Commercial / Attribution. Data tutupan lahan oleh MapBiomas Indonesia.
