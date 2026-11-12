
<script setup lang="ts">
import { computed, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const period = ref('7 Days');

const periods = ['7 Days', '30 Days', '90 Days'];

const demoTrend = computed(() => {
    const points: Record<string, number[]> = {
        '7 Days': [22, 35, 28, 48, 39, 62, 54],
        '30 Days': [20, 28, 24, 40, 35, 50, 46, 64, 48, 58],
        '90 Days': [15, 25, 20, 35, 28, 42, 38, 55, 45, 62],
    };

    return points[period.value] ?? points['7 Days'];
});

const chartPoints = computed(() => {
    const values = demoTrend.value;
    const width = 580;
    const height = 155;
    const max = Math.max(...values) + 10;

    return values.map((value, index) => ({
        x: 10 + (index * (width - 20)) / Math.max(values.length - 1, 1),
        y: height - (value / max) * (height - 20),
    }));
});

const chartLine = computed(() =>
    chartPoints.value
        .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
        .join(' '),
);

const chartArea = computed(() => {
    const lastX = chartPoints.value.at(-1)?.x ?? 590;
    const firstX = chartPoints.value[0]?.x ?? 10;

    return `${chartLine.value} L ${lastX} 155 L ${firstX} 155 Z`;
});

const regions = [
    { name: 'Sumatra', width: 78 },
    { name: 'Kalimantan', width: 62 },
    { name: 'Sulawesi', width: 38 },
    { name: 'Papua', width: 24 },
];

const weatherItems = [
    { label: 'Temperature', value: '—', unit: '°C', icon: '☀' },
    { label: 'Humidity', value: '—', unit: '%', icon: '◌' },
    { label: 'Precipitation', value: '—', unit: 'mm', icon: '☂' },
];


</script>

<template>
    <Head title="NusaFire Dashboard" />

    <div class="nf-app" :class="`theme-${theme}`">
        <!-- Shared sidebar: used by other pages too -->
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main class="nf-main" :class="{ 'nf-sidebar-collapsed': sidebarCollapsed }">
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        type="button"
                        class="nf-icon-button nf-mobile-menu"
                        :class="{ 'nf-menu-visible': sidebarCollapsed }"
                        aria-label="Open navigation menu"
                        @click="sidebarCollapsed = false; mobileMenuOpen = true"
                    >
                        ☰
                    </button>

                    <div class="nf-breadcrumb">
                        <span>Workspace</span>
                        <span class="nf-breadcrumb-separator">/</span>
                        <strong>Overview</strong>
                    </div>
                </div>

                <div class="nf-topbar-right">
                    <span class="nf-live-indicator">
                        <span class="nf-status-dot" />
                        Monitoring workspace
                    </span>

                    <button
                        type="button"
                        class="nf-theme-toggle"
                        :aria-label="
                            theme === 'dark'
                                ? 'Switch to light mode'
                                : 'Switch to dark mode'
                        "
                        :title="
                            theme === 'dark'
                                ? 'Switch to light mode'
                                : 'Switch to dark mode'
                        "
                        @click="toggleTheme"
                    >
                        <span v-if="theme === 'dark'">☀</span>
                        <span v-else>☾</span>
                    </button>
                </div>
            </header>

            <div class="nf-content">
                <section class="nf-page-heading">
                    <div>
                        <div class="nf-eyebrow">
                            <span class="nf-eyebrow-line" />
                            ENVIRONMENTAL INTELLIGENCE
                        </div>

                        <h1>Forest Intelligence</h1>

                        <p>
                            A unified overview of forest fire activity across Indonesia.
                        </p>
                    </div>

                    <div class="nf-heading-date">
                        <span class="nf-date-icon">◷</span>
                        <div>
                            <strong>Data overview</strong>
                            <span>Live data integration pending</span>
                        </div>
                    </div>
                </section>

                <!-- Summary statistics -->
                <section class="nf-stats-grid">
                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">Detected Hotspots</span>
                            <span class="nf-stat-icon nf-icon-green">◎</span>
                        </div>

                        <div class="nf-stat-value">—</div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">NASA FIRMS</span>
                            <span class="nf-stat-tag">Awaiting data</span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">Burned Area</span>
                            <span class="nf-stat-icon nf-icon-orange">▧</span>
                        </div>

                        <div class="nf-stat-value">— <small>ha</small></div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">Burned-area data</span>
                            <span class="nf-stat-tag">Awaiting data</span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">Average Temperature</span>
                            <span class="nf-stat-icon nf-icon-yellow">☀</span>
                        </div>

                        <div class="nf-stat-value">— <small>°C</small></div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">NASA POWER</span>
                            <span class="nf-stat-tag">Awaiting data</span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">Relative Humidity</span>
                            <span class="nf-stat-icon nf-icon-blue">◌</span>
                        </div>

                        <div class="nf-stat-value">— <small>%</small></div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">Weather indicators</span>
                            <span class="nf-stat-tag">Awaiting data</span>
                        </div>
                    </article>
                </section>

                <!-- Trend chart and regional overview -->
                <section class="nf-primary-grid">
                    <article class="nf-panel nf-trend-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">FIRE ACTIVITY</div>
                                <h2>Hotspot activity</h2>
                                <p>Illustrative historical trend preview</p>
                            </div>

                            <select
                                v-model="period"
                                class="nf-select"
                                aria-label="Chart period"
                            >
                                <option
                                    v-for="item in periods"
                                    :key="item"
                                    :value="item"
                                >
                                    {{ item }}
                                </option>
                            </select>
                        </div>

                        <div class="nf-chart-legend">
                            <span class="nf-legend-dot" />
                            Hotspot detections
                            <span class="nf-demo-label">Demo visualization</span>
                        </div>

                        <div class="nf-chart-wrap">
                            <div class="nf-chart-y-labels">
                                <span>High</span>
                                <span>Medium</span>
                                <span>Low</span>
                                <span>0</span>
                            </div>

                            <svg
                                class="nf-line-chart"
                                viewBox="0 0 600 165"
                                preserveAspectRatio="none"
                                role="img"
                                aria-label="Illustrative hotspot trend, not real data"
                            >
                                <defs>
                                    <linearGradient
                                        id="nf-chart-fill"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="0%"
                                            stop-color="#43a978"
                                            stop-opacity=".24"
                                        />
                                        <stop
                                            offset="100%"
                                            stop-color="#43a978"
                                            stop-opacity="0"
                                        />
                                    </linearGradient>
                                </defs>

                                <line x1="10" y1="20" x2="590" y2="20" class="nf-chart-grid" />
                                <line x1="10" y1="60" x2="590" y2="60" class="nf-chart-grid" />
                                <line x1="10" y1="100" x2="590" y2="100" class="nf-chart-grid" />
                                <line x1="10" y1="155" x2="590" y2="155" class="nf-chart-grid" />

                                <path :d="chartArea" fill="url(#nf-chart-fill)" />
                                <path :d="chartLine" class="nf-chart-line" />

                                <circle
                                    v-for="(point, index) in chartPoints"
                                    :key="index"
                                    :cx="point.x"
                                    :cy="point.y"
                                    r="4"
                                    class="nf-chart-point"
                                />
                            </svg>
                        </div>

                        <div class="nf-chart-x-labels">
                            <span>Period start</span>
                            <span>Mid-period</span>
                            <span>Period end</span>
                        </div>

                        <div class="nf-panel-footnote">
                            <span>ⓘ</span>
                            Example visualization only. Real hotspot records are not plotted.
                        </div>
                    </article>

                    <article class="nf-panel nf-region-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">REGIONAL OVERVIEW</div>
                                <h2>Regional distribution</h2>
                                <p>Regions to monitor</p>
                            </div>

                            <span class="nf-mini-icon">⌖</span>
                        </div>

                        <div class="nf-region-list">
                            <div
                                v-for="(region, index) in regions"
                                :key="region.name"
                                class="nf-region-item"
                            >
                                <div class="nf-region-top">
                                    <span class="nf-region-number">
                                        0{{ index + 1 }}
                                    </span>
                                    <span class="nf-region-name">{{ region.name }}</span>
                                    <span class="nf-region-value">—</span>
                                </div>

                                <div class="nf-progress-track">
                                    <div
                                        class="nf-progress-fill"
                                        :style="{ width: `${region.width}%` }"
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="nf-panel-footnote">
                            <span>ⓘ</span>
                            Decorative bars only; regional totals are not yet available.
                        </div>
                    </article>
                </section>

                <!-- Map preview and weather snapshot -->
                <section class="nf-secondary-grid">
                    <article class="nf-panel nf-map-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">GEOSPATIAL MONITORING</div>
                                <h2>Indonesia overview</h2>
                                <p>Hotspot geographic visualization</p>
                            </div>

                            <Link href="/hotspot-map" class="nf-outline-button">
                                Explore map ↗
                            </Link>
                        </div>

                        <div class="nf-map-preview">
                            <div class="nf-map-grid" />

                            <svg
                                viewBox="0 0 650 250"
                                class="nf-island-art"
                                role="img"
                                aria-label="Decorative island illustration, not a geographic map"
                            >
                                <path d="M65 82l35-20 35 8 18 20-14 17-28 4-12 18-23-4-18-17z" class="nf-island" />
                                <path d="M155 148l22-9 21 9 18 28-9 35-16 12-12-20-17-18z" class="nf-island" />
                                <path d="M238 63l20-10 17 13-6 17-20 5-14-10z" class="nf-island" />
                                <path d="M270 102l18-9 14 12-6 18-20 5-13-12z" class="nf-island" />
                                <path d="M335 112l24-17 25 5 17 19-11 17-24-3-17 12-18-12z" class="nf-island" />
                                <path d="M420 73l35-16 38 11 18 20-13 19-32 6-19 20-25-10-15-22z" class="nf-island" />
                                <path d="M505 155l21-9 19 12-5 17-25 5-14-11z" class="nf-island" />

                                <circle cx="130" cy="92" r="4" class="nf-map-dot" />
                                <circle cx="183" cy="174" r="4" class="nf-map-dot" />
                                <circle cx="355" cy="119" r="4" class="nf-map-dot" />
                                <circle cx="456" cy="88" r="4" class="nf-map-dot" />
                            </svg>

                            <div class="nf-map-placeholder">
                                <span class="nf-map-placeholder-icon">⌖</span>
                                <strong>Geospatial layer not connected</strong>
                                <span>
                                    Connect geographic boundaries and hotspot coordinates
                                    to display a real map.
                                </span>

                                <Link href="/hotspot-map" class="nf-map-link">
                                    Open Hotspot Map
                                </Link>
                            </div>

                            <span class="nf-map-disclaimer">
                                DECORATIVE PREVIEW · NOT A GEOGRAPHIC BASEMAP
                            </span>
                        </div>
                    </article>

                    <article class="nf-panel nf-weather-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">ENVIRONMENTAL CONDITIONS</div>
                                <h2>Weather snapshot</h2>
                                <p>Weather indicators</p>
                            </div>

                            <span class="nf-weather-symbol">☼</span>
                        </div>

                        <div class="nf-weather-list">
                            <div
                                v-for="item in weatherItems"
                                :key="item.label"
                                class="nf-weather-item"
                            >
                                <span class="nf-weather-icon">{{ item.icon }}</span>

                                <div class="nf-weather-copy">
                                    <span>{{ item.label }}</span>
                                    <strong>
                                        {{ item.value }}
                                        <small>{{ item.unit }}</small>
                                    </strong>
                                </div>
                            </div>
                        </div>

                        <div class="nf-weather-source">
                            <span class="nf-status-dot" />
                            NASA POWER · Pending integration
                        </div>

                        <Link href="/weather-analysis" class="nf-weather-link">
                            View weather analysis →
                        </Link>
                    </article>
                </section>

                <footer class="nf-footer">
                    <div>
                        <span class="nf-footer-mark">N</span>
                        <span>
                            NusaFire
                            <span class="nf-footer-muted">· Environmental Intelligence</span>
                        </span>
                    </div>

                    <span>BUILT FOR A SAFER, GREENER FUTURE</span>
                </footer>
            </div>
        </main>
    </div>
</template>

<style>
.nf-app {
    --db-bg: #f5f7f4;
    --db-surface: #fff;
    --db-surface-soft: #f8faf7;
    --db-text: #1c2922;
    --db-text-soft: #526158;
    --db-muted: #859087;
    --db-border: #e5eae4;
    --db-accent: #2d8a5b;
    --db-accent-soft: #e8f5ec;
    --db-chart-grid: #e9eee9;
    --db-shadow: 0 4px 20px rgb(23 49 33 / 3%);

    min-height: 100vh;
    color: var(--db-text);
    background: var(--db-bg);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    transition: background .2s ease, color .2s ease;
}

.nf-app.theme-dark {
    --db-bg: #111914;
    --db-surface: #19231c;
    --db-surface-soft: #1d2921;
    --db-text: #edf4ed;
    --db-text-soft: #b0bdb2;
    --db-muted: #849489;
    --db-border: #2b3a2e;
    --db-accent: #70cf98;
    --db-accent-soft: #213b2b;
    --db-chart-grid: #2b382e;
    --db-shadow: 0 4px 20px rgb(0 0 0 / 10%);
}

.nf-app *,
.nf-app *::before,
.nf-app *::after {
    box-sizing: border-box;
}

.nf-app button,
.nf-app select {
    font: inherit;
}

.nf-app button {
    cursor: pointer;
}

.nf-main {
    min-height: 100vh;
    margin-left: 252px;
    transition: margin-left .3s cubic-bezier(.4,0,.2,1);
}

.nf-main.nf-sidebar-collapsed {
    margin-left: 0;
}

.nf-topbar {
    position: sticky;
    top: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 68px;
    padding: 0 36px;
    background: var(--db-surface);
    border-bottom: 1px solid var(--db-border);
}

.nf-topbar-left,
.nf-topbar-right {
    display: flex;
    align-items: center;
    gap: 20px;
}

.nf-breadcrumb {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--db-muted);
    font-size: 11px;
}

.nf-breadcrumb strong {
    color: var(--db-text);
    font-weight: 650;
}

.nf-breadcrumb-separator {
    color: var(--db-border);
}

.nf-live-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--db-text-soft);
    font-size: 10px;
}

.nf-status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    background: #58b77b;
    border-radius: 50%;
}

.nf-theme-toggle,
.nf-icon-button {
    display: grid;
    width: 36px;
    height: 36px;
    place-items: center;
    color: var(--db-text-soft);
    background: var(--db-surface-soft);
    border: 1px solid var(--db-border);
    border-radius: 10px;
    font-size: 18px;
    cursor: pointer;
    transition: color .15s ease, background .15s ease;
}

.nf-theme-toggle:hover,
.nf-icon-button:hover {
    color: var(--db-accent);
    background: var(--db-accent-soft);
}

.nf-mobile-menu {
    display: none;
}

.nf-mobile-menu.nf-menu-visible {
    display: grid;
}

.nf-content {
    width: 100%;
    max-width: 1600px;
    padding: 34px 36px 22px;
    margin: 0 auto;
}

.nf-page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 28px;
}

.nf-eyebrow,
.nf-panel-kicker {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--db-accent);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.45px;
}

.nf-eyebrow-line {
    display: inline-block;
    width: 17px;
    height: 2px;
    background: var(--db-accent);
}

.nf-page-heading h1 {
    margin: 12px 0 8px;
    font-size: clamp(26px, 3vw, 34px);
    font-weight: 750;
    letter-spacing: -1.3px;
    line-height: 1.2;
}

.nf-page-heading p {
    margin: 0;
    color: var(--db-text-soft);
    font-size: 12px;
    line-height: 1.7;
}

.nf-heading-date {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 15px;
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-radius: 10px;
}

.nf-date-icon {
    display: grid;
    width: 31px;
    height: 31px;
    place-items: center;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 8px;
    font-size: 18px;
}

.nf-heading-date div {
    display: grid;
    gap: 4px;
}

.nf-heading-date strong {
    font-size: 10px;
}

.nf-heading-date div span {
    color: var(--db-muted);
    font-size: 9px;
}

.nf-stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 15px;
    margin-bottom: 18px;
}

.nf-stat-card,
.nf-panel {
    min-width: 0;
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-radius: 13px;
    box-shadow: var(--db-shadow);
}

.nf-stat-card {
    padding: 19px 19px 16px;
}

.nf-stat-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.nf-stat-label {
    color: var(--db-text-soft);
    font-size: 11px;
    font-weight: 550;
}

.nf-stat-icon {
    display: grid;
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    place-items: center;
    border-radius: 9px;
    font-size: 19px;
}

.nf-icon-green {
    color: #2f9860;
    background: #e5f5e9;
}

.nf-icon-orange {
    color: #d27d42;
    background: #fff0e3;
}

.nf-icon-yellow {
    color: #c49a31;
    background: #fff6d9;
}

.nf-icon-blue {
    color: #508ec5;
    background: #e7f3ff;
}

.nf-stat-value {
    margin: 19px 0 16px;
    font-size: 31px;
    font-weight: 750;
    letter-spacing: -1px;
}

.nf-stat-value small {
    color: var(--db-text-soft);
    font-size: 13px;
    font-weight: 550;
    letter-spacing: 0;
}

.nf-stat-bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid var(--db-border);
}

.nf-stat-caption {
    color: var(--db-muted);
    font-size: 9px;
}

.nf-stat-tag {
    padding: 4px 6px;
    color: var(--db-text-soft);
    background: var(--db-surface-soft);
    border-radius: 5px;
    font-size: 8px;
}

.nf-primary-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.65fr) minmax(260px, 1fr);
    gap: 18px;
    margin-bottom: 18px;
}

.nf-panel {
    padding: 22px;
}

.nf-panel-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
}

.nf-panel-heading h2 {
    margin: 8px 0 5px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -.3px;
}

.nf-panel-heading p {
    margin: 0;
    color: var(--db-muted);
    font-size: 10px;
    line-height: 1.6;
}

.nf-select {
    max-width: 115px;
    padding: 8px 10px;
    color: var(--db-text);
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-radius: 8px;
    outline: none;
    font-size: 10px;
}

.nf-select:focus {
    border-color: var(--db-accent);
}

.nf-chart-legend {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 24px;
    color: var(--db-text-soft);
    font-size: 10px;
}

.nf-legend-dot {
    width: 7px;
    height: 7px;
    background: #43a978;
    border-radius: 50%;
}

.nf-demo-label {
    margin-left: auto;
    color: var(--db-muted);
    font-size: 9px;
}

.nf-chart-wrap {
    display: flex;
    gap: 12px;
    height: 165px;
    margin-top: 16px;
}

.nf-chart-y-labels {
    display: flex;
    flex: 0 0 42px;
    flex-direction: column;
    justify-content: space-between;
    color: var(--db-muted);
    font-size: 9px;
    text-align: right;
}

.nf-line-chart {
    width: 100%;
    height: 100%;
    overflow: visible;
}

.nf-chart-grid {
    stroke: var(--db-chart-grid);
    stroke-width: 1;
    stroke-dasharray: 3 5;
}

.nf-chart-line {
    fill: none;
    stroke: #43a978;
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.nf-chart-point {
    fill: #43a978;
    stroke: var(--db-surface);
    stroke-width: 2;
}

.nf-chart-x-labels {
    display: flex;
    justify-content: space-between;
    margin: 12px 0 0 54px;
    color: var(--db-muted);
    font-size: 9px;
}

.nf-panel-footnote {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    margin-top: 19px;
    padding-top: 13px;
    color: var(--db-muted);
    border-top: 1px solid var(--db-border);
    font-size: 9px;
    line-height: 1.6;
}

.nf-panel-footnote > span {
    color: var(--db-accent);
}

.nf-mini-icon {
    display: grid;
    width: 31px;
    height: 31px;
    place-items: center;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 8px;
    font-size: 20px;
}

.nf-region-list {
    display: grid;
    gap: 23px;
    margin-top: 30px;
}

.nf-region-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 9px;
}

.nf-region-number {
    color: var(--db-muted);
    font-size: 9px;
}

.nf-region-name {
    flex: 1;
    font-size: 11px;
    font-weight: 600;
}

.nf-region-value {
    color: var(--db-text-soft);
    font-size: 10px;
}

.nf-progress-track {
    height: 5px;
    overflow: hidden;
    background: var(--db-surface-soft);
    border-radius: 20px;
}

.nf-progress-fill {
    height: 100%;
    background: #43a978;
    border-radius: inherit;
    opacity: .85;
}

.nf-secondary-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(260px, 1fr);
    gap: 18px;
    margin-bottom: 26px;
}

.nf-outline-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 9px 11px;
    color: var(--db-accent);
    text-decoration: none;
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-radius: 8px;
    font-size: 10px;
    font-weight: 650;
    white-space: nowrap;
}

.nf-outline-button:hover {
    background: var(--db-accent-soft);
}

.nf-map-preview {
    position: relative;
    display: grid;
    min-height: 265px;
    overflow: hidden;
    margin-top: 20px;
    place-items: center;
    background: var(--db-surface-soft);
    border: 1px solid var(--db-border);
    border-radius: 10px;
}

.nf-map-grid {
    position: absolute;
    inset: 0;
    opacity: .45;
    background-image:
        linear-gradient(var(--db-border) 1px, transparent 1px),
        linear-gradient(90deg, var(--db-border) 1px, transparent 1px);
    background-size: 28px 28px;
}

.nf-island-art {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    padding: 8px;
    opacity: .68;
}

.nf-island {
    fill: #8cbd9a;
    stroke: #4c9966;
    stroke-width: 1.5;
}

.nf-map-dot {
    fill: #e6a65d;
    stroke: var(--db-surface);
    stroke-width: 2;
}

.nf-map-placeholder {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    flex-direction: column;
    max-width: 265px;
    padding: 17px;
    text-align: center;
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-radius: 12px;
    box-shadow: var(--db-shadow);
}

.nf-map-placeholder-icon {
    display: grid;
    width: 35px;
    height: 35px;
    margin-bottom: 10px;
    place-items: center;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 10px;
    font-size: 22px;
}

.nf-map-placeholder strong {
    margin-bottom: 7px;
    font-size: 11px;
}

.nf-map-placeholder > span:not(.nf-map-placeholder-icon) {
    color: var(--db-text-soft);
    font-size: 9px;
    line-height: 1.7;
}

.nf-map-link {
    margin-top: 12px;
    color: var(--db-accent);
    font-size: 10px;
    font-weight: 650;
    text-decoration: none;
}

.nf-map-link:hover,
.nf-weather-link:hover {
    text-decoration: underline;
}

.nf-map-disclaimer {
    position: absolute;
    right: 10px;
    bottom: 9px;
    color: var(--db-muted);
    font-size: 7px;
    font-weight: 700;
    letter-spacing: .8px;
}

.nf-weather-symbol {
    color: #d4aa48;
    font-size: 28px;
}

.nf-weather-list {
    display: grid;
    margin-top: 20px;
}

.nf-weather-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid var(--db-border);
}

.nf-weather-icon {
    display: grid;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    place-items: center;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 10px;
    font-size: 21px;
}

.nf-weather-copy {
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.nf-weather-copy > span {
    color: var(--db-text-soft);
    font-size: 10px;
}

.nf-weather-copy strong {
    font-size: 17px;
}

.nf-weather-copy small {
    color: var(--db-muted);
    font-size: 10px;
    font-weight: 500;
}

.nf-weather-source {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 17px;
    color: var(--db-muted);
    font-size: 9px;
}

.nf-weather-link {
    display: inline-block;
    margin-top: 16px;
    color: var(--db-accent);
    font-size: 10px;
    font-weight: 650;
    text-decoration: none;
}

.nf-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    padding: 18px 0 0;
    color: var(--db-text-soft);
    border-top: 1px solid var(--db-border);
    font-size: 9px;
}

.nf-footer > div {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 650;
}

.nf-footer-mark {
    display: grid;
    width: 22px;
    height: 22px;
    place-items: center;
    color: #fff;
    background: #287a50;
    border-radius: 6px;
    font-size: 11px;
}

.nf-footer-muted {
    color: var(--db-muted);
    font-weight: 400;
}

.nf-footer > span {
    color: var(--db-muted);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: .9px;
}

@media (min-width: 1500px) {
    .nf-content {
        padding-right: 48px;
        padding-left: 48px;
    }

    .nf-topbar {
        padding-right: 48px;
        padding-left: 48px;
    }
}

@media (max-width: 1200px) {
    .nf-content {
        padding-right: 24px;
        padding-left: 24px;
    }

    .nf-topbar {
        padding-right: 24px;
        padding-left: 24px;
    }

    .nf-stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {
    .nf-main {
        margin-left: 0;
    }

    .nf-mobile-menu {
        display: grid;
    }

    .nf-primary-grid,
    .nf-secondary-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 600px) {
    .nf-topbar {
        min-height: 60px;
        padding: 0 15px;
    }

    .nf-topbar-left,
    .nf-topbar-right {
        gap: 10px;
    }

    .nf-live-indicator {
        display: none;
    }

    .nf-content {
        padding: 25px 14px 20px;
    }

    .nf-page-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 21px;
    }

    .nf-page-heading h1 {
        font-size: 27px;
    }

    .nf-heading-date {
        width: 100%;
    }

    .nf-stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    .nf-stat-card {
        padding: 14px 12px;
    }

    .nf-stat-label {
        font-size: 10px;
        line-height: 1.5;
    }

    .nf-stat-icon {
        width: 28px;
        height: 28px;
        flex-basis: 28px;
        font-size: 16px;
    }

    .nf-stat-value {
        margin: 15px 0 13px;
        font-size: 26px;
    }

    .nf-stat-bottom {
        align-items: flex-start;
        flex-direction: column;
        gap: 7px;
    }

    .nf-panel {
        padding: 17px 14px;
    }

    .nf-panel-heading h2 {
        font-size: 14px;
    }

    .nf-select {
        max-width: 94px;
        padding: 7px 5px;
    }

    .nf-chart-wrap {
        height: 145px;
    }

    .nf-chart-x-labels {
        margin-left: 46px;
    }

    .nf-map-preview {
        min-height: 235px;
    }

    .nf-map-placeholder {
        max-width: 230px;
        padding: 13px;
    }

    .nf-footer {
        align-items: flex-start;
        flex-direction: column;
        gap: 11px;
    }

    .nf-footer > span {
        line-height: 1.6;
    }
}

@media (prefers-reduced-motion: reduce) {
    .nf-app *,
    .nf-app *::before,
    .nf-app *::after {
        transition: none !important;
    }
}
</style>
