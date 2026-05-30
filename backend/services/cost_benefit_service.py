import json
import os
from typing import Dict, List, Optional
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CostBenefitAnalysis:
    """Cost-benefit analysis engine for crop recommendations"""

    def __init__(self):
        # Cost data in INR per acre for Indian farming
        self.cost_data = {
            # Input costs per acre
            'seeds': {
                'rice': 1200, 'wheat': 1000, 'maize': 800, 'cotton': 1500, 'sugarcane': 2000,
                'potato': 3000, 'tomato': 2500, 'onion': 2000, 'chilli': 1800, 'groundnut': 1600,
                'soybean': 1400, 'mustard': 1200, 'bajra': 600, 'jowar': 700, 'ragi': 800,
                'moong': 1100, 'urad': 1200, 'gram': 1300, 'peas': 1400, 'masoor': 1100
            },
            'fertilizers': {
                'rice': 3500, 'wheat': 3200, 'maize': 2800, 'cotton': 4200, 'sugarcane': 5000,
                'potato': 4000, 'tomato': 3800, 'onion': 3500, 'chilli': 3600, 'groundnut': 3400,
                'soybean': 3200, 'mustard': 3000, 'bajra': 2500, 'jowar': 2600, 'ragi': 2700,
                'moong': 2900, 'urad': 3000, 'gram': 3100, 'peas': 3200, 'masoor': 2900
            },
            'pesticides': {
                'rice': 800, 'wheat': 700, 'maize': 600, 'cotton': 1200, 'sugarcane': 1000,
                'potato': 900, 'tomato': 1100, 'onion': 800, 'chilli': 1000, 'groundnut': 700,
                'soybean': 600, 'mustard': 500, 'bajra': 400, 'jowar': 450, 'ragi': 500,
                'moong': 550, 'urad': 600, 'gram': 650, 'peas': 700, 'masoor': 550
            },
            'labor': {
                'rice': 8000, 'wheat': 7500, 'maize': 7000, 'cotton': 9000, 'sugarcane': 12000,
                'potato': 10000, 'tomato': 9500, 'onion': 9000, 'chilli': 8500, 'groundnut': 8000,
                'soybean': 7800, 'mustard': 7500, 'bajra': 6500, 'jowar': 6800, 'ragi': 7000,
                'moong': 7200, 'urad': 7400, 'gram': 7600, 'peas': 7800, 'masoor': 7200
            },
            'irrigation': {
                'rice': 3000, 'wheat': 2500, 'maize': 2000, 'cotton': 3500, 'sugarcane': 5000,
                'potato': 4000, 'tomato': 3800, 'onion': 3500, 'chilli': 3600, 'groundnut': 3200,
                'soybean': 3000, 'mustard': 2800, 'bajra': 2200, 'jowar': 2400, 'ragi': 2600,
                'moong': 2700, 'urad': 2800, 'gram': 2900, 'peas': 3000, 'masoor': 2700
            },
            'machinery': {
                'rice': 2000, 'wheat': 1800, 'maize': 1600, 'cotton': 2200, 'sugarcane': 3000,
                'potato': 2500, 'tomato': 2300, 'onion': 2100, 'chilli': 2200, 'groundnut': 2000,
                'soybean': 1900, 'mustard': 1800, 'bajra': 1500, 'jowar': 1600, 'ragi': 1700,
                'moong': 1750, 'urad': 1800, 'gram': 1850, 'peas': 1900, 'masoor': 1750
            }
        }

        # Expected yields in quintals per acre
        self.yield_data = {
            'rice': 25, 'wheat': 22, 'maize': 30, 'cotton': 8, 'sugarcane': 400,
            'potato': 150, 'tomato': 120, 'onion': 100, 'chilli': 15, 'groundnut': 12,
            'soybean': 10, 'mustard': 6, 'bajra': 15, 'jowar': 18, 'ragi': 12,
            'moong': 8, 'urad': 7, 'gram': 9, 'peas': 10, 'masoor': 8
        }

        # Average market prices in INR per quintal (approximate)
        self.price_data = {
            'rice': 2200, 'wheat': 2100, 'maize': 1800, 'cotton': 5500, 'sugarcane': 350,
            'potato': 800, 'tomato': 1200, 'onion': 1500, 'chilli': 8000, 'groundnut': 4500,
            'soybean': 3800, 'mustard': 4200, 'bajra': 1400, 'jowar': 1600, 'ragi': 2200,
            'moong': 7000, 'urad': 8500, 'gram': 4800, 'peas': 3500, 'masoor': 5200
        }

    def calculate_cost_benefit(self, crop_name: str, location: str = None, season: str = None) -> Dict:
        """Calculate detailed cost-benefit analysis for a crop"""
        crop = crop_name.lower().strip()

        # Default values if crop not found
        if crop not in self.cost_data['seeds']:
            return {
                'error': f'Cost data not available for {crop_name}',
                'total_cost': 0,
                'expected_revenue': 0,
                'net_profit': 0,
                'roi_percentage': 0,
                'break_even_yield': 0
            }

        # Calculate total costs
        costs = {
            'seeds': self.cost_data['seeds'].get(crop, 0),
            'fertilizers': self.cost_data['fertilizers'].get(crop, 0),
            'pesticides': self.cost_data['pesticides'].get(crop, 0),
            'labor': self.cost_data['labor'].get(crop, 0),
            'irrigation': self.cost_data['irrigation'].get(crop, 0),
            'machinery': self.cost_data['machinery'].get(crop, 0)
        }

        total_cost = sum(costs.values())

        # Expected yield and revenue
        expected_yield = self.yield_data.get(crop, 0)
        market_price = self.price_data.get(crop, 0)
        expected_revenue = expected_yield * market_price

        # Calculate profit and ROI
        net_profit = expected_revenue - total_cost
        roi_percentage = (net_profit / total_cost * 100) if total_cost > 0 else 0

        # Break-even analysis
        cost_per_quintal = total_cost / expected_yield if expected_yield > 0 else 0
        break_even_price = cost_per_quintal * 1.1  # 10% profit margin

        # Profitability rating
        if roi_percentage >= 50:
            rating = "Excellent"
            color = "green"
        elif roi_percentage >= 30:
            rating = "Good"
            color = "blue"
        elif roi_percentage >= 10:
            rating = "Moderate"
            color = "orange"
        elif roi_percentage >= 0:
            rating = "Low"
            color = "red"
        else:
            rating = "Loss"
            color = "red"

        return {
            'crop_name': crop_name,
            'costs_breakdown': costs,
            'total_cost': total_cost,
            'expected_yield': expected_yield,
            'market_price': market_price,
            'expected_revenue': expected_revenue,
            'net_profit': net_profit,
            'roi_percentage': roi_percentage,
            'break_even_price': break_even_price,
            'profitability_rating': rating,
            'rating_color': color,
            'insights': self._generate_insights(crop, roi_percentage, expected_yield)
        }

    def _generate_insights(self, crop: str, roi: float, yield_qtl: float) -> List[str]:
        """Generate actionable insights for the crop"""
        insights = []

        if roi > 40:
            insights.append("💰 High profitability - Consider expanding cultivation area")
        elif roi > 20:
            insights.append("✅ Good returns - Suitable for medium-scale farming")
        elif roi > 0:
            insights.append("⚠️ Moderate returns - Monitor market prices closely")
        else:
            insights.append("❌ Potential loss - Consider alternative crops or cost optimization")

        # Crop-specific insights
        if crop in ['rice', 'wheat', 'maize']:
            insights.append("🌾 Staple crop - Stable demand but price fluctuations common")
        elif crop in ['cotton', 'sugarcane']:
            insights.append("🏭 Cash crop - Higher risk but better returns if managed well")
        elif crop in ['potato', 'tomato', 'onion']:
            insights.append("🥔 Vegetable crop - Quick returns but requires good marketing")

        # Yield-based insights
        if yield_qtl > 20:
            insights.append("📈 High yield potential - Focus on quality over quantity")
        elif yield_qtl > 10:
            insights.append("📊 Moderate yield - Optimize inputs for better returns")

        return insights

    def compare_crops(self, crop_list: List[str]) -> List[Dict]:
        """Compare profitability of multiple crops"""
        results = []
        for crop in crop_list:
            analysis = self.calculate_cost_benefit(crop)
            if 'error' not in analysis:
                results.append(analysis)

        # Sort by ROI percentage
        results.sort(key=lambda x: x.get('roi_percentage', 0), reverse=True)
        return results
