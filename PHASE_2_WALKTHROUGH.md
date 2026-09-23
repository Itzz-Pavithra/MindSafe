# MIND SAFE — PHASE 2 RESEARCH WALKTHROUGH
## Exploratory Data Analysis, Statistical Analysis & Feature Selection

**Project:** MindSafe: Cyberbullying, Mental Health, and Cyber Law Awareness Analysis  
**Dataset Source:** Primary Google Forms Survey (Original Empirical Responses)  
**Phase Completed:** Phase 2 — Analytical Cohort Refinement, Skip-Logic Recoding, Bivariate/Inferential Statistics, Target Leakage Audit, and Feature Selection  

---

### 1. Original Dataset Size
- **Total Raw/Cleaned Records:** **521**
- **Total Variables:** **19** questionnaire columns
- **Raw Data Status:** **100% Unmodified** (`SHA-256: 090fa5883977de148bc01489b999f88ee02af7ed4132f7c53f785c61b25b46bf`)
- **Phase 1 Cleaned Dataset:** Preserved without modification at `Data/processed/cleaned_survey_data.csv`.

---

### 2. Blank Records Removed
- **Completely Blank Submissions:** Exactly **2** submissions (Rows 21 and 80).
- **Audit Verification:** Both records contained only a Google Forms submission timestamp while leaving all 18 survey questions completely unattempted.
- **Filtering Rule:** Filtered out strictly for Phase 2 analytical processing. No valid survey responses were altered or deleted.

---

### 3. Final Analytical Dataset Size
- **Final Analytical Records ($N$):** **519**
- **Total Columns:** **19**
- **Location:** [`Data/processed/phase2_analysis_data.csv`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/Data/processed/phase2_analysis_data.csv)
- **Traceability Equation:** $521 \text{ (Phase 1 Cleaned)} - 2 \text{ (Blank Submissions)} = 519 \text{ (Analytical Cohort)}$.

---

### 4. Missing-Value Treatment
- **Protection of Legitimate Responses:** In Question 13 (*Which of the following did you experience?*), **222 participants** explicitly checked `"None"` (indicating no negative psychological symptoms). These were strictly preserved as legitimate categorical responses and not converted to missing values.
- **True Missingness Across Analytical Cohort ($N = 519$):**
  - Demographics (Age, Gender): **0** missing (100% complete).
  - Social Media Hours & Platforms: **0** missing (100% complete).
  - Target Variable (`Mental_Health_Impact`): **5** missing (0.96%).
  - General Survey Questions: Average missingness below **1.5%**.

---

### 5. Structural Skip-Logic Treatment
Two questionnaire items featured conditional routing where blanks resulted from survey skip logic rather than non-response:

| Question Item | Prior Condition | Original Missing ($N=519$) | Structural Skip Count | True Missing Count | Recoding & Treatment |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Q8:** *If yes, what was the main reason for your action?* | Q7: *Posted offensive content* | 372 | **371** | **1** | 371 respondents answered "No" to Q7 and were not expected to answer Q8. Recoded explicitly as `"Not Applicable"`. 1 true missing retained as `NaN`. |
| **Q16:** *If you did not report the incident, what was the main reason?* | Q5: *Experienced cyberbullying* & Q18: *Reported account* | 92 | **91** | **1** | 88 respondents never experienced cyberbullying (Q5 == "No") and 3 respondents reported the account in Q18. Recoded explicitly as `"Not Applicable"`. 1 true missing retained as `NaN`. |

---

### 6. Target Variable Distribution
The primary research target variable is **Mental Health Impact** (`[SECTION D: Mental Health Impact] 12. Do you think cyberbullying or online harassment affected your mental health?`):
- **Measurement Scale:** Ordinal Categorical (Rank: 0 = Not at all to 3 = Severely)
- **Valid Empirical Responses:** **514** (99.04%)
- **Missing Responses:** **5** (0.96%)

| Impact Category | Ordinal Score | Frequency | Valid % ($N=514$) | Total % ($N=519$) |
| :--- | :---: | :---: | :---: | :---: |
| **Not at all** | 0 | 229 | 44.55% | 44.12% |
| **Slightly** | 1 | 137 | 26.65% | 26.40% |
| **Moderately** | 2 | 107 | 20.82% | 20.62% |
| **Severely** | 3 | 41 | 7.98% | 7.90% |
| *Missing (NaN)* | — | 5 | — | 0.96% |

---

### 7. Descriptive Statistics Performed
Central tendency and dispersion metrics were calculated for ordinal and numerical scale variables (nominal variables were strictly summarized using counts and proportions):

| Scale Variable | Valid $N$ | Mean | Median | Mode | Std Dev | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Emotional Impact Severity** (1 to 5 Likert Scale) | 509 | 2.094 | 2.000 | 1.000 | 1.218 | 1.000 | 5.000 |
| **Mental Health Impact** (0 to 3 Ordinal Score) | 514 | 0.922 | 1.000 | 0.000 | 0.998 | 0.000 | 3.000 |
| **Cyberbullying Frequency** (0 to 4 Ordinal Score) | 512 | 0.941 | 1.000 | 0.000 | 1.007 | 0.000 | 4.000 |
| **Daily Usage Hours** (0 to 3 Ordinal Score) | 519 | 1.516 | 1.000 | 1.000 | 0.852 | 0.000 | 3.000 |

---

### 8. Chi-Square Tests of Independence
Bivariate tests evaluated statistical dependence between survey predictors and `Mental_Health_Impact` ($\alpha = 0.05$):

| Predictor Variable | Sample $N$ | $\chi^2$ Stat | $df$ | $p$-value | Significance ($\alpha = 0.05$) | Statistical Interpretation |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Experienced_Cyberbullying** | 513 | **146.281** | 3 | **$1.67 \times 10^{-31}$** | **Significant** | Strong sample evidence of dependence between personal cyberbullying victimization and mental health impact. |
| **Cyberbullying_Frequency** | 511 | **51.744** | 12 | **$6.88 \times 10^{-7}$** | **Significant** | Statistically significant association; higher bullying recurrence corresponds with greater impact. |
| **Incident_Platform** | 508 | **21.736** | 12 | **$0.0406$** | **Significant** | Statistically significant association between specific social media platform where incident occurred and impact. |
| **Posted_Offensive_Content** | 514 | 11.790 | 6 | $0.0668$ | Not Significant | Marginally non-significant at $\alpha = 0.05$; suggestive pattern requiring further investigation. |
| **Gender** | 514 | 13.588 | 9 | $0.1377$ | Not Significant | Null hypothesis of independence cannot be rejected across gender categories in this sample. |
| **Harassment_Context_Area** | 505 | 24.442 | 21 | $0.2721$ | Not Significant | Null hypothesis of independence cannot be rejected across social context categories. |
| **Witnessed_Cyberbullying** | 514 | 3.340 | 3 | $0.3421$ | Not Significant | Bystander witnessing alone does not show a statistically significant bivariate association with self impact. |
| **Daily_Usage_Hours** | 514 | 8.981 | 9 | $0.4390$ | Not Significant | Total daily screen time does not demonstrate a statistically significant bivariate association with impact. |

---

### 9. Independent-Samples T-Test Assessment
An independent-samples t-test was validated by pairing a scale metric (**Emotional Impact Severity**, 1 to 5 scale) with a two-group factor (**Experienced Cyberbullying**, Yes vs No):
- **Group 1 (Victimized - Yes):** $N_1 = 168, \text{Mean}_1 = 3.042, \text{SD}_1 = 1.264$
- **Group 2 (Non-Victimized - No):** $N_2 = 340, \text{Mean}_2 = 1.638, \text{SD}_2 = 0.863$
- **Mean Difference:** $+1.404$ scale points
- **Welch's T-Test (Unequal Variances):** $t = 12.976, df = 250.7, p = 1.08 \times 10^{-29}$
- **Student's T-Test (Pooled Variance):** $t = 14.691, df = 506, p = 5.97 \times 10^{-41}$
- **Statistical Interpretation:** Respondents who personally experienced cyberbullying reported statistically significantly higher emotional impact severity than non-victimized respondents ($p < 0.001$).

---

### 10. Correlation Analysis (Spearman Rank)
Monotonic relationships were evaluated among ordinal variables using Spearman rank correlation ($\rho$):

| Variable 1 | Variable 2 | Sample $N$ | Spearman $\rho$ | $p$-value | Significance | Interpretation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Cyberbullying Frequency** | **Mental Health Impact** | 511 | **$+0.2420$** | **$3.02 \times 10^{-8}$** | **Significant** | Statistically significant positive monotonic association; increasing chronicity correlates with increased impact. |
| **Emotional Severity (1-5)** | **Mental Health Impact** | 509 | **$+0.3185$** | **$1.85 \times 10^{-13}$** | **Significant** | Statistically significant positive correlation reflecting convergent measurement of distress. |
| **Cyberbullying Frequency** | **Emotional Severity (1-5)** | 506 | **$+0.2776$** | **$2.08 \times 10^{-10}$** | **Significant** | Statistically significant positive monotonic relationship between recurrence and emotional severity. |
| **Daily Usage Hours** | **Mental Health Impact** | 514 | $-0.0183$ | $0.6794$ | Not Significant | No monotonic relationship observed between screen time and mental health impact. |
| **Daily Usage Hours** | **Emotional Severity** | 509 | $+0.0358$ | $0.4200$ | Not Significant | No significant correlation with emotional severity. |
| **Daily Usage Hours** | **Cyberbullying Frequency**| 512 | $-0.0583$ | $0.1880$ | Not Significant | Screen time alone does not correlate monotonically with cyberbullying frequency. |

---

### 11. Target Leakage Findings & Scenario Protocol
A critical methodological audit evaluated construct overlap with the target variable `Mental_Health_Impact`:
- **Question 13 (`Negative_Emotional_Symptoms`):** Measures anxiety, depression, anger, stress, and loss of confidence.
- **Question 14 (`Emotional_Impact_Severity`):** Direct 1–5 emotional severity scale.
- **Risk Assessment:** These variables measure the psychological reaction to cyberbullying rather than the external exposure or protective factors. Including them creates trivial shortcut learning where an ML model infers "Depressed $\rightarrow$ Severe Impact", bypassing actual cyberbullying risk signals.
- **Dual Scenario Protocol Established:**
  - **Scenario A (Full Benchmark Features):** Includes all survey predictors (useful for upper-bound diagnostic comparison).
  - **Scenario B (Leakage-Controlled Features):** Excludes Questions 13 & 14, requiring ML models to predict mental health vulnerability strictly from exposure, platform, behavioural, and demographic covariates.

---

### 12. Candidate Features
The following features are designated as **Candidate** features for Phase 3 ML modeling:
1. `Age` (Demographic covariate)
2. `Gender` (Demographic covariate)
3. `Platforms_Used` (Multiselect exposure)
4. `Daily_Usage_Hours` (Usage intensity)
5. `Experienced_Cyberbullying` (Primary predictor, $\chi^2 = 146.28, p < 10^{-30}$)
6. `Witnessed_Cyberbullying` (Bystander exposure)
7. `Posted_Offensive_Content` (Online conduct/perpetration)
8. `Cyberbullying_Types_Observed` (Harassment modality taxonomy)
9. `Incident_Platform` (Platform vulnerability context, $\chi^2 = 21.74, p = 0.041$)
10. `Cyberbullying_Frequency` (Chronicity predictor, $\chi^2 = 51.74, p < 10^{-6}, \rho = +0.242$)
11. `Sought_Help` (Coping mechanism / formal-informal psychological support)
12. `Harassment_Context_Area` (Contextual/relational environment)
13. `Action_Taken` (Protective behavioural coping actions)

---

### 13. Excluded Features and Features Under Review
- **Excluded:**
  - `Timestamp`: Excluded as an uninformative Google Forms temporal artifact.
- **Under Review (Controlled Deployment):**
  - `Negative_Emotional_Symptoms` (Q13): High target leakage risk. Included in Scenario A; excluded in Scenario B.
  - `Emotional_Impact_Severity` (Q14): High target leakage risk. Included in Scenario A; excluded in Scenario B.
  - `Offensive_Action_Reason` (Q8): High skip sparsity (71.5% Not Applicable). Requires dedicated indicator encoding if utilized.
  - `Reason_Not_Reported` (Q16): Skip sparsity (17.5% Not Applicable). Requires dedicated indicator encoding if utilized.

---

### 14. Generated Files and Directory Structure

All files have been verified and saved under `Data/processed/` and `notebook/`:

```
Data/
├── raw/
│   └── Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv
│
└── processed/
    ├── cleaned_survey_data.csv                 (Phase 1 Cleaned Dataset: 521 rows)
    ├── data_quality_report.csv                 (Phase 1 Diagnostic Report: 19 rows)
    ├── phase2_analysis_data.csv                (Phase 2 Analytical Dataset: 519 rows)
    ├── statistical_results.csv                 (Master Statistical Compilation)
    ├── chi_square_results.csv                  (Bivariate Chi-Square Test Results)
    ├── t_test_results.csv                      (Independent-Samples T-Test Results)
    ├── correlation_results.csv                 (Spearman Rank Correlation Matrix)
    ├── feature_selection_results.csv           (Feature Screening Matrix)
    ├── mental_health_impact_distribution.csv   (Target Frequency Table)
    ├── demographic_distribution.csv            (Table 1: Demographics)
    ├── social_media_usage.csv                  (Table 2: Usage Hours)
    ├── cyberbullying_experience.csv            (Table 3: Cyberbullying Exposure)
    └── descriptive_statistics.csv              (Table 5: Scale Metrics)

notebook/
├── 01_data_preprocessing.ipynb                 (Phase 1 Executed Notebook: 13 sections)
└── 02_statistical_analysis.ipynb               (Phase 2 Executed Notebook: 16 sections, 10 plots)
```

---

### 15. Methodological Decisions Requiring Your Approval Before Phase 3

Before initiating **Phase 3: Machine Learning Model Development & Validation**, please confirm your approval on the following:

1. **Adoption of Scenario B as the Primary ML Benchmark:**
   - We recommend evaluating **both** Scenario A (Full) and Scenario B (Leakage-Controlled without Q13/Q14) in the ML phase, reporting Scenario B as the primary scientific contribution so that predictive performance is genuine and clinically meaningful.
2. **Encoding Strategy for Multiselect Variables:**
   - Questions 3 (`Platforms_Used`), 9 (`Cyberbullying_Types_Observed`), 15 (`Sought_Help`), and 18 (`Action_Taken`) contain comma-separated multi-select checkboxes. In Phase 3, we propose multi-hot binary indicator encoding (one binary column per unique option).
3. **ML Target Formulation:**
   - The primary target has 4 ordinal classes (`Not at all`, `Slightly`, `Moderately`, `Severely`).
   - We will implement multi-class ordinal/classification models (Random Forest, XGBoost, LightGBM, Logistic Regression) and evaluate both 4-class multi-class classification and binary classification (Minimal Impact vs. Moderate-to-Severe Impact).
