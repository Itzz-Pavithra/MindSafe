# MindSafe ML Prediction & SHAP Explainability Service

Dedicated Python + FastAPI microservice serving the trained **Random Forest Primary Multiclass Model** (`Scenario B: Leakage-Controlled`) and **Tree SHAP Local Explainability Engine** for the MindSafe platform.

## Architecture

- **Framework**: FastAPI (Asynchronous ASGI)
- **Model Engine**: Scikit-Learn `RandomForestClassifier` (100 estimators, balanced weights)
- **Explainability**: SHAP `TreeExplainer` (Tree-based additive local feature contributions)
- **Preprocessing**: Leakage-Controlled `SurveyFeaturePreprocessor` (54 binary & ordinal features)
- **Target Variable**: `Mental_Health_Impact` (`Not at all`, `Slightly`, `Moderately`, `Severely`)

## Setup & Execution

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install -r ml_api/requirements.txt
```

### 2. Start Service (Local Execution from Repository Root)
Run via Uvicorn:
```bash
uvicorn ml_api.main:app --host 127.0.0.1 --port 8000
```

### 3. Deploying on Render (Web Service)
- **Root Directory**: Leave blank (root of repo)
- **Build Command**: `pip install -r ml_api/requirements.txt`
- **Start Command**: `uvicorn ml_api.main:app --host 0.0.0.0 --port $PORT`

### 4. API Endpoints

- `GET /api/ml/health`: Returns model connection health, target classes, and feature count.
- `POST /api/ml/predict`: Accepts questionnaire payload, executes preprocessor + Random Forest inference, generates SHAP local feature attributions, and returns structured prediction payload.
