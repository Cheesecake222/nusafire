<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);

function toggleSidebar() {
    if (window.innerWidth <= 900) {
        mobileMenuOpen.value = !mobileMenuOpen.value;
    } else {
        sidebarCollapsed.value = !sidebarCollapsed.value;
        localStorage.setItem('nf-sidebar-collapsed', String(sidebarCollapsed.value));
    }
}

onMounted(() => {
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) {
        sidebarCollapsed.value = saved === 'true';
    }
});

const featuresList = [
    { name: 'PRECTOTCORR', label: 'Precipitation Corrected', unit: 'mm/day', source: 'NASA POWER & Open-Meteo', role: 'Inverse drought indicator; lower rainfall exponentially increases dry vegetative flammability.' },
    { name: 'T2M', label: 'Mean Air Temperature (2m)', unit: '°C', source: 'NASA POWER & Open-Meteo', role: 'Core thermal driver accelerating fuel moisture evaporation and ignition kinetics.' },
    { name: 'T2M_MAX', label: 'Daily Maximum Temperature', unit: '°C', source: 'NASA POWER & Open-Meteo', role: 'Captures midday thermal peaks when relative humidity reaches daily minimums.' },
    { name: 'T2M_MIN', label: 'Daily Minimum Temperature', unit: '°C', source: 'NASA POWER & Open-Meteo', role: 'Nighttime temperature baseline indicating diurnal thermal retention.' },
    { name: 'RH2M', label: 'Relative Humidity (2m)', unit: '%', source: 'NASA POWER & Open-Meteo', role: 'Critical fuel dryness metric; humidity below 60% drastically elevates wildfire propagation risk.' },
    { name: 'WS10M', label: 'Wind Speed at 10m', unit: 'm/s', source: 'NASA POWER & Open-Meteo', role: 'Oxygen supply and fire spread accelerator; governs flame velocity and spot fire generation.' },
    { name: 'LATITUDE', label: 'Spatial Coordinate (Y)', unit: 'Degrees (°)', source: 'Geospatial Centroid', role: 'Regional equatorial microclimate positioning across the Indonesian archipelago.' },
    { name: 'LONGITUDE', label: 'Spatial Coordinate (X)', unit: 'Degrees (°)', source: 'Geospatial Centroid', role: 'East-west monsoon transition tracking (Sumatra, Kalimantan, Sulawesi, Papua).' },
    { name: 'landcover_class', label: 'Vegetation & Land Cover Class', unit: 'Class ID (3-33)', source: 'MapBiomas Indonesia (2024)', role: 'Determines vegetative fuel loading, canopy structure, and subterranean peat flammability.' },
];
</script>

<template>
    <Head title="Forest Watch — Project Architecture & Tech Stack | NusaFire" />

    <main class="nf-app nf-forestwatch-page" :class="`theme-${theme}`">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <div class="nf-main" :class="{ 'nf-main-collapsed': sidebarCollapsed }">
            <!-- Topbar Navigation -->
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        class="nf-icon-button nf-mobile-menu"
                        type="button"
                        aria-label="Open navigation"
                        @click="toggleSidebar"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
                            <line x1="4" y1="6" x2="20" y2="6" />
                            <line x1="4" y1="12" x2="20" y2="12" />
                            <line x1="4" y1="18" x2="20" y2="18" />
                        </svg>
                    </button>
                    <h1>Forest Watch</h1>
                </div>

                <div class="nf-topbar-right">
                    <button
                        class="nf-icon-button"
                        type="button"
                        :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
                        :title="theme === 'dark' ? 'Light Mode' : 'Dark Mode'"
                        @click="toggleTheme"
                    >
                        <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18">
                            <circle cx="12" cy="12" r="5" />
                            <line x1="12" y1="1" x2="12" y2="3" />
                            <line x1="12" y1="21" x2="12" y2="23" />
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                            <line x1="1" y1="12" x2="3" y2="12" />
                            <line x1="21" y1="12" x2="23" y2="12" />
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                        </svg>
                    </button>
                </div>
            </header>

            <div class="nf-page-content">
                <!-- Page Heading -->
                <section class="nf-page-heading">
                    <div class="nf-heading-text">
                        <div class="nf-eyebrow">
                            <span class="nf-eyebrow-line"></span>
                            AI &amp; GEOSPATIAL INTELLIGENCE SPECIFICATIONS
                        </div>
                        <h1>Forest Watch — Project Architecture &amp; Methodology</h1>
                        <p>Complete documentation of training datasets, machine learning models, real-time satellite telemetry, and meteorological APIs powering the NusaFire Early Warning System.</p>
                    </div>

                    <div class="nf-heading-card">
                        <div class="nf-heading-card-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="20" height="20">
                                <path d="M12 21s8-4 8-11V5l-8-3-8 3v5c0 7 8 11 8 11Z" stroke-linejoin="round" />
                                <path d="m9 12 2 2 4-4" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
                        <div class="nf-heading-card-text">
                            <strong>System Status: Operational</strong>
                            <span>Real-Time Satellite &amp; AI Integration Active</span>
                        </div>
                    </div>
                </section>

                <!-- Top 4 Summary Metric Cards -->
                <section class="nf-summary-grid">
                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">ML Algorithm</span>
                            <span class="nf-card-icon icon-ai">🧠</span>
                        </div>
                        <div class="nf-card-value">XGBoost</div>
                        <div class="nf-card-sub">150 Estimators · Tuned Gradient Boosting</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Training Datasets</span>
                            <span class="nf-card-icon icon-data">📊</span>
                        </div>
                        <div class="nf-card-value">3 Sources</div>
                        <div class="nf-card-sub">NASA FIRMS, NASA POWER, MapBiomas</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Real-Time APIs</span>
                            <span class="nf-card-icon icon-api">🌐</span>
                        </div>
                        <div class="nf-card-value">2 Live Feeds</div>
                        <div class="nf-card-sub">NASA FIRMS (VIIRS 375m) &amp; Open-Meteo</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Monitored Scope</span>
                            <span class="nf-card-icon icon-sat">🛰️</span>
                        </div>
                        <div class="nf-card-value">38 Provinces</div>
                        <div class="nf-card-sub">National multi-source risk prediction</div>
                    </article>
                </section>

                <!-- End-to-End Pipeline & Architecture Visual Flow -->
                <article class="nf-panel nf-pipeline-panel">
                    <div class="nf-panel-header">
                        <div>
                            <div class="nf-panel-eyebrow">PIPELINE ARCHITECTURE</div>
                            <h2>End-to-End Data Fusion &amp; Inference Pipeline</h2>
                            <p>How satellite telemetry, atmospheric data, and machine learning models interact in NusaFire.</p>
                        </div>
                    </div>

                    <div class="nf-pipeline-steps-grid">
                        <div class="nf-pipeline-card">
                            <div class="nf-step-badge">STEP 01</div>
                            <div class="nf-step-icon">📡</div>
                            <h4>Multi-Source Ingestion</h4>
                            <p>Near real-time retrieval of active thermal anomalies via <strong>NASA FIRMS API</strong> (VIIRS 375m &amp; MODIS) combined with hourly &amp; 14-day forecasts from <strong>Open-Meteo API</strong>.</p>
                            <div class="nf-step-tags">
                                <span>NASA FIRMS</span>
                                <span>Open-Meteo API</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">➔</div>

                        <div class="nf-pipeline-card">
                            <div class="nf-step-badge">STEP 02</div>
                            <div class="nf-step-icon">🗺️</div>
                            <h4>Spatial &amp; Biomass Fusion</h4>
                            <p>Spatial join matching coordinates with <strong>MapBiomas 2024 LULC</strong> raster to determine fuel flammability, peat depth vulnerability, and canopy moisture retention.</p>
                            <div class="nf-step-tags">
                                <span>MapBiomas LULC</span>
                                <span>Peat Depth</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">➔</div>

                        <div class="nf-pipeline-card">
                            <div class="nf-step-badge">STEP 03</div>
                            <div class="nf-step-icon">🧠</div>
                            <h4>XGBoost ML Inference</h4>
                            <p>A 9-feature environmental vector is fed into the <strong>XGBoost Classifier</strong> (150 trees, threshold 0.35) producing calibrated fire probabilities.</p>
                            <div class="nf-step-tags">
                                <span>XGBoost</span>
                                <span>Threshold 0.35</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">➔</div>

                        <div class="nf-pipeline-card nf-card-highlight">
                            <div class="nf-step-badge badge-alert">STEP 04</div>
                            <div class="nf-step-icon">🚨</div>
                            <h4>Early Warning Output</h4>
                            <p>Calibrated risk scores mapped across <strong>38 Indonesian provinces</strong>, generating diurnal 24h curves, 7/14-day outlooks, and operational alert triggers.</p>
                            <div class="nf-step-tags">
                                <span>38 Provinces</span>
                                <span>High/Mod/Low Risk</span>
                            </div>
                        </div>
                    </div>
                </article>

                <!-- 3 In-Depth Technical Specification Columns -->
                <div class="nf-grid-3col">
                    <!-- Column 1: DATASETS -->
                    <article class="nf-panel nf-spec-card">
                        <div class="nf-spec-header">
                            <div class="nf-spec-icon icon-data">📊</div>
                            <div>
                                <div class="nf-panel-eyebrow">DATA SPECIFICATIONS</div>
                                <h2>Training Datasets &amp; Spatial Layers</h2>
                                <p>Historical ground-truth and geospatial rasters</p>
                            </div>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>NASA FIRMS Historical Hotspots (2022–2024)</strong>
                                <span class="nf-tag">289 MB CSV</span>
                            </div>
                            <p>Comprehensive historical thermal anomaly archive covering the entire Indonesian archipelago from 2022 to 2024.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Sensors:</strong> VIIRS 375m (Suomi NPP, NOAA-20, NOAA-21) and MODIS 1km (Terra &amp; Aqua).</li>
                                <li><strong>Key Variables:</strong> Fire Radiative Power (<code>FRP</code> in MW), Brightness Temperature (Ch 21/22/31 in Kelvin), Detection Confidence, Latitude/Longitude.</li>
                                <li><strong>Dataset Role:</strong> Supervised binary classification target (<code>is_fire = 1</code> for verified thermal anomaly).</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>NASA POWER Climatology &amp; Meteorology</strong>
                                <span class="nf-tag">67 MB CSV</span>
                            </div>
                            <p>Daily surface meteorology and agroclimatology dataset capturing long-term atmospheric moisture and drought patterns.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Parameters:</strong> Corrected Precipitation (<code>PRECTOTCORR</code>), Temperature at 2m (<code>T2M</code>, <code>T2M_MAX</code>, <code>T2M_MIN</code>), Relative Humidity (<code>RH2M</code>), Wind Speed (<code>WS10M</code>).</li>
                                <li><strong>Dataset Role:</strong> Core meteorological drivers governing vegetative fuel desiccation and fire kinetics.</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>MapBiomas Indonesia (Collection 2.0 / 2024 LULC)</strong>
                                <span class="nf-tag">Spatial GeoTIFF</span>
                            </div>
                            <p>30-meter spatial resolution land use and land cover classification raster covering Indonesia.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Key Classes:</strong> Primary Forest (3), Peatland Forest (4), HTI Plantation (9), Shrubland (12), Grassland (11), Cropland (21), Urban (24).</li>
                                <li><strong>Dataset Role:</strong> Provides fuel flammability multipliers and subterranean peat fire vulnerability factors.</li>
                            </ul>
                        </div>
                    </article>

                    <!-- Column 2: MACHINE LEARNING MODEL -->
                    <article class="nf-panel nf-spec-card">
                        <div class="nf-spec-header">
                            <div class="nf-spec-icon icon-ai">🧠</div>
                            <div>
                                <div class="nf-panel-eyebrow">MODEL SPECIFICATIONS</div>
                                <h2>Machine Learning: XGBoost Classifier</h2>
                                <p>Extreme Gradient Boosting algorithm &amp; calibration</p>
                            </div>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>Model Architecture &amp; Task Formulation</strong>
                                <span class="nf-tag tag-model">Supervised Binary</span>
                            </div>
                            <p>Trained using <strong>XGBoost (Extreme Gradient Boosting)</strong> to predict fire probability given atmospheric and geospatial inputs.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Objective:</strong> <code>binary:logistic</code> with logarithmic loss (<code>logloss</code>) optimization.</li>
                                <li><strong>Target Column:</strong> <code>is_fire</code> (0 = Safe / Non-fire, 1 = Active Wildfire Event).</li>
                                <li><strong>Features:</strong> 9-dimensional fused vector (6 weather + 2 spatial + 1 land cover).</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>Hyperparameters &amp; Imbalance Tuning</strong>
                                <span class="nf-tag">Optimized</span>
                            </div>
                            <p>Tuned to handle severe class imbalance between vast non-fire regions and sparse active fire hotspots.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Estimators:</strong> <code>n_estimators = 150</code> decision trees.</li>
                                <li><strong>Tree Depth:</strong> <code>max_depth = 5</code> (controls complexity and prevents overfitting).</li>
                                <li><strong>Learning Rate:</strong> <code>learning_rate = 0.05</code> for gradual gradient descent.</li>
                                <li><strong>Class Imbalance Weight:</strong> <code>scale_pos_weight = &radic;(N_negative / N_positive)</code>.</li>
                                <li><strong>Subsampling:</strong> <code>subsample = 0.8</code>, <code>colsample_bytree = 0.8</code>.</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>Decision Threshold &amp; Fuel Multipliers</strong>
                                <span class="nf-tag">Threshold 0.35</span>
                            </div>
                            <p>Calibrated risk scoring ensuring early warning alerts fire teams before catastrophic ignition.</p>
                            <ul class="nf-feature-list">
                                <li><strong>High Risk (&ge; 35%):</strong> Immediate mitigation priority, emergency patrol standby.</li>
                                <li><strong>Moderate Risk (15% &ndash; 34%):</strong> Field patrol alert, canal block inspection.</li>
                                <li><strong>Low Risk (&lt; 15%):</strong> Safe / controlled baseline.</li>
                                <li><strong>Fuel Multipliers:</strong> Deep Peat (1.35&times;), Shrubland (1.25&times;), HTI/Sawit (1.15&times;), Natural Forest (1.0&times;), Urban (0.04&times;).</li>
                            </ul>
                        </div>
                    </article>

                    <!-- Column 3: APIS & REAL-TIME TELEMETRY -->
                    <article class="nf-panel nf-spec-card">
                        <div class="nf-spec-header">
                            <div class="nf-spec-icon icon-api">🌐</div>
                            <div>
                                <div class="nf-panel-eyebrow">API SPECIFICATIONS</div>
                                <h2>Integrated APIs &amp; Live Telemetry</h2>
                                <p>Automated real-time feeds and backend services</p>
                            </div>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>NASA FIRMS Active Fire REST API</strong>
                                <span class="nf-tag">Live Feed</span>
                            </div>
                            <p>Direct REST queries polling active satellite thermal anomalies across the Indonesian bounding box (<code>95°E to 141°E, 11°S to 6°N</code>).</p>
                            <ul class="nf-feature-list">
                                <li><strong>Sensor Feeds:</strong> VIIRS 375m (Suomi NPP, NOAA-20, NOAA-21) and MODIS.</li>
                                <li><strong>Cadence:</strong> Refreshed within 3 hours of orbital satellite pass.</li>
                                <li><strong>Data Output:</strong> Real-time coordinates, sensor type, FRP (MW), and detection time.</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>Open-Meteo Global Forecast API</strong>
                                <span class="nf-tag">Hourly &amp; 14-Day</span>
                            </div>
                            <p>High-frequency meteorological data engine serving real-time atmospheric observations and forecasts for all 38 Indonesian provincial centroids.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Weather Variables:</strong> 2m Temperature, Relative Humidity, Precipitation accumulation, Wind Speed &amp; Gusts.</li>
                                <li><strong>Diurnal Projections:</strong> Generates 24-hour diurnal probability curves and weekly risk outlooks.</li>
                            </ul>
                        </div>

                        <div class="nf-detail-item">
                            <div class="nf-detail-head">
                                <strong>NusaFire FastAPI &amp; Laravel Fusion Engine</strong>
                                <span class="nf-tag">REST Services</span>
                            </div>
                            <p>High-performance backend orchestration service executing spatial joins and instant model inferences on demand.</p>
                            <ul class="nf-feature-list">
                                <li><strong>Internal Endpoints:</strong> <code>/internal/ai/realtime-overview</code>, <code>/internal/ai/predict-point</code>.</li>
                                <li><strong>Output:</strong> Calibrated provincial risk ratings, trend forecasts, and alert flags.</li>
                            </ul>
                        </div>
                    </article>
                </div>

                <!-- 9-Feature Table Matrix -->
                <article class="nf-panel">
                    <div class="nf-panel-header">
                        <div>
                            <div class="nf-panel-eyebrow">MODEL FEATURE VECTOR</div>
                            <h2>9 Environmental &amp; Geospatial Model Features</h2>
                            <p>Engineered inputs processed by the XGBoost Classifier to compute wildfire probability.</p>
                        </div>
                    </div>

                    <div class="nf-table-scroll">
                        <table class="nf-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Feature Name</th>
                                    <th>Description</th>
                                    <th>Unit</th>
                                    <th>Data Source</th>
                                    <th>Role in Fire Prediction</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(feat, idx) in featuresList" :key="feat.name">
                                    <td class="cell-rank">{{ idx + 1 }}</td>
                                    <td>
                                        <code class="nf-code">{{ feat.name }}</code>
                                    </td>
                                    <td><strong>{{ feat.label }}</strong></td>
                                    <td><span class="nf-badge-unit">{{ feat.unit }}</span></td>
                                    <td>{{ feat.source }}</td>
                                    <td class="cell-role">{{ feat.role }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </article>

                <!-- Navigation Action Cards -->
                <section class="nf-action-cards-grid">
                    <Link href="/hotspot-map" class="nf-action-card">
                        <div class="nf-action-icon">🛰️</div>
                        <div class="nf-action-text">
                            <strong>Hotspot Map</strong>
                            <span>Pure NASA FIRMS satellite observation &amp; historical dataset</span>
                        </div>
                        <span class="nf-action-arrow">→</span>
                    </Link>

                    <Link href="/weather-analysis" class="nf-action-card">
                        <div class="nf-action-icon">☀️</div>
                        <div class="nf-action-text">
                            <strong>Weather Analysis</strong>
                            <span>Pure Open-Meteo meteorological parameters &amp; climate summary</span>
                        </div>
                        <span class="nf-action-arrow">→</span>
                    </Link>

                    <Link href="/ai-prediction" class="nf-action-card card-ai">
                        <div class="nf-action-icon">⚡</div>
                        <div class="nf-action-text">
                            <strong>AI Prediction &amp; Risk Forecast</strong>
                            <span>Execute calibrated XGBoost model across all 38 provinces</span>
                        </div>
                        <span class="nf-action-arrow">→</span>
                    </Link>
                </section>
            </div>
        </div>
    </main>
</template>

<style scoped>
.nf-forestwatch-page {
    --page-bg: #f8fafc;
    --surface-bg: #ffffff;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --primary: #15803d;
    --primary-light: rgba(21, 128, 61, 0.08);
    display: flex;
    min-height: 100vh;
    background: var(--page-bg);
    color: var(--text-main);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.nf-forestwatch-page.theme-dark {
    --page-bg: #0b1319;
    --surface-bg: #13222d;
    --text-main: #f1f5f9;
    --text-muted: #94a3b8;
    --border-color: #1e3344;
    --primary: #22c55e;
    --primary-light: rgba(34, 197, 94, 0.12);
}

.nf-main {
    flex: 1;
    margin-left: 268px;
    display: flex;
    flex-direction: column;
    min-width: 0;
    transition: margin-left 0.25s ease;
}

.nf-main-collapsed {
    margin-left: 78px;
}

@media (max-width: 900px) {
    .nf-main {
        margin-left: 0 !important;
    }
}

/* Topbar */
.nf-topbar {
    height: 70px;
    padding: 0 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface-bg);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 50;
}

.nf-topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-topbar-left h1 {
    font-size: 19px;
    font-weight: 700;
    margin: 0;
}

.nf-topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nf-icon-button {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--surface-bg);
    color: var(--text-main);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.nf-icon-button:hover {
    background: var(--primary-light);
    color: var(--primary);
}

.nf-mobile-menu {
    display: none;
}

@media (max-width: 900px) {
    .nf-mobile-menu {
        display: flex;
    }
}

/* Page Content */
.nf-page-content {
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 22px;
}

/* Page Heading */
.nf-page-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.nf-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--primary);
    margin-bottom: 4px;
}

.nf-eyebrow-line {
    width: 14px;
    height: 2px;
    background: var(--primary);
    border-radius: 2px;
}

.nf-heading-text h1 {
    font-size: 27px;
    font-weight: 800;
    margin: 0 0 4px;
    letter-spacing: -0.02em;
}

.nf-heading-text p {
    font-size: 13.5px;
    color: var(--text-muted);
    margin: 0;
    max-width: 780px;
}

.nf-heading-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 18px;
    border-radius: 14px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
}

.nf-heading-card-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: var(--primary-light);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
}

.nf-heading-card-text {
    display: flex;
    flex-direction: column;
}

.nf-heading-card-text strong {
    font-size: 12.5px;
}

.nf-heading-card-text span {
    font-size: 11px;
    color: var(--text-muted);
}

/* Summary Grid */
.nf-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
}

.nf-summary-card {
    padding: 18px;
    border-radius: 16px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.nf-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.nf-card-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
}

.nf-card-icon {
    font-size: 18px;
}

.nf-card-value {
    font-size: 24px;
    font-weight: 800;
    color: var(--text-main);
}

.nf-card-sub {
    font-size: 11px;
    color: var(--text-muted);
}

/* Panels */
.nf-panel {
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 24px;
    display: flex;
    flex-direction: column;
}

.nf-panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 18px;
}

.nf-panel-eyebrow {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--primary);
    margin-bottom: 2px;
}

.nf-panel-header h2 {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 2px;
}

.nf-panel-header p {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
}

/* Pipeline Step Grid */
.nf-pipeline-steps-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    gap: 12px;
    align-items: center;
}

@media (max-width: 1100px) {
    .nf-pipeline-steps-grid {
        grid-template-columns: 1fr;
    }
    .nf-pipeline-arrow-col {
        display: none;
    }
}

.nf-pipeline-card {
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-height: 180px;
}

.nf-card-highlight {
    border-color: #86efac;
    background: rgba(22, 163, 74, 0.04);
}

.theme-dark .nf-card-highlight {
    border-color: #166534;
    background: rgba(34, 197, 94, 0.06);
}

.nf-step-badge {
    font-size: 9.5px;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--primary);
}

.badge-alert {
    color: #dc2626;
}

.nf-step-icon {
    font-size: 22px;
}

.nf-pipeline-card h4 {
    font-size: 13.5px;
    font-weight: 700;
    margin: 0;
}

.nf-pipeline-card p {
    font-size: 11px;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.45;
    flex: 1;
}

.nf-step-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.nf-step-tags span {
    font-size: 9.5px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    color: var(--text-main);
}

.nf-pipeline-arrow-col {
    font-size: 18px;
    color: var(--primary);
    font-weight: 700;
    text-align: center;
}

/* 3-Column Specifications Grid */
.nf-grid-3col {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

@media (max-width: 1050px) {
    .nf-grid-3col {
        grid-template-columns: 1fr;
    }
}

.nf-spec-card {
    gap: 16px;
}

.nf-spec-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 14px;
}

.nf-spec-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    display: grid;
    place-items: center;
    font-size: 19px;
    flex: 0 0 40px;
}

.nf-spec-header h2 {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 2px;
}

.nf-spec-header p {
    font-size: 11.5px;
    color: var(--text-muted);
    margin: 0;
}

.nf-detail-item {
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.nf-detail-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

.nf-detail-head strong {
    font-size: 12px;
    font-weight: 700;
}

.nf-tag {
    font-size: 9.5px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 5px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    white-space: nowrap;
}

.tag-model {
    background: var(--primary-light);
    color: var(--primary);
    border-color: rgba(21, 128, 61, 0.2);
}

.nf-detail-item p {
    font-size: 11px;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.45;
}

.nf-feature-list {
    margin: 0;
    padding-left: 14px;
    font-size: 10.5px;
    color: var(--text-muted);
    line-height: 1.5;
}

.nf-feature-list li code {
    background: var(--surface-bg);
    padding: 1px 4px;
    border-radius: 4px;
    font-size: 10px;
    color: var(--text-main);
    border: 1px solid var(--border-color);
}

/* Feature Table */
.nf-table-scroll {
    overflow-x: auto;
    border: 1px solid var(--border-color);
    border-radius: 12px;
}

.nf-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    text-align: left;
}

.nf-table th {
    background: var(--page-bg);
    padding: 10px 14px;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border-color);
}

.nf-table td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border-color);
    vertical-align: middle;
}

.nf-table tr:last-child td {
    border-bottom: 0;
}

.cell-rank {
    font-weight: 800;
    color: var(--text-muted);
    width: 36px;
}

.nf-code {
    background: var(--primary-light);
    color: var(--primary);
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 11px;
    font-family: monospace;
}

.nf-badge-unit {
    padding: 2px 7px;
    border-radius: 5px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    font-size: 10px;
    font-weight: 600;
    color: var(--text-muted);
}

.cell-role {
    font-size: 11.5px;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Navigation Action Cards */
.nf-action-cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

@media (max-width: 900px) {
    .nf-action-cards-grid {
        grid-template-columns: 1fr;
    }
}

.nf-action-card {
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    text-decoration: none;
    color: var(--text-main);
    transition: all 0.2s ease;
}

.nf-action-card:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}

.card-ai {
    background: var(--primary-light);
    border-color: rgba(21, 128, 61, 0.25);
}

.nf-action-icon {
    font-size: 24px;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    display: grid;
    place-items: center;
    flex: 0 0 42px;
}

.nf-action-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
    min-width: 0;
}

.nf-action-text strong {
    font-size: 13.5px;
}

.nf-action-text span {
    font-size: 11px;
    color: var(--text-muted);
}

.nf-action-arrow {
    font-size: 18px;
    font-weight: 700;
    color: var(--primary);
    transition: transform 0.2s;
}

.nf-action-card:hover .nf-action-arrow {
    transform: translateX(4px);
}
</style>
