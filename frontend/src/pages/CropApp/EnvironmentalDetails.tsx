import React, { useMemo, useState } from 'react';
import {
  getAddressFromCoordinates,
  getCoordinatesFromLocation,
  getEnvironmentalData,
  predictCrops,
  type CropRecommendation,
} from '../../services/cropApi';
import './CropApp.css';

type InputMode = 'name' | 'coords';

const safeNumber = (v: unknown, fallback: number) => (typeof v === 'number' && !Number.isNaN(v) ? v : fallback);

export default function EnvironmentalDetails() {
  const [mode, setMode] = useState<InputMode>('name');
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10));

  const [locationName, setLocationName] = useState('');
  const [lat, setLat] = useState<number>(19.076);
  const [lon, setLon] = useState<number>(72.8777);
  const [resolvedAddress, setResolvedAddress] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [weatherData, setWeatherData] = useState<Record<string, any> | null>(null);
  const [soilData, setSoilData] = useState<Record<string, any> | null>(null);
  const [topRecs, setTopRecs] = useState<CropRecommendation[]>([]);
  const [bestCrop, setBestCrop] = useState<CropRecommendation | null>(null);

  const effectiveLocationName = useMemo(() => {
    return mode === 'name' ? locationName.trim() : resolvedAddress.trim();
  }, [mode, locationName, resolvedAddress]);

  const handleFetchEnvironmental = async () => {
    setError(null);
    setWeatherData(null);
    setSoilData(null);
    setTopRecs([]);
    setBestCrop(null);

    setLoading(true);
    try {
      let finalLat = lat;
      let finalLon = lon;
      let finalLocationName = effectiveLocationName;

      if (mode === 'name') {
        const coordsRes = await getCoordinatesFromLocation(locationName);
        if ('error' in coordsRes) throw new Error(coordsRes.error);
        finalLat = coordsRes.data.latitude;
        finalLon = coordsRes.data.longitude;
        finalLocationName = locationName;
      } else {
        const addrRes = await getAddressFromCoordinates(lat, lon);
        if ('error' in addrRes) throw new Error(addrRes.error);
        setResolvedAddress(addrRes.data.address);
        finalLocationName = addrRes.data.address;
      }

      const envRes = await getEnvironmentalData(finalLat, finalLon, finalLocationName);
      if ('error' in envRes) throw new Error(envRes.error);

      setWeatherData(envRes.data.weather_data);
      setSoilData(envRes.data.soil_data);

      // Call crop prediction (weather may sometimes be null; use the same defaults as streamlit)
      const w = envRes.data.weather_data;
      const s = envRes.data.soil_data;

      const weather = {
        temperature: safeNumber(w.temperature, 25.0),
        humidity: safeNumber(w.humidity, 60.0),
        rainfall: safeNumber(w.rainfall, 1000.0),
      };

      const soil = {
        nitrogen: safeNumber(s.nitrogen, 45.0),
        phosphorus: safeNumber(s.phosphorus, 30.0),
        potassium: safeNumber(s.potassium, 38.0),
        ph: safeNumber(s.ph, 6.7),
      };

      const predRes = await predictCrops({ weather, soil, top_n: 5 });
      if ('error' in predRes) throw new Error(predRes.error);

      setTopRecs(predRes.data.top_recommendations);
      setBestCrop(predRes.data.best_crop);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch environmental data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="crop-page">
      <div className="crop-card">
        <div className="crop-card-title">🌤️ Environmental Weather and Soil Conditions</div>
        <div className="crop-subtitle">Pick a date, then fetch weather + soil and run crop recommendations.</div>

        <div className="crop-form-row" style={{ marginTop: 12 }}>
          <div className="crop-field" style={{ flexBasis: 280 }}>
            <label>Select date</label>
            <input
              className="crop-input"
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
            <div className="crop-helper">Date is displayed for context (weather data comes from current conditions).</div>
          </div>
        </div>

        <div className="crop-divider" />

        <div className="crop-form-row" style={{ marginTop: 12 }}>
          <div className="crop-field" style={{ flexBasis: 420 }}>
            <label>Choose input method</label>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="radio"
                  checked={mode === 'name'}
                  onChange={() => {
                    setMode('name');
                    setResolvedAddress('');
                    setWeatherData(null);
                    setSoilData(null);
                    setTopRecs([]);
                    setBestCrop(null);
                    setError(null);
                  }}
                />
                Location Name
              </label>
              <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="radio"
                  checked={mode === 'coords'}
                  onChange={() => {
                    setMode('coords');
                    setResolvedAddress('');
                    setWeatherData(null);
                    setSoilData(null);
                    setTopRecs([]);
                    setBestCrop(null);
                    setError(null);
                  }}
                />
                Coordinates
              </label>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          {mode === 'name' ? (
            <div className="crop-field">
              <label>Location name</label>
              <input
                className="crop-input"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                placeholder="e.g., Mumbai, India"
              />
            </div>
          ) : (
            <div className="crop-form-row">
              <div className="crop-field">
                <label>Latitude</label>
                <input
                  className="crop-input"
                  type="number"
                  step={0.0001}
                  value={lat}
                  onChange={(e) => setLat(Number(e.target.value))}
                />
              </div>
              <div className="crop-field">
                <label>Longitude</label>
                <input
                  className="crop-input"
                  type="number"
                  step={0.0001}
                  value={lon}
                  onChange={(e) => setLon(Number(e.target.value))}
                />
              </div>
            </div>
          )}
        </div>

        <div className="crop-actions" style={{ marginTop: 16 }}>
          <button
            className="btn btn-primary"
            onClick={handleFetchEnvironmental}
            disabled={loading || (mode === 'name' && !locationName.trim())}
          >
            {loading ? 'Fetching...' : 'Get Environmental Data'}
          </button>
        </div>

        {error && <div className="crop-inline-error">{error}</div>}

        {resolvedAddress && mode === 'coords' && (
          <div className="crop-helper" style={{ marginTop: 12 }}>
            Resolved location name: <b>{resolvedAddress}</b>
          </div>
        )}

        {weatherData && soilData && (
          <>
            <div className="crop-divider" />
            <div className="crop-card-title" style={{ marginBottom: 8 }}>
              📅 Environmental Data for {selectedDate}
            </div>

            <div className="crop-metric-grid">
              <div className="crop-metric">
                <div className="k">Temperature</div>
                <div className="v">{safeNumber(weatherData.temperature, 25)}°C</div>
              </div>
              <div className="crop-metric">
                <div className="k">Humidity</div>
                <div className="v">{safeNumber(weatherData.humidity, 60)}%</div>
              </div>
              <div className="crop-metric">
                <div className="k">Rainfall</div>
                <div className="v">{safeNumber(weatherData.rainfall, 1000)} mm</div>
              </div>
              <div className="crop-metric">
                <div className="k">Soil Health Score</div>
                <div className="v">{safeNumber(soilData.health_score, 75)}/100</div>
              </div>
            </div>

            <div className="crop-divider" />

            <div className="crop-metric-grid">
              <div className="crop-metric">
                <div className="k">Nitrogen (N)</div>
                <div className="v">{safeNumber(soilData.nitrogen, 45)} mg/kg</div>
              </div>
              <div className="crop-metric">
                <div className="k">Phosphorus (P)</div>
                <div className="v">{safeNumber(soilData.phosphorus, 30)} mg/kg</div>
              </div>
              <div className="crop-metric">
                <div className="k">Potassium (K)</div>
                <div className="v">{safeNumber(soilData.potassium, 38)} mg/kg</div>
              </div>
              <div className="crop-metric">
                <div className="k">Soil pH</div>
                <div className="v">{safeNumber(soilData.ph, 6.7)}</div>
              </div>
            </div>

            {topRecs.length > 0 && bestCrop && (
              <>
                <div className="crop-divider" />
                <div className="crop-card-title">🏆 Top 5 Crop Recommendations</div>
                <div className="crop-subtitle" style={{ marginBottom: 10 }}>
                  Generated from your weather + soil conditions.
                </div>

                <div className="crop-results">
                  {topRecs.map((r, idx) => (
                    <div key={`${r.crop_name}-${idx}`} className="crop-reco-row">
                      <div className="crop-rank">#{idx + 1}</div>
                      <div className="crop-reco-name">{r.crop_name}</div>
                      <div className="crop-confidence">{(r.confidence * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>

                <div className="crop-divider" />
                <div className="crop-card-title">📋 Best Crop Analysis</div>
                <div className="crop-helper">
                  Recommended Crop: <b>{bestCrop.crop_name}</b>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

