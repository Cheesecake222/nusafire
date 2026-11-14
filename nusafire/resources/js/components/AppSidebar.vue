
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { Link, router, useForm, usePage } from '@inertiajs/vue3';

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

const authUser = computed(() => {
    return (page.props as any).auth?.user ?? null;
});

const currentUrl = computed(() => page.url.split('?')[0]);

const navigationItems = [
    {
        label: 'Overview',
        description: 'Ringkasan dashboard',
        href: '/dashboard',
        icon: 'overview',
    },
    {
        label: 'Hotspot Map',
        description: 'Peta titik panas',
        href: '/hotspot-map',
        icon: 'map',
    },
    {
        label: 'Weather Analysis',
        description: 'Analisis cuaca',
        href: '/weather-analysis',
        icon: 'weather',
    },
    {
        label: 'Burned Area',
        description: 'Area terbakar',
        href: '/burned-area',
        icon: 'area',
    },
];

const isActive = (href: string) => {
    return currentUrl.value === href ||
        currentUrl.value.startsWith(`${href}/`);
};

const userInitials = computed(() => {
    const name = authUser.value?.name?.trim() || 'Pengguna';

    return name
        .split(/\s+/)
        .slice(0, 2)
        .map((part: string) => part.charAt(0).toUpperCase())
        .join('');
});

const showAccountPopup = ref(false);
const isEditingAccount = ref(false);
const isLoggingOut = ref(false);

const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('success');

let toastTimer: ReturnType<typeof setTimeout> | undefined;

const accountForm = useForm({
    name: '',
    email: '',
    current_password: '',
    password: '',
    password_confirmation: '',
});

function resetPasswordFields() {
    accountForm.current_password = '';
    accountForm.password = '';
    accountForm.password_confirmation = '';
}

function notify(
    message: string,
    type: 'success' | 'error' = 'success',
) {
    if (toastTimer) {
        clearTimeout(toastTimer);
    }

    toastMessage.value = message;
    toastType.value = type;
    showToast.value = true;

    toastTimer = setTimeout(() => {
        showToast.value = false;
    }, 3500);
}

function openAccountPopup() {
    accountForm.clearErrors();

    accountForm.name = authUser.value?.name ?? '';
    accountForm.email = authUser.value?.email ?? '';
    resetPasswordFields();

    isEditingAccount.value = false;
    showAccountPopup.value = true;
}

function openEditAccount() {
    accountForm.clearErrors();

    accountForm.name = authUser.value?.name ?? '';
    accountForm.email = authUser.value?.email ?? '';
    resetPasswordFields();

    isEditingAccount.value = true;
}

function cancelEditAccount() {
    if (accountForm.processing) return;

    accountForm.clearErrors();
    accountForm.name = authUser.value?.name ?? '';
    accountForm.email = authUser.value?.email ?? '';
    resetPasswordFields();

    isEditingAccount.value = false;
}

function closeAccountPopup() {
    if (accountForm.processing) return;

    showAccountPopup.value = false;
    isEditingAccount.value = false;
    accountForm.clearErrors();
}

function saveAccount() {
    if (accountForm.processing) return;

    accountForm.patch('/settings/profile', {
        preserveScroll: true,

        onSuccess: () => {
            showAccountPopup.value = false;
            isEditingAccount.value = false;
            resetPasswordFields();
            accountForm.reset('current_password', 'password', 'password_confirmation');

            notify(
                'Perubahan akun berhasil disimpan.',
                'success',
            );
        },

        onError: (errors) => {
            const hasValidationErrors = Object.keys(errors).length > 0;

            notify(
                hasValidationErrors
                    ? 'Periksa kembali nama dan alamat email.'
                    : 'Perubahan akun gagal disimpan. Silakan coba lagi.',
                'error',
            );
        },
    });
}

function logout() {
    if (isLoggingOut.value) return;

    isLoggingOut.value = true;

    router.post('/logout', {}, {
        onFinish: () => {
            isLoggingOut.value = false;
            showAccountPopup.value = false;
            emit('close');
        },
    });
}

function handleEscape(event: KeyboardEvent) {
    if (event.key === 'Escape' && showAccountPopup.value) {
        closeAccountPopup();
    }
}

onMounted(() => {
    window.addEventListener('keydown', handleEscape);
});

onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleEscape);

    if (toastTimer) {
        clearTimeout(toastTimer);
    }
});
</script>

<template>
    <div>
        <!-- Overlay untuk sidebar mobile -->
        <Transition name="nf-sidebar-overlay">
            <button
                v-if="mobileOpen"
                type="button"
                class="nf-sidebar-backdrop"
                aria-label="Tutup navigasi"
                @click="emit('close')"
            />
        </Transition>

        <!-- Sidebar utama -->
        <aside
            class="nf-sidebar"
            :class="{
                'nf-sidebar-mobile-open': mobileOpen,
                'nf-sidebar-mobile-closed': !mobileOpen,
                'nf-sidebar-collapsed': collapsed,
            }"
        >
            <!-- Brand -->
            <div class="nf-sidebar-brand">
                <Link
                    href="/dashboard"
                    class="nf-brand-link"
                    aria-label="NusaFire Overview"
                >
                    <div class="nf-brand-mark">
                        <svg
                            viewBox="0 0 40 40"
                            fill="none"
                            aria-hidden="true"
                        >
                            <path
                                d="M21.5 4.5C23 11 17 13.5 17 19.5C17 22 18.5 24 21 25C20 21.5 23.5 18.5 25.5 16C30 21 32 24.5 32 29C32 35 26.5 38 20 38C12 38 7 33 7 26.5C7 20 11.5 15 15.5 11.5C15 17 16 19 17.5 20.5C17 13 20 9 21.5 4.5Z"
                                fill="currentColor"
                            />
                            <path
                                d="M20 30C22.5 27.5 24 25 24 22.5C28 26.5 28 29 26.5 31.5C25 34 21.5 34.5 19 33C17 31.5 17 29.5 18 28C18.5 29 19 29.5 20 30Z"
                                fill="#D6F2DF"
                            />
                        </svg>
                    </div>

                    <div class="nf-brand-copy">
                        <strong>NusaFire</strong>
                        <span>FOREST MONITORING</span>
                    </div>
                </Link>

                <button
                    type="button"
                    class="nf-sidebar-close"
                    aria-label="Tutup sidebar"
                    @click="emit('close')"
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <path
                            d="M15 18l-6-6 6-6"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                </button>
            </div>

            <!-- Navigation -->
            <div class="nf-sidebar-content">
                <div class="nf-nav-heading">
                    <span>NAVIGATION</span>
                </div>

                <nav class="nf-sidebar-nav" aria-label="Navigasi utama">
                    <Link
                        v-for="item in navigationItems"
                        :key="item.href"
                        :href="item.href"
                        class="nf-nav-link"
                        :class="{ 'nf-nav-link-active': isActive(item.href) }"
                        :title="collapsed ? item.label : undefined"
                        :aria-current="isActive(item.href) ? 'page' : undefined"
                        @click="emit('close')"
                    >
                        <span class="nf-nav-icon">
                            <svg
                                v-if="item.icon === 'overview'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.7"
                                aria-hidden="true"
                            >
                                <rect x="3.5" y="3.5" width="7" height="7" rx="1.5" />
                                <rect x="13.5" y="3.5" width="7" height="7" rx="1.5" />
                                <rect x="3.5" y="13.5" width="7" height="7" rx="1.5" />
                                <rect x="13.5" y="13.5" width="7" height="7" rx="1.5" />
                            </svg>

                            <svg
                                v-else-if="item.icon === 'map'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.7"
                                aria-hidden="true"
                            >
                                <path
                                    d="M9 18l-6 3V6l6-3m0 15l6 3m-6-3V3m6 18l6-3V3l-6 3m0 15V6m0 0L9 3"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                                <circle cx="15" cy="10" r="2" />
                            </svg>

                            <svg
                                v-else-if="item.icon === 'weather'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.7"
                                aria-hidden="true"
                            >
                                <circle cx="12" cy="12" r="4" />
                                <path
                                    d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3l1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3l1.42-1.42"
                                    stroke-linecap="round"
                                />
                            </svg>

                            <svg
                                v-else
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.7"
                                aria-hidden="true"
                            >
                                <path
                                    d="M4 20h16M6 20V9l6-5 6 5v11M9 20v-6h6v6"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                        </span>

                        <span class="nf-nav-copy">
                            <strong>{{ item.label }}</strong>
                            <small>{{ item.description }}</small>
                        </span>

                        <span
                            v-if="isActive(item.href)"
                            class="nf-nav-active-dot"
                        />
                    </Link>
                </nav>

                <!-- Informasi sistem -->
                <div class="nf-sidebar-note">
                    <div class="nf-note-icon">
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >
                            <path
                                d="M12 21s8-4 8-11V5l-8-3-8 3v5c0 7 8 11 8 11Z"
                                stroke-linejoin="round"
                            />
                            <path
                                d="m9 12 2 2 4-4"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                    </div>

                    <div class="nf-note-copy">
                        <strong>Forest Watch</strong>
                        <span>Monitoring kebakaran hutan</span>
                        <span class="nf-system-status">
                            <i />
                            System active
                        </span>
                    </div>
                </div>
            </div>

            <!-- Footer akun -->
            <div class="nf-sidebar-footer">
                <button
                    type="button"
                    class="nf-user-card"
                    :title="collapsed ? (authUser?.name ?? 'Akun') : undefined"
                    @click="openAccountPopup"
                >
                    <div class="nf-user-avatar">
                        {{ userInitials }}
                    </div>

                    <div class="nf-user-copy">
                        <strong>{{ authUser?.name ?? 'Pengguna' }}</strong>
                        <span>{{ authUser?.email ?? 'Email tidak tersedia' }}</span>
                    </div>

                    <svg
                        class="nf-user-settings-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <circle cx="12" cy="12" r="3" />
                        <path
                            d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.6a8 8 0 0 1-1.5.9l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.5-.9l-1.7.6-1.4-2.4 1.4-1.1a7 7 0 0 1 0-1.8l-1.4-1.1 1.4-2.4 1.7.6a8 8 0 0 1 1.5-.9l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.5.9l1.7-.6 1.4 2.4-1.4 1.1a7 7 0 0 1 0 1.7Z"
                            stroke-linejoin="round"
                        />
                    </svg>
                </button>

                <button
                    type="button"
                    class="nf-logout-button"
                    :disabled="isLoggingOut"
                    @click="logout"
                >
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <path
                            d="M10 17l5-5-5-5m5 5H3m9-9h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>

                    <span>
                        {{ isLoggingOut ? 'Keluar...' : 'Keluar dari akun' }}
                    </span>
                </button>

                <div class="nf-sidebar-copyright">
                    <span>NUSAFIRE</span>
                    <span>Environmental Monitoring Platform</span>
                </div>
            </div>
        </aside>

        <!-- Popup akun: tetap pada popup yang sama saat edit -->
        <Teleport to="body">
            <Transition name="nf-account-transition">
                <div
                    v-if="showAccountPopup"
                    class="nf-account-overlay"
                    @click.self="closeAccountPopup"
                >
                    <section
                        class="nf-account-modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="nf-account-title"
                    >
                        <header class="nf-account-header">
                            <div>
                                <span class="nf-account-eyebrow">
                                    NUSAFIRE ACCOUNT
                                </span>

                                <h2 id="nf-account-title">
                                    {{
                                        isEditingAccount
                                            ? 'Edit akun'
                                            : 'Informasi akun'
                                    }}
                                </h2>

                                <p>
                                    {{
                                        isEditingAccount
                                            ? 'Perbarui informasi akun kamu melalui formulir berikut.'
                                            : 'Kelola informasi akun yang kamu gunakan untuk mengakses NusaFire.'
                                    }}
                                </p>
                            </div>

                            <button
                                type="button"
                                class="nf-account-close"
                                aria-label="Tutup popup"
                                :disabled="accountForm.processing"
                                @click="closeAccountPopup"
                            >
                                &times;
                            </button>
                        </header>

                        <div class="nf-account-identity">
                            <div class="nf-account-avatar">
                                {{ userInitials }}
                            </div>

                            <div class="nf-account-identity-copy">
                                <strong>
                                    {{
                                        isEditingAccount
                                            ? accountForm.name || 'Nama pengguna'
                                            : authUser?.name ?? 'Pengguna'
                                    }}
                                </strong>

                                <span>
                                    {{
                                        isEditingAccount
                                            ? accountForm.email
                                            : authUser?.email ?? '-'
                                    }}
                                </span>

                                <span class="nf-account-status">
                                    <i />
                                    Akun aktif
                                </span>
                            </div>
                        </div>

                        <!-- Mode edit -->
                        <form
                            v-if="isEditingAccount"
                            class="nf-account-form"
                            @submit.prevent="saveAccount"
                        >
                            <div class="nf-account-field">
                                <label for="nf-account-name">
                                    Nama lengkap
                                </label>

                                <input
                                    id="nf-account-name"
                                    v-model="accountForm.name"
                                    type="text"
                                    name="name"
                                    autocomplete="name"
                                    placeholder="Masukkan nama lengkap"
                                    maxlength="255"
                                    required
                                    :disabled="accountForm.processing"
                                />

                                <span
                                    v-if="accountForm.errors.name"
                                    class="nf-account-error"
                                >
                                    {{ accountForm.errors.name }}
                                </span>
                            </div>

                            <div class="nf-account-field">
                                <label for="nf-account-email">
                                    Alamat email
                                </label>

                                <input
                                    id="nf-account-email"
                                    v-model="accountForm.email"
                                    type="email"
                                    name="email"
                                    autocomplete="email"
                                    placeholder="nama@email.com"
                                    maxlength="255"
                                    required
                                    :disabled="accountForm.processing"
                                />

                                <span
                                    v-if="accountForm.errors.email"
                                    class="nf-account-error"
                                >
                                    {{ accountForm.errors.email }}
                                </span>
                            </div>

                            <div class="nf-account-password-section">
                                <div class="nf-account-password-heading">
                                    <strong>Ganti password</strong>
                                    <span>Kosongkan bagian ini jika tidak ingin mengganti password.</span>
                                </div>

                                <div class="nf-account-field">
                                    <label for="nf-account-current-password">Password saat ini</label>
                                    <input
                                        id="nf-account-current-password"
                                        v-model="accountForm.current_password"
                                        type="password"
                                        name="current_password"
                                        autocomplete="current-password"
                                        placeholder="Masukkan password saat ini"
                                        :disabled="accountForm.processing"
                                    />
                                    <span v-if="accountForm.errors.current_password" class="nf-account-error">
                                        {{ accountForm.errors.current_password }}
                                    </span>
                                </div>

                                <div class="nf-account-field">
                                    <label for="nf-account-new-password">Password baru</label>
                                    <input
                                        id="nf-account-new-password"
                                        v-model="accountForm.password"
                                        type="password"
                                        name="password"
                                        autocomplete="new-password"
                                        placeholder="Minimal 8 karakter"
                                        :disabled="accountForm.processing"
                                    />
                                    <span v-if="accountForm.errors.password" class="nf-account-error">
                                        {{ accountForm.errors.password }}
                                    </span>
                                </div>

                                <div class="nf-account-field">
                                    <label for="nf-account-password-confirmation">Konfirmasi password baru</label>
                                    <input
                                        id="nf-account-password-confirmation"
                                        v-model="accountForm.password_confirmation"
                                        type="password"
                                        name="password_confirmation"
                                        autocomplete="new-password"
                                        placeholder="Ulangi password baru"
                                        :disabled="accountForm.processing"
                                    />
                                </div>
                            </div>

                            <div class="nf-account-edit-note">
                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="1.7"
                                    aria-hidden="true"
                                >
                                    <circle cx="12" cy="12" r="9" />
                                    <path
                                        d="M12 11v5m0-8h.01"
                                        stroke-linecap="round"
                                    />
                                </svg>

                                <span>
                                    Perubahan akan disimpan ke akun kamu setelah
                                    proses penyimpanan berhasil.
                                </span>
                            </div>

                            <footer class="nf-account-actions">
                                <button
                                    type="button"
                                    class="nf-account-button nf-account-button-secondary"
                                    :disabled="accountForm.processing"
                                    @click="cancelEditAccount"
                                >
                                    Batal
                                </button>

                                <button
                                    type="submit"
                                    class="nf-account-button nf-account-button-primary"
                                    :disabled="accountForm.processing"
                                >
                                    <svg
                                        v-if="accountForm.processing"
                                        class="nf-button-spinner"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        aria-hidden="true"
                                    >
                                        <circle
                                            cx="12"
                                            cy="12"
                                            r="9"
                                            stroke="currentColor"
                                            stroke-width="3"
                                            opacity=".25"
                                        />
                                        <path
                                            d="M21 12a9 9 0 0 0-9-9"
                                            stroke="currentColor"
                                            stroke-width="3"
                                            stroke-linecap="round"
                                        />
                                    </svg>

                                    {{
                                        accountForm.processing
                                            ? 'Menyimpan...'
                                            : 'Simpan perubahan'
                                    }}
                                </button>
                            </footer>
                        </form>

                        <!-- Mode informasi akun -->
                        <div v-else class="nf-account-details">
                            <div class="nf-account-detail">
                                <span>Nama lengkap</span>
                                <strong>
                                    {{ authUser?.name ?? '-' }}
                                </strong>
                            </div>

                            <div class="nf-account-detail">
                                <span>Alamat email</span>
                                <strong>
                                    {{ authUser?.email ?? '-' }}
                                </strong>
                            </div>

                            <footer class="nf-account-actions">
                                <button
                                    type="button"
                                    class="nf-account-button nf-account-button-secondary"
                                    @click="closeAccountPopup"
                                >
                                    Tutup
                                </button>

                                <button
                                    type="button"
                                    class="nf-account-button nf-account-button-primary"
                                    @click="openEditAccount"
                                >
                                    <svg
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="1.8"
                                        aria-hidden="true"
                                    >
                                        <path
                                            d="m15 5 4 4M4 20l4-.8L19 8a2.8 2.8 0 0 0-4-4L4 15l0 5Z"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                        />
                                    </svg>

                                    Edit akun
                                </button>
                            </footer>
                        </div>
                    </section>
                </div>
            </Transition>

            <!-- Notifikasi sementara -->
            <Transition name="nf-toast-transition">
                <div
                    v-if="showToast"
                    class="nf-account-toast"
                    :class="`nf-account-toast-${toastType}`"
                    role="status"
                    aria-live="polite"
                >
                    <span class="nf-toast-icon">
                        <svg
                            v-if="toastType === 'success'"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2.2"
                            aria-hidden="true"
                        >
                            <path
                                d="m5 12 4 4L19 6"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>

                        <span v-else>!</span>
                    </span>

                    <span class="nf-toast-message">
                        <strong>
                            {{
                                toastType === 'success'
                                    ? 'Berhasil'
                                    : 'Belum berhasil'
                            }}
                        </strong>

                        <small>{{ toastMessage }}</small>
                    </span>

                    <button
                        type="button"
                        aria-label="Tutup notifikasi"
                        @click="showToast = false"
                    >
                        &times;
                    </button>
                </div>
            </Transition>
        </Teleport>
    </div>
</template>

<style>
/* ========================================
   NUSAFIRE SIDEBAR
======================================== */

.nf-sidebar {
    --nf-green: #218653;
    --nf-green-dark: #176b43;
    --nf-green-light: #eaf5ed;
    --nf-sidebar-text: var(--db-text, #25372c);
    --nf-sidebar-muted: var(--db-muted, #829087);
    --nf-sidebar-border: var(--db-border, #e6ece7);
    --nf-sidebar-surface: var(--db-surface, #ffffff);

    position: fixed;
    inset: 0 auto 0 0;
    z-index: 80;
    display: flex;
    width: 268px;
    height: 100dvh;
    flex-direction: column;
    overflow: hidden;
    color: var(--nf-sidebar-text);
    background: var(--nf-sidebar-surface);
    border-right: 1px solid var(--nf-sidebar-border);
    box-shadow: 3px 0 20px rgb(20 50 30 / 3%);
    transition:
        width .25s ease,
        transform .25s ease;
}

.nf-sidebar-brand {
    display: flex;
    min-height: 86px;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 18px 20px;
    border-bottom: 1px solid var(--nf-sidebar-border);
}

.nf-brand-link {
    display: flex;
    min-width: 0;
    align-items: center;
    gap: 11px;
    color: inherit;
    text-decoration: none;
}

.nf-brand-mark {
    display: grid;
    width: 43px;
    height: 43px;
    flex: 0 0 43px;
    place-items: center;
    color: #ffffff;
    background: linear-gradient(145deg, #35a86b, #176b43);
    border-radius: 13px;
    box-shadow: 0 5px 12px rgb(33 134 83 / 18%);
}

.nf-brand-mark svg {
    width: 27px;
    height: 27px;
}

.nf-brand-copy {
    display: grid;
    gap: 4px;
    min-width: 0;
}

.nf-brand-copy strong {
    color: var(--nf-sidebar-text);
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -.6px;
}

.nf-brand-copy span {
    color: var(--nf-sidebar-muted);
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1.3px;
    white-space: nowrap;
}

.nf-sidebar-close {
    display: grid;
    width: 31px;
    height: 31px;
    flex: 0 0 31px;
    place-items: center;
    color: var(--nf-sidebar-muted);
    background: transparent;
    border: 1px solid var(--nf-sidebar-border);
    border-radius: 9px;
    cursor: pointer;
    transition: background .2s, color .2s;
}

.nf-sidebar-close:hover {
    color: var(--nf-green);
    background: var(--nf-green-light);
}

.nf-sidebar-close svg {
    width: 19px;
    height: 19px;
}

.nf-sidebar-content {
    flex: 1;
    padding: 25px 14px 18px;
    overflow-x: hidden;
    overflow-y: auto;
}

.nf-nav-heading {
    padding: 0 11px;
    margin-bottom: 12px;
}

.nf-nav-heading span {
    color: var(--nf-sidebar-muted);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.5px;
}

.nf-sidebar-nav {
    display: grid;
    gap: 6px;
}

.nf-nav-link {
    position: relative;
    display: flex;
    min-height: 59px;
    align-items: center;
    gap: 12px;
    padding: 10px 11px;
    color: var(--nf-sidebar-muted);
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    text-decoration: none;
    transition:
        color .2s,
        background .2s,
        border-color .2s;
}

.nf-nav-link:hover {
    color: var(--nf-green-dark);
    background: #f5f9f6;
}

.nf-nav-link-active {
    color: var(--nf-green-dark);
    background: var(--nf-green-light);
    border-color: #d9ebdf;
}

.nf-nav-icon {
    display: grid;
    width: 37px;
    height: 37px;
    flex: 0 0 37px;
    place-items: center;
    background: rgb(125 145 130 / 8%);
    border-radius: 10px;
}

.nf-nav-link-active .nf-nav-icon {
    color: #ffffff;
    background: var(--nf-green);
    box-shadow: 0 4px 9px rgb(33 134 83 / 16%);
}

.nf-nav-icon svg {
    width: 19px;
    height: 19px;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.nf-nav-copy {
    display: grid;
    flex: 1;
    gap: 4px;
    min-width: 0;
}

.nf-nav-copy strong {
    color: inherit;
    font-size: 12px;
    font-weight: 700;
}

.nf-nav-copy small {
    color: var(--nf-sidebar-muted);
    font-size: 10px;
    line-height: 1.35;
}

.nf-nav-active-dot {
    width: 6px;
    height: 6px;
    flex: 0 0 6px;
    background: var(--nf-green);
    border-radius: 50%;
}

.nf-sidebar-note {
    display: flex;
    gap: 11px;
    margin: 30px 1px 0;
    padding: 14px 12px;
    background: #f4f8f5;
    border: 1px solid #e5eee7;
    border-radius: 13px;
}

.nf-note-icon {
    display: grid;
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    place-items: center;
    color: #ffffff;
    background: #34865a;
    border-radius: 10px;
}

.nf-note-icon svg {
    width: 19px;
    height: 19px;
}

.nf-note-copy {
    display: grid;
    gap: 5px;
    min-width: 0;
}

.nf-note-copy strong {
    color: #2a4935;
    font-size: 11px;
    font-weight: 800;
}

.nf-note-copy > span {
    color: #7a8b7f;
    font-size: 9px;
    line-height: 1.5;
}

.nf-note-copy .nf-system-status {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #378452;
    font-size: 9px;
    font-weight: 700;
}

.nf-system-status i {
    width: 6px;
    height: 6px;
    background: #39b66e;
    border-radius: 50%;
}

.nf-sidebar-footer {
    padding: 13px 15px 17px;
    background: var(--nf-sidebar-surface);
    border-top: 1px solid var(--nf-sidebar-border);
}

.nf-user-card {
    display: flex;
    width: 100%;
    min-width: 0;
    align-items: center;
    gap: 10px;
    padding: 10px 3px 13px;
    color: var(--nf-sidebar-text);
    text-align: left;
    background: transparent;
    border: 0;
    border-bottom: 1px solid var(--nf-sidebar-border);
    cursor: pointer;
}

.nf-user-avatar {
    display: grid;
    width: 39px;
    height: 39px;
    flex: 0 0 39px;
    place-items: center;
    color: #ffffff;
    background: linear-gradient(145deg, #45ad75, #23754a);
    border: 2px solid #e3f2e8;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 800;
}

.nf-user-copy {
    display: grid;
    flex: 1;
    gap: 4px;
    min-width: 0;
}

.nf-user-copy strong,
.nf-user-copy span {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.nf-user-copy strong {
    color: var(--nf-sidebar-text);
    font-size: 11px;
    font-weight: 750;
}

.nf-user-copy span {
    color: var(--nf-sidebar-muted);
    font-size: 9px;
}

.nf-user-settings-icon {
    width: 17px;
    height: 17px;
    flex: 0 0 17px;
    color: var(--nf-sidebar-muted);
}

.nf-user-card:hover .nf-user-settings-icon {
    color: var(--nf-green);
}

.nf-logout-button {
    display: flex;
    width: 100%;
    min-height: 39px;
    align-items: center;
    gap: 10px;
    margin-top: 9px;
    padding: 9px 10px;
    color: #a34a4a;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    text-align: left;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    transition: background .2s;
}

.nf-logout-button:hover:not(:disabled) {
    background: #fff0ef;
    border-color: #f5d9d7;
}

.nf-logout-button:disabled {
    opacity: .6;
    cursor: wait;
}

.nf-logout-button svg {
    width: 17px;
    height: 17px;
    flex: 0 0 17px;
}

.nf-sidebar-copyright {
    display: grid;
    gap: 4px;
    margin-top: 13px;
    padding: 10px 3px 0;
}

.nf-sidebar-copyright span:first-child {
    color: var(--nf-sidebar-muted);
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1.3px;
}

.nf-sidebar-copyright span:last-child {
    color: var(--nf-sidebar-muted);
    font-size: 8px;
}

/* Mode sidebar ringkas */
.nf-sidebar-collapsed {
    width: 82px;
}

.nf-sidebar-collapsed .nf-sidebar-brand {
    justify-content: center;
    padding: 15px 8px;
}

.nf-sidebar-collapsed .nf-brand-link {
    justify-content: center;
}

.nf-sidebar-collapsed .nf-brand-copy,
.nf-sidebar-collapsed .nf-sidebar-close,
.nf-sidebar-collapsed .nf-nav-heading,
.nf-sidebar-collapsed .nf-nav-copy,
.nf-sidebar-collapsed .nf-nav-active-dot,
.nf-sidebar-collapsed .nf-note-copy,
.nf-sidebar-collapsed .nf-user-copy,
.nf-sidebar-collapsed .nf-user-settings-icon,
.nf-sidebar-collapsed .nf-logout-button span,
.nf-sidebar-collapsed .nf-sidebar-copyright {
    display: none;
}

.nf-sidebar-collapsed .nf-sidebar-content {
    padding: 23px 10px;
}

.nf-sidebar-collapsed .nf-nav-link {
    justify-content: center;
    padding: 8px;
}

.nf-sidebar-collapsed .nf-nav-icon {
    width: 42px;
    height: 42px;
    flex-basis: 42px;
}

.nf-sidebar-collapsed .nf-sidebar-note {
    justify-content: center;
    padding: 10px 5px;
}

.nf-sidebar-collapsed .nf-user-card {
    justify-content: center;
    padding: 10px 0 13px;
}

.nf-sidebar-collapsed .nf-logout-button {
    justify-content: center;
    padding: 10px 0;
}

/* ========================================
   ACCOUNT POPUP - SOLID BACKGROUND
======================================== */

.nf-account-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: grid;
    place-items: center;
    padding: 20px;
    overflow-y: auto;
    background: rgb(15 29 21 / 62%);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
}

.nf-account-modal {
    width: min(100%, 490px);
    max-height: min(90vh, 760px);
    overflow-y: auto;
    padding: 28px;
    color: #203127;
    background: #ffffff;
    border: 1px solid #e0e9e2;
    border-radius: 22px;
    box-shadow: 0 24px 80px rgb(5 25 13 / 28%);
}

.nf-account-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
}

.nf-account-eyebrow {
    display: block;
    margin-bottom: 9px;
    color: #278653;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1.7px;
}

.nf-account-header h2 {
    margin: 0;
    color: #1d3024;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -.7px;
}

.nf-account-header p {
    margin: 9px 0 0;
    color: #718077;
    font-size: 12px;
    line-height: 1.7;
}

.nf-account-close {
    display: grid;
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    place-items: center;
    color: #617167;
    background: #f1f5f2;
    border: 1px solid #e4ebe5;
    border-radius: 11px;
    font-size: 25px;
    line-height: 1;
    cursor: pointer;
    transition: color .2s, background .2s;
}

.nf-account-close:hover:not(:disabled) {
    color: #176b43;
    background: #e5f3e9;
}

.nf-account-close:disabled {
    opacity: .5;
    cursor: wait;
}

.nf-account-identity {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 24px 0;
    padding: 17px;
    background: #f1f7f3;
    border: 1px solid #e0ece3;
    border-radius: 15px;
}

.nf-account-avatar {
    display: grid;
    width: 50px;
    height: 50px;
    flex: 0 0 50px;
    place-items: center;
    color: #ffffff;
    background: linear-gradient(140deg, #38a76c, #176b43);
    border: 3px solid #e0f0e5;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgb(33 134 83 / 15%);
    font-size: 15px;
    font-weight: 850;
}

.nf-account-identity-copy {
    display: grid;
    gap: 5px;
    min-width: 0;
}

.nf-account-identity-copy strong {
    overflow-wrap: anywhere;
    color: #24392b;
    font-size: 13px;
    font-weight: 800;
}

.nf-account-identity-copy > span {
    overflow-wrap: anywhere;
    color: #748178;
    font-size: 11px;
}

.nf-account-status {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 2px;
    color: #328453 !important;
    font-size: 10px !important;
    font-weight: 700;
}

.nf-account-status i {
    width: 7px;
    height: 7px;
    background: #35b875;
    border-radius: 50%;
    box-shadow: 0 0 0 3px #d9f3e3;
}

.nf-account-details,
.nf-account-form {
    display: grid;
    gap: 17px;
}

.nf-account-detail {
    display: grid;
    gap: 8px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e9efeb;
}

.nf-account-detail > span {
    color: #77847b;
    font-size: 11px;
    font-weight: 600;
}

.nf-account-detail strong {
    overflow-wrap: anywhere;
    color: #26372c;
    font-size: 13px;
    font-weight: 750;
}

.nf-account-field {
    display: grid;
    gap: 8px;
}

.nf-account-field label {
    color: #526258;
    font-size: 11px;
    font-weight: 750;
}

.nf-account-field input {
    box-sizing: border-box;
    width: 100%;
    min-height: 45px;
    padding: 11px 13px;
    color: #26382c;
    background: #ffffff;
    border: 1px solid #dce6df;
    border-radius: 10px;
    outline: none;
    font-family: inherit;
    font-size: 12px;
    transition: border-color .2s, box-shadow .2s;
}

.nf-account-field input::placeholder {
    color: #a1aca4;
}

.nf-account-field input:focus {
    border-color: #31915d;
    box-shadow: 0 0 0 3px rgb(49 145 93 / 12%);
}

.nf-account-field input:disabled {
    background: #f5f7f5;
    cursor: wait;
}

.nf-account-error {
    color: #c93c3c;
    font-size: 10px;
    line-height: 1.5;
}

.nf-account-password-section {
    display: grid;
    gap: 15px;
    padding: 16px;
    background: #fbfdfb;
    border: 1px solid #e1ebe4;
    border-radius: 13px;
}

.nf-account-password-heading {
    display: grid;
    gap: 5px;
}

.nf-account-password-heading strong {
    color: #263b2d;
    font-size: 12px;
    font-weight: 800;
}

.nf-account-password-heading span {
    color: #78867c;
    font-size: 10px;
    line-height: 1.5;
}

.nf-account-edit-note {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 11px 12px;
    color: #64766a;
    background: #f5f8f5;
    border: 1px solid #e8eee9;
    border-radius: 10px;
    font-size: 10px;
    line-height: 1.6;
}

.nf-account-edit-note svg {
    width: 16px;
    height: 16px;
    flex: 0 0 16px;
    margin-top: 1px;
    color: #368459;
}

.nf-account-actions {
    display: flex;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 7px;
}

.nf-account-button {
    display: inline-flex;
    min-height: 42px;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 16px;
    border: 1px solid transparent;
    border-radius: 10px;
    font-family: inherit;
    font-size: 11px;
    font-weight: 750;
    cursor: pointer;
    transition:
        transform .2s,
        background .2s,
        box-shadow .2s,
        opacity .2s;
}

.nf-account-button:hover:not(:disabled) {
    transform: translateY(-1px);
}

.nf-account-button:disabled {
    opacity: .65;
    cursor: wait;
}

.nf-account-button svg {
    width: 16px;
    height: 16px;
    flex: 0 0 16px;
}

.nf-account-button-primary {
    color: #ffffff;
    background: #238653;
    border-color: #238653;
    box-shadow: 0 4px 11px rgb(35 134 83 / 16%);
}

.nf-account-button-primary:hover:not(:disabled) {
    background: #196e43;
    border-color: #196e43;
    box-shadow: 0 6px 14px rgb(35 134 83 / 22%);
}

.nf-account-button-secondary {
    color: #506157;
    background: #ffffff;
    border-color: #dce6df;
}

.nf-account-button-secondary:hover:not(:disabled) {
    background: #f2f6f3;
}

.nf-button-spinner {
    animation: nf-spinner-rotate .8s linear infinite;
}

@keyframes nf-spinner-rotate {
    to {
        transform: rotate(360deg);
    }
}

/* ========================================
   TOAST NOTIFICATION
======================================== */

.nf-account-toast {
    position: fixed;
    top: 22px;
    right: 22px;
    z-index: 1100;
    display: flex;
    width: max-content;
    max-width: min(420px, calc(100vw - 32px));
    align-items: center;
    gap: 11px;
    padding: 14px 15px;
    color: #245338;
    background: #ffffff;
    border: 1px solid #d9e9de;
    border-radius: 13px;
    box-shadow: 0 12px 35px rgb(20 50 30 / 18%);
}

.nf-toast-icon {
    display: grid;
    width: 31px;
    height: 31px;
    flex: 0 0 31px;
    place-items: center;
    color: #ffffff;
    background: #29945c;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 800;
}

.nf-toast-icon svg {
    width: 17px;
    height: 17px;
}

.nf-toast-message {
    display: grid;
    flex: 1;
    gap: 4px;
    min-width: 0;
}

.nf-toast-message strong {
    color: #28563a;
    font-size: 12px;
    font-weight: 800;
}

.nf-toast-message small {
    color: #718077;
    font-size: 10px;
    line-height: 1.5;
}

.nf-account-toast > button {
    align-self: flex-start;
    padding: 0 2px;
    color: #819087;
    background: transparent;
    border: 0;
    font-size: 21px;
    line-height: 1;
    cursor: pointer;
}

.nf-account-toast > button:hover {
    color: #31483a;
}

.nf-account-toast-error {
    color: #9e3636;
    background: #ffffff;
    border-color: #f0d7d7;
}

.nf-account-toast-error .nf-toast-icon {
    background: #cf4848;
}

.nf-account-toast-error .nf-toast-message strong {
    color: #a23535;
}

/* ========================================
   ANIMATIONS
======================================== */

.nf-account-transition-enter-active,
.nf-account-transition-leave-active {
    transition: opacity .2s ease;
}

.nf-account-transition-enter-active .nf-account-modal,
.nf-account-transition-leave-active .nf-account-modal {
    transition: transform .2s ease;
}

.nf-account-transition-enter-from,
.nf-account-transition-leave-to {
    opacity: 0;
}

.nf-account-transition-enter-from .nf-account-modal,
.nf-account-transition-leave-to .nf-account-modal {
    transform: translateY(12px) scale(.98);
}

.nf-toast-transition-enter-active,
.nf-toast-transition-leave-active {
    transition: opacity .2s ease, transform .2s ease;
}

.nf-toast-transition-enter-from,
.nf-toast-transition-leave-to {
    opacity: 0;
    transform: translateY(-8px);
}

.nf-sidebar-overlay-enter-active,
.nf-sidebar-overlay-leave-active {
    transition: opacity .2s ease;
}

.nf-sidebar-overlay-enter-from,
.nf-sidebar-overlay-leave-to {
    opacity: 0;
}

/* ========================================
   RESPONSIVE
======================================== */

.nf-sidebar-backdrop {
    display: none;
}

@media (max-width: 900px) {
    .nf-sidebar {
        width: 268px;
        transform: translateX(-105%);
        box-shadow: 10px 0 35px rgb(10 30 17 / 15%);
    }

    .nf-sidebar-mobile-open {
        transform: translateX(0);
    }

    .nf-sidebar-mobile-closed {
        transform: translateX(-105%);
    }

    .nf-sidebar-collapsed {
        width: 268px;
    }

    .nf-sidebar-collapsed .nf-brand-copy,
    .nf-sidebar-collapsed .nf-sidebar-close,
    .nf-sidebar-collapsed .nf-nav-heading,
    .nf-sidebar-collapsed .nf-nav-copy,
    .nf-sidebar-collapsed .nf-nav-active-dot,
    .nf-sidebar-collapsed .nf-note-copy,
    .nf-sidebar-collapsed .nf-user-copy,
    .nf-sidebar-collapsed .nf-user-settings-icon,
    .nf-sidebar-collapsed .nf-logout-button span,
    .nf-sidebar-collapsed .nf-sidebar-copyright {
        display: revert;
    }

    .nf-sidebar-collapsed .nf-sidebar-brand {
        justify-content: space-between;
        padding: 18px 20px;
    }

    .nf-sidebar-collapsed .nf-nav-link {
        justify-content: flex-start;
        padding: 10px 11px;
    }

    .nf-sidebar-collapsed .nf-sidebar-note {
        justify-content: flex-start;
        padding: 14px 12px;
    }

    .nf-sidebar-collapsed .nf-user-card {
        justify-content: flex-start;
        padding: 10px 3px 13px;
    }

    .nf-sidebar-collapsed .nf-logout-button {
        justify-content: flex-start;
        padding: 9px 10px;
    }

    .nf-sidebar-backdrop {
        position: fixed;
        inset: 0;
        z-index: 79;
        display: block;
        background: rgb(12 25 16 / 50%);
        border: 0;
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
    }
}

@media (min-width: 901px) {
    .nf-sidebar {
        transform: translateX(0);
    }

    .nf-sidebar-backdrop {
        display: none;
    }
}

@media (max-width: 520px) {
    .nf-account-overlay {
        padding: 12px;
    }

    .nf-account-modal {
        padding: 21px;
        border-radius: 17px;
    }

    .nf-account-header h2 {
        font-size: 22px;
    }

    .nf-account-actions {
        flex-direction: column-reverse;
    }

    .nf-account-button {
        width: 100%;
    }

    .nf-account-toast {
        top: 12px;
        right: 12px;
        left: 12px;
        width: auto;
        max-width: none;
    }
}
</style>