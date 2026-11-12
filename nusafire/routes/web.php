
<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

// Landing page
Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

// Dashboard utama
Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

// Peta hotspot
Route::get('/hotspot-map', function () {
    return Inertia::render('HotspotMap');
})->middleware(['auth', 'verified'])->name('hotspot-map');

// Analisis cuaca
Route::get('/weather-analysis', function () {
    return Inertia::render('WeatherAnalysis');
})->middleware(['auth', 'verified'])->name('weather-analysis');

// Analisis area terbakar
Route::get('/burned-area', function () {
    return Inertia::render('BurnedArea');
})->middleware(['auth', 'verified'])->name('burned-area');

require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
