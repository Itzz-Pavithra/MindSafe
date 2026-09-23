"""
MindSafe Phase 4 Comprehensive Integration & Verification Test Suite
Tests:
1. FastAPI startup & health check
2. Primary Model & Preprocessor loading (No synthetic data, real .joblib files)
3. Valid prediction execution & probabilities
4. SHAP TreeExplainer feature attributions & non-causal language formatting
5. Missing input handling (400 validation error)
6. Invalid structure handling (422 validation error)
7. Security: Endpoint access validation & no secrets leakage
"""
import os
import sys
import unittest
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
ML_API_DIR = os.path.join(PROJECT_ROOT, "ml_api")
if ML_API_DIR not in sys.path:
    sys.path.insert(0, ML_API_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from main import app
from model_loader import model_loader
from predictor import predictor, TARGET_CLASSES

class TestPhase4Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        model_loader.load()
        predictor.initialize_explainer()
        cls.client = TestClient(app)

    def test_01_model_loading_and_attributes(self):
        """Verifies primary model and preprocessor are loaded with correct attributes."""
        self.assertTrue(model_loader.is_loaded)
        self.assertIsNotNone(model_loader.model)
        self.assertIsNotNone(model_loader.preprocessor)
        self.assertEqual(len(model_loader.preprocessor.feature_names_), 54)
        self.assertEqual(len(model_loader.model.classes_), 4)

    def test_02_health_endpoint(self):
        """Verifies GET /api/ml/health endpoint returns model metadata and status."""
        res = self.client.get("/api/ml/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["connected"])
        self.assertEqual(data["feature_count"], 54)
        self.assertEqual(data["target_classes"], TARGET_CLASSES)

    def test_03_prediction_with_actual_model(self):
        """Verifies prediction inference with actual Random Forest model and SHAP."""
        payload = {
            "assessment": {
                "age": "18–22",
                "gender": "Female",
                "platforms": ["Instagram", "WhatsApp"],
                "usage": "3–5 hours",
                "q5_exp": "Yes",
                "q6_wit": "Yes",
                "q7_post": "No",
                "q9_types": ["Offensive Comments", "Body Shaming"],
                "q10_plat": "Instagram",
                "q11_freq": "Sometimes",
                "q15_help": ["Friends", "Family"],
                "q17_area": "Social Media Community",
                "q18_act": ["Blocked the user"]
            }
        }
        res = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Prediction assertions
        self.assertTrue(data["success"])
        pred_class = data["prediction"]["class"]
        self.assertIn(pred_class, TARGET_CLASSES)
        self.assertIn(data["prediction"]["predicted_class_index"], [0, 1, 2, 3])

        # Probabilities assertions
        probs = data["prediction"]["probabilities"]
        self.assertEqual(len(probs), 4)
        for c in TARGET_CLASSES:
            self.assertIn(c, probs)
            self.assertGreaterEqual(probs[c], 0.0)
            self.assertLessEqual(probs[c], 1.0)
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=1)

        # SHAP explanation assertions
        explanation = data["explanation"]
        self.assertGreater(len(explanation["top_features"]), 0)
        for feat in explanation["top_features"]:
            self.assertIn("feature", feat)
            self.assertIn("raw_feature", feat)
            self.assertIn("shap_value", feat)
            self.assertIn("direction", feat)
            self.assertIn(feat["direction"], ["increased", "decreased"])
            # Strict non-causal language assertions
            self.assertNotIn("caused", feat["description"].lower())
            self.assertNotIn("proved", feat["description"].lower())

        # Disclaimer assertions
        self.assertIn("analytical result", data["disclaimer"].lower())
        self.assertIn("not a medical diagnosis", data["disclaimer"].lower())

    def test_04_prediction_severe_risk_profile(self):
        """Verifies prediction inference for a high-frequency harassment response."""
        payload = {
            "assessment": {
                "age": "Below 18",
                "gender": "Female",
                "platforms": "Instagram, WhatsApp, YouTube",
                "usage": "More than 5 hours",
                "q5_exp": "Yes",
                "q6_wit": "Yes",
                "q7_post": "Yes",
                "q9_types": "Threats, Stalking, Sexual Harassment",
                "q10_plat": "Instagram",
                "q11_freq": "Very Often",
                "q15_help": "No",
                "q17_area": "Social Media Community",
                "q18_act": "Took No Action"
            }
        }
        res = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn(data["prediction"]["class"], TARGET_CLASSES)
        self.assertEqual(len(data["explanation"]["top_features"]), 5)

    def test_05_missing_input_validation(self):
        """Verifies empty assessment triggers 400 validation error."""
        res = self.client.post("/api/ml/predict", json={"assessment": {}})
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("detail", data)

    def test_06_invalid_payload_format(self):
        """Verifies malformed JSON triggers 422 error."""
        res = self.client.post("/api/ml/predict", json={"wrong_key": 123})
        self.assertEqual(res.status_code, 422)

    def test_07_no_secrets_in_responses(self):
        """Verifies responses do not leak database or internal credentials."""
        res = self.client.get("/api/ml/health")
        content_str = res.text.lower()
        self.assertNotIn("mongodb", content_str)
        self.assertNotIn("password", content_str)
        self.assertNotIn("secret", content_str)

if __name__ == "__main__":
    unittest.main()
