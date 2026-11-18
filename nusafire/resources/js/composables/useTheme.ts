
import { ref } from 'vue';

export type Theme = 'dark' | 'light';

// Baca tema awal dari localStorage atau <html>. Default: 'light' (mode terang)
function getInitialTheme(): Theme {
    if (typeof localStorage !== 'undefined') {
        const saved = localStorage.getItem('nusafire-theme') || localStorage.getItem('appearance');
        if (saved === 'dark') return 'dark';
        if (saved === 'light') return 'light';
    }
    if (typeof document !== 'undefined') {
        if (document.documentElement.classList.contains('theme-dark') || document.documentElement.classList.contains('dark')) {
            return 'dark';
        }
    }
    return 'light';
}

// Satu state reaktif yang dipakai bersama oleh seluruh halaman Vue.
const theme = ref<Theme>(getInitialTheme());

function applyTheme(value: Theme, save = true) {
    theme.value = value;

    if (typeof document !== 'undefined') {
        document.documentElement.classList.remove('theme-dark', 'theme-light', 'dark');
        document.documentElement.classList.add('theme-' + value);
        if (value === 'dark') {
            document.documentElement.classList.add('dark');
        }
        document.documentElement.dataset.theme = value;
        document.documentElement.style.colorScheme = value;
    }

    if (save && typeof localStorage !== 'undefined') {
        localStorage.setItem('nusafire-theme', value);
        localStorage.setItem('appearance', value);
    }
}

export function initializeTheme() {
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
