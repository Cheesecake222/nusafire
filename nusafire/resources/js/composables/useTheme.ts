
import { ref } from 'vue';

export type Theme = 'dark' | 'light';

// Satu state yang dipakai bersama oleh seluruh halaman Vue.
const theme = ref<Theme>('dark');

function applyTheme(value: Theme, save = true) {
    theme.value = value;

    if (typeof document !== 'undefined') {
        document.documentElement.dataset.theme = value;
        document.documentElement.style.colorScheme = value;
    }

    if (save && typeof localStorage !== 'undefined') {
        localStorage.setItem('nusafire-theme', value);
    }
}

function initializeTheme() {
    if (typeof localStorage === 'undefined') {
        return;
    }

    const savedTheme = localStorage.getItem('nusafire-theme');

    if (savedTheme === 'light' || savedTheme === 'dark') {
        applyTheme(savedTheme, false);
    } else {
        applyTheme('dark', false);
    }
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
