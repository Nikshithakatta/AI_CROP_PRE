import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
from typing import List, Dict, Any, Optional
import backend.config as config

class MandiPriceModel:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.feature_columns = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade', 'Arrival_Month']
        self.target_column = 'Modal Price'
        self.model_path = config.MANDI_MODEL_PATH

    def _preprocess_data(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """Preprocess categorical and temporal data."""
        processed_df = df.copy()
        
        # Cleanup column names first
        processed_df.columns = [col.replace("_x0020_", " ") for col in processed_df.columns]
        
        # Extract Month from Arrival Date (assuming format DD/MM/YYYY)
        if 'Arrival Date' in processed_df.columns:
            processed_df['Arrival Date'] = pd.to_datetime(processed_df['Arrival Date'], format='%d/%m/%Y', errors='coerce')
            processed_df['Arrival_Month'] = processed_df['Arrival Date'].dt.month.fillna(1).astype(int)
        else:
            processed_df['Arrival_Month'] = 1

        # categorical columns to encode
        cat_cols = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade']
        
        for col in cat_cols:
            if col not in processed_df.columns:
                processed_df[col] = "Unknown"
            
            if is_training:
                le = LabelEncoder()
                processed_df[col] = le.fit_transform(processed_df[col].astype(str))
                self.encoders[col] = le
            else:
                if col in self.encoders:
                    le = self.encoders[col]
                    # Handle unknown labels during prediction by mapping to a default (0)
                    processed_df[col] = processed_df[col].astype(str).map(
                        lambda x: le.transform([x])[0] if x in le.classes_ else 0
                    )
                else:
                    processed_df[col] = 0
                    
        return processed_df

    def train(self, dataset_path: str) -> Dict[str, float]:
        """Train the Random Forest model on the provided dataset."""
        df = pd.read_csv(dataset_path)
        processed_df = self._preprocess_data(df, is_training=True)
        
        X = processed_df[self.feature_columns]
        y = processed_df[self.target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluation
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        self.save_model()
        
        return {"mae": float(mae), "r2": float(r2)}

    def predict(self, input_data: List[Dict[str, Any]]) -> List[float]:
        """Predict prices for a list of market/commodity records."""
        if self.model is None:
            if not self.load_model():
                return [0.0] * len(input_data)
        
        df = pd.DataFrame(input_data)
        # Rename keys to match expected dataset columns for preprocessing
        rename_map = {
            "state": "State",
            "district": "District",
            "market": "Market",
            "commodity": "Commodity",
            "variety": "Variety",
            "grade": "Grade",
            "arrival_date": "Arrival Date"
        }
        df = df.rename(columns=rename_map)
        
        processed_df = self._preprocess_data(df, is_training=False)
        X = processed_df[self.feature_columns]
        
        predictions = self.model.predict(X)
        return predictions.tolist()

    def save_model(self):
        """Save model and encoders to disk."""
        data = {
            "model": self.model,
            "encoders": self.encoders
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"MandiPriceModel saved to {self.model_path}")

    def load_model(self) -> bool:
        """Load model and encoders from disk."""
        if not os.path.exists(self.model_path):
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.encoders = data["encoders"]
            print(f"MandiPriceModel loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"Error loading MandiPriceModel: {e}")
            return False
