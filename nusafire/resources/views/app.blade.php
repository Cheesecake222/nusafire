<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title inertia>{{ config('app.name', 'Laravel') }}</title>

        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=instrument-sans:400,500,600" rel="stylesheet" />

        @routes
        @vite(['resources/js/app.ts'])
        @inertiaHead
        {{-- Script ini dijalankan sinkron sebelum CSS/Vue dimuat agar --}}
        {{-- class tema langsung diterapkan tanpa flash/perubahan tampilan. --}}
        <script>
            (function () {
                var t = localStorage.getItem('nusafire-theme');
                var theme = (t === 'light' || t === 'dark') ? t : 'dark';
                document.documentElement.classList.add('theme-' + theme);
                document.documentElement.style.colorScheme = theme;
            })();
        </script>
    </head>
    <body class="font-sans antialiased">
        @inertia
    </body>
</html>
