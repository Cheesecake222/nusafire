
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
    <header
        class="flex h-16 shrink-0 items-center gap-2 border-b border-sidebar-border/70 px-6 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 md:px-4"
    >
        <div class="flex items-center gap-2">
            <button
                type="button"
                class="-ml-1 inline-flex h-9 w-9 items-center justify-center rounded-md hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                aria-label="Buka atau tutup sidebar"
                @click="emit('toggle-sidebar')"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                >
                    <rect x="3" y="4" width="18" height="16" rx="2" />
                    <path d="M9 4v16" />
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
