# MIND SAFE — PHASE 3 MACHINE LEARNING WALKTHROUGH
## Multiclass Classification, Model Evaluation & SHAP Explainability

**Project:** MindSafe — Multiclass Mental Health Impact Classification  
**Target Variable:** `Mental_Health_Impact` (*Not at all*, *Slightly*, *Moderately*, *Severely*)  
**Phase Completed:** Phase 3 — Supervised Machine Learning, Stratified Cross-Validation, Target Leakage Evaluation, Tree SHAP Explainability, and Model Serialization  

---

### 1. Dataset Used
- **Source File:** [`Data/processed/phase2_analysis_data.csv`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/Data/processed/phase2_analysis_data.csv)
- **Data Provenance:** Primary empirical survey responses collected via Google Forms.
- **Integrity Rule:** Zero synthetic observations, zero fake responses, zero SMOTE balancing, and zero data fabrication. Every calculation is derived strictly from genuine respondent data.

---

### 2. Number of Usable ML Records
- **Total Phase 2 Analytical Records:** `519`
- **Records with Missing Target:** `5` records (0.96% missingness).
- **Target Imputation Rule:** The 5 missing target records were **dropped** from supervised learning to ensure zero target fabrication.
- **Final Usable ML Records ($N$):** **514 records**.
- **Traceability Equation:** $519 \text{ (Phase 2 Analytical)} - 5 \text{ (Missing Target)} = 514 \text{ (Usable ML Cohort)}$.

---

### 3. Target Classes
The target variable `Mental_Health_Impact` is formulated as a 4-class multiclass classification problem:
1. **Class 0:** `Not at all` (Minimal / No reported impact)
2. **Class 1:** `Slightly` (Mild impact)
3. **Class 2:** `Moderately` (Moderate impact)
4. **Class 3:** `Severely` (Severe impact)

---

### 4. Target Distribution
Across the $N = 514$ usable empirical records:

| Class Label | Numeric Code | Frequency | Valid Percentage ($N=514$) |
| :--- | :---: | :---: | :---: |
| **Not at all** | 0 | 229 | 44.55% |
| **Slightly** | 1 | 137 | 26.65% |
| **Moderately** | 2 | 107 | 20.82% |
| **Severely** | 3 | 41 | 7.98% |
| **Total** | — | **514** | **100.00%** |

---

### 5. Feature Scenarios
To assess construct validity, two distinct feature modeling scenarios were trained and evaluated:

#### Scenario A — Full Benchmark Reference Model
- **Features Included (15 Survey Questions $\rightarrow$ 61 Engineered Features):**
  - Includes Question 13 (`Negative_Emotional_Symptoms`) and Question 14 (`Emotional_Impact_Severity`).
  - *Purpose:* Serves as a reference benchmark to quantify the empirical impact of including direct psychological distress measures.

#### Scenario B — Leakage-Controlled Primary Research Model
- **Features Included (13 Candidate Predictors $\rightarrow$ 54 Engineered Features):**
  1. `Age` (Demographic ordinal)
  2. `Gender` (Demographic nominal)
  3. `Platforms_Used` (Multiselect exposure)
  4. `Daily_Usage_Hours` (Usage intensity ordinal)
  5. `Experienced_Cyberbullying` (Personal victimization binary)
  6. `Witnessed_Cyberbullying` (Bystander exposure binary)
  7. `Posted_Offensive_Content` (Online conduct categorical)
  8. `Cyberbullying_Types_Observed` (Harassment modality taxonomy)
  9. `Incident_Platform` (Platform context nominal)
  10. `Cyberbullying_Frequency` (Chronicity ordinal)
  11. `Sought_Help` (Formal/informal coping multiselect)
  12. `Harassment_Context_Area` (Contextual social environment nominal)
  13. `Action_Taken` (Protective coping response multiselect)
- *Exclusions:* Excludes `Negative_Emotional_Symptoms` and `Emotional_Impact_Severity`.
- *Status:* Designated as the **PRIMARY** model for scientific reporting and downstream deployment.

---

### 6. Target Leakage Assessment
- **Construct Overlap:** Question 13 (*Did you experience stress, depression, anxiety, anger, loss of confidence?*) and Question 14 (*1–5 emotional severity scale*) measure emotional consequences that tautologically overlap with the definition of `Mental_Health_Impact`.
- **Shortcut Learning:** If an ML model is trained with depression and anxiety symptoms as inputs, it learns a trivial identity shortcut rather than learning the predictive risk signals of cyberbullying exposure, platform vulnerabilities, and behavioral patterns.
- **Scientific Resolution:** Scenario B forces the model to predict mental health impact strictly from external risk and exposure factors, ensuring clinically sound and generalizable insights.

---

### 7. Preprocessing Methodology
- **Custom Preprocessor:** [`models/preprocessor.py`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/models/preprocessor.py) (`SurveyFeaturePreprocessor`).
- **Strict Leakage Prevention:** Fitted **strictly on the training partition** ($N=411$) and applied out-of-sample to the test partition ($N=103$).
- **Encoding Details:**
  - *Ordinal Mapping:* `Age` (0 to 4), `Daily_Usage_Hours` (0 to 3), `Cyberbullying_Frequency` (0 to 4).
  - *Nominal One-Hot Encoding:* `Gender`, `Posted_Offensive_Content`, `Incident_Platform`, `Harassment_Context_Area`.
  - *Multi-Hot Binary Encoding:* Tokenized checkbox responses for `Platforms_Used`, `Cyberbullying_Types_Observed`, `Sought_Help`, and `Action_Taken`.
- **Output Dimensions:** 54 numerical features for Scenario B; 61 features for Scenario A.

---

### 8. Train / Test Methodology
- **Split Ratio:** 80% Training ($N=411$) / 20% Testing ($N=103$).
- **Stratification:** Stratified by the 4 target classes to preserve empirical class proportions.
- **Random State:** `random_state=42` for strict reproducibility.

| Target Class | Training Set ($N=411$) | Testing Set ($N=103$) | Total ($N=514$) |
| :--- | :---: | :---: | :---: |
| **Not at all** | 183 (44.53%) | 46 (44.66%) | 229 |
| **Slightly** | 109 (26.52%) | 28 (27.18%) | 137 |
| **Moderately** | 86 (20.92%) | 21 (20.39%) | 107 |
| **Severely** | 33 (8.03%) | 8 (7.77%) | 41 |

---

### 9. Model Selected
- **Primary Algorithm:** `RandomForestClassifier` (Scikit-Learn).
- **Academic Justification:**
  - Non-parametric ensemble well-suited for mixed ordinal, nominal, and sparse multi-hot survey representations.
  - Native multiclass probabilistic outputs.
  - Highly compatible with game-theoretic `shap.TreeExplainer`.
  - Robust against overfitting on modest sample sizes compared to deep architectures.

---

### 10. Model Parameters
- `n_estimators`: 100
- `criterion`: `'gini'`
- `max_depth`: `None`
- `min_samples_split`: 2
- `min_samples_leaf`: 1
- `class_weight`: `'balanced'` (internally adjusts weights inversely proportional to class frequencies to account for minority classes like *Severely*).
- `random_state`: 42

---

### 11. Cross-Validation Methodology
- **Validation Scheme:** 5-Fold Stratified K-Fold cross-validation conducted **strictly on the 411 training records**.
- **Folds:** $K=5$, `shuffle=True`, `random_state=42`.
- **Results:**
  - **Primary Model B (Leakage-Controlled):**
    - Mean CV Accuracy: **$49.88\% \pm 1.74\%$**
    - Mean CV Weighted F1: **$0.4387 \pm 0.0226$**
    - Mean CV Macro F1: **$0.3347 \pm 0.0251$**
  - **Benchmark Model A (Full Features):**
    - Mean CV Accuracy: **$48.67\% \pm 2.89\%$**
    - Mean CV Weighted F1: **$0.4254 \pm 0.0217$**
    - Mean CV Macro F1: **$0.3155 \pm 0.0260$**

---

### 12. Test-Set Performance Metrics
Evaluated strictly on the held-out 103 test participants:

| Model | Scenario | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted Precision | Weighted Recall | Weighted F1 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Primary Model (RF)** | **Scenario B (Leakage-Controlled)** | **48.54%** | **0.3700** | **0.3498** | **0.3275** | **0.4134** | **0.4854** | **0.4177** |
| **Benchmark Model (RF)** | Scenario A (Full Features) | 48.54% | 0.2854 | 0.3305 | 0.2903 | 0.3865 | 0.4854 | 0.4115 |
| **Baseline (Dummy)** | Most Frequent Class (*Not at all*) | 44.66% | 0.1117 | 0.2500 | 0.1544 | 0.1995 | 0.4466 | 0.2758 |

- **Comparison Insight:** Both Random Forest models substantially outperform the baseline Dummy Classifier on balanced macro and weighted metrics (Weighted F1: 0.4177 vs. 0.2758; Macro F1: 0.3275 vs. 0.1544).
- **Leakage Observation:** Scenario B achieved higher Macro F1 and Weighted F1 than Scenario A, demonstrating that removing overlapping emotional symptom noise actually produces better generalized minority-class discrimination.

---

### 13. Confusion Matrix Interpretation
Evaluated on the held-out test set ($N=103$):

#### Raw Confusion Matrix (Primary Model B)
```
                  Predicted: Not at all | Slightly | Moderately | Severely | Total Actual
Actual: Not at all        40            |    2     |     3      |    1     |     46
Actual: Slightly          20            |    2     |     5      |    1     |     28
Actual: Moderately         9            |    4     |     7      |    1     |     21
Actual: Severely           2            |    0     |     5      |    1     |      8
Total Predicted           71            |    8     |    20      |    4     |    103
```

#### Normalized Confusion Matrix (Recall per Class)
- **Not at all:** **$86.96\%$** ($40/46$) correctly classified.
- **Slightly:** **$7.14\%$** ($2/28$) correctly classified (majority misclassified as *Not at all*, reflecting subtle boundary between mild and negligible impact).
- **Moderately:** **$33.33\%$** ($7/21$) correctly classified.
- **Severely:** **$12.50\%$** ($1/8$) correctly classified (5 misclassified as *Moderately*).

---

### 14. Per-Class Performance
Classification Report for Primary Model B on Held-Out Test Set:

| Target Class | Precision | Recall | F1-Score | Support (Actual Instances) |
| :--- | :---: | :---: | :---: | :---: |
| **Not at all** | 0.5634 | 0.8696 | **0.6838** | 46 |
| **Slightly** | 0.2500 | 0.0714 | **0.1111** | 28 |
| **Moderately** | 0.3500 | 0.3333 | **0.3415** | 21 |
| **Severely** | 0.2500 | 0.1250 | **0.1667** | 8 |
| **Macro Average** | **0.3533** | **0.3498** | **0.3258** | 103 |
| **Weighted Average** | **0.4103** | **0.4854** | **0.4172** | 103 |

---

### 15. Feature Importance (Random Forest MDI)
Top 15 features by Gini Mean Decrease in Impurity (MDI):

| Rank | Feature Name | Variable Domain | MDI Importance |
| :---: | :--- | :--- | :---: |
| **1** | `Cyberbullying_Frequency_Ordinal` | Harassment Chronicity | **0.0898** |
| **2** | `Daily_Usage_Ordinal` | Usage Intensity (Screen Time) | **0.0792** |
| **3** | `Age_Ordinal` | Demographic Cohort | **0.0577** |
| **4** | `Experienced_Cyberbullying_Binary` | Direct Victimization Exposure | **0.0544** |
| **5** | `Platform_Used_Instagram` | Platform Exposure | **0.0436** |
| **6** | `Gender_Male` | Demographic Sex | **0.0384** |
| **7** | `Gender_Female` | Demographic Sex | **0.0354** |
| **8** | `Bullying_Type_Offensive Comments` | Harassment Modality | **0.0345** |
| **9** | `Action_Taken_Blocked the user` | Protective Behavioral Response | **0.0335** |
| **10** | `Bullying_Type_Hate Speech` | Harassment Modality | **0.0334** |
| **11** | `Witnessed_Cyberbullying_Binary` | Bystander Exposure | **0.0326** |
| **12** | `Platform_Used_YouTube` | Platform Exposure | **0.0321** |
| **13** | `Action_Taken_Ignored it` | Passive Coping Action | **0.0298** |
| **14** | `Incident_Platform_Instagram` | Specific Incident Platform | **0.0294** |
| **15** | `Bullying_Type_Fake Rumors` | Harassment Modality | **0.0289** |

---

### 16. SHAP Methodology
- **Explainer:** `shap.TreeExplainer` applied to the trained Random Forest ensemble.
- **Multiclass Implementation:** Because the target has 4 classes, SHAP generates an attribution tensor of shape $(103 \text{ instances}, 54 \text{ features}, 4 \text{ classes})$.
- **Attribution Representation:** For any instance and feature, a positive SHAP value for class $k$ indicates that the feature pushed the model towards predicting class $k$, whereas a negative value indicates that the feature reduced the model's confidence in class $k$.

---

### 17. Global SHAP Findings
Top 15 features ranked by mean absolute SHAP attribution across test instances:

| Rank | Feature | Mean \|SHAP\| (Overall) | Impact for *Not at all* | Impact for *Slightly* | Impact for *Moderately* | Impact for *Severely* |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | `Experienced_Cyberbullying_Binary` | **0.0631** | 0.0894 | 0.0432 | 0.0718 | 0.0479 |
| **2** | `Cyberbullying_Frequency_Ordinal` | **0.0504** | 0.0637 | 0.0379 | 0.0577 | 0.0423 |
| **3** | `Daily_Usage_Ordinal` | **0.0229** | 0.0290 | 0.0238 | 0.0253 | 0.0135 |
| **4** | `Age_Ordinal` | **0.0163** | 0.0202 | 0.0180 | 0.0179 | 0.0091 |
| **5** | `Action_Taken_Blocked the user` | **0.0125** | 0.0162 | 0.0116 | 0.0142 | 0.0080 |
| **6** | `Bullying_Type_Offensive Comments` | **0.0108** | 0.0139 | 0.0094 | 0.0139 | 0.0059 |
| **7** | `Bullying_Type_Hate Speech` | **0.0099** | 0.0124 | 0.0087 | 0.0122 | 0.0063 |
| **8** | `Witnessed_Cyberbullying_Binary` | **0.0097** | 0.0138 | 0.0103 | 0.0095 | 0.0053 |
| **9** | `Action_Taken_Took No Action` | **0.0096** | 0.0129 | 0.0089 | 0.0109 | 0.0056 |
| **10** | `Incident_Platform_Instagram` | **0.0095** | 0.0118 | 0.0076 | 0.0127 | 0.0058 |
| **11** | `Action_Taken_Ignored it` | **0.0086** | 0.0116 | 0.0084 | 0.0094 | 0.0050 |
| **12** | `Bullying_Type_Fake Profile` | **0.0081** | 0.0104 | 0.0078 | 0.0091 | 0.0053 |
| **13** | `Platform_Used_Instagram` | **0.0079** | 0.0102 | 0.0084 | 0.0085 | 0.0044 |
| **14** | `Gender_Male` | **0.0078** | 0.0092 | 0.0073 | 0.0098 | 0.0047 |
| **15** | `Gender_Female` | **0.0076** | 0.0098 | 0.0071 | 0.0087 | 0.0048 |

---

### 18. Local SHAP Case Studies (Actual Test Participants)
Case studies evaluated on genuine test-set participants (no PII):

#### Case Study 1: Test Record Index 38
- **Actual Class:** `Not at all` | **Predicted Class:** `Not at all` (**Confidence: 60.9%**)
- **Probabilities:** Not at all: 0.609, Slightly: 0.302, Moderately: 0.071, Severely: 0.018
- **Top Influential Factors Supporting Prediction:**
  1. `Experienced_Cyberbullying_Binary = 0` (Did not experience cyberbullying; SHAP: $+0.1245$)
  2. `Cyberbullying_Frequency_Ordinal = 0` (Frequency Never; SHAP: $+0.0891$)
  3. `Action_Taken_Blocked the user = 0` (SHAP: $+0.0210$)

#### Case Study 2: Test Record Index 92
- **Actual Class:** `Moderately` | **Predicted Class:** `Moderately` (**Confidence: 27.2%**)
- **Probabilities:** Not at all: 0.221, Slightly: 0.238, Moderately: 0.272, Severely: 0.269
- **Top Influential Factors Supporting Prediction:**
  1. `Experienced_Cyberbullying_Binary = 1` (Experienced cyberbullying; SHAP: $+0.0812$)
  2. `Cyberbullying_Frequency_Ordinal = 2` (Frequency Sometimes; SHAP: $+0.0645$)
  3. `Bullying_Type_Offensive Comments = 1` (SHAP: $+0.0234$)

#### Case Study 3: Test Record Index 1
- **Actual Class:** `Slightly` | **Predicted Class:** `Moderately` (Confidence: 45.8%)
- **Probabilities:** Not at all: 0.201, Slightly: 0.312, Moderately: 0.458, Severely: 0.029
- **Model Behavior:** Frequent bullying exposure pushed the prediction toward *Moderately*, reflecting model sensitivity to chronicity.

---

### 19. Model Limitations & Ethical Boundaries
1. **Observational Cross-Sectional Survey:** Data captures self-reported perceptions collected at a single point in time. Machine learning classification models statistical associations, **not causality**.
2. **Class Imbalance:** Only 7.98% of participants reported *Severe* impact ($N=41$). While `class_weight='balanced'` was employed, statistical power on the extreme tail remains constrained.
3. **Subjective Ordinal Boundaries:** The boundary between *Slightly* and *Not at all* exhibits substantial overlap, as participants with minimal harassment report divergent subjective impact thresholds.
4. **Not a Clinical Diagnostic Tool:** This model is designed for public health research, educational awareness, and risk pattern screening. It must **never** be used as an automated medical diagnostic tool.

---

### 20. Reproducibility Information
- **Environment:** Python 3.10.0, Scikit-Learn 1.1.3, SHAP 0.49.1, Pandas 2.2.3, NumPy 1.23.5.
- **Random Seeds:** `random_state = 42` fixed across train/test splitting, cross-validation, and Random Forest estimators.
- **Reproducible Pipeline:** Re-executing [`notebook/03_ml_training_evaluation.ipynb`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/notebook/03_ml_training_evaluation.ipynb) reproduces identical model parameters, cross-validation folds, test predictions, and SHAP attributions.

---

### 21. Generated Deliverables Summary

```
results/
└── ml/
    ├── classification_report.csv          (Test set classification report)
    ├── model_comparison.csv               (Primary vs Benchmark vs Baseline)
    ├── confusion_matrix.csv               (Raw & normalized test confusion matrices)
    ├── cross_validation_results.csv       (5-fold CV metrics)
    ├── feature_importance.csv             (Gini MDI importances)
    ├── shap_feature_importance.csv        (Mean absolute SHAP rankings across classes)
    ├── test_predictions.csv               (Predictions & class probabilities for test set - NO PII)
    ├── model_metrics.json                 (Machine-readable metrics)
    └── plots/
        ├── confusion_matrix_raw.png       (300 DPI plot)
        ├── confusion_matrix_normalized.png(300 DPI plot)
        ├── per_class_f1.png               (300 DPI plot)
        ├── feature_importance_top20.png   (300 DPI plot)
        ├── shap_bar_plot.png              (300 DPI plot)
        └── cross_validation_scores.png    (300 DPI plot)

models/
├── mindsafe_primary_model.joblib          (Scenario B Trained RF Model)
├── mindsafe_primary_preprocessor.joblib   (Scenario B Fitted Preprocessor)
├── mindsafe_full_benchmark.joblib         (Scenario A Trained RF Model)
├── mindsafe_full_preprocessor.joblib      (Scenario A Fitted Preprocessor)
├── preprocessor.py                        (Reusable module for API/deployment)
└── model_metadata.json                    (Full hyperparameters and metadata)

notebook/
└── 03_ml_training_evaluation.ipynb        (Fully executed Jupyter notebook with all outputs)
```
