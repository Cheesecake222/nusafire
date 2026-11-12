
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useTheme } from '@/composables/useTheme';

type Hotspot = {
    id: number;
    latitude: number;
    longitude: number;
    date: string;
    time: string;
    confidence: 'low' | 'nominal' | 'high';
    frp: number;
    satellite: string;
    region: string;
};

const { theme, initializeTheme, toggleTheme } = useTheme();

const mapElement = ref<HTMLDivElement | null>(null);
const mapReady = ref(false);
const selectedHotspot = ref<Hotspot | null>(null);
const selectedRegion = ref('all');
const selectedConfidence = ref('all');
const searchText = ref('');
const startDate = ref('');
const endDate = ref('');
const showSidebar = ref(false);

let map: L.Map | null = null;
let markerLayer: L.LayerGroup | null = null;

const regions = [
    { value: 'all', label: 'Seluruh Indonesia' },
    { value: 'Sumatra', label: 'Sumatra' },
    { value: 'Kalimantan', label: 'Kalimantan' },
    { value: 'Sulawesi', label: 'Sulawesi' },
    { value: 'Papua', label: 'Papua' },
];

const demoHotspots: Hotspot[] = [
    { id: 1, latitude: 1.12, longitude: 102.20, date: '2026-10-28', time: '03:20', confidence: 'high', frp: 18.4, satellite: 'MODIS', region: 'Sumatra' },
    { id: 2, latitude: -0.72, longitude: 101.45, date: '2026-10-28', time: '04:10', confidence: 'nominal', frp: 9.2, satellite: 'VIIRS', region: 'Sumatra' },
    { id: 3, latitude: -2.45, longitude: 103.80, date: '2026-10-29', time: '05:30', confidence: 'high', frp: 31.6, satellite: 'VIIRS', region: 'Sumatra' },
    { id: 4, latitude: 0.85, longitude: 110.20, date: '2026-10-29', time: '06:15', confidence: 'nominal', frp: 12.7, satellite: 'MODIS', region: 'Kalimantan' },
    { id: 5, latitude: -1.75, longitude: 113.40, date: '2026-10-30', time: '02:40', confidence: 'high', frp: 24.1, satellite: 'VIIRS', region: 'Kalimantan' },
    { id: 6, latitude: -2.80, longitude: 115.20, date: '2026-10-30', time: '07:10', confidence: 'low', frp: 4.3, satellite: 'VIIRS', region: 'Kalimantan' },
    { id: 7, latitude: -1.20, longitude: 120.30, date: '2026-10-31', time: '03:55', confidence: 'nominal', frp: 7.8, satellite: 'MODIS', region: 'Sulawesi' },
    { id: 8, latitude: -3.50, longitude: 121.60, date: '2026-10-31', time: '05:20', confidence: 'high', frp: 20.5, satellite: 'VIIRS', region: 'Sulawesi' },
    { id: 9, latitude: -4.20, longitude: 138.40, date: '2026-11-01', time: '04:35', confidence: 'nominal', frp: 11.3, satellite: 'VIIRS', region: 'Papua' },
    { id: 10, latitude: -2.10, longitude: 140.10, date: '2026-11-01', time: '06:00', confidence: 'high', frp: 28.9, satellite: 'MODIS', region: 'Papua' },
    { id: 11, latitude: -0.40, longitude: 103.10, date: '2026-11-02', time: '02:10', confidence: 'low', frp: 3.5, satellite: 'VIIRS', region: 'Sumatra' },
    { id: 12, latitude: -1.60, longitude: 112.80, date: '2026-11-02', time: '05:45', confidence: 'nominal', frp: 14.8, satellite: 'VIIRS', region: 'Kalimantan' },
];

const filteredHotspots = computed(() => {
    return demoHotspots.filter((hotspot) => {
        const matchesRegion =
            selectedRegion.value === 'all' ||
            hotspot.region === selectedRegion.value;

        const matchesConfidence =
            selectedConfidence.value === 'all' ||
            hotspot.confidence === selectedConfidence.value;

        const matchesSearch =
            !searchText.value ||
            hotspot.region.toLowerCase().includes(searchText.value.toLowerCase()) ||
            hotspot.satellite.toLowerCase().includes(searchText.value.toLowerCase()) ||
            String(hotspot.id).includes(searchText.value);

        const matchesStart =
            !startDate.value || hotspot.date >= startDate.value;

        const matchesEnd =
            !endDate.value || hotspot.date <= endDate.value;

        return matchesRegion && matchesConfidence &&
            matchesSearch && matchesStart && matchesEnd;
    });
});

const highCount = computed(
    () => filteredHotspots.value.filter((item) => item.confidence === 'high').length,
);

const regionCount = computed(
    () => new Set(filteredHotspots.value.map((item) => item.region)).size,
);

function confidenceLabel(value: Hotspot['confidence']) {
    if (value === 'high') return 'Tinggi';
    if (value === 'nominal') return 'Sedang';
    return 'Rendah';
}

function markerColor(confidence: Hotspot['confidence']) {
    if (confidence === 'high') return '#ef4444';
    if (confidence === 'nominal') return '#f59e0b';
    return '#38bdf8';
}

function createMarkerIcon(confidence: Hotspot['confidence']) {
    return L.divIcon({
        className: 'hotspot-marker-wrapper',
        html: `<span class="hotspot-marker" style="--marker-color:${markerColor(confidence)}"></span>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9],
    });
}

function selectHotspot(hotspot: Hotspot) {
    selectedHotspot.value = hotspot;

    if (map) {
        map.flyTo([hotspot.latitude, hotspot.longitude], 7, {
            duration: 0.7,
        });
    }
}

function renderMarkers() {
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();

    filteredHotspots.value.forEach((hotspot) => {
        const marker = L.marker(
            [hotspot.latitude, hotspot.longitude],
            { icon: createMarkerIcon(hotspot.confidence) },
        );

        marker.bindPopup(`
            <div class="popup-content">
                <strong>Hotspot #${hotspot.id}</strong>
                <p>Wilayah: ${hotspot.region}</p>
                <p>Tanggal: ${hotspot.date}</p>
                <p>Confidence: ${confidenceLabel(hotspot.confidence)}</p>
                <p>FRP: ${hotspot.frp} MW</p>
            </div>
        `);

        marker.on('click', () => {
            selectedHotspot.value = hotspot;
        });

        marker.addTo(markerLayer!);
    });
}

function resetFilters() {
    selectedRegion.value = 'all';
    selectedConfidence.value = 'all';
    searchText.value = '';
    startDate.value = '';
    endDate.value = '';
    selectedHotspot.value = null;
}

function downloadCsv() {
    const header = [
        'id', 'latitude', 'longitude', 'date', 'time',
        'confidence', 'frp_mw', 'satellite', 'region',
    ];

    const rows = filteredHotspots.value.map((item) => [
        item.id,
        item.latitude,
        item.longitude,
        item.date,
        item.time,
        item.confidence,
        item.frp,
        item.satellite,
        item.region,
    ]);

    const csv = [header, ...rows]
        .map((row) => row.join(','))
        .join('\n');

    const blob = new Blob(['\uFEFF' + csv], {
        type: 'text/csv;charset=utf-8;',
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = 'nusafire-hotspot-demo.csv';
    link.click();

    URL.revokeObjectURL(url);
}

watch(filteredHotspots, renderMarkers);

watch(theme, async () => {
    await nextTick();
    map?.invalidateSize();
});

onMounted(async () => {
    initializeTheme();
    await nextTick();

    if (!mapElement.value) return;

    map = L.map(mapElement.value, {
        zoomControl: false,
        scrollWheelZoom: true,
    }).setView([-2.5, 118], 4.5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);
    renderMarkers();
    mapReady.value = true;

    setTimeout(() => map?.invalidateSize(), 200);
});

onBeforeUnmount(() => {
    map?.remove();
    map = null;
    markerLayer = null;
});
</script>

<template>
    <Head title="Hotspot Map | NusaFire" />

    <main class="hotspot-page" :class="`theme-${theme}`">
        <aside class="sidebar" :class="{ 'sidebar-open': showSidebar }">
            <Link href="/" class="brand">
                <span class="brand-symbol">N</span>
                <span>
                    <strong>NusaFire</strong>
                    <small>FOREST INTELLIGENCE</small>
                </span>
            </Link>

            <div class="sidebar-label">WORKSPACE</div>

            <nav class="navigation">
                <Link href="/dashboard" class="nav-item">
                    <span>▦</span> Overview
                </Link>
                <Link href="/hotspot-map" class="nav-item active">
                    <span>⌖</span> Hotspot Map
                </Link>
                <Link href="/dashboard" class="nav-item">
                    <span>◷</span> Weather Analysis
                </Link>
                <Link href="/dashboard" class="nav-item">
                    <span>▤</span> Burned Area
                </Link>
            </nav>

            <div class="sidebar-bottom">
                <div class="data-status">
                    <span class="status-dot"></span>
                    <div>
                        <strong>Demo environment</strong>
                        <small>Sample data displayed</small>
                    </div>
                </div>
                <button class="theme-button" @click="toggleTheme">
                    <span>{{ theme === 'dark' ? '☀' : '☾' }}</span>
                    {{ theme === 'dark' ? 'Light mode' : 'Dark mode' }}
                </button>
            </div>
        </aside>

        <div v-if="showSidebar" class="mobile-overlay" @click="showSidebar = false"></div>

        <section class="main-content">
            <header class="topbar">
                <button class="mobile-menu" @click="showSidebar = !showSidebar">☰</button>
                <div class="breadcrumb">Workspace <span>/</span> <strong>Hotspot Map</strong></div>
                <div class="topbar-right">
                    <span class="live-indicator"><i></i> MAP VIEW</span>
                    <button class="icon-button" title="Ganti tema" @click="toggleTheme">
                        {{ theme === 'dark' ? '☀' : '☾' }}
                    </button>
                </div>
            </header>

            <div class="page-body">
                <div class="page-heading">
                    <div>
                        <div class="eyebrow">GEOSPATIAL MONITORING</div>
                        <h1>Hotspot Map</h1>
                        <p>Pantau persebaran titik panas di wilayah Indonesia.</p>
                    </div>
                    <button class="export-button" @click="downloadCsv">
                        <span>↓</span> Export CSV
                    </button>
                </div>

                <div class="demo-notice">
                    <span class="notice-icon">ⓘ</span>
                    <div>
                        <strong>Mode demonstrasi</strong>
                        <p>Marker dan statistik saat ini menggunakan data contoh, bukan deteksi aktual NASA FIRMS.</p>
                    </div>
                </div>

                <div class="stat-grid">
                    <article class="stat-card">
                        <div class="stat-top">
                            <span>Total hotspot</span>
                            <span class="stat-icon orange">⌖</span>
                        </div>
                        <div class="stat-value">{{ filteredHotspots.length }}</div>
                        <div class="stat-foot">Titik pada data contoh yang difilter</div>
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span>Confidence tinggi</span>
                            <span class="stat-icon red">↗</span>
                        </div>
                        <div class="stat-value">{{ highCount }}</div>
                        <div class="stat-foot">Dari hasil filter saat ini</div>
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span>Wilayah terpantau</span>
                            <span class="stat-icon green">◎</span>
                        </div>
                        <div class="stat-value">{{ regionCount }}</div>
                        <div class="stat-foot">Wilayah dengan marker yang tampil</div>
                    </article>

                    <article class="stat-card">
                        <div class="stat-top">
                            <span>Rata-rata FRP</span>
                            <span class="stat-icon blue">ϟ</span>
                        </div>
                        <div class="stat-value">
                            {{
                                filteredHotspots.length
                                    ? (filteredHotspots.reduce((sum, item) => sum + item.frp, 0) /
                                        filteredHotspots.length).toFixed(1)
                                    : '—'
                            }}
                            <small>MW</small>
                        </div>
                        <div class="stat-foot">Fire Radiative Power data contoh</div>
                    </article>
                </div>

                <section class="filter-panel">
                    <div class="filter-heading">
                        <div>
                            <h2>Filter data</h2>
                            <p>Sesuaikan hotspot yang ditampilkan di peta.</p>
                        </div>
                        <button class="reset-button" @click="resetFilters">Reset filter</button>
                    </div>

                    <div class="filter-grid">
                        <label class="filter-field">
                            <span>Wilayah</span>
                            <select v-model="selectedRegion">
                                <option v-for="region in regions" :key="region.value" :value="region.value">
                                    {{ region.label }}
                                </option>
                            </select>
                        </label>

                        <label class="filter-field">
                            <span>Confidence</span>
                            <select v-model="selectedConfidence">
                                <option value="all">Semua tingkat</option>
                                <option value="high">Tinggi</option>
                                <option value="nominal">Sedang</option>
                                <option value="low">Rendah</option>
                            </select>
                        </label>

                        <label class="filter-field">
                            <span>Tanggal mulai</span>
                            <input v-model="startDate" type="date" />
                        </label>

                        <label class="filter-field">
                            <span>Tanggal akhir</span>
                            <input v-model="endDate" type="date" />
                        </label>

                        <label class="filter-field search-field">
                            <span>Cari data</span>
                            <input v-model="searchText" type="search" placeholder="ID, wilayah, satelit..." />
                        </label>
                    </div>
                </section>

                <div class="map-layout">
                    <section class="map-card">
                        <div class="map-card-heading">
                            <div>
                                <h2>Indonesia hotspot distribution</h2>
                                <p><span class="status-dot"></span> {{ filteredHotspots.length }} marker ditampilkan</p>
                            </div>
                            <span class="map-badge">OpenStreetMap</span>
                        </div>

                        <div ref="mapElement" class="map-container"></div>

                        <div class="map-legend">
                            <span><i class="legend-dot high"></i> Confidence tinggi</span>
                            <span><i class="legend-dot nominal"></i> Confidence sedang</span>
                            <span><i class="legend-dot low"></i> Confidence rendah</span>
                        </div>
                    </section>

                    <aside class="detail-card">
                        <div class="detail-heading">
                            <div>
                                <h2>Detail hotspot</h2>
                                <p>Informasi titik terpilih</p>
                            </div>
                            <span class="detail-crosshair">⌖</span>
                        </div>

                        <template v-if="selectedHotspot">
                            <div class="selected-id">HOTSPOT #{{ selectedHotspot.id }}</div>
                            <div class="detail-region">{{ selectedHotspot.region }}</div>

                            <div class="confidence-pill" :class="selectedHotspot.confidence">
                                <span></span>
                                Confidence {{ confidenceLabel(selectedHotspot.confidence) }}
                            </div>

                            <div class="detail-list">
                                <div>
                                    <span>Latitude</span>
                                    <strong>{{ selectedHotspot.latitude.toFixed(5) }}</strong>
                                </div>
                                <div>
                                    <span>Longitude</span>
                                    <strong>{{ selectedHotspot.longitude.toFixed(5) }}</strong>
                                </div>
                                <div>
                                    <span>Tanggal deteksi</span>
                                    <strong>{{ selectedHotspot.date }}</strong>
                                </div>
                                <div>
                                    <span>Waktu</span>
                                    <strong>{{ selectedHotspot.time }} UTC*</strong>
                                </div>
                                <div>
                                    <span>FRP</span>
                                    <strong>{{ selectedHotspot.frp }} MW</strong>
                                </div>
                                <div>
                                    <span>Satelit</span>
                                    <strong>{{ selectedHotspot.satellite }}</strong>
                                </div>
                            </div>

                            <button class="clear-selection" @click="selectedHotspot = null">
                                Tutup detail
                            </button>
                        </template>

                        <div v-else class="empty-detail">
                            <div class="empty-icon">⌖</div>
                            <strong>Belum ada titik dipilih</strong>
                            <p>Pilih marker di peta atau pilih salah satu baris data di bawah.</p>
                        </div>

                        <div class="detail-note">
                            *Waktu pada data contoh. Zona waktu data aktual akan mengikuti metadata dataset.
                        </div>
                    </aside>
                </div>

                <section class="table-card">
                    <div class="table-heading">
                        <div>
                            <h2>Daftar hotspot</h2>
                            <p>Menampilkan {{ filteredHotspots.length }} titik berdasarkan filter.</p>
                        </div>
                    </div>

                    <div class="table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Wilayah</th>
                                    <th>Tanggal</th>
                                    <th>Koordinat</th>
                                    <th>Confidence</th>
                                    <th>FRP (MW)</th>
                                    <th>Satelit</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="hotspot in filteredHotspots" :key="hotspot.id">
                                    <td class="id-cell">#{{ hotspot.id }}</td>
                                    <td>{{ hotspot.region }}</td>
                                    <td>{{ hotspot.date }}</td>
                                    <td class="coordinate-cell">
                                        {{ hotspot.latitude.toFixed(3) }}, {{ hotspot.longitude.toFixed(3) }}
                                    </td>
                                    <td>
                                        <span class="table-confidence" :class="hotspot.confidence">
                                            <i></i>{{ confidenceLabel(hotspot.confidence) }}
                                        </span>
                                    </td>
                                    <td>{{ hotspot.frp.toFixed(1) }}</td>
                                    <td>{{ hotspot.satellite }}</td>
                                    <td>
                                        <button class="view-button" @click="selectHotspot(hotspot)">
                                            Lihat
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="filteredHotspots.length === 0">
                                    <td colspan="8" class="no-results">
                                        Tidak ada hotspot yang sesuai dengan filter.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <footer class="page-footer">
                    <span>© 2026 NusaFire · Forest Intelligence</span>
                    <span>Prototype · Data contoh</span>
                </footer>
            </div>
        </section>
    </main>
</template>

<style>
.hotspot-page {
    --page: #f5f7f4;
    --surface: #ffffff;
    --surface-alt: #f8faf8;
    --text: #1d2922;
    --muted: #77827a;
    --border: #e5eae5;
    --green: #248451;
    --green-soft: #e7f5eb;
    --sidebar: #ffffff;
    --input: #ffffff;
    min-height: 100vh;
    display: flex;
    color: var(--text);
    background: var(--page);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
}

.hotspot-page.theme-dark {
    --page: #101713;
    --surface: #18211b;
    --surface-alt: #202a23;
    --text: #e8efe9;
    --muted: #9aa99d;
    --border: #303d33;
    --green: #65c98b;
    --green-soft: #203c2b;
    --sidebar: #151d17;
    --input: #202a23;
}

.hotspot-page * { box-sizing: border-box; }
.hotspot-page button, .hotspot-page input, .hotspot-page select { font: inherit; }
.hotspot-page button { cursor: pointer; }
.hotspot-page a { color: inherit; text-decoration: none; }

.hotspot-page .sidebar {
    width: 244px;
    flex-shrink: 0;
    min-height: 100vh;
    background: var(--sidebar);
    border-right: 1px solid var(--border);
    padding: 26px 16px 18px;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    z-index: 1000;
}

.hotspot-page .brand {
    display: flex;
    gap: 11px;
    align-items: center;
    padding: 0 7px 34px;
}

.hotspot-page .brand-symbol {
    display: grid;
    place-items: center;
    width: 39px;
    height: 39px;
    border-radius: 12px;
    background: #227b49;
    color: white;
    font-size: 23px;
    font-weight: 800;
}

.hotspot-page .brand strong { display: block; font-size: 17px; letter-spacing: -.5px; }
.hotspot-page .brand small { display: block; margin-top: 3px; font-size: 8px; letter-spacing: 1.25px; color: var(--muted); }
.hotspot-page .sidebar-label { color: var(--muted); font-size: 9px; font-weight: 750; letter-spacing: 1.5px; padding: 0 11px 12px; }

.hotspot-page .navigation { display: grid; gap: 5px; }
.hotspot-page .nav-item { display: flex; gap: 12px; align-items: center; padding: 12px; border-radius: 9px; color: var(--muted); font-weight: 550; transition: .2s; }
.hotspot-page .nav-item > span { width: 18px; text-align: center; font-size: 18px; }
.hotspot-page .nav-item:hover { background: var(--surface-alt); color: var(--text); }
.hotspot-page .nav-item.active { background: var(--green-soft); color: var(--green); font-weight: 700; }

.hotspot-page .sidebar-bottom { margin-top: auto; display: grid; gap: 15px; }
.hotspot-page .data-status { display: flex; align-items: center; gap: 10px; border: 1px solid var(--border); padding: 13px 10px; border-radius: 10px; }
.hotspot-page .data-status strong, .hotspot-page .data-status small { display: block; }
.hotspot-page .data-status strong { font-size: 11px; }
.hotspot-page .data-status small { margin-top: 4px; color: var(--muted); font-size: 10px; }
.hotspot-page .status-dot { display: inline-block; flex-shrink: 0; width: 7px; height: 7px; border-radius: 50%; background: #e6a53b; }
.hotspot-page .theme-button { display: flex; align-items: center; gap: 10px; padding: 11px; border: 1px solid var(--border); background: transparent; color: var(--text); border-radius: 9px; text-align: left; }
.hotspot-page .theme-button span { font-size: 17px; }

.hotspot-page .main-content { flex: 1; min-width: 0; }
.hotspot-page .topbar { min-height: 68px; padding: 0 32px; display: flex; align-items: center; justify-content: space-between; gap: 16px; background: var(--surface); border-bottom: 1px solid var(--border); }
.hotspot-page .breadcrumb { color: var(--muted); font-size: 12px; }
.hotspot-page .breadcrumb span { padding: 0 9px; color: var(--border); }
.hotspot-page .breadcrumb strong { color: var(--text); }
.hotspot-page .topbar-right { display: flex; align-items: center; gap: 16px; }
.hotspot-page .live-indicator { display: flex; align-items: center; gap: 7px; font-size: 9px; letter-spacing: 1px; color: var(--muted); font-weight: 800; }
.hotspot-page .live-indicator i { width: 7px; height: 7px; background: var(--green); border-radius: 50%; }
.hotspot-page .icon-button, .hotspot-page .mobile-menu { border: 1px solid var(--border); background: var(--surface); color: var(--text); border-radius: 8px; width: 35px; height: 35px; font-size: 17px; }
.hotspot-page .mobile-menu { display: none; }

.hotspot-page .page-body { max-width: 1600px; padding: 30px 32px 20px; margin: auto; }
.hotspot-page .page-heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 22px; }
.hotspot-page .eyebrow { color: var(--green); font-size: 9px; font-weight: 800; letter-spacing: 1.7px; margin-bottom: 9px; }
.hotspot-page h1 { font-size: clamp(25px, 3vw, 32px); letter-spacing: -1.2px; margin: 0; font-weight: 750; }
.hotspot-page .page-heading p { color: var(--muted); margin: 8px 0 0; font-size: 12px; }
.hotspot-page .export-button { background: #247c49; color: white; border: 0; padding: 11px 15px; border-radius: 8px; font-weight: 650; display: flex; gap: 8px; align-items: center; }
.hotspot-page .export-button:hover { background: #19663a; }

.hotspot-page .demo-notice { display: flex; gap: 12px; align-items: flex-start; padding: 13px 15px; border-radius: 10px; background: var(--green-soft); margin-bottom: 19px; color: var(--text); }
.hotspot-page .notice-icon { color: var(--green); font-size: 18px; }
.hotspot-page .demo-notice strong { font-size: 11px; }
.hotspot-page .demo-notice p { color: var(--muted); margin: 4px 0 0; font-size: 11px; line-height: 1.6; }

.hotspot-page .stat-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 15px; margin-bottom: 20px; }
.hotspot-page .stat-card, .hotspot-page .filter-panel, .hotspot-page .map-card, .hotspot-page .detail-card, .hotspot-page .table-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; }
.hotspot-page .stat-card { padding: 17px; min-width: 0; }
.hotspot-page .stat-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; color: var(--muted); font-size: 11px; }
.hotspot-page .stat-icon { display: grid; place-items: center; width: 32px; height: 32px; border-radius: 9px; font-size: 18px; }
.hotspot-page .stat-icon.orange { background: #fff2df; color: #d98b1c; }
.hotspot-page .stat-icon.red { background: #ffebeb; color: #e44848; }
.hotspot-page .stat-icon.green { background: #e5f6eb; color: #248451; }
.hotspot-page .stat-icon.blue { background: #e6f3ff; color: #3486cc; }
.hotspot-page .stat-value { font-size: 29px; font-weight: 750; letter-spacing: -1px; margin-top: 15px; }
.hotspot-page .stat-value small { font-size: 11px; color: var(--muted); font-weight: 500; letter-spacing: 0; }
.hotspot-page .stat-foot { margin-top: 7px; color: var(--muted); font-size: 10px; }

.hotspot-page .filter-panel { padding: 19px; margin-bottom: 20px; }
.hotspot-page .filter-heading, .hotspot-page .map-card-heading, .hotspot-page .detail-heading, .hotspot-page .table-heading { display: flex; justify-content: space-between; align-items: center; gap: 14px; }
.hotspot-page h2 { margin: 0; font-size: 13px; font-weight: 750; letter-spacing: -.1px; }
.hotspot-page .filter-heading p, .hotspot-page .map-card-heading p, .hotspot-page .detail-heading p, .hotspot-page .table-heading p { color: var(--muted); font-size: 10px; margin: 5px 0 0; }
.hotspot-page .reset-button { background: transparent; border: 0; color: var(--green); font-size: 11px; font-weight: 700; }
.hotspot-page .filter-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
.hotspot-page .filter-field { display: grid; gap: 7px; min-width: 0; }
.hotspot-page .filter-field > span { color: var(--muted); font-size: 10px; font-weight: 650; }
.hotspot-page .filter-field input, .hotspot-page .filter-field select { width: 100%; min-width: 0; height: 38px; padding: 0 10px; border: 1px solid var(--border); background: var(--input); color: var(--text); border-radius: 7px; outline: none; font-size: 11px; }
.hotspot-page .filter-field input:focus, .hotspot-page .filter-field select:focus { border-color: var(--green); box-shadow: 0 0 0 2px color-mix(in srgb, var(--green) 15%, transparent); }

.hotspot-page .map-layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 17px; align-items: stretch; margin-bottom: 20px; }
.hotspot-page .map-card { min-width: 0; overflow: hidden; }
.hotspot-page .map-card-heading { padding: 18px 19px; }
.hotspot-page .map-card-heading p { display: flex; align-items: center; gap: 7px; }
.hotspot-page .map-card-heading .status-dot { background: var(--green); }
.hotspot-page .map-badge { background: var(--surface-alt); color: var(--muted); padding: 6px 9px; border-radius: 6px; font-size: 9px; }
.hotspot-page .map-container { height: 440px; width: 100%; z-index: 1; background: #e5eae5; }
.hotspot-page .map-legend { display: flex; flex-wrap: wrap; gap: 16px; padding: 14px 18px; border-top: 1px solid var(--border); color: var(--muted); font-size: 10px; }
.hotspot-page .map-legend span { display: flex; align-items: center; gap: 6px; }
.hotspot-page .legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.hotspot-page .legend-dot.high { background: #ef4444; }
.hotspot-page .legend-dot.nominal { background: #f59e0b; }
.hotspot-page .legend-dot.low { background: #38bdf8; }

.hotspot-page .detail-card { padding: 18px; min-width: 0; }
.hotspot-page .detail-crosshair { font-size: 22px; color: var(--green); }
.hotspot-page .selected-id { margin-top: 28px; color: var(--muted); font-size: 9px; font-weight: 800; letter-spacing: 1px; }
.hotspot-page .detail-region { font-size: 23px; font-weight: 750; letter-spacing: -.6px; margin-top: 8px; }
.hotspot-page .confidence-pill { display: inline-flex; align-items: center; gap: 7px; margin-top: 12px; padding: 7px 9px; border-radius: 6px; font-size: 10px; }
.hotspot-page .confidence-pill > span { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.hotspot-page .confidence-pill.high { background: #ffebeb; color: #d83c3c; }
.hotspot-page .confidence-pill.nominal { background: #fff3dd; color: #b97a14; }
.hotspot-page .confidence-pill.low { background: #e4f4ff; color: #267db6; }
.hotspot-page .detail-list { display: grid; margin-top: 21px; }
.hotspot-page .detail-list > div { display: flex; justify-content: space-between; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.hotspot-page .detail-list span { color: var(--muted); font-size: 10px; }
.hotspot-page .detail-list strong { font-size: 10px; font-weight: 650; text-align: right; overflow-wrap: anywhere; }
.hotspot-page .clear-selection { margin-top: 15px; width: 100%; background: var(--surface-alt); border: 1px solid var(--border); color: var(--text); border-radius: 7px; padding: 9px; font-size: 10px; }
.hotspot-page .empty-detail { min-height: 280px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.hotspot-page .empty-icon { display: grid; place-items: center; width: 49px; height: 49px; border-radius: 50%; background: var(--green-soft); color: var(--green); font-size: 26px; margin-bottom: 16px; }
.hotspot-page .empty-detail strong { font-size: 11px; }
.hotspot-page .empty-detail p { color: var(--muted); font-size: 10px; line-height: 1.7; max-width: 190px; }
.hotspot-page .detail-note { border-top: 1px solid var(--border); padding-top: 13px; margin-top: 18px; color: var(--muted); font-size: 9px; line-height: 1.7; }

.hotspot-page .table-card { overflow: hidden; }
.hotspot-page .table-heading { padding: 18px 19px; }
.hotspot-page .table-scroll { overflow-x: auto; }
.hotspot-page table { width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; }
.hotspot-page thead { background: var(--surface-alt); }
.hotspot-page th { color: var(--muted); font-size: 9px; font-weight: 700; padding: 12px 15px; }
.hotspot-page td { padding: 13px 15px; border-top: 1px solid var(--border); font-size: 10px; }
.hotspot-page .id-cell { color: var(--green); font-weight: 750; }
.hotspot-page .coordinate-cell { color: var(--muted); font-variant-numeric: tabular-nums; }
.hotspot-page .table-confidence { display: inline-flex; align-items: center; gap: 6px; padding: 5px 7px; border-radius: 5px; font-size: 9px; }
.hotspot-page .table-confidence i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.hotspot-page .table-confidence.high { background: #ffebeb; color: #d83c3c; }
.hotspot-page .table-confidence.nominal { background: #fff3dd; color: #b97a14; }
.hotspot-page .table-confidence.low { background: #e4f4ff; color: #267db6; }
.hotspot-page .view-button { border: 1px solid var(--border); background: var(--surface); color: var(--green); border-radius: 5px; padding: 6px 9px; font-size: 9px; font-weight: 700; }
.hotspot-page .view-button:hover { background: var(--green-soft); }
.hotspot-page .no-results { text-align: center; color: var(--muted); padding: 30px; }
.hotspot-page .page-footer { display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font-size: 9px; padding: 21px 0 5px; }

.hotspot-marker-wrapper { background: transparent; border: 0; }
.hotspot-marker { display: block; width: 13px; height: 13px; border-radius: 50%; background: var(--marker-color); border: 2px solid white; box-shadow: 0 0 0 4px color-mix(in srgb, var(--marker-color) 25%, transparent), 0 1px 5px #0005; }
.hotspot-marker-wrapper:hover { z-index: 1000 !important; }
.hotspot-page .leaflet-popup-content-wrapper, .hotspot-page .leaflet-popup-tip { background: var(--surface); color: var(--text); }
.hotspot-page .popup-content { font-size: 12px; line-height: 1.5; }
.hotspot-page .popup-content strong { color: var(--green); }
.hotspot-page .popup-content p { margin: 4px 0; }
.hotspot-page .mobile-overlay { display: none; }

@media (max-width: 1200px) {
    .hotspot-page .filter-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .hotspot-page .map-layout { grid-template-columns: minmax(0, 1fr) 250px; }
    .hotspot-page .stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 850px) {
    .hotspot-page .sidebar { position: fixed; left: 0; top: 0; transform: translateX(-100%); transition: transform .25s; box-shadow: 10px 0 35px #0001; }
    .hotspot-page .sidebar.sidebar-open { transform: translateX(0); }
    .hotspot-page .mobile-overlay { display: block; position: fixed; inset: 0; background: #0006; z-index: 999; }
    .hotspot-page .mobile-menu { display: block; }
    .hotspot-page .topbar { padding: 0 18px; }
    .hotspot-page .breadcrumb { margin-right: auto; }
    .hotspot-page .page-body { padding: 24px 18px; }
    .hotspot-page .map-layout { grid-template-columns: 1fr; }
    .hotspot-page .detail-card { min-height: auto; }
    .hotspot-page .empty-detail { min-height: 180px; }
    .hotspot-page .detail-list { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; }
}

@media (max-width: 560px) {
    .hotspot-page .page-body { padding: 20px 12px; }
    .hotspot-page .topbar { min-height: 58px; padding: 0 12px; }
    .hotspot-page .live-indicator { display: none; }
    .hotspot-page .page-heading { align-items: flex-start; }
    .hotspot-page .export-button { padding: 10px; font-size: 10px; }
    .hotspot-page .stat-grid { gap: 9px; }
    .hotspot-page .stat-card { padding: 12px; }
    .hotspot-page .stat-value { font-size: 25px; }
    .hotspot-page .stat-foot { line-height: 1.5; }
    .hotspot-page .filter-panel { padding: 14px; }
    .hotspot-page .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .hotspot-page .search-field { grid-column: 1 / -1; }
    .hotspot-page .map-container { height: 350px; }
    .hotspot-page .map-legend { gap: 10px; }
    .hotspot-page .page-footer { flex-direction: column; }
}
</style>
