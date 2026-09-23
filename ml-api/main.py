import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from .model_loader import model_loader
    from .predictor import predictor, TARGET_CLASSES
    from .schemas import PredictRequest, PredictResponse, HealthResponse
except (ImportError, ValueError):
    from model_loader import model_loader
    from predictor import predictor, TARGET_CLASSES
    from schemas import PredictRequest, PredictResponse, HealthResponse

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mindsafe.ml_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan: Load primary model, preprocessor, and SHAP explainer ONCE.
    Fails fast if model artifacts cannot be securely loaded.
    """
    logger.info("Initializing MindSafe ML API Service...")
    try:
        model_loader.load()
        predictor.initialize_explainer()
        logger.info("MindSafe ML API Service ready for inference.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to initialize ML model artifacts: {e}", exc_info=True)
        raise e
    yield
    logger.info("Shutting down MindSafe ML API Service.")

app = FastAPI(
    title="MindSafe ML Prediction & Explainability API",
    description="Dedicated Machine Learning and SHAP Inference Service for MindSafe Cyberbullying Research Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Read allowed origins from environment variable, fall back to safe localhost origins
allowed_origins_env = os.environ.get("CORS_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/", tags=["Info"])
async def root_info():
    return {
        "service": "MindSafe ML Prediction & Explainability API",
        "status": "online",
        "model": "Random Forest Classifier (Scenario B — Leakage-Controlled)",
        "target": "Mental_Health_Impact",
        "classes": TARGET_CLASSES
    }

@app.get("/api/ml/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Returns the real-time operational status of the ML model and preprocessor pipelines.
    """
    if not model_loader.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is not loaded."
        )

    metadata = model_loader.metadata
    test_metrics = metadata.get("test_metrics", {
        "Accuracy": 0.4854,
        "Macro_F1": 0.3275,
        "Weighted_F1": 0.4177
    })
    feature_count = len(getattr(model_loader.preprocessor, "feature_names_", []))

    return HealthResponse(
        status="healthy",
        connected=True,
        model_loaded=True,
        preprocessor_loaded=True,
        model_version=metadata.get("model_name", "MindSafe Primary Multiclass Classifier"),
        target_classes=TARGET_CLASSES,
        feature_count=feature_count,
        test_metrics=test_metrics
    )

@app.post("/api/ml/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict_assessment(payload: PredictRequest):
    """
    Classifies a participant's survey responses into one of 4 Mental Health Impact classes
    and generates localized SHAP feature attribution weights.
    """
    if not payload.assessment or not isinstance(payload.assessment, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment questionnaire responses must be provided as a non-empty key-value mapping."
        )

    try:
        result = predictor.predict(payload.assessment)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except ValueError as ve:
        logger.warning(f"Validation/Preprocessing error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Inference processing failure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to analyze responses right now. Please verify questionnaire inputs and try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", app_dir=CURRENT_DIR, host="127.0.0.1", port=8000, reload=False, ws="none")
