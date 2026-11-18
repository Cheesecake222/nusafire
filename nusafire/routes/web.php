<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Api\NusaFireAiController;

Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::get('/hotspot-map', function () {
    return Inertia::render('HotspotMap');
})->middleware(['auth', 'verified'])->name('hotspot-map');

Route::get('/weather-analysis', function () {
    return Inertia::render('WeatherAnalysis');
})->middleware(['auth', 'verified'])->name('weather-analysis');

// Aliases for weather URL (with spaces, underscores, or shorthand)
Route::get('/weather analysis', function () {
    return redirect()->route('weather-analysis');
})->middleware(['auth', 'verified']);

Route::get('/weather_analysis', function () {
    return redirect()->route('weather-analysis');
})->middleware(['auth', 'verified']);

Route::get('/weather', function () {
    return redirect()->route('weather-analysis');
})->middleware(['auth', 'verified']);

Route::get('/ai-prediction', function () {
    return Inertia::render('AiPrediction');
})->middleware(['auth', 'verified'])->name('ai-prediction');

// Aliases for AI prediction URL
Route::get('/ai prediction', function () {
    return redirect()->route('ai-prediction');
})->middleware(['auth', 'verified']);

Route::get('/ai_prediction', function () {
    return redirect()->route('ai-prediction');
})->middleware(['auth', 'verified']);

// Aliases for hotspot map URL
Route::get('/hotspot map', function () {
    return redirect()->route('hotspot-map');
})->middleware(['auth', 'verified']);

Route::get('/hotspot_map', function () {
    return redirect()->route('hotspot-map');
})->middleware(['auth', 'verified']);

Route::get('/forest-watch', function () {
    return Inertia::render('ForestWatch');
})->middleware(['auth', 'verified'])->name('forest-watch');

// Aliases for Forest Watch URL
Route::get('/forest watch', function () {
    return redirect()->route('forest-watch');
})->middleware(['auth', 'verified']);

Route::get('/forest_watch', function () {
    return redirect()->route('forest-watch');
})->middleware(['auth', 'verified']);


Route::middleware(['auth', 'verified'])
    ->prefix('internal/ai')
    ->name('ai.')
    ->group(function () {
        Route::get('/health', [NusaFireAiController::class, 'health'])->name('health');
        Route::get('/stats', [NusaFireAiController::class, 'stats'])->name('stats');
        Route::get('/hotspots', [NusaFireAiController::class, 'hotspots'])->name('hotspots');
        Route::get('/charts', [NusaFireAiController::class, 'charts'])->name('charts');
        Route::get('/regions', [NusaFireAiController::class, 'regions'])->name('regions');
        Route::get('/locations', [NusaFireAiController::class, 'locations'])->name('locations');
        Route::post('/predict', [NusaFireAiController::class, 'predict'])->name('predict');
        Route::post('/predict-realtime', [NusaFireAiController::class, 'predictRealtime'])->name('predict-realtime');
        Route::get('/realtime-overview', [NusaFireAiController::class, 'realtimeOverview'])->name('realtime-overview');
        Route::get('/weather-history', [NusaFireAiController::class, 'weatherHistory'])->name('weather-history');
        Route::get('/firms-hotspots', [NusaFireAiController::class, 'firmsHotspots'])->name('firms-hotspots');
    });

require __DIR__ . '/settings.php';
require __DIR__ . '/auth.php';