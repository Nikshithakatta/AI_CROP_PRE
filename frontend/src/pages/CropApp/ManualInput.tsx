import React, { useState } from 'react';
import { predictCrops, type CropRecommendation } from '../../services/cropApi';
import './CropApp.css';

const DEFAULTS = {
  temperature: 25.0,
  humidity: 60.0,
  rainfall: 1000.0,
  nitrogen: 50.0,
  phosphorus: 30.0,
  potassium: 40.0,
  ph: 6.5,
};

export default function ManualInput() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [temperature, setTemperature] = useState<number>(DEFAULTS.temperature);
  const [humidity, setHumidity] = useState<number>(DEFAULTS.humidity);
  const [rainfall, setRainfall] = useState<number>(DEFAULTS.rainfall);

  const [nitrogen, setNitrogen] = useState<number>(DEFAULTS.nitrogen);
  const [phosphorus, setPhosphorus] = useState<number>(DEFAULTS.phosphorus);
  const [potassium, setPotassium] = useState<number>(DEFAULTS.potassium);
  const [ph, setPh] = useState<number>(DEFAULTS.ph);

  const [topRecs, setTopRecs] = useState<CropRecommendation[]>([]);
  const [bestCrop, setBestCrop] = useState<CropRecommendation | null>(null);

  const handlePredict = async () => {
    setError(null);
    setLoading(true);
    setTopRecs([]);
    setBestCrop(null);

    try {
      const res = await predictCrops({
        weather: { temperature, humidity, rainfall },
        soil: { nitrogen, phosphorus, potassium, ph },
        top_n: 5,
      });

      if ('error' in res) throw new Error(res.error);

      setTopRecs(res.data.top_recommendations);
      setBestCrop(res.data.best_crop);
    } catch (e: any) {
      setError(e?.message || 'Failed to predict crops');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="crop-page">
      <div className="crop-card">
        <div className="crop-card-title">📝 Enter Custom Environmental Values</div>
        <div className="crop-subtitle">Adjust values and generate crop recommendations instantly.</div>

        <div className="crop-divider" />

        <div className="crop-form-row">
          <div className="crop-field">
            <label>Temperature (°C)</label>
            <input
              className="crop-input"
              type="number"
              step={0.5}
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
            />
          </div>
          <div className="crop-field">
            <label>Humidity (%)</label>
            <input
              className="crop-input"
              type="number"
              step={1}
              value={humidity}
              onChange={(e) => setHumidity(Number(e.target.value))}
            />
          </div>
          <div className="crop-field">
            <label>Rainfall (mm)</label>
            <input
              className="crop-input"
              type="number"
              step={10}
              value={rainfall}
              onChange={(e) => setRainfall(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="crop-divider" />

        <div className="crop-form-row">
          <div className="crop-field">
            <label>Nitrogen (N) mg/kg</label>
            <input
              className="crop-input"
              type="number"
              step={1}
              value={nitrogen}
              onChange={(e) => setNitrogen(Number(e.target.value))}
            />
          </div>
          <div className="crop-field">
            <label>Phosphorus (P) mg/kg</label>
            <input
              className="crop-input"
              type="number"
              step={1}
              value={phosphorus}
              onChange={(e) => setPhosphorus(Number(e.target.value))}
            />
          </div>
          <div className="crop-field">
            <label>Potassium (K) mg/kg</label>
            <input
              className="crop-input"
              type="number"
              step={1}
              value={potassium}
              onChange={(e) => setPotassium(Number(e.target.value))}
            />
          </div>
          <div className="crop-field">
            <label>Soil pH</label>
            <input
              className="crop-input"
              type="number"
              step={0.1}
              value={ph}
              onChange={(e) => setPh(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="crop-actions" style={{ marginTop: 16 }}>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>
            {loading ? 'Predicting...' : '🚀 Predict Crops'}
          </button>
        </div>

        {error && <div className="crop-inline-error">{error}</div>}

        {topRecs.length > 0 && bestCrop && (
          <>
            <div className="crop-divider" />
            <div className="crop-card-title">🏆 Top 5 Crop Recommendations</div>
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
      </div>
    </div>
  );
}

