<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Throwable;

class NusaFireAiController extends Controller
{
    private function aiUrl(): string
    {
        $configured = config('services.nusafire_ai.url')
            ?: env('NUSAFIRE_AI_URL', 'http://127.0.0.1:8001');

        return rtrim((string) $configured, '/');
    }

    private function requestAi(
        string $method,
        string $endpoint,
        array $data = [],
        int $timeout = 30
    ): JsonResponse {
        try {
            $request = Http::acceptJson()
                ->connectTimeout(10)
                ->timeout($timeout);

            $response = match (strtoupper($method)) {
                'POST' => $request->post(
                    $this->aiUrl() . $endpoint,
                    $data
                ),
                'GET' => $request->get(
                    $this->aiUrl() . $endpoint,
                    $data
                ),
                default => throw new \InvalidArgumentException(
                    'Metode permintaan tidak didukung.'
                ),
            };

            if ($response->failed()) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Python AI mengembalikan respons error.',
                    'ai_status' => $response->status(),
                ], 502);
            }

            $result = $response->json();

            if (!is_array($result)) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Respons Python AI bukan JSON yang valid.',
                ], 502);
            }

            return response()->json($result, $response->status());
        } catch (ConnectionException $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Layanan NusaFire AI Engine tidak dapat dijangkau.',
                'detail' => 'Pastikan server FastAPI berjalan pada ' . $this->aiUrl(),
            ], 503);
        } catch (Throwable $e) {
            report($e);

            return response()->json([
                'status' => 'error',
                'message' => 'Terjadi kesalahan saat menghubungi layanan AI.',
            ], 500);
        }
    }

    public function health(): JsonResponse
    {
        return $this->requestAi('GET', '/health', [], 10);
    }

    public function stats(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'start_date' => ['sometimes', 'nullable', 'date_format:Y-m-d'],
            'end_date' => ['sometimes', 'nullable', 'date_format:Y-m-d', 'after_or_equal:start_date'],
            'region' => ['sometimes', 'nullable', 'string', 'max:100'],
        ]);

        return $this->requestAi('GET', '/stats', $filters);
    }

    public function hotspots(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'start_date' => ['sometimes', 'nullable', 'date_format:Y-m-d'],
            'end_date' => ['sometimes', 'nullable', 'date_format:Y-m-d', 'after_or_equal:start_date'],
            'region' => ['sometimes', 'nullable', 'string', 'max:100'],
            'status' => ['sometimes', 'required', 'in:all,fire,non-fire'],
            'limit' => ['sometimes', 'integer', 'min:1', 'max:1000'],
            'offset' => ['sometimes', 'integer', 'min:0'],
        ]);

        return $this->requestAi('GET', '/hotspots', $filters);
    }

    public function locations(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'region' => ['sometimes', 'nullable', 'string', 'max:100'],
        ]);

        return $this->requestAi('GET', '/locations', $filters);
    }

    public function charts(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'period' => ['sometimes', 'in:daily,monthly'],
            'start_date' => ['sometimes', 'nullable', 'date_format:Y-m-d'],
            'end_date' => ['sometimes', 'nullable', 'date_format:Y-m-d', 'after_or_equal:start_date'],
            'region' => ['sometimes', 'nullable', 'string', 'max:100'],
        ]);

        return $this->requestAi('GET', '/charts', $filters);
    }

    public function regions(): JsonResponse
    {
        return $this->requestAi('GET', '/regions');
    }

    public function predict(Request $request): JsonResponse
    {
        $data = $request->validate([
            'PRECTOTCORR' => ['required', 'numeric'],
            'T2M' => ['required', 'numeric'],
            'T2M_MAX' => ['required', 'numeric'],
            'T2M_MIN' => ['required', 'numeric'],
            'RH2M' => ['required', 'numeric', 'between:0,100'],
            'WS10M' => ['required', 'numeric', 'min:0'],
            'LATITUDE' => ['required', 'numeric', 'between:-90,90'],
            'LONGITUDE' => ['required', 'numeric', 'between:-180,180'],
            'landcover_class' => ['required', 'integer', 'min:0'],
        ]);

        return $this->requestAi('POST', '/predict', $data);
    }

    public function predictRealtime(Request $request): JsonResponse
    {
        $data = $request->validate([
            'LATITUDE' => ['required', 'numeric', 'between:-90,90'],
            'LONGITUDE' => ['required', 'numeric', 'between:-180,180'],
            'landcover_class' => ['sometimes', 'nullable', 'integer', 'min:0'],
        ]);

        if (!isset($data['landcover_class']) || $data['landcover_class'] === null) {
            unset($data['landcover_class']);
        }

        return $this->requestAi('POST', '/predict-realtime', $data, 35);
    }

    public function realtimeOverview(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'force_refresh' => ['sometimes', 'boolean'],
        ]);

        return $this->requestAi('GET', '/realtime-overview', $filters, 35);
    }

    public function weatherHistory(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'latitude' => ['required', 'numeric', 'between:-90,90'],
            'longitude' => ['required', 'numeric', 'between:-180,180'],
            'days' => ['sometimes', 'integer', 'min:7', 'max:14'],
        ]);

        return $this->requestAi('GET', '/weather-history', [
            'latitude' => $filters['latitude'],
            'longitude' => $filters['longitude'],
            'days' => $filters['days'] ?? 10,
        ], 30);
    }

    public function firmsHotspots(Request $request): JsonResponse
    {
        $filters = $request->validate([
            'days' => ['sometimes', 'integer', 'min:1', 'max:10'],
            'sensor' => ['sometimes', 'string', 'in:VIIRS_SNPP_NRT,VIIRS_NOAA20_NRT,VIIRS_NOAA21_NRT,MODIS_NRT'],
            'province' => ['sometimes', 'nullable', 'string', 'max:100'],
        ]);

        $params = array_filter([
            'days' => $filters['days'] ?? 2,
            'sensor' => $filters['sensor'] ?? 'VIIRS_SNPP_NRT',
            'province' => $filters['province'] ?? null,
        ], fn ($value) => $value !== null && $value !== '');

        return $this->requestAi('GET', '/firms-hotspots', $params, 40);
    }
}