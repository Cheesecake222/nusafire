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
                            <span class="nf-card-icon nf-icon-green">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <rect x="4" y="4" width="16" height="16" rx="2" />
                                    <rect x="9" y="9" width="6" height="6" />
                                    <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
                                </svg>
                            </span>
                        </div>
                        <div class="nf-card-value">XGBoost</div>
                        <div class="nf-card-sub">150 Estimators · Tuned Gradient Boosting</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Training Datasets</span>
                            <span class="nf-card-icon nf-icon-orange">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <ellipse cx="12" cy="5" rx="9" ry="3" />
                                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                                </svg>
                            </span>
                        </div>
                        <div class="nf-card-value">3 Sources</div>
                        <div class="nf-card-sub">NASA FIRMS, NASA POWER, MapBiomas</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Real-Time APIs</span>
                            <span class="nf-card-icon nf-icon-blue">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="2" y1="12" x2="22" y2="12" />
                                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                                </svg>
                            </span>
                        </div>
                        <div class="nf-card-value">2 Live Feeds</div>
                        <div class="nf-card-sub">NASA FIRMS (VIIRS 375m) &amp; Open-Meteo</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Monitored Scope</span>
                            <span class="nf-card-icon nf-icon-yellow">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="22" y1="12" x2="18" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="6" y1="12" x2="2" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="6" x2="12" y2="2" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="22" x2="12" y2="18" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
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
                            <div class="nf-step-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <path d="M4 11a9 9 0 0 1 9 9" stroke-linecap="round" />
                                    <path d="M4 4a16 16 0 0 1 16 16" stroke-linecap="round" />
                                    <circle cx="5" cy="19" r="1.5" fill="currentColor" />
                                </svg>
                            </div>
                            <h4>Multi-Source Ingestion</h4>
                            <p>Near real-time retrieval of active thermal anomalies via <strong>NASA FIRMS API</strong> (VIIRS 375m &amp; MODIS) combined with hourly &amp; 14-day forecasts from <strong>Open-Meteo API</strong>.</p>
                            <div class="nf-step-tags">
                                <span>NASA FIRMS</span>
                                <span>Open-Meteo API</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" aria-hidden="true">
                                <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <polyline points="12 5 19 12 12 19" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>

                        <div class="nf-pipeline-card">
                            <div class="nf-step-badge">STEP 02</div>
                            <div class="nf-step-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="8" y1="2" x2="8" y2="18" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="16" y1="6" x2="16" y2="22" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </div>
                            <h4>Spatial &amp; Biomass Fusion</h4>
                            <p>Spatial join matching coordinates with <strong>MapBiomas 2024 LULC</strong> raster to determine fuel flammability, peat depth vulnerability, and canopy moisture retention.</p>
                            <div class="nf-step-tags">
                                <span>MapBiomas LULC</span>
                                <span>Peat Depth</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" aria-hidden="true">
                                <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <polyline points="12 5 19 12 12 19" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>

                        <div class="nf-pipeline-card">
                            <div class="nf-step-badge">STEP 03</div>
                            <div class="nf-step-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <rect x="4" y="4" width="16" height="16" rx="2" />
                                    <rect x="9" y="9" width="6" height="6" />
                                    <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" stroke-linecap="round" />
                                </svg>
                            </div>
                            <h4>XGBoost ML Inference</h4>
                            <p>A 9-feature environmental vector is fed into the <strong>XGBoost Classifier</strong> (150 trees, threshold 0.35) producing calibrated fire probabilities.</p>
                            <div class="nf-step-tags">
                                <span>XGBoost</span>
                                <span>Threshold 0.35</span>
                            </div>
                        </div>

                        <div class="nf-pipeline-arrow-col">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" aria-hidden="true">
                                <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <polyline points="12 5 19 12 12 19" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>

                        <div class="nf-pipeline-card nf-card-highlight">
                            <div class="nf-step-badge badge-alert">STEP 04</div>
                            <div class="nf-step-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke-linecap="round" stroke-linejoin="round" />
                                    <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </div>
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
                            <div class="nf-spec-icon icon-data">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <ellipse cx="12" cy="5" rx="9" ry="3" />
                                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                                </svg>
                            </div>
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
                            <div class="nf-spec-icon icon-ai">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <rect x="4" y="4" width="16" height="16" rx="2" />
                                    <rect x="9" y="9" width="6" height="6" />
                                    <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" stroke-linecap="round" />
                                </svg>
                            </div>
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
                            <div class="nf-spec-icon icon-api">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="2" y1="12" x2="22" y2="12" />
                                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                                </svg>
                            </div>
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
                        <div class="nf-action-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" />
                                <line x1="22" y1="12" x2="18" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <line x1="6" y1="12" x2="2" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <line x1="12" y1="6" x2="12" y2="2" stroke-linecap="round" stroke-linejoin="round" />
                                <line x1="12" y1="22" x2="12" y2="18" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
                        <div class="nf-action-text">
                            <strong>Hotspot Map</strong>
                            <span>Pure NASA FIRMS satellite observation &amp; historical dataset</span>
                        </div>
                        <span class="nf-action-arrow">→</span>
                    </Link>

                    <Link href="/weather-analysis" class="nf-action-card">
                        <div class="nf-action-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                <circle cx="12" cy="12" r="5" />
                                <line x1="12" y1="1" x2="12" y2="3" stroke-linecap="round" />
                                <line x1="12" y1="21" x2="12" y2="23" stroke-linecap="round" />
                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke-linecap="round" />
                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke-linecap="round" />
                                <line x1="1" y1="12" x2="3" y2="12" stroke-linecap="round" />
                                <line x1="21" y1="12" x2="23" y2="12" stroke-linecap="round" />
                                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke-linecap="round" />
                                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke-linecap="round" />
                            </svg>
                        </div>
                        <div class="nf-action-text">
                            <strong>Weather Analysis</strong>
                            <span>Pure Open-Meteo meteorological parameters &amp; climate summary</span>
                        </div>
                        <span class="nf-action-arrow">→</span>
                    </Link>

                    <Link href="/ai-prediction" class="nf-action-card card-ai">
                        <div class="nf-action-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" aria-hidden="true">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
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
    --page-bg: #f5f7f4;
    --surface-bg: #ffffff;
    --text-main: #1c2922;
    --text-muted: #526158;
    --border-color: #e5eae4;
    --primary: #2d8a5b;
    --primary-light: rgba(45, 138, 91, 0.08);

    --db-bg: #f5f7f4;
    --db-surface: #fff;
    --db-surface-soft: #f8faf7;
    --db-text: #1c2922;
    --db-text-soft: #526158;
    --db-muted: #859087;
    --db-border: #e5eae4;
    --db-accent: #2d8a5b;
    --db-accent-soft: #e8f5ec;

    display: flex;
    min-height: 100vh;
    background: var(--page-bg);
    color: var(--text-main);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.nf-forestwatch-page.theme-dark,
html.theme-dark .nf-forestwatch-page,
html.dark .nf-forestwatch-page {
    --page-bg: #111914;
    --surface-bg: #19231c;
    --text-main: #edf4ed;
    --text-muted: #b0bdb2;
    --border-color: #2b3a2e;
    --primary: #70cf98;
    --primary-light: rgba(112, 207, 152, 0.12);

    --db-bg: #111914;
    --db-surface: #19231c;
    --db-surface-soft: #1d2921;
    --db-text: #edf4ed;
    --db-text-soft: #b0bdb2;
    --db-muted: #849489;
    --db-border: #2b3a2e;
    --db-accent: #70cf98;
    --db-accent-soft: #213b2b;
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
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 9px;
    flex-shrink: 0;
}

.nf-icon-orange {
    color: #d27d42;
    background: #fff0e3;
}

.nf-icon-yellow {
    color: #c49a31;
    background: #fff6d9;
}

.nf-icon-green {
    color: #2f9860;
    background: #e5f5e9;
}

.nf-icon-blue {
    color: #508ec5;
    background: #e7f3ff;
}

.theme-dark .nf-icon-orange,
html.dark .nf-icon-orange {
    color: #f97316;
    background: rgba(249, 115, 22, 0.15);
}

.theme-dark .nf-icon-yellow,
html.dark .nf-icon-yellow {
    color: #fbbf24;
    background: rgba(251, 191, 36, 0.15);
}

.theme-dark .nf-icon-green,
html.dark .nf-icon-green {
    color: #70cf98;
    background: rgba(112, 207, 152, 0.15);
}

.theme-dark .nf-icon-blue,
html.dark .nf-icon-blue {
    color: #60a5fa;
    background: rgba(96, 165, 250, 0.15);
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
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    flex-shrink: 0;
}

.nf-pipeline-card.nf-card-highlight .nf-step-icon {
    color: #dc2626;
    border-color: rgba(220, 38, 38, 0.25);
    background: rgba(220, 38, 38, 0.06);
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
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
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
    color: var(--primary);
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
    border-color: color-mix(in srgb, var(--primary) 35%, transparent);
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
    border-color: color-mix(in srgb, var(--primary) 35%, transparent);
}

.nf-action-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    display: grid;
    place-items: center;
    color: var(--primary);
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


/* NusaFire Forest Watch visual polish — CSS only */
.nf-forestwatch-page {
    background:
        radial-gradient(ellipse at 8% 4%, rgba(217, 174, 72, 0.10), transparent 28%),
        radial-gradient(ellipse at 88% 16%, rgba(45, 138, 91, 0.10), transparent 30%),
        var(--page-bg);
}

.nf-forestwatch-page .nf-topbar {
    background: color-mix(in srgb, var(--surface-bg) 91%, transparent);
    backdrop-filter: blur(16px);
    border-bottom-color: color-mix(in srgb, var(--primary) 22%, var(--border-color));
    box-shadow: 0 4px 22px rgba(24, 56, 37, 0.035);
}

.nf-forestwatch-page .nf-topbar-left h1 {
    background: linear-gradient(100deg, var(--text-main) 12%, var(--primary) 82%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.nf-forestwatch-page .nf-icon-button {
    transition: transform .22s ease, box-shadow .22s ease, background .22s ease, border-color .22s ease;
}

.nf-forestwatch-page .nf-icon-button:hover {
    transform: translateY(-2px);
    border-color: color-mix(in srgb, var(--primary) 45%, var(--border-color));
    box-shadow: 0 7px 18px rgba(45, 138, 91, .12);
}

.nf-forestwatch-page .nf-page-content {
    position: relative;
    isolation: isolate;
}

.nf-forestwatch-page .nf-page-heading {
    animation: fw-rise-in .55s ease both;
}

.nf-forestwatch-page .nf-eyebrow-line {
    width: 24px;
    background: linear-gradient(90deg, #d7ad46, var(--primary));
    box-shadow: 0 0 12px rgba(215, 173, 70, .32);
}

.nf-forestwatch-page .nf-heading-text h1 {
    text-wrap: balance;
}

.nf-forestwatch-page .nf-heading-card {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(125deg, color-mix(in srgb, var(--primary-light) 55%, var(--surface-bg)), var(--surface-bg) 72%);
    border-color: color-mix(in srgb, var(--primary) 28%, var(--border-color));
    box-shadow: 0 9px 28px rgba(34, 88, 56, .07);
}

.nf-forestwatch-page .nf-heading-card::after {
    content: "";
    position: absolute;
    top: -55%;
    right: -20%;
    width: 110px;
    height: 190%;
    transform: rotate(28deg);
    background: linear-gradient(90deg, transparent, rgba(225, 190, 100, .12), transparent);
    pointer-events: none;
}

.nf-forestwatch-page .nf-heading-card-icon {
    background: linear-gradient(145deg, color-mix(in srgb, var(--primary) 16%, var(--surface-bg)), var(--primary-light));
    box-shadow: 0 0 0 5px color-mix(in srgb, var(--primary-light) 60%, transparent);
}

.nf-forestwatch-page .nf-summary-card {
    position: relative;
    overflow: hidden;
    border-color: color-mix(in srgb, var(--primary) 15%, var(--border-color));
    box-shadow: 0 5px 18px rgba(27, 66, 43, .035);
    animation: fw-rise-in .55s ease both;
    transition: transform .24s ease, box-shadow .24s ease, border-color .24s ease;
}

.nf-forestwatch-page .nf-summary-card:nth-child(2) { animation-delay: .07s; }
.nf-forestwatch-page .nf-summary-card:nth-child(3) { animation-delay: .14s; }
.nf-forestwatch-page .nf-summary-card:nth-child(4) { animation-delay: .21s; }

.nf-forestwatch-page .nf-summary-card::before {
    content: "";
    position: absolute;
    inset: 0 auto auto 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), #d9b653 70%, transparent);
    opacity: .7;
}

.nf-forestwatch-page .nf-summary-card:hover {
    transform: translateY(-4px);
    border-color: color-mix(in srgb, var(--primary) 38%, var(--border-color));
    box-shadow: 0 14px 30px rgba(27, 66, 43, .09);
}

.nf-forestwatch-page .nf-card-icon {
    transition: transform .25s ease, box-shadow .25s ease;
}

.nf-forestwatch-page .nf-summary-card:hover .nf-card-icon {
    transform: translateY(-2px) rotate(-4deg);
    box-shadow: 0 5px 12px rgba(33, 91, 55, .10);
}

.nf-forestwatch-page .nf-panel {
    position: relative;
    border-color: color-mix(in srgb, var(--primary) 14%, var(--border-color));
    box-shadow: 0 7px 24px rgba(27, 66, 43, .035);
    animation: fw-rise-in .62s ease both;
    transition: border-color .22s ease, box-shadow .22s ease;
}

.nf-forestwatch-page .nf-panel:hover {
    border-color: color-mix(in srgb, var(--primary) 28%, var(--border-color));
    box-shadow: 0 11px 28px rgba(27, 66, 43, .055);
}

.nf-forestwatch-page .nf-panel-eyebrow {
    color: var(--primary);
}

.nf-forestwatch-page .nf-spec-icon,
.nf-forestwatch-page .nf-step-icon,
.nf-forestwatch-page .nf-action-icon {
    transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}

.nf-forestwatch-page .nf-spec-card:hover .nf-spec-icon,
.nf-forestwatch-page .nf-pipeline-card:hover .nf-step-icon,
.nf-forestwatch-page .nf-action-card:hover .nf-action-icon {
    transform: translateY(-2px);
    border-color: color-mix(in srgb, var(--primary) 38%, var(--border-color));
    box-shadow: 0 5px 14px rgba(45, 138, 91, .10);
}

.nf-forestwatch-page .nf-pipeline-card {
    transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}

.nf-forestwatch-page .nf-pipeline-card:hover {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--primary) 35%, var(--border-color));
    box-shadow: 0 9px 20px rgba(27, 66, 43, .055);
}

.nf-forestwatch-page .nf-card-highlight {
    background:
        radial-gradient(ellipse at 100% 0%, rgba(217, 174, 72, .09), transparent 48%),
        color-mix(in srgb, var(--primary-light) 50%, var(--surface-bg));
}

.nf-forestwatch-page .nf-action-card {
    box-shadow: 0 4px 15px rgba(27, 66, 43, .035);
}

.nf-forestwatch-page .nf-action-card:hover {
    box-shadow: 0 12px 26px rgba(27, 66, 43, .085);
}

.nf-forestwatch-page .nf-table-scroll {
    border-color: color-mix(in srgb, var(--primary) 16%, var(--border-color));
    border-radius: 12px;
}

.nf-forestwatch-page .nf-table thead th {
    background: color-mix(in srgb, var(--primary-light) 78%, var(--surface-bg));
}

.nf-forestwatch-page .nf-table tbody tr {
    transition: background .18s ease;
}

.nf-forestwatch-page .nf-table tbody tr:hover {
    background: color-mix(in srgb, var(--primary-light) 55%, transparent);
}

.nf-forestwatch-page.theme-dark {
    background:
        radial-gradient(ellipse at 8% 4%, rgba(214, 174, 75, .055), transparent 29%),
        radial-gradient(ellipse at 88% 16%, rgba(75, 173, 112, .075), transparent 30%),
        var(--page-bg);
}

.nf-forestwatch-page.theme-dark .nf-heading-card,
.nf-forestwatch-page.theme-dark .nf-summary-card,
.nf-forestwatch-page.theme-dark .nf-panel,
.nf-forestwatch-page.theme-dark .nf-action-card {
    box-shadow: 0 8px 24px rgba(0, 0, 0, .12);
}

.nf-forestwatch-page.theme-dark .nf-summary-card:hover,
.nf-forestwatch-page.theme-dark .nf-panel:hover,
.nf-forestwatch-page.theme-dark .nf-action-card:hover {
    box-shadow: 0 13px 30px rgba(0, 0, 0, .2);
}

@keyframes fw-rise-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
    .nf-forestwatch-page *,
    .nf-forestwatch-page *::before,
    .nf-forestwatch-page *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
        scroll-behavior: auto !important;
    }
}

@media (max-width: 700px) {
    .nf-forestwatch-page .nf-page-content {
        padding: 18px 14px;
    }

    .nf-forestwatch-page .nf-heading-card {
        width: 100%;
    }
}

</style>
