import os
import sys
import json
import logging
import joblib

# Ensure project root is in sys.path so pickled custom preprocessor class can be resolved
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from models.preprocessor import SurveyFeaturePreprocessor
except ImportError:
    pass

logger = logging.getLogger("mindsafe.ml_api.model_loader")

class ModelLoader:
    """
    Singleton Loader for MindSafe Primary ML Model and Fitted Preprocessor.
    Loads models ONCE at application initialization.
    Validates file integrity and ensures zero silent fallback.
    """
    _instance = None
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.is_loaded = False
        self.model_path = os.path.join(PROJECT_ROOT, "models", "mindsafe_primary_model.joblib")
        self.preprocessor_path = os.path.join(PROJECT_ROOT, "models", "mindsafe_primary_preprocessor.joblib")
        self.metadata_path = os.path.join(PROJECT_ROOT, "models", "model_metadata.json")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        """Loads model, preprocessor, and metadata from disk once."""
        if self.is_loaded:
            return

        logger.info("Initializing MindSafe Primary ML Model artifacts...")

        # 1. Verify file existence
        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(
                f"MindSafe Primary Model file not found at: {self.model_path}. "
                "Ensure Phase 3 artifacts exist in the models/ directory."
            )
        if not os.path.isfile(self.preprocessor_path):
            raise FileNotFoundError(
                f"MindSafe Primary Preprocessor file not found at: {self.preprocessor_path}. "
                "Ensure Phase 3 artifacts exist in the models/ directory."
            )

        # 2. Load model metadata
        if os.path.isfile(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read model metadata JSON: {e}")
                self.metadata = {}

        # 3. Load preprocessor and model via joblib
        try:
            self.preprocessor = joblib.load(self.preprocessor_path)
            logger.info("Successfully loaded primary survey feature preprocessor.")
        except Exception as e:
            raise RuntimeError(f"Critical failure loading preprocessor pipeline: {e}")

        try:
            self.model = joblib.load(self.model_path)
            logger.info("Successfully loaded primary Random Forest model.")
        except Exception as e:
            raise RuntimeError(f"Critical failure loading primary ML model: {e}")

        # 4. Verify model attributes
        if not hasattr(self.model, "predict") or not hasattr(self.model, "predict_proba"):
            raise ValueError("Loaded model object does not implement required scikit-learn classifier API.")

        self.is_loaded = True
        logger.info(
            f"MindSafe Primary Model loaded successfully. "
            f"Feature count: {len(getattr(self.preprocessor, 'feature_names_', []))}, "
            f"Target classes: {self.metadata.get('target_classes', ['Not at all', 'Slightly', 'Moderately', 'Severely'])}"
        )

model_loader = ModelLoader.get_instance()
