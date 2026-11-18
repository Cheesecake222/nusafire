
<script setup lang="ts">
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import type { BreadcrumbItemType } from '@/types';

defineProps<{
    breadcrumbs?: BreadcrumbItemType[];
}>();

const emit = defineEmits<{
    (event: 'toggle-sidebar'): void;
}>();
</script>

<template>
    <header class="nf-layout-header">
        <div class="nf-header-inner">
            <button
                type="button"
                class="nf-header-toggle-btn"
                aria-label="Open navigation"
                @click="emit('toggle-sidebar')"
            >
                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    width="20"
                    height="20"
                    aria-hidden="true"
                >
                    <line x1="4" y1="6" x2="20" y2="6" />
                    <line x1="4" y1="12" x2="20" y2="12" />
                    <line x1="4" y1="18" x2="20" y2="18" />
                </svg>
            </button>

            <template v-if="breadcrumbs && breadcrumbs.length">
                <Breadcrumb>
                    <BreadcrumbList>
                        <template
                            v-for="(item, index) in breadcrumbs"
                            :key="index"
                        >
                            <BreadcrumbItem>
                                <template
                                    v-if="index === breadcrumbs.length - 1"
                                >
                                    <BreadcrumbPage>
                                        {{ item.title }}
                                    </BreadcrumbPage>
                                </template>

                                <template v-else>
                                    <BreadcrumbLink :href="item.href">
                                        {{ item.title }}
                                    </BreadcrumbLink>
                                </template>
                            </BreadcrumbItem>

                            <BreadcrumbSeparator
                                v-if="index !== breadcrumbs.length - 1"
                            />
                        </template>
                    </BreadcrumbList>
                </Breadcrumb>
            </template>
        </div>
    </header>
</template>

<style>
.nf-layout-header {
    display: flex;
    height: 68px;
    min-height: 68px;
    flex-shrink: 0;
    align-items: center;
    padding: 0 32px;
    background: var(--background, #ffffff);
    border-bottom: 1px solid var(--border, #e6ece7);
}

.nf-header-inner {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nf-header-toggle-btn {
    display: none;
    width: 38px;
    height: 38px;
    align-items: center;
    justify-content: center;
    color: inherit;
    background: transparent;
    border: 1px solid var(--border, #e6ece7);
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.nf-header-toggle-btn:hover {
    background: var(--sidebar-accent, #f0f4f1);
    color: var(--sidebar-accent-foreground, #1a3022);
}

@media (max-width: 900px) {
    .nf-layout-header {
        padding: 0 16px;
    }

    .nf-header-toggle-btn {
        display: inline-flex;
    }
}
</style>

