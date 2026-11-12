
<script setup lang="ts">
import { ref, computed } from 'vue';
import { Head } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type WeatherRecord = {
    date: string;
    temperature: number;
    humidity: number;
    rainfall: number;
    wind: number;
};

type MetricKey = 'temperature' | 'humidity' | 'rainfall' | 'wind';

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const selectedPeriod = ref('7');
const selectedMetric = ref<MetricKey>('temperature');

// Data ini hanya untuk demonstrasi antarmuka.
// Ganti dengan data API NASA POWER saat integrasi backend dilakukan.
const weatherData: WeatherRecord[] = [
    { date: '2026-11-03', temperature: 31.2, humidity: 72, rainfall: 3.2, wind: 8.4 },
    { date: '2026-11-04', temperature: 30.6, humidity: 75, rainfall: 5.8, wind: 7.6 },
    { date: '2026-11-05', temperature: 32.1, humidity: 68, rainfall: 0.4, wind: 9.2 },
    { date: '2026-11-06', temperature: 33.4, humidity: 63, rainfall: 0, wind: 10.1 },
    { date: '2026-11-07', temperature: 32.8, humidity: 66, rainfall: 0.2, wind: 8.8 },
    { date: '2026-11-08', temperature: 31.5, humidity: 71, rainfall: 8.6, wind: 7.2 },
    { date: '2026-11-09', temperature: 30.9, humidity: 78, rainfall: 12.4, wind: 6.5 },
    { date: '2026-11-10', temperature: 31.8, humidity: 70, rainfall: 1.2, wind: 8.1 },
    { date: '2026-11-11', temperature: 33.1, humidity: 64, rainfall: 0, wind: 9.8 },
    { date: '2026-11-12', temperature: 32.6, humidity: 67, rainfall: 0.1, wind: 9.1 },
];

const availablePeriods = [
    { value: '7', label: '7 hari terakhir' },
    { value: '10', label: '10 hari tersedia' },
];

const metrics: { value: MetricKey; label: string; unit: string }[] = [
    { value: 'temperature', label: 'Suhu', unit: '°C' },
    { value: 'humidity', label: 'Kelembapan', unit: '%' },
    { value: 'rainfall', label: 'Curah hujan', unit: 'mm' },
    { value: 'wind', label: 'Kecepatan angin', unit: 'km/j' },
];

const visibleData = computed(() => {
    if (selectedPeriod.value === '7') {
        return weatherData.slice(-7);
    }

    return weatherData;
});

const latest = computed<WeatherRecord | null>(
    () => visibleData.value.at(-1) ?? null,
);

function average(key: 'temperature' | 'humidity' | 'wind'): number {
    const records = visibleData.value;

    if (records.length === 0) return 0;

    return records.reduce((sum, item) => sum + item[key], 0) / records.length;
}

const averageTemperature = computed(() => average('temperature'));
const averageHumidity = computed(() => average('humidity'));
const averageWind = computed(() => average('wind'));

const totalRainfall = computed(() =>
    visibleData.value.reduce((sum, item) => sum + item.rainfall, 0),
);

const activeMetric = computed(
    () => metrics.find((item) => item.value === selectedMetric.value) ?? metrics[0],
);

const chartValues = computed(() =>
    visibleData.value.map((item) => ({
        date: item.date,
        label: formatDate(item.date),
        value: item[selectedMetric.value],
    })),
);

const chartMaximum = computed(() => {
    const values = chartValues.value.map((item) => item.value);
    const maximum = Math.max(...values, 1);

    // Sedikit ruang di atas nilai maksimum supaya grafik tidak menempel
    // pada batas atas area grafik.
    return maximum * 1.2;
});

const chartPoints = computed(() => {
    const values = chartValues.value;

    if (values.length === 0) return '';

    return values
        .map((item, index) => {
            const x = values.length === 1
                ? 50
                : (index / (values.length - 1)) * 100;

            const y = 100 - (item.value / chartMaximum.value) * 88;

            return `${x},${y}`;
        })
        .join(' ');
});

const chartAreaPoints = computed(() => {
    if (!chartPoints.value) return '';

    return `0,100 ${chartPoints.value} 100,100`;
});

const fireRisk = computed(() => {
    if (!latest.value) {
        return {
            label: 'Tidak tersedia',
            color: 'low',
            description: 'Belum ada data yang dapat dianalisis.',
        };
    }

    const record = latest.value;

    if (
        record.temperature >= 33 &&
        record.humidity < 65 &&
        record.rainfall < 1
    ) {
        return {
            label: 'Tinggi',
            color: 'high',
            description:
                'Data contoh memenuhi kriteria sederhana untuk pemantauan lebih lanjut. Hasil ini bukan peringatan kebakaran resmi.',
        };
    }

    if (
        record.temperature >= 31 &&
        record.humidity < 75 &&
        record.rainfall < 3
    ) {
        return {
            label: 'Sedang',
            color: 'medium',
            description:
                'Data contoh menunjukkan kondisi yang perlu dipantau. Penilaian ini belum memperhitungkan seluruh faktor kebakaran.',
        };
    }

    return {
        label: 'Rendah',
        color: 'low',
        description:
            'Berdasarkan aturan sederhana pada data contoh, kondisi masuk kategori rendah. Ini bukan jaminan bebas risiko kebakaran.',
    };
});

const periodLabel = computed(() => {
    if (visibleData.value.length === 0) return 'Tidak ada data';

    const first = visibleData.value[0];
    const last = visibleData.value[visibleData.value.length - 1];

    return `${formatDate(first.date)} – ${formatDate(last.date)} 2026`;
});

function formatNumber(value: number, decimals = 1): string {
    return value.toLocaleString('id-ID', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}

function formatDate(date: string): string {
    const parsedDate = new Date(`${date}T00:00:00`);

    return parsedDate.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
    });
}

function getWeatherCondition(item: WeatherRecord): string {
    if (item.rainfall >= 5) return 'Hujan';
    if (item.temperature >= 33) return 'Panas';
    return 'Berawan';
}

function getWeatherClass(item: WeatherRecord): string {
    if (item.rainfall >= 5) return 'badge-rain';
    if (item.temperature >= 33) return 'badge-hot';
    return 'badge-normal';
}


</script>

<template>
    <Head title="Weather Analysis - NusaFire" />

    <div class="nf-app weather-page" :class="`theme-${theme}`">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
            <header class="topbar">
                <div class="topbar-left">
                    <button
                        type="button"
                        class="icon-button mobile-menu"
                        :class="{ 'menu-visible': sidebarCollapsed }"
                        aria-label="Buka navigasi"
                        @click="sidebarCollapsed = false; mobileMenuOpen = true"
                    >
                        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                            <path
                                d="M4 6h16M4 12h16M4 18h16"
                                stroke="currentColor"
                                stroke-width="1.8"
                                stroke-linecap="round"
                            />
                        </svg>
                    </button>

                    <div>
                        <div class="breadcrumb">
                            <span>NusaFire</span>
                            <span>/</span>
                            <span>Analysis</span>
                            <span>/</span>
                            <strong>Weather Analysis</strong>
                        </div>
                        <p class="topbar-subtitle">
                            Environmental and weather monitoring
                        </p>
                    </div>
                </div>

                <button
                    class="icon-button theme-button"
                    type="button"
                    :aria-label="theme === 'dark' ? 'Aktifkan mode terang' : 'Aktifkan mode gelap'"
                    :title="theme === 'dark' ? 'Mode terang' : 'Mode gelap'"
                    @click="toggleTheme"
                >
                    <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <circle
                            cx="12"
                            cy="12"
                            r="4"
                            stroke="currentColor"
                            stroke-width="1.7"
                        />
                        <path
                            d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                        />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path
                            d="M20.2 15.2A8.6 8.6 0 0 1 8.8 3.8 8.8 8.8 0 1 0 20.2 15.2Z"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linejoin="round"
                        />
                    </svg>
                </button>
            </header>

            <div class="page-content">
                <section class="page-heading">
                    <div>
                        <div class="eyebrow">
                            <span></span>
                            ENVIRONMENTAL INTELLIGENCE
                        </div>

                        <h1>Weather <span>Analysis</span></h1>

                        <p>
                            Analisis kondisi cuaca untuk mendukung pemantauan
                            lingkungan dan mengidentifikasi kondisi yang berpotensi
                            meningkatkan risiko kebakaran.
                        </p>
                    </div>

                    <div class="period-card">
                        <span>DATA PERIOD</span>
                        <strong>{{ periodLabel }}</strong>
                        <small>Data demonstrasi</small>
                    </div>
                </section>

                <section class="filter-panel">
                    <div class="filter-heading">
                        <div class="filter-symbol" aria-hidden="true">⌕</div>
                        <div>
                            <h2>Parameter analisis</h2>
                            <p>Pilih periode dan parameter pengamatan.</p>
                        </div>
                    </div>

                    <div class="filter-grid">
                        <label>
                            <span>Wilayah analisis</span>
                            <select disabled aria-describedby="region-help">
                                <option>Belum tersedia — menunggu integrasi data</option>
                            </select>
                            <small id="region-help">
                                Filter wilayah akan aktif setelah data wilayah tersedia.
                            </small>
                        </label>

                        <label>
                            <span>Periode pengamatan</span>
                            <select v-model="selectedPeriod">
                                <option
                                    v-for="period in availablePeriods"
                                    :key="period.value"
                                    :value="period.value"
                                >
                                    {{ period.label }}
                                </option>
                            </select>
                        </label>

                        <label>
                            <span>Parameter grafik</span>
                            <select v-model="selectedMetric">
                                <option
                                    v-for="metric in metrics"
                                    :key="metric.value"
                                    :value="metric.value"
                                >
                                    {{ metric.label }}
                                </option>
                            </select>
                        </label>
                    </div>
                </section>

                <div class="data-notice" role="note">
                    <span class="notice-icon" aria-hidden="true">ⓘ</span>
                    <p>
                        <strong>Data demonstrasi:</strong> angka pada halaman ini
                        merupakan data contoh, bukan hasil pengukuran aktual.
                        Data belum terhubung ke NASA POWER atau sumber cuaca lainnya.
                        Hasilnya tidak boleh digunakan sebagai dasar peringatan
                        kebakaran nyata.
                    </p>
                </div>

                <section class="metrics-grid">
                    <article class="metric-card">
                        <div class="metric-card-top">
                            <span class="metric-icon temperature">♨</span>
                            <span class="metric-title">Suhu rata-rata</span>
                        </div>

                        <div class="metric-value">
                            {{ formatNumber(averageTemperature) }}
                            <small>°C</small>
                        </div>

                        <div class="metric-bottom">
                            <span>Nilai terakhir</span>
                            <strong>{{ latest ? formatNumber(latest.temperature) : '—' }} °C</strong>
                        </div>

                        <div class="metric-track">
                            <span
                                class="temp-track"
                                :style="{ width: `${Math.min(averageTemperature / 40 * 100, 100)}%` }"
                            ></span>
                        </div>
                    </article>

                    <article class="metric-card">
                        <div class="metric-card-top">
                            <span class="metric-icon humidity">◉</span>
                            <span class="metric-title">Kelembapan rata-rata</span>
                        </div>

                        <div class="metric-value">
                            {{ formatNumber(averageHumidity, 0) }}
                            <small>%</small>
                        </div>

                        <div class="metric-bottom">
                            <span>Nilai terakhir</span>
                            <strong>{{ latest ? latest.humidity : '—' }}%</strong>
                        </div>

                        <div class="metric-track">
                            <span
                                class="humidity-track"
                                :style="{ width: `${Math.min(averageHumidity, 100)}%` }"
                            ></span>
                        </div>
                    </article>

                    <article class="metric-card">
                        <div class="metric-card-top">
                            <span class="metric-icon rainfall">☂</span>
                            <span class="metric-title">Total curah hujan</span>
                        </div>

                        <div class="metric-value">
                            {{ formatNumber(totalRainfall) }}
                            <small>mm</small>
                        </div>

                        <div class="metric-bottom">
                            <span>Nilai terakhir</span>
                            <strong>{{ latest ? formatNumber(latest.rainfall) : '—' }} mm</strong>
                        </div>

                        <div class="metric-track">
                            <span
                                class="rain-track"
                                :style="{ width: `${Math.min(totalRainfall / 50 * 100, 100)}%` }"
                            ></span>
                        </div>
                    </article>

                    <article class="metric-card">
                        <div class="metric-card-top">
                            <span class="metric-icon wind">≋</span>
                            <span class="metric-title">Kecepatan angin rata-rata</span>
                        </div>

                        <div class="metric-value">
                            {{ formatNumber(averageWind) }}
                            <small>km/j</small>
                        </div>

                        <div class="metric-bottom">
                            <span>Nilai terakhir</span>
                            <strong>{{ latest ? formatNumber(latest.wind) : '—' }} km/j</strong>
                        </div>

                        <div class="metric-track">
                            <span
                                class="wind-track"
                                :style="{ width: `${Math.min(averageWind / 30 * 100, 100)}%` }"
                            ></span>
                        </div>
                    </article>
                </section>

                <section class="analysis-grid">
                    <article class="panel chart-panel">
                        <div class="panel-heading">
                            <div>
                                <span class="section-label">WEATHER TRENDS</span>
                                <h2>Tren {{ activeMetric.label.toLowerCase() }}</h2>
                                <p>
                                    Perubahan parameter cuaca selama periode
                                    pengamatan yang dipilih.
                                </p>
                            </div>

                            <span class="unit-badge">{{ activeMetric.unit }}</span>
                        </div>

                        <div class="chart-legend">
                            <span class="legend-dot"></span>
                            {{ activeMetric.label }}
                        </div>

                        <div v-if="chartValues.length" class="chart-container">
                            <div class="y-labels">
                                <span>{{ formatNumber(chartMaximum, 0) }}</span>
                                <span>{{ formatNumber(chartMaximum * 0.66, 0) }}</span>
                                <span>{{ formatNumber(chartMaximum * 0.33, 0) }}</span>
                                <span>0</span>
                            </div>

                            <div class="chart-main">
                                <div class="chart-grid" aria-hidden="true">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>

                                <svg
                                    class="chart-svg"
                                    viewBox="0 0 100 100"
                                    preserveAspectRatio="none"
                                    role="img"
                                    :aria-label="`Grafik ${activeMetric.label}`"
                                >
                                    <defs>
                                        <linearGradient
                                            id="weatherGradient"
                                            x1="0"
                                            y1="0"
                                            x2="0"
                                            y2="1"
                                        >
                                            <stop
                                                offset="0%"
                                                stop-color="#278d68"
                                                stop-opacity=".25"
                                            />
                                            <stop
                                                offset="100%"
                                                stop-color="#278d68"
                                                stop-opacity="0"
                                            />
                                        </linearGradient>
                                    </defs>

                                    <polygon
                                        v-if="chartValues.length > 1"
                                        :points="chartAreaPoints"
                                        fill="url(#weatherGradient)"
                                    />

                                    <polyline
                                        :points="chartPoints"
                                        fill="none"
                                        stroke="#278d68"
                                        stroke-width="1.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        vector-effect="non-scaling-stroke"
                                    />

                                    <circle
                                        v-for="(point, index) in chartValues"
                                        :key="point.date"
                                        :cx="chartValues.length === 1 ? 50 : index / (chartValues.length - 1) * 100"
                                        :cy="100 - point.value / chartMaximum * 88"
                                        r="1.4"
                                        fill="#278d68"
                                        stroke="var(--panel)"
                                        stroke-width=".5"
                                        vector-effect="non-scaling-stroke"
                                    />
                                </svg>

                                <div class="x-labels">
                                    <span
                                        v-for="point in chartValues"
                                        :key="point.date"
                                    >
                                        {{ point.label }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div v-else class="empty-state">
                            Belum ada data untuk ditampilkan.
                        </div>

                        <div class="chart-footer">
                            <div>
                                <span>Nilai terakhir</span>
                                <strong>
                                    {{ chartValues.length ? formatNumber(chartValues[chartValues.length - 1].value) : '—' }}
                                    {{ activeMetric.unit }}
                                </strong>
                            </div>

                            <div>
                                <span>Jumlah pengamatan</span>
                                <strong>{{ chartValues.length }} hari</strong>
                            </div>
                        </div>
                    </article>

                    <article class="panel risk-panel">
                        <div class="panel-heading">
                            <div>
                                <span class="section-label">FIRE WEATHER INDICATOR</span>
                                <h2>Indikator cuaca</h2>
                                <p>Ringkasan aturan sederhana dari data demonstrasi.</p>
                            </div>

                            <span class="fire-symbol">♨</span>
                        </div>

                        <div class="risk-display">
                            <div class="risk-ring" :class="`risk-${fireRisk.color}`">
                                <div class="risk-ring-inner">
                                    <span>Indikator contoh</span>
                                    <strong>{{ fireRisk.label }}</strong>
                                </div>
                            </div>
                        </div>

                        <div
                            class="risk-message"
                            :class="`risk-message-${fireRisk.color}`"
                        >
                            <span class="risk-dot"></span>
                            <div>
                                <strong>
                                    Indikator {{ fireRisk.label.toLowerCase() }}
                                </strong>
                                <p>{{ fireRisk.description }}</p>
                            </div>
                        </div>

                        <div class="risk-factors">
                            <div>
                                <span>Suhu</span>
                                <strong>{{ latest ? formatNumber(latest.temperature) : '—' }} °C</strong>
                            </div>
                            <div>
                                <span>Kelembapan</span>
                                <strong>{{ latest ? latest.humidity : '—' }}%</strong>
                            </div>
                            <div>
                                <span>Curah hujan</span>
                                <strong>{{ latest ? formatNumber(latest.rainfall) : '—' }} mm</strong>
                            </div>
                            <div>
                                <span>Kecepatan angin</span>
                                <strong>{{ latest ? formatNumber(latest.wind) : '—' }} km/j</strong>
                            </div>
                        </div>

                        <p class="disclaimer">
                            Ini bukan Fire Weather Index (FWI), bukan model prediksi,
                            dan bukan peringatan kebakaran resmi.
                        </p>
                    </article>
                </section>

                <section class="panel table-panel">
                    <div class="panel-heading table-heading">
                        <div>
                            <span class="section-label">DAILY OBSERVATIONS</span>
                            <h2>Riwayat data cuaca</h2>
                            <p>Ringkasan parameter harian dari data demonstrasi.</p>
                        </div>

                        <span class="count-badge">
                            {{ visibleData.length }} catatan
                        </span>
                    </div>

                    <div class="table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tanggal</th>
                                    <th>Suhu rata-rata</th>
                                    <th>Kelembapan</th>
                                    <th>Curah hujan</th>
                                    <th>Kecepatan angin</th>
                                    <th>Kondisi</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="item in [...visibleData].reverse()"
                                    :key="item.date"
                                >
                                    <td>
                                        <strong>
                                            {{ formatDate(item.date) }} {{ item.date.slice(0, 4) }}
                                        </strong>
                                    </td>
                                    <td>{{ formatNumber(item.temperature) }} °C</td>
                                    <td>{{ item.humidity }}%</td>
                                    <td>{{ formatNumber(item.rainfall) }} mm</td>
                                    <td>{{ formatNumber(item.wind) }} km/j</td>
                                    <td>
                                        <span
                                            class="weather-badge"
                                            :class="getWeatherClass(item)"
                                        >
                                            {{ getWeatherCondition(item) }}
                                        </span>
                                    </td>
                                </tr>

                                <tr v-if="visibleData.length === 0">
                                    <td colspan="6" class="empty-cell">
                                        Belum ada data cuaca.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-footer">
                        <span>Data demonstrasi · Belum terhubung ke API cuaca.</span>
                        <span>Wilayah aktual belum ditentukan.</span>
                    </div>
                </section>

                <footer class="page-footer">
                    <span>NusaFire · Environmental Monitoring</span>
                    <span>Weather Analysis</span>
                </footer>
            </div>
        </main>
    </div>
</template>

<style scoped>
/* nf-app provides --db-* variables consumed by AppSidebar */
.nf-app.weather-page {
    --db-bg: #f5f7f4;
    --db-surface: #fff;
    --db-surface-soft: #f8faf7;
    --db-text: #1c2922;
    --db-text-soft: #526158;
    --db-muted: #859087;
    --db-border: #e5eae4;
    --db-accent: #2d8a5b;
    --db-accent-soft: #e8f5ec;
    --db-shadow: 0 4px 20px rgb(23 49 33 / 3%);

    /* Local aliases used throughout this page's own styles */
    --page-bg: var(--db-bg);
    --panel: var(--db-surface);
    --panel-soft: var(--db-surface-soft);
    --text: var(--db-text);
    --muted: var(--db-muted);
    --border: var(--db-border);
    --accent: var(--db-accent);
    --accent-soft: var(--db-accent-soft);

    min-height: 100vh;
    color: var(--text);
    background: var(--page-bg);
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    font-size: 13px;
    transition: background .2s ease, color .2s ease;
}

.nf-app.weather-page.theme-dark {
    --db-bg: #111914;
    --db-surface: #19231c;
    --db-surface-soft: #1d2921;
    --db-text: #edf4ed;
    --db-text-soft: #b0bdb2;
    --db-muted: #849489;
    --db-border: #2b3a2e;
    --db-accent: #70cf98;
    --db-accent-soft: #213b2b;
    --db-shadow: 0 4px 20px rgb(0 0 0 / 10%);
}

.nf-app.weather-page,
.nf-app.weather-page *,
.nf-app.weather-page *::before,
.nf-app.weather-page *::after {
    box-sizing: border-box;
}

.main-content {
    min-height: 100vh;
    margin-left: 252px;
    transition: margin-left .3s cubic-bezier(.4,0,.2,1);
}

.main-content.sidebar-collapsed {
    margin-left: 0;
}

.topbar {
    min-height: 82px;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 1px solid var(--border);
    background: var(--panel);
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 13px;
    min-width: 0;
}

.breadcrumb {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    color: var(--muted);
    font-size: 12px;
}

.breadcrumb strong {
    color: var(--text);
}

.topbar-subtitle {
    margin: 6px 0 0;
    color: var(--muted);
    font-size: 11px;
}

.icon-button {
    display: grid;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    place-items: center;
    color: var(--text);
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s ease, border-color .2s ease;
}

.icon-button:hover {
    background: var(--panel-soft);
    border-color: var(--accent);
}

.icon-button svg {
    width: 19px;
    height: 19px;
}

.mobile-menu {
    display: none;
}

.mobile-menu.menu-visible {
    display: grid;
}

.page-content {
    width: 100%;
    max-width: 1600px;
    padding: 30px 32px 22px;
    margin: 0 auto;
}

.page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 22px;
    margin-bottom: 25px;
}

.eyebrow,
.section-label {
    color: var(--accent);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.eyebrow {
    display: flex;
    align-items: center;
    gap: 8px;
}

.eyebrow > span {
    width: 18px;
    height: 2px;
    background: var(--accent);
    border-radius: 2px;
}

.page-heading h1 {
    margin: 11px 0 8px;
    font-size: clamp(28px, 3vw, 37px);
    font-weight: 760;
    line-height: 1.15;
    letter-spacing: -1.2px;
}

.page-heading h1 > span {
    color: var(--accent);
}

.page-heading p {
    max-width: 640px;
    margin: 0;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
}

.period-card {
    display: flex;
    min-width: 195px;
    flex-direction: column;
    gap: 7px;
    padding: 14px 16px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--panel);
}

.period-card > span {
    color: var(--muted);
    font-size: 9px;
    font-weight: 750;
    letter-spacing: 1px;
}

.period-card strong {
    font-size: 12px;
}

.period-card small {
    color: #bd8a3b;
    font-size: 10px;
}

.filter-panel,
.panel,
.metric-card {
    min-width: 0;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 13px;
    box-shadow: 0 4px 18px rgb(23 43 53 / 3%);
}

.filter-panel {
    padding: 19px 21px;
    margin-bottom: 16px;
}

.filter-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 17px;
}

.filter-symbol {
    display: grid;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    place-items: center;
    color: var(--accent);
    background: var(--accent-soft);
    border-radius: 10px;
    font-size: 25px;
}

.filter-heading h2,
.panel-heading h2 {
    margin: 0;
    font-size: 14px;
    font-weight: 750;
}

.filter-heading p,
.panel-heading p {
    margin: 5px 0 0;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.5;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
}

.filter-grid label {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 7px;
    color: var(--muted);
    font-size: 11px;
    font-weight: 600;
}

.filter-grid label small {
    color: var(--muted);
    font-size: 10px;
    font-weight: 400;
    line-height: 1.5;
}

.filter-grid select {
    width: 100%;
    min-height: 41px;
    padding: 0 12px;
    color: var(--text);
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 8px;
    outline: none;
    font: inherit;
}

.filter-grid select:focus {
    border-color: var(--accent);
}

.filter-grid select:disabled {
    cursor: not-allowed;
    opacity: .75;
}

.data-notice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    margin-bottom: 17px;
    color: #82632a;
    background: #fff8e9;
    border: 1px solid #ead9b1;
    border-radius: 9px;
    font-size: 11px;
    line-height: 1.6;
}

.nf-app.theme-dark .data-notice {
    color: #d4c27a;
    background: #272619;
    border-color: #4a4522;
}

.notice-icon {
    flex: 0 0 auto;
    font-size: 17px;
}

.data-notice p {
    margin: 0;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 17px;
}

.metric-card {
    padding: 18px;
}

.metric-card-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 19px;
}

.metric-icon {
    display: grid;
    width: 37px;
    height: 37px;
    flex: 0 0 37px;
    place-items: center;
    border-radius: 10px;
    font-size: 20px;
}

.metric-icon.temperature {
    color: #d88645;
    background: #fff0e3;
}

.metric-icon.humidity,
.metric-icon.rainfall {
    color: #388ad4;
    background: #e8f3ff;
}

.metric-icon.wind {
    color: #239e8b;
    background: #e5f7f1;
}

.nf-app.theme-dark .metric-icon.temperature {
    color: #e8a06a;
    background: #3a2b1a;
}

.nf-app.theme-dark .metric-icon.humidity,
.nf-app.theme-dark .metric-icon.rainfall {
    color: #7ab8e8;
    background: #1a2e3f;
}

.nf-app.theme-dark .metric-icon.wind {
    color: #70cf98;
    background: #1a3028;
}

.metric-title {
    color: var(--muted);
    font-size: 11px;
    font-weight: 600;
    line-height: 1.5;
}

.metric-value {
    font-size: clamp(25px, 2.3vw, 32px);
    font-weight: 760;
    letter-spacing: -1px;
    white-space: nowrap;
}

.metric-value small {
    color: var(--muted);
    font-size: 12px;
    font-weight: 550;
    letter-spacing: 0;
}

.metric-bottom {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 15px;
    font-size: 10px;
}

.metric-bottom span {
    color: var(--muted);
}

.metric-track {
    height: 4px;
    overflow: hidden;
    margin-top: 14px;
    background: var(--border);
    border-radius: 5px;
}

.metric-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
    transition: width .2s ease;
}

.temp-track {
    background: #e8a061;
}

.humidity-track {
    background: #559cdb;
}

.rain-track {
    background: #6a9bd7;
}

.wind-track {
    background: #25a78e;
}

.analysis-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.65fr) minmax(280px, .95fr);
    gap: 16px;
    margin-bottom: 17px;
}

.panel {
    padding: 21px;
}

.panel-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
}

.section-label {
    display: block;
    margin-bottom: 8px;
    font-size: 9px;
}

.panel-heading h2 {
    font-size: 15px;
}

.unit-badge,
.count-badge {
    padding: 7px 10px;
    color: var(--accent);
    background: var(--accent-soft);
    border-radius: 7px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.chart-legend {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 24px;
    color: var(--muted);
    font-size: 10px;
}

.legend-dot {
    width: 8px;
    height: 8px;
    background: #278d68;
    border-radius: 50%;
}

.chart-container {
    display: grid;
    grid-template-columns: 36px minmax(0, 1fr);
    gap: 8px;
    margin-top: 16px;
}

.y-labels {
    display: flex;
    height: 210px;
    flex-direction: column;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 23px;
    color: var(--muted);
    font-size: 9px;
}

.chart-main {
    position: relative;
    height: 210px;
    min-width: 0;
    margin-bottom: 23px;
}

.chart-grid {
    position: absolute;
    inset: 0 0 23px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.chart-grid span {
    border-top: 1px dashed var(--border);
}

.chart-svg {
    position: absolute;
    inset: 0 0 23px;
    width: 100%;
    height: calc(100% - 23px);
    overflow: visible;
}

.x-labels {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: space-between;
    gap: 4px;
    color: var(--muted);
    font-size: 9px;
}

.x-labels span {
    text-align: center;
    white-space: nowrap;
}

.chart-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 28px;
    padding-top: 16px;
    margin-top: 6px;
    border-top: 1px solid var(--border);
}

.chart-footer > div {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.chart-footer span {
    color: var(--muted);
    font-size: 10px;
}

.chart-footer strong {
    font-size: 13px;
}

.empty-state {
    display: grid;
    min-height: 210px;
    place-items: center;
    color: var(--muted);
    font-size: 12px;
}

.fire-symbol {
    display: grid;
    width: 39px;
    height: 39px;
    flex: 0 0 39px;
    place-items: center;
    color: #df9950;
    background: #fff1dd;
    border-radius: 10px;
    font-size: 23px;
}

.nf-app.theme-dark .fire-symbol {
    color: #e8a06a;
    background: #3a2b1a;
}

.risk-display {
    display: grid;
    place-items: center;
    padding: 25px 0 21px;
}

.risk-ring {
    position: relative;
    display: grid;
    width: 142px;
    height: 142px;
    place-items: center;
    background: conic-gradient(#36aa89 0 40%, var(--border) 40% 100%);
    border-radius: 50%;
}

.risk-ring::before {
    position: absolute;
    inset: 9px;
    content: "";
    background: var(--panel);
    border-radius: 50%;
}

.risk-ring.risk-high {
    background: conic-gradient(#df6b58 0 85%, var(--border) 85% 100%);
}

.risk-ring.risk-medium {
    background: conic-gradient(#e7ad55 0 65%, var(--border) 65% 100%);
}

.risk-ring-inner {
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    text-align: center;
}

.risk-ring-inner span {
    color: var(--muted);
    font-size: 10px;
}

.risk-ring-inner strong {
    font-size: 21px;
}

.risk-message {
    display: flex;
    gap: 10px;
    padding: 13px;
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 10px;
}

.risk-dot {
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    margin-top: 5px;
    background: #36aa89;
    border-radius: 50%;
}

.risk-message-high .risk-dot {
    background: #df6b58;
}

.risk-message-medium .risk-dot {
    background: #e7ad55;
}

.risk-message strong {
    font-size: 11px;
}

.risk-message p {
    margin: 5px 0 0;
    color: var(--muted);
    font-size: 10px;
    line-height: 1.6;
}

.risk-factors {
    margin-top: 13px;
}

.risk-factors > div {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
}

.risk-factors > div:last-child {
    border-bottom: 0;
}

.risk-factors span {
    color: var(--muted);
}

.risk-factors strong {
    white-space: nowrap;
}

.disclaimer {
    margin: 9px 0 0;
    color: var(--muted);
    font-size: 9px;
    line-height: 1.6;
}

.table-panel {
    padding-bottom: 0;
}

.table-heading {
    margin-bottom: 19px;
}

.table-scroll {
    width: 100%;
    overflow-x: auto;
}

.table-scroll table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    white-space: nowrap;
}

.table-scroll thead {
    background: var(--panel-soft);
}

.table-scroll th {
    padding: 13px 15px;
    color: var(--muted);
    text-align: left;
    font-size: 10px;
    font-weight: 650;
}

.table-scroll td {
    padding: 14px 15px;
    border-bottom: 1px solid var(--border);
}

.table-scroll tbody tr:last-child td {
    border-bottom: 0;
}

.table-scroll tbody tr:hover {
    background: var(--panel-soft);
}

.weather-badge {
    display: inline-flex;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 700;
}

.badge-rain {
    color: #397fb9;
    background: #e8f3ff;
}

.badge-hot {
    color: #b86b35;
    background: #fff0e3;
}

.badge-normal {
    color: #16866e;
    background: #e5f6ef;
}

.nf-app.theme-dark .badge-rain {
    color: #7ab8e8;
    background: #1a2e3f;
}

.nf-app.theme-dark .badge-hot {
    color: #e8a06a;
    background: #3a2b1a;
}

.nf-app.theme-dark .badge-normal {
    color: #70cf98;
    background: #1a3028;
}

.empty-cell {
    color: var(--muted);
    text-align: center;
}

.table-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 0;
    color: var(--muted);
    border-top: 1px solid var(--border);
    font-size: 10px;
}

.page-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 2px 0;
    color: var(--muted);
    font-size: 10px;
}

@media (max-width: 1200px) {
    .page-content {
        padding-right: 22px;
        padding-left: 22px;
    }

    .metrics-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {
    .main-content {
        margin-left: 0;
    }

    .mobile-menu {
        display: grid;
    }

    .analysis-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 620px) {
    .topbar {
        min-height: 72px;
        padding: 12px 14px;
    }

    .breadcrumb {
        gap: 5px;
        font-size: 10px;
    }

    .topbar-subtitle {
        font-size: 10px;
    }

    .page-content {
        padding: 22px 13px 18px;
    }

    .page-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 16px;
    }

    .page-heading h1 {
        font-size: 30px;
    }

    .period-card {
        width: 100%;
    }

    .filter-panel,
    .panel {
        padding: 15px;
    }

    .filter-grid {
        grid-template-columns: 1fr;
    }

    .metrics-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    .metric-card {
        padding: 13px 11px;
    }

    .metric-card-top {
        align-items: flex-start;
        gap: 7px;
        margin-bottom: 15px;
    }

    .metric-icon {
        width: 30px;
        height: 30px;
        flex-basis: 30px;
        font-size: 17px;
    }

    .metric-title {
        font-size: 10px;
    }

    .metric-value {
        font-size: 23px;
    }

    .metric-value small {
        font-size: 10px;
    }

    .metric-bottom {
        align-items: flex-start;
        flex-direction: column;
        gap: 5px;
    }

    .chart-container {
        grid-template-columns: 29px minmax(0, 1fr);
        gap: 5px;
    }

    .chart-main,
    .y-labels {
        height: 175px;
    }

    .x-labels {
        font-size: 8px;
    }

    .chart-footer {
        gap: 18px;
    }

    .table-footer,
    .page-footer {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>
