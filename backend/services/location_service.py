from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from typing import Tuple, Optional
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import ROOT_DIR

class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent=os.getenv("GEOPY_USER_AGENT"))
    
    def get_coordinates_from_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude from location name"""
        try:
            location = self.geolocator.geocode(location_name)
            if location:
                return (location.latitude, location.longitude)
            return None
        except (GeocoderTimedOut, GeocoderServiceError):
            time.sleep(1)
            try:
                location = self.geolocator.geocode(location_name)
                if location:
                    return (location.latitude, location.longitude)
                return None
            except:
                return None
    
    def get_location_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """Get location name from latitude and longitude"""
        try:
            location = self.geolocator.reverse((lat, lon))
            if location:
                return location.address
            return None
        except (GeocoderTimedOut, GeocoderServiceError):
            time.sleep(1)
            try:
                location = self.geolocator.reverse((lat, lon))
                if location:
                    return location.address
                return None
            except:
                return None
