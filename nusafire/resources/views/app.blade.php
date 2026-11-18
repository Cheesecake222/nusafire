<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title inertia>{{ config('app.name', 'Laravel') }}</title>

        <link rel="icon" type="image/png" href="/favicon.png">
        <link rel="shortcut icon" href="/favicon.ico">
        <link rel="apple-touch-icon" href="/logo.png">

        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=instrument-sans:400,500,600" rel="stylesheet" />

        @routes
        @vite(['resources/js/app.ts'])
        @inertiaHead
        {{-- Script ini dijalankan sinkron sebelum CSS/Vue dimuat agar --}}
        {{-- class tema langsung diterapkan tanpa flash/perubahan tampilan. Default: light mode --}}
        <script>
            (function () {
                var t = localStorage.getItem('nusafire-theme') || localStorage.getItem('appearance');
                var theme = (t === 'dark') ? 'dark' : 'light';
                document.documentElement.classList.remove('theme-dark', 'theme-light', 'dark');
                document.documentElement.classList.add('theme-' + theme);
                if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                }
                document.documentElement.dataset.theme = theme;
                document.documentElement.style.colorScheme = theme;
            })();
        </script>
    </head>
    <body class="font-sans antialiased">
        @inertia
    </body>
</html>
