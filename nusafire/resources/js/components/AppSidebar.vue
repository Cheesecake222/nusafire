
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { Link, router, usePage } from '@inertiajs/vue3';

const props = withDefaults(
    defineProps<{
        mobileOpen?: boolean;
        collapsed?: boolean;
    }>(),
    {
        mobileOpen: false,
        collapsed: false,
    },
);

const emit = defineEmits<{
    (event: 'close'): void;
    (event: 'update:collapsed', value: boolean): void;
}>();

const page = usePage();
const isLoggingOut = computed(() => page.url === '/logout');
const isMobile = ref(false);

// Satu computed — desktop pakai collapsed, mobile pakai mobileOpen
const sidebarOpen = computed(() => {
    if (isMobile.value) return props.mobileOpen;
    return !props.collapsed;
});

const navigation = [
    { label: 'Overview', href: '/dashboard', icon: '◫' },
    { label: 'Hotspot Map', href: '/hotspot-map', icon: '◎' },
    { label: 'Weather Analysis', href: '/weather-analysis', icon: '☁' },
    { label: 'Burned Area', href: '/burned-area', icon: '▧' },
];

function updateScreenSize() {
    if (typeof window !== 'undefined') {
        isMobile.value = window.innerWidth <= 900;
    }
}

function isActive(href: string) {
    const currentPath = page.url.split('?')[0];
    if (href === '/dashboard') return currentPath === '/dashboard';
    return currentPath === href || currentPath.startsWith(`${href}/`);
}

function closeSidebar() {
    if (isMobile.value) {
        emit('close');
    } else {
        emit('update:collapsed', true);
    }
}

function handleNavClick() {
    if (isMobile.value) emit('close');
}

function logout() {
    if (isLoggingOut.value) return;
    router.post('/logout', {}, {
        onFinish: () => { if (isMobile.value) emit('close'); },
    });
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
    <div class="nf-sidebar-root">
        <!-- Overlay mobile -->
        <Transition name="nf-overlay">
            <button
                v-if="isMobile && sidebarOpen"
                type="button"
                class="nf-sidebar-overlay"
                aria-label="Tutup sidebar"
                @click="closeSidebar"
            />
        </Transition>

        <aside
            class="nf-sidebar"
            :class="{ 'nf-sidebar-open': sidebarOpen }"
            :aria-hidden="!sidebarOpen"
        >
            <div class="nf-brand">
                <div class="nf-brand-mark">
                    <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
                        <path d="M20 4L7 22h9l-3 13 14-19h-9L20 4Z" fill="currentColor" />
                        <path d="M5 29c5-3 9-3 14 0s10 3 16-1" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".55" />
                    </svg>
                </div>

                <div class="nf-brand-copy">
                    <strong>NusaFire</strong>
                    <span>FOREST INTELLIGENCE</span>
                </div>

                <button
                    type="button"
                    class="nf-icon-button nf-mobile-close"
                    aria-label="Tutup sidebar"
                    title="Tutup sidebar"
                    @click="closeSidebar"
                >
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
                        <path d="m18 6-12 12M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div class="nf-sidebar-section">
                <span class="nf-section-label">WORKSPACE</span>

                <nav class="nf-navigation" aria-label="Main navigation">
                    <Link
                        v-for="item in navigation"
                        :key="item.href"
                        :href="item.href"
                        class="nf-nav-item"
                        :class="{ 'nf-nav-active': isActive(item.href) }"
                        :aria-current="isActive(item.href) ? 'page' : undefined"
                        :tabindex="sidebarOpen ? 0 : -1"
                        @click="handleNavClick"
                    >
                        <span class="nf-nav-icon" aria-hidden="true">{{ item.icon }}</span>
                        <span>{{ item.label }}</span>
                        <span v-if="isActive(item.href)" class="nf-nav-indicator" />
                    </Link>
                </nav>
            </div>

            <div class="nf-sidebar-note">
                <div class="nf-note-icon">✦</div>
                <strong>Forest Watch</strong>
                <p>Understanding fire activity through environmental data.</p>
                <span class="nf-note-status">
                    <span class="nf-status-dot" />
                    Intelligence workspace
                </span>
            </div>

            <div class="nf-sidebar-bottom">
                <div class="nf-user-card">
                    <div class="nf-avatar">NF</div>
                    <div class="nf-user-copy">
                        <strong>NusaFire User</strong>
                        <span>Workspace account</span>
                    </div>
                </div>

                <button type="button" class="nf-logout-button" :disabled="isLoggingOut" @click="logout">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                        <path d="M10 17l5-5-5-5M15 12H3" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6" stroke-linecap="round" />
                    </svg>
                    <span>{{ isLoggingOut ? 'Logging out...' : 'Logout' }}</span>
                </button>

                <div class="nf-sidebar-footer">
                    <span>NUSAFIRE © 2026</span>
                    <span>INDONESIA</span>
                </div>
            </div>
        </aside>
    </div>
</template>

<style>
.nf-sidebar-root,
.nf-sidebar-root * { box-sizing: border-box; }

.nf-sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 30;
    display: flex;
    flex-direction: column;
    width: 252px;
    height: 100vh;
    height: 100dvh;
    padding: 25px 17px 17px;
    overflow-x: hidden;
    overflow-y: auto;
    color: var(--db-text);
    background: var(--db-surface);
    border-right: 1px solid var(--db-border);
    transform: translateX(-100%);
    transition: background .25s ease, color .25s ease, transform .3s cubic-bezier(.4,0,.2,1);
}

.nf-sidebar.nf-sidebar-open {
    transform: translateX(0);
}

.nf-brand { display: flex; align-items: center; gap: 11px; min-height: 43px; padding: 0 8px; margin-bottom: 42px; }
.nf-brand-mark { display: grid; width: 39px; height: 39px; flex: 0 0 39px; place-items: center; color: #fff; background: #287a50; border-radius: 12px; }
.nf-brand-mark svg { width: 29px; height: 29px; }
.nf-brand-copy { display: flex; flex: 1; flex-direction: column; gap: 3px; min-width: 0; }
.nf-brand-copy strong { font-size: 19px; font-weight: 750; letter-spacing: -0.7px; }
.nf-brand-copy span { color: var(--db-muted); font-size: 8px; font-weight: 700; letter-spacing: 1.5px; white-space: nowrap; }

.nf-section-label { display: block; padding: 0 12px; margin-bottom: 12px; color: var(--db-muted); font-size: 9px; font-weight: 750; letter-spacing: 1.5px; }
.nf-navigation { display: grid; gap: 5px; }

.nf-nav-item {
    position: relative; display: flex; align-items: center; gap: 12px; width: 100%; min-height: 44px; padding: 0 12px;
    color: var(--db-text-soft); text-align: left; text-decoration: none; background: transparent; border-radius: 9px;
    transition: background .15s ease, color .15s ease;
}
.nf-nav-item:hover { color: var(--db-text); background: var(--db-surface-soft); }
.nf-nav-active, .nf-nav-active:hover { color: var(--db-accent); background: var(--db-accent-soft); font-weight: 650; }
.nf-nav-icon { display: inline-grid; width: 20px; flex: 0 0 20px; place-items: center; font-size: 19px; }
.nf-nav-indicator { position: absolute; top: 11px; right: 0; width: 3px; height: 22px; background: var(--db-accent); border-radius: 5px 0 0 5px; }

.nf-sidebar-note { padding: 17px 15px; margin: auto 0 22px; background: var(--db-surface-soft); border: 1px solid var(--db-border); border-radius: 12px; }
.nf-note-icon { display: grid; width: 29px; height: 29px; margin-bottom: 12px; place-items: center; color: var(--db-accent); background: var(--db-accent-soft); border-radius: 9px; font-size: 17px; }
.nf-sidebar-note > strong { display: block; margin-bottom: 6px; font-size: 12px; }
.nf-sidebar-note p { margin: 0; color: var(--db-text-soft); font-size: 11px; line-height: 1.7; }
.nf-note-status { display: flex; align-items: center; gap: 7px; margin-top: 13px; color: var(--db-muted); font-size: 9px; }
.nf-status-dot { display: inline-block; width: 7px; height: 7px; flex: 0 0 7px; background: #58b77b; border-radius: 50%; }

.nf-sidebar-bottom { display: grid; flex-shrink: 0; gap: 11px; }
.nf-user-card { display: flex; align-items: center; gap: 10px; padding: 12px 4px 14px; border-top: 1px solid var(--db-border); }
.nf-avatar { display: grid; width: 34px; height: 34px; flex: 0 0 34px; place-items: center; color: var(--db-accent); background: var(--db-accent-soft); border-radius: 10px; font-size: 11px; font-weight: 800; }
.nf-user-copy { display: grid; gap: 4px; min-width: 0; }
.nf-user-copy strong { font-size: 11px; }
.nf-user-copy span { color: var(--db-muted); font-size: 10px; }

.nf-logout-button {
    display: flex; align-items: center; gap: 11px; width: 100%; min-height: 42px; padding: 0 12px;
    color: #c05b55; text-align: left; background: transparent; border: 1px solid transparent; border-radius: 9px; cursor: pointer;
    transition: background .15s ease, border-color .15s ease;
}
.nf-logout-button:hover:not(:disabled) { background: #fff0ee; border-color: #f2d9d5; }
.nf-logout-button:disabled { cursor: wait; opacity: 0.65; }
.theme-dark .nf-logout-button:hover:not(:disabled) { background: #3b2523; border-color: #57322f; }
.nf-logout-button svg { width: 18px; height: 18px; flex: 0 0 18px; }
.nf-logout-button span { font-size: 12px; font-weight: 600; }

.nf-sidebar-footer { display: flex; justify-content: space-between; gap: 8px; padding: 12px 3px 0; color: var(--db-muted); border-top: 1px solid var(--db-border); font-size: 8px; font-weight: 700; letter-spacing: 0.7px; }

.nf-icon-button {
    display: grid; width: 36px; height: 36px; flex: 0 0 36px; place-items: center;
    color: var(--db-text-soft); background: var(--db-surface-soft); border: 1px solid var(--db-border); border-radius: 10px; cursor: pointer;
    transition: color .15s ease, background .15s ease;
}
.nf-icon-button:hover { color: var(--db-accent); background: var(--db-accent-soft); }
.nf-mobile-close { display: grid; margin-left: auto; }

.nf-sidebar-overlay { display: none; }

/* Overlay fade transition */
.nf-overlay-enter-active, .nf-overlay-leave-active { transition: opacity .25s ease; }
.nf-overlay-enter-from, .nf-overlay-leave-to { opacity: 0; }

@media (max-width: 900px) {
    .nf-sidebar { box-shadow: none; }
    .nf-sidebar.nf-sidebar-open { box-shadow: 15px 0 50px rgb(0 0 0 / 15%); }
    .nf-sidebar-overlay { position: fixed; inset: 0; z-index: 25; display: block; padding: 0; background: rgb(0 0 0 / 38%); border: 0; cursor: pointer; }
    .nf-sidebar-note { margin-top: 35px; }
}

@media (prefers-reduced-motion: reduce) {
    .nf-sidebar, .nf-sidebar * { transition: none !important; }
}
</style>
