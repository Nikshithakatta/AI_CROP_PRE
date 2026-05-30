import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Add the project root to sys.path so the 'backend' package is findable
# even if run directly as 'python backend/main.py' from the root.
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import APIRouter, FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from backend.services import EnhancedSoilService, LocationService, WeatherService, MandiService, CostBenefitAnalysis
from backend.models.crop_predictor import CropPredictor
from backend.models.location_crop_predictor import LocationBasedCropPredictor
import backend.config as config

from contextlib import asynccontextmanager

# ---------------------------------------------------------------------------
# Global State
# ---------------------------------------------------------------------------

services: Dict[str, Any] = {}
predictors: Dict[str, Any] = {}

# ---------------------------------------------------------------------------
# FastAPI Setup & Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services
    print("\n[INIT] Initializing services...")
    services["location_service"] = LocationService()
    services["weather_service"] = WeatherService()
    services["soil_service"] = EnhancedSoilService()
    services["mandi_service"] = MandiService()
    services["cost_benefit_service"] = CostBenefitAnalysis()

    # Initialize predictors (load model files from backend/models)
    print("[INIT] Loading machine learning models...")
    try:
        predictors["crop_predictor"] = CropPredictor()
        if not predictors["crop_predictor"].load_model():
            print("[WARN] Crop predictor model failed to load, but continuing...")
    except Exception as e:
        print(f"[WARN] Failed to initialize crop predictor: {e}")

    try:
        predictors["location_crop_predictor"] = LocationBasedCropPredictor()
        if not predictors["location_crop_predictor"].load_model():
            print("[WARN] Location crop predictor model failed to load, but continuing...")
    except Exception as e:
        print(f"[WARN] Failed to initialize location crop predictor: {e}")
    
    # Reload historical data if needed
    if predictors["location_crop_predictor"].location_crop_data is None:
        dataset_path = os.path.join(os.path.dirname(__file__), "data", "crop_production.csv")
        predictors["location_crop_predictor"].load_and_preprocess_data(dataset_path=dataset_path)
    
    print("[OK] System ready and serving requests!\n")
    yield
    # Clean up if needed
    print("[STOP] Shutting down server...")

app = FastAPI(
    title="AI Crop Prediction API",
    lifespan=lifespan,
    description="Backend API for AI-powered Crop Prediction and Market Analysis"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Crop Prediction API is running",
        "documentation": "/docs"
    }

# ---------------------------------------------------------------------------
# Authorization Security
# ---------------------------------------------------------------------------

API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

api_key_header_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)

async def get_api_key(
    api_key: str = Security(api_key_header_scheme),
):
    if api_key == API_KEY_SECRET:
        return api_key
    raise HTTPException(
        status_code=403,
        detail="Could not validate API Key. Please provide a valid X-API-Key header."
    )

class MandiPriceRecord(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float
    predicted_price: Optional[float] = None


class MandiPricesResponse(BaseModel):
    commodity: str
    prices: List[MandiPriceRecord]


class LocationCoordinates(BaseModel):
    latitude: float
    longitude: float


class AddressResponse(BaseModel):
    address: str


class LatLonRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    # Optional: lets us keep the exact location string used by the UI.
    location_name: Optional[str] = None


class EnvironmentalResponse(BaseModel):
    weather_data: Dict[str, Any]
    soil_data: Dict[str, Any]


class CropInputWeather(BaseModel):
    temperature: float
    humidity: float
    rainfall: float


class CropInputSoil(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float


class CropPredictRequest(BaseModel):
    weather: CropInputWeather
    soil: CropInputSoil
    top_n: int = Field(5, ge=1, le=20)


class CropRecommendation(BaseModel):
    crop_name: str
    confidence: float


class CropPredictResponse(BaseModel):
    top_recommendations: List[CropRecommendation]
    best_crop: CropRecommendation


class LocationBasedRecommendationsRequest(BaseModel):
    location_name: str = Field(..., min_length=2)
    top_n: int = Field(10, ge=1, le=20)


class LocationBasedRecommendationsResponse(BaseModel):
    top_recommendations: List[CropRecommendation]


class CostBreakdown(BaseModel):
    seeds: float
    fertilizers: float
    pesticides: float
    labor: float
    irrigation: float
    machinery: float


class CostBenefitAnalysisResponse(BaseModel):
    crop_name: str
    costs_breakdown: CostBreakdown
    total_cost: float
    expected_yield: float
    market_price: float
    expected_revenue: float
    net_profit: float
    roi_percentage: float
    break_even_price: float
    profitability_rating: str
    rating_color: str
    insights: List[str]


class CropComparisonResponse(BaseModel):
    comparisons: List[CostBenefitAnalysisResponse]


def _normalize_part(part: str) -> str:
    part_clean = part.strip().upper()
    # Streamlit app.py removes a few common suffixes to make matching easier.
    part_clean = part_clean.replace(" DISTRICT", "").replace(" CITY", "").replace(" URBAN", "")
    part_clean = part_clean.replace(" RURAL", "")
    return part_clean


def _strings_match(part_clean: str, candidate: str) -> bool:
    candidate_clean = candidate.upper().strip()
    return (
        part_clean == candidate_clean
        or part_clean in candidate_clean
        or candidate_clean in part_clean
        or part_clean.replace(" ", "") == candidate_clean.replace(" ", "")
    )


def _top_state_recommendations(predictor: LocationBasedCropPredictor, state: str, n: int) -> List[Tuple[str, float]]:
    state_data = predictor.location_crop_data[predictor.location_crop_data["State_Name"] == state]
    if state_data.empty:
        return []

    top_crops = (
        state_data.groupby("Crop")["Production"].mean().sort_values(ascending=False).head(n)
    )

    max_prod = top_crops.max() if len(top_crops) > 0 else 0
    results: List[Tuple[str, float]] = []
    for crop, production in top_crops.items():
        confidence = (production / max_prod) if max_prod > 0 else 0.5
        results.append((crop, confidence))
    return results


def _top_district_recommendations(
    predictor: LocationBasedCropPredictor, district: str, n: int
) -> List[Tuple[str, float]]:
    district_data = predictor.location_crop_data[predictor.location_crop_data["District_Name"] == district]
    if district_data.empty:
        return []

    top_crops = (
        district_data.groupby("Crop")["Production"].mean().sort_values(ascending=False).head(n)
    )

    max_prod = top_crops.max() if len(top_crops) > 0 else 0
    results: List[Tuple[str, float]] = []
    for crop, production in top_crops.items():
        confidence = (production / max_prod) if max_prod > 0 else 0.5
        results.append((crop, confidence))
    return results


def _overall_popular_recommendations(predictor: LocationBasedCropPredictor, n: int) -> List[Tuple[str, float]]:
    overall_crops = (
        predictor.location_crop_data.groupby("Crop")["Production"].mean().sort_values(ascending=False).head(max(20, n * 2))
    )

    results: List[Tuple[str, float]] = []
    # Streamlit app.py uses a “balanced” confidence decay for the top 10.
    for i, (crop, _production) in enumerate(overall_crops.head(n).items(), 1):
        confidence = max(0.3, 1.0 - (i - 1) * 0.15)
        results.append((crop, confidence))
    return results


def _format_recommendations(recs: List[Tuple[str, float]]) -> List[CropRecommendation]:
    return [CropRecommendation(crop_name=str(crop).title(), confidence=float(conf)) for crop, conf in recs]


router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/location/coordinates", response_model=LocationCoordinates, dependencies=[Depends(get_api_key)])
def get_coordinates(location_name: str) -> LocationCoordinates:
    loc = services["location_service"].get_coordinates_from_location(location_name)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    lat, lon = loc
    return LocationCoordinates(latitude=lat, longitude=lon)


@router.post("/location/address", response_model=AddressResponse, dependencies=[Depends(get_api_key)])
def get_address(req: LatLonRequest) -> AddressResponse:
    address = services["location_service"].get_location_from_coordinates(req.lat, req.lon)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found for these coordinates")
    return AddressResponse(address=address)


@router.post("/environmental", response_model=EnvironmentalResponse, dependencies=[Depends(get_api_key)])
def get_environmental(req: LatLonRequest) -> EnvironmentalResponse:
    weather_data = services["weather_service"].get_weather_data(req.lat, req.lon)
    soil_data = services["soil_service"].get_soil_data(
        lat=req.lat, lon=req.lon, location_name=req.location_name
    )

    if not weather_data or not soil_data:
        raise HTTPException(status_code=500, detail="Failed to fetch environmental data")

    # Match streamlit app.py behavior: append soil health score
    soil_health_score = services["soil_service"].get_soil_health_score(soil_data)
    soil_data = dict(soil_data)
    soil_data["health_score"] = soil_health_score

    return EnvironmentalResponse(weather_data=weather_data, soil_data=soil_data)


@router.post("/crops", response_model=CropPredictResponse, dependencies=[Depends(get_api_key)])
def predict_crops(req: CropPredictRequest) -> CropPredictResponse:
    crop_predictor: CropPredictor = predictors["crop_predictor"]

    features = {
        "soil_ph": req.soil.ph,
        "temperature": req.weather.temperature,
        "rainfall": req.weather.rainfall,
        "humidity": req.weather.humidity,
        "nitrogen": req.soil.nitrogen,
        "phosphorus": req.soil.phosphorus,
        "potassium": req.soil.potassium,
    }

    recommendations = crop_predictor.get_top_recommendations(features, top_n=req.top_n)
    if not recommendations:
        raise HTTPException(status_code=500, detail="No crop recommendations returned")

    top_recommendations = _format_recommendations(recommendations)
    best_crop_name, best_crop_conf = recommendations[0]
    best_crop = CropRecommendation(crop_name=str(best_crop_name).title(), confidence=float(best_crop_conf))

    return CropPredictResponse(top_recommendations=top_recommendations, best_crop=best_crop)


@router.post("/location-based-recommendations", response_model=LocationBasedRecommendationsResponse, dependencies=[Depends(get_api_key)])
def location_based_recommendations(req: LocationBasedRecommendationsRequest) -> LocationBasedRecommendationsResponse:
    predictor: LocationBasedCropPredictor = predictors["location_crop_predictor"]
    if predictor.location_crop_data is None:
        raise HTTPException(status_code=500, detail="Location-based data not loaded")

    location_name = req.location_name
    parts = [p.strip() for p in location_name.split(",") if p.strip()]

    available_states = predictor.location_crop_data["State_Name"].unique()
    available_districts = predictor.location_crop_data["District_Name"].unique()

    matched_state: Optional[str] = None
    matched_district: Optional[str] = None

    # Match streamlit app.py’s “fuzzy” matching approach.
    for part in parts:
        part_clean = _normalize_part(part)

        for state in available_states:
            if _strings_match(part_clean, str(state)):
                matched_state = str(state)
                break
        if matched_state:
            break

    for part in parts:
        part_clean = _normalize_part(part)

        for district in available_districts:
            if _strings_match(part_clean, str(district)):
                matched_district = str(district)
                break
        if matched_district:
            break

    if matched_state and matched_district:
        # The historical dataset can be sparse for some district/state pairs.
        # If we get very few recommendations, fall back to a broader (state-level) view
        # so the UI shows more useful results.
        recs = predictor.get_location_based_recommendations(matched_state, matched_district, top_n=req.top_n)
        if len(recs) < min(req.top_n, 3):
            recs = _top_state_recommendations(predictor, matched_state, req.top_n)
    elif matched_state:
        recs = _top_state_recommendations(predictor, matched_state, req.top_n)
    elif matched_district:
        recs = _top_district_recommendations(predictor, matched_district, req.top_n)
    else:
        recs = _overall_popular_recommendations(predictor, req.top_n)

    return LocationBasedRecommendationsResponse(top_recommendations=_format_recommendations(recs))


@router.get("/mandi/commodities", response_model=List[str], dependencies=[Depends(get_api_key)])
def get_mandi_commodities() -> List[str]:
    mandi_service: MandiService = services["mandi_service"]
    return mandi_service.get_commodities()


@router.get("/mandi/prices", response_model=MandiPricesResponse, dependencies=[Depends(get_api_key)])
def get_mandi_prices(commodity: str) -> MandiPricesResponse:
    mandi_service: MandiService = services["mandi_service"]
    prices = mandi_service.get_prices_by_commodity(commodity)
    return MandiPricesResponse(commodity=commodity, prices=prices)


@router.post("/mandi/retrain", dependencies=[Depends(get_api_key)])
def retrain_mandi_model() -> Dict[str, Any]:
    mandi_service: MandiService = services["mandi_service"]
    try:
        metrics = mandi_service.retrain_model()
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-benefit/{crop_name}", response_model=CostBenefitAnalysisResponse, dependencies=[Depends(get_api_key)])
def get_cost_benefit_analysis(crop_name: str, location: str = None, season: str = None) -> CostBenefitAnalysisResponse:
    cost_benefit_service: CostBenefitAnalysis = services["cost_benefit_service"]
    analysis = cost_benefit_service.calculate_cost_benefit(crop_name, location, season)
    if 'error' in analysis:
        raise HTTPException(status_code=404, detail=analysis['error'])
    return CostBenefitAnalysisResponse(**analysis)


@router.post("/cost-benefit/compare", response_model=CropComparisonResponse, dependencies=[Depends(get_api_key)])
def compare_crop_costs(crop_list: List[str]) -> CropComparisonResponse:
    cost_benefit_service: CostBenefitAnalysis = services["cost_benefit_service"]
    comparisons = cost_benefit_service.compare_crops(crop_list)
    return CropComparisonResponse(comparisons=comparisons)


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    print("\n[START] Starting AI Crop Prediction API Server...")
    print("[URL] http://127.0.0.1:8000")
    print("[DOCS] http://127.0.0.1:8000/docs\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

