
<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Api\NusaFireAiController;

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

// Integrasi Laravel dengan Python FastAPI
Route::middleware(['auth', 'verified'])
    ->prefix('internal/ai')
    ->name('ai.')
    ->group(function () {

        // Status layanan Python AI
        Route::get('/health', [
            NusaFireAiController::class,
            'health',
        ])->name('health');

        // Statistik data hotspot dan kebakaran
        Route::get('/stats', [
            NusaFireAiController::class,
            'stats',
        ])->name('stats');

        // Daftar data hotspot
        Route::get('/hotspots', [
            NusaFireAiController::class,
            'hotspots',
        ])->name('hotspots');

        // Data grafik harian atau bulanan
        Route::get('/charts', [
            NusaFireAiController::class,
            'charts',
        ])->name('charts');

        // Statistik berdasarkan wilayah
        Route::get('/regions', [
            NusaFireAiController::class,
            'regions',
        ])->name('regions');

        // Prediksi risiko kebakaran
        Route::post('/predict', [
            NusaFireAiController::class,
            'predict',
        ])->name('predict');
    });

// Route pengaturan dan autentikasi
require __DIR__ . '/settings.php';
require __DIR__ . '/auth.php';
