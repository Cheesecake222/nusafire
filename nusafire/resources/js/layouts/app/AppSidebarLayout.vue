 
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import AppContent from '@/components/AppContent.vue';
import AppShell from '@/components/AppShell.vue';
import AppSidebar from '@/components/AppSidebar.vue';
import AppSidebarHeader from '@/components/AppSidebarHeader.vue';
import type { BreadcrumbItemType } from '@/types';

interface Props {
    breadcrumbs?: BreadcrumbItemType[];
}

withDefaults(defineProps<Props>(), {
    breadcrumbs: () => [],
});

const sidebarOpen = ref(true);

function updateScreenSize() {
    sidebarOpen.value = window.innerWidth > 900;
}

function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
    sidebarOpen.value = false;
}

onMounted(() => {
    updateScreenSize();
    window.addEventListener('resize', updateScreenSize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', updateScreenSize);
});
</script>

<template>
    <AppShell variant="sidebar">
        <AppSidebar
            :open="sidebarOpen"
            @close="closeSidebar"
        />

        <AppContent variant="sidebar">
            <AppSidebarHeader
                :breadcrumbs="breadcrumbs"
                @toggle-sidebar="toggleSidebar"
            />

            <slot />
        </AppContent>
    </AppShell>
</template>
