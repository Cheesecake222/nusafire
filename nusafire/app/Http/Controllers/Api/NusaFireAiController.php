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
        return rtrim(
            config('services.nusafire_ai.url', 'http://127.0.0.1:8001'),
            '/'
        );
    }

    private function requestAi(string $method, string $endpoint, array $data = []): JsonResponse
    {
        try {
            $request = Http::acceptJson()->timeout(30);

            $response = match (strtoupper($method)) {
                'POST' => $request->post($this->aiUrl() . $endpoint, $data),
                'GET' => $request->get($this->aiUrl() . $endpoint, $data),
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

            return response()->json($response->json() ?? [
                'status' => 'error',
                'message' => 'Respons Python AI bukan JSON yang valid.',
            ]);
        } catch (ConnectionException $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Tidak dapat terhubung ke layanan Python AI.',
                'detail' => 'Pastikan server FastAPI berjalan pada port 8001.',
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
        return $this->requestAi('GET', '/health');
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
            'limit' => ['sometimes', 'integer', 'min:1', 'max:1000'],
            'offset' => ['sometimes', 'integer', 'min:0'],
        ]);

        return $this->requestAi('GET', '/hotspots', $filters);
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
}
