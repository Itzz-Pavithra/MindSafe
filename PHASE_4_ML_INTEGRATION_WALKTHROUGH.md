# MINDSAFE — PHASE 4: ML MODEL + SHAP EXPLAINABILITY INTEGRATION

## Executive Summary

Phase 4 of the MindSafe research project integrates the trained, leakage-controlled **Random Forest Multiclass Classifier** (`Scenario B`) and **SHAP TreeExplainer Local Explainability Engine** from Phase 3 into the live MindSafe application. 

This phase bridges research machine learning and human-computer interaction by deploying a dedicated Python + FastAPI microservice, establishing secure backend-to-backend communication with the SvelteKit application, persisting authenticated assessment outcomes and feature attributions in MongoDB, updating the participant assessment and result dashboards, and providing researchers with an administrative ML analytics suite.

In accordance with strict empirical research standards:
- **Zero Retraining:** The trained primary model (`mindsafe_primary_model.joblib`) and preprocessor (`mindsafe_primary_preprocessor.joblib`) were loaded unchanged.
- **Zero Synthetic Data:** No synthetic records, SMOTE, or fabricated responses were generated.
- **Strict Explainability Standards:** SHAP values are calculated dynamically per participant submission.
- **Strict Non-Causal Wording:** Explanations adhere strictly to model-attribution semantics (*"The model placed positive analytical weight on..."* rather than clinical or causal claims).
- **Medical Disclaimers:** All participant-facing results explicitly state that the classification represents an analytical research output, not a clinical diagnosis.

---

## 1. System Architecture

The integrated MindSafe Phase 4 architecture implements a secure multi-tier design:

```
┌────────────────────────────────────────────────────────┐
│                   SvelteKit Frontend                   │
│   • Assessment Form (13 Empirical Predictors)          │
│   • Professional Loading Screen ("Analyzing...")       │
│   • Result Dashboard (4-Level Scale & SHAP Explanations)│
│   • Participant Profile & Assessment History Table     │
│   • Admin ML & SHAP Analytics Dashboard                │
└───────────────────────────┬────────────────────────────┘
                            │ (Authenticated Session Cookie)
                            ▼
┌────────────────────────────────────────────────────────┐
│               MindSafe SvelteKit Backend               │
│   • Session Authentication (locals.user verification)  │
│   • Input Validation & Normalization                   │
│   • mlService.js (HTTP Client to FastAPI)              │
│   • MongoDB Mongoose Models (SurveyResponse & Results) │
└───────────────────────────┬────────────────────────────┘
                            │ (Internal HTTP POST /api/ml/predict)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Python FastAPI ML API                  │
│   • Singleton ModelLoader (Lifespan Startup)           │
│   • SurveyFeaturePreprocessor (54 Features, Scenario B)│
│   • Random Forest Classifier (100 Trees, Balanced)     │
│   • SHAP TreeExplainer (Additive Feature Attributions)│
│   • Friendly Feature Name Labeler                      │
└────────────────────────────────────────────────────────┘
```

---

## 2. FastAPI Implementation

The ML microservice is organized inside `ml-api/`:

```
ml-api/
├── main.py              # FastAPI server, lifespan initialization, CORS & endpoints
├── model_loader.py      # Singleton loader for .joblib models and metadata
├── predictor.py         # Questionnaire normalization, RF inference, orchestration
├── shap_explainer.py    # TreeExplainer manager and non-causal explanation formatting
├── schemas.py           # Pydantic request/response validation schemas
├── requirements.txt     # Python dependency specifications
└── README.md            # Microservice documentation and run instructions
```

### Key Service Features:
1. **Lifespan Startup:** Models are loaded into memory exactly once at application startup. Zero per-request file reads.
2. **CORS Security:** Restricted to authorized MindSafe frontend origins (`http://localhost:5173`, `http://127.0.0.1:5173`, etc.).
3. **Structured Pydantic Schemas:** Strong typing for `PredictRequest`, `PredictResponse`, `PredictionDetail`, and `ExplanationDetail`.
4. **Resilient HTTP API:** Health endpoint `GET /api/ml/health` and prediction endpoint `POST /api/ml/predict`.

---

## 3. Model Loading Protocol

Model artifacts are managed by `ModelLoader` in `ml-api/model_loader.py`:

- **Primary Model:** `models/mindsafe_primary_model.joblib`
- **Primary Preprocessor:** `models/mindsafe_primary_preprocessor.joblib`
- **Model Metadata:** `models/model_metadata.json`

### Fail-Fast Verification:
- Checks existence of `.joblib` files on disk prior to loading.
- Raises explicit server-side exceptions if artifacts are missing or corrupted.
- **Zero Silent Fallback:** The system will never fabricate predictions or instantiate an untrained dummy model if files fail to load.

---

## 4. Prediction Endpoint (`POST /api/ml/predict`)

The endpoint accepts questionnaire responses, applies the fitted preprocessing pipeline, executes the Random Forest ensemble, computes class probabilities, and generates SHAP explanations.

### Request Payload:
```json
{
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
```

### Response Payload:
```json
{
  "success": true,
  "model_name": "MindSafe Primary Random Forest Classifier",
  "model_version": "1.0.0-ScenarioB",
  "prediction": {
    "class": "Moderately",
    "predicted_class_index": 2,
    "probabilities": {
      "Not at all": 0.19,
      "Slightly": 0.23,
      "Moderately": 0.39,
      "Severely": 0.19
    }
  },
  "explanation": {
    "top_features": [
      {
        "feature": "Experienced Cyberbullying",
        "raw_feature": "Experienced_Cyberbullying_Binary",
        "shap_value": 0.0529,
        "direction": "increased",
        "description": "The model placed positive analytical weight on Experienced Cyberbullying toward predicting 'Moderately'."
      },
      {
        "feature": "Observed: Body Shaming",
        "raw_feature": "Bullying_Type_Body Shaming",
        "shap_value": 0.0394,
        "direction": "increased",
        "description": "The model placed positive analytical weight on Observed: Body Shaming toward predicting 'Moderately'."
      },
      {
        "feature": "Cyberbullying Frequency",
        "raw_feature": "Cyberbullying_Frequency_Ordinal",
        "shap_value": 0.0365,
        "direction": "increased",
        "description": "The model placed positive analytical weight on Cyberbullying Frequency toward predicting 'Moderately'."
      }
    ],
    "method": "SHAP TreeExplainer (Additive Feature Attributions)",
    "note": "SHAP values quantify model decision weights for this response pattern and do not indicate clinical causation."
  },
  "disclaimer": "This is an analytical result from the project ML model and is not a medical diagnosis."
}
```

---

## 5. SHAP Integration & Language Standards

### Computation:
- Utilizes `shap.TreeExplainer(model)` initialized once at startup.
- Multiclass output tensor shape: `(1, 54, 4)`.
- For the predicted class $k \in \{0, 1, 2, 3\}$, the slice `shap_values[0, :, k]` provides the exact attribution of each of the 54 features.
- Features are sorted by absolute magnitude $|\phi_j|$ and the top contributing factors are extracted.

### Human-Readable Feature Mapping:
Technical pipeline tokens are mapped to user-friendly labels:
- `Cyberbullying_Frequency_Ordinal` $\rightarrow$ **Cyberbullying Frequency**
- `Experienced_Cyberbullying_Binary` $\rightarrow$ **Experienced Cyberbullying**
- `Daily_Usage_Ordinal` $\rightarrow$ **Daily Social Media Usage**
- `Age_Ordinal` $\rightarrow$ **Age Group**
- `Bullying_Type_Body Shaming` $\rightarrow$ **Observed: Body Shaming**
- `Action_Taken_Blocked the user` $\rightarrow$ **Action Taken: Blocked the User**

### Non-Causal Explanation Wording:
All generated text complies with academic explainability standards:
- **Approved:** *"The model placed positive analytical weight on Cyberbullying Frequency toward predicting 'Moderately'."*
- **Approved:** *"The model placed countervailing weight on Gender (Female) relative to predicting 'Moderately'."*
- **Prohibited:** *"Cyberbullying caused your distress."*
- **Prohibited:** *"This proves that your mental health was damaged by social media."*

---

## 6. Participant Flow & UI States

1. **Authentication:** Participant logs in and accesses `/assessment`.
2. **Assessment:** Form presents the 13 Scenario B questions with clear single-select radios and multi-select checkboxes.
3. **Review State:** Participant reviews selections before final submission.
4. **Submission & Loading:**
   - Displays modal: `"Analyzing your responses..."` with SVG spinner (no emojis).
   - Backend submits to `POST /api/ml/predict`.
5. **Result Dashboard (`/result`):**
   - **4-Level Visual Indicator:** Horizontal scale (`Not at all` $\rightarrow$ `Slightly` $\rightarrow$ `Moderately` $\rightarrow$ `Severely`) with the predicted class exclusively highlighted.
   - **"Why did the model make this prediction?":** Real SHAP feature contributions with magnitude and direction badges.
   - **Model Class Probabilities:** Expandable analytical probability distribution with explicit disclaimer explaining that probabilities are model estimates, not clinical diagnostic probabilities.
   - **Disclaimers & Resources:** Statutory helpline (1930) and medical disclaimer.

---

## 7. Database Integration & MongoDB Storage

Upon receiving a valid prediction from the FastAPI service, the SvelteKit backend persists the records to MongoDB:

1. **`SurveyResponse` Collection:**
   ```json
   {
     "_id": "ObjectId(...)",
     "userId": "ObjectId(...)",
     "responses": { ...raw questionnaire responses... },
     "submittedAt": "2026-09-24T01:25:00.000Z"
   }
   ```

2. **`AssessmentResult` Collection:**
   ```json
   {
     "_id": "ObjectId(...)",
     "userId": "ObjectId(...)",
     "responseId": "ObjectId(...)",
     "classification": "Moderately",
     "probabilities": {
       "Not at all": 0.19,
       "Slightly": 0.23,
       "Moderately": 0.39,
       "Severely": 0.19
     },
     "topFeatures": [ ...top SHAP feature objects... ],
     "modelVersion": "MindSafe Primary Random Forest (Scenario B)",
     "disclaimer": "This is an analytical result from the project ML model and is not a medical diagnosis.",
     "createdAt": "2026-09-24T01:25:00.000Z"
   }
   ```

---

## 8. Participant Assessment History

On `/profile`:
- Displays participant credentials and assessment status.
- Renders an **Assessment & ML Prediction History** table displaying:
  - Assessment Timestamp
  - Predicted Mental Health Impact (color-coded badge)
  - Model Version
  - Direct navigation link to view detailed SHAP results.

---

## 9. Admin ML & SHAP Analytics (`/admin/ml-analysis`)

Dedicated research analytics page reading directly from Phase 3 CSV/JSON results without client-side recalculation:

### Displayed Artifacts & Metrics:
1. **Model Specification:** Random Forest Classifier (100 trees, balanced weights, Scenario B).
2. **Documented Held-Out Test Metrics ($N=103$):**
   - **Accuracy:** $48.54\%$
   - **Macro Precision:** $0.3700$
   - **Macro Recall:** $0.3498$
   - **Macro F1:** $0.3275$
   - **Weighted F1:** $0.4177$
3. **5-Fold Cross-Validation Metrics ($N=411$):**
   - **Mean CV Accuracy:** $49.88\% \pm 1.74\%$
   - **Mean CV Weighted F1:** $0.4387 \pm 0.0226$
4. **Global SHAP Feature Importance:**
   - Horizontal bar chart rendering the top 15 features by Mean Absolute SHAP value from `shap_feature_importance.csv`.
   - Clear explanatory caption: *"Mean absolute SHAP values indicate the average magnitude of each feature's contribution to model predictions."*
5. **Per-Class Metrics & Model Benchmark Comparison:**
   - Full breakdown for all 4 outcome classes.
   - Benchmark comparison against Scenario A (Full Model) and Baseline Dummy classifier.

---

## 10. Security & Access Control

- **Session Guarding:** `POST /api/ml/predict` enforces participant session authentication via `locals.user`. Anonymous submissions return HTTP 401.
- **Admin RBAC:** `/admin/ml-analysis` enforces administrator authentication (`locals.user.role === 'admin'`). Non-admin attempts return HTTP 403.
- **Zero Secrets Exposure:** MongoDB connection strings, JWT secrets, and admin credentials reside strictly in server-side environment variables (`.env`).
- **No Static Model Exposure:** `.joblib` files are stored in `models/` on the server filesystem and are never served through `static/` or client bundles.

---

## 11. Testing & Verification

A comprehensive automated test suite was constructed and executed:

| Test Script | Target | Status |
| :--- | :--- | :---: |
| `scratch/test_ml_api.py` | FastAPI Startup, Health Check, Prediction, Probabilities, Validation Errors | **PASS** (5/5 tests) |
| `scratch/test_phase4_integration.py` | Preprocessor 54 Features, SHAP Attributions, Non-Causal Wording, No Secrets | **PASS** (7/7 tests) |
| `scratch/test_e2e_backend.js` | End-to-End Flow: Health $\rightarrow$ Inference $\rightarrow$ MongoDB Storage $\rightarrow$ Retrieval $\rightarrow$ Cleanup | **PASS** (4/4 stages) |
| `npm run build` | Full SvelteKit compilation of all routes, server endpoints, and components | **PASS** (Built in 18.66s) |

---

## 12. Final Project Structure

```
MindSafe/
├── Data/
│   ├── raw/                       # Original survey CSV (Untouched)
│   └── processed/                 # Phase 1 & 2 cleaned datasets (519 records)
├── ml-api/
│   ├── main.py                    # FastAPI server & routes
│   ├── model_loader.py            # Singleton model loader
│   ├── predictor.py               # Preprocessing & inference orchestrator
│   ├── shap_explainer.py          # SHAP TreeExplainer & label formatter
│   ├── schemas.py                 # Pydantic schemas
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # Microservice documentation
├── models/
│   ├── mindsafe_primary_model.joblib          # Trained RF Primary Model (Scenario B)
│   ├── mindsafe_primary_preprocessor.joblib   # Fitted Preprocessor (54 Features)
│   ├── mindsafe_full_benchmark.joblib         # Trained RF Benchmark Model (Scenario A)
│   ├── mindsafe_full_preprocessor.joblib      # Benchmark Preprocessor (61 Features)
│   ├── model_metadata.json                    # Model hyperparameters & metrics
│   └── preprocessor.py                        # Standalone preprocessor class definition
├── results/
│   └── ml/                        # Phase 3 CSV evaluation reports & plots
├── src/
│   ├── lib/
│   │   ├── components/            # Svelte UI components (Cards, Buttons, Sidebar)
│   │   └── server/
│   │       ├── db.js              # MongoDB Atlas connection
│   │       ├── models/            # Mongoose schemas (User, SurveyResponse, AssessmentResult)
│   │       └── services/
│   │           └── mlService.js   # HTTP Client calling FastAPI ML service
│   └── routes/
│       ├── (user)/
│       │   ├── assessment/        # Questionnaire form with loading screen
│       │   ├── result/            # Result dashboard with 4-level scale & SHAP
│       │   └── profile/           # Participant profile & assessment history
│       ├── admin/
│       │   ├── +page.svelte       # Admin overview with active ML status
│       │   └── ml-analysis/       # Research ML evaluation & SHAP analytics
│       └── api/
│           ├── ml/
│           │   ├── predict/       # Authenticated prediction endpoint
│           │   └── status/        # ML service health check endpoint
│           └── survey/
│               ├── my-result/     # Participant latest result query
│               └── my-response/   # Participant survey submission query
├── PHASE_2_WALKTHROUGH.md
├── PHASE_3_ML_WALKTHROUGH.md
├── PHASE_4_ML_INTEGRATION_WALKTHROUGH.md
└── package.json
```

---

## 13. Run Instructions

### 1. Start Python FastAPI ML API (Port 8000)
```bash
python -m uvicorn main:app --app-dir ml-api --host 127.0.0.1 --port 8000 --ws none
```

### 2. Start MindSafe SvelteKit Application (Port 5173)
```bash
npm run dev
```

### 3. Verify Operational Status
- **ML Health Check:** `http://127.0.0.1:8000/api/ml/health`
- **Frontend Assessment:** `http://localhost:5173/assessment`
- **Result Dashboard:** `http://localhost:5173/result`
- **Participant Profile:** `http://localhost:5173/profile`
- **Admin ML Analytics:** `http://localhost:5173/admin/ml-analysis`

---

## 14. Known Limitations & Research Context

1. **Model Accuracy Context:** The primary model achieves 48.54% test accuracy (5-fold CV 49.88% ± 1.74%) on self-reported social media survey data across 4 discrete classes. This exceeds the baseline majority-class guessing (44.66%) and weighted F1 (0.4177 vs 0.2758 baseline), but reflects the subjective noise inherent in survey-based psychological self-reports.
2. **Non-Clinical Purpose:** The predictions represent analytical pattern recognition across survey dimensions. They do not constitute a diagnostic medical or psychiatric evaluation.
3. **Local Explainability:** SHAP TreeExplainer attributes decision weight within the fitted decision trees. Features with positive SHAP values indicate that the respondent's answers aligned with patterns that the model associates with that class; they do not establish causal etiology.

---

## PHASE 4 COMPLETE
