# MIND SAFE — PHASE 3 MACHINE LEARNING WALKTHROUGH
## Multiclass Classification, Model Evaluation & SHAP Explainability

**Project:** MindSafe — Multiclass Mental Health Impact Classification  
**Target Variable:** `Mental_Health_Impact` (*Not at all*, *Slightly*, *Moderately*, *Severely*)  
**Experimental Design:** Supervised Machine Learning, 5-Fold Stratified Cross-Validation, Target Leakage Evaluation, Tree SHAP Feature Attribution, and Model Serialization.

---

### A. Dataset Characteristics & Partition Verification
- **Source File:** [`Data/processed/cleaned_survey_data.csv`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/Data/processed/cleaned_survey_data.csv)
- **Data Provenance:** Empirical survey responses collected via Google Forms (1,521 raw submissions).
- **Integrity Rule:** Zero synthetic data, zero oversampling, zero duplicated records.
- **Data Cleaning Breakdown:**
  - Raw CSV row count: **1,521**
  - Removed completely blank submissions: **2** (Indices 21, 80)
  - Removed incomplete target submissions: **5** (Indices 16, 24, 25, 46, 70)
  - Exact duplicate rows: **0**
  - **Final Usable Analytical Dataset ($N$):** **1,514 records** ($1,521 - 7 = 1,514$).
- **Stratified 80/20 Train/Test Partition (`random_state=42`):**
  - Training Set: **1,211 records** (80.0%)
  - Testing Set: **303 records** (20.0%)
  - Verification: $1,211 + 303 = 1,514$.

#### Target Distribution Across Partitions:
| Target Category | Full Dataset ($N=1,514$) | Training Set ($N=1,211$) | Testing Set ($N=303$) |
| :--- | :---: | :---: | :---: |
| **Not at all** | 479 (31.64%) | 383 (31.63%) | 96 (31.68%) |
| **Slightly** | 387 (25.56%) | 309 (25.52%) | 78 (25.74%) |
| **Moderately** | 357 (23.58%) | 286 (23.62%) | 71 (23.43%) |
| **Severely** | 291 (19.22%) | 233 (19.24%) | 58 (19.14%) |

---

### B. Four-Model Classification Comparison
**Objective:** To determine which conventional machine-learning classifier performs best when predicting the survey-defined Mental Health Impact category using leakage-controlled predictors.

All four conventional models were evaluated on the identical 54 leakage-controlled features and tested on the held-out test cohort ($N = 303$):

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **0.6799** | **0.6924** | **0.6820** | **0.6865** | **0.6811** |
| **Support Vector Machine (SVM)** | 0.6601 | 0.6695 | 0.6611 | 0.6646 | 0.6613 |
| **Logistic Regression** | 0.6502 | 0.6541 | 0.6488 | 0.6512 | 0.6507 |
| **Decision Tree** | 0.6139 | 0.6283 | 0.6133 | 0.6197 | 0.6183 |

**Result Summary:** Random Forest achieved the highest performance across all evaluation metrics (Accuracy = 0.6799, Macro F1 = 0.6865), followed closely by Support Vector Machine (Accuracy = 0.6601, Macro F1 = 0.6646), Logistic Regression (Accuracy = 0.6502, Macro F1 = 0.6512), and Decision Tree (Accuracy = 0.6139, Macro F1 = 0.6197).

---

### C. Leakage-Controlled vs. Full-Feature Benchmark Evaluation
To assess the vulnerability of survey-based ML models to target leakage, a controlled comparison was performed between the **Primary Random Forest** (54 features) and a **Benchmark Random Forest** (61 features):

| Model Representation | Features | Test Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Primary Random Forest — Leakage Controlled** | **54** | **0.6799** | **0.6924** | **0.6820** | **0.6865** | **0.6811** |
| **Benchmark Random Forest — Full Features / Leakage** | 61 | 0.8548 | 0.8669 | 0.8544 | 0.8591 | 0.8549 |

#### Scientific Explanation of Performance Gap:
- **Primary Model (54 Features):** Relies solely on true prospective predictors (demographics, platform usage habits, victimization exposure, cyberbullying frequency, and proactive coping actions).
- **Benchmark Model (61 Features):** Includes Question 13 (`Negative_Emotional_Symptoms`: Anxiety, Depression, Stress, None) and Question 14 (`Emotional_Impact_Severity`: 1 to 5 scale).
- **Reason for Inflation:** Questions 13 and 14 measure post-outcome psychological distress consequences that directly overlap with Question 12 (`Mental_Health_Impact`). Including them trivially inflates test accuracy from 67.99% to 85.48%. The benchmark model demonstrates the danger of target leakage and is **not** a deployable prospective risk model.

---

### D. 5-Fold Stratified Cross-Validation Results
Conducted strictly across the training set ($N = 1,211$) to evaluate algorithm stability without test data exposure:

| Model | Mean CV Accuracy $\pm$ SD | Mean CV Macro F1 $\pm$ SD | Mean CV Weighted F1 $\pm$ SD |
| :--- | :---: | :---: | :---: |
| **Random Forest** | **0.6705 $\pm$ 0.0270** | **0.6713 $\pm$ 0.0278** | **0.6686 $\pm$ 0.0265** |
| **Support Vector Machine (SVM)** | 0.6408 $\pm$ 0.0289 | 0.6388 $\pm$ 0.0293 | 0.6385 $\pm$ 0.0287 |
| **Logistic Regression** | 0.6235 $\pm$ 0.0329 | 0.6227 $\pm$ 0.0321 | 0.6204 $\pm$ 0.0326 |
| **Decision Tree** | 0.5649 $\pm$ 0.0422 | 0.5658 $\pm$ 0.0432 | 0.5652 $\pm$ 0.0416 |
| *Benchmark RF (Full Features / Leakage)* | *0.8118 $\pm$ 0.0226* | *0.8176 $\pm$ 0.0229* | *0.8121 $\pm$ 0.0229* |

---

### E. Per-Class Evaluation & Confusion Matrix (Primary Random Forest)
Evaluated on the held-out test partition ($N = 303$):

| Target Category | Precision | Recall | F1-Score | Support ($N=303$) |
| :--- | :---: | :---: | :---: | :---: |
| **Not at all** | 0.7500 | 0.7812 | **0.7653** | 96 |
| **Slightly** | 0.5060 | 0.5385 | **0.5217** | 78 |
| **Moderately** | 0.6061 | 0.5634 | **0.5839** | 71 |
| **Severely** | 0.9074 | 0.8448 | **0.8750** | 58 |
| **Macro Average** | **0.6924** | **0.6820** | **0.6865** | **303** |
| **Weighted Average** | **0.6836** | **0.6799** | **0.6811** | **303** |

#### Test Set Confusion Matrix ($N = 303$):
```
                    Predicted Category:
True Category       Not at all  Slightly  Moderately  Severely   Total
Not at all              75         17          4          0        96
Slightly                20         42         16          0        78
Moderately               5         21         40          5        71
Severely                 0          3          6         49        58
```
*Note: Severe misclassifications between opposite extremes ("Not at all" vs "Severely") are 0. Misclassifications occur primarily between adjacent ordinal categories, reflecting genuine real-world gradations in survey responses.*

---

### F. Tree SHAP Global Explainability Analysis
SHAP (Shapley Additive Explanations) via `TreeExplainer` was applied strictly to the selected Primary Random Forest model:

| Rank | Survey Feature Name | Mean Absolute SHAP | Empirical Survey Description |
| :---: | :--- | :---: | :--- |
| **1** | `Experienced_Cyberbullying_Binary` | **0.0471** | Personal direct cyberbullying exposure |
| **2** | `Sought_Help_No` | **0.0423** | Absence of informal/formal social support |
| **3** | `Cyberbullying_Frequency_Ordinal` | **0.0417** | Frequency of harassment encounters |
| **4** | `Action_Taken_Reported the account` | **0.0350** | Formal platform reporting response |
| **5** | `Action_Taken_Told Friends / Family` | **0.0328** | Interpersonal informal disclosure |
| **6** | `Sought_Help_Psychologist` | **0.0256** | Professional psychological help engagement |
| **7** | `Action_Taken_Ignored it` | **0.0177** | Passive avoidance coping strategy |
| **8** | `Sought_Help_Friends` | **0.0154** | Peer social support mobilization |
| **9** | `Action_Taken_Blocked the user` | **0.0144** | Digital barrier enforcement |
| **10** | `Action_Taken_Took No Action` | **0.0123** | Non-intervention behavioral response |
| **11** | `Sought_Help_Family` | **0.0112** | Familial support engagement |
| **12** | `Witnessed_Cyberbullying_Binary` | **0.0085** | Bystander observation of peer harassment |
| **13** | `Action_Taken_Sought Professional Help` | **0.0073** | Clinical/counseling coping response |
| **14** | `Daily_Usage_Ordinal` | **0.0054** | Screen time / daily platform usage intensity |
| **15** | `Sought_Help_Teacher` | **0.0050** | Academic institutional support seeking |

*Epistemological Clarification: SHAP values describe the mathematical contribution of a feature to the classifier's output across categories. They quantify feature importance within the predictive model and do not establish clinical diagnosis or medical causation.*

---

### G. Generated Research Figures
All 7 figures generated and saved at 300 DPI for IEEE manuscript publication:
1. **Fig. 1:** [`results/ml/plots/figure1_architecture.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure1_architecture.png) — Overall MindSafe operational architecture.
2. **Fig. 2:** [`results/ml/plots/figure2_target_distribution.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure2_target_distribution.png) — Target class distribution ($N = 1,514$).
3. **Fig. 3:** [`results/ml/plots/figure3_four_model_comparison.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure3_four_model_comparison.png) — Four-model test-set comparison (SVM vs RF vs LR vs DT).
4. **Fig. 4:** [`results/ml/plots/figure4_leakage_vs_benchmark.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure4_leakage_vs_benchmark.png) — Leakage-controlled RF vs Benchmark full-feature RF.
5. **Fig. 5:** [`results/ml/plots/figure5_cross_validation_comparison.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure5_cross_validation_comparison.png) — 5-Fold stratified cross-validation performance with error bars.
6. **Fig. 6:** [`results/ml/plots/figure6_confusion_matrix.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure6_confusion_matrix.png) — Primary Random Forest test-set confusion matrix.
7. **Fig. 7:** [`results/ml/plots/figure7_shap_importance.png`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/results/ml/plots/figure7_shap_importance.png) — Tree SHAP top-15 global feature importance.
