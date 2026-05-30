import React, { useMemo, useState } from 'react';
import {
  getCoordinatesFromLocation,
  getLocationBasedRecommendations,
  getAddressFromCoordinates,
  type LocationCoordinates,
  type CropRecommendation,
} from '../../services/cropApi';
import './CropApp.css';

type InputMode = 'name' | 'coords';

export default function LocationBasedRecommendations() {
  const [mode, setMode] = useState<InputMode>('name');

  const [locationName, setLocationName] = useState('');
  const [coords, setCoords] = useState<LocationCoordinates | null>(null);

  const [lat, setLat] = useState<number>(19.076);
  const [lon, setLon] = useState<number>(72.8777);
  const [resolvedAddress, setResolvedAddress] = useState<string>('');

  const [topRecs, setTopRecs] = useState<CropRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveLocationName = useMemo(() => {
    return mode === 'name' ? locationName.trim() : resolvedAddress.trim();
  }, [mode, locationName, resolvedAddress]);

  const canFetchCoordinates = mode === 'name' ? locationName.trim().length > 1 : true;
  const canFetchRecommendations = effectiveLocationName.length > 1;

  const handleGetCoordinates = async () => {
    setError(null);
    setTopRecs([]);

    if (!canFetchCoordinates) return;

    if (mode === 'name') {
      setLoading(true);
      const res = await getCoordinatesFromLocation(locationName);
      setLoading(false);

      if ('error' in res) {
        setError(res.error);
        return;
      }

      setCoords(res.data);
    } else {
      setLoading(true);
      const res = await getAddressFromCoordinates(lat, lon);
      setLoading(false);

      if ('error' in res) {
        setError(res.error);
        return;
      }
      setResolvedAddress(res.data.address);
    }
  };

  const handleGetRecommendations = async () => {
    setError(null);
    setLoading(true);

    const res = await getLocationBasedRecommendations(effectiveLocationName, 10);
    setLoading(false);

    if ('error' in res) {
      setError(res.error);
      return;
    }

    setTopRecs(res.data.top_recommendations);
  };

  return (
    <div className="crop-page">
      <div className="crop-card">
        <div className="crop-card-title">🗺️ Location-Based Crop Recommendations</div>
        <div className="crop-subtitle">
          Enter a place name or coordinates to generate crop recommendations based on historical data.
        </div>

        <div className="crop-form-row" style={{ marginBottom: 12 }}>
          <div className="crop-field">
            <label>Choose input method</label>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="radio"
                  checked={mode === 'name'}
                  onChange={() => {
                    setMode('name');
                    setCoords(null);
                    setResolvedAddress('');
                    setTopRecs([]);
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
                    setCoords(null);
                    setResolvedAddress('');
                    setTopRecs([]);
                  }}
                />
                Coordinates
              </label>
            </div>
          </div>
        </div>

        {mode === 'name' ? (
          <div className="crop-form-row">
            <div className="crop-field">
              <label>Location name (e.g., “Mumbai, India”)</label>
              <input
                className="crop-input"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                placeholder="Type a location..."
              />
              <div className="crop-helper">We’ll geocode it into coordinates, then match state/district.</div>
            </div>
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

        <div className="crop-actions" style={{ marginTop: 16 }}>
          <button
            className="btn btn-primary"
            onClick={handleGetCoordinates}
            disabled={loading || (mode === 'name' && !locationName.trim())}
          >
            {loading ? 'Processing...' : mode === 'name' ? 'Get Coordinates' : 'Get Location Name'}
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleGetRecommendations}
            disabled={loading || !canFetchRecommendations}
          >
            {loading ? 'Loading...' : 'Get Location-Based Crop Suggestions'}
          </button>
        </div>

        {error && <div className="crop-inline-error">{error}</div>}

        {(coords || resolvedAddress) && (
          <div style={{ marginTop: 14 }}>
            {coords && (
              <div className="crop-helper">
                Found coordinates: <b>{coords.latitude.toFixed(4)}</b>, <b>{coords.longitude.toFixed(4)}</b>
              </div>
            )}
            {resolvedAddress && (
              <div className="crop-helper">
                Resolved location name: <b>{resolvedAddress}</b>
              </div>
            )}
          </div>
        )}
      </div>

      {topRecs.length > 0 && (
        <div className="crop-card">
          <div className="crop-card-title">🏆 Top Recommendations</div>
          <div className="crop-subtitle">Best matching crops based on historical production.</div>

          <div className="crop-results">
            {topRecs.map((r, idx) => (
              <div key={`${r.crop_name}-${idx}`} className="crop-reco-row">
                <div className="crop-rank">#{idx + 1}</div>
                <div className="crop-reco-name">{r.crop_name}</div>
                <div className="crop-confidence">{(r.confidence * 100).toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

