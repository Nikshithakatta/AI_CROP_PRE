"""
Retrain the crop prediction model with the correct dataset
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pickle
import os

print("="*60)
print("Retraining Crop Prediction Model")
print("="*60)

# Load the dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "data", "Crop recommendation dataset.csv")
df = pd.read_csv(dataset_path)

print(f"\n[OK] Loaded dataset with {len(df)} records")
print(f"Columns: {df.columns.tolist()}")
print(f"\nUnique crops in dataset: {df['CROPS'].nunique()}")
print(f"\nTop 10 crops:")
print(df['CROPS'].value_counts().head(10))

# Check if Capsicum exists
capsicum_count = (df['CROPS'] == 'Capsicum').sum()
print(f"\nCapsicum count in dataset: {capsicum_count}")

# Select features for prediction
feature_columns = ['SOIL_PH', 'TEMP', 'WATERREQUIRED', 'RELATIVE_HUMIDITY', 'N', 'P', 'K']

# Create feature matrix and target
X = df[feature_columns].copy()
y = df['CROPS']

# Handle missing values
X = X.fillna(X.mean())

print(f"\nFeatures being used: {feature_columns}")
print(f"Target variable: CROPS")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
print("\n[TRAIN] Training RandomForest model...")
model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    max_depth=20,
    min_samples_split=5,
    class_weight='balanced',
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)

# Evaluate the model
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n[OK] Model trained successfully!")
print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Number of crops in model: {len(model.classes_)}")

# Save the model
models_dir = os.path.join(script_dir, "models")
os.makedirs(models_dir, exist_ok=True)

# Save model and scaler together
model_data = {
    'model': model,
    'scaler': scaler,
    'feature_columns': feature_columns,
    'crop_labels': model.classes_
}

model_path = os.path.join(models_dir, "crop_predictor_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"\n[SAVE] Model saved to: {model_path}")

# Test predictions for different conditions
print("\n" + "="*60)
print("Testing Model Predictions")
print("="*60)

def test_prediction(features, description):
    feature_vector = np.array([[
        features['soil_ph'],
        features['temperature'],
        features['rainfall'],
        features['humidity'],
        features['nitrogen'],
        features['phosphorus'],
        features['potassium']
    ]])
    
    feature_vector_scaled = scaler.transform(feature_vector)
    prediction = model.predict(feature_vector_scaled)[0]
    probabilities = model.predict_proba(feature_vector_scaled)[0]
    
    top_5_idx = np.argsort(probabilities)[-5:][::-1]
    
    print(f"\n{description}:")
    print(f"Input: Temp={features['temperature']}C, Rain={features['rainfall']}mm, Humidity={features['humidity']}%")
    for i, idx in enumerate(top_5_idx[:5], 1):
        print(f"  {i}. {model.classes_[idx]}: {probabilities[idx]:.2%}")
    return prediction

# Test 1: Hot and humid (tropical)
test_1 = {'soil_ph': 6.5, 'temperature': 32, 'rainfall': 2000, 'humidity': 80, 
          'nitrogen': 85, 'phosphorus': 50, 'potassium': 55}
test_prediction(test_1, "Hot & Humid (Tropical)")

# Test 2: Cool and dry
test_2 = {'soil_ph': 6.5, 'temperature': 20, 'rainfall': 800, 'humidity': 55, 
          'nitrogen': 50, 'phosphorus': 35, 'potassium': 40}
test_prediction(test_2, "Cool & Dry (Temperate)")

# Test 3: Moderate
test_3 = {'soil_ph': 7.0, 'temperature': 25, 'rainfall': 1200, 'humidity': 70, 
          'nitrogen': 70, 'phosphorus': 45, 'potassium': 50}
test_prediction(test_3, "Moderate Conditions")

print("\n" + "="*60)
print("Model retraining complete!")
print("="*60)
