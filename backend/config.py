import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the project root directory (parent of the backend folder)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Model and Dataset Paths (Structural constants)
MODEL_PATH = os.path.join(ROOT_DIR, "models", "crop_predictor.pkl")
SCALER_PATH = os.path.join(ROOT_DIR, "models", "scaler.pkl")
DATASET_PATH = os.path.join(ROOT_DIR, "data", "Crop recommendation dataset.csv")
CROP_PRODUCTION_PATH = os.path.join(ROOT_DIR, "data", "crop_production.csv")
MANDI_MODEL_PATH = os.path.join(ROOT_DIR, "models", "mandi_price_model.pkl")
MANDI_DATA_PATH = os.path.join(ROOT_DIR, "data", "commodity_price.csv")

# NOTE: API Keys and URLs are now read directly from environment variables 
# using os.getenv() in the respective service files.
