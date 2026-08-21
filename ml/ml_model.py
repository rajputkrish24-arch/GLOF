import os
import pickle
import numpy as np

class GLOFMLModel:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "glof_model.pkl")
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
            except Exception as e:
                print(f"[ML Model Error] Failed to load model pickle: {e}")
                self.model = None

    def predict_risk(self, rainfall_24h, temp_c, water_level_m, lake_area_sqkm, level_rise_rate):
        """
        Takes input environmental features and returns GLOF risk prediction.
        Features vector: [rainfall_24h, temp_c, water_level_m, lake_area_sqkm, level_rise_rate]
        Returns: { "prediction": "NORMAL" | "MODERATE" | "CRITICAL", "confidence": float, "probabilities": dict }
        """
        features = np.array([[rainfall_24h, temp_c, water_level_m, lake_area_sqkm, level_rise_rate]])
        
        if self.model:
            try:
                pred_code = self.model.predict(features)[0]
                probs = self.model.predict_proba(features)[0]
                
                label_map = {0: "NORMAL", 1: "MODERATE", 2: "CRITICAL"}
                prediction = label_map.get(pred_code, "NORMAL")
                
                return {
                    "prediction": prediction,
                    "confidence": round(float(np.max(probs)) * 100, 1),
                    "probabilities": {
                        "NORMAL": round(float(probs[0]) * 100, 1) if len(probs) > 0 else 0,
                        "MODERATE": round(float(probs[1]) * 100, 1) if len(probs) > 1 else 0,
                        "CRITICAL": round(float(probs[2]) * 100, 1) if len(probs) > 2 else 0,
                    },
                    "is_ml_active": True
                }
            except Exception as e:
                print(f"[ML Prediction Error]: {e}")

        # Rule-based fallback if ML model pickle is not yet generated
        if rainfall_24h > 70 or level_rise_rate > 1.0 or water_level_m > 18.0:
            pred = "CRITICAL"
            conf = 88.5
        elif rainfall_24h > 30 or temp_c > 20 or level_rise_rate > 0.4:
            pred = "MODERATE"
            conf = 76.2
        else:
            pred = "NORMAL"
            conf = 92.0

        return {
            "prediction": pred,
            "confidence": conf,
            "probabilities": {"NORMAL": 20.0, "MODERATE": 30.0, "CRITICAL": 50.0},
            "is_ml_active": False
        }
