<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Head } from '@inertiajs/vue3';
import axios from 'axios';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type MetricKey = 'temperature' | 'humidity' | 'rainfall' | 'wind';

type WeatherRecord = {
    date: string;
    temperature: number;
    temperatureMax: number;
    temperatureMin: number;
    humidity: number;
    rainfall: number;
    windMs: number;
    wind: number;
    weatherCode: number;
};

type CurrentWeatherInfo = {
    temperature: number;
    humidity: number;
    rainfall: number;
    wind: number;
    weatherCode: number;
    isDay: boolean;
    time: string;
};

type LocationOption = {
    id: string;
    label: string;
    latitude: number;
    longitude: number;
    region: string;
    island: string;
    province: string;
    district: string;
    gridId: string;
    totalHotspots: number;
};

type LocationsResponse = {
    status: string;
    total_locations: number;
    data: {
        REGION: string;
        LOCATION: string;
        GRID_ID: string;
        LATITUDE: number;
        LONGITUDE: number;
        total_records: number;
        total_hotspots: number;
        label: string;
        island?: string | null;
        province?: string | null;
        district?: string | null;
    }[];
};


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

const LANDCOVER_OPTIONS: { value: number | null; label: string }[] = [
    { value: null, label: 'Automatic (Regional Default)' },
    { value: 3, label: 'Natural / Primary Forest (Class 3)' },
    { value: 9, label: 'Plantation Forest / HTI (Class 9)' },
    { value: 12, label: 'Shrubland / Peatland (Class 12)' },
    { value: 11, label: 'Grassland / Savanna (Class 11)' },
    { value: 21, label: 'Agriculture & Plantations (Class 21)' },
    { value: 25, label: 'Open / Barren Land (Class 25)' },
];

const provinces = Object.keys(PROVINCE_COORDINATES);

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);

const { theme, toggleTheme } = useTheme();
const isDark = computed(() => theme.value === 'dark');

function toggleSidebar() {
    if (window.innerWidth <= 900) {
        mobileMenuOpen.value = !mobileMenuOpen.value;
    } else {
        sidebarCollapsed.value = !sidebarCollapsed.value;
        localStorage.setItem('nf-sidebar-collapsed', String(sidebarCollapsed.value));
    }
}

// Form input sementara (sebelum tombol eksekusi ditekan)
const formProvince = ref('Bengkulu');
const formPeriod = ref('7');
const formLandcoverClass = ref<number | null>(null);

// Parameter aktif yang benar-benar dikirim ke API
const selectedProvince = ref('Bengkulu');
const selectedPeriod = ref('7');
const landcoverClass = ref<number | null>(null);

const selectedMetric = ref<MetricKey>('temperature');
const selectedLocationId = ref('');

const locations = ref<LocationOption[]>([]);
const loadingLocations = ref(false);

const provinceLocations = computed(() =>
    locations.value.filter((location) =>
        normalizeProvince(location.province) === normalizeProvince(selectedProvince.value),
    ),
);

const activeProvincePoints = computed(() => {
    if (provinceLocations.value.length > 0) {
        return provinceLocations.value.map((point) => ({
            latitude: point.latitude,
            longitude: point.longitude,
        }));
    }

    const fallback = PROVINCE_COORDINATES[selectedProvince.value];
    return fallback ? [{ latitude: fallback.lat, longitude: fallback.lon }] : [];
});

const activeCoordinates = computed(() => {
    const points = activeProvincePoints.value;
    if (points.length > 0) {
        return { lat: points[0].latitude, lon: points[0].longitude };
    }
    const fallback = PROVINCE_COORDINATES[selectedProvince.value];
    return fallback ? { lat: fallback.lat, lon: fallback.lon } : { lat: -0.7, lon: 113.9 };
});


const selectedLandcoverLabel = computed(() =>
    LANDCOVER_OPTIONS.find((opt) => opt.value === landcoverClass.value)?.label
    ?? 'Automatic (Regional Default)',
);

const weatherData = ref<WeatherRecord[]>([]);
const currentWeather = ref<CurrentWeatherInfo | null>(null);
const loadingWeather = ref(false);
const weatherError = ref('');
const weatherSourceLabel = ref('Open-Meteo Real-Time API');
const weatherIsLive = ref(true);
const lastUpdated = ref('');

const aiStatus = ref<'checking' | 'online' | 'offline'>('checking');
// Atmospheric and Meteorological Summary (Pure Observation)
const atmosphericExtremes = computed(() => {
    const list = weatherData.value;
    if (list.length === 0) {
        return {
            maxTemp: currentWeather.value ? currentWeather.value.temperature : 0,
            minTemp: currentWeather.value ? currentWeather.value.temperature : 0,
            avgTemp: currentWeather.value ? currentWeather.value.temperature : 0,
            minHumidity: currentWeather.value ? currentWeather.value.humidity : 0,
            avgHumidity: currentWeather.value ? currentWeather.value.humidity : 0,
            totalRainfall: currentWeather.value ? currentWeather.value.rainfall : 0,
            maxWind: currentWeather.value ? currentWeather.value.wind : 0,
            dryDays: 0,
        };
    }

    const temps = list.map((d) => d.temperatureMax ?? d.temperature);
    const minTemps = list.map((d) => d.temperatureMin ?? d.temperature);
    const hums = list.map((d) => d.humidity);
    const rains = list.map((d) => d.rainfall);
    const winds = list.map((d) => d.wind);

    const maxT = Math.max(...temps);
    const minT = Math.min(...minTemps);
    const avgT = Math.round((temps.reduce((a, b) => a + b, 0) / temps.length) * 10) / 10;
    const minH = Math.min(...hums);
    const avgH = Math.round(hums.reduce((a, b) => a + b, 0) / hums.length);
    const totalR = Math.round(rains.reduce((a, b) => a + b, 0) * 10) / 10;
    const maxW = Math.max(...winds);
    const dryDays = rains.filter((r) => r === 0).length;

    return {
        maxTemp: maxT,
        minTemp: minT,
        avgTemp: avgT,
        minHumidity: minH,
        avgHumidity: avgH,
        totalRainfall: totalR,
        maxWind: maxW,
        dryDays,
    };
});


const periods = [
    { value: '7', label: 'Last 7 days' },
    { value: '10', label: 'Last 10 days' },
];

const metrics: {
    value: MetricKey;
    label: string;
    shortLabel: string;
    unit: string;
}[] = [
    { value: 'temperature', label: 'Average temperature', shortLabel: 'Temp', unit: '°C' },
    { value: 'humidity', label: 'Humidity', shortLabel: 'Humidity', unit: '%' },
    { value: 'rainfall', label: 'Rainfall', shortLabel: 'Rain', unit: 'mm' },
    { value: 'wind', label: 'Wind speed', shortLabel: 'Wind', unit: 'km/h' },
];

const visibleData = computed(() =>
    weatherData.value.slice(-Number(selectedPeriod.value)),
);

const latest = computed<WeatherRecord | null>(() => {
    const records = visibleData.value;
    return records.length ? records[records.length - 1] : null;
});

function describeWmoCode(code: number, isDay = true): {
    label: string;
    icon: string;
    badgeClass: string;
    summary: string;
} {
    if (code === 0) {
        return {
            label: isDay ? 'Clear' : 'Clear Night',
            icon: isDay ? '☀' : '☾',
            badgeClass: 'clear',
            summary: 'Clear sky without significant cloud cover',
        };
    }
    if (code === 1 || code === 2) {
        return {
            label: 'Partly Cloudy',
            icon: '⛅',
            badgeClass: 'partly',
            summary: 'Partly cloudy with moderate solar radiation',
        };
    }
    if (code === 3) {
        return {
            label: 'Overcast',
            icon: '☁',
            badgeClass: 'cloud',
            summary: 'Overcast sky with heavy clouds',
        };
    }
    if (code === 45 || code === 48) {
        return {
            label: 'Foggy',
            icon: '🌫',
            badgeClass: 'cloud',
            summary: 'Fog or humid misty air',
        };
    }
    if ((code >= 51 && code <= 57) || (code >= 80 && code <= 81)) {
        return {
            label: 'Light Rain',
            icon: '🌦',
            badgeClass: 'rain',
            summary: 'Drizzle or light local rain showers',
        };
    }
    if ((code >= 61 && code <= 67) || (code >= 82)) {
        return {
            label: 'Rain',
            icon: '🌧',
            badgeClass: 'rain',
            summary: 'Moderate to heavy rain showers',
        };
    }
    if (code >= 95) {
        return {
            label: 'Thunderstorm',
            icon: '⛈',
            badgeClass: 'storm',
            summary: 'Heavy rain accompanied by lightning',
        };
    }
    return {
        label: 'Partly Cloudy',
        icon: '⛅',
        badgeClass: 'partly',
        summary: 'Stable atmospheric conditions',
    };
}

const currentCondition = computed(() => {
    if (!currentWeather.value) return null;
    return describeWmoCode(currentWeather.value.weatherCode, currentWeather.value.isDay);
});

function average(key: 'temperature' | 'humidity' | 'wind'): number | null {
    const records = visibleData.value;
    if (!records.length) return null;
    return records.reduce((sum, record) => sum + record[key], 0) / records.length;
}

const averageTemperature = computed(() => average('temperature'));
const averageHumidity = computed(() => average('humidity'));
const averageWind = computed(() => average('wind'));

const totalRainfall = computed<number | null>(() => {
    if (!visibleData.value.length) return null;
    return visibleData.value.reduce((sum, record) => sum + record.rainfall, 0);
});

const activeMetric = computed(
    () => metrics.find((metric) => metric.value === selectedMetric.value) ?? metrics[0],
);

const chartValues = computed(() =>
    visibleData.value.map((record) => ({
        date: record.date,
        label: formatDate(record.date),
        value: record[selectedMetric.value],
    })),
);

const chartMaximum = computed(() => {
    const values = chartValues.value.map((item) => item.value);
    return Math.max(...values, 1) * 1.15;
});

const chartPoints = computed(() => {
    const values = chartValues.value;
    if (!values.length) return '';

    return values.map((item, index) => {
        const x = values.length === 1 ? 50 : (index / (values.length - 1)) * 100;
        const y = 100 - (item.value / chartMaximum.value) * 85;
        return `${x},${y}`;
    }).join(' ');
});

const chartAreaPoints = computed(() => {
    if (!chartPoints.value) return '';
    return `0,100 ${chartPoints.value} 100,100`;
});

const periodLabel = computed(() => {
    if (!visibleData.value.length) return 'No data available';
    const first = visibleData.value[0];
    const last = visibleData.value[visibleData.value.length - 1];
    return `${formatFullDate(first.date)} – ${formatFullDate(last.date)}`;
});

const aiStatusLabel = computed(() => {
    if (aiStatus.value === 'checking') return 'Checking system...';
    if (aiStatus.value === 'online') return 'Live Monitoring';
    return 'Service Offline';
});


function formatNumber(value: number | null | undefined, decimals = 1): string {
    if (value == null || !Number.isFinite(value)) return '—';
    return value.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}

function formatDate(date: string): string {
    return new Date(`${date}T00:00:00`).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
    });
}

function formatFullDate(date: string): string {
    return new Date(`${date}T00:00:00`).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
    });
}

function getWeatherCondition(record: WeatherRecord): string {
    return describeWmoCode(record.weatherCode, true).label;
}

function getWeatherClass(record: WeatherRecord): string {
    return describeWmoCode(record.weatherCode, true).badgeClass;
}

function normalizeProvince(value: string): string {
    const normalized = value
        .trim()
        .toLocaleLowerCase('id-ID')
        .replace(/[.]/g, '')
        .replace(/\s+/g, ' ');

    const aliases: Record<string, string> = {
        'sumatra utara': 'sumatera utara',
        'sumatra barat': 'sumatera barat',
        'sumatra selatan': 'sumatera selatan',
        'bangka belitung': 'kepulauan bangka belitung',
        'kepulauan bangka belitung': 'kepulauan bangka belitung',
        'jakarta': 'dki jakarta',
        'dki jakarta': 'dki jakarta',
        'daerah khusus ibukota jakarta': 'dki jakarta',
        'daerah khusus jakarta': 'dki jakarta',
        'diy': 'di yogyakarta',
        'yogyakarta': 'di yogyakarta',
        'di yogyakarta': 'di yogyakarta',
        'daerah istimewa yogyakarta': 'di yogyakarta',
        'nanggroe aceh darussalam': 'aceh',
    };

    return aliases[normalized] ?? normalized;
}

async function loadLocations() {
    loadingLocations.value = true;

    try {
        const response = await axios.get<LocationsResponse>('/internal/ai/locations');
        const payload = response.data;

        if (payload.status !== 'success' || !Array.isArray(payload.data)) {
            throw new Error('Invalid location list format.');
        }

        locations.value = payload.data
            .filter((item) =>
                Number.isFinite(Number(item.LATITUDE))
                && Number.isFinite(Number(item.LONGITUDE))
                && Boolean(item.GRID_ID)
                && Boolean(item.LOCATION),
            )
            .map((item) => ({
                id: item.GRID_ID,
                label: item.label || `${item.REGION} — ${item.LOCATION}`,
                latitude: Number(item.LATITUDE),
                longitude: Number(item.LONGITUDE),
                region: item.REGION,
                island: String(item.island ?? '').trim() || 'Unavailable',
                province: String(item.province ?? '').trim() || 'Unavailable',
                district: String(item.district ?? '').trim() || 'Unavailable',
                gridId: item.GRID_ID,
                totalHotspots: Number(item.total_hotspots ?? 0),
            }));

        const provinceMatches = locations.value.filter((location) =>
            normalizeProvince(location.province) === normalizeProvince(selectedProvince.value),
        );
        selectedLocationId.value = provinceMatches[0]?.id ?? '';
    } catch {
        locations.value = [];
        selectedLocationId.value = '';
    } finally {
        loadingLocations.value = false;
    }
}

async function loadWeather() {
    const points = activeProvincePoints.value;

    if (!points.length) {
        weatherData.value = [];
        currentWeather.value = null;
        weatherError.value = `Coordinates for province ${selectedProvince.value} not found.`;
        
        return;
    }

    loadingWeather.value = true;
    weatherError.value = '';
    
    

    const avgLat = points.reduce((sum, point) => sum + point.latitude, 0) / points.length;
    const avgLon = points.reduce((sum, point) => sum + point.longitude, 0) / points.length;

    try {
        const response = await axios.get('/internal/ai/weather-history', {
            params: {
                latitude: avgLat,
                longitude: avgLon,
                days: 10,
            },
        });

        const payload = response.data;
        const current = payload?.current;
        const daily = payload?.daily;

        if (!daily || !Array.isArray(daily.time)) {
            throw new Error('Server response does not contain daily weather data.');
        }

        weatherSourceLabel.value = payload?.source || 'Open-Meteo Real-Time API';
        weatherIsLive.value = payload?.live !== false;

        if (current) {
            const windMsCurrent = Number(current.wind_speed_10m ?? 0);
            currentWeather.value = {
                temperature: Number(current.temperature_2m ?? 0),
                humidity: Number(current.relative_humidity_2m ?? 0),
                rainfall: Number(current.precipitation ?? 0),
                wind: windMsCurrent * 3.6,
                weatherCode: Number(current.weather_code ?? 1),
                isDay: Number(current.is_day ?? 1) === 1,
                time: String(current.time ?? ''),
            };
        } else {
            currentWeather.value = null;
        }

        const records: WeatherRecord[] = daily.time.flatMap((date: string, index: number) => {
            const t = Number(daily.temperature_2m_mean?.[index]);
            const tMax = Number(daily.temperature_2m_max?.[index]);
            const tMin = Number(daily.temperature_2m_min?.[index]);
            const rh = Number(daily.relative_humidity_2m_mean?.[index]);
            const rain = Number(daily.precipitation_sum?.[index]);
            const windMs = Number(daily.wind_speed_10m_mean?.[index]);
            const code = Number(daily.weather_code?.[index] ?? 1);

            if (
                !Number.isFinite(t)
                || !Number.isFinite(tMax)
                || !Number.isFinite(tMin)
                || !Number.isFinite(rh)
                || !Number.isFinite(rain)
                || !Number.isFinite(windMs)
            ) {
                return [];
            }

            return [{
                date,
                temperature: t,
                temperatureMax: tMax,
                temperatureMin: tMin,
                humidity: rh,
                rainfall: rain,
                windMs,
                wind: windMs * 3.6,
                weatherCode: Number.isFinite(code) ? code : 1,
            }];
        });

        weatherData.value = records;
        lastUpdated.value = new Date().toLocaleString('en-US');

        if (!records.length) {
            weatherError.value = 'No complete weather data available to display.';
        } else if (aiStatus.value === 'online') {
            // Meteorological observation refreshed
        }
    } catch (error: unknown) {
        weatherData.value = [];
        currentWeather.value = null;
        weatherError.value = axios.isAxiosError(error)
            ? error.response?.data?.message || error.message || 'Failed to fetch weather data from AI server.'
            : error instanceof Error
                ? error.message
                : 'Failed to fetch weather data.';
    } finally {
        loadingWeather.value = false;
    }
}

async function checkAiHealth() {
    aiStatus.value = 'checking';

    try {
        const response = await axios.get('/internal/ai/health');
        aiStatus.value = response.data?.model_loaded ? 'online' : 'offline';
    } catch {
        aiStatus.value = 'offline';
    }
}


async function applyFilters() {
    selectedProvince.value = formProvince.value;
    selectedPeriod.value = formPeriod.value;
    landcoverClass.value = formLandcoverClass.value;

    const firstLocation = locations.value.find((location) =>
        normalizeProvince(location.province) === normalizeProvince(selectedProvince.value),
    );
    selectedLocationId.value = firstLocation?.id ?? '';

    await loadWeather();
}


onMounted(async () => {
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) sidebarCollapsed.value = saved === 'true';
    await Promise.all([
        loadLocations(),
        checkAiHealth(),
    ]);

    await loadWeather();
});
</script>

<template>
    <Head title="Weather Analysis | NusaFire" />

    <div class="weather-page" :class="{ 'dark-mode': isDark, 'theme-dark': isDark, 'theme-light': !isDark }">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main class="weather-main" :class="{ 'weather-main-collapsed': sidebarCollapsed }">
            <header class="topbar">
                <div class="topbar-left">
                    <button
                        class="icon-button mobile-menu-button"
                        type="button"
                        aria-label="Open navigation"
                        @click="toggleSidebar"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="20" height="20" aria-hidden="true">
                            <line x1="4" y1="6" x2="20" y2="6" />
                            <line x1="4" y1="12" x2="20" y2="12" />
                            <line x1="4" y1="18" x2="20" y2="18" />
                        </svg>
                    </button>

                    <h1>Weather Analysis</h1>
                </div>

                <div class="topbar-actions">
                    <span class="connection-dot" :class="aiStatus" />
                    <span class="connection-label">{{ aiStatusLabel }}</span>

                    <button
                        class="icon-button"
                        type="button"
                        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
                        :title="isDark ? 'Light Mode' : 'Dark Mode'"
                        @click="toggleTheme"
                    >
                        <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18" aria-hidden="true">
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

            <div class="page-content">
                <section class="page-heading">
                    <div class="heading-text">
                        <div class="eyebrow">
                            <span class="eyebrow-line"></span>
                            REAL-TIME ENVIRONMENTAL MONITORING
                        </div>

                        <h1>Weather Analysis</h1>

                        <p class="page-subtitle">
                            Monitor real-time weather conditions, forecasts, and wildfire risk levels across Indonesia.
                        </p>
                    </div>

                    <div class="heading-actions">
                        <div class="heading-card">
                            <div class="heading-card-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18" aria-hidden="true">
                                    <circle cx="12" cy="12" r="5" />
                                    <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </div>
                            <div>
                                <strong>Real-Time Weather &amp; Risk</strong>
                                <span>38 Provinces Monitored</span>
                            </div>
                        </div>

                        <button
                            class="refresh-button"
                            type="button"
                            :disabled="loadingWeather"
                            @click="loadWeather"
                        >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="16" height="16" aria-hidden="true" :class="{ 'spin-anim': loadingWeather }">
                                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.19" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                            {{ loadingWeather ? 'Loading data...' : 'Refresh data' }}
                        </button>
                    </div>
                </section>

                <section class="filter-card">
                    <div class="section-heading">
                        <div>
                            <h2>Observation parameters</h2>
                            <p>Select province, display period, and land cover class, then click Apply Analysis.</p>
                        </div>
                        <span class="filter-symbol">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" stroke-linecap="round">
                                <line x1="4" y1="6" x2="20" y2="6"/>
                                <line x1="4" y1="12" x2="20" y2="12"/>
                                <line x1="4" y1="18" x2="20" y2="18"/>
                            </svg>
                        </span>
                    </div>

                    <form class="filter-grid" @submit.prevent="applyFilters">
                        <label class="field">
                            <span>Province (38 Provinces)</span>
                            <select v-model="formProvince">
                                <option
                                    v-for="province in provinces"
                                    :key="province"
                                    :value="province"
                                >
                                    {{ province }}
                                </option>
                            </select>
                        </label>

                        <label class="field">
                            <span>Display period</span>
                            <select v-model="formPeriod">
                                <option
                                    v-for="period in periods"
                                    :key="period.value"
                                    :value="period.value"
                                >
                                    {{ period.label }}
                                </option>
                            </select>
                        </label>

                        <label class="field">
                            <span>Land cover class</span>
                            <select v-model="formLandcoverClass">
                                <option
                                    v-for="option in LANDCOVER_OPTIONS"
                                    :key="String(option.value)"
                                    :value="option.value"
                                >
                                    {{ option.label }}
                                </option>
                            </select>
                        </label>

                        <div class="filter-action-wrap">
                            <button
                                type="submit"
                                class="prediction-button filter-submit-btn"
                                :disabled="loadingWeather"
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" stroke-linecap="round" stroke-linejoin="round">
                                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                                </svg>
                                {{ loadingWeather ? 'Processing...' : 'Apply Analysis' }}
                            </button>
                        </div>
                    </form>

                    <div class="location-bar">
                        <span class="location-pin">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                <circle cx="12" cy="10" r="3"/>
                            </svg>
                        </span>
                        <span class="location-summary">
                            <strong>{{ selectedProvince }}</strong>
                            <span>·</span>
                            <span>
                                {{
                                    provinceLocations.length > 0
                                        ? `${provinceLocations.length} grid points`
                                        : `Center coordinates (${activeProvincePoints[0]?.latitude.toFixed(2)}, ${activeProvincePoints[0]?.longitude.toFixed(2)})`
                                }}
                            </span>
                            <span>·</span>
                            <span>{{ periodLabel }}</span>
                            <template v-if="lastUpdated">
                                <span>·</span>
                                <span>Updated {{ lastUpdated }}</span>
                            </template>
                        </span>
                    </div>
                </section>

                <div v-if="weatherError" class="error-banner" role="alert">
                    <span class="error-icon">!</span>
                    <div>
                        <strong>Failed to load weather data</strong>
                        <p>{{ weatherError }}</p>
                        <button type="button" class="text-button" @click="loadWeather">
                            Try again
                        </button>
                    </div>
                </div>

                <div v-if="loadingWeather && !weatherData.length" class="loading-card">
                    <span class="loading-spinner" />
                    <div>
                        <strong>Fetching real-time weather data</strong>
                        <p>Connecting to NusaFire meteorological service...</p>
                    </div>
                </div>

                <section class="stats-grid">
                    <article class="stat-card">
                        <div class="stat-top">
                            <span class="stat-label">Weather condition</span>
                            <span class="stat-icon condition-icon">
                                <svg
                                    v-if="currentCondition?.badgeClass === 'clear'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    width="18"
                                    height="18"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    aria-hidden="true"
                                >
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
                                <svg
                                    v-else-if="currentCondition?.badgeClass === 'partly'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    width="18"
                                    height="18"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    aria-hidden="true"
                                >
                                    <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2" />
                                    <path d="M17.5 19H9a5 5 0 0 1-1-9.9 6 6 0 0 1 11 3 4 4 0 0 1-1.5 6.9z" />
                                </svg>
                                <svg
                                    v-else-if="currentCondition?.badgeClass === 'rain'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    width="18"
                                    height="18"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    aria-hidden="true"
                                >
                                    <line x1="16" y1="13" x2="16" y2="21" />
                                    <line x1="8" y1="13" x2="8" y2="21" />
                                    <line x1="12" y1="15" x2="12" y2="23" />
                                    <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" />
                                </svg>
                                <svg
                                    v-else-if="currentCondition?.badgeClass === 'storm'"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    width="18"
                                    height="18"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    aria-hidden="true"
                                >
                                    <path d="M19 16.9A5 5 0 0 0 18 7h-1.26a8 8 0 1 0-11.62 9" />
                                    <polyline points="13 11 9 17 15 17 11 23" />
                                </svg>
                                <svg
                                    v-else
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    width="18"
                                    height="18"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    aria-hidden="true"
                                >
                                    <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
                                </svg>
                            </span>
                        </div>
                        <div class="stat-value condition-stat-value">
                            {{ currentCondition ? currentCondition.label : 'Clear' }}
                        </div>
                        <div class="stat-description">
                            {{ currentCondition ? currentCondition.summary : 'Stable atmospheric conditions' }}
                        </div>
                        <div class="stat-accent condition-accent" />
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span class="stat-label">Average temperature</span>
                            <span class="stat-icon temperature-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
                                </svg>
                            </span>
                        </div>
                        <div class="stat-value">
                            {{ formatNumber(averageTemperature) }} <span>°C</span>
                        </div>
                        <div class="stat-description">
                            Current: {{ currentWeather ? `${formatNumber(currentWeather.temperature)} °C` : '—' }}
                        </div>
                        <div class="stat-accent temperature-accent" />
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span class="stat-label">Average humidity</span>
                            <span class="stat-icon humidity-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
                                </svg>
                            </span>
                        </div>
                        <div class="stat-value">
                            {{ formatNumber(averageHumidity) }} <span>%</span>
                        </div>
                        <div class="stat-description">
                            Current: {{ currentWeather ? `${formatNumber(currentWeather.humidity, 0)}%` : '—' }}
                        </div>
                        <div class="stat-accent humidity-accent" />
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span class="stat-label">Rainfall accumulation</span>
                            <span class="stat-icon rainfall-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="8" y1="19" x2="8" y2="21"/>
                                    <line x1="8" y1="13" x2="8" y2="15"/>
                                    <line x1="16" y1="19" x2="16" y2="21"/>
                                    <line x1="16" y1="13" x2="16" y2="15"/>
                                    <line x1="12" y1="21" x2="12" y2="23"/>
                                    <line x1="12" y1="15" x2="12" y2="17"/>
                                    <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/>
                                </svg>
                            </span>
                        </div>
                        <div class="stat-value">
                            {{ formatNumber(totalRainfall) }} <span>mm</span>
                        </div>
                        <div class="stat-description">
                            Total rainfall over last {{ selectedPeriod }} days
                        </div>
                        <div class="stat-accent rainfall-accent" />
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span class="stat-label">Wind speed</span>
                            <span class="stat-icon wind-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/>
                                </svg>
                            </span>
                        </div>
                        <div class="stat-value">
                            {{ formatNumber(averageWind) }} <span>km/h</span>
                        </div>
                        <div class="stat-description">
                            Current: {{ currentWeather ? `${formatNumber(currentWeather.wind)} km/h` : '—' }}
                        </div>
                        <div class="stat-accent wind-accent" />
                    </article>
                </section>

                <section class="content-grid">
                    <article class="panel chart-panel">
                        <div class="panel-header chart-panel-header">
                            <div>
                                <div class="panel-eyebrow">METEOROLOGICAL DATA</div>
                                <h2>Weather trends</h2>
                                <p>{{ activeMetric.label }} ({{ activeMetric.unit }})</p>
                            </div>

                            <div class="chart-metric-switch" role="tablist" aria-label="Select chart metric">
                                <button
                                    v-for="metric in metrics"
                                    :key="metric.value"
                                    type="button"
                                    class="metric-pill"
                                    :class="{ active: selectedMetric === metric.value }"
                                    @click="selectedMetric = metric.value"
                                >
                                    {{ metric.shortLabel }}
                                </button>
                            </div>
                        </div>

                        <div class="chart-legend">
                            <span class="legend-dot" />
                            <span>{{ activeMetric.label }}</span>
                            <span class="legend-period">{{ periodLabel }}</span>
                        </div>

                        <div v-if="!chartValues.length" class="empty-chart">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="32" height="32" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="18" y1="20" x2="18" y2="10"/>
                                <line x1="12" y1="20" x2="12" y2="4"/>
                                <line x1="6" y1="20" x2="6" y2="14"/>
                            </svg>
                            <strong>Chart unavailable</strong>
                            <p>Data will appear once loaded.</p>
                        </div>

                        <div v-else class="chart-wrap">
                            <div class="chart-y-labels">
                                <span>{{ formatNumber(chartMaximum) }}</span>
                                <span>{{ formatNumber(chartMaximum * .66) }}</span>
                                <span>{{ formatNumber(chartMaximum * .33) }}</span>
                                <span>0</span>
                            </div>

                            <div class="chart-visual">
                                <div class="chart-grid-lines">
                                    <span />
                                    <span />
                                    <span />
                                    <span />
                                </div>

                                <svg
                                    class="weather-chart"
                                    viewBox="0 0 100 100"
                                    preserveAspectRatio="none"
                                    role="img"
                                    :aria-label="`Chart ${activeMetric.label}`"
                                >
                                    <defs>
                                        <linearGradient
                                            id="weatherAreaGradient"
                                            x1="0"
                                            y1="0"
                                            x2="0"
                                            y2="1"
                                        >
                                            <stop offset="0%" stop-color="#35a879" stop-opacity=".25" />
                                            <stop offset="100%" stop-color="#35a879" stop-opacity="0" />
                                        </linearGradient>
                                    </defs>

                                    <polygon :points="chartAreaPoints" fill="url(#weatherAreaGradient)" />

                                    <polyline
                                        :points="chartPoints"
                                        fill="none"
                                        stroke="#35a879"
                                        stroke-width="1.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        vector-effect="non-scaling-stroke"
                                    />
                                </svg>
                            </div>

                            <div class="chart-x-labels">
                                <span
                                    v-for="(item, index) in chartValues"
                                    :key="item.date"
                                    v-show="
                                        chartValues.length <= 7
                                        || index === 0
                                        || index === chartValues.length - 1
                                        || index % 2 === 0
                                    "
                                >
                                    {{ item.label }}
                                </span>
                            </div>
                        </div>

                        <div v-if="chartValues.length" class="chart-summary">
                            <div>
                                <span>Today ({{ formatDate(chartValues[chartValues.length - 1].date) }})</span>
                                <strong>
                                    {{ formatNumber(chartValues[chartValues.length - 1].value) }}
                                    {{ activeMetric.unit }}
                                </strong>
                            </div>
                            <div>
                                <span>Observations</span>
                                <strong>{{ chartValues.length }} days</strong>
                            </div>
                        </div>
                    </article>

                    <article class="panel climate-panel">
                        <div class="panel-header">
                            <div>
                                <div class="panel-eyebrow">METEOROLOGICAL SUMMARY</div>
                                <h2>Atmospheric Extremes</h2>
                                <p>Real-time atmospheric telemetry summary from Open-Meteo API.</p>
                            </div>
                            <span class="panel-icon" style="background: rgba(14, 165, 233, 0.12); color: #0284c7;">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
                                </svg>
                            </span>
                        </div>

                        <div class="climate-stats-grid">
                            <div class="climate-stat-card">
                                <span class="climate-stat-label">Temperature Range</span>
                                <strong class="climate-stat-val">{{ atmosphericExtremes.minTemp }}°C – {{ atmosphericExtremes.maxTemp }}°C</strong>
                                <small>Average: {{ atmosphericExtremes.avgTemp }}°C</small>
                            </div>

                            <div class="climate-stat-card">
                                <span class="climate-stat-label">Relative Humidity (RH)</span>
                                <strong class="climate-stat-val">{{ atmosphericExtremes.minHumidity }}% – {{ atmosphericExtremes.avgHumidity }}%</strong>
                                <small>Minimum recorded RH</small>
                            </div>

                            <div class="climate-stat-card">
                                <span class="climate-stat-label">Total Rainfall Accumulation</span>
                                <strong class="climate-stat-val">{{ atmosphericExtremes.totalRainfall }} mm</strong>
                                <small>{{ atmosphericExtremes.dryDays }} dry days</small>
                            </div>

                            <div class="climate-stat-card">
                                <span class="climate-stat-label">Peak Wind Speed</span>
                                <strong class="climate-stat-val">{{ atmosphericExtremes.maxWind }} km/h</strong>
                                <small>{{ (atmosphericExtremes.maxWind / 3.6).toFixed(1) }} m/s gust</small>
                            </div>
                        </div>

                        <div class="climate-ai-bridge">
                            <div class="climate-ai-bridge-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke-linecap="round"/>
                                </svg>
                            </div>
                            <div class="climate-ai-bridge-content">
                                <strong>Looking to analyze wildfire risk?</strong>
                                <p>Access the dedicated AI Prediction module to fuse this weather data with NASA FIRMS satellite and XGBoost models.</p>
                                <a :href="`/ai-prediction?lat=${activeCoordinates?.lat || -0.7}&lon=${activeCoordinates?.lon || 113.9}`" class="climate-ai-btn">
                                    Open AI Prediction &rarr;
                                </a>
                            </div>
                        </div>
                    </article>
                </section>

                <section class="panel table-panel">
                    <div class="panel-header table-panel-header">
                        <div>
                            <div class="panel-eyebrow">OBSERVATION RECORDS</div>
                            <h2>Daily weather history</h2>
                            <p>Historical daily weather records for {{ selectedProvince }}.</p>
                        </div>
                        <span class="record-count">{{ visibleData.length }} records</span>
                    </div>

                    <div class="table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Avg Temp</th>
                                    <th>Max Temp</th>
                                    <th>Min Temp</th>
                                    <th>Humidity</th>
                                    <th>Rainfall</th>
                                    <th>Wind</th>
                                    <th>Condition</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr v-if="loadingWeather && !visibleData.length">
                                    <td colspan="8" class="table-message">Loading weather data...</td>
                                </tr>

                                <tr v-else-if="!visibleData.length">
                                    <td colspan="8" class="table-message">
                                        No data available to display.
                                    </td>
                                </tr>

                                <tr
                                    v-for="record in [...visibleData].reverse()"
                                    :key="record.date"
                                >
                                    <td class="date-cell">{{ formatFullDate(record.date) }}</td>
                                    <td>{{ formatNumber(record.temperature) }} °C</td>
                                    <td>{{ formatNumber(record.temperatureMax) }} °C</td>
                                    <td>{{ formatNumber(record.temperatureMin) }} °C</td>
                                    <td>{{ formatNumber(record.humidity) }}%</td>
                                    <td>{{ formatNumber(record.rainfall) }} mm</td>
                                    <td>{{ formatNumber(record.wind) }} km/h</td>
                                    <td>
                                        <span class="condition-badge" :class="`condition-${getWeatherClass(record)}`">
                                            {{ getWeatherCondition(record) }}
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-footer">
                        <span>
                            {{ selectedProvince }} · Daily observation data
                        </span>
                        <span>{{ visibleData.length }} of {{ weatherData.length }} records</span>
                    </div>
                </section>

                <footer class="page-footer">
                    <span>© {{ new Date().getFullYear() }} NusaFire</span>
                    <span>Environmental Monitoring &amp; Fire Risk Analysis</span>
                </footer>
            </div>
        </main>
    </div>
</template>

<style scoped>
.weather-page {
    --page-bg: #f5f7f6;
    --card-bg: #fff;
    --text-main: #20352d;
    --text-secondary: #7c8c84;
    --border-color: #e7ede9;
    --green: #278d68;
    --green-dark: #1e7253;
    --green-soft: #eaf6ef;
    --shadow: 0 5px 22px rgba(31, 65, 48, .035);
    min-height: 100vh;
    width: 100%;
    background: var(--page-bg);
    color: var(--text-main);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    transition: background .2s, color .2s;
}

.weather-page.dark-mode {
    --page-bg: #101a16;
    --card-bg: #18251f;
    --text-main: #e4eee8;
    --text-secondary: #94a89b;
    --border-color: #2b3b32;
    --green: #55c392;
    --green-dark: #6bd3a4;
    --green-soft: #203a2d;
    --shadow: 0 5px 22px rgba(0, 0, 0, .12);
}

.weather-main {
    width: auto;
    min-width: 0;
    min-height: 100vh;
    margin-left: 268px;
    transition: margin-left .25s ease;
}

.weather-main.weather-main-collapsed {
    margin-left: 82px;
}

.topbar {
    position: sticky;
    top: 0;
    z-index: 50;
    height: 68px;
    min-height: 68px;
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    background: #ffffff;
    background: var(--card-bg, #ffffff);
    border-bottom: 1px solid #e5eae4;
    border-bottom: 1px solid var(--border-color, #e5eae4);
}

.weather-page.dark-mode .topbar {
    background: #1d2721;
    background: var(--card-bg, #1d2721);
    border-bottom: 1px solid #2b3b32;
    border-bottom: 1px solid var(--border-color, #2b3b32);
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.topbar-left h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 750;
    color: var(--text-main);
    letter-spacing: -0.01em;
}

.topbar-actions {
    display: flex;
    align-items: center;
    gap: 14px;
}

.connection-dot,
.source-dot {
    width: 7px;
    height: 7px;
    flex-shrink: 0;
    border-radius: 50%;
    background: #9aa69e;
}

.connection-dot.online {
    background: #2eae75;
}

.connection-dot.offline {
    background: #d78b53;
}

.connection-label {
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
}

.icon-button {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--card-bg);
    color: var(--text-main);
    cursor: pointer;
    transition: color .15s ease, background .15s ease, border-color .15s ease;
}

.mobile-menu-button {
    display: none;
}

.page-content {
    width: 100%;
    max-width: 1600px;
    margin: 0;
    padding: 32px;
}

.page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 28px;
}

.eyebrow,
.panel-eyebrow {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 10px;
    color: var(--green, #165b33);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    line-height: 1;
}

.eyebrow-line {
    display: inline-block;
    width: 18px;
    height: 2px;
    border-radius: 2px;
    background: var(--green, #165b33);
    flex-shrink: 0;
}

.page-heading h1 {
    margin: 0 0 8px 0;
    font-size: clamp(26px, 2.8vw, 34px);
    font-weight: 750;
    letter-spacing: -1.1px;
    line-height: 1.2;
    color: var(--text-main, #141f17);
}

.page-subtitle {
    max-width: 660px;
    margin: 0;
    color: var(--text-secondary, #5f7065);
    font-size: 13px;
    line-height: 1.6;
}

.heading-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
}

.heading-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    min-height: 52px;
    background: #ffffff;
    background: var(--card-bg, #ffffff);
    border: 1px solid #e5eae4;
    border: 1px solid var(--border-color, #e5eae4);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    white-space: nowrap;
}

.heading-card-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    min-width: 34px;
    min-height: 34px;
    flex-shrink: 0;
    color: var(--green, #165b33);
    background: #e8f5e9;
    border-radius: 8px;
    line-height: 0;
    box-sizing: border-box;
    padding: 0;
}

.heading-card-icon svg {
    display: block;
    width: 18px;
    height: 18px;
    margin: auto;
    flex-shrink: 0;
}

.weather-page.dark-mode .heading-card-icon {
    background: rgba(52, 211, 153, 0.15);
    color: #34d399;
}

.heading-card strong {
    display: block;
    font-size: 12px;
    font-weight: 700;
    color: var(--text-main, #141f17);
    line-height: 1.3;
}

.heading-card > div > span {
    display: block;
    font-size: 11px;
    color: var(--text-secondary, #5f7065);
    line-height: 1.4;
}

.refresh-button {
    height: 52px;
    min-height: 52px;
    padding: 0 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    border: 1px solid #d7e7dd;
    border: 1px solid var(--border-color, #d7e7dd);
    border-radius: 12px;
    background: var(--card-bg, #ffffff);
    color: var(--green-dark, #165b33);
    font: inherit;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, border-color 0.15s;
}

.refresh-button:hover:not(:disabled) {
    background: #f0f7f3;
    border-color: var(--green, #165b33);
}

.spin-anim {
    animation: nf-spin 1s linear infinite;
}

@keyframes nf-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.refresh-button:disabled {
    cursor: wait;
    opacity: .6;
}

.source-banner {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    margin-bottom: 18px;
    border: 1px solid #d9ebe0;
    border-radius: 12px;
    background: linear-gradient(105deg, #edf8f1, #f9fcfa);
}

.dark-mode .source-banner {
    background: #1b3025;
    border-color: #2d4b3a;
}

.source-icon {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: #dcefe3;
    color: #267e59;
    line-height: 0;
}

.source-icon svg {
    display: block;
    margin: auto;
}

.dark-mode .source-icon {
    background: #284735;
    color: #80d4a6;
}

.source-copy {
    flex: 1;
    min-width: 0;
}

.source-copy strong {
    font-size: 12px;
    font-weight: 750;
}

.condition-highlight {
    color: var(--green-dark);
}

.source-copy p {
    margin: 4px 0;
    color: #6d8275;
    font-size: 11px;
    line-height: 1.6;
}

.dark-mode .source-copy p {
    color: var(--text-secondary);
}

.source-copy small {
    color: var(--text-secondary);
    font-size: 10px;
}

.source-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 10px;
    border: 1px solid #dce9df;
    border-radius: 30px;
    background: rgba(255, 255, 255, .75);
    color: #4e7960;
    font-size: 10px;
    white-space: nowrap;
}

.dark-mode .source-badge {
    background: #20372a;
    border-color: #355342;
    color: #9bd4af;
}

.source-dot {
    background: #32a96f;
}

.filter-card,
.stat-card,
.panel {
    border: 1px solid var(--border-color);
    border-radius: 13px;
    background: var(--card-bg);
    box-shadow: var(--shadow);
}

.filter-card {
    padding: 20px 22px 18px;
    margin-bottom: 18px;
}

.section-heading,
.panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
}

.section-heading {
    margin-bottom: 16px;
}

.section-heading h2,
.panel-header h2 {
    margin: 0;
    color: var(--text-main);
    font-size: 14px;
    font-weight: 750;
}

.section-heading p,
.panel-header p {
    margin: 5px 0 0;
    color: var(--text-secondary);
    font-size: 11px;
    line-height: 1.6;
}

.filter-symbol,
.panel-icon {
    width: 34px;
    height: 34px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: var(--green-soft);
    color: var(--green);
    line-height: 0;
}

.filter-symbol svg,
.panel-icon svg {
    display: block;
    margin: auto;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr)) auto;
    gap: 16px;
    align-items: flex-end;
}

.filter-action-wrap {
    display: flex;
    align-items: flex-end;
}

.filter-submit-btn {
    height: 41px;
    padding: 0 20px;
    white-space: nowrap;
}

.field {
    display: flex;
    flex-direction: column;
    gap: 7px;
    min-width: 0;
}

.field > span {
    color: var(--text-main);
    font-size: 11px;
    font-weight: 700;
}

.field select,
.field input {
    width: 100%;
    min-width: 0;
    height: 41px;
    padding: 0 12px;
    border: 1px solid var(--border-color);
    border-radius: 9px;
    outline: none;
    background: var(--card-bg);
    color: var(--text-main);
    font: inherit;
    font-size: 12px;
    transition: border-color .15s ease, box-shadow .15s ease;
}

.field select:focus,
.field input:focus {
    border-color: var(--green);
    box-shadow: 0 0 0 3px rgba(39, 141, 104, .1);
}

.location-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    padding: 9px 12px;
    border-radius: 8px;
    background: var(--page-bg);
    color: var(--text-secondary);
    font-size: 11px;
}

.location-pin {
    color: var(--green);
    font-size: 15px;
    line-height: 1;
}

.location-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}

.location-summary strong {
    color: var(--text-main);
    font-weight: 700;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 18px;
}

.stat-card {
    position: relative;
    min-width: 0;
    overflow: hidden;
    padding: 19px 19px 21px;
}

.stat-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 600;
}

.stat-icon {
    width: 33px;
    height: 33px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    line-height: 0;
}

.stat-icon svg {
    display: block;
    margin: auto;
}

.temperature-icon {
    background: #fff0e6;
    color: #d9864b;
}

.humidity-icon {
    background: #e8f2ff;
    color: #508ed0;
}

.rainfall-icon {
    background: #e7f4ff;
    color: #478ebc;
}

.wind-icon {
    background: #f0eaff;
    color: #9275ce;
}

.stat-value {
    margin-top: 20px;
    color: var(--text-main);
    font-size: clamp(23px, 2.4vw, 30px);
    font-weight: 780;
    letter-spacing: -1px;
    white-space: nowrap;
}

.stat-value > span {
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0;
}

.stat-description {
    margin-top: 8px;
    color: var(--text-secondary);
    font-size: 10px;
    line-height: 1.5;
}

.stat-accent {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 3px;
    opacity: .8;
}

.temperature-accent { background: #df9a64; }
.humidity-accent { background: #679fdd; }
.rainfall-accent { background: #5d9dc5; }
.wind-accent { background: #a38cda; }

/* Weather condition stat card */
.condition-icon {
    background: #e8f5ed;
    color: #267e59;
}

.weather-page.dark-mode .condition-icon {
    background: #1b3827;
    color: #6dd4a4;
}

/* Condition value: use smaller font so longer text fits cleanly */
.condition-stat-value {
    margin-top: 14px;
    font-size: clamp(14px, 1.6vw, 18px) !important;
    font-weight: 720;
    letter-spacing: -0.3px;
    white-space: normal;
    line-height: 1.25;
    color: var(--text-main);
}

.condition-accent { background: #3dba80; }

.content-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
    gap: 18px;
    margin-bottom: 18px;
    align-items: stretch;
}

.panel {
    min-width: 0;
    padding: 22px;
}

.panel-eyebrow {
    margin-bottom: 8px;
    font-size: 8px;
}

.panel-header h2 {
    font-size: 15px;
}

.panel-header p {
    font-size: 10px;
}

.chart-panel-header {
    align-items: center;
    flex-wrap: wrap;
}

.chart-metric-switch {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--border-color);
    border-radius: 9px;
    background: var(--page-bg);
}

.metric-pill {
    padding: 6px 10px;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: var(--text-secondary);
    font: inherit;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    transition: background .15s ease, color .15s ease;
}

.metric-pill:hover {
    color: var(--text-main);
}

.metric-pill.active {
    background: var(--card-bg);
    color: var(--green-dark);
    box-shadow: 0 1px 4px rgba(0, 0, 0, .07);
}

.chart-legend {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 20px;
    color: var(--text-secondary);
    font-size: 10px;
}

.legend-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #35a879;
}

.legend-period {
    margin-left: auto;
    font-size: 9px;
    text-align: right;
}

.chart-wrap {
    display: grid;
    grid-template-columns: 35px minmax(0, 1fr);
    grid-template-rows: 190px 25px;
    gap: 0 8px;
    margin-top: 16px;
}

.chart-y-labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    color: var(--text-secondary);
    font-size: 9px;
    text-align: right;
}

.chart-visual {
    position: relative;
    min-width: 0;
    height: 190px;
}

.chart-grid-lines {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.chart-grid-lines span {
    display: block;
    width: 100%;
    border-top: 1px dashed var(--border-color);
}

.weather-chart {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
}

.chart-x-labels {
    grid-column: 2;
    display: flex;
    justify-content: space-between;
    gap: 4px;
    padding-top: 10px;
    color: var(--text-secondary);
    font-size: 9px;
}

.chart-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
    padding-top: 16px;
    margin-top: 14px;
    border-top: 1px solid var(--border-color);
}

.chart-summary > div {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.chart-summary span {
    color: var(--text-secondary);
    font-size: 10px;
}

.chart-summary strong {
    color: var(--text-main);
    font-size: 12px;
}

.empty-chart {
    min-height: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 9px;
    color: var(--text-secondary);
    text-align: center;
}

.empty-chart > span {
    color: var(--green);
    font-size: 30px;
}

.empty-chart strong {
    color: var(--text-main);
    font-size: 12px;
}

.empty-chart p {
    margin: 0;
    font-size: 10px;
}

.risk-panel-icon {
    background: #fff2e7;
    color: #d18b4f;
}

.dark-mode .risk-panel-icon {
    background: #3a2d20;
    color: #e8ad74;
}

.risk-result {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 18px 15px;
    margin-top: 20px;
    border: 1px solid var(--border-color);
    border-radius: 11px;
    background: var(--page-bg);
}

.risk-high {
    background: #fff5ee;
    border-color: #f4d9c4;
}

.dark-mode .risk-high {
    background: #34251f;
    border-color: #5c3d2d;
}

.risk-moderate {
    background: #fffbeb;
    border-color: #fde68a;
}

.dark-mode .risk-moderate {
    background: #332b18;
    border-color: #5c4b23;
}

.risk-low {
    background: #edf8f1;
    border-color: #d6ebde;
}

.dark-mode .risk-low {
    background: #20352a;
    border-color: #355743;
}

.risk-gauge {
    width: 49px;
    height: 49px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border-color);
    border-radius: 50%;
    background: var(--card-bg);
    color: var(--text-secondary);
    font-size: 24px;
    font-weight: 800;
}

.risk-high .risk-gauge {
    color: #c66b3e;
    border-color: #efd2bd;
}

.risk-moderate .risk-gauge {
    color: #b7791f;
    border-color: #f6e05e;
}

.risk-low .risk-gauge {
    color: #278d68;
    border-color: #d4e9dc;
}

.risk-result-copy {
    min-width: 0;
}

.risk-caption {
    display: block;
    margin-bottom: 5px;
    color: var(--text-secondary);
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1px;
}

.risk-result-copy > strong {
    color: var(--text-main);
    font-size: 16px;
}

.risk-high .risk-result-copy > strong {
    color: #bb673c;
}

.risk-moderate .risk-result-copy > strong {
    color: #b7791f;
}

.risk-low .risk-result-copy > strong {
    color: #278d68;
}

.risk-result-copy p {
    margin: 6px 0 0;
    color: var(--text-secondary);
    font-size: 10px;
    line-height: 1.7;
}

.probability-section {
    margin-top: 20px;
}

.probability-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    color: var(--text-secondary);
    font-size: 10px;
}

.probability-heading strong {
    color: var(--text-main);
    font-size: 13px;
}

.probability-track {
    height: 7px;
    overflow: hidden;
    margin-top: 10px;
    border-radius: 20px;
    background: var(--border-color);
}

.probability-fill {
    height: 100%;
    border-radius: inherit;
    background: #d18b4f;
    transition: width .3s ease;
}

.probability-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    color: var(--text-secondary);
    font-size: 9px;
}

.risk-input-summary {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    padding: 15px 0;
    margin-top: 13px;
    border-top: 1px solid var(--border-color);
}

.risk-input-summary > div {
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 0;
}

.risk-input-summary span {
    color: var(--text-secondary);
    font-size: 10px;
}

.risk-input-summary strong {
    color: var(--text-main);
    font-size: 10px;
    overflow-wrap: anywhere;
}

.prediction-button {
    width: 100%;
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    padding: 9px 14px;
    border: 0;
    border-radius: 9px;
    background: #278d68;
    color: #fff;
    font: inherit;
    font-size: 11px;
    font-weight: 750;
    cursor: pointer;
    transition: background .2s, opacity .2s;
}

.prediction-button:hover:not(:disabled) {
    opacity: .92;
}

.prediction-button:disabled {
    cursor: not-allowed;
    opacity: .5;
}

.prediction-error {
    padding: 10px;
    margin: 10px 0 0;
    border-radius: 8px;
    background: #fff0ed;
    color: #b64f3c;
    font-size: 10px;
    line-height: 1.6;
}

.dark-mode .prediction-error {
    background: #3a2522;
    color: #ffb5a4;
}

.model-note {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    padding: 11px;
    margin-top: 13px;
    border-radius: 8px;
    background: var(--page-bg);
    color: var(--text-secondary);
}

.model-note > span {
    flex-shrink: 0;
    color: var(--green);
    font-size: 14px;
}

.model-note p {
    margin: 0;
    font-size: 9px;
    line-height: 1.7;
}

.table-panel {
    padding-bottom: 0;
}

.table-panel-header {
    align-items: center;
    margin-bottom: 20px;
}

.record-count {
    padding: 7px 10px;
    border: 1px solid var(--border-color);
    border-radius: 7px;
    color: var(--text-secondary);
    font-size: 10px;
    white-space: nowrap;
}

.table-scroll {
    overflow-x: auto;
    width: 100%;
}

table {
    width: 100%;
    border-collapse: collapse;
    white-space: nowrap;
    text-align: left;
}

thead {
    background: var(--page-bg);
}

th {
    padding: 12px 13px;
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 750;
}

td {
    padding: 14px 13px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-main);
    font-size: 10px;
}

tbody tr:last-child td {
    border-bottom: 0;
}

tbody tr:hover {
    background: var(--page-bg);
}

.date-cell {
    font-weight: 700;
}

.condition-badge {
    display: inline-flex;
    align-items: center;
    padding: 5px 8px;
    border-radius: 20px;
    font-size: 9px;
    font-weight: 700;
}

.condition-rain,
.condition-storm {
    background: #e8f2ff;
    color: #437dbb;
}

.condition-clear {
    background: #fff0e4;
    color: #bd743b;
}

.condition-partly {
    background: #edf7ef;
    color: #3c8860;
}

.condition-cloud {
    background: #edf2f7;
    color: #667f91;
}

.table-message {
    padding: 35px 15px;
    color: var(--text-secondary);
    text-align: center;
}

.table-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding: 15px 0;
    margin-top: 3px;
    border-top: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 9px;
}

.page-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    padding: 22px 0 4px;
    color: var(--text-secondary);
    font-size: 9px;
}

.error-banner {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 15px;
    margin-bottom: 18px;
    border: 1px solid #efd2c9;
    border-radius: 10px;
    background: #fff5f1;
    color: #a84c37;
}

.error-icon {
    width: 23px;
    height: 23px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid currentColor;
    border-radius: 50%;
    font-weight: 800;
}

.text-button {
    padding: 0;
    border: 0;
    background: transparent;
    color: inherit;
    font: inherit;
    font-size: 10px;
    font-weight: 800;
    text-decoration: underline;
    cursor: pointer;
}

.loading-card {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 20px;
    margin-bottom: 18px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--card-bg);
}

.loading-spinner {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
    border: 2px solid var(--border-color);
    border-top-color: var(--green);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 1250px) and (min-width: 901px) {
    .stats-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .content-grid {
        grid-template-columns: minmax(0, 1fr);
    }
}

@media (max-width: 900px) {
    .weather-main,
    .weather-main.weather-main-collapsed {
        width: 100%;
        margin-left: 0;
    }

    .mobile-menu-button {
        display: inline-flex;
    }

    .page-heading {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
    }

    .heading-actions {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
    }

    .filter-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .content-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 600px) {
    .stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
<style scoped>

/* Climate Extremes & Summary Panel */
.climate-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 18px;
}

.climate-stat-card {
    padding: 14px;
    border-radius: 12px;
    background: var(--page-bg);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.climate-stat-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
}

.climate-stat-val {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-color);
}

.climate-stat-card small {
    font-size: 11px;
    color: var(--text-muted);
}

.climate-ai-bridge {
    margin-top: 20px;
    padding: 16px;
    border-radius: 12px;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.25);
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.climate-ai-bridge-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #10b981;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.climate-ai-bridge-content {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.climate-ai-bridge-content strong {
    font-size: 13px;
    color: var(--text-color);
}

.climate-ai-bridge-content p {
    font-size: 12px;
    line-height: 1.45;
    color: var(--text-muted);
    margin: 0;
}

.climate-ai-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
    font-size: 12px;
    font-weight: 600;
    color: #059669;
    text-decoration: none;
}

.climate-ai-btn:hover {
    text-decoration: underline;
}

</style>
