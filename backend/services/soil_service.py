import requests
from typing import Dict, Optional, Tuple
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import ROOT_DIR

class SoilService:
    def __init__(self):
        self.base_url = os.getenv("DATA_GOV_IN_BASE_URL")
        self.api_key = os.getenv("DATA_GOV_IN_API_KEY")
    
    def get_soil_data(self, state: str = None, district: str = None) -> Optional[Dict]:
        """Fetch soil data from data.gov.in API"""
        try:
            headers = {
                'Accept': 'application/json',
                'X-API-KEY': self.api_key
            }
            
            # For demonstration, we'll use a general soil dataset
            # In practice, you might need to find specific datasets for NPK values
            params = {
                'format': 'json',
                'limit': '10'
            }
            
            # Add location filters if provided
            if state:
                params['state'] = state
            if district:
                params['district'] = district
            
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract soil information from the response
            # Note: The actual field names may vary based on the dataset
            records = data.get('records', [])
            
            if records:
                # For demonstration, return average values or first record
                # In practice, you'd need to parse the actual dataset structure
                soil_info = {
                    'nitrogen': 50.0,  # Default values - replace with actual API response parsing
                    'phosphorus': 40.0,
                    'potassium': 30.0,
                    'ph': 6.5,
                    'soil_type': 'Loamy',
                    'organic_matter': 2.5
                }
                
                # Try to extract actual values from the first record
                first_record = records[0]
                if 'nitrogen' in first_record:
                    soil_info['nitrogen'] = float(first_record['nitrogen'])
                if 'phosphorus' in first_record:
                    soil_info['phosphorus'] = float(first_record['phosphorus'])
                if 'potassium' in first_record:
                    soil_info['potassium'] = float(first_record['potassium'])
                if 'ph' in first_record:
                    soil_info['ph'] = float(first_record['ph'])
                
                return soil_info
            else:
                # Return default soil values if no data found
                return {
                    'nitrogen': 50.0,
                    'phosphorus': 40.0,
                    'potassium': 30.0,
                    'ph': 6.5,
                    'soil_type': 'Loamy',
                    'organic_matter': 2.5
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching soil data: {e}")
            # Return default values on API failure
            return {
                'nitrogen': 50.0,
                'phosphorus': 40.0,
                'potassium': 30.0,
                'ph': 6.5,
                'soil_type': 'Loamy',
                'organic_matter': 2.5
            }
        except Exception as e:
            print(f"Error processing soil data: {e}")
            return None
