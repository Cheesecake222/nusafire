
<script setup lang="ts">
import { computed, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type BurnedRecord = {
    id: number;
    region: string;
    province: string;
    area: number;
    date: string;
    severity: 'low' | 'moderate' | 'high';
    landcover: string;
    satellite: string;
};

type SeverityKey = 'low' | 'moderate' | 'high';

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const selectedRegion = ref('all');
const selectedSeverity = ref('all');
const selectedPeriod = ref('30');

// Data demonstrasi — akan diganti dengan data API saat integrasi backend
const burnedData = ref<BurnedRecord[]>([
    { id: 1, region: 'Kalimantan', province: 'Kalimantan Tengah', area: 245.8, date: '2026-11-10', severity: 'high', landcover: 'Lahan gambut', satellite: 'Sentinel-2' },
    { id: 2, region: 'Sumatra', province: 'Riau', area: 189.3, date: '2026-11-09', severity: 'high', landcover: 'Hutan primer', satellite: 'Landsat-9' },
    { id: 3, region: 'Kalimantan', province: 'Kalimantan Barat', area: 132.7, date: '2026-11-08', severity: 'moderate', landcover: 'Perkebunan', satellite: 'Sentinel-2' },
    { id: 4, region: 'Sulawesi', province: 'Sulawesi Selatan', area: 87.4, date: '2026-11-07', severity: 'moderate', landcover: 'Savana', satellite: 'Landsat-9' },
    { id: 5, region: 'Papua', province: 'Papua Barat', area: 56.2, date: '2026-11-06', severity: 'low', landcover: 'Hutan sekunder', satellite: 'Sentinel-2' },
    { id: 6, region: 'Sumatra', province: 'Jambi', area: 178.5, date: '2026-11-05', severity: 'high', landcover: 'Lahan gambut', satellite: 'Sentinel-2' },
    { id: 7, region: 'Kalimantan', province: 'Kalimantan Selatan', area: 95.1, date: '2026-11-04', severity: 'moderate', landcover: 'Semak belukar', satellite: 'Landsat-9' },
    { id: 8, region: 'Sulawesi', province: 'Sulawesi Tengah', area: 42.6, date: '2026-11-03', severity: 'low', landcover: 'Perkebunan', satellite: 'Sentinel-2' },
    { id: 9, region: 'Sumatra', province: 'Sumatera Selatan', area: 210.9, date: '2026-11-02', severity: 'high', landcover: 'Lahan gambut', satellite: 'Landsat-9' },
    { id: 10, region: 'Papua', province: 'Papua', area: 31.8, date: '2026-11-01', severity: 'low', landcover: 'Padang rumput', satellite: 'Sentinel-2' },
    { id: 11, region: 'Kalimantan', province: 'Kalimantan Timur', area: 167.3, date: '2026-10-31', severity: 'high', landcover: 'Hutan primer', satellite: 'Sentinel-2' },
    { id: 12, region: 'Sumatra', province: 'Riau', area: 78.4, date: '2026-10-30', severity: 'moderate', landcover: 'Semak belukar', satellite: 'Landsat-9' },
]);

const regions = computed(() =>
    [...new Set(burnedData.value.map((r) => r.region))].sort(),
);

const filteredData = computed(() => {
    const periodDays = parseInt(selectedPeriod.value);
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - periodDays);
    const cutoffStr = cutoff.toISOString().slice(0, 10);

    return burnedData.value.filter((item) => {
        const matchRegion = selectedRegion.value === 'all' || item.region === selectedRegion.value;
        const matchSeverity = selectedSeverity.value === 'all' || item.severity === selectedSeverity.value;
        const matchDate = item.date >= cutoffStr;
        return matchRegion && matchSeverity && matchDate;
    });
});

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

// Data untuk grafik tren area terbakar per wilayah
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

// Data untuk grafik harian
const dailyTrend = computed(() => {
    const map = new Map<string, number>();
    filteredData.value.forEach((item) => {
        map.set(item.date, (map.get(item.date) || 0) + item.area);
    });

    return [...map.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
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

// Distribusi severity
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

// Distribusi land cover
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
    selectedPeriod.value = '30';
}
</script>

<template>
    <Head title="Burned Area - NusaFire" />

    <div class="nf-app nf-burnedarea" :class="`theme-${theme}`">
        <AppSidebar
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <main class="ba-main" :class="{ 'ba-sidebar-collapsed': sidebarCollapsed }">
            <header class="ba-topbar">
                <div class="ba-topbar-left">
                    <button
                        type="button"
                        class="ba-icon-button ba-mobile-menu"
                        :class="{ 'ba-menu-visible': sidebarCollapsed }"
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
                        <div class="ba-breadcrumb">
                            <span>NusaFire</span>
                            <span>/</span>
                            <span>Analysis</span>
                            <span>/</span>
                            <strong>Burned Area</strong>
                        </div>
                        <p class="ba-topbar-subtitle">
                            Burned area monitoring and analysis
                        </p>
                    </div>
                </div>

                <button
                    class="ba-icon-button"
                    type="button"
                    :aria-label="theme === 'dark' ? 'Aktifkan mode terang' : 'Aktifkan mode gelap'"
                    :title="theme === 'dark' ? 'Mode terang' : 'Mode gelap'"
                    @click="toggleTheme"
                >
                    <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7" />
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

            <div class="ba-content">
                <!-- Page heading -->
                <section class="ba-page-heading">
                    <div>
                        <div class="ba-eyebrow">
                            <span></span>
                            FIRE SCAR ANALYSIS
                        </div>
                        <h1>Burned <span>Area</span></h1>
                        <p>
                            Analisis luas area terbakar berdasarkan citra satelit
                            untuk mendukung pemantauan dampak kebakaran hutan dan lahan.
                        </p>
                    </div>

                    <div class="ba-period-card">
                        <span>TOTAL AREA</span>
                        <strong>{{ formatNumber(totalArea, 0) }} ha</strong>
                        <small>Data demonstrasi</small>
                    </div>
                </section>

                <!-- Filter panel -->
                <section class="ba-filter-panel">
                    <div class="ba-filter-heading">
                        <div class="ba-filter-symbol" aria-hidden="true">⌕</div>
                        <div>
                            <h2>Parameter analisis</h2>
                            <p>Saring data berdasarkan wilayah, tingkat keparahan, dan periode.</p>
                        </div>
                    </div>

                    <div class="ba-filter-grid">
                        <label>
                            <span>Wilayah</span>
                            <select v-model="selectedRegion">
                                <option value="all">Semua wilayah</option>
                                <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
                            </select>
                        </label>

                        <label>
                            <span>Tingkat keparahan</span>
                            <select v-model="selectedSeverity">
                                <option value="all">Semua tingkat</option>
                                <option value="high">Tinggi</option>
                                <option value="moderate">Sedang</option>
                                <option value="low">Rendah</option>
                            </select>
                        </label>

                        <label>
                            <span>Periode pengamatan</span>
                            <select v-model="selectedPeriod">
                                <option value="7">7 hari terakhir</option>
                                <option value="14">14 hari terakhir</option>
                                <option value="30">30 hari terakhir</option>
                                <option value="90">90 hari terakhir</option>
                            </select>
                        </label>

                        <label class="ba-reset-wrap">
                            <span>&nbsp;</span>
                            <button type="button" class="ba-reset-btn" @click="resetFilters">
                                Reset filter
                            </button>
                        </label>
                    </div>
                </section>

                <!-- Data notice -->
                <div class="ba-notice" role="note">
                    <span class="ba-notice-icon" aria-hidden="true">ⓘ</span>
                    <p>
                        <strong>Data demonstrasi:</strong> angka pada halaman ini merupakan
                        data contoh, bukan hasil analisis citra satelit aktual.
                        Data belum terhubung ke Sentinel-2 atau Landsat.
                    </p>
                </div>

                <!-- Stat cards -->
                <section class="ba-stats-grid">
                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-fire">▧</span>
                            <span class="ba-stat-label">Total area terbakar</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ formatNumber(totalArea, 0) }} <small>ha</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>{{ filteredData.length }} kejadian</span>
                            <strong>{{ affectedProvinces }} provinsi</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-fire" :style="{ width: `${Math.min(totalArea / 2000 * 100, 100)}%` }"></span>
                        </div>
                    </article>

                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-high">△</span>
                            <span class="ba-stat-label">Keparahan tinggi</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ formatNumber(highSeverityArea, 0) }} <small>ha</small>
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
                            <span class="ba-stat-icon ba-icon-region">◎</span>
                            <span class="ba-stat-label">Wilayah terdampak</span>
                        </div>
                        <div class="ba-stat-value">
                            {{ affectedRegions }} <small>wilayah</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>Provinsi</span>
                            <strong>{{ affectedProvinces }}</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-region" :style="{ width: `${affectedRegions / 4 * 100}%` }"></span>
                        </div>
                    </article>

                    <article class="ba-stat-card">
                        <div class="ba-stat-top">
                            <span class="ba-stat-icon ba-icon-sat">◈</span>
                            <span class="ba-stat-label">Sumber data</span>
                        </div>
                        <div class="ba-stat-value">
                            2 <small>satelit</small>
                        </div>
                        <div class="ba-stat-bottom">
                            <span>Sentinel-2 &amp; Landsat-9</span>
                            <strong>Demo</strong>
                        </div>
                        <div class="ba-stat-track">
                            <span class="ba-track-sat" style="width: 50%"></span>
                        </div>
                    </article>
                </section>

                <!-- Charts grid -->
                <section class="ba-analysis-grid">
                    <!-- Trend chart -->
                    <article class="ba-panel ba-chart-panel">
                        <div class="ba-panel-heading">
                            <div>
                                <span class="ba-section-label">BURN TRENDS</span>
                                <h2>Tren area terbakar</h2>
                                <p>Luas kebakaran harian selama periode pengamatan.</p>
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
                            Belum ada data untuk ditampilkan.
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

                    <!-- Severity and regional breakdown -->
                    <article class="ba-panel ba-breakdown-panel">
                        <div class="ba-panel-heading">
                            <div>
                                <span class="ba-section-label">SEVERITY ANALYSIS</span>
                                <h2>Tingkat keparahan</h2>
                                <p>Distribusi kebakaran berdasarkan severity.</p>
                            </div>
                            <span class="ba-fire-symbol">▧</span>
                        </div>

                        <!-- Severity bars -->
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

                        <!-- Regional breakdown -->
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

                        <!-- Land cover -->
                        <div class="ba-landcover-section">
                            <h3>Tutupan lahan terdampak</h3>
                            <div class="ba-landcover-list">
                                <div v-for="lc in landcoverBreakdown" :key="lc.name" class="ba-landcover-item">
                                    <span>{{ lc.name }}</span>
                                    <strong>{{ formatNumber(lc.value, 0) }} ha</strong>
                                </div>
                            </div>
                        </div>
                    </article>
                </section>

                <!-- Data table -->
                <section class="ba-panel ba-table-panel">
                    <div class="ba-panel-heading ba-table-heading">
                        <div>
                            <span class="ba-section-label">BURN RECORDS</span>
                            <h2>Riwayat area terbakar</h2>
                            <p>Data kejadian kebakaran dari citra satelit.</p>
                        </div>
                        <span class="ba-count-badge">{{ filteredData.length }} catatan</span>
                    </div>

                    <div class="ba-table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Tanggal</th>
                                    <th>Wilayah</th>
                                    <th>Provinsi</th>
                                    <th>Luas</th>
                                    <th>Tutupan lahan</th>
                                    <th>Keparahan</th>
                                    <th>Satelit</th>
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
                                        Tidak ada data yang sesuai dengan filter.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="ba-table-footer">
                        <span>Data demonstrasi · Belum terhubung ke analisis citra satelit.</span>
                        <span>Sumber data aktual belum ditentukan.</span>
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
/* ─── Design tokens ─── */
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

/* ─── Layout ─── */
.ba-main {
    min-height: 100vh;
    margin-left: 252px;
    transition: margin-left .3s cubic-bezier(.4,0,.2,1);
}

.ba-main.ba-sidebar-collapsed {
    margin-left: 0;
}

.ba-topbar {
    min-height: 82px;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 1px solid var(--ba-border);
    background: var(--ba-surface);
}

.ba-topbar-left {
    display: flex;
    align-items: center;
    gap: 13px;
    min-width: 0;
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

.ba-mobile-menu.ba-menu-visible { display: grid; }

.ba-content {
    width: 100%;
    max-width: 1600px;
    padding: 30px 32px 22px;
    margin: 0 auto;
}

/* ─── Page heading ─── */
.ba-page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 22px;
    margin-bottom: 25px;
}

.ba-eyebrow,
.ba-section-label {
    color: var(--ba-accent);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.ba-eyebrow {
    display: flex;
    align-items: center;
    gap: 8px;
}

.ba-eyebrow > span {
    width: 18px;
    height: 2px;
    background: var(--ba-accent);
    border-radius: 2px;
}

.ba-page-heading h1 {
    margin: 11px 0 8px;
    font-size: clamp(28px, 3vw, 37px);
    font-weight: 760;
    line-height: 1.15;
    letter-spacing: -1.2px;
}

.ba-page-heading h1 > span { color: var(--ba-accent); }

.ba-page-heading p {
    max-width: 640px;
    margin: 0;
    color: var(--ba-muted);
    font-size: 12px;
    line-height: 1.7;
}

.ba-period-card {
    display: flex;
    min-width: 195px;
    flex-direction: column;
    gap: 7px;
    padding: 14px 16px;
    border: 1px solid var(--ba-border);
    border-radius: 12px;
    background: var(--ba-surface);
}

.ba-period-card > span {
    color: var(--ba-muted);
    font-size: 9px;
    font-weight: 750;
    letter-spacing: 1px;
}

.ba-period-card strong { font-size: 12px; }
.ba-period-card small { color: #bd8a3b; font-size: 10px; }

/* ─── Filter panel ─── */
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
    display: grid;
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    place-items: center;
    color: var(--ba-accent);
    background: var(--ba-accent-soft);
    border-radius: 10px;
    font-size: 25px;
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

/* ─── Notice ─── */
.ba-notice {
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

.nf-app.nf-burnedarea.theme-dark .ba-notice {
    color: #d4c27a;
    background: #272619;
    border-color: #4a4522;
}

.ba-notice-icon { flex: 0 0 auto; font-size: 17px; }
.ba-notice p { margin: 0; }

/* ─── Stat cards ─── */
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
    display: grid;
    width: 37px;
    height: 37px;
    flex: 0 0 37px;
    place-items: center;
    border-radius: 10px;
    font-size: 20px;
}

.ba-icon-fire { color: #d97706; background: #fff5e5; }
.ba-icon-high { color: #dc2626; background: #fef2f2; }
.ba-icon-region { color: #2d8a5b; background: #e8f5ec; }
.ba-icon-sat { color: #508ec5; background: #e7f3ff; }

.nf-app.nf-burnedarea.theme-dark .ba-icon-fire { color: #fbbf24; background: #3a2b1a; }
.nf-app.nf-burnedarea.theme-dark .ba-icon-high { color: #f87171; background: #3a1a1a; }
.nf-app.nf-burnedarea.theme-dark .ba-icon-region { color: #70cf98; background: #1a3028; }
.nf-app.nf-burnedarea.theme-dark .ba-icon-sat { color: #7ab8e8; background: #1a2e3f; }

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

/* ─── Analysis grid ─── */
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

/* ─── Chart ─── */
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

/* ─── Breakdown panel ─── */
.ba-fire-symbol {
    display: grid;
    width: 39px;
    height: 39px;
    flex: 0 0 39px;
    place-items: center;
    color: #d97706;
    background: #fff5e5;
    border-radius: 10px;
    font-size: 23px;
}

.nf-app.nf-burnedarea.theme-dark .ba-fire-symbol {
    color: #fbbf24;
    background: #3a2b1a;
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

/* Region breakdown */
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

/* Land cover */
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

/* ─── Table ─── */
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

.nf-app.nf-burnedarea.theme-dark .ba-badge.severity-high { color: #f87171; background: #3a1a1a; }
.nf-app.nf-burnedarea.theme-dark .ba-badge.severity-moderate { color: #fbbf24; background: #3a2b1a; }
.nf-app.nf-burnedarea.theme-dark .ba-badge.severity-low { color: #7ab8e8; background: #1a2e3f; }

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

/* ─── Responsive ─── */
@media (max-width: 1200px) {
    .ba-content { padding-right: 22px; padding-left: 22px; }
    .ba-stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .ba-filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
    .ba-main { margin-left: 0; }
    .ba-mobile-menu { display: grid; }
    .ba-analysis-grid { grid-template-columns: 1fr; }
}

@media (max-width: 620px) {
    .ba-topbar { min-height: 72px; padding: 12px 14px; }
    .ba-breadcrumb { gap: 5px; font-size: 10px; }
    .ba-topbar-subtitle { font-size: 10px; }
    .ba-content { padding: 22px 13px 18px; }
    .ba-page-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 16px;
    }
    .ba-page-heading h1 { font-size: 30px; }
    .ba-period-card { width: 100%; }
    .ba-filter-panel, .ba-panel { padding: 15px; }
    .ba-filter-grid { grid-template-columns: 1fr; }
    .ba-stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .ba-stat-card { padding: 13px 11px; }
    .ba-stat-top { gap: 7px; margin-bottom: 15px; }
    .ba-stat-icon { width: 30px; height: 30px; flex-basis: 30px; font-size: 17px; }
    .ba-stat-label { font-size: 10px; }
    .ba-stat-value { font-size: 23px; }
    .ba-stat-value small { font-size: 10px; }
}
</style>
