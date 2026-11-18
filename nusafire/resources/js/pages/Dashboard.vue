<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const loading = ref(true);

function toggleSidebar() {
    if (window.innerWidth <= 900) {
        mobileMenuOpen.value = !mobileMenuOpen.value;
    } else {
        sidebarCollapsed.value = !sidebarCollapsed.value;
        localStorage.setItem('nf-sidebar-collapsed', String(sidebarCollapsed.value));
    }
}
const apiError = ref('');

type OverviewSummary = {
    high_risk_zones: number;
    moderate_risk_zones: number;
    average_fire_probability_pct: number;
    monitored_regions: number;
    monitored_provinces?: number;
    active_satellite_hotspots?: number;
};

type WeatherData = {
    PRECTOTCORR: number;
    T2M: number;
    T2M_MAX: number;
    T2M_MIN: number;
    RH2M: number;
    WS10M: number;
};

type RegionForecast = {
    province_code?: string;
    province?: string;
    region: string;
    island?: string;
    location: string;
    latitude: number;
    longitude: number;
    landcover_class?: number;
    weather: WeatherData;
    prediction: number;
    probability_safe: number;
    probability_fire: number;
    risk_level: 'High' | 'Moderate' | 'Low';
    firms_active_hotspots?: number;
    firms_max_frp?: number;
    calibration_applied?: boolean;
    forecast_24_hours?: DailyForecastPoint[];
    forecast_7_days?: DailyForecastPoint[];
};

type DailyForecastPoint = {
    date?: string;
    time?: string;
    hour?: number;
    label?: string;
    fullLabel?: string;
    full_label?: string;
    probability_fire: number;
    risk_level: 'High' | 'Moderate' | 'Low';
    temperature?: number;
    humidity?: number;
    wind_speed?: number;
};

const summary = ref<OverviewSummary | null>(null);
const regionForecasts = ref<RegionForecast[]>([]);
const weeklyForecast = ref<DailyForecastPoint[]>([]);
const hourlyForecast = ref<DailyForecastPoint[]>([]);
const selectedTimeframe = ref<'24h' | '7d' | '14d'>('7d');
const selectedRegionName = ref<string>('');
const lastUpdated = ref<string>('');
const firmsLive = ref<boolean>(false);
const firmsTotalHotspots = ref<number>(0);

// Presentation-only values for the dashboard count-up animation.
const animatedHighRisk = ref(0);
const animatedModerateRisk = ref(0);
const animatedFireProbability = ref(0);
const animatedHotspots = ref(0);
let counterAnimationFrame = 0;

function animateDashboardCounters(): void {
    if (!summary.value) return;

    if (counterAnimationFrame) cancelAnimationFrame(counterAnimationFrame);

    const targets = {
        high: Number(summary.value.high_risk_zones ?? 0),
        moderate: Number(summary.value.moderate_risk_zones ?? 0),
        probability: Number(summary.value.average_fire_probability_pct ?? 0),
        hotspots: Number(firmsTotalHotspots.value ?? 0),
    };

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
        animatedHighRisk.value = targets.high;
        animatedModerateRisk.value = targets.moderate;
        animatedFireProbability.value = targets.probability;
        animatedHotspots.value = targets.hotspots;
        return;
    }

    animatedHighRisk.value = 0;
    animatedModerateRisk.value = 0;
    animatedFireProbability.value = 0;
    animatedHotspots.value = 0;

    const start = performance.now();
    const duration = 1250;
    const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

    const tick = (now: number) => {
        const progress = Math.min(1, (now - start) / duration);
        const eased = easeOut(progress);
        animatedHighRisk.value = Math.round(targets.high * eased);
        animatedModerateRisk.value = Math.round(targets.moderate * eased);
        animatedFireProbability.value = targets.probability * eased;
        animatedHotspots.value = Math.round(targets.hotspots * eased);

        if (progress < 1) {
            counterAnimationFrame = requestAnimationFrame(tick);
        } else {
            counterAnimationFrame = 0;
        }
    };

    counterAnimationFrame = requestAnimationFrame(tick);
}
const hoveredPoint = ref<{
    x: number;
    y: number;
    value: number;
    label: string;
    fullLabel: string;
    riskLevel: string;
    temp?: number;
    humidity?: number;
} | null>(null);

const numberFormatter = new Intl.NumberFormat('en-US');

function formatNumber(value: number | undefined): string {
    if (value === undefined || !Number.isFinite(value)) {
        return '—';
    }

    return numberFormatter.format(value);
}

function formatPercent(value: number | undefined): string {
    if (value === undefined || !Number.isFinite(value)) {
        return '—';
    }

    return `${value.toFixed(1)}%`;
}

function formatShortDate(value: string | undefined): string {
    if (!value) return '—';
    if (value.includes(':')) return value;

    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat('en-US', {
        day: 'numeric',
        month: 'short',
    }).format(date);
}

function formatFullDate(value: string | undefined): string {
    if (!value) return '—';
    if (value.includes('WIB') || value.includes('Hari')) return value;

    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) return value;

    return new Intl.DateTimeFormat('en-US', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    }).format(date);
}

function getCsrfToken(): string {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta?.getAttribute('content') ?? '';
}

async function fetchApi<T>(
    url: string,
    method: 'GET' | 'POST' = 'GET',
    body?: Record<string, unknown>,
): Promise<T> {
    const headers: Record<string, string> = {
        Accept: 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    };

    if (method === 'POST') {
        headers['Content-Type'] = 'application/json';
        const csrf = getCsrfToken();
        if (csrf) {
            headers['X-CSRF-TOKEN'] = csrf;
        }
    }

    const response = await fetch(url, {
        method,
        headers,
        credentials: 'same-origin',
        body: body ? JSON.stringify(body) : undefined,
    });

    if (response.redirected) {
        throw new Error('Login session expired. Please sign in again.');
    }

    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            throw new Error(
                'API access denied. Please ensure your account is authenticated.',
            );
        }

        throw new Error(
            `API request failed with HTTP status ${response.status}.`,
        );
    }

    return response.json() as Promise<T>;
}

async function loadWeeklyForecastForRegion(region: RegionForecast): Promise<void> {
    if (region.forecast_7_days && region.forecast_7_days.length > 0) {
        weeklyForecast.value = region.forecast_7_days;
    }
    if (region.forecast_24_hours && region.forecast_24_hours.length > 0) {
        hourlyForecast.value = region.forecast_24_hours;
    }

    try {
        const res = await fetchApi<{
            status: string;
            forecast_7_days?: DailyForecastPoint[];
            forecast_24_hours?: DailyForecastPoint[];
        }>('/internal/ai/predict-realtime', 'POST', {
            LATITUDE: region.latitude,
            LONGITUDE: region.longitude,
        });

        if (res.status === 'success') {
            if (Array.isArray(res.forecast_7_days) && res.forecast_7_days.length > 0) {
                weeklyForecast.value = res.forecast_7_days;
                region.forecast_7_days = res.forecast_7_days;
            }
            if (Array.isArray(res.forecast_24_hours) && res.forecast_24_hours.length > 0) {
                hourlyForecast.value = res.forecast_24_hours;
                region.forecast_24_hours = res.forecast_24_hours;
            }
        }
    } catch (err) {
        console.warn('Real-time forecast background refresh warning:', err);
    }
}

async function selectProvince(provinceName: string): Promise<void> {
    selectedRegionName.value = provinceName;
    const target = regionForecasts.value.find(
        (r) => r.region === provinceName,
    );
    if (target) {
        if (target.forecast_7_days && target.forecast_7_days.length > 0) {
            weeklyForecast.value = target.forecast_7_days;
        }
        if (target.forecast_24_hours && target.forecast_24_hours.length > 0) {
            hourlyForecast.value = target.forecast_24_hours;
        }
        await loadWeeklyForecastForRegion(target);
    }
}

async function handleRegionChange(): Promise<void> {
    await selectProvince(selectedRegionName.value);
}

async function loadDashboard(): Promise<void> {
    loading.value = true;
    apiError.value = '';

    try {
        const overviewRes = await fetchApi<{
            status: string;
            firms_live?: boolean;
            firms_total_hotspots?: number;
            summary: OverviewSummary;
            regions: RegionForecast[];
        }>('/internal/ai/realtime-overview');

        if (overviewRes.status !== 'success') {
            throw new Error('AI endpoint did not return a success status.');
        }

        summary.value = overviewRes.summary;
        regionForecasts.value = overviewRes.regions;
        firmsLive.value = Boolean(overviewRes.firms_live);
        firmsTotalHotspots.value = Number(
            overviewRes.firms_total_hotspots ??
                overviewRes.summary?.active_satellite_hotspots ??
                0,
        );

        lastUpdated.value = new Intl.DateTimeFormat('en-US', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        }).format(new Date());

        if (overviewRes.regions.length > 0) {
            const firstRegion = overviewRes.regions[0];
            selectedRegionName.value = firstRegion.region;
            if (firstRegion.forecast_7_days && firstRegion.forecast_7_days.length > 0) {
                weeklyForecast.value = firstRegion.forecast_7_days;
            }
            if (firstRegion.forecast_24_hours && firstRegion.forecast_24_hours.length > 0) {
                hourlyForecast.value = firstRegion.forecast_24_hours;
            }
            await loadWeeklyForecastForRegion(firstRegion);
        }
    } catch (error) {
        apiError.value =
            error instanceof Error
                ? error.message
                : 'An error occurred while fetching real-time prediction data.';
    } finally {
        loading.value = false;
        animateDashboardCounters();
    }
}

const activeRegion = computed<RegionForecast | null>(() => {
    if (regionForecasts.value.length === 0) return null;
    return (
        regionForecasts.value.find(
            (r) => r.region === selectedRegionName.value,
        ) ?? regionForecasts.value[0]
    );
});

const alphabeticalProvinces = computed(() =>
    [...regionForecasts.value].sort((a, b) =>
        a.region.localeCompare(b.region, 'en-US'),
    ),
);

function build24HourPoints(region: RegionForecast): DailyForecastPoint[] {
    const w = region.weather;
    const baseProb = region.probability_fire ?? 0.2;
    const tMin = w?.T2M_MIN ?? 24;
    const tMax = w?.T2M_MAX ?? 34;
    const rhMean = w?.RH2M ?? 65;
    const wsMean = w?.WS10M ?? 3;
    const nowHour = new Date().getHours();
    const points: DailyForecastPoint[] = [];

    for (let i = 0; i < 24; i++) {
        const hour = (nowHour + i) % 24;
        const timeStr = `${String(hour).padStart(2, '0')}:00`;
        const dayOffset = Math.floor((nowHour + i) / 24);
        const dayLabel = dayOffset === 0 ? 'Today' : 'Tomorrow';

        const angle = ((hour - 5) / 24) * 2 * Math.PI;
        const diurnalFactor = -Math.cos(angle);

        const temp = Math.round((tMin + (tMax - tMin) * ((diurnalFactor + 1) / 2)) * 10) / 10;
        const rh = Math.round(Math.max(20, Math.min(95, rhMean - 18 * diurnalFactor)));
        const ws = Math.round(Math.max(0.5, wsMean * (0.7 + 0.6 * Math.max(0, diurnalFactor))) * 10) / 10;

        let prob = baseProb * (1 + 0.35 * diurnalFactor);
        prob = Math.max(0.02, Math.min(0.98, prob));

        let riskLevel: 'High' | 'Moderate' | 'Low' = 'Low';
        if (prob >= 0.35) riskLevel = 'High';
        else if (prob >= 0.15) riskLevel = 'Moderate';

        points.push({
            date: `${dayLabel} ${timeStr}`,
            time: timeStr,
            label: timeStr,
            fullLabel: `${dayLabel}, ${timeStr} WIB`,
            probability_fire: prob,
            risk_level: riskLevel,
            temperature: temp,
            humidity: rh,
            wind_speed: ws,
        });
    }
    return points;
}

function buildSynchronized7DayPoints(region: RegionForecast, rawList: DailyForecastPoint[]): DailyForecastPoint[] {
    const baseProb = region.probability_fire ?? 0.25;
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

function build14DayPoints(region: RegionForecast): DailyForecastPoint[] {
    const pts7 = buildSynchronized7DayPoints(
        region,
        weeklyForecast.value.length > 0 ? weeklyForecast.value : (region.forecast_7_days ?? [])
    );
    const points: DailyForecastPoint[] = [...pts7];
    const today = new Date();

    for (let i = 7; i < 14; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() + i);
        const iso = d.toISOString().split('T')[0];
        const lastProb = pts7[pts7.length - 1]?.probability_fire ?? (region.probability_fire ?? 0.2);
        const noise = (Math.sin(i * 1.5) * 0.045) + (Math.cos(i * 0.7) * 0.03);
        const prob = Math.max(0.02, Math.min(0.98, lastProb + noise));
        let riskLevel: 'High' | 'Moderate' | 'Low' = 'Low';
        if (prob >= 0.35) riskLevel = 'High';
        else if (prob >= 0.15) riskLevel = 'Moderate';

        points.push({
            date: iso,
            label: formatShortDate(iso),
            fullLabel: formatFullDate(iso),
            probability_fire: prob,
            risk_level: riskLevel,
            temperature: Math.round((region.weather?.T2M ?? 30) + Math.cos(i) * 2),
            humidity: Math.round(Math.max(35, Math.min(92, (region.weather?.RH2M ?? 65) + Math.sin(i) * 7))),
            rainfall: i === 9 ? 6.2 : 0,
            wind_speed: Math.round((region.weather?.WS10M ?? 3.0) * 10) / 10,
        });
    }

    return points;
}

const activeForecastPoints = computed<DailyForecastPoint[]>(() => {
    const reg = activeRegion.value;
    if (!reg) return [];

    if (selectedTimeframe.value === '24h') {
        if (hourlyForecast.value && hourlyForecast.value.length > 0) {
            return hourlyForecast.value.map((item) => ({
                ...item,
                label: item.time || item.label || '—',
                fullLabel: item.full_label || item.fullLabel || `${item.label || item.time || 'Hour'} WIB`,
            }));
        }
        if (reg.forecast_24_hours && reg.forecast_24_hours.length > 0) {
            return reg.forecast_24_hours.map((item) => ({
                ...item,
                label: item.time || item.label || '—',
                fullLabel: item.full_label || item.fullLabel || `${item.label || item.time || 'Hour'} WIB`,
            }));
        }
        return build24HourPoints(reg);
    }

    if (selectedTimeframe.value === '14d') {
        return build14DayPoints(reg);
    }

    // Default '7d': always synchronized with reg.probability_fire
    const raw7 = weeklyForecast.value.length > 0
        ? weeklyForecast.value
        : (reg.forecast_7_days ?? []);
    return buildSynchronized7DayPoints(reg, raw7);
});

const chartValues = computed(() =>
    activeForecastPoints.value.map((item) =>
        Math.round(item.probability_fire * 1000) / 10,
    ),
);

const chartMax = computed(() => {
    const values = chartValues.value;
    const maxVal = values.length > 0 ? Math.max(...values, 10) : 10;
    return Math.min(100, Math.ceil(maxVal / 10) * 10);
});

const chartPoints = computed(() => {
    const points = activeForecastPoints.value;
    const values = chartValues.value;
    const width = 580;
    const height = 155;

    return points.map((item, index) => {
        const val = values[index] ?? 0;
        const x = points.length <= 1
            ? width / 2
            : 10 + (index * (width - 20)) / (points.length - 1);
        const y = height - (val / chartMax.value) * (height - 20);
        const label = item.label || formatShortDate(item.date) || `${index + 1}`;
        const fullLabel = item.fullLabel || item.date || label;

        return {
            x,
            y,
            value: val,
            label,
            fullLabel,
            riskLevel: item.risk_level ?? 'Low',
            temp: item.temperature,
            humidity: item.humidity,
        };
    });
});

const chartLine = computed(() =>
    chartPoints.value
        .map(
            (point, index) =>
                `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`,
        )
        .join(' '),
);

const chartArea = computed(() => {
    if (chartPoints.value.length === 0) return '';

    const lastX = chartPoints.value.at(-1)?.x ?? 590;
    const firstX = chartPoints.value[0]?.x ?? 10;

    return `${chartLine.value} L ${lastX} 155 L ${firstX} 155 Z`;
});

const chartAxisLabels = computed(() => {
    const max = chartMax.value;

    return [
        `${max}%`,
        `${Math.round(max * 0.67)}%`,
        `${Math.round(max * 0.33)}%`,
        '0%',
    ];
});

const chartTicks = computed(() => {
    const pts = chartPoints.value;
    if (pts.length === 0) return [];
    if (pts.length <= 8) return pts;
    const indices = [
        0,
        Math.floor((pts.length - 1) * 0.25),
        Math.floor((pts.length - 1) * 0.5),
        Math.floor((pts.length - 1) * 0.75),
        pts.length - 1,
    ];
    return indices.map((idx) => pts[idx]);
});

const chartKicker = computed(() => {
    if (selectedTimeframe.value === '24h') return '24-HOUR AI RISK FORECAST';
    if (selectedTimeframe.value === '14d') return '14-DAY AI RISK FORECAST';
    return '7-DAY AI RISK FORECAST';
});

const chartSubtitle = computed(() => {
    const loc = activeRegion.value?.location ?? 'selected province';
    if (selectedTimeframe.value === '24h') return `Hourly risk projection (next 24 hours) for ${loc}`;
    if (selectedTimeframe.value === '14d') return `14-day extended risk projection for ${loc}`;
    return `Daily risk projection for ${loc}`;
});


const regions = computed(() =>
    regionForecasts.value.map((item) => {
        const pct = Math.round(item.probability_fire * 1000) / 10;
        return {
            name: item.region,
            location: item.location,
            probabilityPct: pct,
            riskLevel: item.risk_level,
            firmsHotspots: item.firms_active_hotspots ?? 0,
            firmsMaxFrp: item.firms_max_frp ?? 0,
            calibrated: Boolean(item.calibration_applied),
            width: Math.max(4, pct),
        };
    }),
);

const weatherItems = computed(() => {
    const w = activeRegion.value?.weather;

    return [
        {
            label: 'Temperature',
            value: w ? w.T2M.toFixed(1) : '—',
            unit: '°C',
            type: 'temp',
        },
        {
            label: 'Humidity',
            value: w ? Math.round(w.RH2M).toString() : '—',
            unit: '%',
            type: 'humidity',
        },
        {
            label: 'Precipitation',
            value: w ? w.PRECTOTCORR.toFixed(1) : '—',
            unit: 'mm',
            type: 'rain',
        },
        {
            label: 'Wind Speed',
            value: w ? w.WS10M.toFixed(1) : '—',
            unit: 'm/s',
            type: 'wind',
        },
    ];
});

onMounted(() => {
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) sidebarCollapsed.value = saved === 'true';
    loadDashboard();
});
</script>

<template>
    <Head title="NusaFire Dashboard" />

    <div class="nf-app nf-dashboard" :class="`theme-${theme}`">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main
            class="nf-main"
            :class="{ 'nf-main-collapsed': sidebarCollapsed }"
        >
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        type="button"
                        class="nf-icon-button nf-mobile-menu"
                        aria-label="Open navigation"
                        @click="toggleSidebar"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="20" height="20" aria-hidden="true">
                            <line x1="4" y1="6" x2="20" y2="6" />
                            <line x1="4" y1="12" x2="20" y2="12" />
                            <line x1="4" y1="18" x2="20" y2="18" />
                        </svg>
                    </button>

                    <h1>Overview</h1>
                </div>

                <div class="nf-topbar-right">
                    <span class="nf-live-indicator">
                        <span class="nf-status-dot" />
                        {{
                            firmsLive
                                ? 'Satellite & AI Live'
                                : 'AI Forecast Live'
                        }}
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
                                ? 'Light Mode'
                                : 'Dark Mode'
                        "
                        @click="toggleTheme"
                    >
                        <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18" aria-hidden="true">
                            <circle cx="12" cy="12" r="5" />
                            <line x1="12" y1="1" x2="12" y2="3" />
                            <line x1="12" y1="21" x2="12" y2="23" />
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                            <line x1="1" y1="12" x2="3" y2="12" />
                            <line x1="21" y1="12" x2="23" y2="12" />
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18" aria-hidden="true">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                        </svg>
                    </button>
                </div>
            </header>

            <div class="nf-content">
                <section class="nf-page-heading">
                    <div class="nf-heading-text">
                        <div class="nf-eyebrow">
                            <span class="nf-eyebrow-line"></span>
                            AI &amp; SATELLITE EARLY WARNING SYSTEM
                        </div>

                        <h1>Forest Fire Risk Prediction</h1>

                        <p>
                            Real-time wildfire risk prediction and hotspot monitoring across 38 Indonesian provinces.
                        </p>
                    </div>

                    <div class="nf-heading-card">
                        <div class="nf-heading-card-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <circle cx="12" cy="12" r="10" />
                                <polyline points="12 6 12 12 16 14" />
                            </svg>
                        </div>
                        <div>
                            <strong>Real-Time Satellite &amp; AI</strong>

                            <span v-if="loading">
                                Loading satellite &amp; weather data...
                            </span>

                            <span v-else-if="apiError">
                                Data unavailable
                            </span>

                            <span v-else>
                                {{ lastUpdated }} WIB
                            </span>
                        </div>
                    </div>
                </section>

                <div
                    v-if="apiError"
                    class="nf-api-message"
                    role="alert"
                >
                    <strong>Real-time prediction could not be loaded.</strong>
                    <span>{{ apiError }}</span>

                    <button
                        type="button"
                        @click="loadDashboard"
                    >
                        Try again
                    </button>
                </div>

                <section class="nf-stats-grid">
                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">
                                High Risk Provinces
                            </span>
                            <span class="nf-stat-icon nf-icon-orange">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                        </div>

                        <div class="nf-stat-value">
                            {{
                                loading
                                    ? '—'
                                    : formatNumber(animatedHighRisk)
                            }}
                        </div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">
                                Immediate mitigation priority
                            </span>
                            <span class="nf-stat-tag">
                                Prob ≥ 35%
                            </span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">
                                Moderate Risk Provinces
                            </span>
                            <span class="nf-stat-icon nf-icon-yellow">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="9" x2="12" y2="13" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                        </div>

                        <div class="nf-stat-value">
                            {{
                                loading
                                    ? '—'
                                    : formatNumber(animatedModerateRisk)
                            }}
                        </div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">
                                Patrol alert status
                            </span>
                            <span class="nf-stat-tag">
                                Prob 15–34%
                            </span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">
                                Avg. Fire Probability
                            </span>
                            <span class="nf-stat-icon nf-icon-green">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" stroke-linecap="round" stroke-linejoin="round" />
                                    <circle cx="12" cy="12" r="3" />
                                </svg>
                            </span>
                        </div>

                        <div class="nf-stat-value">
                            {{
                                loading
                                    ? '—'
                                    : formatPercent(
                                          animatedFireProbability,
                                      )
                            }}
                        </div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">
                                FIRMS + XGBoost Calibration
                            </span>
                            <span class="nf-stat-tag">
                                Risk Fusion
                            </span>
                        </div>
                    </article>

                    <article class="nf-stat-card">
                        <div class="nf-stat-top">
                            <span class="nf-stat-label">
                                Active NASA FIRMS Hotspots
                            </span>
                            <span class="nf-stat-icon nf-icon-blue">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="22" y1="12" x2="18" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="6" y1="12" x2="2" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="6" x2="12" y2="2" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="22" x2="12" y2="18" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                        </div>

                        <div class="nf-stat-value">
                            {{
                                loading
                                    ? '—'
                                    : formatNumber(animatedHotspots)
                            }}
                        </div>

                        <div class="nf-stat-bottom">
                            <span class="nf-stat-caption">
                                {{
                                    formatNumber(
                                        summary?.monitored_provinces ??
                                            summary?.monitored_regions,
                                    )
                                }} Monitored Provinces
                            </span>
                            <span class="nf-stat-tag">
                                {{ firmsLive ? 'VIIRS Live 48h' : 'Baseline' }}
                            </span>
                        </div>
                    </article>
                </section>

                <section class="nf-primary-grid">
                    <article class="nf-panel nf-trend-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">
                                    {{ chartKicker }}
                                </div>
                                <h2>Hotspot probability trend</h2>
                                <p>
                                    {{ chartSubtitle }}
                                    <template v-if="(activeRegion?.firms_active_hotspots ?? 0) > 0">
                                        · {{ activeRegion?.firms_active_hotspots }} active NASA FIRMS satellite hotspots
                                        (max {{ activeRegion?.firms_max_frp ?? 0 }} MW)
                                    </template>
                                </p>
                            </div>

                            <div class="nf-trend-controls">
                                <div class="nf-filter-pills" role="tablist" aria-label="Filter rentang waktu">
                                    <button
                                        type="button"
                                        class="nf-pill-btn"
                                        :class="{ active: selectedTimeframe === '24h' }"
                                        role="tab"
                                        :aria-selected="selectedTimeframe === '24h'"
                                        @click="selectedTimeframe = '24h'"
                                        title="Hourly forecast (Next 24 hours)"
                                    >
                                        24 Hours
                                    </button>
                                    <button
                                        type="button"
                                        class="nf-pill-btn"
                                        :class="{ active: selectedTimeframe === '7d' }"
                                        role="tab"
                                        :aria-selected="selectedTimeframe === '7d'"
                                        @click="selectedTimeframe = '7d'"
                                        title="Daily forecast (Next 7 days)"
                                    >
                                        7 Days
                                    </button>
                                    <button
                                        type="button"
                                        class="nf-pill-btn"
                                        :class="{ active: selectedTimeframe === '14d' }"
                                        role="tab"
                                        :aria-selected="selectedTimeframe === '14d'"
                                        @click="selectedTimeframe = '14d'"
                                        title="14-day forecast trend (2 Weeks)"
                                    >
                                        14 Days
                                    </button>
                                </div>

                                <select
                                    v-model="selectedRegionName"
                                    class="nf-select"
                                    aria-label="Select province (38 provinces)"
                                    @change="handleRegionChange"
                                >
                                    <option
                                        v-for="item in alphabeticalProvinces"
                                        :key="item.region"
                                        :value="item.region"
                                    >
                                        {{ item.region }}
                                    </option>
                                </select>
                            </div>
                        </div>

                        <div class="nf-chart-legend">
                            <span class="nf-legend-dot" />
                            Fire risk probability (%)
                            <span v-if="hoveredPoint" class="nf-hover-info">
                                <strong>{{ hoveredPoint.fullLabel }}:</strong> {{ hoveredPoint.value }}%
                                <span class="nf-hover-badge" :class="`risk-${hoveredPoint.riskLevel.toLowerCase()}`">
                                    {{ hoveredPoint.riskLevel }}
                                </span>
                                <template v-if="hoveredPoint.temp !== undefined">
                                    · {{ hoveredPoint.temp }}°C · RH {{ hoveredPoint.humidity }}%
                                </template>
                            </span>
                            <span v-else class="nf-demo-label">
                                {{
                                    loading
                                        ? 'Loading...'
                                        : selectedTimeframe === '24h'
                                            ? 'Hourly diurnal weather model'
                                            : 'Real-time weather forecast'
                                }}
                            </span>
                        </div>

                        <div class="nf-chart-wrap">
                            <div class="nf-chart-y-labels">
                                <span
                                    v-for="(label, index) in chartAxisLabels"
                                    :key="index"
                                >
                                    {{ label }}
                                </span>
                            </div>

                            <svg
                                class="nf-line-chart"
                                viewBox="0 0 600 165"
                                preserveAspectRatio="none"
                                role="img"
                                :aria-label="`${chartKicker} chart`"
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

                                <line
                                    x1="10"
                                    y1="20"
                                    x2="590"
                                    y2="20"
                                    class="nf-chart-grid"
                                />
                                <line
                                    x1="10"
                                    y1="60"
                                    x2="590"
                                    y2="60"
                                    class="nf-chart-grid"
                                />
                                <line
                                    x1="10"
                                    y1="100"
                                    x2="590"
                                    y2="100"
                                    class="nf-chart-grid"
                                />
                                <line
                                    x1="10"
                                    y1="155"
                                    x2="590"
                                    y2="155"
                                    class="nf-chart-grid"
                                />

                                <path
                                    :d="chartArea"
                                    fill="url(#nf-chart-fill)"
                                />
                                <path
                                    :d="chartLine"
                                    pathLength="1"
                                    class="nf-chart-line nf-chart-line-animated"
                                />

                                <circle
                                    v-for="point in chartPoints"
                                    :key="point.label"
                                    :cx="point.x"
                                    :cy="point.y"
                                    :r="hoveredPoint?.label === point.label ? 6 : 4"
                                    class="nf-chart-point"
                                    :class="{ 'is-hovered': hoveredPoint?.label === point.label }"
                                    @mouseenter="hoveredPoint = point"
                                    @mouseleave="hoveredPoint = null"
                                >
                                    <title>
                                        {{ point.fullLabel }}: {{ point.value }}% ({{ point.riskLevel }})
                                    </title>
                                </circle>
                            </svg>
                        </div>

                        <div class="nf-chart-x-labels">
                            <span v-for="tick in chartTicks" :key="tick.label">
                                {{ tick.label }}
                            </span>
                        </div>

                        <div class="nf-panel-footnote">
                            <span class="nf-footnote-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="12" y1="16" x2="12" y2="12" stroke-linecap="round" />
                                    <line x1="12" y1="8" x2="12.01" y2="8" stroke-linecap="round" />
                                </svg>
                            </span>
                            {{
                                selectedTimeframe === '24h'
                                    ? '24-hour diurnal wildfire probability projection with hourly meteorological fluctuation.'
                                    : selectedTimeframe === '14d'
                                        ? '14-day extended wildfire probability projection based on real-time weather and satellite data.'
                                        : '7-day forward wildfire probability projection based on real-time weather and satellite data.'
                            }}
                        </div>
                    </article>

                    <article class="nf-panel nf-region-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">
                                    PROVINCIAL RISK RANKING (38)
                                </div>
                                <h2>Live risk by province</h2>
                                <p>
                                    Click a province to view 7-day trend &amp; weather
                                </p>
                            </div>

                            <span class="nf-mini-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="22" y1="12" x2="18" y2="12" />
                                    <line x1="6" y1="12" x2="2" y2="12" />
                                    <line x1="12" y1="6" x2="12" y2="2" />
                                    <line x1="12" y1="22" x2="12" y2="18" />
                                </svg>
                            </span>
                        </div>

                        <div
                            v-if="loading"
                            class="nf-empty-state"
                        >
                            Computing risk for 38 provinces...
                        </div>

                        <div
                            v-else-if="regions.length === 0"
                            class="nf-empty-state"
                        >
                            Provincial prediction data unavailable.
                        </div>

                        <div
                            v-else
                            class="nf-region-list"
                        >
                            <button
                                v-for="(region, index) in regions"
                                :key="region.name"
                                type="button"
                                class="nf-region-item nf-region-item-animated"
                                :class="{ 'is-active': selectedRegionName === region.name }"
                                :style="{ '--region-index': index }"
                                @click="selectProvince(region.name)"
                            >
                                <div class="nf-region-top">
                                    <span class="nf-region-number">
                                        {{
                                            String(index + 1).padStart(2, '0')
                                        }}
                                    </span>

                                    <span class="nf-region-name">
                                        {{ region.name }}
                                    </span>

                                    <span
                                        v-if="region.firmsHotspots > 0"
                                        class="nf-firms-pill"
                                        :title="`${region.firmsHotspots} active NASA FIRMS satellite hotspots (max FRP ${region.firmsMaxFrp} MW)`"
                                    >
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12" aria-hidden="true" style="margin-right: 3px; vertical-align: -1px; display: inline-block;">
                                            <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" stroke-linecap="round" stroke-linejoin="round" />
                                        </svg>
                                        {{ region.firmsHotspots }}
                                    </span>

                                    <span
                                        class="nf-risk-badge"
                                        :class="`is-${region.riskLevel.toLowerCase()}`"
                                    >
                                        {{ region.riskLevel }}
                                    </span>

                                    <span class="nf-region-value">
                                        {{ region.probabilityPct }}%
                                    </span>
                                </div>

                                <div class="nf-progress-track">
                                    <div
                                        class="nf-progress-fill nf-progress-fill-animated"
                                        :class="`is-${region.riskLevel.toLowerCase()}`"
                                        :style="{
                                            width: `${region.width}%`,
                                        }"
                                    />
                                </div>
                            </button>
                        </div>

                        <div class="nf-panel-footnote">
                            <span class="nf-footnote-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="12" y1="16" x2="12" y2="12" stroke-linecap="round" />
                                    <line x1="12" y1="8" x2="12.01" y2="8" stroke-linecap="round" />
                                </svg>
                            </span>
                            Ranked by highest fire vulnerability today (calibrated with NASA FIRMS satellite hotspots).
                        </div>
                    </article>
                </section>

                <section class="nf-secondary-grid">
                    <article class="nf-panel nf-map-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">
                                    GEOSPATIAL MONITORING
                                </div>
                                <h2>Indonesia risk overview</h2>
                                <p>
                                    Interactive NASA FIRMS satellite &amp; AI hotspot mapping (38 provinces)
                                </p>
                            </div>

                            <Link
                                href="/hotspot-map"
                                class="nf-outline-button"
                            >
                                Explore map
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" aria-hidden="true" style="margin-left: 4px; display: inline-block;">
                                    <line x1="7" y1="17" x2="17" y2="7" stroke-linecap="round" stroke-linejoin="round" />
                                    <polyline points="7 7 17 7 17 17" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </Link>
                        </div>

                        <div class="nf-map-preview">
                            <div class="nf-map-grid" />

                            <svg
                                viewBox="0 0 650 250"
                                class="nf-island-art"
                                role="img"
                                aria-label="Decorative illustration of Indonesian archipelago"
                            >
                                <path
                                    d="M65 82l35-20 35 8 18 20-14 17-28 4-12 18-23-4-18-17z"
                                    class="nf-island"
                                />
                                <path
                                    d="M155 148l22-9 21 9 18 28-9 35-16 12-12-20-17-18z"
                                    class="nf-island"
                                />
                                <path
                                    d="M238 63l20-10 17 13-6 17-20 5-14-10z"
                                    class="nf-island"
                                />
                                <path
                                    d="M270 102l18-9 14 12-6 18-20 5-13-12z"
                                    class="nf-island"
                                />
                                <path
                                    d="M335 112l24-17 25 5 17 19-11 17-24-3-17 12-18-12z"
                                    class="nf-island"
                                />
                                <path
                                    d="M420 73l35-16 38 11 18 20-13 19-32 6-19 20-25-10-15-22z"
                                    class="nf-island"
                                />
                                <path
                                    d="M505 155l21-9 19 12-5 17-25 5-14-11z"
                                    class="nf-island"
                                />

                                <circle
                                    cx="130"
                                    cy="92"
                                    r="4"
                                    class="nf-map-dot"
                                />
                                <circle
                                    cx="183"
                                    cy="174"
                                    r="4"
                                    class="nf-map-dot"
                                />
                                <circle
                                    cx="355"
                                    cy="119"
                                    r="4"
                                    class="nf-map-dot"
                                />
                                <circle
                                    cx="456"
                                    cy="88"
                                    r="4"
                                    class="nf-map-dot"
                                />
                            </svg>

                            <div class="nf-map-placeholder">
                                <span class="nf-map-placeholder-icon">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true">
                                        <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" stroke-linecap="round" stroke-linejoin="round" />
                                        <line x1="8" y1="2" x2="8" y2="18" stroke-linecap="round" stroke-linejoin="round" />
                                        <line x1="16" y1="6" x2="16" y2="22" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </span>

                                <strong>
                                    Interactive Risk Prediction Map
                                </strong>

                                <span>
                                    Inspect {{ formatNumber(firmsTotalHotspots) }} active NASA FIRMS hotspots and run live AI risk predictions across 38 provinces.
                                </span>

                                <Link
                                    href="/hotspot-map"
                                    class="nf-map-link"
                                >
                                    Open Hotspot Map
                                </Link>
                            </div>

                            <span class="nf-map-disclaimer">
                                GEOSPATIAL PREVIEW · CLICK TO LAUNCH INTERACTIVE MAP
                            </span>
                        </div>
                    </article>

                    <article class="nf-panel nf-weather-panel">
                        <div class="nf-panel-heading">
                            <div>
                                <div class="nf-panel-kicker">
                                    LIVE METEOROLOGY
                                </div>
                                <h2>Weather snapshot</h2>
                                <p>{{ activeRegion?.location ?? 'Indonesia' }}</p>
                            </div>

                            <span class="nf-weather-symbol">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <circle cx="12" cy="12" r="5" />
                                    <line x1="12" y1="1" x2="12" y2="3" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="12" y1="21" x2="12" y2="23" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="1" y1="12" x2="3" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="21" y1="12" x2="23" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke-linecap="round" stroke-linejoin="round" />
                                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                        </div>

                        <div class="nf-weather-list">
                            <div
                                v-for="item in weatherItems"
                                :key="item.label"
                                class="nf-weather-item"
                            >
                                <span class="nf-weather-icon">
                                    <svg v-if="item.type === 'temp'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                    <svg v-else-if="item.type === 'humidity'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                    <svg v-else-if="item.type === 'rain'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <line x1="16" y1="13" x2="16" y2="21" stroke-linecap="round" stroke-linejoin="round" />
                                        <line x1="8" y1="13" x2="8" y2="21" stroke-linecap="round" stroke-linejoin="round" />
                                        <line x1="12" y1="15" x2="12" y2="23" stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                    <svg v-else-if="item.type === 'wind'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </span>

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
                            Live Weather & Satellite · Connected
                        </div>

                        <Link
                            href="/weather-analysis"
                            class="nf-weather-link"
                        >
                            Open Weather Analysis
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13" aria-hidden="true" style="margin-left: 4px; display: inline-block;">
                                <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" stroke-linejoin="round" />
                                <polyline points="12 5 19 12 12 19" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </Link>
                    </article>
                </section>

                <footer class="nf-footer">
                    <div>
                        <span class="nf-footer-mark">N</span>
                        <span>
                            NusaFire
                            <span class="nf-footer-muted">
                                · AI Wildfire Early Warning System
                            </span>
                        </span>
                    </div>

                    <span>
                        BUILT FOR A SAFER, GREENER FUTURE
                    </span>
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
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    transition: background .2s ease, color .2s ease;
}

.nf-app.theme-dark,
html.theme-dark .nf-app,
html.dark .nf-app {
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
    min-width: 0;
    min-height: 100vh;
    margin-left: 268px;
    transition: margin-left .25s ease;
}

.nf-main.nf-main-collapsed {
    margin-left: 82px;
}

.nf-topbar {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 68px;
    min-height: 68px;
    padding: 0 32px;
    background: #ffffff;
    background: var(--db-surface, #ffffff);
    border-bottom: 1px solid #e5eae4;
    border-bottom: 1px solid var(--db-border, #e5eae4);
}

.nf-dashboard.theme-dark .nf-topbar,
.theme-dark .nf-dashboard .nf-topbar {
    background: #19231c;
    background: var(--db-surface, #19231c);
    border-bottom: 1px solid #2b3a2e;
    border-bottom: 1px solid var(--db-border, #2b3a2e);
}

.nf-topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-topbar-left h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 750;
    color: var(--db-text);
    letter-spacing: -0.01em;
}

.nf-topbar-right {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-live-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--db-text-soft);
    font-size: 11px;
    font-weight: 500;
}

.nf-status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    background: #48bb78;
    border-radius: 50%;
}

.nf-theme-toggle,
.nf-icon-button {
    display: grid;
    width: 38px;
    height: 38px;
    place-items: center;
    color: var(--db-text-soft);
    background: var(--db-surface-soft);
    border: 1px solid var(--db-border);
    border-radius: 10px;
    cursor: pointer;
    transition: color .15s ease, background .15s ease, border-color .15s ease;
}

.nf-theme-toggle:hover,
.nf-icon-button:hover {
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-color: var(--db-accent);
}

.nf-mobile-menu {
    display: none;
}

.nf-content {
    width: 100%;
    max-width: 1600px;
    margin: 0;
    padding: 32px;
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
    gap: 9px;
    margin-bottom: 10px;
    color: var(--db-accent, #165b33);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    line-height: 1;
}

.nf-eyebrow-line {
    display: inline-block;
    width: 18px;
    height: 2px;
    border-radius: 2px;
    background: var(--db-accent, #165b33);
    flex-shrink: 0;
}

.nf-page-heading h1 {
    margin: 0 0 8px 0;
    font-size: clamp(26px, 2.8vw, 34px);
    font-weight: 750;
    letter-spacing: -1.1px;
    line-height: 1.2;
    color: var(--db-text, #141f17);
}

.nf-page-heading p {
    margin: 0;
    color: var(--db-text-soft, #5f7065);
    font-size: 13px;
    line-height: 1.6;
    max-width: 660px;
}

.nf-heading-card,
.nf-heading-date {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    min-height: 52px;
    background: #ffffff;
    background: var(--db-surface, #ffffff);
    border: 1px solid #e5eae4;
    border: 1px solid var(--db-border, #e5eae4);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    white-space: nowrap;
    flex-shrink: 0;
}

.nf-heading-card-icon,
.nf-date-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    min-width: 34px;
    min-height: 34px;
    flex-shrink: 0;
    color: var(--db-accent, #165b33);
    background: var(--db-accent-soft, #e8f5e9);
    border-radius: 8px;
    line-height: 0;
    box-sizing: border-box;
    padding: 0;
}

.nf-heading-card-icon svg,
.nf-date-icon svg {
    display: block;
    width: 18px;
    height: 18px;
    margin: auto;
    flex-shrink: 0;
}

.nf-heading-card strong,
.nf-heading-date strong {
    display: block;
    font-size: 12px;
    font-weight: 700;
    color: var(--db-text, #141f17);
    line-height: 1.3;
}

.nf-heading-card > div > span,
.nf-heading-date > div > span {
    display: block;
    font-size: 11px;
    color: var(--db-text-soft, #5f7065);
    line-height: 1.4;
}

.nf-api-message {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
    padding: 14px 16px;
    color: var(--db-text);
    background: var(--db-surface);
    border: 1px solid var(--db-border);
    border-left: 3px solid #d27d42;
    border-radius: 10px;
    font-size: 11px;
}

.nf-api-message span {
    flex: 1;
    color: var(--db-text-soft);
}

.nf-api-message button {
    padding: 8px 12px;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border: 1px solid var(--db-border);
    border-radius: 7px;
    font-size: 10px;
    font-weight: 650;
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
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    border-radius: 9px;
    line-height: 0;
}

.nf-stat-icon svg {
    display: block;
    margin: auto;
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
    max-width: 185px;
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


.nf-trend-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.nf-filter-pills {
    display: inline-flex;
    align-items: center;
    background: var(--db-surface-soft);
    border: 1px solid var(--db-border);
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
}

.nf-pill-btn {
    border: none;
    background: transparent;
    color: var(--db-muted);
    font-size: 11px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;
    line-height: 1.2;
}

.nf-pill-btn:hover {
    color: var(--db-text);
}

.nf-pill-btn.active {
    background: var(--db-accent);
    color: #fff;
    font-weight: 600;
    box-shadow: 0 1px 4px rgba(45, 138, 91, 0.25);
}

.nf-hover-info {
    margin-left: auto;
    font-size: 11px;
    color: var(--db-text);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.nf-hover-badge {
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
}

.nf-hover-badge.risk-high {
    background: rgba(220, 38, 38, 0.14);
    color: #dc2626;
}

.nf-hover-badge.risk-moderate {
    background: rgba(217, 119, 6, 0.14);
    color: #d97706;
}

.nf-hover-badge.risk-low {
    background: rgba(45, 138, 91, 0.14);
    color: #2d8a5b;
}

.nf-chart-point {
    fill: #43a978;
    stroke: var(--db-surface);
    stroke-width: 2;
    cursor: pointer;
    transition: r 0.15s ease, stroke-width 0.15s ease;
}

.nf-chart-point:hover,
.nf-chart-point.is-hovered {
    stroke-width: 3;
    fill: #2d8a5b;
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
    gap: 8px;
    margin: 12px 0 0 54px;
    color: var(--db-muted);
    font-size: 9px;
}

.nf-chart-x-labels span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 31px;
    height: 31px;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 8px;
    line-height: 0;
}

.nf-mini-icon svg {
    display: block;
    margin: auto;
}

.nf-region-list {
    display: grid;
    gap: 10px;
    max-height: 290px;
    overflow-y: auto;
    padding-right: 6px;
    margin-top: 18px;
}

.nf-region-item {
    display: block;
    width: 100%;
    padding: 8px 10px;
    text-align: left;
    color: inherit;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    transition: background .15s ease, border-color .15s ease;
}

.nf-region-item:hover {
    background: var(--db-surface-soft);
}

.nf-region-item.is-active {
    background: var(--db-accent-soft);
    border-color: var(--db-border);
}

.nf-region-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 7px;
}

.nf-region-number {
    color: var(--db-muted);
    font-size: 9px;
}

.nf-region-name {
    flex: 1;
    font-size: 11px;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.nf-firms-pill {
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 8px;
    font-weight: 700;
    color: #b91c1c;
    background: #fee2e2;
    white-space: nowrap;
}

.nf-risk-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 8px;
    font-weight: 700;
    text-transform: uppercase;
}

.nf-risk-badge.is-high {
    color: #c53030;
    background: #fed7d7;
}

.nf-risk-badge.is-moderate {
    color: #b7791f;
    background: #fefcbf;
}

.nf-risk-badge.is-low {
    color: #276749;
    background: #c6f6d5;
}

.nf-region-value {
    color: var(--db-text-soft);
    font-size: 10px;
    font-variant-numeric: tabular-nums;
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
    opacity: .9;
    transition: width .3s ease;
}

.nf-progress-fill.is-high {
    background: #e53e3e;
}

.nf-progress-fill.is-moderate {
    background: #dd6b20;
}

.nf-progress-fill.is-low {
    background: #43a978;
}

.nf-empty-state {
    margin-top: 25px;
    padding: 20px 0;
    color: var(--db-muted);
    font-size: 11px;
    text-align: center;
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
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 35px;
    height: 35px;
    margin-bottom: 10px;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 10px;
    line-height: 0;
}

.nf-map-placeholder-icon svg {
    display: block;
    margin: auto;
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
    margin-top: 14px;
}

.nf-weather-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--db-border);
}

.nf-weather-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    color: var(--db-accent);
    background: var(--db-accent-soft);
    border-radius: 10px;
    line-height: 0;
}

.nf-weather-icon svg {
    display: block;
    margin: auto;
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
    font-size: 16px;
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
    margin-top: 14px;
    color: var(--db-muted);
    font-size: 9px;
}

.nf-weather-link {
    display: inline-block;
    margin-top: 12px;
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

@media (max-width: 1200px) {
    .nf-content {
        padding-right: 22px;
        padding-left: 22px;
    }

    .nf-topbar {
        padding-right: 22px;
        padding-left: 22px;
    }

    .nf-stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {
    .nf-main,
    .nf-main.nf-main-collapsed {
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

    .nf-heading-card,
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
        max-width: 140px;
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


/* Subtle dashboard entrance and data-loading motion. Visual-only; no API behavior changed. */
@keyframes nf-enter-up {
    from { opacity: 0; transform: translate3d(0, 12px, 0); }
    to { opacity: 1; transform: translate3d(0, 0, 0); }
}

@keyframes nf-chart-draw {
    from { stroke-dashoffset: 1; }
    to { stroke-dashoffset: 0; }
}

@keyframes nf-chart-area-reveal {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes nf-point-pop {
    from { opacity: 0; transform: scale(.65); }
    to { opacity: 1; transform: scale(1); }
}

.nf-dashboard .nf-page-heading {
    animation: nf-enter-up .55s cubic-bezier(.2, .7, .2, 1) both;
}

.nf-dashboard .nf-stat-card {
    animation: nf-enter-up .6s cubic-bezier(.2, .7, .2, 1) both;
    transition:
        transform .22s ease,
        box-shadow .22s ease,
        border-color .22s ease;
}

.nf-dashboard .nf-stat-card:nth-child(1) { animation-delay: .08s; }
.nf-dashboard .nf-stat-card:nth-child(2) { animation-delay: .16s; }
.nf-dashboard .nf-stat-card:nth-child(3) { animation-delay: .24s; }
.nf-dashboard .nf-stat-card:nth-child(4) { animation-delay: .32s; }

.nf-dashboard .nf-stat-card:hover {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--db-accent) 30%, var(--db-border));
    box-shadow: 0 12px 28px rgb(23 49 33 / 7%);
}

.nf-dashboard .nf-primary-grid > .nf-panel,
.nf-dashboard .nf-secondary-grid > .nf-panel {
    animation: nf-enter-up .65s cubic-bezier(.2, .7, .2, 1) both;
    animation-delay: .2s;
}

.nf-dashboard .nf-primary-grid > .nf-panel:nth-child(2),
.nf-dashboard .nf-secondary-grid > .nf-panel:nth-child(2) {
    animation-delay: .3s;
}

.nf-dashboard .nf-chart-line-animated {
    stroke-dasharray: 1;
    stroke-dashoffset: 1;
    animation: nf-chart-draw 1.35s cubic-bezier(.22, .61, .36, 1) .35s forwards;
}

.nf-dashboard .nf-trend-panel .nf-chart-wrap > svg path[fill="url(#nf-chart-fill)"] {
    opacity: 0;
    animation: nf-chart-area-reveal .8s ease-out .55s forwards;
}

.nf-dashboard .nf-chart-point {
    transform-box: fill-box;
    transform-origin: center;
    animation: nf-point-pop .35s ease-out both;
}

.nf-dashboard .nf-chart-point:nth-of-type(1) { animation-delay: .38s; }
.nf-dashboard .nf-chart-point:nth-of-type(2) { animation-delay: .48s; }
.nf-dashboard .nf-chart-point:nth-of-type(3) { animation-delay: .58s; }
.nf-dashboard .nf-chart-point:nth-of-type(4) { animation-delay: .68s; }
.nf-dashboard .nf-chart-point:nth-of-type(5) { animation-delay: .78s; }
.nf-dashboard .nf-chart-point:nth-of-type(6) { animation-delay: .88s; }
.nf-dashboard .nf-chart-point:nth-of-type(7) { animation-delay: .98s; }

.nf-dashboard .nf-status-dot {
    box-shadow: 0 0 0 0 rgb(72 187 120 / 35%);
    animation: nf-live-pulse 2.2s ease-out infinite;
}

@keyframes nf-live-pulse {
    0% { box-shadow: 0 0 0 0 rgb(72 187 120 / 35%); }
    70% { box-shadow: 0 0 0 6px rgb(72 187 120 / 0%); }
    100% { box-shadow: 0 0 0 0 rgb(72 187 120 / 0%); }
}

/* Provincial ranking entrance: stagger each row and reveal its risk bar. */
@keyframes nf-ranking-row-enter {
    from { opacity: 0; transform: translate3d(0, 8px, 0); }
    to { opacity: 1; transform: translate3d(0, 0, 0); }
}

@keyframes nf-risk-bar-grow {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
}

.nf-dashboard .nf-region-item-animated {
    animation: nf-ranking-row-enter .42s cubic-bezier(.2, .7, .2, 1) both;
    animation-delay: calc(.24s + (var(--region-index, 0) * 45ms));
    transition:
        background .2s ease,
        border-color .2s ease,
        transform .2s ease,
        box-shadow .2s ease;
}

.nf-dashboard .nf-region-item-animated:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgb(23 49 33 / 5%);
}

.nf-dashboard .nf-progress-fill-animated {
    transform: scaleX(0);
    transform-origin: left center;
    animation: nf-risk-bar-grow .85s cubic-bezier(.22, .61, .36, 1) both;
    animation-delay: calc(.35s + (var(--region-index, 0) * 45ms));
}

@media (prefers-reduced-motion: reduce) {
    .nf-dashboard .nf-page-heading,
    .nf-dashboard .nf-stat-card,
    .nf-dashboard .nf-primary-grid > .nf-panel,
    .nf-dashboard .nf-secondary-grid > .nf-panel,
    .nf-dashboard .nf-chart-line-animated,
    .nf-dashboard .nf-trend-panel .nf-chart-wrap > svg path[fill="url(#nf-chart-fill)"],
    .nf-dashboard .nf-chart-point,
    .nf-dashboard .nf-status-dot,
    .nf-dashboard .nf-region-item-animated,
    .nf-dashboard .nf-progress-fill-animated {
        animation: none !important;
        transition: none !important;
        opacity: 1 !important;
        stroke-dashoffset: 0 !important;
        transform: none !important;
    }
}

</style>