<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import AppSidebar from '@/components/AppSidebar.vue';
import AppSidebarHeader from '@/components/AppSidebarHeader.vue';
import type { BreadcrumbItemType } from '@/types';

interface Props {
    breadcrumbs?: BreadcrumbItemType[];
}

withDefaults(defineProps<Props>(), {
    breadcrumbs: () => [],
});

// State untuk mengatur apakah sidebar dalam kondisi collapsed (diringkas) atau tidak
const isCollapsed = ref(false);
const mobileOpen = ref(false);

const SIDEBAR_FULL_WIDTH = 268;
const SIDEBAR_COLLAPSED_WIDTH = 82;
const MOBILE_BREAKPOINT = 900;

function isMobile() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
}

function updateScreenSize() {
    if (isMobile()) {
        mobileOpen.value = false;
    }
}

// Fungsi untuk toggle buka/tutup sidebar
function toggleSidebar() {
    if (isMobile()) {
        mobileOpen.value = !mobileOpen.value;
    } else {
        isCollapsed.value = !isCollapsed.value;
        localStorage.setItem('nf-sidebar-collapsed', String(isCollapsed.value));
    }
}

function closeSidebar() {
    mobileOpen.value = false;
}

onMounted(() => {
    // Pulihkan state collapsed dari localStorage
    const saved = localStorage.getItem('nf-sidebar-collapsed');
    if (saved !== null) {
        isCollapsed.value = saved === 'true';
    }
    updateScreenSize();
    window.addEventListener('resize', updateScreenSize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', updateScreenSize);
});
</script>

<template>
    <div
        class="nf-layout-root"
        :class="{
            'nf-layout-collapsed': isCollapsed,
            'nf-layout-mobile-open': mobileOpen,
        }"
    >
        <!-- Kirim state collapsed dan mobileOpen ke AppSidebar -->
        <AppSidebar
            v-model:collapsed="isCollapsed"
            :mobile-open="mobileOpen"
            @close="closeSidebar"
        />

        <div class="nf-layout-main">
            <AppSidebarHeader
                :breadcrumbs="breadcrumbs"
                @toggle-sidebar="toggleSidebar"
            />

            <div class="nf-layout-content">
                <slot />
            </div>
        </div>
    </div>
</template>

<style>
/* ========================================
   NUSAFIRE LAYOUT ROOT
======================================== */

.nf-layout-root {
    --nf-layout-sidebar-width: 268px;
    --nf-layout-sidebar-collapsed-width: 82px;

    display: flex;
    min-height: 100dvh;
    width: 100%;
    background: var(--background, #f7f9f8);
}

/* Area konten utama – bergeser sesuai lebar sidebar */
.nf-layout-main {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-width: 0;
    min-height: 100dvh;
    margin-left: var(--nf-layout-sidebar-width);
    transition: margin-left 0.25s ease;
    overflow: hidden;
}

/* Saat sidebar di-collapse, margin diperkecil */
.nf-layout-collapsed .nf-layout-main {
    margin-left: var(--nf-layout-sidebar-collapsed-width);
}

/* Area scrollable konten halaman */
.nf-layout-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
}

/* ========================================
   RESPONSIVE – Mobile
======================================== */

@media (max-width: 900px) {
    .nf-layout-main {
        margin-left: 0 !important;
    }
}
</style>