import React, { useState, useEffect } from 'react';
import { 
  getMandiCommodities, 
  getMandiPrices, 
  MandiPriceRecord,
  retrainMandiModel
} from '../../services/cropApi';
import { Loader2, RefreshCw } from 'lucide-react';
import './CostBenefit.css';

export default function MandiPrices() {
  const [commodities, setCommodities] = useState<string[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('');
  const [analyzedCommodity, setAnalyzedCommodity] = useState<string>('');
  const [prices, setPrices] = useState<MandiPriceRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [retraining, setRetraining] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [dropdownOpen, setDropdownOpen] = useState<boolean>(false);

  useEffect(() => {
    fetchCommodities();
  }, []);

  const fetchCommodities = async () => {
    const res = await getMandiCommodities();
    if (res.data) {
      setCommodities(res.data);
    } else if (res.error) {
      setError(res.error);
    }
  };

  const handleSelectCommodity = (commodity: string) => {
    setSelectedCommodity(commodity);
    setDropdownOpen(false);
  };

  const fetchAnalysis = async (commodity: string) => {
    setLoading(true);
    setError(null);
    const res = await getMandiPrices(commodity);
    if (res.data) {
      setPrices(res.data.prices);
      setAnalyzedCommodity(commodity);
    } else if (res.error) {
      setError(res.error);
      setPrices([]);
      setAnalyzedCommodity('');
    }
    setLoading(false);
  };

  const handleAnalyzeCommodity = async () => {
    if (!selectedCommodity) {
      setError('Please select a commodity first.');
      return;
    }
    await fetchAnalysis(selectedCommodity);
  };

  const handleRetrain = async () => {
    setRetraining(true);
    setError(null);
    const res = await retrainMandiModel();
    if (res.data) {
      alert(`Model retrained successfully! R² Score: ${res.data.metrics.r2.toFixed(4)}`);
      // Refresh current analysis if commodity is analyzed
      if (analyzedCommodity) {
        await fetchAnalysis(analyzedCommodity);
      }
    } else if (res.error) {
      setError("Failed to retrain: " + res.error);
    }
    setRetraining(false);
  };

  return (
    <div className="cost-benefit-page">
      <div className="cost-benefit-header">
        <h2>💹 Mandi Prices (Live & AI Predicted)</h2>
        <p>Compare real-time market prices with AI predictions for better insights</p>
      </div>

      <div className="cost-benefit-controls">
        <div className="analysis-section">
          <h3>Search Commodity</h3>
          <div className="input-group" style={{ flexDirection: 'row', gap: '12px', alignItems: 'center' }}>
            <select
              value={selectedCommodity}
              onChange={(e) => handleSelectCommodity(e.target.value)}
              className="crop-select"
              style={{ flex: 1, padding: '12px', borderRadius: '10px', border: 'none', background: 'rgba(255,255,255,0.1)', color: '#fff' }}
            >
              <option value="">Select a commodity...</option>
              {commodities.map(commodity => (
                <option key={commodity} value={commodity}>{commodity}</option>
              ))}
            </select>
            <button
              onClick={handleAnalyzeCommodity}
              disabled={!selectedCommodity || loading}
              className="analyze-btn"
              style={{ padding: '12px 24px', borderRadius: '10px', border: 'none', background: '#16a34a', color: '#fff', fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' }}
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message" style={{ marginBottom: '2rem' }}>
          ❌ {error}
        </div>
      )}

      {analyzedCommodity && (
        <div className="analysis-results">
          <div className="result-header">
            <h3>📊 AI Analysis for {analyzedCommodity}</h3>
          </div>

          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <Loader2 className="animate-spin" style={{ color: '#4ade80', width: '32px', height: '32px' }} />
            </div>
          ) : prices.length > 0 ? (
            <div style={{ overflowX: 'auto', marginTop: '15px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', color: '#fff' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left' }}>
                    <th style={{ padding: '12px', fontWeight: 600 }}>Location</th>
                    <th style={{ padding: '12px', fontWeight: 600 }}>Variety</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: 600 }}>Min (₹)</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: 600 }}>Max (₹)</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: 600 }}>Actual (₹)</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: 600, color: '#4ade80' }}>AI Predicted (₹)</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600 }}>Diff</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.map((p, i) => {
                    const diff = p.predicted_price ? (p.modal_price - p.predicted_price) : 0;
                    const diffPercent = p.predicted_price ? ((diff / p.predicted_price) * 100).toFixed(1) : "0";
                    
                    return (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '12px' }}>
                          <div style={{ fontWeight: 600 }}>{p.market}</div>
                          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)' }}>{p.district}, {p.state}</div>
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px' }}>{p.variety}</td>
                        <td style={{ padding: '12px', textAlign: 'right', color: 'rgba(255,255,255,0.6)' }}>{p.min_price}</td>
                        <td style={{ padding: '12px', textAlign: 'right', color: 'rgba(255,255,255,0.6)' }}>{p.max_price}</td>
                        <td style={{ padding: '12px', textAlign: 'right', fontWeight: 800 }}>{p.modal_price}</td>
                        <td style={{ padding: '12px', textAlign: 'right', color: '#4ade80', fontWeight: 600 }}>
                          {p.predicted_price ? `₹${p.predicted_price}` : 'N/A'}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          {p.predicted_price && (
                            <span style={{ 
                              fontSize: '11px', 
                              padding: '2px 6px', 
                              borderRadius: '4px',
                              background: diff > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                              color: diff > 0 ? '#ef4444' : '#22c55e'
                            }}>
                              {diff > 0 ? '+' : ''}{diffPercent}%
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: 'rgba(255,255,255,0.4)' }}>
              No data records found.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
