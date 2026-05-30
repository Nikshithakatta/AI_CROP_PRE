import requests
from typing import Dict, Optional
import random
import math
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import ROOT_DIR

class EnhancedSoilService:
    def __init__(self):
        self.base_url = os.getenv("DATA_GOV_IN_BASE_URL")
        self.api_key = os.getenv("DATA_GOV_IN_API_KEY")
    
    def get_soil_data(self, lat: float = None, lon: float = None, location_name: str = None) -> Optional[Dict]:
        """
        Get soil data with fallback strategies:
        1. Try data.gov.in API
        2. Generate realistic data based on coordinates
        3. Use default values as last resort
        """
        
        # Try data.gov.in API first
        api_data = self._try_data_gov_api()
        if api_data:
            return api_data
        
        # Generate coordinate-based realistic data
        if lat and lon:
            coord_data = self._generate_coordinate_based_soil_data(lat, lon)
            return coord_data
        
        # Final fallback to default values
        return self._get_default_soil_data()
    
    def _try_data_gov_api(self) -> Optional[Dict]:
        """Try to fetch data from data.gov.in API"""
        try:
            headers = {
                'Accept': 'application/json',
                'X-API-KEY': self.api_key
            }
            
            params = {
                'format': 'json',
                'limit': '10'
            }
            
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            records = data.get('records', [])
            
            if records:
                first_record = records[0]
                soil_info = {
                    'nitrogen': float(first_record.get('nitrogen', 50.0)),
                    'phosphorus': float(first_record.get('phosphorus', 40.0)),
                    'potassium': float(first_record.get('potassium', 30.0)),
                    'ph': float(first_record.get('ph', 6.5)),
                    'soil_type': first_record.get('soil_type', 'Loamy'),
                    'organic_matter': float(first_record.get('organic_matter', 2.0))
                }
                return soil_info
                
        except Exception as e:
            print(f"Data.gov.in API failed: {e}")
            return None
    
    def _get_default_soil_data(self) -> Dict:
        """Return default soil values"""
        return {
            'nitrogen': 45.0,
            'phosphorus': 30.0,
            'potassium': 38.0,
            'ph': 6.7,
            'soil_type': 'Loamy',
            'organic_matter': 1.5
        }
    
    def _generate_coordinate_based_soil_data(self, lat: float, lon: float) -> Dict:
        """
        Generate realistic soil data based on geographic coordinates
        Uses mathematical functions to simulate soil variations by region
        """
        # Base values influenced by latitude and longitude
        lat_factor = (lat + 90) / 180  # Normalize to 0-1
        lon_factor = (lon + 180) / 360  # Normalize to 0-1
        
        # Generate realistic NPK values based on location
        # Indian subcontinent tends to have certain characteristics
        if 8 <= lat <= 37 and 68 <= lon <= 97:  # India bounds
            nitrogen = 40 + 20 * math.sin(lat_factor * math.pi) + random.uniform(-5, 5)
            phosphorus = 25 + 15 * math.cos(lon_factor * math.pi) + random.uniform(-3, 3)
            potassium = 35 + 15 * math.sin((lat_factor + lon_factor) * math.pi / 2) + random.uniform(-4, 4)
            ph = 6.0 + 2.0 * math.sin(lat_factor * math.pi) + random.uniform(-0.3, 0.3)
            organic_matter = 1.0 + 1.5 * math.cos(lon_factor * math.pi) + random.uniform(-0.2, 0.2)
        else:
            # Global default values
            nitrogen = 45 + random.uniform(-10, 15)
            phosphorus = 30 + random.uniform(-8, 12)
            potassium = 38 + random.uniform(-10, 12)
            ph = 6.5 + random.uniform(-0.5, 0.5)
            organic_matter = 1.5 + random.uniform(-0.5, 0.8)
        
        # Determine soil type based on pH and location
        if ph > 7.5:
            soil_type = 'Alkaline'
        elif ph < 6.0:
            soil_type = 'Acidic'
        elif 6.8 <= ph <= 7.2:
            soil_type = 'Neutral'
        else:
            soil_type = 'Slightly Acidic'
        
        return {
            'nitrogen': round(max(10, min(80, nitrogen)), 1),
            'phosphorus': round(max(5, min(60, phosphorus)), 1),
            'potassium': round(max(10, min(70, potassium)), 1),
            'ph': round(max(4.5, min(8.5, ph)), 1),
            'soil_type': soil_type,
            'organic_matter': round(max(0.5, min(3.5, organic_matter)), 1)
        }
    
    def get_soil_health_score(self, soil_data: Dict) -> float:
        """
        Calculate overall soil health score (0-100)
        Based on NPK levels, pH, and organic matter
        """
        n = soil_data.get('nitrogen', 45)
        p = soil_data.get('phosphorus', 30)
        k = soil_data.get('potassium', 38)
        ph = soil_data.get('ph', 6.7)
        om = soil_data.get('organic_matter', 1.5)
        
        # Optimal ranges for Indian soils
        n_score = min(100, (n / 60) * 100)  # Optimal N: 40-60 mg/kg
        p_score = min(100, (p / 40) * 100)  # Optimal P: 25-40 mg/kg
        k_score = min(100, (k / 50) * 100)  # Optimal K: 30-50 mg/kg
        ph_score = 100 - abs(ph - 6.8) * 20  # Optimal pH: 6.5-7.0
        om_score = min(100, (om / 2.5) * 100)  # Optimal OM: 1.5-2.5%
        
        overall_score = (n_score * 0.25 + p_score * 0.2 + k_score * 0.2 + 
                        ph_score * 0.2 + om_score * 0.15)
        
        return round(overall_score, 1)
