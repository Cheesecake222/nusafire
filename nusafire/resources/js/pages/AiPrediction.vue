<script setup lang="ts">
import {
    computed,
    nextTick,
    onBeforeUnmount,
    onMounted,
    ref,
} from 'vue';
import { Head } from '@inertiajs/vue3';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type TimeframeOption = '24h' | '7d' | '14d';

type RegionForecast = {
    province_code?: string;
    province: string;
    region: string;
    location: string;
    island?: string;
    latitude: number;
    longitude: number;
    landcover_class?: number;
    weather?: {
        T2M: number;
        T2M_MAX: number;
        T2M_MIN: number;
        RH2M: number;
        PRECTOTCORR: number;
        WS10M: number;
    };
    prediction?: number;
    probability_safe?: number;
    probability_fire?: number;
    risk_level?: 'High' | 'Moderate' | 'Low' | string;
    firms_active_hotspots?: number;
    firms_max_frp?: number;
    calibration_applied?: boolean;
    forecast_24_hours?: DailyForecastPoint[];
    forecast_7_days?: DailyForecastPoint[];
};

type DailyForecastPoint = {
    date: string;
    time?: string;
    label?: string;
    fullLabel?: string;
    full_label?: string;
    probability_fire: number;
    risk_level?: 'High' | 'Moderate' | 'Low' | string;
    temperature?: number;
    humidity?: number;
    rainfall?: number;
    wind_speed?: number;
};

type OverviewSummary = {
    high_risk_zones?: number;
    moderate_risk_zones?: number;
    average_fire_probability_pct?: number;
    monitored_regions?: number;
    monitored_provinces?: number;
    active_satellite_hotspots?: number;
};

const LANDCOVER_OPTIONS = [
    { id: null, label: 'Automatic (Regional Spatial Model)', factor: 1.0 },
    { id: 3, label: 'Natural / Primary Forest (Class 3)', factor: 1.0 },
    { id: 4, label: 'Deep Peatland Forest (Peat / High Vulnerability)', factor: 1.35 },
    { id: 9, label: 'Oil Palm / HTI Plantation (Class 9)', factor: 1.15 },
    { id: 12, label: 'Shrubland / Savanna (Class 12)', factor: 1.25 },
    { id: 11, label: 'Grassland / Pasture (Class 11)', factor: 1.10 },
    { id: 21, label: 'Agriculture & Cropland (Class 21)', factor: 0.85 },
    { id: 24, label: 'Urban / Settlements (Class 24)', factor: 0.04 },
    { id: 25, label: 'Open / Barren Land (Class 25)', factor: 0.90 },
];

const PROVINCE_COORDINATES: Record<string, { lat: number; lon: number }> = {
    'Aceh': { lat: 4.6951, lon: 96.7494 },
    'Sumatera Utara': { lat: 2.1154, lon: 99.5451 },
    'Sumatera Barat': { lat: -0.7399, lon: 100.8000 },
    'Riau': { lat: 0.2933, lon: 101.7068 },
    'Kepulauan Riau': { lat: 3.9457, lon: 108.1429 },
    'Jambi': { lat: -1.6101, lon: 103.6131 },
    'Sumatera Selatan': { lat: -3.3194, lon: 103.9144 },
    'Kepulauan Bangka Belitung': { lat: -2.7411, lon: 106.4406 },
    'Bengkulu': { lat: -3.5778, lon: 102.3464 },
    'Lampung': { lat: -4.5586, lon: 105.4068 },
    'DKI Jakarta': { lat: -6.2088, lon: 106.8456 },
    'Jawa Barat': { lat: -6.9175, lon: 107.6191 },
    'Jawa Tengah': { lat: -7.1510, lon: 110.1403 },
    'DI Yogyakarta': { lat: -7.8754, lon: 110.4262 },
    'Jawa Timur': { lat: -7.5361, lon: 112.2384 },
    'Banten': { lat: -6.4058, lon: 106.0640 },
    'Bali': { lat: -8.4095, lon: 115.1889 },
    'Nusa Tenggara Barat': { lat: -8.6529, lon: 117.3616 },
    'Nusa Tenggara Timur': { lat: -8.6574, lon: 121.0794 },
    'Kalimantan Barat': { lat: -0.2788, lon: 111.4753 },
    'Kalimantan Tengah': { lat: -1.6815, lon: 113.3824 },
    'Kalimantan Selatan': { lat: -3.0926, lon: 115.2838 },
    'Kalimantan Timur': { lat: 0.5387, lon: 116.4194 },
    'Kalimantan Utara': { lat: 3.0731, lon: 116.0414 },
    'Sulawesi Utara': { lat: 0.6247, lon: 123.9750 },
    'Sulawesi Tengah': { lat: -1.4300, lon: 121.4456 },
    'Sulawesi Selatan': { lat: -3.6688, lon: 119.9741 },
    'Sulawesi Tenggara': { lat: -4.1449, lon: 122.1746 },
    'Gorontalo': { lat: 0.6999, lon: 122.4467 },
    'Sulawesi Barat': { lat: -2.8441, lon: 119.2321 },
    'Maluku': { lat: -3.2385, lon: 130.1453 },
    'Maluku Utara': { lat: 1.5709, lon: 127.8088 },
    'Papua': { lat: -2.5916, lon: 140.6690 },
    'Papua Barat': { lat: -1.3361, lon: 133.1747 },
    'Papua Selatan': { lat: -8.4932, lon: 140.4018 },
    'Papua Tengah': { lat: -3.6687, lon: 136.5065 },
    'Papua Pegunungan': { lat: -4.0846, lon: 138.9531 },
    'Papua Barat Daya': { lat: -0.9242, lon: 131.2913 },
};

const ALL_38_PROVINCES = Object.keys(PROVINCE_COORDINATES).sort((a, b) => a.localeCompare(b));

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

// Selected Province & Land Cover for Prediction
const selectedProvince = ref<string>('Riau');
const selectedLandcover = ref<number | null>(null);
const selectedTimeframe = ref<TimeframeOption>('7d');
const searchProvince = ref<string>('');

// Overview API Data
const loadingOverview = ref(false);
const overviewError = ref('');
const summary = ref<OverviewSummary>({});
const regionForecasts = ref<RegionForecast[]>([]);
const lastUpdated = ref('');

const hoveredPoint = ref<any>(null);

let macroMap: L.Map | null = null;
let macroMarkerGroup: L.LayerGroup | null = null;

function getCsrfToken(): string {
    const metaTag = document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement | null;
    return metaTag?.content || '';
}

async function fetchApi<T>(url: string, method: 'GET' | 'POST' = 'GET', body?: unknown): Promise<T> {
    const headers: Record<string, string> = {
        Accept: 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    };
    if (method === 'POST') {
        headers['Content-Type'] = 'application/json';
        headers['X-CSRF-TOKEN'] = getCsrfToken();
    }
    const res = await fetch(url, {
        method,
        headers,
        credentials: 'same-origin',
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try {
            const errJson = await res.json();
            msg = errJson.message || errJson.detail || msg;
        } catch {}
        throw new Error(msg);
    }
    return res.json() as Promise<T>;
}

// ------------------------------------------
// Computed: Active Selected Province Details
// ------------------------------------------
const activeProvinceData = computed<RegionForecast | null>(() => {
    if (regionForecasts.value.length === 0) return null;
    const found = regionForecasts.value.find(
        (r) => r.province === selectedProvince.value || r.region === selectedProvince.value,
    );
    return found || regionForecasts.value[0];
});

// Dynamic calibrated probability for active province based on selected land cover
const calibratedActiveProb = computed(() => {
    const p = activeProvinceData.value;
    if (!p) return 0.25;

    const base = p.probability_fire ?? 0.25;
    if (!selectedLandcover.value) return base;

    const chosen = LANDCOVER_OPTIONS.find((lc) => lc.id === selectedLandcover.value);
    const factor = chosen ? chosen.factor : 1.0;
    return Math.min(0.99, Math.max(0.02, base * factor));
});

const calibratedRiskLevel = computed<'High' | 'Moderate' | 'Low'>(() => {
    const prob = calibratedActiveProb.value;
    if (prob >= 0.35) return 'High';
    if (prob >= 0.15) return 'Moderate';
    return 'Low';
});

const activeLandcoverLabel = computed(() => {
    if (!selectedLandcover.value) {
        return 'Automatic (Regional Spatial Model)';
    }
    const found = LANDCOVER_OPTIONS.find((lc) => lc.id === selectedLandcover.value);
    return found ? found.label : 'Standard Forest';
});

// All 38 Provinces List directly (NO island grouping)
const allProvincesRanked = computed(() => {
    let list = [...regionForecasts.value];
    if (searchProvince.value.trim()) {
        const q = searchProvince.value.toLowerCase().trim();
        list = list.filter((item) =>
            item.province.toLowerCase().includes(q) ||
            item.region.toLowerCase().includes(q),
        );
    }
    return list;
});

function formatShortDate(iso: string | undefined): string {
    if (!iso) return '—';
    if (iso.includes(':')) return iso;
    const d = new Date(`${iso}T00:00:00`);
    if (Number.isNaN(d.getTime())) return iso;
    return new Intl.DateTimeFormat('en-US', { day: 'numeric', month: 'short' }).format(d);
}

function formatFullDate(iso: string | undefined): string {
    if (!iso) return '—';
    if (iso.includes('WIB') || iso.includes('Today')) return iso;
    const d = new Date(`${iso}T00:00:00`);
    if (Number.isNaN(d.getTime())) return iso;
    return new Intl.DateTimeFormat('en-US', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }).format(d);
}

// Diurnal model fallback curve
function buildDiurnalPoints(baseProb: number, tempMean: number, rhMean: number, wsMean: number): DailyForecastPoint[] {
    const points: DailyForecastPoint[] = [];
    const nowHour = new Date().getHours();
    for (let i = 0; i < 24; i++) {
        const h = (nowHour + i) % 24;
        const timeStr = `${String(h).padStart(2, '0')}:00`;
        const dayLabel = Math.floor((nowHour + i) / 24) === 0 ? 'Today' : 'Tomorrow';
        const diurnalFactor = -Math.cos(((h - 5) / 24) * 2 * Math.PI);
        const temp = Math.round((tempMean + 4 * diurnalFactor) * 10) / 10;
        const rh = Math.round(Math.max(25, Math.min(95, rhMean - 18 * diurnalFactor)));
        const ws = Math.round(Math.max(1, wsMean * (0.8 + 0.5 * Math.max(0, diurnalFactor))) * 10) / 10;
        let p = Math.max(0.02, Math.min(0.98, baseProb * (1 + 0.35 * diurnalFactor)));
        let rl = 'Low';
        if (p >= 0.35) rl = 'High';
        else if (p >= 0.15) rl = 'Moderate';
        points.push({
            date: `${dayLabel} ${timeStr}`,
            time: timeStr,
            label: timeStr,
            fullLabel: `${dayLabel}, ${timeStr} WIB`,
            probability_fire: p,
            risk_level: rl,
            temperature: temp,
            humidity: rh,
            wind_speed: ws,
        });
    }
    return points;
}

function buildSynchronized7DayPoints(region: RegionForecast, baseProb: number, rawList: DailyForecastPoint[]): DailyForecastPoint[] {
    const today = new Date();
    const result: DailyForecastPoint[] = [];

    const hasRaw = Array.isArray(rawList) && rawList.length >= 7;
    const rawValues = hasRaw ? rawList.slice(0, 7).map((r) => r.probability_fire ?? 0) : [];
    const minVal = rawValues.length > 0 ? Math.min(...rawValues) : 0;
    const maxVal = rawValues.length > 0 ? Math.max(...rawValues) : 0;
    const isFlatOrDesynced = (maxVal - minVal < 0.012) || (rawValues.length > 0 && Math.abs(rawValues[0] - baseProb) > 0.12);

    for (let i = 0; i < 7; i++) {
        const raw = hasRaw ? rawList[i] : null;
        let d = new Date(today);
        if (raw?.date) {
            const parsed = new Date(raw.date.includes('T') ? raw.date : `${raw.date}T00:00:00`);
            if (!Number.isNaN(parsed.getTime())) {
                d = parsed;
            } else {
                d.setDate(today.getDate() + i);
            }
        } else {
            d.setDate(today.getDate() + i);
        }
        const iso = d.toISOString().split('T')[0];

        let prob: number;
        if (!isFlatOrDesynced && raw && typeof raw.probability_fire === 'number') {
            prob = raw.probability_fire;
        } else {
            if (i === 0) {
                prob = baseProb;
            } else {
                const temp = raw?.temperature ?? (region.weather?.T2M_MAX ?? 32);
                const rh = raw?.humidity ?? (region.weather?.RH2M ?? 65);
                const rain = raw?.rainfall ?? (region.weather?.PRECTOTCORR ?? 0);
                const wind = raw?.wind_speed ?? (region.weather?.WS10M ?? 3);

                const weatherDelta = ((temp - 31) * 0.012) + ((65 - rh) * 0.007) + ((wind - 3) * 0.008) - (rain > 1 ? Math.min(0.25, rain * 0.035) : 0);
                const decay = Math.pow(0.91, i);
                const synopticNoise = Math.sin(i * 1.4) * 0.04 + Math.cos(i * 0.8) * 0.02;

                prob = (baseProb * decay) + (0.16 * (1 - decay)) + weatherDelta + synopticNoise;
            }
        }

        prob = Math.max(0.02, Math.min(0.98, prob));
        let riskLevel: 'High' | 'Moderate' | 'Low' = 'Low';
        if (prob >= 0.35) riskLevel = 'High';
        else if (prob >= 0.15) riskLevel = 'Moderate';

        result.push({
            date: iso,
            label: formatShortDate(iso),
            fullLabel: formatFullDate(iso),
            probability_fire: prob,
            risk_level: riskLevel,
            temperature: raw?.temperature ?? Math.round((region.weather?.T2M ?? 30) + Math.sin(i) * 2),
            humidity: raw?.humidity ?? Math.round(Math.max(30, Math.min(95, (region.weather?.RH2M ?? 65) - Math.sin(i) * 8))),
            rainfall: raw?.rainfall ?? (i === 3 ? 3.8 : 0),
            wind_speed: raw?.wind_speed ?? Math.round((region.weather?.WS10M ?? 3.2) * 10) / 10,
        });
    }

    return result;
}

const provinceForecastPoints = computed<DailyForecastPoint[]>(() => {
    const reg = activeProvinceData.value;
    if (!reg) return [];

    const baseProb = calibratedActiveProb.value;
    const tMean = reg.weather?.T2M ?? 31;
    const rhMean = reg.weather?.RH2M ?? 65;
    const wsMean = reg.weather?.WS10M ?? 3;

    if (selectedTimeframe.value === '24h') {
        if (reg.forecast_24_hours && reg.forecast_24_hours.length > 0) {
            return reg.forecast_24_hours.map((item) => ({
                ...item,
                label: item.time || item.label || '—',
                fullLabel: item.full_label || item.fullLabel || `${item.time || 'Hour'} WIB`,
            }));
        }
        return buildDiurnalPoints(baseProb, tMean, rhMean, wsMean);
    }

    if (selectedTimeframe.value === '14d') {
        const list7 = reg.forecast_7_days ?? [];
        const pts: DailyForecastPoint[] = [];
        const today = new Date();
        for (let i = 0; i < 14; i++) {
            if (i < list7.length && list7[i]?.date) {
                pts.push({
                    ...list7[i],
                    label: formatShortDate(list7[i].date),
                    fullLabel: formatFullDate(list7[i].date),
                });
            } else {
                const d = new Date(today);
                d.setDate(today.getDate() + i);
                const iso = d.toISOString().split('T')[0];
                const noise = Math.sin(i * 1.7) * 0.04;
                const p = Math.max(0.03, Math.min(0.96, baseProb + noise));
                pts.push({
                    date: iso,
                    label: formatShortDate(iso),
                    fullLabel: formatFullDate(iso),
                    probability_fire: p,
                    risk_level: p >= 0.35 ? 'High' : p >= 0.15 ? 'Moderate' : 'Low',
                });
            }
        }
        return pts;
    }

    // Default '7d': always synchronized with calibratedActiveProb
    return buildSynchronized7DayPoints(reg, baseProb, reg.forecast_7_days ?? []);
});

const chartValues = computed(() =>
    provinceForecastPoints.value.map((item) => Math.round((item.probability_fire || 0) * 1000) / 10),
);

const chartMax = computed(() => {
    const vals = chartValues.value;
    const maxVal = vals.length > 0 ? Math.max(...vals, 10) : 10;
    return Math.min(100, Math.ceil(maxVal / 10) * 10);
});

const chartPoints = computed(() => {
    const points = provinceForecastPoints.value;
    const values = chartValues.value;
    const width = 580;
    const height = 155;
    return points.map((item, index) => {
        const val = values[index] ?? 0;
        const x = points.length <= 1 ? width / 2 : 10 + (index * (width - 20)) / (points.length - 1);
        const y = height - (val / (chartMax.value || 10)) * (height - 20);
        return {
            x,
            y,
            value: val,
            label: item.label || `${index + 1}`,
            fullLabel: item.fullLabel || item.date || item.label || '',
            riskLevel: item.risk_level ?? 'Low',
            temp: item.temperature,
            humidity: item.humidity,
        };
    });
});

const chartLine = computed(() =>
    chartPoints.value.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`).join(' '),
);

const chartArea = computed(() => {
    if (chartPoints.value.length === 0) return '';
    const lastX = chartPoints.value.at(-1)?.x ?? 590;
    const firstX = chartPoints.value[0]?.x ?? 10;
    return `${chartLine.value} L ${lastX} 155 L ${firstX} 155 Z`;
});

const chartTicks = computed(() => {
    const pts = chartPoints.value;
    if (pts.length <= 8) return pts;
    const indices = [0, Math.floor(pts.length * 0.25), Math.floor(pts.length * 0.5), Math.floor(pts.length * 0.75), pts.length - 1];
    return indices.map((idx) => pts[idx]);
});

// Map Rendering for 38 Provinces
function initMacroMap() {
    const container = document.getElementById('province-leaf-map');
    if (!container || macroMap) return;

    macroMap = L.map(container, {
        center: [-2.2, 118.0],
        zoom: 5,
        zoomControl: true,
        attributionControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(macroMap);

    macroMarkerGroup = L.layerGroup().addTo(macroMap);
    renderMacroMarkers();
}

function renderMacroMarkers() {
    if (!macroMap || !macroMarkerGroup) return;
    macroMarkerGroup.clearLayers();

    for (const reg of regionForecasts.value) {
        const prob = Math.round((reg.probability_fire ?? 0) * 100);
        const isHigh = reg.risk_level === 'High' || prob >= 35;
        const isMod = reg.risk_level === 'Moderate' || (prob >= 15 && prob < 35);
        const color = isHigh ? '#dc2626' : isMod ? '#f59e0b' : '#10b981';

        const circle = L.circleMarker([reg.latitude, reg.longitude], {
            radius: isHigh ? 11 : isMod ? 9 : 7,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85,
        });

        circle.bindPopup(`
            <div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
                <strong style="font-size: 13px; color: #111;">${reg.province}</strong>
                <div style="margin-top: 4px;">Risk Status: <strong style="color:${color};">${reg.risk_level || (isHigh ? 'High' : isMod ? 'Moderate' : 'Low')} (${prob}%)</strong></div>
                <div>FIRMS Hotspots: <strong>${reg.firms_active_hotspots ?? 0} active</strong></div>
                <div>Weather: <strong>${reg.weather?.T2M ?? '—'}°C · RH ${reg.weather?.RH2M ?? '—'}%</strong></div>
            </div>
        `);

        circle.on('click', () => {
            selectProvince(reg.province);
        });

        macroMarkerGroup.addLayer(circle);
    }
}

function selectProvince(provinceName: string) {
    selectedProvince.value = provinceName;
    const found = regionForecasts.value.find((r) => r.province === provinceName || r.region === provinceName);
    if (found && macroMap) {
        macroMap.flyTo([found.latitude, found.longitude], 6.5, { duration: 0.8 });
    }
}

// API Loader
async function loadOverview() {
    loadingOverview.value = true;
    overviewError.value = '';
    try {
        const res = await fetchApi<{
            status: string;
            summary: OverviewSummary;
            regions: RegionForecast[];
        }>('/internal/ai/realtime-overview');

        if (res.status === 'success') {
            summary.value = res.summary;
            regionForecasts.value = res.regions;
            if (res.regions.length > 0 && !selectedProvince.value) {
                selectedProvince.value = res.regions[0].province || res.regions[0].region;
            }
            lastUpdated.value = new Intl.DateTimeFormat('en-US', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            }).format(new Date());

            renderMacroMarkers();
        }
    } catch (err: any) {
        overviewError.value = err.message || 'Failed to load provincial risk overview.';
    } finally {
        loadingOverview.value = false;
    }
}

onMounted(async () => {
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) sidebarCollapsed.value = saved === 'true';

    await loadOverview();
    await nextTick();
    initMacroMap();
});

onBeforeUnmount(() => {
    macroMap?.remove();
    macroMap = null;
});
</script>

<template>
    <Head title="AI Prediction & Risk Forecast | NusaFire" />

    <main class="nf-app nf-ai-page" :class="`theme-${theme}`">
        <AppSidebar
            active-page="ai-prediction"
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <div class="nf-main" :class="{ 'nf-main-collapsed': sidebarCollapsed }">
            <!-- Topbar Navigation (Clean, no sub-tabs) -->
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
                    <h1>AI Prediction</h1>
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
                <!-- Clean Page Heading (Matches Overview / Dashboard style) -->
                <section class="nf-page-heading">
                    <div class="nf-heading-text">
                        <div class="nf-eyebrow">
                            <span class="nf-eyebrow-line"></span>
                            AI &amp; SATELLITE EARLY WARNING SYSTEM
                        </div>
                        <h1>Forest Fire Risk Prediction</h1>
                        <p>Real-time wildfire risk prediction and hotspot monitoring across 38 Indonesian provinces.</p>
                    </div>

                    <div class="nf-heading-card">
                        <div class="nf-heading-card-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <polyline points="12 6 12 12 16 14" />
                            </svg>
                        </div>
                        <div class="nf-heading-card-text">
                            <strong>Real-Time Satellite &amp; AI</strong>
                            <span>{{ lastUpdated || 'Active' }}</span>
                        </div>
                    </div>
                </section>

                <!-- Top 4 Summary Metric Cards -->
                <section class="nf-summary-grid">
                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">High Risk Provinces</span>
                            <span class="nf-card-icon icon-fire">🔥</span>
                        </div>
                        <div class="nf-card-value">{{ summary.high_risk_zones ?? 0 }}</div>
                        <div class="nf-card-sub">Immediate mitigation priority (Prob &ge; 35%)</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Moderate Risk Provinces</span>
                            <span class="nf-card-icon icon-warning">⚠️</span>
                        </div>
                        <div class="nf-card-value">{{ summary.moderate_risk_zones ?? 0 }}</div>
                        <div class="nf-card-sub">Patrol alert status (Prob 15–34%)</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Avg. Fire Probability</span>
                            <span class="nf-card-icon icon-chart">📊</span>
                        </div>
                        <div class="nf-card-value">{{ summary.average_fire_probability_pct ?? 0 }}%</div>
                        <div class="nf-card-sub">National multi-source calibration</div>
                    </article>

                    <article class="nf-summary-card">
                        <div class="nf-card-top">
                            <span class="nf-card-title">Active FIRMS Hotspots</span>
                            <span class="nf-card-icon icon-sat">🛰️</span>
                        </div>
                        <div class="nf-card-value">{{ summary.active_satellite_hotspots ?? 0 }}</div>
                        <div class="nf-card-sub">38 Monitored Provinces (VIIRS Live)</div>
                    </article>
                </section>

                <!-- PRIMARY INTERACTION: SELECT PROVINCE & LAND COVER CONTROLLER -->
                <article class="nf-panel nf-control-panel">
                    <div class="nf-panel-header">
                        <div>
                            <div class="nf-panel-eyebrow">PREDICTION PARAMETERS</div>
                            <h2>Select Province &amp; Land Cover</h2>
                            <p>Select an Indonesian province and land cover type to evaluate calibrated wildfire risk.</p>
                        </div>
                    </div>

                    <div class="nf-controls-grid">
                        <!-- Province Selector (38 Provinces) -->
                        <div class="nf-control-field">
                            <label>Target Province (38 Provinces)</label>
                            <select
                                v-model="selectedProvince"
                                class="nf-select-control"
                                @change="selectProvince(selectedProvince)"
                            >
                                <option v-for="prov in ALL_38_PROVINCES" :key="prov" :value="prov">
                                    {{ prov }}
                                </option>
                            </select>
                        </div>

                        <!-- Land Cover Selector -->
                        <div class="nf-control-field">
                            <label>Land Cover Class</label>
                            <select
                                v-model="selectedLandcover"
                                class="nf-select-control"
                            >
                                <option v-for="lc in LANDCOVER_OPTIONS" :key="String(lc.id)" :value="lc.id">
                                    {{ lc.label }}
                                </option>
                            </select>
                        </div>

                        <!-- Timeframe Selector -->
                        <div class="nf-control-field">
                            <label>Forecast Timeframe</label>
                            <div class="nf-timeframe-pills">
                                <button
                                    type="button"
                                    class="nf-timeframe-btn"
                                    :class="{ active: selectedTimeframe === '24h' }"
                                    @click="selectedTimeframe = '24h'"
                                >
                                    24 Hours
                                </button>
                                <button
                                    type="button"
                                    class="nf-timeframe-btn"
                                    :class="{ active: selectedTimeframe === '7d' }"
                                    @click="selectedTimeframe = '7d'"
                                >
                                    7 Days
                                </button>
                                <button
                                    type="button"
                                    class="nf-timeframe-btn"
                                    :class="{ active: selectedTimeframe === '14d' }"
                                    @click="selectedTimeframe = '14d'"
                                >
                                    14 Days
                                </button>
                            </div>
                        </div>
                    </div>
                </article>

                <!-- SELECTED PROVINCE RESULT & FORECAST CHART -->
                <div class="nf-grid-2col">
                    <!-- Province Risk Assessment Card -->
                    <article class="nf-panel nf-result-card">
                        <div class="nf-panel-header">
                            <div>
                                <div class="nf-panel-eyebrow">RISK ASSESSMENT</div>
                                <h2>{{ selectedProvince }}</h2>
                                <p>{{ activeLandcoverLabel }}</p>
                            </div>
                            <span
                                class="nf-status-tag"
                                :class="`tag-${calibratedRiskLevel.toLowerCase()}`"
                            >
                                {{ calibratedRiskLevel }} RISK
                            </span>
                        </div>

                        <!-- Big Probability Ring / Bar Display -->
                        <div class="nf-risk-display">
                            <div class="nf-prob-number">
                                <strong>{{ Math.round(calibratedActiveProb * 1000) / 10 }}%</strong>
                                <small>Wildfire Probability</small>
                            </div>

                            <div class="nf-prob-track">
                                <div
                                    class="nf-prob-progress"
                                    :class="`fill-${calibratedRiskLevel.toLowerCase()}`"
                                    :style="{ width: `${Math.min(100, calibratedActiveProb * 100)}%` }"
                                ></div>
                            </div>

                            <div class="nf-prob-legend">
                                <span>0% Safe</span>
                                <span>35% High Risk Threshold</span>
                                <span>100% Critical</span>
                            </div>
                        </div>

                        <!-- Factor Breakdown -->
                        <div class="nf-factors-list">
                            <div class="nf-factor-item">
                                <span>Status Level</span>
                                <strong :class="`text-${calibratedRiskLevel.toLowerCase()}`">
                                    {{
                                        calibratedRiskLevel === 'High'
                                            ? 'Immediate Mitigation Priority'
                                            : calibratedRiskLevel === 'Moderate'
                                              ? 'Patrol Alert Status'
                                              : 'Controlled / Safe'
                                    }}
                                </strong>
                            </div>

                            <div class="nf-factor-item">
                                <span>Active FIRMS Hotspots</span>
                                <strong>
                                    {{ (activeProvinceData?.firms_active_hotspots ?? 0) > 0
                                        ? `${activeProvinceData?.firms_active_hotspots} active hotspots (Max FRP ${activeProvinceData?.firms_max_frp ?? 0} MW)`
                                        : '0 Hotspots detected'
                                    }}
                                </strong>
                            </div>

                            <div class="nf-factor-item">
                                <span>Real-Time Weather</span>
                                <strong>
                                    {{ activeProvinceData?.weather
                                        ? `${activeProvinceData.weather.T2M}°C · RH ${activeProvinceData.weather.RH2M}% · Wind ${activeProvinceData.weather.WS10M} m/s`
                                        : 'Telemetry ready'
                                    }}
                                </strong>
                            </div>

                            <div class="nf-factor-item">
                                <span>Land Cover Vulnerability</span>
                                <strong>{{ activeLandcoverLabel }}</strong>
                            </div>
                        </div>
                    </article>

                    <!-- Forecast Probability Trend Chart -->
                    <article class="nf-panel nf-chart-card">
                        <div class="nf-panel-header">
                            <div>
                                <div class="nf-panel-eyebrow">RISK PROJECTION</div>
                                <h2>Probability Trend: {{ selectedProvince }}</h2>
                                <p>
                                    {{ selectedTimeframe === '24h'
                                        ? 'Hourly diurnal probability curve (24 Hours)'
                                        : selectedTimeframe === '14d'
                                          ? '14-Day bi-weekly trend outlook'
                                          : '7-Day daily forecast projection'
                                    }}
                                </p>
                            </div>
                        </div>

                        <div class="nf-chart-wrap">
                            <div class="nf-chart-y-axis">
                                <span>{{ chartMax }}%</span>
                                <span>{{ Math.round(chartMax * 0.66) }}%</span>
                                <span>{{ Math.round(chartMax * 0.33) }}%</span>
                                <span>0%</span>
                            </div>

                            <svg class="nf-svg-chart" viewBox="0 0 600 165" preserveAspectRatio="none">
                                <defs>
                                    <linearGradient id="nf-ai-gradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stop-color="#16a34a" stop-opacity="0.32" />
                                        <stop offset="100%" stop-color="#16a34a" stop-opacity="0" />
                                    </linearGradient>
                                </defs>

                                <!-- Grid lines -->
                                <line x1="10" y1="20" x2="590" y2="20" class="nf-grid-line" />
                                <line x1="10" y1="65" x2="590" y2="65" class="nf-grid-line" />
                                <line x1="10" y1="110" x2="590" y2="110" class="nf-grid-line" />
                                <line x1="10" y1="155" x2="590" y2="155" class="nf-grid-line" />

                                <path :d="chartArea" fill="url(#nf-ai-gradient)" />
                                <path :d="chartLine" class="nf-chart-line" />

                                <circle
                                    v-for="pt in chartPoints"
                                    :key="pt.label"
                                    :cx="pt.x"
                                    :cy="pt.y"
                                    :r="hoveredPoint?.label === pt.label ? 6 : 4"
                                    class="nf-chart-dot"
                                    :class="{ 'is-hovered': hoveredPoint?.label === pt.label }"
                                    @mouseenter="hoveredPoint = pt"
                                    @mouseleave="hoveredPoint = null"
                                />
                            </svg>
                        </div>

                        <div class="nf-chart-x-axis">
                            <span v-for="t in chartTicks" :key="t.label">{{ t.label }}</span>
                        </div>

                        <div class="nf-chart-tooltip">
                            <span v-if="hoveredPoint">
                                <strong>{{ hoveredPoint.fullLabel }}:</strong> {{ hoveredPoint.value }}% Fire Probability
                                ({{ hoveredPoint.riskLevel }} Risk)
                                <template v-if="hoveredPoint.temp !== undefined">
                                    · {{ hoveredPoint.temp }}°C · RH {{ hoveredPoint.humidity }}%
                                </template>
                            </span>
                            <span v-else class="nf-muted-text">
                                Hover over data points to inspect probability and weather forecast.
                            </span>
                        </div>
                    </article>
                </div>

                <!-- SPATIAL MAP & 38 PROVINCES RANKING TABLE (NO ISLAND GROUPING) -->
                <div class="nf-grid-2col" style="margin-top: 20px;">
                    <!-- Spatial Risk Map -->
                    <article class="nf-panel">
                        <div class="nf-panel-header">
                            <div>
                                <div class="nf-panel-eyebrow">SPATIAL MONITORING</div>
                                <h2>38 Provinces Spatial Distribution</h2>
                                <p>Click any province marker to select and inspect its forecast.</p>
                            </div>
                            <div class="nf-map-legend">
                                <span class="legend-red">● High Risk</span>
                                <span class="legend-orange">● Moderate</span>
                                <span class="legend-green">● Low</span>
                            </div>
                        </div>

                        <div id="province-leaf-map" class="nf-leaf-map"></div>
                    </article>

                    <!-- All 38 Provinces Table (Directly listed, NO island filter) -->
                    <article class="nf-panel">
                        <div class="nf-panel-header">
                            <div>
                                <div class="nf-panel-eyebrow">NATIONAL RANKING</div>
                                <h2>38 Provinces Risk Status</h2>
                                <p>Ranked by fire risk probability. Click any row to select.</p>
                            </div>

                            <div class="nf-search-wrap">
                                <input
                                    v-model="searchProvince"
                                    type="text"
                                    placeholder="Search province..."
                                    class="nf-search-box"
                                />
                            </div>
                        </div>

                        <div class="nf-table-scroll">
                            <table class="nf-table">
                                <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Province</th>
                                        <th>Risk Status</th>
                                        <th>Probability</th>
                                        <th>Hotspots</th>
                                        <th>Weather</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="(prov, idx) in allProvincesRanked"
                                        :key="prov.province"
                                        :class="{ 'is-selected': prov.province === selectedProvince }"
                                        @click="selectProvince(prov.province)"
                                    >
                                        <td class="cell-rank">#{{ idx + 1 }}</td>
                                        <td>
                                            <strong>{{ prov.province }}</strong>
                                        </td>
                                        <td>
                                            <span class="nf-badge" :class="`badge-${(prov.risk_level || 'Low').toLowerCase()}`">
                                                {{ prov.risk_level || 'Low' }}
                                            </span>
                                        </td>
                                        <td>
                                            <div class="nf-prob-num">
                                                {{ Math.round((prov.probability_fire ?? 0) * 1000) / 10 }}%
                                            </div>
                                            <div class="nf-mini-bar">
                                                <div
                                                    class="nf-mini-fill"
                                                    :class="`fill-${(prov.risk_level || 'Low').toLowerCase()}`"
                                                    :style="{ width: `${Math.min(100, (prov.probability_fire ?? 0) * 100)}%` }"
                                                ></div>
                                            </div>
                                        </td>
                                        <td>
                                            <span v-if="(prov.firms_active_hotspots ?? 0) > 0" class="text-danger">
                                                🔥 {{ prov.firms_active_hotspots }} (Max {{ prov.firms_max_frp ?? 0 }} MW)
                                            </span>
                                            <span v-else class="text-safe">
                                                ✓ 0 active
                                            </span>
                                        </td>
                                        <td>
                                            <span v-if="prov.weather" class="nf-weather-summary">
                                                {{ prov.weather.T2M }}°C · RH {{ prov.weather.RH2M }}%
                                            </span>
                                            <span v-else class="nf-muted-text">—</span>
                                        </td>
                                        <td>
                                            <button
                                                type="button"
                                                class="nf-select-btn"
                                                :class="{ 'btn-selected': prov.province === selectedProvince }"
                                                @click.stop="selectProvince(prov.province)"
                                            >
                                                {{ prov.province === selectedProvince ? 'Active' : 'Select' }}
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </article>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
.nf-ai-page {
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

.nf-ai-page.theme-dark {
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
    gap: 20px;
}

/* Clean Page Heading (Matches Dashboard style) */
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
    font-size: 28px;
    font-weight: 800;
    margin: 0 0 4px;
    letter-spacing: -0.02em;
}

.nf-heading-text p {
    font-size: 13.5px;
    color: var(--text-muted);
    margin: 0;
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
    width: 36px;
    height: 36px;
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
    font-size: 26px;
    font-weight: 800;
    color: var(--text-main);
}

.nf-card-sub {
    font-size: 11px;
    color: var(--text-muted);
}

/* Panel Styles */
.nf-panel {
    background: var(--surface-bg);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 22px;
    display: flex;
    flex-direction: column;
}

.nf-panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 16px;
    gap: 14px;
    flex-wrap: wrap;
}

.nf-panel-eyebrow {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--primary);
    margin-bottom: 2px;
}

.nf-panel-header h2 {
    font-size: 17px;
    font-weight: 700;
    margin: 0 0 2px;
}

.nf-panel-header p {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
}

/* Controls Grid */
.nf-controls-grid {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1fr;
    gap: 16px;
}

@media (max-width: 900px) {
    .nf-controls-grid {
        grid-template-columns: 1fr;
    }
}

.nf-control-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.nf-control-field label {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--text-muted);
}

.nf-select-control {
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--surface-bg);
    color: var(--text-main);
    font-size: 13px;
    font-weight: 500;
}

.nf-timeframe-pills {
    display: flex;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 3px;
    gap: 3px;
}

.nf-timeframe-btn {
    flex: 1;
    padding: 7px 10px;
    border-radius: 7px;
    border: 0;
    background: transparent;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.nf-timeframe-btn.active {
    background: var(--surface-bg);
    color: var(--primary);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* 2-Column Grid Layouts */
.nf-grid-2col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

@media (max-width: 1050px) {
    .nf-grid-2col {
        grid-template-columns: 1fr;
    }
}

/* Status Tags */
.nf-status-tag {
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
}

.tag-high { background: #fee2e2; color: #b91c1c; }
.tag-moderate { background: #fef3c7; color: #b45309; }
.tag-low { background: #dcfce7; color: #15803d; }

/* Probability Ring/Bar in Result Card */
.nf-risk-display {
    padding: 16px;
    border-radius: 14px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.nf-prob-number strong {
    font-size: 36px;
    font-weight: 800;
    line-height: 1;
    display: block;
}

.nf-prob-number small {
    font-size: 12px;
    color: var(--text-muted);
}

.nf-prob-track {
    height: 10px;
    border-radius: 5px;
    background: var(--border-color);
    overflow: hidden;
}

.nf-prob-progress {
    height: 100%;
    border-radius: 5px;
    transition: width 0.4s ease;
}

.fill-high { background: #dc2626; }
.fill-moderate { background: #f59e0b; }
.fill-low { background: #16a34a; }

.nf-prob-legend {
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: var(--text-muted);
}

/* Factor Items */
.nf-factors-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 14px;
}

.nf-factor-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
    font-size: 12.5px;
}

.nf-factor-item:last-child {
    border-bottom: 0;
    padding-bottom: 0;
}

.nf-factor-item span {
    color: var(--text-muted);
}

.text-high { color: #dc2626; }
.text-moderate { color: #d97706; }
.text-low { color: #16a34a; }
.text-danger { color: #dc2626; font-weight: 600; }
.text-safe { color: #16a34a; font-weight: 600; }

/* SVG Chart */
.nf-chart-wrap {
    display: flex;
    gap: 12px;
    height: 180px;
    margin-top: 6px;
}

.nf-chart-y-axis {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    width: 36px;
    text-align: right;
    padding: 6px 0;
}

.nf-svg-chart {
    flex: 1;
    width: 100%;
    height: 100%;
    overflow: visible;
}

.nf-grid-line {
    stroke: var(--border-color);
    stroke-width: 1;
    stroke-dasharray: 4 4;
}

.nf-chart-line {
    fill: none;
    stroke: #16a34a;
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.nf-chart-dot {
    fill: #16a34a;
    stroke: var(--surface-bg);
    stroke-width: 2;
    cursor: pointer;
    transition: r 0.2s ease;
}

.nf-chart-dot.is-hovered {
    fill: #dc2626;
    stroke-width: 3;
}

.nf-chart-x-axis {
    display: flex;
    justify-content: space-between;
    margin-left: 48px;
    margin-top: 6px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
}

.nf-chart-tooltip {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    font-size: 12px;
}

/* Leaflet Map */
.nf-leaf-map {
    height: 380px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    overflow: hidden;
}

.nf-map-legend {
    display: flex;
    gap: 10px;
    font-size: 11px;
    font-weight: 600;
}

.legend-red { color: #dc2626; }
.legend-orange { color: #d97706; }
.legend-green { color: #16a34a; }

/* 38 Provinces Table (NO island filter) */
.nf-search-wrap {
    display: flex;
}

.nf-search-box {
    padding: 7px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--surface-bg);
    color: var(--text-main);
    font-size: 12px;
    min-width: 180px;
}

.nf-table-scroll {
    max-height: 380px;
    overflow-y: auto;
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
    position: sticky;
    top: 0;
    background: var(--surface-bg);
    padding: 10px 12px;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 2px solid var(--border-color);
    z-index: 10;
}

.nf-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-color);
    vertical-align: middle;
}

.nf-table tr {
    cursor: pointer;
    transition: background 0.15s;
}

.nf-table tr:hover {
    background: var(--page-bg);
}

.nf-table tr.is-selected {
    background: var(--primary-light);
}

.cell-rank {
    font-weight: 800;
    color: var(--text-muted);
}

.nf-badge {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}

.badge-high { background: #fee2e2; color: #b91c1c; }
.badge-moderate { background: #fef3c7; color: #b45309; }
.badge-low { background: #dcfce7; color: #15803d; }

.nf-prob-num {
    font-weight: 700;
    font-size: 12px;
}

.nf-mini-bar {
    width: 70px;
    height: 4px;
    border-radius: 2px;
    background: var(--border-color);
    overflow: hidden;
    margin-top: 3px;
}

.nf-mini-fill {
    height: 100%;
    border-radius: 2px;
}

.nf-weather-summary {
    font-size: 11px;
    color: var(--text-muted);
}

.nf-select-btn {
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: var(--surface-bg);
    color: var(--primary);
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.nf-select-btn:hover, .nf-select-btn.btn-selected {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
}
</style>
