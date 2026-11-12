
<script setup lang="ts">
import { ref } from 'vue';
import { Head, Link, useForm } from '@inertiajs/vue3';
import { useTheme } from '@/composables/useTheme';

defineProps<{
    status?: string;
    canResetPassword?: boolean;
    canRegister?: boolean;
}>();

const { theme, toggleTheme } = useTheme();

const showPassword = ref(false);

const form = useForm({
    email: '',
    password: '',
    remember: false,
});

function submit() {
    form.post('/login', {
        onFinish: () => {
            form.reset('password');
        },
    });
}


</script>

<template>
    <Head title="Login | NusaFire" />

    <main class="login-page" :class="`theme-${theme}`">
        <button
            type="button"
            class="theme-switch"
            :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
            :title="theme === 'dark' ? 'Light mode' : 'Dark mode'"
            @click="toggleTheme"
        >
            <span v-if="theme === 'dark'">☀</span>
            <span v-else>☾</span>
        </button>

        <section class="login-visual">
            <div class="visual-background">
                <div class="visual-glow visual-glow-one"></div>
                <div class="visual-glow visual-glow-two"></div>

                <svg
                    class="forest-art"
                    viewBox="0 0 720 900"
                    preserveAspectRatio="xMidYMid slice"
                    aria-hidden="true"
                >
                    <defs>
                        <linearGradient id="forest-sky" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#173e2d" />
                            <stop offset="100%" stop-color="#0c241b" />
                        </linearGradient>

                        <linearGradient id="forest-ground" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#204d36" />
                            <stop offset="100%" stop-color="#0b1b14" />
                        </linearGradient>

                        <linearGradient id="forest-light" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#9acba1" stop-opacity=".2" />
                            <stop offset="100%" stop-color="#9acba1" stop-opacity="0" />
                        </linearGradient>
                    </defs>

                    <rect width="720" height="900" fill="url(#forest-sky)" />

                    <circle
                        cx="505"
                        cy="205"
                        r="185"
                        fill="url(#forest-light)"
                    />

                    <g fill="#28563b" opacity=".8">
                        <path d="M0 380L75 190L150 380Z" />
                        <path d="M82 420L180 140L280 420Z" />
                        <path d="M430 390L530 110L630 390Z" />
                        <path d="M550 420L650 175L750 420Z" />
                    </g>

                    <g fill="#173e2b">
                        <path d="M-30 560L70 280L170 560Z" />
                        <path d="M75 580L190 235L305 580Z" />
                        <path d="M410 570L525 225L640 570Z" />
                        <path d="M530 570L645 265L760 570Z" />
                    </g>

                    <path
                        d="M0 545Q120 475 235 560T470 545T720 535V900H0Z"
                        fill="url(#forest-ground)"
                    />

                    <g fill="#102e20">
                        <path d="M-35 740L50 390L135 740Z" />
                        <path d="M50 790L160 370L270 790Z" />
                        <path d="M200 830L295 455L390 830Z" />
                        <path d="M390 790L495 370L600 790Z" />
                        <path d="M535 790L635 405L735 790Z" />
                    </g>

                    <g fill="#0b2117">
                        <path d="M-40 900L80 490L200 900Z" />
                        <path d="M100 900L230 435L360 900Z" />
                        <path d="M340 900L470 445L600 900Z" />
                        <path d="M510 900L640 490L770 900Z" />
                    </g>

                    <g
                        fill="none"
                        stroke="#82b98d"
                        stroke-width="1"
                        opacity=".14"
                    >
                        <path d="M0 610Q180 540 360 615T720 600" />
                        <path d="M0 680Q180 610 360 685T720 670" />
                        <path d="M0 750Q180 680 360 755T720 740" />
                    </g>
                </svg>

                <div class="visual-grain"></div>
            </div>

            <div class="visual-content">
                <Link href="/" class="brand-lockup">
                    <span class="brand-symbol">
                        <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
                            <path
                                d="M20 4L7 22h9l-3 13 14-19h-9L20 4Z"
                                fill="currentColor"
                            />
                            <path
                                d="M5 29c5-3 9-3 14 0s10 3 16-1"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                opacity=".6"
                            />
                        </svg>
                    </span>

                    <span class="brand-text">
                        <strong>NusaFire</strong>
                        <small>FOREST INTELLIGENCE</small>
                    </span>
                </Link>

                <div class="visual-message">
                    <div class="visual-eyebrow">
                        <span class="eyebrow-line"></span>
                        PROTECTING WHAT MATTERS
                    </div>

                    <h1>
                        See the signs.
                        <br />
                        <span>Protect the forest.</span>
                    </h1>

                    <p>
                        An environmental intelligence platform for understanding
                        fire hotspots, weather patterns, and forest fire activity
                        across Indonesia.
                    </p>

                    <div class="visual-features">
                        <div class="feature-item">
                            <span class="feature-icon">◎</span>
                            <div>
                                <strong>Hotspot monitoring</strong>
                                <span>Discover fire activity patterns</span>
                            </div>
                        </div>

                        <div class="feature-item">
                            <span class="feature-icon">⌁</span>
                            <div>
                                <strong>Environmental insights</strong>
                                <span>Explore weather and fire data</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="visual-footer">
                    <div class="footer-location">
                        <span class="location-dot"></span>
                        <span>INDONESIA</span>
                    </div>

                    <span>FOR A SAFER, GREENER FUTURE</span>
                </div>
            </div>
        </section>

        <section class="login-panel">
            <div class="login-panel-inner">
                <div class="mobile-brand">
                    <span class="brand-symbol">
                        <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
                            <path
                                d="M20 4L7 22h9l-3 13 14-19h-9L20 4Z"
                                fill="currentColor"
                            />
                            <path
                                d="M5 29c5-3 9-3 14 0s10 3 16-1"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                opacity=".6"
                            />
                        </svg>
                    </span>
                    <span class="brand-text">
                        <strong>NusaFire</strong>
                        <small>FOREST INTELLIGENCE</small>
                    </span>
                </div>

                <div class="login-heading">
                    <div class="form-eyebrow">WELCOME BACK</div>
                    <h2>Sign in to NusaFire</h2>
                    <p>
                        Welcome back. Enter your credentials to access your workspace.
                    </p>
                </div>

                <div v-if="status" class="status-message" role="status">
                    {{ status }}
                </div>

                <form class="login-form" @submit.prevent="submit">
                    <div class="form-field">
                        <label for="email">Email address</label>

                        <div
                            class="input-wrap"
                            :class="{ 'input-error': form.errors.email }"
                        >
                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.6"
                                aria-hidden="true"
                            >
                                <rect x="3" y="5" width="18" height="14" rx="2" />
                                <path
                                    d="m4 7 8 6 8-6"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>

                            <input
                                id="email"
                                v-model="form.email"
                                type="email"
                                name="email"
                                autocomplete="username"
                                placeholder="you@example.com"
                                required
                                autofocus
                                :disabled="form.processing"
                            />
                        </div>

                        <p v-if="form.errors.email" class="field-error">
                            {{ form.errors.email }}
                        </p>
                    </div>

                    <div class="form-field">
                        <div class="label-row">
                            <label for="password">Password</label>

                            <Link
                                v-if="canResetPassword"
                                href="/forgot-password"
                                class="forgot-link"
                            >
                                Forgot password?
                            </Link>
                        </div>

                        <div
                            class="input-wrap"
                            :class="{ 'input-error': form.errors.password }"
                        >
                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.6"
                                aria-hidden="true"
                            >
                                <rect x="4" y="10" width="16" height="11" rx="2" />
                                <path
                                    d="M8 10V7a4 4 0 0 1 8 0v3"
                                    stroke-linecap="round"
                                />
                                <circle cx="12" cy="15" r="1" />
                            </svg>

                            <input
                                id="password"
                                v-model="form.password"
                                :type="showPassword ? 'text' : 'password'"
                                name="password"
                                autocomplete="current-password"
                                placeholder="Enter your password"
                                required
                                :disabled="form.processing"
                            />

                            <button
                                type="button"
                                class="password-toggle"
                                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                                @click="showPassword = !showPassword"
                            >
                                <svg
                                    v-if="!showPassword"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="1.6"
                                    aria-hidden="true"
                                >
                                    <path
                                        d="M2.5 12s3.3-6 9.5-6 9.5 6 9.5 6-3.3 6-9.5 6-9.5-6-9.5-6Z"
                                        stroke-linejoin="round"
                                    />
                                    <circle cx="12" cy="12" r="2.5" />
                                </svg>

                                <svg
                                    v-else
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="1.6"
                                    aria-hidden="true"
                                >
                                    <path
                                        d="m3 3 18 18M10.6 6.2A10.5 10.5 0 0 1 12 6c6.2 0 9.5 6 9.5 6a16 16 0 0 1-3 3.5M6.2 6.2C3.8 7.7 2.5 12 2.5 12s3.3 6 9.5 6c1 0 1.9-.2 2.8-.5"
                                        stroke-linecap="round"
                                    />
                                </svg>
                            </button>
                        </div>

                        <p v-if="form.errors.password" class="field-error">
                            {{ form.errors.password }}
                        </p>
                    </div>

                    <label class="remember-row">
                        <input
                            v-model="form.remember"
                            type="checkbox"
                            name="remember"
                            :disabled="form.processing"
                        />
                        <span class="custom-checkbox"></span>
                        <span>Remember me</span>
                    </label>

                    <div v-if="form.errors.email && !form.errors.password" class="login-error-summary">
                        Please check your email and password, then try again.
                    </div>

                    <button
                        type="submit"
                        class="login-submit"
                        :disabled="form.processing"
                    >
                        <span>{{ form.processing ? 'Signing in...' : 'Sign in to workspace' }}</span>
                        <svg
                            v-if="!form.processing"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.8"
                            aria-hidden="true"
                        >
                            <path
                                d="M5 12h14m-6-6 6 6-6 6"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                        <span v-else class="loading-indicator"></span>
                    </button>

                    <div class="form-divider">
                        <span></span>
                        <small>SECURE ACCESS</small>
                        <span></span>
                    </div>

                    <p v-if="canRegister" class="register-prompt">
                        Don't have an account?
                        <Link href="/register">Create an account</Link>
                    </p>
                </form>

                <div class="security-note">
                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3Z"
                            stroke-linejoin="round"
                        />
                        <path
                            d="m9 12 2 2 4-4"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                    <span>Your workspace is protected by secure authentication.</span>
                </div>
            </div>

            <footer class="login-bottom-footer">
                <span>© 2026 NusaFire</span>
                <span>Environmental Intelligence</span>
            </footer>
        </section>
    </main>
</template>

<style>
.login-page {
    --login-bg: #f7f9f6;
    --login-surface: #ffffff;
    --login-text: #1c2922;
    --login-muted: #738078;
    --login-border: #e1e8e0;
    --login-input: #ffffff;
    --login-accent: #287a50;
    --login-accent-hover: #206642;
    --login-accent-soft: #eaf5ed;
    --login-error: #c14f49;

    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1.04fr) minmax(430px, .96fr);
    min-height: 100vh;
    color: var(--login-text);
    background: var(--login-bg);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    transition: color .2s ease, background .2s ease;
}

.login-page.theme-dark {
    --login-bg: #111914;
    --login-surface: #19231c;
    --login-text: #edf4ed;
    --login-muted: #9aa99d;
    --login-border: #2b3a2e;
    --login-input: #151e18;
    --login-accent: #70cf98;
    --login-accent-hover: #88dda9;
    --login-accent-soft: #213b2b;
    --login-error: #f08b82;
}

.login-page *,
.login-page *::before,
.login-page *::after {
    box-sizing: border-box;
}

.login-page button,
.login-page input {
    font: inherit;
}

.login-page button,
.login-page a {
    -webkit-tap-highlight-color: transparent;
}

.login-page a {
    text-decoration: none;
}

.login-page button:focus-visible,
.login-page a:focus-visible,
.login-page input:focus-visible {
    outline: 3px solid rgb(73 167 106 / 35%);
    outline-offset: 3px;
}

.theme-switch {
    position: absolute;
    top: 24px;
    right: 25px;
    z-index: 10;
    display: grid;
    width: 40px;
    height: 40px;
    place-items: center;
    color: var(--login-text);
    background: var(--login-surface);
    border: 1px solid var(--login-border);
    border-radius: 12px;
    box-shadow: 0 3px 12px rgb(0 0 0 / 4%);
    cursor: pointer;
    font-size: 20px;
    transition: background .2s ease, color .2s ease;
}

.theme-switch:hover {
    color: var(--login-accent);
}

.login-visual {
    position: relative;
    display: flex;
    min-height: 100vh;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    padding: 36px clamp(30px, 5vw, 76px) 29px;
    color: #f4f8f3;
    background: #102c20;
}

.visual-background {
    position: absolute;
    inset: 0;
    overflow: hidden;
    background: #102c20;
}

.forest-art {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: .95;
}

.visual-glow {
    position: absolute;
    z-index: 1;
    width: 400px;
    height: 400px;
    pointer-events: none;
    border-radius: 50%;
    filter: blur(90px);
}

.visual-glow-one {
    top: 10%;
    right: -25%;
    background: rgb(79 158 99 / 16%);
}

.visual-glow-two {
    bottom: 8%;
    left: -30%;
    background: rgb(45 120 77 / 18%);
}

.visual-grain {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        180deg,
        rgb(7 24 16 / 14%) 0%,
        rgb(7 24 16 / 5%) 40%,
        rgb(7 24 16 / 72%) 100%
    );
}

.visual-content {
    position: relative;
    z-index: 2;
    display: flex;
    flex: 1;
    flex-direction: column;
}

.brand-lockup {
    display: inline-flex;
    align-items: center;
    align-self: flex-start;
    gap: 12px;
    color: #fff;
}

.brand-symbol {
    display: grid;
    width: 43px;
    height: 43px;
    flex: 0 0 43px;
    place-items: center;
    color: #fff;
    background: #2d8657;
    border: 1px solid rgb(255 255 255 / 14%);
    border-radius: 12px;
}

.brand-symbol svg {
    width: 31px;
    height: 31px;
}

.brand-text {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.brand-text strong {
    font-size: 20px;
    font-weight: 750;
    letter-spacing: -.65px;
}

.brand-text small {
    color: #b8cdbd;
    font-size: 8px;
    font-weight: 750;
    letter-spacing: 1.65px;
}

.visual-message {
    max-width: 530px;
    margin-top: auto;
    margin-bottom: auto;
    padding: 70px 0 55px;
}

.visual-eyebrow,
.form-eyebrow {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #a8d8b4;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 1.8px;
}

.eyebrow-line {
    width: 24px;
    height: 2px;
    background: #75bd8a;
}

.visual-message h1 {
    margin: 25px 0 20px;
    color: #f5faf4;
    font-size: clamp(36px, 4.2vw, 59px);
    font-weight: 750;
    letter-spacing: -2.4px;
    line-height: 1.13;
}

.visual-message h1 span {
    color: #a6d6b0;
}

.visual-message > p {
    max-width: 430px;
    margin: 0;
    color: #c4d3c7;
    font-size: 13px;
    line-height: 1.95;
}

.visual-features {
    display: grid;
    gap: 19px;
    margin-top: 40px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 13px;
}

.feature-icon {
    display: grid;
    width: 41px;
    height: 41px;
    flex: 0 0 41px;
    place-items: center;
    color: #a6d6b0;
    background: rgb(255 255 255 / 7%);
    border: 1px solid rgb(255 255 255 / 10%);
    border-radius: 11px;
    font-size: 23px;
}

.feature-item div {
    display: grid;
    gap: 5px;
}

.feature-item strong {
    color: #f0f6f0;
    font-size: 12px;
    font-weight: 650;
}

.feature-item div span {
    color: #a8bdb0;
    font-size: 10px;
}

.visual-footer {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding-top: 22px;
    color: #a5bbae;
    border-top: 1px solid rgb(255 255 255 / 14%);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 1px;
}

.footer-location {
    display: flex;
    align-items: center;
    gap: 8px;
}

.location-dot {
    width: 7px;
    height: 7px;
    background: #7bc58f;
    border-radius: 50%;
}

.login-panel {
    display: flex;
    min-width: 0;
    min-height: 100vh;
    flex-direction: column;
    justify-content: center;
    padding: 88px clamp(30px, 5.5vw, 88px) 25px;
    background: var(--login-bg);
    transition: background .2s ease;
}

.login-panel-inner {
    width: 100%;
    max-width: 405px;
    margin: 0 auto;
}

.mobile-brand {
    display: none;
}

.login-heading {
    margin-bottom: 34px;
}

.form-eyebrow {
    color: var(--login-accent);
    font-size: 9px;
    letter-spacing: 1.7px;
}

.login-heading h2 {
    margin: 15px 0 11px;
    color: var(--login-text);
    font-size: clamp(25px, 2.5vw, 32px);
    font-weight: 750;
    letter-spacing: -1.1px;
    line-height: 1.25;
}

.login-heading p {
    max-width: 360px;
    margin: 0;
    color: var(--login-muted);
    font-size: 12px;
    line-height: 1.8;
}

.login-form {
    display: grid;
    gap: 23px;
}

.form-field {
    display: grid;
    gap: 9px;
}

.form-field > label,
.label-row > label {
    color: var(--login-text);
    font-size: 11px;
    font-weight: 650;
}

.label-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.forgot-link {
    color: var(--login-accent);
    font-size: 10px;
    font-weight: 650;
}

.forgot-link:hover,
.register-prompt a:hover {
    text-decoration: underline;
    text-underline-offset: 3px;
}

.input-wrap {
    display: flex;
    align-items: center;
    min-height: 49px;
    gap: 11px;
    padding: 0 13px;
    background: var(--login-input);
    border: 1px solid var(--login-border);
    border-radius: 10px;
    transition: border-color .15s ease, box-shadow .15s ease, background .2s ease;
}

.input-wrap:focus-within {
    border-color: var(--login-accent);
    box-shadow: 0 0 0 3px rgb(65 148 92 / 10%);
}

.input-wrap.input-error {
    border-color: var(--login-error);
}

.input-wrap > svg {
    width: 18px;
    height: 18px;
    flex: 0 0 18px;
    color: var(--login-muted);
}

.input-wrap input {
    width: 100%;
    min-width: 0;
    height: 46px;
    padding: 0;
    color: var(--login-text);
    background: transparent;
    border: 0;
    outline: none;
    font-size: 11px;
}

.input-wrap input::placeholder {
    color: var(--login-muted);
    opacity: .75;
}

.input-wrap input:focus-visible {
    outline: none;
}

.input-wrap input:disabled {
    opacity: .65;
}

.password-toggle {
    display: grid;
    width: 28px;
    height: 32px;
    flex: 0 0 28px;
    place-items: center;
    color: var(--login-muted);
    background: transparent;
    border: 0;
    border-radius: 6px;
}

.password-toggle:hover {
    color: var(--login-accent);
}

.password-toggle svg {
    width: 18px;
    height: 18px;
}

.field-error {
    margin: 0;
    color: var(--login-error);
    font-size: 10px;
    line-height: 1.6;
}

.remember-row {
    position: relative;
    display: inline-flex;
    align-items: center;
    align-self: flex-start;
    gap: 10px;
    color: var(--login-muted);
    font-size: 11px;
    cursor: pointer;
    user-select: none;
}

.remember-row input {
    position: absolute;
    width: 17px;
    height: 17px;
    margin: 0;
    opacity: 0;
    cursor: pointer;
}

.custom-checkbox {
    display: grid;
    width: 17px;
    height: 17px;
    flex: 0 0 17px;
    place-items: center;
    background: var(--login-input);
    border: 1px solid var(--login-border);
    border-radius: 5px;
    transition: background .15s ease, border-color .15s ease;
}

.remember-row input:checked + .custom-checkbox {
    background: var(--login-accent);
    border-color: var(--login-accent);
}

.remember-row input:checked + .custom-checkbox::after {
    width: 5px;
    height: 9px;
    content: "";
    border-right: 2px solid #fff;
    border-bottom: 2px solid #fff;
    transform: translateY(-1px) rotate(45deg);
}

.remember-row input:focus-visible + .custom-checkbox {
    outline: 3px solid rgb(73 167 106 / 35%);
    outline-offset: 3px;
}

.login-error-summary,
.status-message {
    padding: 11px 13px;
    border-radius: 8px;
    font-size: 11px;
    line-height: 1.7;
}

.login-error-summary {
    color: var(--login-error);
    background: rgb(193 79 73 / 8%);
    border: 1px solid rgb(193 79 73 / 20%);
}

.status-message {
    margin-bottom: 20px;
    color: var(--login-accent);
    background: var(--login-accent-soft);
}

.login-submit {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 49px;
    gap: 12px;
    padding: 0 17px;
    color: #fff;
    background: #287a50;
    border: 0;
    border-radius: 10px;
    box-shadow: 0 5px 13px rgb(40 122 80 / 14%);
    font-size: 11px;
    font-weight: 700;
    transition: background .15s ease, transform .15s ease, box-shadow .15s ease;
}

.login-submit:hover:not(:disabled) {
    background: #206642;
    box-shadow: 0 7px 18px rgb(40 122 80 / 20%);
    transform: translateY(-1px);
}

.login-submit:disabled {
    opacity: .7;
}

.login-submit svg {
    width: 17px;
    height: 17px;
}

.loading-indicator {
    width: 15px;
    height: 15px;
    border: 2px solid rgb(255 255 255 / 35%);
    border-top-color: #fff;
    border-radius: 50%;
    animation: login-spin .7s linear infinite;
}

@keyframes login-spin {
    to {
        transform: rotate(360deg);
    }
}

.form-divider {
    display: flex;
    align-items: center;
    gap: 13px;
    margin-top: 1px;
}

.form-divider span {
    height: 1px;
    flex: 1;
    background: var(--login-border);
}

.form-divider small {
    color: var(--login-muted);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 1.2px;
}

.register-prompt {
    margin: -2px 0 0;
    color: var(--login-muted);
    font-size: 11px;
    text-align: center;
}

.register-prompt a {
    margin-left: 4px;
    color: var(--login-accent);
    font-weight: 700;
}

.security-note {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 9px;
    margin-top: 34px;
    padding-top: 20px;
    color: var(--login-muted);
    border-top: 1px solid var(--login-border);
    font-size: 9px;
    line-height: 1.7;
}

.security-note svg {
    width: 17px;
    height: 17px;
    flex: 0 0 17px;
    color: var(--login-accent);
}

.login-bottom-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    max-width: 405px;
    margin: 48px auto 0;
    color: var(--login-muted);
    font-size: 9px;
}

@media (min-width: 1500px) {
    .login-panel {
        padding-right: 90px;
        padding-left: 90px;
    }
}

@media (max-width: 1000px) {
    .login-page {
        grid-template-columns: minmax(0, .85fr) minmax(390px, 1fr);
    }

    .login-visual {
        padding-right: 30px;
        padding-left: 30px;
    }

    .visual-message h1 {
        font-size: 39px;
        letter-spacing: -1.6px;
    }

    .login-panel {
        padding-right: 32px;
        padding-left: 32px;
    }
}

@media (max-width: 760px) {
    .login-page {
        display: flex;
        min-height: 100vh;
        flex-direction: column;
    }

    .login-visual {
        display: none;
    }

    .login-panel {
        position: relative;
        min-height: 100vh;
        padding: 95px 25px 25px;
    }

    .theme-switch {
        top: 20px;
        right: 20px;
    }

    .mobile-brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin-bottom: 55px;
    }

    .mobile-brand .brand-symbol {
        color: #fff;
        background: #287a50;
    }

    .mobile-brand .brand-text strong {
        color: var(--login-text);
    }

    .mobile-brand .brand-text small {
        color: var(--login-muted);
    }

    .login-panel-inner {
        max-width: 440px;
    }

    .login-bottom-footer {
        max-width: 440px;
        margin-top: 45px;
    }
}

@media (max-width: 420px) {
    .login-panel {
        padding-right: 20px;
        padding-left: 20px;
    }

    .mobile-brand {
        margin-bottom: 43px;
    }

    .login-heading h2 {
        font-size: 27px;
    }

    .login-form {
        gap: 20px;
    }

    .login-bottom-footer {
        align-items: flex-start;
        flex-direction: column;
        gap: 7px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .login-page *,
    .login-page *::before,
    .login-page *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
    }
}
</style>
