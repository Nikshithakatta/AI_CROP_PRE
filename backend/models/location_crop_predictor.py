import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
from typing import List, Tuple, Optional, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import backend.config as config

class LocationBasedCropPredictor:
    """Crop predictor based on location and historical production data"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = None
        self.crop_labels = None
        self.location_crop_data = None
        
    def load_and_preprocess_data(self, dataset_path: str = None):
        """Load and preprocess the crop production dataset"""
        try:
            # If no path provided, look in backend/data directory
            if dataset_path is None:
                dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "crop_production.csv")
            
            df = pd.read_csv(dataset_path)
            print(f"Loaded dataset with {len(df)} records")
            print(f"Columns: {list(df.columns)}")
            print(f"Unique states: {df['State_Name'].nunique()}")
            print(f"Unique crops: {df['Crop'].nunique()}")
            
            # Handle missing values
            df = df.dropna()
            
            # Calculate production per area (yield)
            df['Yield'] = df['Production'] / (df['Area'] + 1)  # +1 to avoid division by zero
            
            # Create location identifier
            df['Location'] = df['State_Name'] + '_' + df['District_Name']
            
            # Encode categorical variables
            self.label_encoder.fit(df['Crop'])
            df['Crop_Encoded'] = self.label_encoder.transform(df['Crop'])
            
            # Prepare features
            # We'll use: Area, Production, Yield, Crop_Year, Season
            # and encode State and District
            
            state_encoder = LabelEncoder()
            district_encoder = LabelEncoder()
            season_encoder = LabelEncoder()
            
            df['State_Encoded'] = state_encoder.fit_transform(df['State_Name'])
            df['District_Encoded'] = district_encoder.fit_transform(df['District_Name'])
            df['Season_Encoded'] = season_encoder.fit_transform(df['Season'])
            
            self.feature_columns = [
                'State_Encoded', 'District_Encoded', 'Crop_Year', 
                'Season_Encoded', 'Area', 'Production', 'Yield'
            ]
            
            # Store encoders for later use
            self.state_encoder = state_encoder
            self.district_encoder = district_encoder
            self.season_encoder = season_encoder
            
            X = df[self.feature_columns].copy()
            y = df['Crop_Encoded']
            
            # Store original crop names
            self.crop_labels = df['Crop'].unique()
            
            # Store location-based crop statistics
            self.location_crop_data = df.groupby(['State_Name', 'District_Name', 'Crop']).agg({
                'Production': 'mean',
                'Area': 'mean',
                'Yield': 'mean'
            }).reset_index()
            
            return X, y, df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None, None, None
    
    def train_model(self):
        """Train the location-based crop prediction model"""
        X, y, df = self.load_and_preprocess_data()
        
        if X is None or y is None:
            print("Failed to load data")
            return None
        
        # Filter out classes with very few samples (less than 2)
        class_counts = y.value_counts()
        valid_classes = class_counts[class_counts >= 2].index
        mask = y.isin(valid_classes)
        X = X[mask]
        y = y[mask]
        df = df[mask]
        
        print(f"After filtering rare crops: {len(X)} records, {len(y.unique())} crops")
        
        # Split data with stratification for better distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model with improved parameters
        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nLocation-based Model trained with accuracy: {accuracy:.4f}")
        print(f"Number of crops: {len(self.crop_labels)}")
        print(f"Number of locations: {df['Location'].nunique()}")
        
        return accuracy
    
    def get_location_based_recommendations(self, state: str, district: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get crop recommendations based on location's historical data"""
        if self.location_crop_data is None:
            return []
        
        # Filter data for the specific location
        location_data = self.location_crop_data[
            (self.location_crop_data['State_Name'].str.lower() == state.lower()) &
            (self.location_crop_data['District_Name'].str.lower() == district.lower())
        ]
        
        if location_data.empty:
            return []
        
        # Sort by production (higher production = better recommendation)
        location_data = location_data.sort_values('Production', ascending=False)
        
        # Get top N crops
        recommendations = []
        for _, row in location_data.head(top_n).iterrows():
            crop = row['Crop']
            # Calculate confidence based on production relative to max
            max_production = location_data['Production'].max()
            confidence = row['Production'] / max_production if max_production > 0 else 0.5
            recommendations.append((crop, confidence))
        
        return recommendations
    
    def predict_for_location(self, state: str, district: str, season: str = 'Kharif', 
                           area: float = 1000, year: int = 2024) -> List[Tuple[str, float]]:
        """Predict crops for a specific location"""
        if self.model is None:
            print("Model not trained. Call train_model() first.")
            return []
        
        try:
            # Encode inputs
            state_encoded = self.state_encoder.transform([state])[0]
            district_encoded = self.district_encoder.transform([district])[0]
            season_encoded = self.season_encoder.transform([season])[0]
            
            # Create feature vector
            features = np.array([[state_encoded, district_encoded, year, season_encoded, area, 0, 0]])
            features_scaled = self.scaler.transform(features)
            
            # Predict
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get top N recommendations
            top_indices = np.argsort(probabilities)[::-1][:5]
            recommendations = []
            
            for idx in top_indices:
                crop = self.label_encoder.inverse_transform([idx])[0]
                confidence = probabilities[idx]
                recommendations.append((crop, confidence))
            
            return recommendations
            
        except Exception as e:
            print(f"Error predicting for location: {e}")
            # Fallback to historical data
            return self.get_location_based_recommendations(state, district, top_n=5)
    
    def save_model(self, model_path: str = None):
        """Save the trained model"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "location_crop_predictor.pkl")
        if self.model is None:
            print("No model to save")
            return
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'state_encoder': self.state_encoder,
            'district_encoder': self.district_encoder,
            'season_encoder': self.season_encoder,
            'feature_columns': self.feature_columns,
            'crop_labels': self.crop_labels,
            'location_crop_data': self.location_crop_data
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str = None):
        """Load a trained model"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "location_crop_predictor.pkl")
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.state_encoder = model_data['state_encoder']
            self.district_encoder = model_data['district_encoder']
            self.season_encoder = model_data['season_encoder']
            self.feature_columns = model_data['feature_columns']
            self.crop_labels = model_data['crop_labels']
            self.location_crop_data = model_data['location_crop_data']
            
            print("Location-based model loaded successfully")
            return True
            
        except FileNotFoundError:
            print("Model files not found. Training new model...")
            self.train_model()
            self.save_model()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

if __name__ == "__main__":
    print("=== Training Location-Based Crop Prediction Model ===\n")
    
    predictor = LocationBasedCropPredictor()
    
    # Train the model
    accuracy = predictor.train_model()
    
    # Save the model
    predictor.save_model()
    
    # Test with some locations
    print("\n=== Testing Location-Based Predictions ===\n")
    
    test_locations = [
        ('Andhra Pradesh', 'GUNTUR'),
        ('Punjab', 'AMRITSAR'),
        ('Karnataka', 'BANGALORE RURAL'),
        ('Maharashtra', 'PUNE'),
        ('Uttar Pradesh', 'AGRA')
    ]
    
    for state, district in test_locations:
        print(f"=== {state} - {district} ===")
        recommendations = predictor.get_location_based_recommendations(state, district, top_n=5)
        
        if recommendations:
            for i, (crop, confidence) in enumerate(recommendations, 1):
                print(f"{i}. {crop}: {confidence:.2%}")
        else:
            print("No historical data found for this location")
        print()
