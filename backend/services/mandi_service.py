import os
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.models.mandi_price_model import MandiPriceModel
import backend.config as config

class MandiService:
    def __init__(self):
        self.data_path = config.MANDI_DATA_PATH
        self.df = None
        self.model = MandiPriceModel()
        self._load_data()
        # Attempt to load existing model
        self.model.load_model()

    def _load_data(self):
        """Load and prep the commodity price dataset."""
        try:
            if os.path.exists(self.data_path):
                self.df = pd.read_csv(self.data_path)
                # Cleanup column names if they have weird characters like _x0020_
                self.df.columns = [col.replace("_x0020_", " ") for col in self.df.columns]
                print(f"MandiService: Loaded {len(self.df)} records from {self.data_path}")
            else:
                print(f"MandiService: Data file not found at {self.data_path}")
        except Exception as e:
            print(f"MandiService: Error loading data: {e}")

    def get_commodities(self) -> List[str]:
        """Return a unique list of commodities available in the dataset."""
        if self.df is None:
            return []
        return sorted(self.df['Commodity'].unique().tolist())

    def get_prices_by_commodity(self, commodity: str) -> List[Dict[str, Any]]:
        """Fetch all mandi prices for a specific commodity along with AI predictions."""
        if self.df is None or not commodity:
            return []
        
        filtered_df = self.df[self.df['Commodity'] == commodity]
        if filtered_df.empty:
            # Fallback to search if exact match fails
            filtered_df = self.df[self.df['Commodity'].str.contains(commodity, case=False, na=False)]
        
        if filtered_df.empty:
            return []

        # Convert to list of dicts
        results = []
        raw_rows = []
        for _, row in filtered_df.iterrows():
            record = {
                "state": row.get("State", "N/A"),
                "district": row.get("District", "N/A"),
                "market": row.get("Market", "N/A"),
                "commodity": row.get("Commodity", "N/A"),
                "variety": row.get("Variety", "N/A"),
                "grade": row.get("Grade", "N/A"),
                "arrival_date": row.get("Arrival Date", "N/A"),
                "min_price": float(row.get("Min Price", 0)),
                "max_price": float(row.get("Max Price", 0)),
                "modal_price": float(row.get("Modal Price", 0))
            }
            results.append(record)
            raw_rows.append(record)
        
        # Add AI Predictions if the model is loaded
        if self.model.model is not None:
            try:
                predictions = self.model.predict(raw_rows)
                for i in range(len(results)):
                    results[i]["predicted_price"] = round(float(predictions[i]), 2)
            except Exception as e:
                print(f"MandiService: Prediction error: {e}")

        # Sort by state then district then market
        results.sort(key=lambda x: (x['state'], x['district'], x['market']))
        return results

    def retrain_model(self) -> Dict[str, float]:
        """Retrain the Mandi price prediction model."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("Dataset not found for retraining.")
        
        metrics = self.model.train(self.data_path)
        return metrics
