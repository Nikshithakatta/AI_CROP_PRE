import requests
from typing import Dict, Optional
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import ROOT_DIR

class WeatherService:
    def __init__(self):
        self.base_url = os.getenv("OPEN_METEO_BASE_URL")
    
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch weather data from Open-Meteo API"""
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
                'hourly': 'temperature_2m,relativehumidity_2m,precipitation',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            current_weather = data.get('current_weather', {})
            hourly_data = data.get('hourly', {})
            daily_data = data.get('daily', {})
            
            weather_info = {
                'temperature': current_weather.get('temperature'),
                'humidity': hourly_data.get('relativehumidity_2m', [None])[0] if hourly_data.get('relativehumidity_2m') else None,
                'rainfall': daily_data.get('precipitation_sum', [None])[0] if daily_data.get('precipitation_sum') else None,
                'max_temperature': daily_data.get('temperature_2m_max', [None])[0] if daily_data.get('temperature_2m_max') else None,
                'min_temperature': daily_data.get('temperature_2m_min', [None])[0] if daily_data.get('temperature_2m_min') else None
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except Exception as e:
            print(f"Error processing weather data: {e}")
            return None
