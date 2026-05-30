from backend.models.crop_predictor import CropPredictor
import pandas as pd

# Initialize the crop predictor
predictor = CropPredictor()

print('=== Crop Predictor Model Training & Evaluation ===\n')

# Train the model
print('Training model...')
accuracy = predictor.train_model()

print(f'\nFinal Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)\n')

# Load the dataset to show more details
try:
    df = pd.read_csv('backend/data/Crop recommendation dataset.csv')
    print(f'Dataset Shape: {df.shape}')
    print(f'Number of Crop Types: {df["CROPS"].nunique()}')
    print(f'Crop Types: {df["CROPS"].unique()}')
    
    print(f'\nFeature Statistics:')
    features = ['SOIL_PH', 'TEMP', 'WATERREQUIRED', 'RELATIVE_HUMIDITY', 'N', 'P', 'K']
    for feature in features:
        if feature in df.columns:
            print(f'{feature}: min={df[feature].min():.2f}, max={df[feature].max():.2f}, mean={df[feature].mean():.2f}')
    
    # Test prediction with sample data
    print(f'\n=== Sample Predictions ===')
    sample_data = [
        {'soil_ph': 6.5, 'temperature': 25.0, 'waterrequired': 1000.0, 'relative_humidity': 60.0, 'n': 50.0, 'p': 40.0, 'k': 30.0},
        {'soil_ph': 7.0, 'temperature': 30.0, 'waterrequired': 800.0, 'relative_humidity': 70.0, 'n': 60.0, 'p': 35.0, 'k': 40.0},
        {'soil_ph': 6.0, 'temperature': 22.0, 'waterrequired': 1200.0, 'relative_humidity': 55.0, 'n': 45.0, 'p': 30.0, 'k': 35.0}
    ]
    
    for i, sample in enumerate(sample_data, 1):
        recommendations = predictor.get_top_recommendations(sample, top_n=3)
        print(f'Sample {i} - Input: N={sample["n"]}, P={sample["p"]}, K={sample["k"]}, pH={sample["soil_ph"]}, Temp={sample["temperature"]}°C')
        for j, (crop, confidence) in enumerate(recommendations, 1):
            print(f'  {j}. {crop}: {confidence:.2%}')
        print()

except Exception as e:
    print(f'Error loading dataset: {e}')

print('=== Model Training Complete ===')
