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

type MapMode = 'firms' | 'historical';

type Hotspot = {
    id: number;
    gridId: string;
    location: string;
    latitude: number;
    longitude: number;
    date: string;
    region: string;
    district?: string;
    hotspotCount: number;
    isFire: boolean;
    probabilityFire?: number;
    riskLevel?: string;
    weatherSummary?: string;
    frp?: number;
    brightness?: number;
    confidence?: string;
    acqTime?: string;
    satellite?: string;
    firmsActiveHotspots?: number;
    firmsMaxFrp?: number;
    calibrationApplied?: boolean;
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

type FirmsHotspotItem = {
    latitude: number;
    longitude: number;
    province: string | null;
    province_code?: string | null;
    district: string | null;
    island?: string;
    brightness: number;
    frp: number;
    confidence: string;
    acq_date: string;
    acq_time: string;
    satellite: string;
    daynight?: string;
};

type RealtimeRegionItem = {
    province?: string;
    region: string;
    island?: string;
    location: string;
    latitude: number;
    longitude: number;
    probability_fire: number;
    risk_level: string;
    prediction: number;
    firms_active_hotspots?: number;
    firms_max_frp?: number;
    calibration_applied?: boolean;
    weather: {
        T2M: number;
        RH2M: number;
        PRECTOTCORR: number;
        WS10M: number;
    };
};

const { theme, toggleTheme } = useTheme();

const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const mapElement = ref<HTMLDivElement | null>(null);
const isMapExpanded = ref(false);
let previousBodyOverflow = '';

function toggleSidebar() {
    if (window.innerWidth <= 900) {
        mobileMenuOpen.value = !mobileMenuOpen.value;
    } else {
        sidebarCollapsed.value = !sidebarCollapsed.value;
        localStorage.setItem('nf-sidebar-collapsed', String(sidebarCollapsed.value));
    }
}

const mapMode = ref<MapMode>('firms');

// Form input sementara (sebelum tombol terapkan diklik)
const formRegion = ref('all');
const formStatus = ref<'all' | 'fire' | 'non-fire'>('all');
const formFirmsDays = ref<number>(2);
const formStartDate = ref('');
const formEndDate = ref('');

// Filter aktif yang benar-benar dieksekusi ke sistem/API
const selectedRegion = ref('all');
const selectedStatus = ref<'all' | 'fire' | 'non-fire'>('all');
const firmsDays = ref<number>(2);
const startDate = ref('');
const endDate = ref('');

const hotspots = ref<Hotspot[]>([]);
const realtimePoints = ref<Hotspot[]>([]);
const firmsPoints = ref<Hotspot[]>([]);
const firmsSourceLabel = ref('NASA FIRMS (VIIRS_SNPP_NRT)');
const firmsIsLive = ref(true);

const totalApiRecords = ref(0);
const totalFireRecords = ref(0);
const totalNonFireRecords = ref(0);
const hasMore = ref(false);

const selectedHotspot = ref<Hotspot | null>(null);
const loading = ref(false);
const predictingPin = ref(false);
const mapReady = ref(false);
const errorMessage = ref('');
const copyMessage = ref('');

const pageSize = 500;
const currentOffset = ref(0);
const requestVersion = ref(0);

let map: L.Map | null = null;
let markerLayer: L.LayerGroup | null = null;
let customPinMarker: L.Marker | null = null;
let copyMessageTimeout: ReturnType<typeof setTimeout> | null = null;
let requestController: AbortController | null = null;

const PROVINCE_TO_ISLAND_MAP: Record<string, string> = {
    'Aceh': 'Sumatra',
    'Sumatera Utara': 'Sumatra',
    'Sumatera Barat': 'Sumatra',
    'Riau': 'Sumatra',
    'Kepulauan Riau': 'Sumatra',
    'Jambi': 'Sumatra',
    'Sumatera Selatan': 'Sumatra',
    'Kepulauan Bangka Belitung': 'Sumatra',
    'Bengkulu': 'Sumatra',
    'Lampung': 'Sumatra',
    'DKI Jakarta': 'Java-Bali-Nusa Tenggara',
    'Jawa Barat': 'Java-Bali-Nusa Tenggara',
    'Jawa Tengah': 'Java-Bali-Nusa Tenggara',
    'DI Yogyakarta': 'Java-Bali-Nusa Tenggara',
    'Jawa Timur': 'Java-Bali-Nusa Tenggara',
    'Banten': 'Java-Bali-Nusa Tenggara',
    'Bali': 'Java-Bali-Nusa Tenggara',
    'Nusa Tenggara Barat': 'Java-Bali-Nusa Tenggara',
    'Nusa Tenggara Timur': 'Java-Bali-Nusa Tenggara',
    'Kalimantan Barat': 'Kalimantan',
    'Kalimantan Tengah': 'Kalimantan',
    'Kalimantan Selatan': 'Kalimantan',
    'Kalimantan Timur': 'Kalimantan',
    'Kalimantan Utara': 'Kalimantan',
    'Sulawesi Utara': 'Sulawesi',
    'Sulawesi Tengah': 'Sulawesi',
    'Sulawesi Selatan': 'Sulawesi',
    'Sulawesi Tenggara': 'Sulawesi',
    'Gorontalo': 'Sulawesi',
    'Sulawesi Barat': 'Sulawesi',
    'Maluku': 'Maluku',
    'Maluku Utara': 'Maluku',
    'Papua': 'Papua',
    'Papua Barat': 'Papua',
    'Papua Selatan': 'Papua',
    'Papua Tengah': 'Papua',
    'Papua Pegunungan': 'Papua',
    'Papua Barat Daya': 'Papua',
};

const regions = Object.keys(PROVINCE_TO_ISLAND_MAP);

const activeDataset = computed(() => {
    if (mapMode.value === 'firms') return firmsPoints.value;
    return hotspots.value;
});

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
    let list = activeDataset.value;

    if (mapMode.value === 'firms') {
        if (selectedRegion.value !== 'all') {
            list = list.filter((item) => item.region === selectedRegion.value);
        }
        if (selectedStatus.value === 'fire') {
            list = list.filter((item) => (item.frp ?? 0) >= 10);
        } else if (selectedStatus.value === 'non-fire') {
            list = list.filter((item) => (item.frp ?? 0) < 10);
        }
    }

    return list;
});

const totalHotspots = computed(() => {
    if (mapMode.value === 'firms') {
        return filteredHotspots.value.length;
    }
    return selectedStatus.value === 'non-fire' ? 0 : totalFireRecords.value;
});

const totalNonFire = computed(() => {
    if (mapMode.value === 'firms') {
        if (filteredHotspots.value.length === 0) return 0;
        return Math.round(
            Math.max(...filteredHotspots.value.map((i) => i.frp ?? 0)) * 10,
        ) / 10;
    }
    return selectedStatus.value === 'fire' ? 0 : totalNonFireRecords.value;
});

const affectedProvincesCount = computed(() => {
    if (mapMode.value === 'firms') {
        const uniqueProvs = new Set(
            filteredHotspots.value
                .map((i) => i.region)
                .filter((r) => r && r !== 'Unknown' && r !== 'Tidak diketahui'),
        );
        return uniqueProvs.size;
    }
    return selectedRegion.value === 'all' ? regions.length : 1;
});

const totalGridRecords = computed(() =>
    mapMode.value !== 'historical'
        ? filteredHotspots.value.length
        : totalApiRecords.value,
);

const dateRangeInvalid = computed(
    () =>
        Boolean(formStartDate.value && formEndDate.value) &&
        formStartDate.value > formEndDate.value,
);

const hasActiveFilter = computed(() =>
    formRegion.value !== 'all' ||
    formStatus.value !== 'all' ||
    Boolean(formStartDate.value) ||
    Boolean(formEndDate.value),
);

function getCsrfToken(): string {
    return (
        document
            .querySelector('meta[name="csrf-token"]')
            ?.getAttribute('content') || ''
    );
}

function statusLabel(item: Hotspot): string {
    if (mapMode.value === 'firms') {
        const frp = item.frp ?? 0;
        const level = frp >= 20 ? 'High FRP' : frp >= 8 ? 'Moderate FRP' : 'Low FRP';
        return `${level} (${frp.toFixed(1)} MW)`;
    }
    if (mapMode.value === 'realtime' && item.riskLevel) {
        return `${item.riskLevel} (${((item.probabilityFire ?? 0) * 100).toFixed(1)}%)`;
    }
    return item.isFire ? 'Fire' : 'Non-fire';
}

function statusColor(item: Hotspot): string {
    if (mapMode.value === 'firms') {
        const frp = item.frp ?? 0;
        if (frp >= 20) return '#ef4444';
        if (frp >= 8) return '#f59e0b';
        return '#f97316';
    }
    if (mapMode.value === 'realtime') {
        if (item.riskLevel === 'High' || item.isFire) return '#ef4444';
        if (item.riskLevel === 'Moderate') return '#f59e0b';
        return '#10b981';
    }
    return item.isFire ? '#ef4444' : '#3b82f6';
}

function createMarkerIcon(item: Hotspot): L.DivIcon {
    return L.divIcon({
        className: 'nf-hotspot-marker-wrapper',
        html: `
            <div class="nf-hotspot-marker"
                 style="--marker-color:${statusColor(item)}">
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
    if (mapMode.value === 'firms') {
        return `
            <div class="nf-hotspot-popup">
                <strong>${escapeHtml(item.location)}</strong>
                <p>Province: ${escapeHtml(item.region)}</p>
                <p>Intensity (FRP): <strong>${(item.frp ?? 0).toFixed(2)} MW</strong></p>
                <p>Brightness: ${item.brightness ?? '—'} K · Conf: ${escapeHtml(item.confidence ?? 'nominal')}</p>
                <p>Satellite Time: ${escapeHtml(item.date)} ${escapeHtml(item.acqTime ?? '')} (Sensor ${escapeHtml(item.satellite ?? 'VIIRS')})</p>
                <p>Coordinates: ${item.latitude.toFixed(4)}, ${item.longitude.toFixed(4)}</p>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #e5e7eb;">
                    <a href="/ai-prediction?lat=${item.latitude}&lon=${item.longitude}" style="color: #16a34a; font-weight: 600; font-size: 11px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        ⚡ Analyze Risk in AI Prediction &rarr;
                    </a>
                </div>
            </div>
        `;
    }



    return `
        <div class="nf-hotspot-popup">
            <strong>${escapeHtml(item.gridId)}</strong>
            <p>Region: ${escapeHtml(item.region)}</p>
            <p>Location: ${escapeHtml(item.location)}</p>
            <p>Date: ${escapeHtml(item.date)}</p>
            <p>Data status: ${statusLabel(item)}</p>
            <p>Hotspot count: ${item.hotspotCount}</p>
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
        gridId: String(row.GRID_ID ?? 'Unknown'),
        location: String(row.LOCATION ?? 'Unknown'),
        latitude,
        longitude,
        date: String(row.DATE ?? '').slice(0, 10),
        region: String(row.REGION ?? 'Unknown'),
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
            { icon: createMarkerIcon(item) },
        );

        marker.bindPopup(popupContent(item));

        marker.on('click', () => {
            selectedHotspot.value = item;
        });

        markerLayer.addLayer(marker);
    }
}

async function handleMapClick(e: L.LeafletMouseEvent): Promise<void> {
    if (mapMode.value === 'historical' || predictingPin.value) return;

    const lat = Number(e.latlng.lat.toFixed(4));
    const lon = Number(e.latlng.lng.toFixed(4));

    predictingPin.value = true;
    errorMessage.value = '';

    try {
        const response = await fetch('/internal/ai/predict-realtime', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-TOKEN': getCsrfToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                LATITUDE: lat,
                LONGITUDE: lon,
            }),
        });

        const res = await response.json();
        if (!response.ok || res?.status !== 'success') {
            throw new Error(res?.message || 'Failed to analyze coordinate point.');
        }

        const locName = [
            res.coordinates?.district,
            res.coordinates?.province,
        ]
            .filter(Boolean)
            .join(', ') || `Selected Pin (${lat}, ${lon})`;

        const w = res.weather_realtime;
        const customItem: Hotspot = {
            id: Date.now(),
            gridId: `CUSTOM-${lat.toFixed(2)}_${lon.toFixed(2)}`,
            location: locName,
            latitude: lat,
            longitude: lon,
            date: new Date().toISOString().slice(0, 10),
            region: res.coordinates?.province || 'Custom Coordinates',
            district: res.coordinates?.district || undefined,
            hotspotCount: res.firms_active_hotspots ?? (res.prediction === 1 ? 1 : 0),
            isFire: res.prediction === 1,
            probabilityFire: res.probability_fire,
            riskLevel: res.risk_level,
            firmsActiveHotspots: res.firms_active_hotspots ?? 0,
            firmsMaxFrp: res.firms_max_frp ?? 0,
            calibrationApplied: Boolean(res.calibration_applied),
            weatherSummary: w
                ? `${w.T2M}°C · RH ${w.RH2M}% · Rain ${w.PRECTOTCORR}mm`
                : undefined,
        };

        if (customPinMarker && map) {
            map.removeLayer(customPinMarker);
        }

        if (map) {
            customPinMarker = L.marker([lat, lon], {
                icon: createMarkerIcon(customItem),
            })
                .addTo(map)
                .bindPopup(
                    `
                    <div class="nf-hotspot-popup">
                        <strong>${escapeHtml(customItem.location)}</strong>
                        <p>Province: ${escapeHtml(customItem.region)}</p>
                        <p>AI Fusion Risk: <strong>${escapeHtml(customItem.riskLevel ?? 'Low')} (${((customItem.probabilityFire ?? 0) * 100).toFixed(1)}%)</strong></p>
                        <p>Nearby FIRMS Hotspots: <strong>${customItem.firmsActiveHotspots ?? 0}</strong></p>
                        ${customItem.weatherSummary ? `<p>Weather: ${escapeHtml(customItem.weatherSummary)}</p>` : ''}
                        <p>Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}</p>
                    </div>
                `,
                )
                .openPopup();
        }

        selectedHotspot.value = customItem;
    } catch (err) {
        errorMessage.value =
            err instanceof Error
                ? err.message
                : 'Failed to predict selected coordinate.';
    } finally {
        predictingPin.value = false;
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
    map.on('click', (e: L.LeafletMouseEvent) => {
        void handleMapClick(e);
    });

    mapReady.value = true;

    nextTick(() => map?.invalidateSize());
}

async function loadFirmsHotspots(): Promise<void> {
    loading.value = true;
    errorMessage.value = '';

    try {
        const params = new URLSearchParams({
            days: String(firmsDays.value),
        });

        const response = await fetch(`/internal/ai/firms-hotspots?${params.toString()}`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });

        const result = await response.json();
        if (!response.ok || result?.status !== 'success' || !Array.isArray(result.data)) {
            throw new Error(result?.message || 'Failed to load NASA FIRMS satellite hotspots.');
        }

        firmsSourceLabel.value = result.source || 'NASA FIRMS (VIIRS_SNPP_NRT)';
        firmsIsLive.value = Boolean(result.live);

        firmsPoints.value = result.data.map(
            (item: FirmsHotspotItem, idx: number) => {
                const prov = item.province || 'Unknown';
                const locParts = [item.district, item.province].filter(Boolean);
                return {
                    id: idx + 1,
                    gridId: `VIIRS-${String(idx + 1).padStart(4, '0')}`,
                    location:
                        locParts.length > 0
                            ? locParts.join(', ')
                            : `Coordinates (${Number(item.latitude).toFixed(3)}, ${Number(item.longitude).toFixed(3)})`,
                    latitude: Number(item.latitude),
                    longitude: Number(item.longitude),
                    date: item.acq_date || new Date().toISOString().slice(0, 10),
                    region: prov,
                    district: item.district || undefined,
                    hotspotCount: 1,
                    isFire: true,
                    frp: Number(item.frp ?? 0),
                    brightness: Number(item.brightness ?? 0),
                    confidence: item.confidence || 'nominal',
                    acqTime: item.acq_time || '',
                    satellite: item.satellite || 'VIIRS',
                };
            },
        );
    } catch (error) {
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'An error occurred while loading NASA FIRMS satellite data.';
    } finally {
        loading.value = false;
        renderMarkers();
    }
}


async function loadHotspots(): Promise<void> {
    if (mapMode.value === 'firms') {
        await loadFirmsHotspots();
        return;
    }

    if (dateRangeInvalid.value) {
        errorMessage.value =
            'Start date cannot be later than end date.';
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
        const mappedIsland =
            PROVINCE_TO_ISLAND_MAP[selectedRegion.value] ?? selectedRegion.value;
        params.set('region', mappedIsland);
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
                `Data request failed (HTTP ${response.status}).`,
            );
        }

        if (
            !result ||
            result.status !== 'success' ||
            !Array.isArray(result.data)
        ) {
            throw new Error(
                'Invalid API response format or hotspot data not found.',
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
                'Data is available, but no valid coordinates or status found on this page.';
        }
    } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return;
        if (thisRequest !== requestVersion.value) return;

        console.error('Failed to load hotspot data:', error);

        errorMessage.value = error instanceof Error
            ? error.message
            : 'An error occurred while fetching hotspot data.';
    } finally {
        if (thisRequest === requestVersion.value) {
            loading.value = false;
            renderMarkers();
        }
    }
}

function switchMode(mode: MapMode): void {
    if (mapMode.value === mode) return;
    mapMode.value = mode;
    selectedHotspot.value = null;
    currentOffset.value = 0;
    if (customPinMarker && map) {
        map.removeLayer(customPinMarker);
        customPinMarker = null;
    }
    void loadHotspots();
}

function applyFilters(): void {
    if (dateRangeInvalid.value) {
        errorMessage.value =
            'Start date cannot be later than end date.';
        return;
    }

    // Move temporary form state to active state
    selectedRegion.value = formRegion.value;
    selectedStatus.value = formStatus.value;
    firmsDays.value = formFirmsDays.value;
    startDate.value = formStartDate.value;
    endDate.value = formEndDate.value;

    currentOffset.value = 0;
    selectedHotspot.value = null;

    if (mapMode.value === 'firms') {
        void loadFirmsHotspots();
    } else {
        void loadHotspots();
    }

    // Shift map view if a specific province is selected
    if (selectedRegion.value !== 'all' && map) {
        const target = activeDataset.value.find(
            (p) => p.region === selectedRegion.value,
        );
        if (target) {
            focusHotspot(target);
        }
    } else if (map) {
        map.flyTo([-2.5, 118], 5, { duration: 0.6 });
    }
}

function resetFilters(): void {
    formRegion.value = 'all';
    formStatus.value = 'all';
    formFirmsDays.value = 2;
    formStartDate.value = '';
    formEndDate.value = '';

    applyFilters();
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

            if (!copied) throw new Error('Clipboard is unavailable.');
        }

        showCopyMessage('Coordinates copied to clipboard.');
    } catch (error) {
        console.error(error);
        showCopyMessage('Failed to copy. Please copy coordinates manually.');
    }
}

function exportCsv(): void {
    const headers = [
        'ID',
        'Grid ID',
        'Location',
        'Latitude',
        'Longitude',
        'Date',
        'Province / Region',
        'Hotspot Count / FRP',
        'Data Status',
    ];

    const rows = filteredHotspots.value.map((item) => [
        item.id,
        item.gridId,
        item.location,
        item.latitude,
        item.longitude,
        item.date,
        item.region,
        mapMode.value === 'firms' ? `${item.frp ?? 0} MW` : item.hotspotCount,
        statusLabel(item),
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
        `nusafire-hotspots-${mapMode.value}-${new Date().toISOString().slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

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
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) sidebarCollapsed.value = saved === 'true';
    await nextTick();
    initializeMap();
    await loadHotspots();
});

onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleMapEscape);
    document.body.style.overflow = previousBodyOverflow;
    if (statAnimationFrame !== null) window.cancelAnimationFrame(statAnimationFrame);
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
            :class="{ 'nf-main-collapsed': sidebarCollapsed }"
        >
            <header class="nf-topbar">
                <div class="nf-topbar-left">
                    <button
                        class="nf-icon-button nf-mobile-menu"
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

                    <h1>Hotspot Map</h1>
                </div>

                <div class="nf-topbar-right">
                    <div class="nf-mode-switch" role="tablist">
                        <button
                            type="button"
                            class="nf-mode-btn"
                            :class="{ active: mapMode === 'firms' }"
                            @click="switchMode('firms')"
                        >
                            🛰️ Live Satellite (NASA FIRMS)
                        </button>
                        <button
                            type="button"
                            class="nf-mode-btn"
                            :class="{ active: mapMode === 'historical' }"
                            @click="switchMode('historical')"
                        >
                            📜 Historical Hotspots (2022–2024)
                        </button>
                    </div>

                    <button
                        class="nf-icon-button"
                        type="button"
                        :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
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

            <div class="nf-page-content">
                <section class="nf-page-heading">
                    <div class="nf-heading-text">
                        <div class="nf-eyebrow">
                            <span class="nf-eyebrow-line"></span>
                            {{
                                mapMode === 'firms'
                                    ? 'NASA FIRMS VIIRS 375M LIVE SATELLITE OBSERVATION'
                                    : 'HISTORICAL DATASET ARCHIVE (2022–2024)'
                            }}
                        </div>
                        <h1>Hotspot Mapping</h1>
                        <p>
                            {{
                                mapMode === 'firms'
                                    ? 'Active fire hotspot detection from NASA FIRMS (VIIRS) satellites across Indonesia. Click any point on the map to run AI fusion analysis.'
                                    : mapMode === 'realtime'
                                      ? 'Daily fire risk prediction across 38 Indonesian provinces fused with real-time meteorology & NASA FIRMS satellite detection.'
                                      : 'Explore historical hotspot grid dataset by coordinates, region, date, and classification status.'
                            }}
                        </p>
                    </div>

                    <div class="nf-heading-actions">
                        <div class="nf-heading-card">
                            <div class="nf-heading-card-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="18" height="18" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <polyline points="12 6 12 12 16 14" />
                                </svg>
                            </div>
                            <div>
                                <strong>NASA FIRMS VIIRS Satellites</strong>
                                <span>{{ (filteredHotspots.length || 0).toLocaleString('en-US') }} Hotspots Detected</span>
                            </div>
                        </div>

                        <button
                            class="nf-button nf-button-primary nf-export-btn"
                            type="button"
                            :disabled="filteredHotspots.length === 0"
                            @click="exportCsv"
                        >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="16" height="16" aria-hidden="true">
                                <path d="M12 3v12m-5-5 5 5 5-5M5 17v3h14v-3" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                            Export CSV
                        </button>
                    </div>
                </section>

                <div v-if="errorMessage" class="nf-alert" role="alert">
                    <strong>Hotspot data error.</strong>
                    <span>{{ errorMessage }}</span>
                    <button
                        class="nf-retry-button"
                        type="button"
                        :disabled="loading"
                        @click="loadHotspots"
                    >
                        {{ loading ? 'Loading...' : 'Try again' }}
                    </button>
                </div>

                <section class="nf-stats-grid">
                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon red">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                            <span>
                                {{
                                    mapMode === 'firms'
                                        ? 'Satellite Hotspots'
                                        : mapMode === 'realtime'
                                          ? 'High Risk Zones'
                                          : 'Fire Records'
                                }}
                            </span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : totalHotspots.toLocaleString('en-US') }}
                        </div>
                        <p>
                            {{
                                mapMode === 'firms'
                                    ? `Active thermal detections (last ${firmsDays} days).`
                                    : mapMode === 'realtime'
                                      ? 'Provinces with high fire risk probability.'
                                      : 'Total fire records matching server filter.'
                            }}
                        </p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon blue">
                                <svg v-if="mapMode === 'firms'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </span>
                            <span>
                                {{
                                    mapMode === 'firms'
                                        ? 'Maximum FRP (MW)'
                                        : mapMode === 'realtime'
                                          ? 'Safe / Low Risk Zones'
                                          : 'Non-fire Records'
                                }}
                            </span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : totalNonFire.toLocaleString('en-US') }}
                        </div>
                        <p>
                            {{
                                mapMode === 'firms'
                                    ? 'Highest Fire Radiative Power detected.'
                                    : mapMode === 'realtime'
                                      ? 'Provinces below high risk threshold.'
                                      : 'Total non-fire records matching server filter.'
                            }}
                        </p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon green">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="22" y1="12" x2="18" y2="12" />
                                    <line x1="6" y1="12" x2="2" y2="12" />
                                    <line x1="12" y1="6" x2="12" y2="2" />
                                    <line x1="12" y1="22" x2="12" y2="18" />
                                </svg>
                            </span>
                            <span>{{ mapMode === 'firms' ? 'Detected Provinces' : 'Monitored Provinces' }}</span>
                        </div>
                        <div class="nf-stat-value">
                            {{ loading ? '—' : affectedProvincesCount }}
                        </div>
                        <p>
                            {{
                                mapMode === 'firms'
                                    ? (selectedRegion === 'all' ? 'Provinces with active hotspots' : selectedRegion)
                                    : (selectedRegion === 'all' ? '38 Indonesian Provinces' : selectedRegion)
                            }}
                        </p>
                    </article>

                    <article class="nf-card nf-stat-card">
                        <div class="nf-stat-heading">
                            <span class="nf-stat-icon orange">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                    <ellipse cx="12" cy="5" rx="9" ry="3" />
                                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                                </svg>
                            </span>
                            <span>{{ mapMode === 'firms' ? 'Satellite Feed Status' : 'Total Hotspots / Records' }}</span>
                        </div>
                        <div class="nf-stat-value">
                            {{
                                mapMode === 'firms'
                                    ? (firmsIsLive ? 'LIVE' : 'FALLBACK')
                                    : loading
                                      ? '—'
                                      : totalGridRecords.toLocaleString('en-US')
                            }}
                        </div>
                        <p>
                            {{
                                mapMode === 'firms'
                                    ? firmsSourceLabel
                                    : mapMode === 'realtime'
                                      ? 'Active monitoring points today.'
                                      : 'Total data matching server filter.'
                            }}
                        </p>
                    </article>
                </section>

                <section class="nf-card nf-panel nf-filter-panel">
                    <div class="nf-filter-header">
                        <div class="nf-filter-header-main">
                            <span class="nf-filter-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <path d="M4 5h16M7 12h10m-7 7h4" />
                                </svg>
                            </span>
                            <div>
                                <h3>Filter Hotspot Data</h3>
                                <p>
                                    Select province and parameters then click Apply Filter to refine data.
                                </p>
                            </div>
                        </div>

                        <button
                            class="nf-button nf-button-outline nf-reset-button"
                            type="button"
                            :disabled="loading || (!hasActiveFilter && formFirmsDays === 2)"
                            @click="resetFilters"
                        >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                <path d="M3 12a9 9 0 1 0 3-6.7L3 8m0-5v5h5" />
                            </svg>
                            Reset filter
                        </button>
                    </div>

                    <p v-if="dateRangeInvalid" class="nf-date-error" role="alert">
                        Start date cannot be later than end date.
                    </p>

                    <form
                        class="nf-filter-grid"
                        :class="mapMode === 'historical' ? 'is-historical' : mapMode === 'firms' ? 'is-firms' : 'is-realtime'"
                        @submit.prevent="applyFilters"
                    >
                        <label class="nf-field">
                            <span>Province (38 Provinces)</span>
                            <select v-model="formRegion">
                                <option value="all">All provinces (38)</option>
                                <option
                                    v-for="region in regions"
                                    :key="region"
                                    :value="region"
                                >
                                    {{ region }}
                                </option>
                            </select>
                        </label>

                        <label v-if="mapMode === 'firms'" class="nf-field">
                            <span>Satellite Observation Range</span>
                            <select v-model.number="formFirmsDays">
                                <option :value="1">Last 24 Hours (1 Day)</option>
                                <option :value="2">Last 48 Hours (2 Days)</option>
                                <option :value="5">Last 5 Days</option>
                                <option :value="7">Last 7 Days</option>
                            </select>
                        </label>

                        <label class="nf-field">
                            <span>{{ mapMode === 'firms' ? 'Thermal Intensity (FRP)' : 'Data status' }}</span>
                            <select v-model="formStatus">
                                <option value="all">All statuses</option>
                                <option value="fire">
                                    {{ mapMode === 'firms' ? 'High Intensity (FRP ≥ 10 MW)' : 'Fire / High Risk' }}
                                </option>
                                <option value="non-fire">
                                    {{ mapMode === 'firms' ? 'Low Intensity (FRP < 10 MW)' : 'Non-fire / Low Risk' }}
                                </option>
                            </select>
                        </label>

                        <label v-if="mapMode === 'historical'" class="nf-field">
                            <span>Start date</span>
                            <input
                                v-model="formStartDate"
                                type="date"
                                :max="formEndDate || undefined"
                            />
                        </label>

                        <label v-if="mapMode === 'historical'" class="nf-field">
                            <span>End date</span>
                            <input
                                v-model="formEndDate"
                                type="date"
                                :min="formStartDate || undefined"
                            />
                        </label>

                        <div class="nf-filter-footer">
                            <span class="nf-filter-hint">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                                    <circle cx="12" cy="12" r="9" />
                                    <path d="M12 11v5m0-8h.01" />
                                </svg>
                                {{
                                    mapMode === 'firms'
                                        ? 'Click satellite fire hotspots for FRP details or click any map area for AI fusion risk analysis.'
                                        : mapMode === 'realtime'
                                          ? 'Click anywhere on the map to evaluate fire risk for any coordinate.'
                                          : 'Click Apply Filter to refresh archived server data.'
                                }}
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
                                {{ loading ? 'Loading data...' : 'Apply Filter' }}
                            </button>
                        </div>
                    </form>
                </section>

                <section class="nf-main-grid">
                    <article class="nf-card nf-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>
                                    {{
                                        mapMode === 'firms'
                                            ? 'Active NASA FIRMS (VIIRS) Hotspot Map'
                                            : mapMode === 'realtime'
                                              ? 'Real-Time Risk Prediction Map (38 Provinces)'
                                              : 'Hotspot Distribution Map'
                                    }}
                                </h3>
                                <p>
                                    {{
                                        mapMode === 'firms'
                                            ? 'Click hotspot markers to view satellite intensity or click map for risk simulation.'
                                            : mapMode === 'realtime'
                                              ? 'Click map for coordinate analysis or click provincial markers.'
                                              : 'Click marker to view record information.'
                                    }}
                                </p>
                            </div>
                            <span class="nf-count">
                                {{ predictingPin ? 'Analyzing coordinates...' : `${filteredHotspots.length.toLocaleString('en-US')} markers` }}
                            </span>
                        </div>

                        <div class="nf-legend">
                            <template v-if="mapMode === 'firms'">
                                <span><i class="high"></i> High FRP (≥ 20 MW)</span>
                                <span><i class="moderate"></i> Moderate FRP (8–19 MW)</span>
                                <span><i class="orange-dot"></i> Low FRP (&lt; 8 MW)</span>
                            </template>
                            <template v-else-if="mapMode === 'realtime'">
                                <span><i class="high"></i> High Risk</span>
                                <span><i class="moderate"></i> Moderate Risk</span>
                                <span><i class="safe"></i> Low Risk</span>
                            </template>
                            <template v-else>
                                <span><i class="high"></i> Fire</span>
                                <span><i class="low"></i> Non-fire</span>
                            </template>
                        </div>

                        <Teleport to="body" :disabled="!isMapExpanded">
                            <div
                                v-if="isMapExpanded"
                                class="nf-map-backdrop"
                                aria-hidden="true"
                                @click="closeMapExpansion"
                            ></div>

                            <div v-if="loading" class="nf-map-message">
                                Loading hotspot data...
                            </div>
                            <div v-else-if="errorMessage" class="nf-map-message">
                                {{ errorMessage }}
                            </div>
                            <div v-else-if="filteredHotspots.length === 0" class="nf-map-message">
                                No matching data found.
                            </div>
                        </div>

                        <div class="nf-map-footer">
                            <span><i></i> OpenStreetMap · {{ firmsSourceLabel }}</span>
                            <span>Decimal degree coordinates</span>
                        </div>
                    </article>

                    <article class="nf-card nf-panel nf-detail-panel">
                        <div class="nf-section-heading">
                            <div>
                                <h3>Hotspot Details</h3>
                                <p>Information on selected hotspot or record.</p>
                            </div>
                        </div>

                        <template v-if="selectedHotspot">
                            <div class="nf-detail-hero">
                                <span
                                    class="nf-stat-icon"
                                    :class="selectedHotspot.isFire ? 'red' : 'blue'"
                                >
                                    <svg v-if="selectedHotspot.isFire" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" aria-hidden="true">
                                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </span>
                                <div>
                                    <small>
                                        {{
                                            selectedHotspot.gridId.startsWith('CUSTOM-')
                                                ? 'CUSTOM COORDINATE ANALYSIS'
                                                : mapMode === 'firms'
                                                  ? 'NASA FIRMS SATELLITE DETECTION'
                                                  : mapMode === 'realtime'
                                                    ? 'REAL-TIME FUSION ANALYSIS'
                                                    : `RECORD #${selectedHotspot.id}`
                                        }}
                                    </small>
                                    <h4>{{ selectedHotspot.location }}</h4>
                                    <span
                                        class="nf-confidence"
                                        :class="selectedHotspot.isFire ? 'confidence-high' : 'confidence-low'"
                                    >
                                        {{ statusLabel(selectedHotspot) }}
                                    </span>
                                </div>
                            </div>

                            <div class="nf-detail-list">
                                <div><span>Grid / Sensor ID</span><strong>{{ selectedHotspot.gridId }}</strong></div>
                                <div><span>Location</span><strong>{{ selectedHotspot.location }}</strong></div>
                                <div><span>Province / Region</span><strong>{{ selectedHotspot.region }}</strong></div>
                                <div><span>Acquisition Date</span><strong>{{ selectedHotspot.date }} {{ selectedHotspot.acqTime || '' }}</strong></div>
                                <div><span>Latitude</span><strong>{{ selectedHotspot.latitude.toFixed(5) }}</strong></div>
                                <div><span>Longitude</span><strong>{{ selectedHotspot.longitude.toFixed(5) }}</strong></div>
                                <template v-if="selectedHotspot.frp !== undefined">
                                    <div><span>Intensity (FRP)</span><strong>{{ selectedHotspot.frp.toFixed(2) }} MW</strong></div>
                                    <div><span>Brightness Temp</span><strong>{{ selectedHotspot.brightness ?? '—' }} K</strong></div>
                                    <div><span>Confidence</span><strong>{{ selectedHotspot.confidence ?? 'nominal' }}</strong></div>
                                </template>
                                <template v-else-if="selectedHotspot.weatherSummary">
                                    <div><span>Current Weather</span><strong>{{ selectedHotspot.weatherSummary }}</strong></div>
                                    <div><span>Nearby FIRMS Hotspots</span><strong>{{ selectedHotspot.firmsActiveHotspots ?? 0 }} hotspots (Max {{ selectedHotspot.firmsMaxFrp ?? 0 }} MW)</strong></div>
                                </template>
                                <div v-else><span>Hotspot count</span><strong>{{ selectedHotspot.hotspotCount }}</strong></div>
                                <div><span>Status</span><strong>{{ statusLabel(selectedHotspot) }}</strong></div>
                            </div>

                            <button
                                class="nf-button nf-button-outline nf-full-button"
                                type="button"
                                @click="copyCoordinates"
                            >
                                Copy coordinates
                            </button>

                            <p v-if="copyMessage" class="nf-copy-message" role="status">
                                {{ copyMessage }}
                            </p>
                        </template>

                        <div v-else class="nf-empty-state">
                            <span class="nf-empty-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="28" height="28" aria-hidden="true">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="22" y1="12" x2="18" y2="12" />
                                    <line x1="6" y1="12" x2="2" y2="12" />
                                    <line x1="12" y1="6" x2="12" y2="2" />
                                    <line x1="12" y1="22" x2="12" y2="18" />
                                </svg>
                            </span>
                            <h4>No location selected</h4>
                            <p>
                                {{
                                    mapMode !== 'historical'
                                        ? 'Select a marker on the map or click anywhere to inspect details and live AI fire risk.'
                                        : 'Select a marker on the map or click View in the table.'
                                }}
                            </p>
                        </div>

                        <div class="nf-note">
                            {{
                                mapMode === 'firms'
                                    ? 'Real-time hotspot data is directly retrieved from NASA FIRMS VIIRS satellites (375m resolution).'
                                    : mapMode === 'realtime'
                                      ? 'Real-Time mode fuses current meteorological parameters and NASA FIRMS hotspots with NusaFire\'s XGBoost model.'
                                      : 'Each record represents a grid/date entry from the historical dataset archive.'
                            }}
                        </div>
                    </article>
                </section>

                <section class="nf-card nf-panel nf-table-panel">
                    <div class="nf-section-heading">
                        <div>
                            <h3>
                                {{
                                    mapMode === 'firms'
                                        ? 'NASA FIRMS Satellite Hotspot List'
                                        : mapMode === 'realtime'
                                          ? 'Real-Time Monitoring List (38 Provinces)'
                                          : 'Hotspot Data List'
                                }}
                            </h3>
                            <p>
                                Table data reflects the active filters and mode selected above.
                            </p>
                        </div>
                        <span class="nf-count">
                            {{ filteredHotspots.length.toLocaleString('en-US') }} records shown
                        </span>
                    </div>

                    <div class="nf-table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Location / Grid</th>
                                    <th>Province / Region</th>
                                    <th>Coordinates</th>
                                    <th>Date</th>
                                    <th>
                                        {{
                                            mapMode === 'firms'
                                                ? 'FRP / Brightness'
                                                : mapMode === 'realtime'
                                                  ? 'Weather & FIRMS'
                                                  : 'Hotspot Count'
                                        }}
                                    </th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="item in filteredHotspots"
                                    :key="item.id"
                                    :class="{ 'is-selected': selectedHotspot?.id === item.id }"
                                >
                                    <td class="nf-id-cell">#{{ item.id }}</td>
                                    <td>{{ item.location }}</td>
                                    <td>{{ item.region }}</td>
                                    <td>
                                        {{ item.latitude.toFixed(3) }},
                                        {{ item.longitude.toFixed(3) }}
                                    </td>
                                    <td>{{ item.date }}</td>
                                    <td>
                                        <template v-if="mapMode === 'firms'">
                                            {{ (item.frp ?? 0).toFixed(1) }} MW · {{ item.brightness ?? '—' }} K
                                        </template>
                                        <template v-else-if="mapMode === 'realtime'">
                                            {{ item.weatherSummary || '—' }} ({{ item.firmsActiveHotspots ?? 0 }} FIRMS)
                                        </template>
                                        <template v-else>
                                            {{ item.hotspotCount }}
                                        </template>
                                    </td>
                                    <td>
                                        <span
                                            class="nf-confidence"
                                            :class="item.isFire ? 'confidence-high' : 'confidence-low'"
                                        >
                                            {{ statusLabel(item) }}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            class="nf-view-button"
                                            type="button"
                                            @click="focusHotspot(item)"
                                        >
                                            View
                                        </button>
                                    </td>
                                </tr>

                                <tr v-if="filteredHotspots.length === 0">
                                    <td colspan="8" class="nf-empty-table">
                                        {{ loading ? 'Loading data...' : 'No matching data found.' }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-if="mapMode === 'historical'" class="nf-pagination">
                        <div>
                            Showing
                            {{ pageStart.toLocaleString('en-US') }}–{{ pageEnd.toLocaleString('en-US') }}
                            of {{ totalApiRecords.toLocaleString('en-US') }} records.
                        </div>

                        <div class="nf-pagination-controls">
                            <button
                                class="nf-button nf-button-outline"
                                type="button"
                                :disabled="loading || currentOffset === 0"
                                @click="previousPage"
                            >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" aria-hidden="true" style="margin-right: 4px; display: inline-block;">
                                    <polyline points="15 18 9 12 15 6" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                                Previous
                            </button>

                            <span>
                                Page {{ currentPage }} of {{ Math.max(totalPages, 1) }}
                            </span>

                            <button
                                class="nf-button nf-button-outline"
                                type="button"
                                :disabled="loading || !hasMore"
                                @click="nextPage"
                            >
                                Next
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" aria-hidden="true" style="margin-left: 4px; display: inline-block;">
                                    <polyline points="9 18 15 12 9 6" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </section>

                <footer class="nf-page-footer">
                    <span>NusaFire · Hotspot Monitoring &amp; Analysis</span>
                    <span>Data powered by NusaFire API &amp; NASA FIRMS</span>
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
    --hm-brand: #165b33;
    --hm-brand-soft: #e8f5e9;

    min-height: 100vh;
    color: var(--hm-text);
    background: var(--hm-bg);
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    font-size: 13px;
    transition: color .2s ease, background .2s ease;
}

.nf-app.nf-hotspotmap.theme-dark,
html.theme-dark .nf-app.nf-hotspotmap,
html.dark .nf-app.nf-hotspotmap {
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
    --hm-brand: #34d399;
    --hm-brand-soft: rgba(52, 211, 153, 0.15);
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
    margin-left: 268px;
    transition: margin-left .25s ease;
}

.nf-main.nf-main-collapsed {
    margin-left: 82px;
}

.nf-hotspotmap .nf-topbar {
    position: sticky;
    z-index: 50;
    top: 0;
    display: flex;
    height: 68px;
    min-height: 68px;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 0 32px;
    background: #ffffff;
    background: var(--hm-surface, #ffffff);
    border-bottom: 1px solid #e5eae4;
    border-bottom: 1px solid var(--hm-border, #e5eae4);
}

.nf-hotspotmap.theme-dark .nf-topbar,
.theme-dark .nf-hotspotmap .nf-topbar {
    background: #19231c;
    background: var(--hm-surface, #19231c);
    border-bottom: 1px solid #2b3a2e;
    border-bottom: 1px solid var(--hm-border, #2b3a2e);
}

.nf-topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-topbar-right {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-mode-switch {
    display: inline-flex;
    padding: 4px;
    border: 1px solid var(--hm-border);
    border-radius: 10px;
    background: var(--hm-soft);
    gap: 4px;
}

.nf-mode-btn {
    padding: 6px 11px;
    border: 0;
    border-radius: 7px;
    background: transparent;
    color: var(--hm-text-soft);
    font-size: 11px;
    font-weight: 650;
    white-space: nowrap;
}

.nf-mode-btn.active {
    background: var(--hm-surface);
    color: var(--hm-text);
    box-shadow: 0 1px 4px rgb(0 0 0 / 8%);
}

.nf-topbar h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 750;
    color: var(--hm-text);
    letter-spacing: -0.01em;
}

.nf-icon-button {
    display: grid;
    width: 38px;
    height: 38px;
    flex-shrink: 0;
    place-items: center;
    border: 1px solid var(--hm-border);
    border-radius: 10px;
    color: var(--hm-text-soft);
    background: var(--hm-surface);
    cursor: pointer;
    transition: color .15s ease, background .15s ease, border-color .15s ease;
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

.nf-eyebrow {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 10px;
    color: var(--hm-brand, #165b33);
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
    background: var(--hm-brand, #165b33);
    flex-shrink: 0;
}

.nf-page-heading h1 {
    margin: 0 0 8px 0;
    font-size: clamp(26px, 2.8vw, 34px);
    font-weight: 750;
    letter-spacing: -1.1px;
    line-height: 1.2;
    color: var(--hm-text, #141f17);
}

.nf-page-heading p,
.nf-section-heading p {
    margin: 0;
    color: var(--hm-text-soft, #5f7065);
    font-size: 13px;
    line-height: 1.6;
    max-width: 660px;
}

.nf-heading-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
}

.nf-heading-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    min-height: 52px;
    background: #ffffff;
    background: var(--hm-surface, #ffffff);
    border: 1px solid #e5eae4;
    border: 1px solid var(--hm-border, #e5eae4);
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    white-space: nowrap;
}

.nf-heading-card-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    min-width: 34px;
    min-height: 34px;
    flex-shrink: 0;
    color: var(--hm-brand, #165b33);
    background: var(--hm-brand-soft, #e8f5e9);
    border-radius: 8px;
    line-height: 0;
    box-sizing: border-box;
    padding: 0;
}

.nf-heading-card-icon svg {
    display: block;
    width: 18px;
    height: 18px;
    margin: auto;
    flex-shrink: 0;
}

.nf-heading-card strong {
    display: block;
    font-size: 12px;
    font-weight: 700;
    color: var(--hm-text, #141f17);
    line-height: 1.3;
}

.nf-heading-card > div > span {
    display: block;
    font-size: 11px;
    color: var(--hm-text-soft, #5f7065);
    line-height: 1.4;
}

.nf-export-btn {
    height: 52px;
    min-height: 52px;
    padding: 0 18px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
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
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}

.nf-button-primary {
    flex-shrink: 0;
    border-color: var(--hm-accent);
    color: #fff;
    background: var(--hm-accent);
}

.nf-button-primary:hover:not(:disabled) {
    filter: brightness(.94);
}

.nf-button-outline {
    color: var(--hm-text);
    background: var(--hm-surface);
}

.nf-button-outline:hover:not(:disabled) {
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
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    border-radius: 10px;
    line-height: 0;
}

.nf-stat-icon svg {
    display: block;
    margin: auto;
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

.nf-filter-panel {
    margin-bottom: 20px;
    scroll-margin-top: 90px;
}

.nf-filter-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding-bottom: 16px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--hm-border);
}

.nf-filter-header-main {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}

.nf-filter-header-main h3 {
    margin: 0 0 4px;
    font-size: 15px;
    font-weight: 750;
}

.nf-filter-header-main p {
    margin: 0;
    color: var(--hm-text-soft);
    font-size: 11px;
    line-height: 1.55;
}

.nf-filter-icon {
    display: grid;
    width: 38px;
    height: 38px;
    flex-shrink: 0;
    place-items: center;
    border-radius: 10px;
    color: var(--hm-accent);
    background: var(--hm-accent-soft);
}

.nf-filter-icon svg {
    width: 19px;
    height: 19px;
}

.nf-reset-button {
    flex-shrink: 0;
}

.nf-filter-grid {
    display: grid;
    gap: 16px;
}

.nf-filter-grid.is-realtime {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.nf-filter-grid.is-firms {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.nf-filter-grid.is-historical {
    grid-template-columns: repeat(4, minmax(0, 1fr));
}

.nf-field {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 7px;
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
    padding: 0 12px;
    border: 1px solid var(--hm-border);
    border-radius: 9px;
    outline: none;
    color: var(--hm-text);
    background: var(--hm-surface);
    font-size: 12px;
    transition: border-color .15s ease, box-shadow .15s ease;
}

.nf-field input:focus,
.nf-field select:focus {
    border-color: var(--hm-accent);
    box-shadow: 0 0 0 3px rgb(217 75 61 / 10%);
}

.nf-filter-footer {
    display: flex;
    grid-column: 1 / -1;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding: 10px 12px;
    border: 1px solid var(--hm-border);
    border-radius: 9px;
    background: var(--hm-soft);
}

.nf-filter-hint {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--hm-text-soft);
    font-size: 11px;
    line-height: 1.5;
}

.nf-filter-hint svg {
    width: 15px;
    height: 15px;
    flex-shrink: 0;
    color: var(--hm-accent);
}

.nf-apply-button {
    min-width: 145px;
}

.nf-date-error {
    margin: 0 0 13px;
    color: #dc3e3e;
    font-size: 11px;
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

.nf-legend .moderate {
    background: #f59e0b;
}

.nf-legend .orange-dot {
    background: #f97316;
}

.nf-legend .safe {
    background: #10b981;
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

.nf-map-expand-button {
    position: absolute;
    z-index: 1200;
    top: 12px;
    right: 12px;
    display: inline-grid;
    width: 40px;
    height: 40px;
    place-items: center;
    border: 1px solid rgb(220 228 220 / 95%);
    border-radius: 10px;
    color: #26372c;
    background: rgb(255 255 255 / 96%);
    box-shadow: 0 3px 12px rgb(22 42 28 / 14%);
    cursor: pointer;
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}

.nf-map-expand-button:hover {
    transform: translateY(-1px);
    background: #fff;
    box-shadow: 0 5px 16px rgb(22 42 28 / 20%);
}

.nf-map-expand-button:focus-visible {
    outline: 3px solid rgb(22 163 74 / 35%);
    outline-offset: 2px;
}

.nf-map-backdrop {
    position: fixed;
    z-index: 2000;
    inset: 0;
    background: rgb(10 20 14 / 58%);
    backdrop-filter: blur(4px);
    animation: nf-hm-fade-in .32s ease-out both;
}

.nf-map-wrap.is-expanded {
    --hm-surface: #fff;
    --hm-soft: #f8faf7;
    --hm-text: #1c2922;
    --hm-text-soft: #526158;
    --hm-muted: #859087;
    --hm-border: #e5eae4;
    --hm-shadow: 0 4px 20px rgb(23 49 33 / 3%);
    position: fixed;
    z-index: 2001;
    inset: 36px;
    width: auto;
    height: auto;
    border-radius: 16px;
    border-color: rgb(255 255 255 / 70%);
    box-shadow: 0 24px 80px rgb(0 0 0 / 35%);
    animation: nf-map-expand-in .38s cubic-bezier(.22, 1, .36, 1) both;
    will-change: opacity, transform;
}

.nf-map-wrap.is-expanded .nf-map-expand-button {
    top: 16px;
    right: 16px;
}

.nf-map-wrap.is-expanded.theme-dark {
    --hm-surface: #19231c;
    --hm-soft: #1d2921;
    --hm-text: #edf4ed;
    --hm-text-soft: #b0bdb2;
    --hm-muted: #849489;
    --hm-border: #2b3a2e;
    --hm-shadow: 0 4px 20px rgb(0 0 0 / 10%);
}

.nf-map-wrap.is-expanded.theme-dark .nf-map-expand-button {
    color: #edf4ed;
    background: rgb(25 35 28 / 96%);
    border-color: #3a4b3d;
}

@keyframes nf-map-expand-in {
    from { opacity: 0; transform: scale(.975); }
    to { opacity: 1; transform: scale(1); }
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

@media (max-width: 1200px) {
    .nf-page-content,
    .nf-topbar {
        padding-right: 22px;
        padding-left: 22px;
    }

    .nf-stats-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .nf-filter-grid.is-historical {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .nf-main-grid {
        grid-template-columns: minmax(0, 1.5fr) minmax(240px, 1fr);
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
}

@media (max-width: 560px) {
    .nf-topbar {
        padding: 12px 14px;
        flex-wrap: wrap;
    }

    .nf-topbar h1 {
        font-size: 18px;
    }

    .nf-page-content {
        padding: 19px 13px;
    }

    .nf-page-heading,
    .nf-filter-header {
        align-items: stretch;
        flex-direction: column;
        gap: 16px;
    }

    .nf-page-heading h1 {
        font-size: 24px;
    }

    .nf-heading-actions {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
    }

    .nf-button-primary,
    .nf-reset-button {
        width: 100%;
    }

    .nf-stats-grid {
        gap: 10px;
    }

    .nf-stat-card {
        padding: 13px;
    }

    .nf-stat-value {
        font-size: 24px;
    }

    .nf-panel {
        padding: 14px;
    }

    .nf-filter-grid.is-realtime,
    .nf-filter-grid.is-firms,
    .nf-filter-grid.is-historical {
        grid-template-columns: minmax(0, 1fr);
    }

    .nf-map-wrap {
        height: 310px;
    }
}
</style>