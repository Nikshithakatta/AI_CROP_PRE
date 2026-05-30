import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
from typing import List, Tuple, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend.config as config


class CropPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.crop_labels = None

    def _build_feature_vector(self, features: dict) -> np.ndarray:
        """Build model input in the exact feature order expected by training."""
        return np.array([[
            features.get('soil_ph', 6.5),
            features.get('temperature', 25.0),
            features.get('rainfall', 1000.0),
            features.get('humidity', 60.0),
            features.get('nitrogen', 50.0),
            features.get('phosphorus', 40.0),
            features.get('potassium', 30.0)
        ]])

    def _recover_model(self):
        """Retrain and persist a fresh model when a stale pickle is incompatible."""
        print("Detected incompatible crop model. Retraining a compatible model...")
        self.train_model()
        self.save_model()
        
    def load_and_preprocess_data(self, dataset_path: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and preprocess the crop dataset"""
        df = pd.read_csv(dataset_path)
        
        # Select relevant features for prediction
        feature_columns = [
            'SOIL_PH', 'TEMP', 'WATERREQUIRED', 'RELATIVE_HUMIDITY', 
            'N', 'P', 'K'
        ]
        
        # Create feature matrix and target
        X = df[feature_columns].copy()
        y = df['CROPS']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Store feature columns and crop labels
        self.feature_columns = feature_columns
        self.crop_labels = y.unique()
        
        return X, y
    
    def train_model(self, dataset_path: str = None) -> float:
        """Train the crop prediction model"""
        if dataset_path is None:
            dataset_path = config.DATASET_PATH
            
        # Load and preprocess data
        X, y = self.load_and_preprocess_data(dataset_path)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            max_depth=10
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained with accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def predict_crop(self, features: dict) -> Tuple[str, float]:
        """Predict the best crop for given features"""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Prepare feature vector in the correct order
        feature_vector = self._build_feature_vector(features)

        try:
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Get prediction and probabilities
            prediction = self.model.predict(feature_vector_scaled)[0]
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        except (AttributeError, ValueError):
            # Common when loading old sklearn pickles with a newer sklearn runtime.
            self._recover_model()
            feature_vector_scaled = self.scaler.transform(feature_vector)
            prediction = self.model.predict(feature_vector_scaled)[0]
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        
        # Get probability for the predicted crop
        crop_index = np.where(self.crop_labels == prediction)[0][0]
        confidence = probabilities[crop_index]
        
        return prediction, confidence
    
    def get_top_recommendations(self, features: dict, top_n: int = 3) -> List[Tuple[str, float]]:
        """Get top N crop recommendations with confidence scores"""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Prepare feature vector
        feature_vector = self._build_feature_vector(features)

        try:
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Get probabilities
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        except (AttributeError, ValueError):
            # Auto-heal incompatible persisted models, then retry once.
            self._recover_model()
            feature_vector_scaled = self.scaler.transform(feature_vector)
            probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        
        # Get top N recommendations
        top_indices = np.argsort(probabilities)[::-1][:top_n]
        recommendations = []
        
        for idx in top_indices:
            crop = self.crop_labels[idx]
            confidence = probabilities[idx]
            recommendations.append((crop, confidence))
        
        return recommendations
    
    def save_model(self, model_path: str = None):
        """Save the trained model and scaler to a single file"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "crop_predictor_model.pkl")
            
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model, scaler, and crop labels together
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'crop_labels': self.crop_labels
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
            
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str = None):
        """Load a trained model and scaler from single file"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "crop_predictor_model.pkl")
            
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.crop_labels = model_data['crop_labels']
            
            print("Model and scaler loaded successfully")
            return True
            
        except FileNotFoundError:
            print("Model file not found. Training new model...")
            self.train_model()
            self.save_model()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
