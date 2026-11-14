
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

type Hotspot = {
    id: number;
    gridId: string;
    location: string;
    latitude: number;
    longitude: number;
    date: string;
    region: string;
    hotspotCount: number;
    isFire: boolean;
};

type HotspotApiRow = {
    DATE?: string;
    GRID_ID?: string;
    LOCATION?: string;
    REGION?: string;
    LATITUDE?: number | string;
    LONGITUDE?: number | string;
    hotspot_count?: number | string;
    is_fire?: number | string | boolean;
};

type HotspotApiResponse = {
    status?: string;
    total?: number;
    total_fire?: number;
    total_non_fire?: number;
    limit?: number;
    offset?: number;
    filter_status?: string;
    returned?: number;
    has_more?: boolean;
    data?: HotspotApiRow[];
    message?: string;
    errors?: Record<string, string[]>;
};

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const mapElement = ref<HTMLDivElement | null>(null);

const searchQuery = ref('');
const selectedRegion = ref('all');
const selectedStatus = ref<'all' | 'fire' | 'non-fire'>('all');
const startDate = ref('');
const endDate = ref('');

const hotspots = ref<Hotspot[]>([]);
const totalApiRecords = ref(0);
const totalFireRecords = ref(0);
const totalNonFireRecords = ref(0);
const hasMore = ref(false);

const selectedHotspot = ref<Hotspot | null>(null);
const loading = ref(false);
const mapReady = ref(false);
const errorMessage = ref('');
const copyMessage = ref('');

const pageSize = 500;
const currentOffset = ref(0);
const requestVersion = ref(0);

let map: L.Map | null = null;
let markerLayer: L.LayerGroup | null = null;
let copyMessageTimeout: ReturnType<typeof setTimeout> | null = null;
let requestController: AbortController | null = null;

const regions = [
    'Sumatra',
    'Java-Bali-Nusa Tenggara',
    'Kalimantan',
    'Sulawesi',
    'Maluku',
    'Papua',
];

const currentPage = computed(
    () => Math.floor(currentOffset.value / pageSize) + 1,
);

const totalPages = computed(
    () => Math.ceil(totalApiRecords.value / pageSize),
);

const pageStart = computed(() =>
    totalApiRecords.value === 0 ? 0 : currentOffset.value + 1,
);

const pageEnd = computed(() =>
    Math.min(
        currentOffset.value + hotspots.value.length,
        totalApiRecords.value,
    ),
);

const filteredHotspots = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();

    if (!query) return hotspots.value;

    return hotspots.value.filter((item) =>
        [
            item.gridId,
            item.location,
            item.region,
            item.date,
            String(item.id),
            String(item.latitude),
            String(item.longitude),
        ].some((value) => value.toLowerCase().includes(query)),
    );
});

const totalHotspots = computed(() =>
    selectedStatus.value === 'non-fire' ? 0 : totalFireRecords.value,
);

const totalNonFire = computed(() =>
    selectedStatus.value === 'fire' ? 0 : totalNonFireRecords.value,
);

const totalGridRecords = computed(() => totalApiRecords.value);

const dateRangeInvalid = computed(
    () =>
        Boolean(startDate.value && endDate.value) &&
        startDate.value > endDate.value,
);

function statusLabel(isFire: boolean): string {
    return isFire ? 'Fire' : 'Non-fire';
}

function statusColor(isFire: boolean): string {
    return isFire ? '#ef4444' : '#3b82f6';
}

function createMarkerIcon(isFire: boolean): L.DivIcon {
    return L.divIcon({
        className: 'nf-hotspot-marker-wrapper',
        html: `
            <div class="nf-hotspot-marker"
                 style="--marker-color:${statusColor(isFire)}">
                <span></span>
            </div>
        `,
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
            <strong>${escapeHtml(item.gridId)}</strong>
            <p>Wilayah: ${escapeHtml(item.region)}</p>
            <p>Lokasi: ${escapeHtml(item.location)}</p>
            <p>Tanggal: ${escapeHtml(item.date)}</p>
            <p>Status data: ${statusLabel(item.isFire)}</p>
            <p>Jumlah hotspot: ${item.hotspotCount}</p>
            <p>Latitude: ${item.latitude}</p>
            <p>Longitude: ${item.longitude}</p>
        </div>
    `;
}

function normalizeHotspot(
    row: HotspotApiRow,
    index: number,
): Hotspot | null {
    const latitude = Number(row.LATITUDE);
    const longitude = Number(row.LONGITUDE);
    const hotspotCount = Number(row.hotspot_count);
    const rawStatus = row.is_fire;

    if (
        row.LATITUDE === null ||
        row.LATITUDE === undefined ||
        row.LONGITUDE === null ||
        row.LONGITUDE === undefined ||
        !Number.isFinite(latitude) ||
        !Number.isFinite(longitude) ||
        latitude < -90 ||
        latitude > 90 ||
        longitude < -180 ||
        longitude > 180 ||
        ![0, 1, true, false, '0', '1'].includes(rawStatus as never)
    ) {
        return null;
    }

    return {
        id: currentOffset.value + index + 1,
        gridId: String(row.GRID_ID ?? 'Tidak diketahui'),
        location: String(row.LOCATION ?? 'Tidak diketahui'),
        latitude,
        longitude,
        date: String(row.DATE ?? '').slice(0, 10),
        region: String(row.REGION ?? 'Tidak diketahui'),
        hotspotCount: Number.isFinite(hotspotCount) ? hotspotCount : 0,
        isFire: rawStatus === true || Number(rawStatus) === 1,
    };
}

function renderMarkers(): void {
    if (!map || !markerLayer) return;

    markerLayer.clearLayers();

    for (const item of filteredHotspots.value) {
        const marker = L.marker(
            [item.latitude, item.longitude],
            { icon: createMarkerIcon(item.isFire) },
        );

        marker.bindPopup(popupContent(item));

        marker.on('click', () => {
            selectedHotspot.value = item;
        });

        markerLayer.addLayer(marker);
    }
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
    mapReady.value = true;

    nextTick(() => map?.invalidateSize());
}

async function loadHotspots(): Promise<void> {
    if (dateRangeInvalid.value) {
        errorMessage.value =
            'Tanggal mulai tidak boleh melebihi tanggal akhir.';
        return;
    }

    requestController?.abort();

    const controller = new AbortController();
    requestController = controller;

    const thisRequest = ++requestVersion.value;

    loading.value = true;
    errorMessage.value = '';

    const params = new URLSearchParams({
        status: selectedStatus.value,
        limit: String(pageSize),
        offset: String(currentOffset.value),
    });

    if (selectedRegion.value !== 'all') {
        params.set('region', selectedRegion.value);
    }

    if (startDate.value) {
        params.set('start_date', startDate.value);
    }

    if (endDate.value) {
        params.set('end_date', endDate.value);
    }

    try {
        const response = await fetch(
            `/internal/ai/hotspots?${params.toString()}`,
            {
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
                signal: controller.signal,
            },
        );

        const result = await response.json().catch(() => null) as
            | HotspotApiResponse
            | null;

        if (!response.ok) {
            const validationMessage = result?.errors
                ? Object.values(result.errors).flat().join(' ')
                : '';

            throw new Error(
                validationMessage ||
                result?.message ||
                `Permintaan data gagal (HTTP ${response.status}).`,
            );
        }

        if (
            !result ||
            result.status !== 'success' ||
            !Array.isArray(result.data)
        ) {
            throw new Error(
                'Format respons API tidak sesuai atau data hotspot tidak ditemukan.',
            );
        }

        if (thisRequest !== requestVersion.value) return;

        hotspots.value = result.data
            .map((row, index) => normalizeHotspot(row, index))
            .filter((item): item is Hotspot => item !== null);

        totalApiRecords.value = Number(result.total ?? 0);
        totalFireRecords.value = Number(result.total_fire ?? 0);
        totalNonFireRecords.value = Number(result.total_non_fire ?? 0);
        hasMore.value = Boolean(result.has_more);

        if (hotspots.value.length === 0 && totalApiRecords.value > 0) {
            errorMessage.value =
                'Data tersedia, tetapi tidak ada koordinat atau status yang valid pada halaman ini.';
        }
    } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return;
        if (thisRequest !== requestVersion.value) return;

        console.error('Gagal memuat data hotspot:', error);

        errorMessage.value = error instanceof Error
            ? error.message
            : 'Terjadi kesalahan saat mengambil data hotspot.';
    } finally {
        if (thisRequest === requestVersion.value) {
            loading.value = false;
            renderMarkers();
        }
    }
}

function applyFilters(): void {
    if (dateRangeInvalid.value) {
        errorMessage.value =
            'Tanggal mulai tidak boleh melebihi tanggal akhir.';
        return;
    }

    currentOffset.value = 0;
    selectedHotspot.value = null;
    searchQuery.value = '';
    void loadHotspots();
}

function resetFilters(): void {
    searchQuery.value = '';
    selectedRegion.value = 'all';
    selectedStatus.value = 'all';
    startDate.value = '';
    endDate.value = '';
    currentOffset.value = 0;
    selectedHotspot.value = null;

    void loadHotspots();
}

function nextPage(): void {
    if (loading.value || !hasMore.value) return;

    currentOffset.value += pageSize;
    selectedHotspot.value = null;

    void loadHotspots();
}

function previousPage(): void {
    if (loading.value || currentOffset.value === 0) return;

    currentOffset.value = Math.max(0, currentOffset.value - pageSize);
    selectedHotspot.value = null;

    void loadHotspots();
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
        showCopyMessage('Gagal menyalin. Salin koordinat secara manual.');
    }
}

function exportCsv(): void {
    const headers = [
        'ID',
        'Grid ID',
        'Lokasi',
        'Latitude',
        'Longitude',
        'Tanggal',
        'Wilayah',
        'Jumlah Hotspot',
        'Status Data',
    ];

    const rows = filteredHotspots.value.map((item) => [
        item.id,
        item.gridId,
        item.location,
        item.latitude,
        item.longitude,
        item.date,
        item.region,
        item.hotspotCount,
        statusLabel(item.isFire),
    ]);

    const csv = [headers, ...rows]
        .map((row) =>
            row.map((value) =>
                `"${String(value).replace(/"/g, '""')}"`,
            ).join(','),
        )
        .join('\r\n');

    const blob = new Blob(['\uFEFF' + csv], {
        type: 'text/csv;charset=utf-8;',
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download =
        `nusafire-hotspots-${new Date().toISOString().slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

watch(
    [selectedRegion, selectedStatus, startDate, endDate],
    () => {
        currentOffset.value = 0;
        selectedHotspot.value = null;
        void loadHotspots();
    },
);

watch(
    filteredHotspots,
    (items) => {
        renderMarkers();

        if (
            selectedHotspot.value &&
            !items.some((item) => item.id === selectedHotspot.value?.id)
        ) {
            selectedHotspot.value = null;
        }
    },
    { flush: 'post' },
);

onMounted(async () => {
    await nextTick();
    initializeMap();
    await loadHotspots();
});

onBeforeUnmount(() => {
    requestController?.abort();

    if (copyMessageTimeout) clearTimeout(copyMessageTimeout);

    map?.remove();
    map = null;
    markerLayer = null;
});
</script>

<template>
    <Head title="Hotspot Map | NusaFire" />

    <main class="nf-app nf-hotspotmap" :class="`theme-${theme}`">
        <AppSidebar
            active-page="hotspot-map"
            :mobile-open="mobileMenuOpen"
            v-model:collapsed="sidebarCollapsed"
            @close="mobileMenuOpen = false"
        />

        <div
            class="nf-main"
            :class="{ 'nf-sidebar-collapsed': sidebarCollapsed }"
        >
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        class="nf-icon-button nf-mobile-menu"
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
                            <span></span>
                            MONITORING KEBAKARAN
                        </div>
                        <h2>Pemetaan Titik Panas</h2>
                        <p>
                            Pantau data grid hotspot berdasarkan koordinat,
                            wilayah, tanggal, dan status klasifikasi.
                        </p>
                    </div>

                    <button
                        class="nf-button nf-button-primary"
                        type="button"
                        :disabled="filteredHotspots.length === 0"
                        @click="exportCsv"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                            <path d="M12 3v12m-5-5 5 5 5-5M5 17v3h14v-3" />
                        </svg>
                        Ekspor CSV
                    </button>
                </section>

                <div v-if="errorMessage" class="nf-alert" role="alert">
                    <strong>Data hotspot bermasalah.</strong>
                    <span>{{ errorMessage }}</span>
                    <button
                        class="nf-retry-button"
                        type="button"
                        :disabled="loading"
                        @click="loadHotspots"
                    >
                        {{ loading ? 'Memuat...' : 'Coba lagi' }}
                    </button>
                </div>

                <!-- RINGKASAN INFORMASI -->
                <section class="nf-stats-grid">
                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon red">🔥</span>
                            <span>Record Fire</span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : totalHotspots.toLocaleString('id-ID') }}
                        </div>
                        <p>Total record fire sesuai filter server.</p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon blue">○</span>
                            <span>Record Non-fire</span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : totalNonFire.toLocaleString('id-ID') }}
                        </div>
                        <p>Total record non-fire sesuai filter server.</p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon green">⌖</span>
                            <span>Wilayah Tersedia</span>
                        </div>
                        <div class="nf-stat-value">
                            {{ selectedRegion === 'all' ? regions.length : 1 }}
                        </div>
                        <p>
                            {{ selectedRegion === 'all' ? 'Daftar wilayah dataset' : selectedRegion }}
                        </p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon orange">▦</span>
                            <span>Total Record</span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : totalGridRecords.toLocaleString('id-ID') }}
                        </div>
                        <p>Total data yang cocok dengan filter server.</p>
                    </article>
                </section>

                <!-- FILTER DIPINDAHKAN KE ATAS PETA -->
                <section class="nf-card nf-panel nf-filter-panel">
                    <div class="nf-section-heading">
                        <div>
                            <div class="nf-filter-title">
                                <span class="nf-filter-icon">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                        <path d="M4 5h16M7 12h10m-7 7h4" />
                                    </svg>
                                </span>
                                <h3>Filter Data Hotspot</h3>
                            </div>
                            <p>
                                Atur filter di sini, lalu lihat hasilnya langsung
                                pada peta dan tabel di bawah.
                            </p>
                        </div>

                        <button
                            class="nf-button nf-button-outline"
                            type="button"
                            :disabled="loading"
                            @click="resetFilters"
                        >
                            Reset filter
                        </button>
                    </div>

                    <p v-if="dateRangeInvalid" class="nf-date-error" role="alert">
                        Tanggal mulai tidak boleh melebihi tanggal akhir.
                    </p>

                    <form class="nf-filter-grid" @submit.prevent="applyFilters">
                        <label class="nf-field">
                            <span>Cari data pada halaman ini</span>
                            <input
                                v-model="searchQuery"
                                type="search"
                                placeholder="Grid ID, lokasi, wilayah..."
                            />
                        </label>

                        <label class="nf-field">
                            <span>Wilayah</span>
                            <select v-model="selectedRegion">
                                <option value="all">Semua wilayah</option>
                                <option
                                    v-for="region in regions"
                                    :key="region"
                                    :value="region"
                                >
                                    {{ region }}
                                </option>
                            </select>
                        </label>

                        <label class="nf-field">
                            <span>Status data</span>
                            <select v-model="selectedStatus">
                                <option value="all">Semua status</option>
                                <option value="fire">Fire</option>
                                <option value="non-fire">Non-fire</option>
                            </select>
                        </label>

                        <label class="nf-field">
                            <span>Tanggal mulai</span>
                            <input
                                v-model="startDate"
                                type="date"
                                :max="endDate || undefined"
                            />
                        </label>

                        <label class="nf-field">
                            <span>Tanggal akhir</span>
                            <input
                                v-model="endDate"
                                type="date"
                                :min="startDate || undefined"
                            />
                        </label>

                        <div class="nf-filter-actions">
                            <span class="nf-filter-hint">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <circle cx="12" cy="12" r="9" />
                                    <path d="M12 11v5m0-8h.01" />
                                </svg>
                                Filter tanggal, wilayah, dan status diterapkan ke server.
                            </span>

                            <button
                                class="nf-button nf-button-primary nf-apply-button"
                                type="submit"
                                :disabled="loading || dateRangeInvalid"
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <circle cx="10.5" cy="10.5" r="6.5" />
                                    <path d="m16 16 4 4" />
                                </svg>
                                {{ loading ? 'Memuat data...' : 'Terapkan filter' }}
                            </button>
                        </div>
                    </form>
                </section>

                <!-- PETA DAN DETAIL -->
                <section class="nf-main-grid">
                    <article class="nf-card nf-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>Peta Persebaran Hotspot</h3>
                                <p>Klik marker untuk melihat informasi record.</p>
                            </div>
                            <span class="nf-count">
                                {{ filteredHotspots.length.toLocaleString('id-ID') }} marker
                            </span>
                        </div>

                        <div class="nf-legend">
                            <span><i class="high"></i> Fire</span>
                            <span><i class="low"></i> Non-fire</span>
                        </div>

                        <div class="nf-map-wrap">
                            <div ref="mapElement" class="nf-leaflet-map"></div>

                            <div v-if="loading" class="nf-map-message">
                                Memuat data hotspot...
                            </div>
                            <div v-else-if="errorMessage" class="nf-map-message">
                                {{ errorMessage }}
                            </div>
                            <div v-else-if="filteredHotspots.length === 0" class="nf-map-message">
                                Tidak ada data yang sesuai.
                            </div>
                        </div>

                        <div class="nf-map-footer">
                            <span><i></i> Peta OpenStreetMap</span>
                            <span>Koordinat derajat desimal</span>
                        </div>
                    </article>

                    <article class="nf-card nf-panel nf-detail-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>Detail Hotspot</h3>
                                <p>Informasi record yang dipilih.</p>
                            </div>
                        </div>

                        <template v-if="selectedHotspot">
                            <div class="nf-detail-hero">
                                <span
                                    class="nf-stat-icon"
                                    :class="selectedHotspot.isFire ? 'red' : 'blue'"
                                >
                                    {{ selectedHotspot.isFire ? '🔥' : '○' }}
                                </span>
                                <div>
                                    <small>RECORD #{{ selectedHotspot.id }}</small>
                                    <h4>{{ selectedHotspot.region }}</h4>
                                    <span
                                        class="nf-confidence"
                                        :class="selectedHotspot.isFire ? 'confidence-high' : 'confidence-low'"
                                    >
                                        {{ statusLabel(selectedHotspot.isFire) }}
                                    </span>
                                </div>
                            </div>

                            <div class="nf-detail-list">
                                <div><span>Grid ID</span><strong>{{ selectedHotspot.gridId }}</strong></div>
                                <div><span>Lokasi</span><strong>{{ selectedHotspot.location }}</strong></div>
                                <div><span>Wilayah</span><strong>{{ selectedHotspot.region }}</strong></div>
                                <div><span>Tanggal</span><strong>{{ selectedHotspot.date }}</strong></div>
                                <div><span>Latitude</span><strong>{{ selectedHotspot.latitude.toFixed(5) }}</strong></div>
                                <div><span>Longitude</span><strong>{{ selectedHotspot.longitude.toFixed(5) }}</strong></div>
                                <div><span>Jumlah hotspot</span><strong>{{ selectedHotspot.hotspotCount }}</strong></div>
                                <div><span>Status data</span><strong>{{ statusLabel(selectedHotspot.isFire) }}</strong></div>
                            </div>

                            <button
                                class="nf-button nf-button-outline nf-full-button"
                                type="button"
                                @click="copyCoordinates"
                            >
                                Salin koordinat
                            </button>

                            <p v-if="copyMessage" class="nf-copy-message" role="status">
                                {{ copyMessage }}
                            </p>
                        </template>

                        <div v-else class="nf-empty-state">
                            <span class="nf-empty-icon">⌖</span>
                            <h4>Belum ada titik dipilih</h4>
                            <p>Pilih marker pada peta atau tekan tombol Lihat pada tabel.</p>
                        </div>

                        <div class="nf-note">
                            Satu record merepresentasikan data grid/tanggal, bukan selalu
                            satu deteksi api individual. Status fire/non-fire mengikuti
                            label dataset.
                        </div>
                    </article>
                </section>

                <!-- TABEL TETAP DI BAWAH PETA -->
                <section class="nf-card nf-panel nf-table-panel">
                    <div class="nf-section-heading">
                        <div>
                            <h3>Daftar Data Hotspot</h3>
                            <p>
                                Data pada tabel mengikuti filter yang diterapkan di atas.
                            </p>
                        </div>
                        <span class="nf-count">
                            {{ filteredHotspots.length.toLocaleString('id-ID') }} data tampil
                        </span>
                    </div>

                    <div class="nf-table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Grid ID</th>
                                    <th>Wilayah</th>
                                    <th>Koordinat</th>
                                    <th>Tanggal</th>
                                    <th>Jumlah Hotspot</th>
                                    <th>Status</th>
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
                                    <td>{{ item.gridId }}</td>
                                    <td>{{ item.region }}</td>
                                    <td>
                                        {{ item.latitude.toFixed(3) }},
                                        {{ item.longitude.toFixed(3) }}
                                    </td>
                                    <td>{{ item.date }}</td>
                                    <td>{{ item.hotspotCount }}</td>
                                    <td>
                                        <span
                                            class="nf-confidence"
                                            :class="item.isFire ? 'confidence-high' : 'confidence-low'"
                                        >
                                            {{ statusLabel(item.isFire) }}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            class="nf-view-button"
                                            type="button"
                                            @click="focusHotspot(item)"
                                        >
                                            Lihat
                                        </button>
                                    </td>
                                </tr>

                                <tr v-if="filteredHotspots.length === 0">
                                    <td colspan="8" class="nf-empty-table">
                                        {{ loading ? 'Sedang memuat data...' : 'Tidak ada data yang sesuai.' }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="nf-pagination">
                        <div>
                            Menampilkan
                            {{ pageStart.toLocaleString('id-ID') }}–{{ pageEnd.toLocaleString('id-ID') }}
                            dari {{ totalApiRecords.toLocaleString('id-ID') }} record.
                            <span v-if="searchQuery">
                                Pencarian lokal: {{ filteredHotspots.length }} hasil pada halaman ini.
                            </span>
                        </div>

                        <div class="nf-pagination-controls">
                            <button
                                class="nf-button nf-button-outline"
                                type="button"
                                :disabled="loading || currentOffset === 0"
                                @click="previousPage"
                            >
                                ← Sebelumnya
                            </button>

                            <span>
                                Halaman {{ currentPage }} dari {{ Math.max(totalPages, 1) }}
                            </span>

                            <button
                                class="nf-button nf-button-outline"
                                type="button"
                                :disabled="loading || !hasMore"
                                @click="nextPage"
                            >
                                Berikutnya →
                            </button>
                        </div>
                    </div>
                </section>

                <footer class="nf-page-footer">
                    <span>NusaFire · Monitoring dan Analisis Hotspot</span>
                    <span>Data bersumber dari API NusaFire</span>
                </footer>
            </div>
        </div>
    </main>
</template>

<style>
.nf-app.nf-hotspotmap {
    --hm-bg: #f5f7f4;
    --hm-surface: #fff;
    --hm-soft: #f8faf7;
    --hm-text: #1c2922;
    --hm-text-soft: #526158;
    --hm-muted: #859087;
    --hm-border: #e5eae4;
    --hm-shadow: 0 4px 20px rgb(23 49 33 / 3%);
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
    --hm-bg: #111914;
    --hm-surface: #19231c;
    --hm-soft: #1d2921;
    --hm-text: #edf4ed;
    --hm-text-soft: #b0bdb2;
    --hm-muted: #849489;
    --hm-border: #2b3a2e;
    --hm-shadow: 0 4px 20px rgb(0 0 0 / 10%);
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

.nf-app.nf-hotspotmap button:disabled {
    cursor: not-allowed;
    opacity: .55;
}

.nf-main {
    min-width: 0;
    min-height: 100vh;
    margin-left: 252px;
    transition: margin-left .3s ease;
}

.nf-main.nf-sidebar-collapsed {
    margin-left: 0;
}

.nf-topbar {
    position: sticky;
    z-index: 500;
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

.nf-eyebrow > span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--hm-accent);
}

.nf-page-heading h2 {
    margin: 0 0 8px;
    font-size: 26px;
    font-weight: 780;
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
}

.nf-button svg {
    width: 17px;
    height: 17px;
    flex-shrink: 0;
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

.nf-alert {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 12px;
    margin-bottom: 20px;
    padding: 14px 16px;
    border: 1px solid #efc5c0;
    border-radius: 10px;
    color: var(--hm-text);
    background: var(--hm-accent-soft);
    font-size: 12px;
    line-height: 1.6;
}

.nf-alert strong {
    color: var(--hm-accent);
}

.nf-retry-button {
    margin-left: auto;
    padding: 7px 10px;
    border: 1px solid var(--hm-border);
    border-radius: 7px;
    color: var(--hm-text);
    background: var(--hm-surface);
    font-weight: 650;
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
    font-size: 19px;
}

.nf-stat-icon.red {
    color: #d94b3d;
    background: #fff0ed;
}

.nf-stat-icon.orange {
    color: #d97706;
    background: #fff5e5;
}

.nf-stat-icon.blue {
    color: #3478d4;
    background: #eaf3ff;
}

.nf-stat-icon.green {
    color: #169b69;
    background: #e8f8f0;
}

.nf-stat-value {
    margin-bottom: 7px;
    font-size: 28px;
    font-weight: 780;
    line-height: 1.2;
}

.nf-stat-card > p {
    margin: 0;
    color: var(--hm-muted);
    font-size: 11px;
    line-height: 1.6;
}

/* FILTER PANEL */
.nf-filter-panel {
    margin-bottom: 20px;
    scroll-margin-top: 90px;
}

.nf-filter-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.nf-filter-title h3 {
    margin: 0;
    font-size: 15px;
    font-weight: 750;
}

.nf-filter-icon {
    display: grid;
    width: 34px;
    height: 34px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 9px;
    color: var(--hm-accent);
    background: var(--hm-accent-soft);
}

.nf-filter-icon svg {
    width: 19px;
    height: 19px;
}

.nf-filter-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 15px;
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
    height: 42px;
    padding: 0 10px;
    border: 1px solid var(--hm-border);
    border-radius: 8px;
    outline: none;
    color: var(--hm-text);
    background: var(--hm-surface);
    font-size: 11px;
}

.nf-field input:focus,
.nf-field select:focus {
    border-color: var(--hm-accent);
    box-shadow: 0 0 0 3px rgb(217 75 61 / 10%);
}

.nf-filter-actions {
    display: flex;
    grid-column: 1 / -1;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 4px;
}

.nf-filter-hint {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: var(--hm-muted);
    font-size: 10px;
    line-height: 1.6;
}

.nf-filter-hint svg {
    width: 15px;
    height: 15px;
    flex-shrink: 0;
}

.nf-apply-button {
    min-width: 145px;
}

.nf-date-error {
    margin: 0 0 13px;
    color: #dc3e3e;
    font-size: 11px;
}

/* MAP AND DETAIL */
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

.nf-legend .high {
    background: #ef4444;
}

.nf-legend .low {
    background: #3b82f6;
}

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
    line-height: 1.6;
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

.confidence-high {
    color: #c93636;
    background: #ffeded;
}

.confidence-low {
    color: #286fc1;
    background: #eaf3ff;
}

.nf-app.nf-hotspotmap.theme-dark .confidence-high {
    color: #ffaaaa;
    background: #442629;
}

.nf-app.nf-hotspotmap.theme-dark .confidence-low {
    color: #9bc9ff;
    background: #1e3550;
}

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
    max-width: 65%;
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
    font-size: 27px;
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

/* TABLE */
.nf-table-panel {
    margin-bottom: 20px;
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

.nf-pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 15px;
    padding-top: 14px;
    border-top: 1px solid var(--hm-border);
    color: var(--hm-muted);
    font-size: 10px;
    line-height: 1.7;
}

.nf-pagination-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 9px;
}

.nf-pagination-controls > span {
    color: var(--hm-text-soft);
    white-space: nowrap;
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

/* LEAFLET */
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
    min-width: 160px;
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

.nf-app.nf-hotspotmap .nf-leaflet-map {
    z-index: 1;
}

.nf-app.nf-hotspotmap .leaflet-control-attribution {
    font-size: 9px;
}

/* RESPONSIVE */
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

    .nf-filter-panel > .nf-section-heading {
        align-items: flex-start;
    }

    .nf-filter-panel > .nf-section-heading > .nf-button {
        min-height: 34px;
        padding: 0 9px;
        font-size: 10px;
    }

    .nf-filter-grid {
        grid-template-columns: minmax(0, 1fr);
    }

    .nf-filter-actions {
        align-items: stretch;
        flex-direction: column;
    }

    .nf-apply-button {
        width: 100%;
    }

    .nf-map-wrap {
        height: 310px;
    }

    .nf-map-footer,
    .nf-page-footer {
        align-items: flex-start;
        flex-direction: column;
        gap: 7px;
    }

    .nf-alert {
        align-items: flex-start;
        flex-direction: column;
    }

    .nf-retry-button {
        margin-left: 0;
    }

    .nf-pagination {
        align-items: stretch;
        flex-direction: column;
    }

    .nf-pagination-controls {
        justify-content: space-between;
    }

    .nf-pagination-controls .nf-button {
        padding: 0 9px;
        font-size: 10px;
    }
}
</style>
