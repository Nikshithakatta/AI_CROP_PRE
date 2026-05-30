import React from 'react';
import { Link } from 'react-router-dom';
import './CropApp.css';

export default function CropHome() {
  return (
    <div className="crop-page">
      <div className="crop-hero">
        <h2>🌾 AI Crop Prediction System</h2>
        <p>
          Empowering agriculture with precision AI. Get personalized crop recommendations based on
          your location, real-time weather, and soil health.
        </p>

        <div className="crop-actions">
          <Link className="btn btn-primary" to="/location-based">
            Location-Based Recommendations
          </Link>
          <Link className="btn btn-primary" to="/environmental">
            Environmental Details
          </Link>
          <Link className="btn btn-primary" to="/manual-input">
            Manual Input
          </Link>
          <Link className="btn btn-primary" to="/mandi-prices">
            Mandi Prices
          </Link>
          <Link className="btn btn-primary" to="/cost-benefit">
            💰 Cost-Benefit Analysis
          </Link>
        </div>
      </div>

      <div className="crop-grid">
        <div className="crop-card">
          <div className="crop-card-title">📍 Location Services</div>
          <div className="crop-subtitle">
            Enter a place name or coordinates to power recommendations.
          </div>
        </div>
        <div className="crop-card">
          <div className="crop-card-title">🌤️ Weather + Soil</div>
          <div className="crop-subtitle">
            Pull environmental data and calculate soil health score.
          </div>
        </div>
        <div className="crop-card">
          <div className="crop-card-title">🤖 AI Predictions</div>
          <div className="crop-subtitle">
            The model outputs top crops and the best match for your conditions.
          </div>
        </div>
        <div className="crop-card">
          <div className="crop-card-title">💹 Mandi Prices</div>
          <div className="crop-subtitle">
            Real-time market prices for crops across different locations in India.
          </div>
        </div>
        <div className="crop-card">
          <div className="crop-card-title">💰 Cost-Benefit Analysis</div>
          <div className="crop-subtitle">
            Analyze profitability, ROI, and compare costs for different crops.
          </div>
        </div>
      </div>
    </div>
  );
}

