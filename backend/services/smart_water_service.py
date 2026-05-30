"""
Smart Water Management Service
Provides water requirement predictions and irrigation recommendations
"""

class SmartWaterManagement:
    def __init__(self):
        """Initialize Smart Water Management service"""
        pass
    
    def calculate_water_requirement(self, crop_type, temperature, humidity, rainfall, soil_moisture):
        """
        Calculate water requirement based on crop and environmental conditions
        
        Args:
            crop_type (str): Type of crop
            temperature (float): Temperature in Celsius
            humidity (float): Humidity percentage
            rainfall (float): Rainfall in mm
            soil_moisture (float): Soil moisture percentage
            
        Returns:
            dict: Water requirement and irrigation recommendations
        """
        # Base water requirement (mm/day) for different crops
        base_requirements = {
            'wheat': 4.0,
            'rice': 6.5,
            'maize': 5.0,
            'cotton': 5.5,
            'sugarcane': 7.0,
            'pulses': 3.5,
            'millets': 3.0,
            'vegetables': 4.5
        }
        
        # Get base requirement or default
        base_req = base_requirements.get(crop_type.lower(), 4.0)
        
        # Temperature adjustment (higher temp = more water)
        temp_factor = 1.0 + (temperature - 25) * 0.02
        
        # Humidity adjustment (lower humidity = more water)
        humidity_factor = 2.0 - (humidity / 100)
        
        # Rainfall contribution
        effective_rainfall = min(rainfall, base_req * 0.7)
        
        # Soil moisture contribution
        soil_moisture_contrib = (soil_moisture / 100) * base_req * 0.3
        
        # Calculate net water requirement
        net_requirement = max(0, base_req * temp_factor * humidity_factor - effective_rainfall - soil_moisture_contrib)
        
        # Irrigation recommendation
        if net_requirement <= 0:
            irrigation_status = "No irrigation needed"
            irrigation_amount = 0
        elif net_requirement < 2:
            irrigation_status = "Light irrigation recommended"
            irrigation_amount = net_requirement
        elif net_requirement < 4:
            irrigation_status = "Moderate irrigation recommended"
            irrigation_amount = net_requirement
        else:
            irrigation_status = "Heavy irrigation recommended"
            irrigation_amount = net_requirement
        
        return {
            'crop_type': crop_type,
            'base_requirement': base_req,
            'net_requirement': round(net_requirement, 2),
            'irrigation_status': irrigation_status,
            'irrigation_amount_mm': round(irrigation_amount, 2),
            'effective_rainfall': round(effective_rainfall, 2),
            'soil_moisture_contribution': round(soil_moisture_contrib, 2),
            'temperature_factor': round(temp_factor, 2),
            'humidity_factor': round(humidity_factor, 2)
        }
    
    def get_irrigation_schedule(self, crop_type, growth_stage, water_requirement):
        """
        Generate irrigation schedule based on crop growth stage
        
        Args:
            crop_type (str): Type of crop
            growth_stage (str): Growth stage (seedling, vegetative, flowering, maturity)
            water_requirement (float): Daily water requirement in mm
            
        Returns:
            dict: Irrigation schedule recommendations
        """
        # Growth stage multipliers
        stage_multipliers = {
            'seedling': 0.6,
            'vegetative': 0.8,
            'flowering': 1.2,
            'maturity': 0.7
        }
        
        multiplier = stage_multipliers.get(growth_stage.lower(), 1.0)
        adjusted_requirement = water_requirement * multiplier
        
        # Irrigation frequency based on requirement
        if adjusted_requirement < 2:
            frequency = "Every 3-4 days"
            duration = "30-45 minutes"
        elif adjusted_requirement < 4:
            frequency = "Every 2-3 days"
            duration = "45-60 minutes"
        else:
            frequency = "Daily or every other day"
            duration = "60-90 minutes"
        
        return {
            'growth_stage': growth_stage,
            'stage_multiplier': multiplier,
            'adjusted_requirement': round(adjusted_requirement, 2),
            'irrigation_frequency': frequency,
            'irrigation_duration': duration,
            'best_time': "Early morning (6-8 AM) or evening (5-7 PM)"
        }
    
    def assess_water_efficiency(self, irrigation_method, crop_type, field_size):
        """
        Assess water efficiency for different irrigation methods
        
        Args:
            irrigation_method (str): Irrigation method (drip, sprinkler, flood)
            crop_type (str): Type of crop
            field_size (float): Field size in hectares
            
        Returns:
            dict: Water efficiency assessment
        """
        # Efficiency percentages for different methods
        efficiency_ratings = {
            'drip': 90,
            'sprinkler': 70,
            'flood': 50
        }
        
        efficiency = efficiency_ratings.get(irrigation_method.lower(), 60)
        
        # Water loss percentage
        water_loss = 100 - efficiency
        
        # Cost implications (per hectare)
        cost_per_hectare = {
            'drip': 50000,
            'sprinkler': 25000,
            'flood': 10000
        }
        
        installation_cost = cost_per_hectare.get(irrigation_method.lower(), 20000)
        total_cost = installation_cost * field_size
        
        return {
            'irrigation_method': irrigation_method,
            'efficiency_percentage': efficiency,
            'water_loss_percentage': water_loss,
            'installation_cost_per_hectare': installation_cost,
            'total_installation_cost': total_cost,
            'water_saving_potential': f"{efficiency}% water efficiency",
            'recommendation': self._get_method_recommendation(irrigation_method, efficiency)
        }
    
    def _get_method_recommendation(self, method, efficiency):
        """Get recommendation based on irrigation method efficiency"""
        if efficiency >= 85:
            return "Excellent choice! Highly water-efficient with minimal waste."
        elif efficiency >= 70:
            return "Good option. Reasonably efficient with moderate water savings."
        else:
            return "Consider upgrading to more efficient methods to conserve water."
