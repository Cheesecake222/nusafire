
import { ref } from 'vue';

export type Theme = 'dark' | 'light';

// Baca tema awal dari <html> yang sudah diset oleh inline script di <head>.
// Ini memastikan state Vue langsung sinkron dengan DOM sejak render pertama,
// sehingga tidak ada flash/perubahan tampilan saat halaman dimuat.
function getInitialTheme(): Theme {
    if (typeof document !== 'undefined') {
        if (document.documentElement.classList.contains('theme-light')) return 'light';
        if (document.documentElement.classList.contains('theme-dark')) return 'dark';
    }
    // Fallback: cek localStorage langsung
    if (typeof localStorage !== 'undefined') {
        const saved = localStorage.getItem('nusafire-theme');
        if (saved === 'light' || saved === 'dark') return saved;
    }
    return 'dark';
}

// Satu state yang dipakai bersama oleh seluruh halaman Vue.
const theme = ref<Theme>(getInitialTheme());

function applyTheme(value: Theme, save = true) {
    theme.value = value;

    if (typeof document !== 'undefined') {
        // Update class di <html> (dipakai oleh script head dan CSS global)
        document.documentElement.classList.remove('theme-dark', 'theme-light');
        document.documentElement.classList.add('theme-' + value);
        document.documentElement.dataset.theme = value;
        document.documentElement.style.colorScheme = value;
    }

    if (save && typeof localStorage !== 'undefined') {
        localStorage.setItem('nusafire-theme', value);
    }
}

function initializeTheme() {
    // State sudah diinisialisasi dari getInitialTheme() di atas.
    // Fungsi ini hanya memastikan atribut DOM sinkron (untuk pages yang
    // belum pernah render applyTheme).
    applyTheme(theme.value, false);
}

function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark');
}

function setTheme(value: Theme) {
    applyTheme(value);
}

export function useTheme() {
    return {
        theme,
        initializeTheme,
        toggleTheme,
        setTheme,
    };
}
