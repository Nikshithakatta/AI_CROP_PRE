import json
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DiseasePestPredictor:
    """AI Disease and Pest Prediction based on weather and crop conditions"""

    def __init__(self):
        # Disease and pest database based on common Indian crop diseases
        self.disease_database = {
            'rice': {
                'blast': {
                    'conditions': {'temperature': (20, 30), 'humidity': (80, 100), 'rainfall': (100, 300)},
                    'risk_level': 'high',
                    'symptoms': 'Diamond-shaped lesions on leaves',
                    'prevention': 'Use resistant varieties, avoid excessive nitrogen'
                },
                'brown_spot': {
                    'conditions': {'temperature': (20, 28), 'humidity': (70, 90), 'rainfall': (50, 200)},
                    'risk_level': 'medium',
                    'symptoms': 'Brown spots with yellow halos',
                    'prevention': 'Balanced fertilization, field sanitation'
                },
                'bacterial_blight': {
                    'conditions': {'temperature': (25, 35), 'humidity': (85, 100), 'rainfall': (150, 400)},
                    'risk_level': 'high',
                    'symptoms': 'Water-soaked lesions turning yellow',
                    'prevention': 'Use certified seeds, avoid water stress'
                }
            },
            'wheat': {
                'rust': {
                    'conditions': {'temperature': (15, 25), 'humidity': (60, 80), 'rainfall': (50, 150)},
                    'risk_level': 'high',
                    'symptoms': 'Orange to reddish-brown pustules',
                    'prevention': 'Use resistant varieties, crop rotation'
                },
                'powdery_mildew': {
                    'conditions': {'temperature': (18, 25), 'humidity': (70, 90), 'rainfall': (30, 100)},
                    'risk_level': 'medium',
                    'symptoms': 'White powdery coating on leaves',
                    'prevention': 'Avoid dense planting, ensure air circulation'
                }
            },
            'cotton': {
                'bollworm': {
                    'conditions': {'temperature': (25, 35), 'humidity': (50, 80), 'rainfall': (50, 200)},
                    'risk_level': 'high',
                    'symptoms': 'Holes in leaves and bolls',
                    'prevention': 'Use BT cotton, biological control agents'
                },
                'leaf_curl': {
                    'conditions': {'temperature': (25, 35), 'humidity': (60, 90), 'rainfall': (30, 150)},
                    'risk_level': 'medium',
                    'symptoms': 'Curling and yellowing of leaves',
                    'prevention': 'Use resistant varieties, control whiteflies'
                }
            },
            'potato': {
                'late_blight': {
                    'conditions': {'temperature': (15, 22), 'humidity': (85, 100), 'rainfall': (100, 300)},
                    'risk_level': 'high',
                    'symptoms': 'Dark lesions on leaves and tubers',
                    'prevention': 'Avoid overhead irrigation, use fungicides'
                },
                'early_blight': {
                    'conditions': {'temperature': (20, 28), 'humidity': (70, 90), 'rainfall': (50, 150)},
                    'risk_level': 'medium',
                    'symptoms': 'Dark spots with concentric rings',
                    'prevention': 'Crop rotation, fungicide application'
                }
            },
            'tomato': {
                'blight': {
                    'conditions': {'temperature': (18, 25), 'humidity': (85, 100), 'rainfall': (100, 250)},
                    'risk_level': 'high',
                    'symptoms': 'Brown spots on leaves and fruits',
                    'prevention': 'Mulching, proper spacing, fungicides'
                },
                'fruit_rot': {
                    'conditions': {'temperature': (20, 30), 'humidity': (80, 95), 'rainfall': (80, 200)},
                    'risk_level': 'medium',
                    'symptoms': 'Soft, watery spots on fruits',
                    'prevention': 'Avoid wetting fruits, improve drainage'
                }
            }
        }

        # Pest database
        self.pest_database = {
            'rice': ['stem_borer', 'brown_plant_hopper', 'rice_hispa'],
            'wheat': ['wheat_aphid', 'wheat_thrips', 'army_worm'],
            'cotton': ['pink_bollworm', 'american_bollworm', 'whitefly'],
            'potato': ['potato_tuber_moth', 'aphids', 'cutworms'],
            'tomato': ['fruit_borer', 'aphids', 'whitefly'],
            'maize': ['stem_borer', 'fall_armyworm', 'corn_borer'],
            'sugarcane': ['borers', 'scales', 'mealybugs']
        }

    def predict_disease_risk(self, crop: str, weather_data: Dict) -> List[Dict]:
        """Predict disease risk based on crop and weather conditions"""
        crop = crop.lower().strip()

        if crop not in self.disease_database:
            return [{
                'disease': 'Unknown',
                'risk_level': 'low',
                'confidence': 0,
                'message': f'No disease data available for {crop}'
            }]

        predictions = []
        diseases = self.disease_database[crop]

        for disease_name, disease_info in diseases.items():
            risk_score = self._calculate_risk_score(weather_data, disease_info['conditions'])

            # Determine risk level based on score
            if risk_score >= 80:
                final_risk = 'high'
                confidence = 90
            elif risk_score >= 60:
                final_risk = 'medium'
                confidence = 75
            else:
                final_risk = 'low'
                confidence = 60

            predictions.append({
                'disease': disease_name.replace('_', ' ').title(),
                'risk_level': final_risk,
                'confidence': confidence,
                'risk_score': risk_score,
                'symptoms': disease_info['symptoms'],
                'prevention': disease_info['prevention'],
                'conditions': disease_info['conditions']
            })

        # Sort by risk score descending
        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        return predictions[:3]  # Return top 3 risks

    def predict_pest_risk(self, crop: str, weather_data: Dict) -> List[Dict]:
        """Predict pest risk based on crop and weather conditions"""
        crop = crop.lower().strip()

        if crop not in self.pest_database:
            return [{
                'pest': 'Unknown',
                'risk_level': 'low',
                'message': f'No pest data available for {crop}'
            }]

        pests = self.pest_database[crop]
        predictions = []

        for pest in pests:
            # Calculate risk based on weather conditions favorable for pests
            temperature = weather_data.get('temperature', 25)
            humidity = weather_data.get('humidity', 70)
            rainfall = weather_data.get('rainfall', 100)

            # General pest risk calculation
            risk_score = 0

            # Temperature factor
            if 20 <= temperature <= 35:
                risk_score += 40
            elif 15 <= temperature <= 40:
                risk_score += 20

            # Humidity factor (most pests thrive in moderate to high humidity)
            if 60 <= humidity <= 90:
                risk_score += 35
            elif 40 <= humidity <= 95:
                risk_score += 15

            # Rainfall factor
            if 50 <= rainfall <= 200:
                risk_score += 25

            # Determine final risk
            if risk_score >= 80:
                risk_level = 'high'
                confidence = 85
            elif risk_score >= 60:
                risk_level = 'medium'
                confidence = 70
            else:
                risk_level = 'low'
                confidence = 55

            predictions.append({
                'pest': pest.replace('_', ' ').title(),
                'risk_level': risk_level,
                'confidence': confidence,
                'risk_score': risk_score
            })

        # Sort by risk score
        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        return predictions[:3]

    def _calculate_risk_score(self, weather_data: Dict, disease_conditions: Dict) -> float:
        """Calculate risk score based on how well weather matches disease conditions"""
        temperature = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 70)
        rainfall = weather_data.get('rainfall', 100)

        temp_range = disease_conditions.get('temperature', (20, 30))
        humidity_range = disease_conditions.get('humidity', (70, 90))
        rainfall_range = disease_conditions.get('rainfall', (50, 200))

        # Calculate how well each condition matches (0-100 scale)
        temp_match = self._range_match(temperature, temp_range)
        humidity_match = self._range_match(humidity, humidity_range)
        rainfall_match = self._range_match(rainfall, rainfall_range)

        # Weighted average (temperature most important)
        risk_score = (temp_match * 0.4) + (humidity_match * 0.4) + (rainfall_match * 0.2)

        return risk_score

    def _range_match(self, value: float, range_tuple: tuple) -> float:
        """Calculate how well a value fits within a range (0-100)"""
        min_val, max_val = range_tuple

        if min_val <= value <= max_val:
            return 100  # Perfect match
        elif value < min_val:
            # Below range - score decreases as we get further away
            distance = min_val - value
            return max(0, 100 - (distance * 5))  # Lose 5 points per unit below
        else:
            # Above range - score decreases as we get further away
            distance = value - max_val
            return max(0, 100 - (distance * 5))  # Lose 5 points per unit above

    def get_preventive_measures(self, crop: str, top_risks: List[Dict]) -> List[str]:
        """Get comprehensive preventive measures for top risks"""
        measures = []

        # General preventive measures for the crop
        general_measures = {
            'rice': [
                'Use certified seeds from reliable sources',
                'Maintain proper field drainage',
                'Practice crop rotation with non-rice crops',
                'Monitor fields regularly for early symptoms',
                'Apply balanced fertilizers to avoid excessive nitrogen'
            ],
            'wheat': [
                'Use disease-resistant varieties',
                'Practice proper seed treatment',
                'Maintain field sanitation',
                'Avoid water stagnation',
                'Implement proper crop rotation'
            ],
            'cotton': [
                'Use BT cotton varieties',
                'Implement integrated pest management',
                'Maintain proper plant spacing',
                'Regular field monitoring',
                'Use pheromone traps for pest monitoring'
            ]
        }

        # Add crop-specific measures
        if crop in general_measures:
            measures.extend(general_measures[crop][:3])  # Top 3 general measures

        # Add specific measures for top risks
        for risk in top_risks[:2]:  # Top 2 risks
            if 'prevention' in risk:
                measures.append(f"For {risk['disease']}: {risk['prevention']}")

        return list(set(measures))  # Remove duplicates
