import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_glof_dataset(n_samples=1000, seed=42):
    """
    Generates a realistic synthetic dataset for GLOF outburst risk prediction.
    Features:
      1. rainfall_24h (mm)
      2. temp_c (Degrees Celsius)
      3. water_level_m (Meters)
      4. lake_area_sqkm (Square kilometers)
      5. level_rise_rate (Meters per day)
    Target Label:
      0 = NORMAL, 1 = MODERATE, 2 = CRITICAL
    """
    np.random.seed(seed)
    
    rainfall_24h = np.random.uniform(5.0, 120.0, n_samples)
    temp_c = np.random.uniform(2.0, 30.0, n_samples)
    water_level_m = np.random.uniform(5.0, 25.0, n_samples)
    lake_area_sqkm = np.random.uniform(0.5, 5.0, n_samples)
    level_rise_rate = np.random.uniform(0.0, 2.5, n_samples)

    targets = []
    for r, t, w, a, rate in zip(rainfall_24h, temp_c, water_level_m, lake_area_sqkm, level_rise_rate):
        score = (r * 0.4) + (t * 1.2) + (w * 1.5) + (a * 4.0) + (rate * 25.0)
        if score >= 85:
            targets.append(2) # CRITICAL
        elif score >= 50:
            targets.append(1) # MODERATE
        else:
            targets.append(0) # NORMAL

    df = pd.DataFrame({
        'rainfall_24h': rainfall_24h,
        'temp_c': temp_c,
        'water_level_m': water_level_m,
        'lake_area_sqkm': lake_area_sqkm,
        'level_rise_rate': level_rise_rate,
        'target': targets
    })
    return df

def train_and_save_model():
    """
    Trains RandomForestClassifier model and exports glof_model.pkl.
    """
    print("[ML Training] Generating synthetic GLOF dataset...")
    df = generate_synthetic_glof_dataset()
    
    X = df[['rainfall_24h', 'temp_c', 'water_level_m', 'lake_area_sqkm', 'level_rise_rate']]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[ML Training] Model trained successfully! Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=["NORMAL", "MODERATE", "CRITICAL"]))
    
    model_path = os.path.join(os.path.dirname(__file__), "glof_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
        
    print(f"[ML Training] Saved model artifact to {model_path}")
    return acc

if __name__ == "__main__":
    train_and_save_model()
