<script setup lang="ts">
import AppLogoIcon from '@/components/AppLogoIcon.vue';

interface Props {
    class?: string;
}

defineProps<Props>();
</script>

<template>
    <div class="flex aspect-square size-9 items-center justify-center rounded-lg bg-white p-1 shadow-sm border border-border overflow-hidden dark:bg-[#19231c]">
        <AppLogoIcon class="size-full object-contain" />
    </div>
    <div class="ml-2 grid flex-1 text-left text-sm leading-tight">
        <span class="mb-0.5 truncate font-bold tracking-tight">NusaFire</span>
        <span class="truncate text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Fire Early Warning</span>
    </div>
</template>
