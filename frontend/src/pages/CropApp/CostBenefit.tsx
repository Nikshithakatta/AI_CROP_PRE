import React, { useState } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { getCostBenefitAnalysis, type CostBenefitAnalysisResponse } from '../../services/cropApi';
import './CostBenefit.css';

const POPULAR_CROPS = [
  'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane',
  'Potato', 'Tomato', 'Onion', 'Chilli', 'Groundnut',
  'Soybean', 'Mustard', 'Bajra', 'Jowar', 'Ragi'
];

const CostBenefit: React.FC = () => {
  const [selectedCrop, setSelectedCrop] = useState<string>('');
  const [analysis, setAnalysis] = useState<CostBenefitAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleAnalyzeCrop = async () => {
    if (!selectedCrop) return;

    setLoading(true);
    setError('');

    try {
      const response = await getCostBenefitAnalysis(selectedCrop);
      if (response.error) {
        setError(response.error);
      } else {
        setAnalysis(response.data!);
      }
    } catch (err) {
      setError('Failed to analyze crop costs');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getRatingColor = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'excellent': return '#16a34a';
      case 'good': return '#2563eb';
      case 'moderate': return '#d97706';
      case 'low': return '#dc2626';
      case 'loss': return '#dc2626';
      default: return '#6b7280';
    }
  };

  // Prepare chart data
  const costBreakdownData = analysis ? Object.entries(analysis.costs_breakdown).map(([category, amount]) => ({
    category: category.charAt(0).toUpperCase() + category.slice(1),
    amount: amount,
    percentage: ((amount / analysis.total_cost) * 100).toFixed(1)
  })) : [];

  const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  return (
    <div className="cost-benefit-page">
      <div className="cost-benefit-header">
        <h2>💰 Cost-Benefit Analysis Dashboard</h2>
        <p>Analyze profitability and compare costs for different crops</p>
      </div>

      <div className="cost-benefit-controls">
        <div className="analysis-section">
          <h3>Single Crop Analysis</h3>
          <div className="input-group">
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="crop-select"
            >
              <option value="">Select a crop...</option>
              {POPULAR_CROPS.map(crop => (
                <option key={crop} value={crop}>{crop}</option>
              ))}
            </select>
            <button
              onClick={handleAnalyzeCrop}
              disabled={!selectedCrop || loading}
              className="analyze-btn"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {analysis && (
        <div className="analysis-results">
          <div className="result-header">
            <h3>{analysis.crop_name} - Cost & Profit Analysis</h3>
            <div
              className="rating-badge"
              style={{ backgroundColor: getRatingColor(analysis.profitability_rating) }}
            >
              {analysis.profitability_rating}
            </div>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <h4>Total Cost</h4>
              <div className="metric-value cost">{formatCurrency(analysis.total_cost)}</div>
            </div>

            <div className="metric-card">
              <h4>Expected Revenue</h4>
              <div className="metric-value revenue">{formatCurrency(analysis.expected_revenue)}</div>
            </div>

            <div className="metric-card">
              <h4>Net Profit</h4>
              <div className={`metric-value profit ${analysis.net_profit >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(analysis.net_profit)}
              </div>
            </div>

            <div className="metric-card">
              <h4>ROI</h4>
              <div className={`metric-value roi ${analysis.roi_percentage >= 0 ? 'positive' : 'negative'}`}>
                {analysis.roi_percentage.toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="cost-breakdown">
            <h4>Cost Breakdown (per acre)</h4>
            <div className="breakdown-content">
              <div className="breakdown-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={costBreakdownData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }) => `${category}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {costBreakdownData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="breakdown-list">
                {costBreakdownData.map((item, index) => (
                  <div key={item.category} className="breakdown-item">
                    <div className="category-info">
                      <span
                        className="color-dot"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <span className="category">{item.category}</span>
                    </div>
                    <span className="amount">{formatCurrency(item.amount)}</span>
                    <span className="percentage">({item.percentage}%)</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="insights-section">
            <h4>💡 Insights & Recommendations</h4>
            <ul className="insights-list">
              {analysis.insights.map((insight, index) => (
                <li key={index}>{insight}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default CostBenefit;