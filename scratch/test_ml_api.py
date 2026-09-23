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
from predictor import predictor

class TestMLApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        model_loader.load()
        predictor.initialize_explainer()
        cls.client = TestClient(app)

    def test_01_root_info(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("Mental_Health_Impact", data["target"])

    def test_02_health_check(self):
        response = self.client.get("/api/ml/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["connected"])
        self.assertTrue(data["model_loaded"])
        self.assertEqual(data["feature_count"], 54)
        self.assertEqual(data["target_classes"], ["Not at all", "Slightly", "Moderately", "Severely"])

    def test_03_valid_prediction(self):
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
        response = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn(data["prediction"]["class"], ["Not at all", "Slightly", "Moderately", "Severely"])
        self.assertEqual(len(data["prediction"]["probabilities"]), 4)
        prob_sum = sum(data["prediction"]["probabilities"].values())
        self.assertAlmostEqual(prob_sum, 1.0, places=1)
        self.assertGreater(len(data["explanation"]["top_features"]), 0)
        self.assertIn("analytical result", data["disclaimer"])

    def test_04_missing_assessment_fails(self):
        response = self.client.post("/api/ml/predict", json={"assessment": {}})
        self.assertEqual(response.status_code, 400)

    def test_05_invalid_json_fails(self):
        response = self.client.post("/api/ml/predict", json={})
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
