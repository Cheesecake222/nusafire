
<script setup lang="ts">

import { ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import { useTheme } from '@/composables/useTheme';

const { theme, toggleTheme } = useTheme();
const globeFocused = ref(false);
const globeFocusActive = ref(false);
const globeFocusReady = ref(false);
const globeFocusStyle = ref<Record<string, string>>({});

function focusGlobe(event: MouseEvent) {
    if (globeFocusActive.value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const sphere = event.currentTarget as HTMLElement;
    const rect = sphere.getBoundingClientRect();
    const targetWidth = Math.min(window.innerWidth * 0.70, 560);
    const targetHeight = targetWidth;
    globeFocusStyle.value = {
        '--globe-start-left': `${rect.left}px`,
        '--globe-start-top': `${rect.top}px`,
        '--globe-start-width': `${rect.width}px`,
        '--globe-focus-width': `${targetWidth}px`,
        '--globe-focus-x': `${window.innerWidth / 2 - rect.left - targetWidth / 2}px`,
        '--globe-focus-y': `${window.innerHeight / 2 - rect.top - targetHeight / 2}px`,
    };
    globeFocusReady.value = false;
    globeFocusActive.value = true;
    requestAnimationFrame(() => { globeFocused.value = true; });
}

function leaveGlobe() {
    globeFocusReady.value = false;
    globeFocused.value = false;
}

function trackGlobePointer(event: MouseEvent) {
    if (!globeFocusReady.value || !globeFocusActive.value) return;
    const sphere = document.querySelector<HTMLElement>('.globe-sphere');
    if (!sphere) return;
    const rect = sphere.getBoundingClientRect();
    const inside = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
    if (!inside) leaveGlobe();
}

function finishGlobeTransition(event: TransitionEvent) {
    if (event.propertyName !== 'transform') return;
    if (globeFocused.value) {
        globeFocusReady.value = true;
    } else {
        globeFocusActive.value = false;
        globeFocusStyle.value = {};
    }
}


</script>

<template>
    <Head title="NusaFire — Fire Early Warning & Environmental Intelligence" />

    <main class="landing-page" :class="[`theme-${theme}`, { 'globe-focused': globeFocusActive }]" @mousemove="trackGlobePointer">
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

            <!-- OPEN GLOBE VISUAL — intentionally no surrounding card -->
            <div class="preview-wrap globe-visual-wrap" :class="{ 'globe-focus-wrap': globeFocusActive }">
                <div class="globe-ambient-glow" aria-hidden="true"></div>
                <div class="globe-orbit-ring globe-orbit-ring-one" aria-hidden="true"></div>
                <div class="globe-orbit-ring globe-orbit-ring-two" aria-hidden="true"></div>
                <span class="globe-particle globe-particle-one" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-two" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-three" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-four" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-five" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-six" aria-hidden="true"></span>
                <span class="globe-particle globe-particle-seven" aria-hidden="true"></span>
                <div class="map-preview globe-preview">
                    <div class="globe-stage" role="img" aria-label="Animated globe centered on Indonesia with illustrative glowing hotspot indicators">
                        <div
                            class="globe-sphere"
                            :class="{ 'globe-focus-active': globeFocusActive, 'globe-focus-leaving': globeFocusActive && !globeFocused }"
                            :style="globeFocusStyle"
                            @mouseenter="focusGlobe"
                            @transitionend.self="finishGlobeTransition"
                        >
                            <div class="globe-atmosphere"></div>
                            <div class="globe-rotation-ring" aria-hidden="true"></div>
                            <div class="globe-latitude globe-latitude-one"></div>
                            <div class="globe-latitude globe-latitude-two"></div>
                            <div class="globe-longitude"></div>
                            <div class="globe-map-track">
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

                            <g class="hotspot hotspot-delay-one"><circle cx="208" cy="145" r="10"/><circle cx="208" cy="145" r="3.6"/></g>
                            <g class="hotspot hotspot-delay-two"><circle cx="367" cy="146" r="10"/><circle cx="367" cy="146" r="3.6"/></g>
                            <g class="hotspot hotspot-delay-three"><circle cx="411" cy="160" r="9"/><circle cx="411" cy="160" r="3.4"/></g>
                            <g class="hotspot hotspot-delay-four"><circle cx="493" cy="190" r="10"/><circle cx="493" cy="190" r="3.6"/></g>
                        </svg>
<svg
                            class="indonesia-map"
                            viewBox="0 0 620 270"
                            fill="none"
                            aria-hidden="true"
                            
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

                            <g class="hotspot hotspot-delay-one"><circle cx="208" cy="145" r="10"/><circle cx="208" cy="145" r="3.6"/></g>
                            <g class="hotspot hotspot-delay-two"><circle cx="367" cy="146" r="10"/><circle cx="367" cy="146" r="3.6"/></g>
                            <g class="hotspot hotspot-delay-three"><circle cx="411" cy="160" r="9"/><circle cx="411" cy="160" r="3.4"/></g>
                            <g class="hotspot hotspot-delay-four"><circle cx="493" cy="190" r="10"/><circle cx="493" cy="190" r="3.6"/></g>
                        </svg>
                            </div>
                            <div class="globe-label-track" aria-hidden="true">
                                <span class="globe-region-label globe-label-sumatra">SUMATRA</span>
                                <span class="globe-region-label globe-label-kalimantan">KALIMANTAN</span>
                                <span class="globe-region-label globe-label-papua">PAPUA</span>
                            </div>
                            <div class="globe-shine"></div>
                        </div>
                    </div>
                    <div class="map-legend"><span></span> ACTIVE HOTSPOTS</div>
                    <span class="map-disclaimer">INDONESIA · SATELLITE MONITORING</span>
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
                        Trained XGBoost machine learning model calculates daily wildfire probabilities across 38 provinces, 24 hours, 7 day and 14 day risk trend forecasts, and provincial mitigation priority rankings.
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


/* Open, atmospheric globe visual — no card or system-status badge */
.preview-wrap.globe-visual-wrap {
    position: relative;
    min-width: 0;
    min-height: 530px;
    display: grid;
    place-items: center;
    isolation: isolate;
    padding: 0;
}

.globe-preview {
    isolation: isolate;
    display: grid;
    place-items: center;
    width: 100%;
    height: 520px;
    overflow: visible;
    background: transparent;
}

.globe-ambient-glow {
    position: absolute;
    z-index: -2;
    width: 108%;
    aspect-ratio: 1.15;
    border-radius: 50%;
    background: radial-gradient(ellipse, rgba(255, 151, 35, .20) 0%, rgba(255, 151, 35, .09) 27%, rgba(39, 130, 79, .08) 48%, transparent 72%);
    filter: blur(27px);
    animation: nf-ambient-breathe 7s ease-in-out infinite;
    pointer-events: none;
}

.globe-orbit-ring {
    position: absolute;
    z-index: -1;
    width: 112%;
    height: 43%;
    border: 1px solid rgba(246, 166, 35, .25);
    border-radius: 50%;
    transform: rotate(-23deg);
    pointer-events: none;
    transform-origin: center;
}

.globe-orbit-ring-one { animation: nf-orbit-spin 22s linear infinite; }
.globe-orbit-ring-two {
    width: 120%;
    height: 55%;
    border-color: rgba(39, 130, 79, .2);
    transform: rotate(28deg);
    animation: nf-orbit-spin-reverse 30s linear infinite;
}

.globe-particle {
    position: absolute;
    z-index: 4;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #ff9f1c;
    box-shadow: 0 0 9px 3px rgba(255, 159, 28, .38), 0 0 25px 7px rgba(255, 133, 30, .16);
    pointer-events: none;
    animation: nf-particle-float 5.5s ease-in-out infinite;
}
.globe-particle-one { top: 19%; left: 16%; }
.globe-particle-two { top: 70%; right: 12%; width: 4px; height: 4px; animation-delay: -1.8s; }
.globe-particle-three { top: 14%; right: 24%; width: 5px; height: 5px; animation-delay: -3.2s; }
.globe-particle-four { top: 31%; right: 7%; width: 3px; height: 3px; background: #9edfc1; box-shadow: 0 0 10px 3px rgba(116, 222, 174, .35); animation-delay: -2.4s; }
.globe-particle-five { bottom: 17%; left: 19%; width: 4px; height: 4px; background: #b5ddff; box-shadow: 0 0 12px 4px rgba(143, 199, 255, .28); animation-delay: -4.1s; }
.globe-particle-six { top: 52%; left: 5%; width: 3px; height: 3px; animation-delay: -1.1s; }
.globe-particle-seven { bottom: 12%; right: 31%; width: 5px; height: 5px; background: #ffd28b; animation-delay: -3.7s; }

.globe-stage {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    perspective: 1000px;
}

.globe-sphere {
    position: relative;
    width: min(84%, 410px);
    aspect-ratio: 1;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, var(--nf-map-stroke) 65%, transparent);
    border-radius: 50%;
    background:
        radial-gradient(ellipse at 32% 27%, rgba(255,255,255,.84) 0%, rgba(255,255,255,.15) 17%, transparent 38%),
        radial-gradient(ellipse at 35% 35%, color-mix(in srgb, var(--nf-map) 76%, #e7f3e7) 0%, var(--nf-map) 48%, color-mix(in srgb, var(--nf-map-stroke) 50%, #143c2a) 100%);
    box-shadow:
        inset -32px -12px 48px rgba(13, 46, 31, .25),
        inset 12px 7px 28px rgba(255,255,255,.3),
        0 0 0 10px color-mix(in srgb, var(--nf-accent) 4%, transparent),
        0 0 42px rgba(255, 150, 35, .15),
        0 0 95px rgba(255, 150, 35, .10),
        0 28px 65px var(--nf-shadow);
    transform-style: preserve-3d;
}

.globe-atmosphere {
    position: absolute;
    z-index: 5;
    inset: -2px;
    border: 1px solid color-mix(in srgb, #ff9f1c 34%, transparent);
    border-radius: inherit;
    box-shadow: inset 0 0 22px rgba(255, 159, 28, .13), 0 0 22px rgba(255, 159, 28, .14);
    pointer-events: none;
}

/* Rotating meridian band gives the sphere itself a clear, continuous spin cue. */
.globe-rotation-ring {
    position: absolute;
    z-index: 3;
    inset: 1% 17%;
    border: 1px solid rgba(255, 159, 28, .32);
    border-radius: 50%;
    transform: rotate(-22deg) scaleX(.32);
    box-shadow: 0 0 12px rgba(255, 159, 28, .10);
    pointer-events: none;
    animation: nf-meridian-spin 8s ease-in-out infinite;
}

.globe-map-track {
    position: absolute;
    z-index: 2;
    top: 16%;
    left: 0;
    width: 200%;
    height: 68%;
    display: flex;
    align-items: center;
    animation: nf-globe-orbit 34s linear infinite;
    will-change: transform;
}
.globe-map-track .indonesia-map {
    position: relative;
    inset: auto;
    display: block;
    flex: 0 0 50%;
    width: 50%;
    height: 100%;
    overflow: visible;
    padding: 0;
    opacity: .98;
}
.globe-map-track .island {
    fill: color-mix(in srgb, var(--nf-map) 78%, #e4f0df);
    stroke: var(--nf-map-stroke);
    stroke-width: 1.7;
    vector-effect: non-scaling-stroke;
}
.globe-map-track .hotspot circle:first-child {
    fill: rgba(255, 151, 35, .25);
    stroke: rgba(255, 151, 35, .72);
    stroke-width: 1;
    animation: nf-hotspot-pulse 2.8s ease-out infinite;
    transform-box: fill-box;
    transform-origin: center;
}
.globe-map-track .hotspot circle:last-child {
    fill: #ff9f1c;
    stroke: #fff0cf;
    stroke-width: 2;
    filter: drop-shadow(0 0 5px rgba(255, 159, 28, .95)) drop-shadow(0 0 14px rgba(255, 124, 26, .68));
    animation: nf-hotspot-core 2.8s ease-in-out infinite;
}
.globe-map-track .hotspot-delay-one circle { animation-delay: -.7s !important; }
.globe-map-track .hotspot-delay-two circle { animation-delay: -1.4s !important; }
.globe-map-track .hotspot-delay-three circle { animation-delay: -2s !important; }
.globe-map-track .hotspot-delay-four circle { animation-delay: -1.1s !important; }

.globe-latitude, .globe-longitude {
    position: absolute;
    z-index: 3;
    border: 1px solid rgba(55, 126, 83, .22);
    border-radius: 50%;
    pointer-events: none;
}
.globe-latitude-one { inset: 25% -2%; }
.globe-latitude-two { inset: 39% -2%; }
.globe-longitude { inset: -2% 27%; border-width: 1px; transform: rotate(13deg); animation: nf-longitude-turn 10s ease-in-out infinite; }
.globe-shine {
    position: absolute;
    z-index: 4;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(112deg, rgba(255,255,255,.25), transparent 33%, transparent 68%, rgba(9,42,27,.13));
    pointer-events: none;
}
.globe-label-track {
    position: absolute;
    z-index: 6;
    top: 16%;
    left: 0;
    width: 200%;
    height: 68%;
    pointer-events: none;
    animation: nf-globe-orbit 34s linear infinite;
    will-change: transform;
}
.globe-region-label {
    position: absolute;
    color: var(--nf-muted);
    font-size: 7px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-shadow: 0 1px 3px var(--nf-surface), 0 0 8px rgba(255,255,255,.22);
    white-space: nowrap;
    pointer-events: none;
    animation: nf-region-label-fade 34s ease-in-out infinite;
}
/* Label coordinates share the moving map's coordinate system, so they travel with each island. */
.globe-label-sumatra { left: 12.5%; top: 39.7%; animation-delay: -2s; }
.globe-label-kalimantan { left: 21.5%; top: 57.4%; animation-delay: -12s; }
.globe-label-papua { left: 38%; top: 45.6%; animation-delay: -22s; }
@keyframes nf-region-label-fade {
    0%, 7% { opacity: 0; }
    16%, 63% { opacity: .9; }
    76%, 100% { opacity: 0; }
}

.map-legend {
    position: absolute;
    right: 3%;
    bottom: 23px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 0;
    color: var(--nf-muted);
    font-size: 9px;
    font-weight: 750;
    letter-spacing: 1px;
    background: transparent;
    border: 0;
}
.map-legend span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #ff9f1c;
    box-shadow: 0 0 10px rgba(255, 159, 28, .8);
}
.map-disclaimer {
    position: absolute;
    left: 3%;
    bottom: 23px;
    color: var(--nf-subtle);
    font-size: 8px;
    font-weight: 750;
    letter-spacing: 1.3px;
}

@keyframes nf-globe-orbit { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes nf-meridian-spin {
    0%, 100% { transform: rotate(-22deg) scaleX(.28); opacity: .48; }
    25% { transform: rotate(-8deg) scaleX(.82); opacity: .9; }
    50% { transform: rotate(8deg) scaleX(.34); opacity: .65; }
    75% { transform: rotate(22deg) scaleX(.88); opacity: .95; }
}
@keyframes nf-longitude-turn {
    0%, 100% { transform: rotate(13deg) scaleX(1); opacity: .65; }
    50% { transform: rotate(13deg) scaleX(.18); opacity: .95; }
}
@keyframes nf-orbit-spin { from { transform: rotate(-23deg); } to { transform: rotate(337deg); } }
@keyframes nf-orbit-spin-reverse { from { transform: rotate(28deg); } to { transform: rotate(-332deg); } }
@keyframes nf-hotspot-pulse { 0% { opacity: .95; transform: scale(.72); } 72%, 100% { opacity: .06; transform: scale(2.1); } }
@keyframes nf-hotspot-core {
    0%, 100% { opacity: .86; filter: drop-shadow(0 0 4px rgba(255, 159, 28, .8)) drop-shadow(0 0 10px rgba(255, 124, 26, .42)); }
    50% { opacity: 1; filter: drop-shadow(0 0 8px rgba(255, 178, 55, 1)) drop-shadow(0 0 21px rgba(255, 124, 26, .82)); }
}
@keyframes nf-ambient-breathe { 0%, 100% { opacity: .65; transform: scale(.96); } 50% { opacity: 1; transform: scale(1.06); } }
@keyframes nf-orbit-glow { 0%, 100% { opacity: .4; } 50% { opacity: .9; } }
@keyframes nf-orbit-glow-two { 0%, 100% { opacity: .35; transform: rotate(28deg) scale(.98); } 50% { opacity: .78; transform: rotate(34deg) scale(1.03); } }
@keyframes nf-particle-float { 0%, 100% { opacity: .45; transform: translate3d(0, 4px, 0) scale(.8); } 50% { opacity: 1; transform: translate3d(8px, -9px, 0) scale(1.25); } }

@media (max-width: 800px) {
    .preview-wrap.globe-visual-wrap { min-height: 450px; }
    .globe-preview { height: 440px; }
    .globe-sphere { width: min(82%, 360px); }
}
@media (max-width: 480px) {
    .preview-wrap.globe-visual-wrap { min-height: 355px; }
    .globe-preview { height: 350px; }
    .globe-sphere { width: min(86%, 285px); }
    .globe-region-label { font-size: 6px; letter-spacing: .7px; }
    .globe-orbit-ring { width: 120%; }
    .map-legend { right: 2%; bottom: 8px; }
    .map-disclaimer { left: 2%; bottom: 8px; }
}
@media (prefers-reduced-motion: reduce) {
    .globe-map-track, .globe-label-track, .globe-region-label, .globe-map-track .hotspot circle, .globe-ambient-glow, .globe-orbit-ring, .globe-rotation-ring, .globe-longitude, .globe-particle { animation: none !important; }
}

/* Hover-to-focus: the globe smoothly lifts above the page, which becomes a soft cosmic backdrop. */
.landing-page::before,
.landing-page::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0;
    visibility: hidden;
    transition: opacity .58s cubic-bezier(.22, 1, .36, 1), visibility 0s linear .58s;
}
.landing-page::before {
    z-index: 1000;
    background: rgba(4, 12, 16, .32);
    -webkit-backdrop-filter: blur(0px);
    backdrop-filter: blur(0px);
    transition: opacity .58s cubic-bezier(.22, 1, .36, 1), backdrop-filter .62s cubic-bezier(.22, 1, .36, 1), -webkit-backdrop-filter .62s cubic-bezier(.22, 1, .36, 1), visibility 0s linear .62s;
}
.landing-page::after {
    z-index: 1001;
    opacity: 0;
    background-image:
        radial-gradient(ellipse at 18% 28%, rgba(255, 177, 72, .20) 0 1px, transparent 2px),
        radial-gradient(ellipse at 73% 22%, rgba(142, 210, 255, .26) 0 1.2px, transparent 2.5px),
        radial-gradient(ellipse at 82% 72%, rgba(255, 177, 72, .22) 0 1.5px, transparent 3px),
        radial-gradient(ellipse at 28% 78%, rgba(128, 216, 178, .22) 0 1px, transparent 2.5px),
        radial-gradient(ellipse at 60% 62%, rgba(255, 255, 255, .22) 0 1px, transparent 2px),
        radial-gradient(ellipse at 50% 50%, transparent 35%, rgba(6, 17, 24, .22) 100%);
    background-size: 170px 160px, 230px 210px, 190px 230px, 240px 180px, 130px 170px, 100% 100%;
}
.landing-page.globe-focused::before,
.landing-page.globe-focused::after {
    opacity: 1;
    visibility: visible;
    transition-delay: 0s;
}
.landing-page.globe-focused::before {
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
    transition-delay: 0s;
}
.landing-page.globe-focused::after {
    animation: nf-cosmic-drift 24s linear infinite;
}
.globe-visual-wrap.globe-focus-wrap {
    position: fixed;
    inset: 0;
    z-index: 1002;
    display: grid;
    place-items: center;
    min-height: 0;
    width: 100vw;
    height: 100dvh;
    padding: 0;
    pointer-events: none;
}
/* Keep the cosmic orbit lines and particles visible; remove only the old oversized ambient glow. */
.globe-visual-wrap.globe-focus-wrap > .globe-ambient-glow {
    display: none;
}
.globe-visual-wrap.globe-focus-wrap > .globe-orbit-ring {
    z-index: 1;
    left: 50%;
    top: 50%;
    width: min(88vw, 900px);
    height: min(48vh, 430px);
    translate: -50% -50%;
    opacity: .95;
}
.globe-visual-wrap.globe-focus-wrap > .globe-orbit-ring-two {
    width: min(96vw, 1020px);
    height: min(58vh, 510px);
}
.globe-visual-wrap.globe-focus-wrap > .globe-particle {
    z-index: 2;
}
/* The globe is the only foreground content while focused: fade all landing-page copy away. */
.landing-page.globe-focused .navbar,
.landing-page.globe-focused .hero-copy,
.landing-page.globe-focused > section:not(#home),
.landing-page.globe-focused .map-legend,
.landing-page.globe-focused .map-disclaimer {
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    transition: opacity .42s cubic-bezier(.22, 1, .36, 1), visibility 0s linear .42s !important;
}
.landing-page .navbar,
.landing-page .hero-copy,
.landing-page > section:not(#home),
.landing-page .map-legend,
.landing-page .map-disclaimer {
    transition: opacity .48s cubic-bezier(.22, 1, .36, 1), visibility 0s linear 0s;
}
.globe-visual-wrap.globe-focus-wrap .globe-preview,
.globe-visual-wrap.globe-focus-wrap .globe-stage {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere {
    position: fixed;
    z-index: 1003;
    top: var(--globe-start-top);
    left: var(--globe-start-left);
    width: var(--globe-start-width);
    max-width: none;
    margin: 0;
    pointer-events: auto;
    transform: translate3d(0, 0, 0) scale(1);
    transition: transform 1.05s cubic-bezier(.22, 1, .36, 1), width 1.05s cubic-bezier(.22, 1, .36, 1), box-shadow .82s cubic-bezier(.22, 1, .36, 1), filter .78s cubic-bezier(.22, 1, .36, 1);
    will-change: transform, width;
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere.globe-focus-active {
    width: var(--globe-focus-width);
    transform: translate3d(var(--globe-focus-x), var(--globe-focus-y), 0) scale(1);
    box-shadow:
        inset -32px -12px 48px rgba(13, 46, 31, .25),
        inset 12px 7px 28px rgba(255,255,255,.3),
        0 0 0 16px rgba(255, 159, 28, .09),
        0 0 0 34px rgba(122, 211, 166, .035),
        0 0 62px rgba(255, 150, 35, .32),
        0 0 145px rgba(255, 150, 35, .22),
        0 0 205px rgba(82, 196, 148, .13),
        0 36px 100px rgba(0, 0, 0, .38);
    filter: saturate(1.08) brightness(1.035);
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere.globe-focus-leaving {
    width: var(--globe-start-width);
    transform: translate3d(0, 0, 0) scale(1);
    /* Return faster than the entrance so leaving focus never feels stuck. */
    transition: transform .62s cubic-bezier(.4, 0, .2, 1), width .62s cubic-bezier(.4, 0, .2, 1), box-shadow .48s ease-out, filter .48s ease-out;
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere > * {
    pointer-events: none;
}
@media (prefers-reduced-motion: reduce) {
    .landing-page::before, .landing-page::after { transition: none !important; }
    .landing-page.globe-focused::before { -webkit-backdrop-filter: none; backdrop-filter: none; }
    .globe-visual-wrap.globe-focus-wrap .globe-sphere { transition: none !important; }
    .landing-page.globe-focused .navbar,
    .landing-page.globe-focused .hero-copy,
    .landing-page.globe-focused > section:not(#home),
    .landing-page.globe-focused .map-legend,
    .landing-page.globe-focused .map-disclaimer { transition: none !important; }
}
@keyframes nf-cosmic-backdrop-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes nf-cosmic-drift {
    from { background-position: 0 0, 0 0, 0 0, 0 0, 0 0, center; }
    to { background-position: 170px 120px, -230px 210px, 190px -230px, -240px -180px, 130px 170px, center; }
}




/* =========================================
   LIVING LANDING PAGE — warm satellite aura
   Visual-only enhancements; no API or logic changes.
   ========================================= */
.landing-page {
    position: relative;
    isolation: isolate;
    background:
        radial-gradient(ellipse at 78% 7%, rgba(255, 190, 72, .16), transparent 27%),
        radial-gradient(ellipse at 12% 23%, rgba(255, 172, 48, .075), transparent 29%),
        radial-gradient(ellipse at 52% 68%, color-mix(in srgb, var(--nf-accent) 5%, transparent), transparent 43%),
        var(--nf-bg);
}

.landing-page::before,
.landing-page::after {
    content: "";
    position: absolute;
    z-index: -1;
    pointer-events: none;
    border-radius: 50%;
    filter: blur(42px);
}
.landing-page::before {
    width: 390px;
    height: 390px;
    top: 60px;
    right: -180px;
    background: rgba(255, 186, 55, .10);
    animation: nf-page-aura 13s ease-in-out infinite alternate;
}
.landing-page::after {
    width: 300px;
    height: 300px;
    top: 680px;
    left: -180px;
    background: rgba(255, 144, 35, .07);
    animation: nf-page-aura 16s ease-in-out infinite alternate-reverse;
}

/* Warm golden aura above the navigation, like soft sunlight. */
.navbar {
    position: relative;
    z-index: 10;
    isolation: isolate;
    background: color-mix(in srgb, var(--nf-bg) 90%, transparent);
    border-bottom-color: color-mix(in srgb, #f5b83d 28%, var(--nf-border));
    box-shadow: 0 10px 38px rgba(244, 177, 54, .045);
    backdrop-filter: blur(16px);
}
.navbar::before {
    content: "";
    position: absolute;
    z-index: -1;
    pointer-events: none;
    width: min(780px, 78vw);
    height: 125px;
    top: -82px;
    left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(ellipse, rgba(255, 194, 73, .25) 0%, rgba(255, 177, 46, .11) 34%, transparent 72%);
    filter: blur(22px);
    animation: nf-header-glow 8s ease-in-out infinite;
}
.navbar::after {
    content: "";
    position: absolute;
    left: 7%;
    right: 7%;
    bottom: -1px;
    height: 1px;
    pointer-events: none;
    background: linear-gradient(90deg, transparent, rgba(255, 191, 66, .45), color-mix(in srgb, var(--nf-accent) 35%, transparent), transparent);
    opacity: .75;
}
.brand-icon {
    position: relative;
}
.brand-icon::after {
    content: "";
    position: absolute;
    inset: 3px;
    z-index: -1;
    border-radius: 50%;
    background: rgba(255, 186, 49, .25);
    filter: blur(13px);
    opacity: .8;
    animation: nf-logo-glow 4s ease-in-out infinite;
}
.nav-links a {
    position: relative;
    transition: color .25s ease, transform .25s ease;
}
.nav-links a::after {
    content: "";
    position: absolute;
    left: 0;
    right: 100%;
    bottom: -8px;
    height: 2px;
    border-radius: 99px;
    background: linear-gradient(90deg, #f5b83d, var(--nf-accent));
    transition: right .28s ease;
}
.nav-links a:hover {
    color: var(--nf-text);
    transform: translateY(-1px);
}
.nav-links a:hover::after { right: 0; }
.theme-toggle,
.nav-cta,
.button-primary,
.button-secondary {
    position: relative;
    overflow: hidden;
}
.theme-toggle:hover {
    box-shadow: 0 0 0 4px rgba(255, 188, 55, .09), 0 0 24px rgba(255, 180, 40, .12);
}
.nav-cta:hover {
    box-shadow: 0 8px 28px rgba(255, 177, 43, .11);
    transform: translateY(-2px);
}

/* Hero content enters gently; the globe remains the visual centerpiece. */
.hero-copy > * {
    animation: nf-rise-in .85s cubic-bezier(.2,.75,.25,1) both;
}
.hero-copy > :nth-child(1) { animation-delay: .08s; }
.hero-copy > :nth-child(2) { animation-delay: .16s; }
.hero-copy > :nth-child(3) { animation-delay: .24s; }
.hero-copy > :nth-child(4) { animation-delay: .32s; }
.hero-copy > :nth-child(5) { animation-delay: .4s; }
.globe-visual-wrap {
    filter: saturate(1.05);
    animation: nf-globe-arrive 1.15s cubic-bezier(.18,.72,.2,1) both;
}
.hero h1 span {
    color: var(--nf-accent);
    text-shadow: 0 0 34px rgba(255, 190, 61, .13);
}
.eyebrow .status-dot {
    background: #f4b83f;
    box-shadow: 0 0 0 4px rgba(244, 184, 63, .12), 0 0 18px rgba(244, 184, 63, .65);
    animation: nf-status-pulse 3s ease-in-out infinite;
}
.footnote-line {
    background: linear-gradient(90deg, #f2b83d, var(--nf-accent));
    box-shadow: 0 0 12px rgba(255, 184, 52, .32);
}
.button-primary {
    box-shadow: 0 9px 25px color-mix(in srgb, var(--nf-accent) 15%, transparent);
}
.button-primary::after,
.button-secondary::after,
.nav-cta::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(110deg, transparent 20%, rgba(255,255,255,.22) 48%, transparent 72%);
    transform: translateX(-140%);
    transition: transform .65s ease;
}
.button-primary:hover::after,
.button-secondary:hover::after,
.nav-cta:hover::after { transform: translateX(140%); }

/* Section backgrounds have a soft glow instead of a flat, static canvas. */
.section-marker {
    position: relative;
    border-top-color: color-mix(in srgb, #eab54a 22%, var(--nf-border));
}
.section-marker a {
    transition: color .25s ease, gap .25s ease;
}
.section-marker a:hover { color: var(--nf-accent); gap: 19px; }
.content-section {
    position: relative;
    border-bottom-color: color-mix(in srgb, var(--nf-accent) 12%, var(--nf-border));
}
.content-section::before {
    content: "";
    position: absolute;
    z-index: -1;
    width: 340px;
    height: 260px;
    top: 18%;
    right: -180px;
    border-radius: 50%;
    pointer-events: none;
    background: radial-gradient(ellipse, rgba(255, 184, 58, .07), transparent 70%);
    filter: blur(24px);
    opacity: .8;
}
.section-heading h2 span {
    text-shadow: 0 0 28px rgba(255, 190, 61, .10);
}
.capability-card {
    position: relative;
    overflow: hidden;
    border-radius: 9px;
    background: color-mix(in srgb, var(--nf-surface) 90%, transparent);
    box-shadow: 0 10px 34px rgba(20, 58, 35, .025);
    transition: transform .35s cubic-bezier(.2,.75,.25,1), border-color .35s ease, box-shadow .35s ease, background-color .35s ease;
}
.capability-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 12%;
    right: 12%;
    height: 2px;
    opacity: .35;
    background: linear-gradient(90deg, transparent, #f5b83d, var(--nf-accent), transparent);
    transition: opacity .35s ease, left .35s ease, right .35s ease;
}
.capability-card::after {
    content: "";
    position: absolute;
    width: 150px;
    height: 150px;
    right: -90px;
    bottom: -100px;
    border-radius: 50%;
    background: rgba(255, 185, 54, .12);
    filter: blur(26px);
    opacity: 0;
    transition: opacity .35s ease;
    pointer-events: none;
}
.capability-card:hover {
    transform: translateY(-7px);
    border-color: color-mix(in srgb, #efb744 55%, var(--nf-map-stroke));
    box-shadow: 0 20px 48px rgba(24, 65, 39, .08), 0 0 28px rgba(255, 181, 48, .075);
    background: color-mix(in srgb, var(--nf-surface) 95%, #fff1cc);
}
.capability-card:hover::before { opacity: .95; left: 0; right: 0; }
.capability-card:hover::after { opacity: 1; }
.capability-icon {
    transition: transform .35s ease, box-shadow .35s ease, background-color .35s ease;
}
.capability-card:hover .capability-icon {
    transform: translateY(-2px) rotate(-3deg);
    box-shadow: 0 0 25px rgba(255, 184, 52, .13);
}
.process-item {
    transition: padding-left .3s ease, border-color .3s ease;
}
.process-item:hover { padding-left: 10px; }
.process-number {
    transition: color .25s ease, text-shadow .25s ease;
}
.process-item:hover .process-number {
    color: #e5a72e;
    text-shadow: 0 0 20px rgba(255, 184, 52, .28);
}
.final-cta {
    position: relative;
    overflow: hidden;
    border-radius: 9px;
    background:
        radial-gradient(ellipse at 100% 0%, rgba(255, 188, 55, .11), transparent 45%),
        var(--nf-surface);
    box-shadow: 0 18px 50px rgba(24, 65, 39, .035);
}
.final-cta::after {
    content: "";
    position: absolute;
    top: -90px;
    right: -50px;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    border: 1px solid rgba(255, 185, 54, .14);
    box-shadow: 0 0 0 18px rgba(255, 185, 54, .025), 0 0 0 38px rgba(255, 185, 54, .018);
    pointer-events: none;
}
.footer {
    position: relative;
}
.footer::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 184, 52, .25), transparent);
}

@keyframes nf-header-glow {
    0%, 100% { opacity: .55; transform: translateX(-50%) scaleX(.88); }
    50% { opacity: 1; transform: translateX(-50%) scaleX(1.08); }
}
@keyframes nf-logo-glow {
    0%, 100% { opacity: .4; transform: scale(.85); }
    50% { opacity: .95; transform: scale(1.13); }
}
@keyframes nf-page-aura {
    from { transform: translate3d(-8px, -5px, 0) scale(.92); opacity: .55; }
    to { transform: translate3d(18px, 16px, 0) scale(1.1); opacity: 1; }
}
@keyframes nf-rise-in {
    from { opacity: 0; transform: translateY(17px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes nf-globe-arrive {
    from { opacity: 0; transform: translateY(18px) scale(.97); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes nf-status-pulse {
    0%, 100% { box-shadow: 0 0 0 4px rgba(244, 184, 63, .10), 0 0 12px rgba(244, 184, 63, .42); }
    50% { box-shadow: 0 0 0 7px rgba(244, 184, 63, .035), 0 0 21px rgba(244, 184, 63, .78); }
}

@media (max-width: 800px) {
    .navbar { box-shadow: 0 7px 28px rgba(244, 177, 54, .035); }
    .content-section { padding-block: 76px; }
    .capability-card:hover { transform: translateY(-3px); }
    .process-item:hover { padding-left: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .landing-page::before, .landing-page::after, .navbar::before, .brand-icon::after,
    .hero-copy > *, .globe-visual-wrap, .eyebrow .status-dot,
    .capability-card, .capability-icon, .process-item, .process-number {
        animation: none !important;
        transition: none !important;
    }
}

</style>

/* Smooth, responsive focus polish + richer cosmic atmosphere */
.landing-page::before,
.landing-page::after {
    position: fixed !important;
    inset: 0 !important;
    border-radius: 0 !important;
    filter: none !important;
    pointer-events: none !important;
}
.landing-page::before {
    z-index: 1000 !important;
    opacity: 0;
    visibility: hidden;
    background: rgba(5, 15, 18, .24) !important;
    -webkit-backdrop-filter: blur(0px);
    backdrop-filter: blur(0px);
    transition: opacity .58s cubic-bezier(.2,.8,.2,1),
        backdrop-filter .72s cubic-bezier(.2,.8,.2,1),
        -webkit-backdrop-filter .72s cubic-bezier(.2,.8,.2,1),
        visibility 0s linear .72s !important;
}
.landing-page::after {
    z-index: 1001 !important;
    opacity: 0;
    visibility: hidden;
    background-image:
        radial-gradient(circle at 13% 24%, rgba(255,181,75,.95) 0 1px, transparent 2.8px),
        radial-gradient(circle at 23% 72%, rgba(150,235,205,.9) 0 1px, transparent 3px),
        radial-gradient(circle at 36% 18%, rgba(255,220,157,.9) 0 1.3px, transparent 3px),
        radial-gradient(circle at 49% 83%, rgba(133,211,255,.9) 0 1px, transparent 3px),
        radial-gradient(circle at 63% 27%, rgba(255,185,83,.95) 0 1.4px, transparent 3.4px),
        radial-gradient(circle at 77% 66%, rgba(155,237,201,.9) 0 1.1px, transparent 3px),
        radial-gradient(circle at 88% 35%, rgba(255,222,160,.95) 0 1.2px, transparent 3px),
        radial-gradient(circle at 92% 82%, rgba(127,196,255,.85) 0 1px, transparent 3px),
        radial-gradient(ellipse at 50% 50%, rgba(255,190,92,.10), transparent 48%),
        radial-gradient(ellipse at 50% 50%, transparent 35%, rgba(4,15,20,.18) 100%) !important;
    background-size: 100% 100% !important;
    transition: opacity .5s ease, visibility 0s linear .5s !important;
}
.landing-page.globe-focused::before {
    opacity: 1 !important;
    visibility: visible !important;
    -webkit-backdrop-filter: blur(10px) saturate(1.12) !important;
    backdrop-filter: blur(10px) saturate(1.12) !important;
    transition-delay: 0s !important;
}
.landing-page.globe-focused::after {
    opacity: 1 !important;
    visibility: visible !important;
    animation: nf-cosmic-drift 16s linear infinite, nf-cosmic-twinkle 3.8s ease-in-out infinite alternate !important;
    transition-delay: 0s !important;
}
.landing-page.globe-focused .navbar,
.landing-page.globe-focused .hero-copy,
.landing-page.globe-focused > section:not(#home),
.landing-page.globe-focused .map-legend,
.landing-page.globe-focused .map-disclaimer {
    transition: opacity .48s cubic-bezier(.2,.8,.2,1), visibility 0s linear .48s !important;
}
.landing-page.globe-focused .navbar,
.landing-page.globe-focused .hero-copy,
.landing-page.globe-focused > section:not(#home),
.landing-page.globe-focused .map-legend,
.landing-page.globe-focused .map-disclaimer {
    opacity: 0 !important;
    visibility: hidden !important;
}
.globe-visual-wrap.globe-focus-wrap > .globe-orbit-ring {
    filter: drop-shadow(0 0 9px rgba(255,184,79,.42));
    animation-duration: 13s !important;
}
.globe-visual-wrap.globe-focus-wrap > .globe-orbit-ring-two {
    animation-duration: 19s !important;
}
.globe-visual-wrap.globe-focus-wrap > .globe-particle {
    box-shadow: 0 0 9px 3px rgba(255,174,66,.26), 0 0 25px 8px rgba(117,221,175,.12);
    animation-duration: 3.2s !important;
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere {
    transition: transform 1.12s cubic-bezier(.2,.9,.22,1),
        width 1.12s cubic-bezier(.2,.9,.22,1),
        box-shadow .9s cubic-bezier(.2,.9,.22,1),
        filter .85s cubic-bezier(.2,.9,.22,1) !important;
    will-change: transform, width, filter, box-shadow;
}
.globe-visual-wrap.globe-focus-wrap .globe-sphere.globe-focus-active {
    box-shadow:
        inset -34px -15px 52px rgba(13,46,31,.25),
        inset 13px 8px 30px rgba(255,255,255,.34),
        0 0 0 12px rgba(255,159,28,.11),
        0 0 0 30px rgba(122,211,166,.055),
        0 0 0 58px rgba(117,196,255,.025),
        0 0 72px rgba(255,150,35,.4),
        0 0 150px rgba(255,150,35,.26),
        0 0 225px rgba(82,196,148,.2),
        0 0 285px rgba(107,187,255,.10),
        0 36px 100px rgba(0,0,0,.34) !important;
    filter: saturate(1.16) brightness(1.055) contrast(1.02) !important;
}
@keyframes nf-cosmic-twinkle {
    from { filter: brightness(.88); }
    to { filter: brightness(1.22); }
}
@media (prefers-reduced-motion: reduce) {
    .landing-page::before, .landing-page::after { transition: none !important; }
    .globe-visual-wrap.globe-focus-wrap .globe-sphere { transition: none !important; }
}

