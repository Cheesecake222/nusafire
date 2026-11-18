
<script setup lang="ts">

import { Head, Link } from '@inertiajs/vue3';
import { useTheme } from '@/composables/useTheme';

const { theme, toggleTheme } = useTheme();


</script>

<template>
    <Head title="NusaFire — Fire Early Warning & Environmental Intelligence" />

    <main class="landing-page" :class="`theme-${theme}`">
        <!-- NAVIGATION -->
        <header class="navbar">
            <a href="#home" class="brand">
                <span class="brand-icon">
                    <img
                        src="/logo.png"
                        alt="NusaFire Logo"
                        class="brand-logo-img"
                    />
                </span>

                <span class="brand-copy">
                    <strong>NusaFire</strong>
                    <small>FIRE EARLY WARNING</small>
                </span>
            </a>

            <nav class="nav-links">
                <a href="#about">About</a>
                <a href="#capabilities">Capabilities</a>
                <a href="#how-it-works">How It Works</a>
            </nav>

            <div class="nav-actions">
                <button
                    type="button"
                    class="theme-toggle"
                    @click="toggleTheme"
                    :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
                    :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
                >
                    <svg
                        v-if="theme === 'dark'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >
                        <circle cx="12" cy="12" r="4" />
                        <path
                            d="M12 2V4M12 20V22M4.93 4.93L6.34 6.34M17.66 17.66L19.07 19.07M2 12H4M20 12H22M4.93 19.07L6.34 17.66M17.66 6.34L19.07 4.93"
                        />
                    </svg>

                    <svg
                        v-else
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >
                        <path
                            d="M20.9 13A9 9 0 0 1 11 3.1A9 9 0 1 0 20.9 13Z"
                        />
                    </svg>
                </button>

                <Link href="/dashboard" class="nav-cta">
                    Explore Dashboard
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="7" y1="17" x2="17" y2="7" />
                        <polyline points="7 7 17 7 17 17" />
                    </svg>
                </Link>
            </div>
        </header>

        <!-- HERO -->
        <section id="home" class="hero section-container">
            <div class="hero-copy">
                <div class="eyebrow">
                    <span class="status-dot"></span>
                    AI &amp; SATELLITE EARLY WARNING SYSTEM
                </div>

                <h1>
                    See the signals.
                    <span>Protect the forests.</span>
                </h1>

                <p class="hero-description">
                    Environmental intelligence platform powered by active NASA FIRMS VIIRS (375m) satellites, Open-Meteo real-time meteorology, and XGBoost machine learning for wildfire risk prediction across 38 Indonesian provinces.
                </p>

                <div class="hero-actions">
                    <Link href="/dashboard" class="button-primary">
                        Explore NusaFire
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <line x1="5" y1="12" x2="19" y2="12" />
                            <polyline points="12 5 19 12 12 19" />
                        </svg>
                    </Link>

                    <a href="#capabilities" class="button-secondary">
                        Discover the platform
                    </a>
                </div>

                <div class="hero-footnote">
                    <span class="footnote-line"></span>
                    INTEGRATED SATELLITE &amp; AI INTELLIGENCE FOR TARGETED WILDFIRE MITIGATION
                </div>
            </div>

            <!-- PREVIEW PANEL -->
            <div class="preview-wrap">
                <article class="preview-card">
                    <div class="preview-header">
                        <div>
                            <span class="mini-label">NATIONAL MONITORING (38 PROVINCES)</span>
                            <h2>Indonesia Fire Watch</h2>
                        </div>

                        <span class="preview-badge">
                            <span></span>
                            LIVE AI &amp; SATELLITE
                        </span>
                    </div>

                    <div class="map-preview">
                        <div class="map-grid"></div>

                        <svg
                            class="indonesia-map"
                            viewBox="0 0 620 270"
                            fill="none"
                            role="img"
                            aria-label="Decorative illustration of the Indonesian archipelago"
                        >
                            <!-- Sumatra -->
                            <path
                                class="island"
                                d="M44 91L62 84L77 69L94 74L106 63L122 70L116 83L132 91L124 106L104 111L93 125L78 117L64 126L49 111L41 104Z"
                            />

                            <!-- Java -->
                            <path
                                class="island"
                                d="M185 136L210 130L232 140L224 151L199 155L181 147Z"
                            />

                            <!-- Kalimantan -->
                            <path
                                class="island"
                                d="M178 103L195 89L217 95L231 112L219 128L198 132L182 122L169 115Z"
                            />

                            <!-- Sulawesi -->
                            <path
                                class="island"
                                d="M268 105L283 94L300 101L312 95L326 107L316 119L299 120L289 134L276 123L264 120Z"
                            />

                            <!-- Papua -->
                            <path
                                class="island"
                                d="M427 102L451 91L472 99L483 113L471 127L448 122L436 132L421 119Z"
                            />

                            <!-- Maluku and Nusa Tenggara -->
                            <path
                                class="island"
                                d="M352 143L366 135L381 140L378 151L365 155L353 151Z"
                            />
                            <path
                                class="island"
                                d="M393 158L407 151L421 160L415 169L401 169Z"
                            />
                            <path
                                class="island"
                                d="M447 158L461 151L473 160L468 170L454 169Z"
                            />
                            <path
                                class="island"
                                d="M490 187L502 180L512 188L506 198L495 198Z"
                            />

                            <!-- Illustrative hotspot points -->
                            <g class="hotspot">
                                <circle cx="83" cy="95" r="11" />
                                <circle cx="83" cy="95" r="4" />
                            </g>
                            <g class="hotspot">
                                <circle cx="200" cy="112" r="11" />
                                <circle cx="200" cy="112" r="4" />
                            </g>
                            <g class="hotspot">
                                <circle cx="295" cy="111" r="11" />
                                <circle cx="295" cy="111" r="4" />
                            </g>
                            <g class="hotspot">
                                <circle cx="451" cy="108" r="11" />
                                <circle cx="451" cy="108" r="4" />
                            </g>
                        </svg>

                        <span class="map-label sumatra-label">SUMATRA</span>
                        <span class="map-label kalimantan-label">KALIMANTAN</span>
                        <span class="map-label papua-label">PAPUA</span>

                        <div class="map-legend">
                            <span></span>
                            Active Satellite Hotspots
                        </div>

                        <span class="map-disclaimer">
                            REGIONAL PREVIEW · NASA FIRMS &amp; AI
                        </span>
                    </div>

                    <div class="preview-footer">
                        <div class="preview-metric">
                            <span class="metric-icon coverage-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="2" y1="12" x2="22" y2="12" />
                                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                                </svg>
                            </span>
                            <div>
                                <span class="mini-label">DATA COVERAGE</span>
                                <strong>38 Indonesian Provinces</strong>
                            </div>
                        </div>

                        <div class="preview-metric">
                            <span class="metric-icon fire-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
                                </svg>
                            </span>
                            <div>
                                <span class="mini-label">DETECTION SENSOR</span>
                                <strong>NASA FIRMS VIIRS (375m)</strong>
                            </div>
                        </div>
                    </div>
                </article>

                <div class="floating-note">
                    <span class="floating-indicator"></span>
                    <div>
                        <span class="mini-label">SYSTEM STATUS</span>
                        <strong>XGBoost AI Model Active</strong>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION DIVIDER -->
        <div class="section-marker section-container">
            <span>01 / ABOUT PLATFORM</span>
            <a href="#about">
                SCROLL TO EXPLORE
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <polyline points="19 12 12 19 5 12" />
                </svg>
            </a>
        </div>

        <!-- ABOUT -->
        <section id="about" class="content-section section-container">
            <div class="section-heading">
                <span class="eyebrow">01 — ABOUT NUSAFIRE</span>
                <h2>Turning spatial data &amp; weather into <span>targeted mitigation decisions.</span></h2>
            </div>

            <p class="section-description">
                Wildfire mitigation requires faster, more comprehensive intelligence than reactive firefighting. NusaFire combines 375-meter resolution NASA FIRMS VIIRS thermal satellite feeds, real-time Open-Meteo weather telemetry, and predictive XGBoost machine learning to forecast daily hotspot probabilities across 38 Indonesian provinces, evaluate risk levels, and support coordinated preventive patrols.
            </p>
        </section>

        <!-- CAPABILITIES -->
        <section id="capabilities" class="content-section section-container">
            <div class="section-heading">
                <span class="eyebrow">02 — CAPABILITIES &amp; FEATURES</span>
                <h2>Three integrated pillars for <span>monitoring &amp; early warning.</span></h2>
            </div>

            <div class="capability-grid">
                <article class="capability-card">
                    <div class="capability-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <rect x="3" y="3" width="7" height="7" rx="1.5" />
                            <rect x="14" y="3" width="7" height="7" rx="1.5" />
                            <rect x="14" y="14" width="7" height="7" rx="1.5" />
                            <rect x="3" y="14" width="7" height="7" rx="1.5" />
                        </svg>
                    </div>
                    <span class="mini-label">01 / AI RISK PREDICTION</span>
                    <h3>Forest Fire Risk Prediction</h3>
                    <p>
                        Trained XGBoost machine learning model calculates daily wildfire probabilities across 38 provinces, 7-day risk trend forecasts, and provincial mitigation priority rankings.
                    </p>
                </article>

                <article class="capability-card">
                    <div class="capability-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="22" y1="12" x2="18" y2="12" />
                            <line x1="6" y1="12" x2="2" y2="12" />
                            <line x1="12" y1="6" x2="12" y2="2" />
                            <line x1="12" y1="22" x2="12" y2="18" />
                        </svg>
                    </div>
                    <span class="mini-label">02 / SATELLITE GEOSPATIAL</span>
                    <h3>Interactive Hotspot Map</h3>
                    <p>
                        Interactive Leaflet GIS mapping featuring live NASA FIRMS VIIRS (375m) feeds, Fire Radiative Power (FRP) metrics, confidence levels, region filtering, and CSV export.
                    </p>
                </article>

                <article class="capability-card">
                    <div class="capability-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
                        </svg>
                    </div>
                    <span class="mini-label">03 / REAL-TIME METEOROLOGY</span>
                    <h3>Weather &amp; Land Cover Analysis</h3>
                    <p>
                        Real-time meteorological monitoring (temperature, humidity, precipitation, wind speed) from Open-Meteo, with AI simulation on land cover sensitivity.
                    </p>
                </article>
            </div>
        </section>

        <!-- HOW IT WORKS -->
        <section id="how-it-works" class="content-section section-container">
            <div class="section-heading">
                <span class="eyebrow">03 — SYSTEM WORKFLOW</span>
                <h2>From multi-source data fusion to <span>actionable early warnings.</span></h2>
            </div>

            <div class="process-list">
                <article class="process-item">
                    <span class="process-number">01</span>
                    <div>
                        <h3>Acquire Satellite &amp; Weather Data</h3>
                        <p>
                            Continuous ingestion of thermal anomaly detections from NASA FIRMS VIIRS (375m) and daily meteorological telemetry from Open-Meteo across 38 provinces.
                        </p>
                    </div>
                </article>

                <article class="process-item">
                    <span class="process-number">02</span>
                    <div>
                        <h3>Data Fusion &amp; XGBoost AI Modeling</h3>
                        <p>
                            Synthesizing atmospheric variables, satellite FRP readings, and land cover classifications through calibrated machine learning algorithms to compute fire probabilities.
                        </p>
                    </div>
                </article>

                <article class="process-item">
                    <span class="process-number">03</span>
                    <div>
                        <h3>Visualization &amp; Mitigation Decisions</h3>
                        <p>
                            Delivering insights via an interactive dashboard, geospatial hotspot mapping, and categorized risk status (High / Moderate Risk) to guide field patrols.
                        </p>
                    </div>
                </article>
            </div>

            <div class="final-cta">
                <div>
                    <span class="eyebrow">READY TO EXPLORE?</span>
                    <h2>Start exploring the NusaFire platform today.</h2>
                    <p>
                        Access AI early warning predictions, monitor active satellite hotspots, and analyze real-time weather conditions across Indonesia.
                    </p>
                </div>

                <Link href="/dashboard" class="button-primary">
                    Explore Dashboard
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="5" y1="12" x2="19" y2="12" />
                        <polyline points="12 5 19 12 12 19" />
                    </svg>
                </Link>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="footer section-container">
            <a href="#home" class="brand footer-brand">
                <span class="brand-icon">
                    <img
                        src="/logo.png"
                        alt="NusaFire Logo"
                        class="brand-logo-img"
                    />
                </span>
                <span class="brand-copy">
                    <strong>NusaFire</strong>
                    <small>FIRE EARLY WARNING</small>
                </span>
            </a>

            <p>Indonesia Wildfire Intelligence &amp; Early Warning System Powered by Satellite &amp; AI.</p>

            <span class="footer-copy">© 2026 NUSAFIRE · INDONESIA FIRE INTELLIGENCE</span>
        </footer>
    </main>
</template>

<style>
/* =========================================
   NUSAFIRE GLOBAL THEME
   ========================================= */

:root {
    color-scheme: light;
    --nf-bg: #f3f6ef;
    --nf-surface: #fbfcf8;
    --nf-surface-raised: #e8f0e5;
    --nf-text: #152d20;
    --nf-muted: #52695a;
    --nf-subtle: #718779;
    --nf-border: #d0dfd0;
    --nf-accent: #28784c;
    --nf-accent-hover: #1f643e;
    --nf-accent-text: #ffffff;
    --nf-grid: rgba(47, 112, 70, 0.07);
    --nf-map: #c6e0ca;
    --nf-map-stroke: #5c9870;
    --nf-shadow: rgba(38, 66, 44, 0.08);
}

:root[data-theme='light'],
:root.theme-light,
.landing-page.theme-light {
    color-scheme: light;
    --nf-bg: #f3f6ef;
    --nf-surface: #fbfcf8;
    --nf-surface-raised: #e8f0e5;
    --nf-text: #152d20;
    --nf-muted: #52695a;
    --nf-subtle: #718779;
    --nf-border: #d0dfd0;
    --nf-accent: #28784c;
    --nf-accent-hover: #1f643e;
    --nf-accent-text: #ffffff;
    --nf-grid: rgba(47, 112, 70, 0.07);
    --nf-map: #c6e0ca;
    --nf-map-stroke: #5c9870;
    --nf-shadow: rgba(38, 66, 44, 0.08);
}

:root[data-theme='dark'],
:root.theme-dark,
:root.dark,
.landing-page.theme-dark {
    color-scheme: dark;
    --nf-bg: #07120e;
    --nf-surface: #0b1913;
    --nf-surface-raised: #10231a;
    --nf-text: #f1f6f1;
    --nf-muted: #aabbb0;
    --nf-subtle: #71877a;
    --nf-border: #203b2d;
    --nf-accent: #82d8a5;
    --nf-accent-hover: #a0e8bb;
    --nf-accent-text: #07150d;
    --nf-grid: rgba(126, 199, 151, 0.055);
    --nf-map: #24563f;
    --nf-map-stroke: #65a985;
    --nf-shadow: rgba(0, 0, 0, 0.18);
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background: var(--nf-bg);
    color: var(--nf-text);
    font-family:
        Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}

button,
a {
    font: inherit;
}

button:focus-visible,
a:focus-visible {
    outline: 2px solid var(--nf-accent);
    outline-offset: 4px;
}

.landing-page {
    min-height: 100vh;
    overflow: hidden;
    background:
        radial-gradient(
            ellipse at 75% 43%,
            color-mix(in srgb, var(--nf-accent) 5%, transparent),
            transparent 45%
        ),
        var(--nf-bg);
    color: var(--nf-text);
    transition: background-color 0.25s ease, color 0.25s ease;
}

.section-container {
    width: min(1450px, calc(100% - 14%));
    margin-inline: auto;
}

/* NAVIGATION */

.navbar {
    min-height: 92px;
    padding-inline: 7%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 28px;
    border-bottom: 1px solid var(--nf-border);
    background: var(--nf-bg);
}

.brand {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    color: var(--nf-text);
    text-decoration: none;
    flex-shrink: 0;
}

.brand-icon {
    width: 46px;
    height: 46px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.brand-logo-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}

.brand-copy {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.brand-copy strong {
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -1.2px;
    line-height: 1;
}

.brand-copy small {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--nf-subtle);
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 38px;
}

.nav-links a {
    color: var(--nf-muted);
    text-decoration: none;
    font-size: 13px;
    transition: color 0.2s ease;
}

.nav-links a:hover {
    color: var(--nf-accent);
}

.nav-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.theme-toggle {
    width: 43px;
    height: 43px;
    display: inline-grid;
    place-items: center;
    border: 1px solid var(--nf-border);
    border-radius: 9px;
    background: var(--nf-surface);
    color: var(--nf-text);
    cursor: pointer;
    transition: 0.2s ease;
}

.theme-toggle:hover {
    border-color: var(--nf-accent);
    color: var(--nf-accent);
}

.theme-toggle svg {
    width: 20px;
    height: 20px;
}

.nav-cta,
.button-primary,
.button-secondary {
    min-height: 48px;
    padding: 0 19px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 750;
    text-decoration: none;
    transition:
        background-color 0.2s ease,
        color 0.2s ease,
        border-color 0.2s ease,
        transform 0.2s ease;
}

.nav-cta {
    border: 1px solid var(--nf-map-stroke);
    color: var(--nf-text);
    background: transparent;
}

.nav-cta:hover,
.button-secondary:hover {
    border-color: var(--nf-accent);
    color: var(--nf-accent);
}

.nav-cta svg,
.button-primary svg {
    flex-shrink: 0;
    display: block;
}

/* HERO */

.hero {
    min-height: 710px;
    padding-block: 90px 85px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 7%;
}

.hero-copy {
    min-width: 0;
}

.eyebrow {
    display: flex;
    align-items: center;
    gap: 11px;
    color: var(--nf-accent);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    line-height: 1.6;
}

.status-dot {
    width: 8px;
    height: 8px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--nf-accent);
    box-shadow: 0 0 13px color-mix(in srgb, var(--nf-accent) 55%, transparent);
}

.hero h1 {
    margin: 36px 0 22px;
    font-size: clamp(42px, 4.4vw, 76px);
    font-weight: 850;
    letter-spacing: -0.065em;
    line-height: 1.12;
}

.hero h1 span {
    display: block;
    color: var(--nf-accent);
}

.hero-description {
    max-width: 510px;
    margin: 0;
    color: var(--nf-muted);
    font-size: 15px;
    line-height: 2.05;
}

.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 13px;
    margin-top: 32px;
}

.button-primary {
    min-height: 54px;
    padding-inline: 23px;
    background: var(--nf-accent);
    color: var(--nf-accent-text);
    border: 1px solid var(--nf-accent);
}

.button-primary:hover {
    background: var(--nf-accent-hover);
    border-color: var(--nf-accent-hover);
    transform: translateY(-2px);
}

.button-secondary {
    min-height: 54px;
    border: 1px solid var(--nf-border);
    color: var(--nf-text);
    background: transparent;
}

.hero-footnote {
    margin-top: 51px;
    display: flex;
    align-items: center;
    gap: 13px;
    color: var(--nf-subtle);
    font-size: 9px;
    font-weight: 750;
    letter-spacing: 2px;
}

.footnote-line {
    width: 32px;
    height: 1px;
    background: var(--nf-accent);
}

/* PREVIEW */

.preview-wrap {
    position: relative;
    min-width: 0;
    padding-bottom: 12px;
}

.preview-card {
    overflow: hidden;
    border: 1px solid var(--nf-border);
    border-radius: 10px;
    background: var(--nf-surface);
    box-shadow: 0 22px 70px var(--nf-shadow);
}

.preview-header {
    min-height: 103px;
    padding: 25px 23px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    border-bottom: 1px solid var(--nf-border);
}

.mini-label {
    display: block;
    color: var(--nf-subtle);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.7px;
}

.preview-header h2 {
    margin: 13px 0 0;
    font-size: 16px;
    letter-spacing: -0.4px;
}

.preview-badge {
    padding: 8px 10px;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    border: 1px solid rgba(246, 166, 35, 0.3);
    border-radius: 3px;
    color: #e9ad42;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
}

.preview-badge span,
.map-legend span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #f6a623;
}

.map-preview {
    height: 310px;
    position: relative;
    overflow: hidden;
    background: var(--nf-surface);
}

.map-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(var(--nf-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--nf-grid) 1px, transparent 1px);
    background-size: 36px 36px;
}

.indonesia-map {
    position: absolute;
    inset: 12px 3% 20px;
    width: 94%;
    height: calc(100% - 32px);
    overflow: visible;
}

.island {
    fill: var(--nf-map);
    stroke: var(--nf-map-stroke);
    stroke-width: 1.4;
    opacity: 0.92;
}

.hotspot circle:first-child {
    fill: rgba(246, 166, 35, 0.22);
    stroke: rgba(246, 166, 35, 0.45);
    stroke-width: 1;
}

.hotspot circle:last-child {
    fill: #f6a623;
    stroke: rgba(255, 230, 172, 0.8);
    stroke-width: 2;
}

.map-label {
    position: absolute;
    color: var(--nf-subtle);
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

.sumatra-label {
    left: 10%;
    top: 38%;
}

.kalimantan-label {
    left: 37%;
    top: 53%;
}

.papua-label {
    right: 9%;
    top: 66%;
}

.map-legend {
    position: absolute;
    right: 14px;
    bottom: 38px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    border: 1px solid var(--nf-border);
    border-radius: 3px;
    background: var(--nf-surface);
    color: var(--nf-text);
    font-size: 9px;
}

.map-disclaimer {
    position: absolute;
    left: 15px;
    bottom: 14px;
    color: var(--nf-subtle);
    font-size: 8px;
    font-weight: 750;
    letter-spacing: 1.3px;
}

.preview-footer {
    display: grid;
    grid-template-columns: 1fr 1fr;
    border-top: 1px solid var(--nf-border);
}

.preview-metric {
    min-height: 70px;
    padding: 13px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.preview-metric + .preview-metric {
    border-left: 1px solid var(--nf-border);
}

.metric-icon {
    width: 36px;
    height: 36px;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    line-height: 0;
}

.metric-icon svg {
    display: block;
    margin: auto;
}

.coverage-icon {
    background: var(--nf-surface-raised);
    color: var(--nf-accent);
}

.fire-icon {
    background: rgba(246, 166, 35, 0.1);
    color: #e7a43c;
}

.preview-metric strong {
    display: block;
    margin-top: 7px;
    font-size: 11px;
}

.floating-note {
    position: absolute;
    right: -18px;
    bottom: -9px;
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 15px;
    border: 1px solid var(--nf-border);
    border-radius: 5px;
    background: var(--nf-surface-raised);
    box-shadow: 0 12px 35px var(--nf-shadow);
}

.floating-indicator {
    width: 12px;
    height: 12px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--nf-accent);
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--nf-accent) 12%, transparent);
}

.floating-note strong {
    display: block;
    margin-top: 7px;
    font-size: 11px;
}

/* SECTION MARKER */

.section-marker {
    min-height: 75px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    border-top: 1px solid var(--nf-border);
    color: var(--nf-subtle);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.8px;
}

.section-marker a {
    display: flex;
    gap: 14px;
    align-items: center;
    color: var(--nf-muted);
    text-decoration: none;
}

.section-marker a span {
    color: var(--nf-accent);
    font-size: 18px;
}

/* CONTENT SECTIONS */

.content-section {
    padding-block: 105px;
    border-bottom: 1px solid var(--nf-border);
    scroll-margin-top: 35px;
}

.section-heading {
    max-width: 760px;
}

.section-heading h2,
.final-cta h2 {
    margin: 22px 0 0;
    font-size: clamp(30px, 3.6vw, 49px);
    line-height: 1.18;
    letter-spacing: -0.045em;
}

.section-heading h2 span {
    color: var(--nf-accent);
}

.section-description {
    max-width: 730px;
    margin-top: 24px;
    color: var(--nf-muted);
    font-size: 15px;
    line-height: 2;
}

.capability-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin-top: 44px;
}

.capability-card {
    padding: 29px;
    border: 1px solid var(--nf-border);
    border-radius: 6px;
    background: var(--nf-surface);
    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}

.capability-card:hover {
    transform: translateY(-4px);
    border-color: var(--nf-map-stroke);
}

.capability-icon {
    width: 46px;
    height: 46px;
    margin-bottom: 30px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 5px;
    background: var(--nf-surface-raised);
    color: var(--nf-accent);
    line-height: 0;
}

.capability-icon svg {
    display: block;
    margin: auto;
}

.capability-card h3,
.process-item h3 {
    margin: 16px 0 10px;
    font-size: 18px;
}

.capability-card p,
.process-item p,
.final-cta p {
    margin: 0;
    color: var(--nf-muted);
    font-size: 13px;
    line-height: 1.9;
}

.process-list {
    margin-top: 45px;
    border-top: 1px solid var(--nf-border);
}

.process-item {
    padding: 28px 0;
    display: grid;
    grid-template-columns: 75px 1fr;
    gap: 20px;
    border-bottom: 1px solid var(--nf-border);
}

.process-number {
    color: var(--nf-accent);
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1px;
}

.process-item h3 {
    margin-top: 0;
}

.final-cta {
    margin-top: 65px;
    padding: 38px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
    border: 1px solid var(--nf-border);
    border-radius: 6px;
    background: var(--nf-surface);
}

.final-cta h2 {
    margin-block: 13px;
    font-size: 30px;
}

.final-cta p {
    max-width: 520px;
}

/* FOOTER */

.footer {
    min-height: 125px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
}

.footer p {
    color: var(--nf-muted);
    font-size: 12px;
}

.footer-copy {
    color: var(--nf-subtle);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

/* RESPONSIVE */

@media (max-width: 1100px) {
    .section-container {
        width: calc(100% - 9%);
    }

    .navbar {
        padding-inline: 4.5%;
    }

    .nav-links {
        gap: 20px;
    }

    .hero {
        gap: 4%;
    }

    .hero h1 {
        font-size: clamp(40px, 5vw, 60px);
    }

    .floating-note {
        right: -7px;
    }
}

@media (max-width: 800px) {
    .navbar {
        min-height: 78px;
        flex-wrap: wrap;
        gap: 15px;
        padding-block: 15px;
    }

    .brand-icon {
        width: 35px;
        height: 39px;
    }

    .brand-copy strong {
        font-size: 20px;
    }

    .nav-links {
        order: 3;
        width: 100%;
        justify-content: center;
        gap: 28px;
        padding-top: 5px;
    }

    .nav-links a {
        font-size: 12px;
    }

    .nav-cta {
        min-height: 42px;
        padding-inline: 12px;
        gap: 8px;
        font-size: 11px;
    }

    .theme-toggle {
        width: 40px;
        height: 40px;
    }

    .hero {
        min-height: auto;
        padding-block: 70px 85px;
        grid-template-columns: 1fr;
        gap: 65px;
    }

    .hero h1 {
        max-width: 700px;
        font-size: clamp(45px, 8vw, 68px);
    }

    .hero-description {
        max-width: 600px;
    }

    .preview-wrap {
        width: 100%;
        max-width: 650px;
        margin-inline: auto;
    }

    .capability-grid {
        grid-template-columns: 1fr;
    }

    .capability-card {
        padding: 25px;
    }

    .capability-icon {
        margin-bottom: 20px;
    }

    .content-section {
        padding-block: 75px;
    }
}

@media (max-width: 480px) {
    .section-container {
        width: calc(100% - 36px);
    }

    .navbar {
        padding-inline: 18px;
    }

    .brand {
        gap: 8px;
    }

    .brand-copy small {
        font-size: 7px;
        letter-spacing: 1.3px;
    }

    .nav-cta {
        font-size: 0;
        gap: 0;
        width: 40px;
        padding: 0;
    }

    .nav-cta span {
        font-size: 20px;
    }

    .nav-links {
        justify-content: space-between;
        gap: 12px;
    }

    .nav-links a {
        font-size: 11px;
    }

    .hero {
        padding-block: 55px 65px;
        gap: 48px;
    }

    .eyebrow {
        font-size: 9px;
        letter-spacing: 1.3px;
    }

    .hero h1 {
        margin-top: 26px;
        font-size: clamp(39px, 10vw, 48px);
    }

    .hero-description {
        font-size: 13px;
        line-height: 1.9;
    }

    .hero-actions {
        align-items: stretch;
        flex-direction: column;
    }

    .hero-actions a {
        width: 100%;
        box-sizing: border-box;
    }

    .hero-footnote {
        margin-top: 35px;
        font-size: 8px;
        letter-spacing: 1px;
    }

    .preview-header {
        padding: 18px 14px;
    }

    .preview-header h2 {
        font-size: 14px;
    }

    .preview-badge {
        padding: 7px;
        font-size: 8px;
    }

    .map-preview {
        height: 245px;
    }

    .preview-metric {
        padding: 10px 8px;
        gap: 7px;
    }

    .metric-icon {
        width: 29px;
        height: 29px;
    }

    .preview-metric .mini-label {
        font-size: 7px;
        letter-spacing: 0.8px;
    }

    .preview-metric strong {
        font-size: 9px;
    }

    .floating-note {
        right: -3px;
        bottom: -20px;
        padding: 11px;
    }

    .floating-note strong {
        font-size: 9px;
    }

    .section-marker {
        font-size: 8px;
        letter-spacing: 0.8px;
    }

    .section-marker a {
        gap: 6px;
    }

    .content-section {
        padding-block: 65px;
    }

    .section-heading h2 {
        font-size: 32px;
    }

    .section-description {
        font-size: 13px;
    }

    .process-item {
        grid-template-columns: 35px 1fr;
        gap: 10px;
    }

    .final-cta {
        padding: 24px;
        align-items: stretch;
        flex-direction: column;
    }

    .final-cta h2 {
        font-size: 27px;
    }

    .final-cta .button-primary {
        align-self: flex-start;
    }

    .footer {
        padding-block: 25px;
        align-items: flex-start;
        flex-direction: column;
        gap: 12px;
    }

    .footer p {
        margin: 0;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
