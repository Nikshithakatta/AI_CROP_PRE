import React, { useEffect } from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import CropHome from './pages/CropApp/CropHome';
import LocationBasedRecommendations from './pages/CropApp/LocationBasedRecommendations';
import EnvironmentalDetails from './pages/CropApp/EnvironmentalDetails';
import ManualInput from './pages/CropApp/ManualInput';
import MandiPrices from './pages/CropApp/MandiPrices';
import CostBenefit from './pages/CropApp/CostBenefit';

export default function App() {
  useEffect(() => {
    // Setting the authorization key in Local Storage for visual verification
    localStorage.setItem('X-API-Key', 'AI_CROP_SECRET_2024');
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><CropHome /></Layout>} />
        <Route path="/location-based" element={<Layout><LocationBasedRecommendations /></Layout>} />
        <Route path="/environmental" element={<Layout><EnvironmentalDetails /></Layout>} />
        <Route path="/manual-input" element={<Layout><ManualInput /></Layout>} />
        <Route path="/mandi-prices" element={<Layout><MandiPrices /></Layout>} />
        <Route path="/cost-benefit" element={<Layout><CostBenefit /></Layout>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
