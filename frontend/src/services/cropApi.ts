const API_BASE_URL =
  process.env.REACT_APP_CROP_API_BASE_URL || 'http://127.0.0.1:8000/api';

type ApiOk<T> = { data: T; error?: undefined };
type ApiErr = { error: string; data?: undefined };
type ApiResponse<T> = ApiOk<T> | ApiErr;

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 800;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('X-API-Key') || 'AI_CROP_SECRET_2024',
          ...(options.headers || {}),
        },
      });

      const contentType = res.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');
      const body = isJson ? await res.json() : null;

      if (!res.ok) {
        return {
          error:
            (body && (body.detail || (body as any).message)) ||
            res.statusText ||
            'Request failed',
        };
      }

      return { data: body as T };
    } catch (e: any) {
      const msg = e?.message || 'Network error';
      if (attempt < MAX_RETRIES - 1) {
        await delay(RETRY_DELAY_MS * (attempt + 1));
        continue;
      }
      return { error: msg };
    }
  }
}

export type LocationCoordinates = {
  latitude: number;
  longitude: number;
};

export async function getCoordinatesFromLocation(
  location_name: string
): Promise<ApiResponse<LocationCoordinates>> {
  return apiRequest<LocationCoordinates>(
    `/location/coordinates?location_name=${encodeURIComponent(location_name)}`
  );
}

export type AddressResponse = { address: string };
export async function getAddressFromCoordinates(
  lat: number,
  lon: number
): Promise<ApiResponse<AddressResponse>> {
  return apiRequest<AddressResponse>('/location/address', {
    method: 'POST',
    body: JSON.stringify({ lat, lon }),
  });
}

export type EnvironmentalResponse = {
  weather_data: Record<string, number | string | null>;
  soil_data: Record<string, number | string | null>;
};

export async function getEnvironmentalData(
  lat: number,
  lon: number,
  location_name?: string
): Promise<ApiResponse<EnvironmentalResponse>> {
  return apiRequest<EnvironmentalResponse>('/environmental', {
    method: 'POST',
    body: JSON.stringify({ lat, lon, location_name }),
  });
}

export type CropRecommendation = {
  crop_name: string;
  confidence: number;
};

export type CropPredictResponse = {
  top_recommendations: CropRecommendation[];
  best_crop: CropRecommendation;
};

export type CropPredictRequest = {
  weather: { temperature: number; humidity: number; rainfall: number };
  soil: { nitrogen: number; phosphorus: number; potassium: number; ph: number };
  top_n?: number;
};

export async function predictCrops(
  req: CropPredictRequest
): Promise<ApiResponse<CropPredictResponse>> {
  return apiRequest<CropPredictResponse>('/crops', {
    method: 'POST',
    body: JSON.stringify({ ...req, top_n: req.top_n ?? 5 }),
  });
}

export type LocationBasedRecommendationsResponse = {
  top_recommendations: CropRecommendation[];
};

export async function getLocationBasedRecommendations(
  location_name: string,
  top_n: number = 10
): Promise<ApiResponse<LocationBasedRecommendationsResponse>> {
  return apiRequest<LocationBasedRecommendationsResponse>(
    '/location-based-recommendations',
    {
      method: 'POST',
      body: JSON.stringify({ location_name, top_n }),
    }
  );
}

export type MandiPriceRecord = {
  state: string;
  district: string;
  market: string;
  commodity: string;
  variety: string;
  grade: string;
  arrival_date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  predicted_price?: number;
};

export type MandiPricesResponse = {
  commodity: string;
  prices: MandiPriceRecord[];
};

export async function getMandiCommodities(): Promise<ApiResponse<string[]>> {
  return apiRequest<string[]>('/mandi/commodities');
}

export async function getMandiPrices(
  commodity: string
): Promise<ApiResponse<MandiPricesResponse>> {
  return apiRequest<MandiPricesResponse>(
    `/mandi/prices?commodity=${encodeURIComponent(commodity)}`
  );
}

export async function retrainMandiModel(): Promise<ApiResponse<{ status: string; metrics: any }>> {
  return apiRequest<{ status: string; metrics: any }>('/mandi/retrain', {
    method: 'POST',
  });
}

export type CostBreakdown = {
  seeds: number;
  fertilizers: number;
  pesticides: number;
  labor: number;
  irrigation: number;
  machinery: number;
};

export type CostBenefitAnalysisResponse = {
  crop_name: string;
  costs_breakdown: CostBreakdown;
  total_cost: number;
  expected_yield: number;
  market_price: number;
  expected_revenue: number;
  net_profit: number;
  roi_percentage: number;
  break_even_price: number;
  profitability_rating: string;
  rating_color: string;
  insights: string[];
};

export type CropComparisonResponse = {
  comparisons: CostBenefitAnalysisResponse[];
};

export async function getCostBenefitAnalysis(
  cropName: string,
  location?: string,
  season?: string
): Promise<ApiResponse<CostBenefitAnalysisResponse>> {
  const params = new URLSearchParams();
  if (location) params.append('location', location);
  if (season) params.append('season', season);

  return apiRequest<CostBenefitAnalysisResponse>(
    `/cost-benefit/${encodeURIComponent(cropName)}${params.toString() ? '?' + params.toString() : ''}`
  );
}

export async function compareCropCosts(
  cropList: string[]
): Promise<ApiResponse<CropComparisonResponse>> {
  return apiRequest<CropComparisonResponse>('/cost-benefit/compare', {
    method: 'POST',
    body: JSON.stringify(cropList),
  });
}
