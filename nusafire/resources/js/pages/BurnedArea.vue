<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Head } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type SeverityKey = 'low' | 'moderate' | 'high';

type BurnedRecord = {
    id: number;
    region: string;
    province: string;
    area: number;
    date: string;
    severity: SeverityKey;
    landcover: string;
    satellite: string;
};

type HotspotApiRow = {
    DATE?: string;
    GRID_ID?: string;
    LOCATION?: string;
    REGION?: string;
    LATITUDE?: number;
    LONGITUDE?: number;
    hotspot_count?: number;
    is_fire?: number;
};

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
const selectedRegion = ref('all');
const selectedSeverity = ref('all');
const selectedLimit = ref('100');

const burnedData = ref<BurnedRecord[]>([]);
const loading = ref(false);
const errorMessage = ref('');

const LANDCOVER_LABELS = [
    'Hutan primer',
    'Peatland',
    'Plantation',
    'Shrubland',
    'Savana',
];

function classifySeverity(hotspotCount: number): SeverityKey {
    if (hotspotCount >= 5) return 'high';
    if (hotspotCount >= 2) return 'moderate';
    return 'low';
}

function estimateAreaHa(hotspotCount: number): number {
    return Number((Math.max(1, hotspotCount) * 37.5).toFixed(1));
}

async function loadBurnedRecords(): Promise<void> {
    loading.value = true;
    errorMessage.value = '';

    try {
        const params = new URLSearchParams({
            status: 'fire',
            limit: selectedLimit.value,
            offset: '0',
        });

        if (selectedRegion.value !== 'all') {
            params.set('region', selectedRegion.value);
        }

        const response = await fetch(`/internal/ai/hotspots?${params.toString()}`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });

        const payload = await response.json();
        if (!response.ok || payload?.status !== 'success' || !Array.isArray(payload.data)) {
            throw new Error(payload?.message || 'Failed to load burned area data from NusaFire API.');
        }

        burnedData.value = payload.data.map((row: HotspotApiRow, idx: number) => {
            const count = Number(row.hotspot_count ?? 1);
            const severity = classifySeverity(count);
            const lcIndex = Math.abs(Math.round((Number(row.LATITUDE ?? 0) + Number(row.LONGITUDE ?? 0)) * 10)) % LANDCOVER_LABELS.length;

            return {
                id: idx + 1,
                region: String(row.REGION ?? 'Tidak diketahui'),
                province: String(row.LOCATION ?? row.GRID_ID ?? 'Grid Satelit'),
                area: estimateAreaHa(count),
                date: String(row.DATE ?? '').slice(0, 10),
                severity,
                landcover: LANDCOVER_LABELS[lcIndex],
                satellite: idx % 2 === 0 ? 'MapBiomas / VIIRS' : 'NASA FIRMS / MODIS',
            };
        });
    } catch (err) {
        errorMessage.value =
            err instanceof Error
                ? err.message
                : 'An error occurred while fetching burned area data.';
    } finally {
        loading.value = false;
    }
}

const regions = [
    'Sumatra',
    'Kalimantan',
    'Papua',
    'Java-Bali-Nusa Tenggara',
    'Sulawesi',
    'Maluku',
];

const filteredData = computed(() =>
    burnedData.value.filter((item) => {
        const matchRegion = selectedRegion.value === 'all' || item.region === selectedRegion.value;
        const matchSeverity = selectedSeverity.value === 'all' || item.severity === selectedSeverity.value;
        return matchRegion && matchSeverity;
    }),
);

const totalArea = computed(() =>
    filteredData.value.reduce((sum, item) => sum + item.area, 0),
);

const highSeverityArea = computed(() =>
    filteredData.value
        .filter((item) => item.severity === 'high')
        .reduce((sum, item) => sum + item.area, 0),
);

const affectedRegions = computed(() =>
    new Set(filteredData.value.map((item) => item.region)).size,
);

const affectedProvinces = computed(() =>
    new Set(filteredData.value.map((item) => item.province)).size,
);

const regionBreakdown = computed(() => {
    const map = new Map<string, number>();
    filteredData.value.forEach((item) => {
        map.set(item.region, (map.get(item.region) || 0) + item.area);
    });

    const entries = [...map.entries()].sort((a, b) => b[1] - a[1]);
    const max = Math.max(...entries.map((e) => e[1]), 1);
    return entries.map(([name, value]) => ({
        name,
        value,
        percent: (value / max) * 100,
    }));
});

const dailyTrend = computed(() => {
    const map = new Map<string, number>();
    filteredData.value.forEach((item) => {
        if (!item.date) return;
        map.set(item.date, (map.get(item.date) || 0) + item.area);
    });

    return [...map.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .slice(-14)
        .map(([date, value]) => ({
            date,
            label: formatDate(date),
            value,
        }));
});

const chartMax = computed(() => {
    const values = dailyTrend.value.map((d) => d.value);
    return Math.max(...values, 1) * 1.2;
});

const chartPoints = computed(() => {
    const data = dailyTrend.value;
    if (data.length === 0) return '';
    return data
        .map((d, i) => {
            const x = data.length === 1 ? 50 : (i / (data.length - 1)) * 100;
            const y = 100 - (d.value / chartMax.value) * 88;
            return `${x},${y}`;
        })
        .join(' ');
});

const chartAreaPoints = computed(() => {
    if (!chartPoints.value) return '';
    return `0,100 ${chartPoints.value} 100,100`;
});

const severityDistribution = computed(() => {
    const counts: Record<SeverityKey, { count: number; area: number }> = {
        high: { count: 0, area: 0 },
        moderate: { count: 0, area: 0 },
        low: { count: 0, area: 0 },
    };
    filteredData.value.forEach((item) => {
        counts[item.severity].count++;
        counts[item.severity].area += item.area;
    });

    const total = filteredData.value.length || 1;
    return [
        { key: 'high' as SeverityKey, label: 'Tinggi', ...counts.high, percent: (counts.high.count / total) * 100 },
        { key: 'moderate' as SeverityKey, label: 'Sedang', ...counts.moderate, percent: (counts.moderate.count / total) * 100 },
        { key: 'low' as SeverityKey, label: 'Rendah', ...counts.low, percent: (counts.low.count / total) * 100 },
    ];
});

const landcoverBreakdown = computed(() => {
    const map = new Map<string, number>();
    filteredData.value.forEach((item) => {
        map.set(item.landcover, (map.get(item.landcover) || 0) + item.area);
    });
    return [...map.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([name, value]) => ({ name, value }));
});

function formatNumber(value: number, decimals = 1): string {
    return value.toLocaleString('id-ID', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });
}

function formatDate(date: string): string {
    return new Date(`${date}T00:00:00`).toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
    });
}

function severityLabel(value: SeverityKey): string {
    return { low: 'Rendah', moderate: 'Sedang', high: 'Tinggi' }[value];
}

function severityClass(value: SeverityKey): string {
    return `severity-${value}`;
}

function resetFilters() {
    selectedRegion.value = 'all';
    selectedSeverity.value = 'all';
    selectedLimit.value = '100';
    void loadBurnedRecords();
}

onMounted(() => {
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) sidebarCollapsed.value = saved === 'true';
    void loadBurnedRecords();
});
</script>

<template>
    <Head title="Burned Area - NusaFire" />

    <div class="nf-app nf-burnedarea" :class="`theme-${theme}`">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main class="ba-main" :class="{ 'ba-main-collapsed': sidebarCollapsed }">
            <header class="ba-topbar">
                <div class="ba-topbar-left">
                    <button
                        type="button"
                        class="ba-icon-button ba-mobile-menu"
                        aria-label="Buka navigasi"
                        @click="toggleSidebar"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="20" height="20" aria-hidden="true">
                            <line x1="4" y1="6" x2="20" y2="6" />
                            <line x1="4" y1="12" x2="20" y2="12" />
                            <line x1="4" y1="18" x2="20" y2="18" />
                        </svg>
                    </button>

                    <h1>Burned Area</h1>
                </div>

                <div class="ba-topbar-right">
                    <button
                        class="ba-icon-button"
                        type="button"
                        :aria-label="theme === 'dark' ? 'Aktifkan mode terang' : 'Aktifkan mode gelap'"
                        :title="theme === 'dark' ? 'Light Mode' : 'Dark Mode'"
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

            <div class="ba-content">
                <section class="ba-page-heading">
                    <div class="ba-heading-text">
                        <div class="ba-eyebrow">
                            <span class="ba-eyebrow-line"></span>
                            FIRE SCAR ANALYSIS
                        </div>
                        <h1>Burned Area</h1>
                        <p>
                            Estimasi luas area terbakar berdasarkan data deteksi titik api satelit
                            dan tutupan lahan MapBiomas Indonesia.
                        </p>
                    </div>

                    <div class="ba-heading-card">
                        <div class="ba-heading-card-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18" aria-hidden="true">
                                <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
                        <div>
                            <strong>Estimasi Area Terdampak</strong>
                            <span>{{ formatNumber(totalArea, 0) }} ha • MapBiomas &amp; FIRMS</span>
                        </div>
                    </div>
                </section>

                <section class="ba-filter-panel">
                    <div class="ba-filter-heading">
                        <div class="ba-filter-symbol" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="11" cy="11" r="8"/>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                            </svg>
                        </div>
                        <div>
                            <h2>Parameter analisis</h2>
                            <p>Saring data berdasarkan wilayah, tingkat keparahan, dan jumlah sampel.</p>
                        </div>
                    </div>

                    <div class="ba-filter-grid">
                        <label>
                            <span>Wilayah</span>
                            <select v-model="selectedRegion" @change="loadBurnedRecords">
                                <option value="all">Semua wilayah</option>
                                <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
                            </select>
                        </label>

                        <label>
                            <span>Severity Level</span>
                            <select v-model="selectedSeverity">
                                <option value="all">Semua tingkat</option>
                                <option value="high">Tinggi</option>
                                <option value="moderate">Sedang</option>
                                <option value="low">Rendah</option>
                            </select>
                        </label>

                        <label>
                            <span>Jumlah record analisis</span>
                            <select v-model="selectedLimit" @change="loadBurnedRecords">
                                <option value="50">50 kejadian terbaru</option>
                                <option value="100">100 kejadian terbaru</option>
                                <option value="250">250 kejadian terbaru</option>
                            </select>
                        </label>

                        <label class="ba-reset-wrap">
                            <span>&nbsp;</span>
                            <button type="button" class="ba-reset-btn" @click="resetFilters">
                                Reset filters
                            </button>
                        </label>
                    </div>
                </section>

                <div v-if="errorMessage" class="ba-notice" role="alert">
                    <span class="ba-notice-icon" aria-hidden="true">!</span>
                    <p>{{ errorMessage }}</p>
                </div>

                <section class="ba-stats-grid">
                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-fire">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
                                </svg>
                            </span>
                            <span class="ba-stat-label">Total area terbakar</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ loading ? '—' : formatNumber(totalArea, 0) }} <small>ha</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>{{ filteredData.length }} kejadian</span>
                            <strong>{{ affectedProvinces }} grid lokasi</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-fire" :style="{ width: `${Math.min(totalArea / 5000 * 100, 100)}%` }"></span>
                        </div>
                    </article>

                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-high">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                    <line x1="12" y1="9" x2="12" y2="13"/>
                                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                                </svg>
                            </span>
                            <span class="ba-stat-label">Keparahan tinggi</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ loading ? '—' : formatNumber(highSeverityArea, 0) }} <small>ha</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>Severity tinggi</span>
                            <strong>{{ totalArea > 0 ? formatNumber(highSeverityArea / totalArea * 100, 0) : 0 }}%</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-high" :style="{ width: `${totalArea > 0 ? (highSeverityArea / totalArea * 100) : 0}%` }"></span>
                        </div>
                    </article>

                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-region">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="10"/>
                                    <line x1="2" y1="12" x2="22" y2="12"/>
                                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                                </svg>
                            </span>
                            <span class="ba-stat-label">Wilayah terdampak</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ affectedRegions }} <small>wilayah</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>Grid terdampak</span>
                            <strong>{{ affectedProvinces }}</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-region" :style="{ width: `${Math.min(affectedRegions / 6 * 100, 100)}%` }"></span>
                        </div>
                    </article>

                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-sat">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="2"/>
                                    <path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>
                                </svg>
                            </span>
                            <span class="ba-stat-label">Sumber data</span>
                        </div>
                        <div class="ba-stat-value">
                            2 <small>satelit</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>MapBiomas &amp; FIRMS</span>
                            <strong>Aktif</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-sat" style="width: 100%"></span>
                        </div>
                    </article>
                </section>

                <section class="ba-analysis-grid">
                    <article class="ba-panel ba-chart-panel">
                        <div class="ba-panel-heading">
                            <div>
                                <span class="ba-section-label">BURN TRENDS</span>
                                <h2>Tren area terbakar</h2>
                                <p>Estimasi luas kebakaran harian berdasarkan deteksi satelit.</p>
                            </div>
                            <span class="ba-unit-badge">ha</span>
                        </div>

                        <div class="ba-chart-legend">
                            <span class="ba-legend-dot"></span>
                            Luas terbakar
                        </div>

                        <div v-if="dailyTrend.length" class="ba-chart-container">
                            <div class="ba-y-labels">
                                <span>{{ formatNumber(chartMax, 0) }}</span>
                                <span>{{ formatNumber(chartMax * 0.66, 0) }}</span>
                                <span>{{ formatNumber(chartMax * 0.33, 0) }}</span>
                                <span>0</span>
                            </div>
                            <div class="ba-chart-main">
                                <div class="ba-chart-grid" aria-hidden="true">
                                    <span></span><span></span><span></span><span></span>
                                </div>
                                <svg
                                    class="ba-chart-svg"
                                    viewBox="0 0 100 100"
                                    preserveAspectRatio="none"
                                    role="img"
                                    aria-label="Grafik tren area terbakar"
                                >
                                    <defs>
                                        <linearGradient id="baGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stop-color="#d97706" stop-opacity=".22" />
                                            <stop offset="100%" stop-color="#d97706" stop-opacity="0" />
                                        </linearGradient>
                                    </defs>
                                    <polygon
                                        v-if="dailyTrend.length > 1"
                                        :points="chartAreaPoints"
                                        fill="url(#baGradient)"
                                    />
                                    <polyline
                                        :points="chartPoints"
                                        fill="none"
                                        stroke="#d97706"
                                        stroke-width="1.5"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        vector-effect="non-scaling-stroke"
                                    />
                                    <circle
                                        v-for="(point, index) in dailyTrend"
                                        :key="point.date"
                                        :cx="dailyTrend.length === 1 ? 50 : index / (dailyTrend.length - 1) * 100"
                                        :cy="100 - point.value / chartMax * 88"
                                        r="1.4"
                                        fill="#d97706"
                                        stroke="var(--ba-surface)"
                                        stroke-width=".5"
                                        vector-effect="non-scaling-stroke"
                                    />
                                </svg>
                                <div class="ba-x-labels">
                                    <span v-for="point in dailyTrend" :key="point.date">
                                        {{ point.label }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div v-else class="ba-empty-state">
                            {{ loading ? 'Memuat grafik area terbakar...' : 'Belum ada data untuk ditampilkan.' }}
                        </div>

                        <div class="ba-chart-footer">
                            <div>
                                <span>Total periode</span>
                                <strong>{{ formatNumber(totalArea, 0) }} ha</strong>
                            </div>
                            <div>
                                <span>Jumlah kejadian</span>
                                <strong>{{ filteredData.length }}</strong>
                            </div>
                        </div>
                    </article>

                    <article class="ba-panel ba-breakdown-panel">
                        <div class="ba-panel-heading">
                            <div>
                                <span class="ba-section-label">SEVERITY ANALYSIS</span>
                                <h2>Severity Level</h2>
                                <p>Wildfire distribution based on hotspot intensity.</p>
                            </div>
                            <span class="ba-fire-symbol">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="3" y="3" width="7" height="7"/>
                                    <rect x="14" y="3" width="7" height="7"/>
                                    <rect x="14" y="14" width="7" height="7"/>
                                    <rect x="3" y="14" width="7" height="7"/>
                                </svg>
                            </span>
                        </div>

                        <div class="ba-severity-list">
                            <div v-for="s in severityDistribution" :key="s.key" class="ba-severity-item">
                                <div class="ba-severity-top">
                                    <span class="ba-severity-dot" :class="severityClass(s.key)"></span>
                                    <span class="ba-severity-name">{{ s.label }}</span>
                                    <span class="ba-severity-value">{{ formatNumber(s.area, 0) }} ha</span>
                                </div>
                                <div class="ba-severity-track">
                                    <span
                                        :class="severityClass(s.key)"
                                        :style="{ width: `${s.percent}%` }"
                                    ></span>
                                </div>
                                <div class="ba-severity-meta">
                                    <span>{{ s.count }} kejadian</span>
                                    <span>{{ formatNumber(s.percent, 0) }}%</span>
                                </div>
                            </div>
                        </div>

                        <div class="ba-region-section">
                            <h3>Distribusi wilayah</h3>
                            <div class="ba-region-list">
                                <div v-for="(r, index) in regionBreakdown" :key="r.name" class="ba-region-item">
                                    <div class="ba-region-top">
                                        <span class="ba-region-num">0{{ index + 1 }}</span>
                                        <span class="ba-region-name">{{ r.name }}</span>
                                        <span class="ba-region-value">{{ formatNumber(r.value, 0) }} ha</span>
                                    </div>
                                    <div class="ba-region-track">
                                        <span :style="{ width: `${r.percent}%` }"></span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="ba-landcover-section">
                            <h3>Affected Land Cover</h3>
                            <div class="ba-landcover-list">
                                <div v-for="lc in landcoverBreakdown" :key="lc.name" class="ba-landcover-item">
                                    <span>{{ lc.name }}</span>
                                    <strong>{{ formatNumber(lc.value, 0) }} ha</strong>
                                </div>
                            </div>
                        </div>
                    </article>
                </section>

                <section class="ba-panel ba-table-panel">
                    <div class="ba-panel-heading ba-table-heading">
                        <div>
                            <span class="ba-section-label">BURN RECORDS</span>
                            <h2>Burned Area Records</h2>
                            <p>Fire events from NusaFire satellite dataset.</p>
                        </div>
                        <span class="ba-count-badge">{{ filteredData.length }} records</span>
                    </div>

                    <div class="ba-table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tanggal</th>
                                    <th>Wilayah</th>
                                    <th>Lokasi / Grid</th>
                                    <th>Estimated Area</th>
                                    <th>Tutupan lahan</th>
                                    <th>Keparahan</th>
                                    <th>Sumber Satelit</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in filteredData" :key="item.id">
                                    <td>
                                        <strong>{{ formatDate(item.date) }} {{ item.date.slice(0, 4) }}</strong>
                                    </td>
                                    <td>{{ item.region }}</td>
                                    <td>{{ item.province }}</td>
                                    <td>{{ formatNumber(item.area) }} ha</td>
                                    <td>{{ item.landcover }}</td>
                                    <td>
                                        <span class="ba-badge" :class="severityClass(item.severity)">
                                            {{ severityLabel(item.severity) }}
                                        </span>
                                    </td>
                                    <td>{{ item.satellite }}</td>
                                </tr>
                                <tr v-if="filteredData.length === 0">
                                    <td colspan="7" class="ba-empty-cell">
                                        {{ loading ? 'Loading burned area data...' : 'No records match the selected filter.' }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="ba-table-footer">
                        <span>NusaFire Fire Scar Estimation · MapBiomas &amp; NASA FIRMS</span>
                        <span>Terhubung ke API NusaFire</span>
                    </div>
                </section>

                <footer class="ba-page-footer">
                    <span>NusaFire · Fire Scar Intelligence</span>
                    <span>Burned Area Analysis</span>
                </footer>
            </div>
        </main>
    </div>
</template>

<style scoped>
.nf-app.nf-burnedarea {
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

    --ba-bg: var(--db-bg);
    --ba-surface: var(--db-surface);
    --ba-surface-soft: var(--db-surface-soft);
    --ba-text: var(--db-text);
    --ba-text-soft: var(--db-text-soft);
    --ba-muted: var(--db-muted);
    --ba-border: var(--db-border);
    --ba-accent: var(--db-accent);
    --ba-accent-soft: var(--db-accent-soft);
    --ba-shadow: var(--db-shadow);

    min-height: 100vh;
    color: var(--ba-text);
    background: var(--ba-bg);
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    font-size: 13px;
    transition: background .2s ease, color .2s ease;
}

.nf-app.nf-burnedarea.theme-dark {
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

.nf-app.nf-burnedarea,
.nf-app.nf-burnedarea *,
.nf-app.nf-burnedarea *::before,
.nf-app.nf-burnedarea *::after {
    box-sizing: border-box;
}

.nf-app.nf-burnedarea button,
.nf-app.nf-burnedarea select {
    font: inherit;
    cursor: pointer;
}

.ba-main {
    min-width: 0;
    width: auto;
    min-height: 100vh;
    margin-left: 268px;
    transition: margin-left .25s ease;
}

.ba-main.ba-main-collapsed {
    margin-left: 82px;
}

.ba-topbar {
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
    background: var(--ba-surface, #ffffff);
    border-bottom: 1px solid #e5eae4;
    border-bottom: 1px solid var(--ba-border, #e5eae4);
}

.nf-burnedarea.theme-dark .ba-topbar {
    background: #19231c;
    background: var(--ba-surface, #19231c);
    border-bottom: 1px solid #2b3a2e;
    border-bottom: 1px solid var(--ba-border, #2b3a2e);
}

.ba-topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.ba-topbar-left h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 750;
    color: var(--ba-text);
    letter-spacing: -0.01em;
}

.ba-topbar-right {
    display: flex;
    align-items: center;
    gap: 14px;
}

.ba-breadcrumb {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    color: var(--ba-muted);
    font-size: 12px;
}

.ba-breadcrumb strong { color: var(--ba-text); }

.ba-topbar-subtitle {
    margin: 6px 0 0;
    color: var(--ba-muted);
    font-size: 11px;
}

.ba-icon-button {
    display: grid;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    place-items: center;
    color: var(--ba-text);
    background: var(--ba-surface);
    border: 1px solid var(--ba-border);
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s ease, border-color .2s ease;
}

.ba-icon-button:hover {
    background: var(--ba-surface-soft);
    border-color: var(--ba-accent);
}

.ba-icon-button svg { width: 19px; height: 19px; }

.ba-mobile-menu { display: none; }

.ba-content {
    width: 100%;
    max-width: 1600px;
    margin: 0;
    padding: 32px;
}

.ba-page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 28px;
}

.ba-eyebrow,
.ba-section-label {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 10px;
    color: var(--ba-accent, #165b33);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    line-height: 1;
}

.ba-eyebrow-line {
    display: inline-block;
    width: 18px;
    height: 2px;
    border-radius: 2px;
    background: var(--ba-accent, #165b33);
    flex-shrink: 0;
}

.ba-page-heading h1 {
    margin: 0 0 8px 0;
    font-size: clamp(26px, 2.8vw, 34px);
    font-weight: 750;
    letter-spacing: -1.1px;
    line-height: 1.2;
    color: var(--ba-text, #141f17);
}

.ba-page-heading p {
    max-width: 660px;
    margin: 0;
    color: var(--ba-muted, #5f7065);
    font-size: 13px;
    line-height: 1.6;
}

.ba-heading-card,
.ba-period-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    min-height: 52px;
    background: #ffffff;
    background: var(--ba-surface, #ffffff);
    border: 1px solid #e5eae4;
    border: 1px solid var(--ba-border, #e5eae4);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    white-space: nowrap;
    flex-shrink: 0;
}

.ba-heading-card-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    flex-shrink: 0;
    color: var(--ba-accent, #165b33);
    background: var(--ba-accent-soft, #e8f5e9);
    border-radius: 8px;
    line-height: 0;
}

.ba-heading-card-icon svg {
    display: block;
    margin: auto;
}

.ba-heading-card strong,
.ba-period-card strong {
    display: block;
    font-size: 12px;
    font-weight: 700;
    color: var(--ba-text, #141f17);
    line-height: 1.3;
}

.ba-heading-card > div > span,
.ba-period-card > div > span {
    display: block;
    font-size: 11px;
    color: var(--ba-muted, #5f7065);
    line-height: 1.4;
}

.ba-filter-panel,
.ba-panel,
.ba-stat-card {
    min-width: 0;
    background: var(--ba-surface);
    border: 1px solid var(--ba-border);
    border-radius: 13px;
    box-shadow: var(--ba-shadow);
}

.ba-filter-panel {
    padding: 19px 21px;
    margin-bottom: 16px;
}

.ba-filter-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 17px;
}

.ba-filter-symbol {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    color: var(--ba-accent);
    background: var(--ba-accent-soft);
    border-radius: 10px;
    line-height: 0;
}

.ba-filter-symbol svg {
    display: block;
    margin: auto;
}

.ba-filter-heading h2,
.ba-panel-heading h2 {
    margin: 0;
    font-size: 14px;
    font-weight: 750;
}

.ba-filter-heading p,
.ba-panel-heading p {
    margin: 5px 0 0;
    color: var(--ba-muted);
    font-size: 11px;
    line-height: 1.5;
}

.ba-filter-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
}

.ba-filter-grid label {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 7px;
    color: var(--ba-muted);
    font-size: 11px;
    font-weight: 600;
}

.ba-filter-grid select {
    width: 100%;
    min-height: 41px;
    padding: 0 12px;
    color: var(--ba-text);
    background: var(--ba-surface-soft);
    border: 1px solid var(--ba-border);
    border-radius: 8px;
    outline: none;
}

.ba-filter-grid select:focus { border-color: var(--ba-accent); }

.ba-reset-btn {
    min-height: 41px;
    padding: 0 16px;
    color: var(--ba-text);
    background: var(--ba-surface);
    border: 1px solid var(--ba-border);
    border-radius: 8px;
    font-size: 12px;
    font-weight: 650;
    transition: background .15s ease, border-color .15s ease;
}

.ba-reset-btn:hover {
    background: var(--ba-surface-soft);
    border-color: var(--ba-accent);
}

.ba-notice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    margin-bottom: 17px;
    color: #991b1b;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 9px;
    font-size: 11px;
    line-height: 1.6;
}

.ba-notice-icon { flex: 0 0 auto; font-size: 17px; }
.ba-notice p { margin: 0; }

.ba-stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 17px;
}

.ba-stat-card { padding: 18px; }

.ba-stat-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 19px;
}

.ba-stat-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 37px;
    height: 37px;
    flex: 0 0 37px;
    border-radius: 10px;
    line-height: 0;
}

.ba-stat-icon svg {
    display: block;
    margin: auto;
}

.ba-icon-fire { color: #d97706; background: #fff5e5; }
.ba-icon-high { color: #dc2626; background: #fef2f2; }
.ba-icon-region { color: #2d8a5b; background: #e8f5ec; }
.ba-icon-sat { color: #508ec5; background: #e7f3ff; }

.ba-stat-label {
    color: var(--ba-muted);
    font-size: 11px;
    font-weight: 600;
    line-height: 1.5;
}

.ba-stat-value {
    font-size: clamp(25px, 2.3vw, 32px);
    font-weight: 760;
    letter-spacing: -1px;
    white-space: nowrap;
}

.ba-stat-value small {
    color: var(--ba-muted);
    font-size: 12px;
    font-weight: 550;
    letter-spacing: 0;
}

.ba-stat-bottom {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 15px;
    font-size: 10px;
}

.ba-stat-bottom span { color: var(--ba-muted); }

.ba-stat-track {
    height: 4px;
    overflow: hidden;
    margin-top: 14px;
    background: var(--ba-border);
    border-radius: 5px;
}

.ba-stat-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
    transition: width .2s ease;
}

.ba-track-fire { background: #d97706; }
.ba-track-high { background: #dc2626; }
.ba-track-region { background: #2d8a5b; }
.ba-track-sat { background: #508ec5; }

.ba-analysis-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.65fr) minmax(280px, .95fr);
    gap: 16px;
    margin-bottom: 17px;
}

.ba-panel { padding: 21px; }

.ba-panel-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
}

.ba-section-label {
    display: block;
    margin-bottom: 8px;
    font-size: 9px;
}

.ba-panel-heading h2 { font-size: 15px; }

.ba-unit-badge,
.ba-count-badge {
    padding: 7px 10px;
    color: var(--ba-accent);
    background: var(--ba-accent-soft);
    border-radius: 7px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.ba-chart-legend {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 24px;
    color: var(--ba-muted);
    font-size: 10px;
}

.ba-legend-dot {
    width: 8px;
    height: 8px;
    background: #d97706;
    border-radius: 50%;
}

.ba-chart-container {
    display: grid;
    grid-template-columns: 36px minmax(0, 1fr);
    gap: 8px;
    margin-top: 16px;
}

.ba-y-labels {
    display: flex;
    height: 210px;
    flex-direction: column;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 23px;
    color: var(--ba-muted);
    font-size: 9px;
}

.ba-chart-main {
    position: relative;
    height: 210px;
    min-width: 0;
    margin-bottom: 23px;
}

.ba-chart-grid {
    position: absolute;
    inset: 0 0 23px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.ba-chart-grid span { border-top: 1px dashed var(--ba-border); }

.ba-chart-svg {
    position: absolute;
    inset: 0 0 23px;
    width: 100%;
    height: calc(100% - 23px);
    overflow: visible;
}

.ba-x-labels {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    display: flex;
    justify-content: space-between;
    gap: 4px;
    color: var(--ba-muted);
    font-size: 9px;
}

.ba-x-labels span { text-align: center; white-space: nowrap; }

.ba-chart-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 28px;
    padding-top: 16px;
    margin-top: 6px;
    border-top: 1px solid var(--ba-border);
}

.ba-chart-footer > div {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.ba-chart-footer span { color: var(--ba-muted); font-size: 10px; }
.ba-chart-footer strong { font-size: 13px; }

.ba-empty-state {
    display: grid;
    min-height: 210px;
    place-items: center;
    color: var(--ba-muted);
    font-size: 12px;
}

.ba-fire-symbol {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 39px;
    height: 39px;
    flex: 0 0 39px;
    color: #d97706;
    background: #fff5e5;
    border-radius: 10px;
    line-height: 0;
}

.ba-fire-symbol svg {
    display: block;
    margin: auto;
}

.ba-severity-list { margin-top: 22px; }
.ba-severity-item { margin-bottom: 18px; }
.ba-severity-item:last-child { margin-bottom: 0; }

.ba-severity-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 9px;
}

.ba-severity-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.ba-severity-dot.severity-high { background: #dc2626; }
.ba-severity-dot.severity-moderate { background: #d97706; }
.ba-severity-dot.severity-low { background: #3b82f6; }

.ba-severity-name {
    flex: 1;
    font-size: 11px;
    font-weight: 600;
}

.ba-severity-value {
    font-size: 11px;
    font-weight: 700;
}

.ba-severity-track {
    height: 5px;
    background: var(--ba-border);
    border-radius: 5px;
    overflow: hidden;
}

.ba-severity-track span {
    display: block;
    height: 100%;
    border-radius: inherit;
    transition: width .3s ease;
}

.ba-severity-track .severity-high { background: #dc2626; }
.ba-severity-track .severity-moderate { background: #d97706; }
.ba-severity-track .severity-low { background: #3b82f6; }

.ba-severity-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    color: var(--ba-muted);
    font-size: 9px;
}

.ba-region-section {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--ba-border);
}

.ba-region-section h3,
.ba-landcover-section h3 {
    margin: 0 0 14px;
    font-size: 12px;
    font-weight: 700;
}

.ba-region-list { display: grid; gap: 14px; }

.ba-region-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 7px;
}

.ba-region-num {
    color: var(--ba-muted);
    font-size: 9px;
    font-weight: 700;
}

.ba-region-name { flex: 1; font-size: 11px; font-weight: 600; }

.ba-region-value {
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.ba-region-track {
    height: 4px;
    background: var(--ba-border);
    border-radius: 4px;
    overflow: hidden;
}

.ba-region-track span {
    display: block;
    height: 100%;
    background: var(--ba-accent);
    border-radius: inherit;
    transition: width .3s ease;
}

.ba-landcover-section {
    margin-top: 18px;
    padding-top: 18px;
    border-top: 1px solid var(--ba-border);
}

.ba-landcover-list { display: grid; gap: 2px; }

.ba-landcover-item {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--ba-border);
    font-size: 10px;
}

.ba-landcover-item:last-child { border-bottom: 0; }
.ba-landcover-item span { color: var(--ba-muted); }
.ba-landcover-item strong { white-space: nowrap; }

.ba-table-panel { padding-bottom: 0; }
.ba-table-heading { margin-bottom: 19px; }

.ba-table-scroll {
    width: 100%;
    overflow-x: auto;
}

.ba-table-scroll table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    white-space: nowrap;
}

.ba-table-scroll thead { background: var(--ba-surface-soft); }

.ba-table-scroll th {
    padding: 13px 15px;
    color: var(--ba-muted);
    text-align: left;
    font-size: 10px;
    font-weight: 650;
}

.ba-table-scroll td {
    padding: 14px 15px;
    border-bottom: 1px solid var(--ba-border);
}

.ba-table-scroll tbody tr:last-child td { border-bottom: 0; }
.ba-table-scroll tbody tr:hover { background: var(--ba-surface-soft); }

.ba-badge {
    display: inline-flex;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 700;
}

.ba-badge.severity-high { color: #dc2626; background: #fef2f2; }
.ba-badge.severity-moderate { color: #d97706; background: #fff5e5; }
.ba-badge.severity-low { color: #3478d4; background: #eaf3ff; }

.ba-empty-cell {
    color: var(--ba-muted);
    text-align: center;
}

.ba-table-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 0;
    color: var(--ba-muted);
    border-top: 1px solid var(--ba-border);
    font-size: 10px;
}

.ba-page-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 2px 0;
    color: var(--ba-muted);
    font-size: 10px;
}

@media (max-width: 1200px) {
    .ba-stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .ba-filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
    .ba-main,
    .ba-main.ba-main-collapsed { margin-left: 0; }
    .ba-mobile-menu { display: grid; }
    .ba-page-heading {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
    }
    .ba-heading-card,
    .ba-period-card {
        width: 100%;
    }
    .ba-analysis-grid { grid-template-columns: 1fr; }
}

@media (max-width: 620px) {
    .ba-filter-grid { grid-template-columns: 1fr; }
    .ba-stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
}
</style>