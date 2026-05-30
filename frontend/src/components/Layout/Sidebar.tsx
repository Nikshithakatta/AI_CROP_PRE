import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  MapPin,
  CloudSun,
  ClipboardList,
  Banknote,
  TrendingUp
} from 'lucide-react';
import './Sidebar.css';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const navigationItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/location-based', label: 'Location-Based Crops', icon: MapPin },
  { path: '/environmental', label: 'Environmental Data', icon: CloudSun },
  { path: '/manual-input', label: 'Manual Input', icon: ClipboardList },
  { path: '/mandi-prices', label: 'Mandi Prices', icon: Banknote },
  { path: '/cost-benefit', label: 'Cost-Benefit Analysis', icon: TrendingUp },
];

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const location = useLocation();

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header" style={collapsed ? { justifyContent: "center" } : {}}>
        <div className="logo logo-clickable" onClick={onToggle} title={collapsed ? "Expand menu" : "Collapse menu"}>
          {collapsed ? (
            <span style={{ fontWeight: 800, fontSize: 14, color: 'inherit' }}>AI</span>
          ) : (
            <span style={{ fontWeight: 800, fontSize: 14, color: '#16a34a' }}>
              AI Crop Prediction
            </span>
          )}
        </div>
      </div>
      
      <nav className="sidebar-nav">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <Icon size={20} />
              {!collapsed && <span className="nav-label">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {!collapsed && (
        <div className="sidebar-footer" style={{ padding: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', color: '#16a34a', fontSize: '11px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16a34a', boxShadow: '0 0 8px #16a34a' }}></div>
            <span>System Unlocked</span>
          </div>
          <div style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: '10px', marginTop: '4px' }}>
            Key: AI_CROP_SECRET_2024
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
