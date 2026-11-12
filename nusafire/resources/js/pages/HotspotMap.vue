
<script setup lang="ts">
import {
    computed,
    nextTick,
    onBeforeUnmount,
    onMounted,
    ref,
    watch,
} from 'vue';
import { Head } from '@inertiajs/vue3';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import AppSidebar from '@/components/AppSidebar.vue';
import { useTheme } from '@/composables/useTheme';

type Confidence = 'low' | 'nominal' | 'high';

type Hotspot = {
    id: number;
    latitude: number;
    longitude: number;
    date: string;
    time: string;
    confidence: Confidence;
    frp: number;
    satellite: string;
    region: string;
};

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const mapElement = ref<HTMLDivElement | null>(null);
const searchQuery = ref('');
const selectedRegion = ref('all');
const selectedConfidence = ref('all');
const startDate = ref('');
const endDate = ref('');
const selectedHotspot = ref<Hotspot | null>(null);
const mapReady = ref(false);
const copyMessage = ref('');

let map: L.Map | null = null;
let markerLayer: L.LayerGroup | null = null;
let copyMessageTimeout: ReturnType<typeof setTimeout> | null = null;

const hotspots = ref<Hotspot[]>([
    { id: 1, latitude: -0.7893, longitude: 100.65, date: '2026-11-02', time: '02:15', confidence: 'high', frp: 45.6, satellite: 'SNPP', region: 'Sumatra' },
    { id: 2, latitude: -1.42, longitude: 102.1, date: '2026-11-02', time: '03:40', confidence: 'nominal', frp: 18.2, satellite: 'NOAA-20', region: 'Sumatra' },
    { id: 3, latitude: -2.15, longitude: 113.85, date: '2026-11-01', time: '04:20', confidence: 'high', frp: 67.8, satellite: 'SNPP', region: 'Kalimantan' },
    { id: 4, latitude: -0.5, longitude: 114.25, date: '2026-11-01', time: '05:10', confidence: 'low', frp: 8.4, satellite: 'NOAA-20', region: 'Kalimantan' },
    { id: 5, latitude: -2.85, longitude: 116.1, date: '2026-10-31', time: '06:30', confidence: 'nominal', frp: 23.1, satellite: 'NOAA-21', region: 'Kalimantan' },
    { id: 6, latitude: -3.8, longitude: 119.9, date: '2026-10-31', time: '07:15', confidence: 'high', frp: 51.3, satellite: 'SNPP', region: 'Sulawesi' },
    { id: 7, latitude: -1.2, longitude: 120.4, date: '2026-10-30', time: '08:05', confidence: 'low', frp: 5.7, satellite: 'NOAA-20', region: 'Sulawesi' },
    { id: 8, latitude: -4.2, longitude: 138.1, date: '2026-10-30', time: '09:25', confidence: 'nominal', frp: 29.6, satellite: 'NOAA-21', region: 'Papua' },
    { id: 9, latitude: -3.1, longitude: 140.5, date: '2026-10-29', time: '10:40', confidence: 'high', frp: 72.4, satellite: 'SNPP', region: 'Papua' },
    { id: 10, latitude: -0.9, longitude: 101.3, date: '2026-10-29', time: '11:20', confidence: 'nominal', frp: 14.9, satellite: 'NOAA-20', region: 'Sumatra' },
    { id: 11, latitude: -1.8, longitude: 110.8, date: '2026-10-28', time: '12:10', confidence: 'low', frp: 6.2, satellite: 'NOAA-21', region: 'Kalimantan' },
    { id: 12, latitude: -5.1, longitude: 122.6, date: '2026-10-28', time: '13:45', confidence: 'high', frp: 38.7, satellite: 'SNPP', region: 'Sulawesi' },
]);

const regions = computed(() =>
    [...new Set(hotspots.value.map((item) => item.region))].sort(),
);

const filteredHotspots = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();

    return hotspots.value.filter((item) => {
        const matchesRegion =
            selectedRegion.value === 'all' ||
            item.region === selectedRegion.value;

        const matchesConfidence =
            selectedConfidence.value === 'all' ||
            item.confidence === selectedConfidence.value;

        const matchesSearch =
            !query ||
            [
                item.region,
                item.satellite,
                item.date,
                String(item.id),
                String(item.latitude),
                String(item.longitude),
            ].some((value) => value.toLowerCase().includes(query));

        const matchesStart = !startDate.value || item.date >= startDate.value;
        const matchesEnd = !endDate.value || item.date <= endDate.value;

        return matchesRegion && matchesConfidence &&
            matchesSearch && matchesStart && matchesEnd;
    });
});

const dateRangeInvalid = computed(
    () => Boolean(startDate.value && endDate.value) &&
        startDate.value > endDate.value,
);

const totalHotspots = computed(() => filteredHotspots.value.length);

const highConfidenceCount = computed(
    () => filteredHotspots.value.filter(
        (item) => item.confidence === 'high',
    ).length,
);

const totalRegions = computed(
    () => new Set(filteredHotspots.value.map((item) => item.region)).size,
);

const averageFrp = computed(() => {
    const items = filteredHotspots.value;
    return items.length
        ? items.reduce((sum, item) => sum + item.frp, 0) / items.length
        : 0;
});

function confidenceLabel(value: Confidence): string {
    return {
        low: 'Rendah',
        nominal: 'Sedang',
        high: 'Tinggi',
    }[value];
}

function confidenceColor(value: Confidence): string {
    return {
        low: '#3b82f6',
        nominal: '#f59e0b',
        high: '#ef4444',
    }[value];
}

function createMarkerIcon(value: Confidence): L.DivIcon {
    return L.divIcon({
        className: 'nf-hotspot-marker-wrapper',
        html: `<div class="nf-hotspot-marker" style="--marker-color:${confidenceColor(value)}"><span></span></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12],
    });
}

function escapeHtml(value: string | number): string {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function popupContent(item: Hotspot): string {
    return `
        <div class="nf-hotspot-popup">
            <strong>Hotspot #${item.id}</strong>
            <p>Wilayah: ${escapeHtml(item.region)}</p>
            <p>Tanggal: ${escapeHtml(item.date)}</p>
            <p>Waktu: ${escapeHtml(item.time)}</p>
            <p>Confidence: ${confidenceLabel(item.confidence)}</p>
            <p>FRP: ${item.frp.toFixed(1)} MW</p>
        </div>
    `;
}

function renderMarkers(): void {
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();

    filteredHotspots.value.forEach((item) => {
        const marker = L.marker(
            [item.latitude, item.longitude],
            { icon: createMarkerIcon(item.confidence) },
        );

        marker.bindPopup(popupContent(item));

        marker.on('click', () => {
            selectedHotspot.value = item;
        });

        markerLayer?.addLayer(marker);
    });
}

function initializeMap(): void {
    if (!mapElement.value || map) return;

    map = L.map(mapElement.value, {
        center: [-2.5, 118],
        zoom: 5,
        zoomControl: true,
        scrollWheelZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
    }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);
    renderMarkers();
    mapReady.value = true;

    nextTick(() => map?.invalidateSize());
}

function focusHotspot(item: Hotspot): void {
    selectedHotspot.value = item;

    if (!map) return;

    map.flyTo(
        [item.latitude, item.longitude],
        Math.max(map.getZoom(), 8),
        { duration: 0.7 },
    );

    markerLayer?.eachLayer((layer) => {
        if (
            layer instanceof L.Marker &&
            layer.getLatLng().lat === item.latitude &&
            layer.getLatLng().lng === item.longitude
        ) {
            layer.openPopup();
        }
    });
}

function resetFilters(): void {
    searchQuery.value = '';
    selectedRegion.value = 'all';
    selectedConfidence.value = 'all';
    startDate.value = '';
    endDate.value = '';
    selectedHotspot.value = null;
}

function showCopyMessage(message: string): void {
    copyMessage.value = message;

    if (copyMessageTimeout) clearTimeout(copyMessageTimeout);

    copyMessageTimeout = setTimeout(() => {
        copyMessage.value = '';
        copyMessageTimeout = null;
    }, 2500);
}

async function copyCoordinates(): Promise<void> {
    const item = selectedHotspot.value;
    if (!item) return;

    const coordinates = `${item.latitude}, ${item.longitude}`;

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(coordinates);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = coordinates;
            textarea.setAttribute('readonly', '');
            textarea.style.position = 'fixed';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);
            textarea.select();

            const copied = document.execCommand('copy');
            textarea.remove();

            if (!copied) throw new Error('Clipboard tidak tersedia.');
        }

        showCopyMessage('Koordinat berhasil disalin.');
    } catch (error) {
        console.error(error);
        showCopyMessage('Gagal menyalin. Silakan salin koordinat secara manual.');
    }
}

function exportCsv(): void {
    const headers = [
        'ID', 'Latitude', 'Longitude', 'Tanggal', 'Waktu',
        'Confidence', 'FRP (MW)', 'Satelit', 'Wilayah',
    ];

    const rows = filteredHotspots.value.map((item) => [
        item.id,
        item.latitude,
        item.longitude,
        item.date,
        item.time,
        confidenceLabel(item.confidence),
        item.frp,
        item.satellite,
        item.region,
    ]);

    const csv = [headers, ...rows]
        .map((row) => row.map(
            (value) => `"${String(value).replace(/"/g, '""')}"`,
        ).join(','))
        .join('\r\n');

    const blob = new Blob(['\uFEFF' + csv], {
        type: 'text/csv;charset=utf-8;',
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `nusafire-hotspots-${new Date().toISOString().slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

watch(filteredHotspots, (items) => {
    renderMarkers();

    if (
        selectedHotspot.value &&
        !items.some((item) => item.id === selectedHotspot.value?.id)
    ) {
        selectedHotspot.value = null;
    }
}, { flush: 'post' });

watch([startDate, endDate], ([start, end]) => {
    if (start && end && start > end) {
        showCopyMessage('Tanggal mulai tidak boleh melebihi tanggal akhir.');
    }
});

onMounted(async () => {
    await nextTick();
    initializeMap();
});

onBeforeUnmount(() => {
    if (copyMessageTimeout) clearTimeout(copyMessageTimeout);

    map?.remove();
    map = null;
    markerLayer = null;
});
</script>

<template>
    <Head title="Hotspot Map | NusaFire" />

    <main class="nf-app nf-hotspotmap" :class="`theme-${theme}`">
        <!-- Sidebar hanya berasal dari komponen bersama. -->
        <AppSidebar
            active-page="hotspot-map"
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <div class="nf-main" :class="{ 'nf-sidebar-collapsed': sidebarCollapsed }">
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        class="nf-icon-button nf-mobile-menu"
                        :class="{ 'nf-menu-visible': sidebarCollapsed }"
                        type="button"
                        aria-label="Buka navigasi"
                        @click="sidebarCollapsed = false; mobileMenuOpen = true"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                            <path d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>

                    <div>
                        <div class="nf-breadcrumb">NusaFire / Pemetaan</div>
                        <h1>Hotspot Map</h1>
                    </div>
                </div>

                <button
                    class="nf-icon-button"
                    type="button"
                    :aria-label="theme === 'dark' ? 'Aktifkan mode terang' : 'Aktifkan mode gelap'"
                    @click="toggleTheme"
                >
                    <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <circle cx="12" cy="12" r="4" />
                        <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z" />
                    </svg>
                </button>
            </header>

            <div class="nf-page-content">
                <section class="nf-page-heading">
                    <div>
                        <div class="nf-eyebrow">
                            <span></span> MONITORING KEBAKARAN
                        </div>
                        <h2>Pemetaan Titik Panas</h2>
                        <p>
                            Pantau persebaran hotspot dan analisis informasi
                            berdasarkan wilayah, tanggal, dan confidence.
                        </p>
                    </div>

                    <button class="nf-button nf-button-primary" type="button" @click="exportCsv">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                            <path d="M12 3v12m-5-5 5 5 5-5M5 17v3h14v-3" />
                        </svg>
                        Ekspor CSV
                    </button>
                </section>

                <section class="nf-stats-grid">
                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon red">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M12 22c4.4 0 7-3 7-7 0-2.8-1.5-4.5-3.5-7-.2 2-1 3-2 3.5C13.5 7.5 10.5 4 8 2c.5 4-1 6-2.5 8.5A9 9 0 0 0 5 15c0 4 2.8 7 7 7Z" />
                                </svg>
                            </span>
                            <span>Total Hotspot</span>
                        </div>
                        <div class="nf-stat-value">{{ totalHotspots }}</div>
                        <p>Sesuai filter yang dipilih</p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon orange">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M12 3 22 20H2L12 3Z" />
                                    <path d="M12 9v5m0 3h.01" />
                                </svg>
                            </span>
                            <span>Confidence Tinggi</span>
                        </div>
                        <div class="nf-stat-value">{{ highConfidenceCount }}</div>
                        <p>Hotspot dengan confidence tinggi</p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon blue">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M3 10.5 12 3l9 7.5V21H3V10.5Z" />
                                    <path d="M9 21v-7h6v7" />
                                </svg>
                            </span>
                            <span>Wilayah Terdeteksi</span>
                        </div>
                        <div class="nf-stat-value">{{ totalRegions }}</div>
                        <p>Wilayah dalam hasil filter</p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon green">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M3 17 9 11l4 4 8-9" />
                                    <path d="M15 6h6v6" />
                                </svg>
                            </span>
                            <span>Rata-rata FRP</span>
                        </div>
                        <div class="nf-stat-value">{{ averageFrp.toFixed(1) }} <small>MW</small></div>
                        <p>Fire Radiative Power rata-rata</p>
                    </article>
                </section>

                <section class="nf-main-grid">
                    <article class="nf-card nf-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>Peta Persebaran Hotspot</h3>
                                <p>Klik marker untuk melihat detail titik panas.</p>
                            </div>
                            <span class="nf-count">{{ filteredHotspots.length }} titik</span>
                        </div>

                        <div class="nf-legend">
                            <span><i class="high"></i>Tinggi</span>
                            <span><i class="nominal"></i>Sedang</span>
                            <span><i class="low"></i>Rendah</span>
                        </div>

                        <div class="nf-map-wrap">
                            <div ref="mapElement" class="nf-leaflet-map"></div>
                            <div v-if="!mapReady" class="nf-map-message">Memuat peta...</div>
                            <div v-else-if="filteredHotspots.length === 0" class="nf-map-message">
                                Tidak ada hotspot yang sesuai dengan filter.
                            </div>
                        </div>

                        <div class="nf-map-footer">
                            <span><i></i>Peta OpenStreetMap</span>
                            <span>Koordinat derajat desimal</span>
                        </div>
                    </article>

                    <article class="nf-card nf-panel nf-detail-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>Detail Hotspot</h3>
                                <p>Informasi titik yang dipilih.</p>
                            </div>
                        </div>

                        <template v-if="selectedHotspot">
                            <div class="nf-detail-hero">
                                <span class="nf-stat-icon red">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                        <path d="M12 22c4.4 0 7-3 7-7-0-2.8-1.5-4.5-3.5-7-.2 2-1 3-2 3.5C13.5 7.5 10.5 4 8 2c.5 4-1 6-2.5 8.5A9 9 0 0 0 5 15c0 4 2.8 7 7 7Z" />
                                    </svg>
                                </span>
                                <div>
                                    <small>HOTSPOT #{{ selectedHotspot.id }}</small>
                                    <h4>{{ selectedHotspot.region }}</h4>
                                    <span class="nf-confidence" :class="`confidence-${selectedHotspot.confidence}`">
                                        {{ confidenceLabel(selectedHotspot.confidence) }} confidence
                                    </span>
                                </div>
                            </div>

                            <div class="nf-detail-list">
                                <div><span>Tanggal deteksi</span><strong>{{ selectedHotspot.date }}</strong></div>
                                <div><span>Waktu deteksi</span><strong>{{ selectedHotspot.time }}</strong></div>
                                <div><span>Latitude</span><strong>{{ selectedHotspot.latitude.toFixed(4) }}</strong></div>
                                <div><span>Longitude</span><strong>{{ selectedHotspot.longitude.toFixed(4) }}</strong></div>
                                <div><span>FRP</span><strong>{{ selectedHotspot.frp.toFixed(1) }} MW</strong></div>
                                <div><span>Satelit</span><strong>{{ selectedHotspot.satellite }}</strong></div>
                            </div>

                            <button class="nf-button nf-button-outline nf-full-button" type="button" @click="copyCoordinates">
                                Salin koordinat
                            </button>
                            <p v-if="copyMessage" class="nf-copy-message" role="status">{{ copyMessage }}</p>
                        </template>

                        <div v-else class="nf-empty-state">
                            <span class="nf-empty-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
                                    <path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" />
                                    <circle cx="12" cy="10" r="2.5" />
                                </svg>
                            </span>
                            <h4>Belum ada titik dipilih</h4>
                            <p>Pilih marker pada peta atau klik tombol Lihat pada tabel.</p>
                        </div>

                        <div class="nf-note">
                            Data pada halaman ini merupakan data contoh untuk pengembangan antarmuka, bukan data aktual.
                        </div>
                    </article>
                </section>

                <section class="nf-card nf-panel nf-filter-panel">
                    <div class="nf-section-heading">
                        <div>
                            <h3>Filter Data Hotspot</h3>
                            <p>Saring data berdasarkan kriteria yang diperlukan.</p>
                        </div>
                        <button class="nf-button nf-button-outline" type="button" @click="resetFilters">
                            Reset filter
                        </button>
                    </div>

                    <p v-if="dateRangeInvalid" class="nf-date-error" role="alert">
                        Tanggal mulai tidak boleh melebihi tanggal akhir.
                    </p>

                    <div class="nf-filter-grid">
                        <label class="nf-field nf-search-field">
                            <span>Cari hotspot</span>
                            <input v-model="searchQuery" type="search" placeholder="ID, wilayah, satelit..." />
                        </label>

                        <label class="nf-field">
                            <span>Wilayah</span>
                            <select v-model="selectedRegion">
                                <option value="all">Semua wilayah</option>
                                <option v-for="region in regions" :key="region" :value="region">
                                    {{ region }}
                                </option>
                            </select>
                        </label>

                        <label class="nf-field">
                            <span>Confidence</span>
                            <select v-model="selectedConfidence">
                                <option value="all">Semua tingkat</option>
                                <option value="high">Tinggi</option>
                                <option value="nominal">Sedang</option>
                                <option value="low">Rendah</option>
                            </select>
                        </label>

                        <label class="nf-field">
                            <span>Tanggal mulai</span>
                            <input v-model="startDate" type="date" :max="endDate || undefined" />
                        </label>

                        <label class="nf-field">
                            <span>Tanggal akhir</span>
                            <input v-model="endDate" type="date" :min="startDate || undefined" />
                        </label>
                    </div>
                </section>

                <section class="nf-card nf-panel nf-table-panel">
                    <div class="nf-section-heading">
                        <div>
                            <h3>Data Hotspot</h3>
                            <p>Daftar titik panas berdasarkan hasil filter.</p>
                        </div>
                        <span class="nf-count">{{ filteredHotspots.length }} data</span>
                    </div>

                    <div class="nf-table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Wilayah</th>
                                    <th>Koordinat</th>
                                    <th>Tanggal</th>
                                    <th>Confidence</th>
                                    <th>FRP (MW)</th>
                                    <th>Satelit</th>
                                    <th>Aksi</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr
                                    v-for="item in filteredHotspots"
                                    :key="item.id"
                                    :class="{ 'is-selected': selectedHotspot?.id === item.id }"
                                >
                                    <td class="nf-id-cell">#{{ item.id }}</td>
                                    <td>{{ item.region }}</td>
                                    <td>{{ item.latitude.toFixed(3) }}, {{ item.longitude.toFixed(3) }}</td>
                                    <td>{{ item.date }}</td>
                                    <td>
                                        <span class="nf-confidence" :class="`confidence-${item.confidence}`">
                                            {{ confidenceLabel(item.confidence) }}
                                        </span>
                                    </td>
                                    <td>{{ item.frp.toFixed(1) }}</td>
                                    <td>{{ item.satellite }}</td>
                                    <td>
                                        <button class="nf-view-button" type="button" @click="focusHotspot(item)">
                                            Lihat
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="filteredHotspots.length === 0">
                                    <td colspan="8" class="nf-empty-table">
                                        Tidak ada data yang sesuai dengan filter.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="nf-table-footer">
                        Menampilkan {{ filteredHotspots.length }} dari {{ hotspots.length }} data hotspot
                    </div>
                </section>

                <footer class="nf-page-footer">
                    <span>NusaFire · Monitoring dan Analisis Hotspot</span>
                    <span>Data contoh untuk pengembangan antarmuka</span>
                </footer>
            </div>
        </div>
    </main>
</template>

<style>
/* Variabel halaman ini — scope ke .nf-hotspotmap agar tidak tabrakan dengan Dashboard */
.nf-app.nf-hotspotmap {
    /* Palet dasar — identik dengan Dashboard */
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

    /* Alias halaman — base + accent merah khusus hotspot */
    --hm-bg: var(--db-bg);
    --hm-surface: var(--db-surface);
    --hm-soft: var(--db-surface-soft);
    --hm-text: var(--db-text);
    --hm-text-soft: var(--db-text-soft);
    --hm-muted: var(--db-muted);
    --hm-border: var(--db-border);
    --hm-shadow: var(--db-shadow);
    --hm-accent: #d94b3d;
    --hm-accent-soft: #fff0ed;

    min-height: 100vh;
    color: var(--hm-text);
    background: var(--hm-bg);
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    font-size: 13px;
    transition: color .2s ease, background .2s ease;
}

.nf-app.nf-hotspotmap.theme-dark {
    /* Palet gelap — identik dengan Dashboard */
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

    /* Accent merah hotspot, versi gelap */
    --hm-accent: #e06b61;
    --hm-accent-soft: #3b1e1c;
}

.nf-app.nf-hotspotmap *,
.nf-app.nf-hotspotmap *::before,
.nf-app.nf-hotspotmap *::after {
    box-sizing: border-box;
}

.nf-app.nf-hotspotmap button,
.nf-app.nf-hotspotmap input,
.nf-app.nf-hotspotmap select {
    font: inherit;
}

.nf-app.nf-hotspotmap button {
    cursor: pointer;
}

.nf-main {
    min-width: 0;
    min-height: 100vh;
    margin-left: 252px;
    transition: margin-left .3s cubic-bezier(.4,0,.2,1);
}

.nf-main.nf-sidebar-collapsed {
    margin-left: 0;
}

.nf-topbar {
    position: sticky;
    z-index: 300;
    top: 0;
    display: flex;
    min-height: 78px;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 15px 30px;
    border-bottom: 1px solid var(--hm-border);
    background: var(--hm-surface);
}

.nf-topbar-left {
    display: flex;
    align-items: center;
    gap: 13px;
}

.nf-breadcrumb {
    margin-bottom: 5px;
    color: var(--hm-muted);
    font-size: 12px;
}

.nf-topbar h1 {
    margin: 0;
    font-size: 21px;
    font-weight: 750;
    letter-spacing: -.4px;
}

.nf-icon-button {
    display: grid;
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    place-items: center;
    border: 1px solid var(--hm-border);
    border-radius: 10px;
    color: var(--hm-text-soft);
    background: var(--hm-surface);
}

.nf-icon-button svg {
    width: 19px;
    height: 19px;
}

.nf-mobile-menu {
    display: none;
}

.nf-mobile-menu.nf-menu-visible {
    display: grid;
}

.nf-page-content {
    width: 100%;
    max-width: 1700px;
    margin: 0 auto;
    padding: 27px 30px 22px;
}

.nf-page-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 23px;
}

.nf-eyebrow {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    color: var(--hm-accent);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.3px;
}

.nf-eyebrow span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--hm-accent);
}

.nf-page-heading h2 {
    margin: 0 0 8px;
    font-size: 26px;
    font-weight: 780;
    letter-spacing: -.7px;
}

.nf-page-heading p,
.nf-section-heading p {
    margin: 0;
    color: var(--hm-text-soft);
    font-size: 12px;
    line-height: 1.7;
}

.nf-button {
    display: inline-flex;
    min-height: 39px;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 13px;
    border: 1px solid var(--hm-border);
    border-radius: 9px;
    font-size: 12px;
    font-weight: 650;
    transition: background .15s ease, border-color .15s ease;
}

.nf-button svg {
    width: 17px;
    height: 17px;
}

.nf-button-primary {
    flex-shrink: 0;
    border-color: var(--hm-accent);
    color: #fff;
    background: var(--hm-accent);
}

.nf-button-primary:hover {
    filter: brightness(.94);
}

.nf-button-outline {
    color: var(--hm-text);
    background: var(--hm-surface);
}

.nf-button-outline:hover {
    background: var(--hm-soft);
}

.nf-stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

.nf-card {
    min-width: 0;
    border: 1px solid var(--hm-border);
    border-radius: 13px;
    background: var(--hm-surface);
    box-shadow: var(--hm-shadow);
}

.nf-stat-card {
    padding: 18px;
}

.nf-stat-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
    color: var(--hm-text-soft);
    font-size: 11px;
    font-weight: 650;
}

.nf-stat-icon {
    display: grid;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 10px;
}

.nf-stat-icon svg {
    width: 19px;
    height: 19px;
}

.nf-stat-icon.red { color: #d94b3d; background: #fff0ed; }
.nf-stat-icon.orange { color: #d97706; background: #fff5e5; }
.nf-stat-icon.blue { color: #3478d4; background: #eaf3ff; }
.nf-stat-icon.green { color: #169b69; background: #e8f8f0; }

.nf-stat-value {
    margin-bottom: 7px;
    font-size: 28px;
    font-weight: 780;
    letter-spacing: -.8px;
    line-height: 1.2;
}

.nf-stat-value small {
    color: var(--hm-text-soft);
    font-size: 12px;
    font-weight: 600;
}

.nf-stat-card > p {
    margin: 0;
    color: var(--hm-muted);
    font-size: 11px;
    line-height: 1.6;
}

.nf-main-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.8fr) minmax(270px, .9fr);
    align-items: stretch;
    gap: 17px;
    margin-bottom: 20px;
}

.nf-panel {
    padding: 20px;
}

.nf-section-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
}

.nf-section-heading h3 {
    margin: 0 0 6px;
    font-size: 15px;
    font-weight: 750;
    letter-spacing: -.2px;
}

.nf-section-heading p {
    font-size: 11px;
}

.nf-count {
    display: inline-flex;
    flex-shrink: 0;
    align-items: center;
    padding: 6px 9px;
    border: 1px solid var(--hm-border);
    border-radius: 7px;
    color: var(--hm-text-soft);
    background: var(--hm-soft);
    font-size: 10px;
    font-weight: 650;
}

.nf-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 13px;
}

.nf-legend span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: var(--hm-text-soft);
    font-size: 11px;
}

.nf-legend i,
.nf-map-footer i {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.nf-legend .high { background: #ef4444; }
.nf-legend .nominal { background: #f59e0b; }
.nf-legend .low { background: #3b82f6; }

.nf-map-wrap {
    position: relative;
    height: 390px;
    overflow: hidden;
    border: 1px solid var(--hm-border);
    border-radius: 10px;
    background: var(--hm-soft);
}

.nf-leaflet-map {
    width: 100%;
    height: 100%;
}

.nf-map-message {
    position: absolute;
    z-index: 450;
    top: 50%;
    left: 50%;
    max-width: calc(100% - 30px);
    padding: 12px 15px;
    transform: translate(-50%, -50%);
    border: 1px solid var(--hm-border);
    border-radius: 9px;
    color: var(--hm-text);
    background: var(--hm-surface);
    box-shadow: var(--hm-shadow);
    font-size: 12px;
    text-align: center;
    pointer-events: none;
}

.nf-map-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 12px;
    color: var(--hm-muted);
    font-size: 10px;
}

.nf-map-footer > span:first-child {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.nf-map-footer i {
    width: 6px;
    height: 6px;
    background: #22c55e;
}

.nf-detail-panel {
    display: flex;
    flex-direction: column;
}

.nf-detail-hero {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px;
    border: 1px solid var(--hm-border);
    border-radius: 10px;
    background: var(--hm-soft);
}

.nf-detail-hero small {
    display: block;
    margin-bottom: 5px;
    color: var(--hm-muted);
    font-size: 9px;
    font-weight: 750;
    letter-spacing: .8px;
}

.nf-detail-hero h4 {
    margin: 0 0 8px;
    font-size: 15px;
}

.nf-confidence {
    display: inline-flex;
    align-items: center;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.confidence-high { color: #c93636; background: #ffeded; }
.confidence-nominal { color: #a66b06; background: #fff4dc; }
.confidence-low { color: #286fc1; background: #eaf3ff; }

.nf-app.nf-hotspotmap.theme-dark .confidence-high { color: #ffaaaa; background: #442629; }
.nf-app.nf-hotspotmap.theme-dark .confidence-nominal { color: #ffd27b; background: #44351d; }
.nf-app.nf-hotspotmap.theme-dark .confidence-low { color: #9bc9ff; background: #1e3550; }

.nf-detail-list {
    padding: 8px 0;
}

.nf-detail-list > div {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--hm-border);
}

.nf-detail-list > div:last-child {
    border-bottom: 0;
}

.nf-detail-list span {
    color: var(--hm-text-soft);
    font-size: 11px;
}

.nf-detail-list strong {
    overflow-wrap: anywhere;
    text-align: right;
    font-size: 11px;
    font-weight: 700;
}

.nf-full-button {
    width: 100%;
    margin-top: 5px;
}

.nf-copy-message {
    margin: 9px 0 0;
    color: var(--hm-text-soft);
    font-size: 11px;
    line-height: 1.6;
}

.nf-empty-state {
    display: flex;
    min-height: 250px;
    flex: 1;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px 12px;
    text-align: center;
}

.nf-empty-icon {
    display: grid;
    width: 49px;
    height: 49px;
    margin-bottom: 14px;
    place-items: center;
    border-radius: 13px;
    color: var(--hm-muted);
    background: var(--hm-soft);
}

.nf-empty-icon svg {
    width: 24px;
    height: 24px;
}

.nf-empty-state h4 {
    margin: 0 0 8px;
    font-size: 13px;
}

.nf-empty-state p {
    max-width: 230px;
    margin: 0;
    color: var(--hm-text-soft);
    font-size: 11px;
    line-height: 1.7;
}

.nf-note {
    margin-top: 14px;
    padding: 11px 12px;
    border-radius: 8px;
    color: var(--hm-text-soft);
    background: var(--hm-soft);
    font-size: 10px;
    line-height: 1.7;
}

.nf-filter-panel,
.nf-table-panel {
    margin-bottom: 20px;
}

.nf-filter-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 13px;
}

.nf-field {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 8px;
}

.nf-field > span {
    color: var(--hm-text-soft);
    font-size: 11px;
    font-weight: 650;
}

.nf-field input,
.nf-field select {
    width: 100%;
    min-width: 0;
    height: 41px;
    padding: 0 10px;
    border: 1px solid var(--hm-border);
    border-radius: 8px;
    outline: none;
    color: var(--hm-text);
    background: var(--hm-surface);
    font-size: 11px;
}

.nf-field input::placeholder {
    color: var(--hm-muted);
}

.nf-field input:focus,
.nf-field select:focus {
    border-color: var(--hm-accent);
    box-shadow: 0 0 0 3px rgb(217 75 61 / 10%);
}

.nf-date-error {
    margin: 0 0 13px;
    color: #dc3e3e;
    font-size: 11px;
}

.nf-table-scroll {
    width: 100%;
    overflow-x: auto;
}

.nf-table-scroll table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    white-space: nowrap;
}

.nf-table-scroll th {
    padding: 13px 12px;
    border-top: 1px solid var(--hm-border);
    border-bottom: 1px solid var(--hm-border);
    color: var(--hm-muted);
    background: var(--hm-soft);
    font-size: 10px;
    font-weight: 750;
}

.nf-table-scroll td {
    padding: 14px 12px;
    border-bottom: 1px solid var(--hm-border);
    color: var(--hm-text-soft);
    font-size: 11px;
}

.nf-table-scroll tbody tr:last-child td {
    border-bottom: 0;
}

.nf-table-scroll tbody tr:hover,
.nf-table-scroll tbody tr.is-selected {
    background: var(--hm-soft);
}

.nf-table-scroll .nf-id-cell {
    color: var(--hm-text);
    font-weight: 750;
}

.nf-view-button {
    padding: 6px 10px;
    border: 1px solid var(--hm-border);
    border-radius: 6px;
    color: var(--hm-text);
    background: var(--hm-surface);
    font-size: 10px;
    font-weight: 700;
}

.nf-view-button:hover {
    border-color: var(--hm-accent);
    color: var(--hm-accent);
}

.nf-empty-table {
    padding: 32px 12px !important;
    text-align: center;
}

.nf-table-footer {
    margin-top: 14px;
    padding-top: 13px;
    border-top: 1px solid var(--hm-border);
    color: var(--hm-muted);
    font-size: 10px;
}

.nf-page-footer {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 3px 0 8px;
    color: var(--hm-muted);
    font-size: 10px;
    line-height: 1.6;
}

/* Marker Leaflet */
.nf-hotspot-marker-wrapper {
    border: 0;
    background: transparent;
}

.nf-hotspot-marker {
    display: grid;
    width: 24px;
    height: 24px;
    place-items: center;
    border: 2px solid #fff;
    border-radius: 50%;
    background: var(--marker-color);
    box-shadow: 0 2px 8px rgb(0 0 0 / 25%);
}

.nf-hotspot-marker span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #fff;
}

.nf-hotspot-popup {
    min-width: 150px;
    color: #182230;
    font-family: inherit;
}

.nf-hotspot-popup strong {
    display: block;
    margin-bottom: 8px;
    font-size: 13px;
}

.nf-hotspot-popup p {
    margin: 5px 0;
    font-size: 11px;
}

@media (max-width: 1200px) {
    .nf-page-content {
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

    .nf-filter-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .nf-main-grid {
        grid-template-columns: minmax(0, 1.5fr) minmax(240px, 1fr);
    }
}

@media (max-width: 900px) {
    .nf-main {
        margin-left: 0;
    }

    .nf-mobile-menu {
        display: grid;
    }

    .nf-topbar {
        min-height: 72px;
        padding: 13px 20px;
    }

    .nf-page-content {
        padding: 22px 20px;
    }

    .nf-main-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .nf-filter-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 560px) {
    .nf-topbar {
        padding: 12px 14px;
    }

    .nf-topbar h1 {
        font-size: 18px;
    }

    .nf-page-content {
        padding: 19px 13px;
    }

    .nf-page-heading {
        align-items: stretch;
        flex-direction: column;
        gap: 15px;
    }

    .nf-page-heading h2 {
        font-size: 23px;
    }

    .nf-button-primary {
        width: 100%;
    }

    .nf-stats-grid {
        gap: 10px;
    }

    .nf-stat-card {
        padding: 13px;
    }

    .nf-stat-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 12px;
    }

    .nf-stat-icon {
        width: 32px;
        height: 32px;
    }

    .nf-stat-value {
        font-size: 24px;
    }

    .nf-stat-card > p {
        font-size: 10px;
    }

    .nf-panel {
        padding: 14px;
    }

    .nf-section-heading h3 {
        font-size: 13px;
    }

    .nf-section-heading p {
        font-size: 10px;
    }

    .nf-map-wrap {
        height: 310px;
    }

    .nf-map-footer {
        align-items: flex-start;
        flex-direction: column;
        gap: 7px;
    }

    .nf-filter-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .nf-page-footer {
        flex-direction: column;
        gap: 6px;
    }
}
</style>
