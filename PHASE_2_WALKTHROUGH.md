# MIND SAFE — PHASE 2 RESEARCH WALKTHROUGH
## Exploratory Data Analysis, Statistical Analysis & Feature Selection

**Project:** MindSafe: Cyberbullying, Mental Health, and Cyber Law Awareness Analysis  
**Dataset Source:** Primary Google Forms Survey (Original Empirical Responses)  
**Phase Completed:** Phase 2 — Analytical Cohort Refinement, Skip-Logic Recoding, Bivariate/Inferential Statistics, Target Leakage Audit, and Feature Selection  

---

### 1. Original Dataset Size
- **Total Raw Records:** **1,521**
- **Total Variables:** **19** questionnaire columns
- **Raw Data Status:** **100% Unmodified**
- **Cleaned Dataset:** Preserved at [`Data/processed/cleaned_survey_data.csv`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/Data/processed/cleaned_survey_data.csv).

---

### 2. Blank Records Removed
- **Completely Blank Submissions:** Exactly **2** submissions (Rows 21 and 80).
- **Audit Verification:** Both records contained only a Google Forms submission timestamp while leaving all 18 survey questions completely unattempted.
- **Incomplete Records Missing Target:** **5** submissions (Rows 16, 24, 25, 46, 70).
- **Total Records Dropped:** **7** records (0.46% of raw dataset).
- **Filtering Rule:** Filtered out strictly for analytical and ML integrity. Zero valid target responses were altered or deleted.

---

### 3. Final Analytical Dataset Size
- **Final Analytical Records ($N$):** **1,514**
- **Total Columns:** **19**
- **Location:** [`Data/processed/phase2_analysis_data.csv`](file:///c:/Users/pavit/OneDrive/Desktop/MindSafe/Data/processed/phase2_analysis_data.csv)
- **Traceability Equation:** $1,521 \text{ (Raw Responses)} - 7 \text{ (Blank & Incomplete Records)} = 1,514 \text{ (Analytical Cohort)}$.

---

### 4. Missing-Value Treatment
- **Protection of Legitimate Responses:** In Question 13 (*Which of the following did you experience?*), participants who selected `"None"` were strictly preserved as legitimate categorical responses and not converted to missing values.
- **True Missingness Across Analytical Cohort ($N = 1,514$):**
  - Demographics (Age, Gender): **0** missing (100% complete).
  - Target Variable (`Mental_Health_Impact`): **0** missing (100% complete across analytical cohort).
  - General Survey Questions: Average missingness below **1.2%**.

---

### 5. Structural Skip-Logic Treatment
Two questionnaire items featured conditional routing where blanks resulted from survey skip logic rather than non-response:

| Question Item | Prior Condition | Structural Skip Treatment |
| :--- | :--- | :--- |
| **Q8:** *If yes, what was the main reason for your action?* | Q7: *Posted offensive content* | Respondents who answered "No" to Q7 were not expected to answer Q8. Recoded explicitly as `"Not Applicable"`. |
| **Q16:** *If you did not report the incident, what was the main reason?* | Q5: *Experienced cyberbullying* & Q18: *Reported account* | Respondents who never experienced cyberbullying or reported the incident were not expected to answer Q16. Recoded explicitly as `"Not Applicable"`. |

---

### 6. Target Variable Distribution
The primary research target variable is **Mental Health Impact** (`[SECTION D: Mental Health Impact] 12. Do you think cyberbullying or online harassment affected your mental health?`):
- **Measurement Scale:** Ordinal Categorical (Rank: 0 = Not at all to 3 = Severely)
- **Valid Empirical Responses:** **1,514** (100.00%)

| Impact Category | Ordinal Score | Frequency | Valid % ($N=1,514$) |
| :--- | :---: | :---: | :---: |
| **Not at all** | 0 | 479 | 31.64% |
| **Slightly** | 1 | 387 | 25.56% |
| **Moderately** | 2 | 357 | 23.58% |
| **Severely** | 3 | 291 | 19.22% |
| **Total** | — | **1,514** | **100.00%** |

---

### 7. Descriptive Statistics
Descriptive statistics across the primary ordinal scales ($N = 1,514$):

| Scale Variable | Valid N | Mean | Median | Mode | Std Dev | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mental_Health_Impact** (0 to 3) | 1,514 | 1.304 | 1.000 | 0.000 | 1.118 | 0.000 | 3.000 |
| **Emotional_Impact_Severity** (1 to 5) | 1,509 | 2.580 | 2.000 | 1.000 | 1.455 | 1.000 | 5.000 |
| **Cyberbullying_Frequency** (0 to 4) | 1,512 | 1.378 | 1.000 | 1.000 | 1.171 | 0.000 | 4.000 |
| **Daily_Usage_Hours** (0 to 3) | 1,139 | 1.488 | 1.000 | 1.000 | 0.778 | 0.000 | 3.000 |

---

### 8. Inferential Statistical Analysis

#### A. Chi-Square Tests of Independence ($\chi^2$)
Testing bivariate associations with the target variable `Mental_Health_Impact`:

| Predictor Variable | Sample Size ($N$) | $\chi^2$ Statistic | $df$ | $p$-value | Cramér's $V$ | Association Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Cyberbullying Frequency (Q11)** | 1,512 | 818.036 | 12 | $2.24 \times 10^{-167}$ | 0.425 | **Statistically Significant** ($p < 0.001$) |
| **Experienced Cyberbullying (Q5)** | 1,513 | 555.765 | 3 | $3.91 \times 10^{-120}$ | 0.606 | **Statistically Significant** ($p < 0.001$, Strong) |
| **Witnessed Cyberbullying (Q6)** | 1,514 | 125.542 | 3 | $4.94 \times 10^{-27}$ | 0.288 | **Statistically Significant** ($p < 0.001$) |
| **Harassment Context Area (Q17)** | 1,505 | 93.073 | 21 | $4.74 \times 10^{-11}$ | 0.144 | **Statistically Significant** ($p < 0.001$) |
| **Daily Usage Hours (Q4)** | 1,139 | 74.408 | 15 | $7.24 \times 10^{-10}$ | 0.128 | **Statistically Significant** ($p < 0.001$) |
| **Incident Platform (Q10)** | 1,509 | 39.390 | 12 | $9.07 \times 10^{-5}$ | 0.100 | **Statistically Significant** ($p < 0.001$) |
| **Gender Identity (Q2)** | 1,514 | 10.439 | 9 | $0.3161$ | 0.048 | *Not Significant* ($p \ge 0.05$) |
| **Posted Offensive Content (Q7)** | 1,514 | 1.223 | 6 | $0.9757$ | 0.020 | *Not Significant* ($p \ge 0.05$) |

#### B. Independent Two-Sample Welch's T-Test
Comparing participants who experienced cyberbullying ($Q5 = \text{Yes}$) vs non-victims ($Q5 = \text{No}$):
- **Emotional Impact Severity (1–5 scale):**
  - Victims Mean: $3.411 \pm 1.367$ ($N=784$)
  - Non-Victims Mean: $1.680 \pm 0.921$ ($N=724$)
  - Difference: $+1.731$, $t = 29.027$, $p = 5.13 \times 10^{-145}$, Cohen's $d = 1.474$ (Large Effect).
- **Mental Health Impact Score (0–3 scale):**
  - Victims Mean: $1.949 \pm 0.962$ ($N=784$)
  - Non-Victims Mean: $0.610 \pm 0.794$ ($N=729$)
  - Difference: $+1.339$, $t = 29.601$, $p = 7.50 \times 10^{-152}$, Cohen's $d = 1.513$ (Large Effect).

#### C. Spearman Rank Correlation
Monotonic relationships between survey dimensions:
- **Emotional Impact Severity vs Mental Health Impact:** $\rho = 0.8073, p < 10^{-300}$ (Strong positive monotonic association).
- **Cyberbullying Frequency vs Mental Health Impact:** $\rho = 0.6011, p = 4.20 \times 10^{-149}$ (Substantial positive monotonic association).
- **Cyberbullying Frequency vs Emotional Impact Severity:** $\rho = 0.6064, p = 6.63 \times 10^{-152}$ (Substantial positive monotonic association).
- **Daily Usage Hours vs Mental Health Impact:** $\rho = 0.0442, p = 0.1362$ (Negligible, non-significant).

---

### 9. Target Leakage Control
To prevent analytical and model leakage:
1. **Excluded Feature 1:** `Negative_Emotional_Symptoms` (Question 13) — Directly reflects the acute outcome/symptom state of distress.
2. **Excluded Feature 2:** `Emotional_Impact_Severity` (Question 14) — Explicit Likert severity scale (1–5) serving as a direct post-outcome proxy for mental health impact.
3. **Excluded Features 3 & 4:** `Offensive_Action_Reason` (Q8) and `Reason_Not_Reported` (Q16) — Skip-logic conditional items with high sparsity.
4. **Primary Model Predictors:** Retained **13 predictor questions** spanning demographics, usage intensity, victimization, witnessing, platform, frequency, help-seeking, and coping actions, generating **54 numeric features**.
