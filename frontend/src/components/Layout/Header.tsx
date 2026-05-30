import React from 'react';
import './Header.css';

interface HeaderProps {
  currentPath: string;
}

const getPageTitle = (path: string, userName?: string): string => {
  const titles: { [key: string]: string } = {
    '/': 'AI Crop Prediction System',
    '/location-based': 'Location-Based Crop Recommendations',
    '/environmental': 'Environmental Weather & Soil Conditions',
    '/manual-input': 'Manual Environmental Input',
    '/cost-benefit': 'Cost-Benefit Analysis Dashboard',
  };
  return titles[path] || 'AI Crop Prediction System';
};

const Header: React.FC<HeaderProps> = ({ currentPath }) => {
  const pageSubtitle: string =
    currentPath === '/'
      ? 'Get personalized crop recommendations from location, weather, and soil health.'
      : 'Use the inputs below to fetch data and generate recommendations.';

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-titles">
          <h1 className="page-title">{getPageTitle(currentPath)}</h1>
          <p className="page-subtitle">{pageSubtitle}</p>
        </div>
      </div>
    </header>
  );
};

export default Header;
