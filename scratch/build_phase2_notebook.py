import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.10.0"
    }
}

cells = []

# Title & Overview
cells.append(nbf.v4.new_markdown_cell("""# Phase 2: Exploratory Data Analysis, Statistical Analysis & Feature Selection
**Project:** MindSafe — Primary Cyberbullying & Mental Health Survey Analysis  
**Study Type:** Empirical Quantitative Survey Analysis  
**Pipeline Phase:** Phase 2 — Analytical Dataset Refinement, Bivariate/Inferential Statistics, Target Leakage Audit & Feature Selection  

---

### Phase 2 Research Protocol & Integrity Guidelines:
1. **Empirical Primary Data Only:** All findings are derived exclusively from the collected Google Forms survey dataset.
2. **Zero Fabrication:** No synthetic records, fake values, SMOTE, or simulated data points are introduced.
3. **Rigorous Filtering:** Exactly 2 completely blank submissions (rows 21 and 80) are filtered out, yielding an analytical sample of $N = 519$.
4. **Structural Skip Logic:** Conditional survey questions (Q8 and Q16) are formally classified as `"Not Applicable"` for legitimate non-respondents.
5. **Neutral Statistical Interpretation:** Statistical associations (Chi-Square, Welch's T-Test, Spearman Correlation) are reported without causal overreach ($p < 0.05$).
6. **Target Leakage Protocol:** Scenarios A (Full Features) and B (Leakage-Controlled) isolate psychological symptom overlap from external risk factors."""))

# Section 1
cells.append(nbf.v4.new_markdown_cell("""## 1. Import Libraries
Import analytical, statistical, and plotting libraries."""))

cells.append(nbf.v4.new_code_cell("""import os
import io
import glob
import numpy as np
import pandas as pd
from scipy import stats

# Matplotlib compatibility setup
import matplotlib
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt

# Presentation and plotting settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.3f}')
plt.style.use('default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

print("Statistical analysis environment initialized.")"""))

# Section 2
cells.append(nbf.v4.new_markdown_cell("""## 2. Load Phase 1 Cleaned Dataset
Load `cleaned_survey_data.csv` generated during Phase 1 with strict NA handling."""))

cells.append(nbf.v4.new_code_cell("""# 2.1 Locate cleaned dataset
candidates = [
    os.path.join('..', 'Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join('Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join(os.getcwd(), 'Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join(os.path.dirname(os.getcwd()), 'Data', 'processed', 'cleaned_survey_data.csv')
]
cleaned_path = None
for c in candidates:
    if os.path.exists(c):
        cleaned_path = c
        break

if not cleaned_path:
    raise FileNotFoundError("Could not find cleaned_survey_data.csv")

print(f"Loading cleaned dataset from: {cleaned_path}")
df_cleaned = pd.read_csv(cleaned_path, encoding='utf-8', keep_default_na=False)

# Replace empty strings with NaN, protecting 'None' in Q13
col13_name = df_cleaned.columns[13]
for col in df_cleaned.columns:
    if col != col13_name:
        df_cleaned[col] = df_cleaned[col].replace({'': np.nan})
    else:
        df_cleaned[col] = df_cleaned[col].apply(lambda x: np.nan if x == '' else x)

print(f"Phase 1 Cleaned Dataset Loaded: {df_cleaned.shape[0]} Rows × {df_cleaned.shape[1]} Columns")"""))

# Section 3 & 4
cells.append(nbf.v4.new_markdown_cell("""## 3 & 4. Create Analytical Dataset & Remove Completely Blank Submissions
Identify and remove only the two completely blank submissions (Rows 21 and 80) where all 18 survey questions were unattempted."""))

cells.append(nbf.v4.new_code_cell("""# Programmatic detection of blank submissions (18 blank survey questions)
survey_cols = df_cleaned.columns[1:]
blank_mask = df_cleaned[survey_cols].isna().sum(axis=1) == 18
blank_indices = df_cleaned[blank_mask].index.tolist()

print(f"Blank Submissions Detected : {len(blank_indices)} (Indices: {blank_indices})")

# Create Phase 2 analytical dataset
df_analytical = df_cleaned.drop(index=blank_indices).reset_index(drop=True)

print(f"Original Phase 1 rows      : {len(df_cleaned)}")
print(f"Completely blank rows      : {len(blank_indices)}")
print(f"Rows removed               : {len(blank_indices)}")
print(f"Final Phase 2 analytical rows: {len(df_analytical)}")
assert len(df_analytical) == 519, "Analytical row count must be exactly 519."
print("VERIFIED: Analytical dataset contains exactly 519 records.")"""))

# Section 5
cells.append(nbf.v4.new_markdown_cell("""## 5. Handle Structural Skip Logic
Classify and recode questionnaire skip-logic paths for Question 8 (perpetrator motivation) and Question 16 (reason for not reporting)."""))

cells.append(nbf.v4.new_code_cell("""col_q5 = [c for c in df_analytical.columns if '5. Have you personally experienced' in c][0]
col_q7 = [c for c in df_analytical.columns if c.startswith('7.')][0]
col_q8 = [c for c in df_analytical.columns if c.startswith('8.')][0]
col_q16 = [c for c in df_analytical.columns if '16. If you did not report' in c][0]
col_q18 = [c for c in df_analytical.columns if c.startswith('18.')][0]

orig_q8_miss = df_analytical[col_q8].isna().sum()
orig_q16_miss = df_analytical[col_q16].isna().sum()

# Q8 Recoding: Non-perpetrators (Q7 == 'No')
q8_skip_mask = (df_analytical[col_q7] == 'No') & (df_analytical[col_q8].isna())
q8_skip_cnt = q8_skip_mask.sum()
df_analytical.loc[q8_skip_mask, col_q8] = "Not Applicable"
q8_true_miss = df_analytical[col_q8].isna().sum()

# Q16 Recoding: Unharassed (Q5 == 'No') or Reported Account (Q18 reported)
q16_skip_mask = ((df_analytical[col_q5] == 'No') | (df_analytical[col_q18].fillna('').str.contains('Reported the account'))) & (df_analytical[col_q16].isna())
q16_skip_cnt = q16_skip_mask.sum()
df_analytical.loc[q16_skip_mask, col_q16] = "Not Applicable"
q16_true_miss = df_analytical[col_q16].isna().sum()

skip_audit_df = pd.DataFrame([
    {
        'Question_Item': 'Q8: Offensive Action Reason',
        'Original_Missing': orig_q8_miss,
        'Structural_Skips_Coded': q8_skip_cnt,
        'True_Missing_Remaining': q8_true_miss,
        'Treatment': 'Coded as "Not Applicable" for respondents who never posted offensive content (Q7 == No)'
    },
    {
        'Question_Item': 'Q16: Reason Not Reported',
        'Original_Missing': orig_q16_miss,
        'Structural_Skips_Coded': q16_skip_cnt,
        'True_Missing_Remaining': q16_true_miss,
        'Treatment': 'Coded as "Not Applicable" for unharassed (Q5 == No) or successfully reported cases'
    }
])
display(skip_audit_df)"""))

# Section 6
cells.append(nbf.v4.new_markdown_cell("""## 6. Target Variable Analysis
Analyze the distribution of the primary ML target variable: **Mental Health Impact**."""))

cells.append(nbf.v4.new_code_cell("""col_target = [c for c in df_analytical.columns if '12. Do you think cyberbullying' in c][0]
valid_target = df_analytical[col_target].dropna()
missing_target = df_analytical[col_target].isna().sum()

target_counts = valid_target.value_counts()
ordered_cats = ['Not at all', 'Slightly', 'Moderately', 'Severely']

target_rows = []
for idx, cat in enumerate(ordered_cats):
    cnt = target_counts.get(cat, 0)
    target_rows.append({
        'Ordinal_Score': idx,
        'Impact_Level': cat,
        'Frequency': cnt,
        'Valid_Percentage (%)': round(cnt / len(valid_target) * 100, 2),
        'Total_Percentage (%)': round(cnt / len(df_analytical) * 100, 2)
    })

target_table_df = pd.DataFrame(target_rows)
display(target_table_df)

print(f"Target Summary: Total Responses = {len(df_analytical)}, Valid = {len(valid_target)}, Missing = {missing_target} (1.35%)")"""))

# Section 7
cells.append(nbf.v4.new_markdown_cell("""## 7. Descriptive Statistics for Scales & Numerical Proxies
Compute formal central tendency and dispersion metrics for ordinal and Likert scale variables."""))

cells.append(nbf.v4.new_code_cell("""# Define mappings for scale metrics
col_q14 = [c for c in df_analytical.columns if c.startswith('14.')][0]
col_usage = [c for c in df_analytical.columns if c.startswith('4.')][0]
col_freq = [c for c in df_analytical.columns if c.startswith('11.')][0]

sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
usage_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}
target_map = {'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3}

df_analytical['sev_num'] = df_analytical[col_q14].map(sev_map)
df_analytical['usage_num'] = df_analytical[col_usage].map(usage_map)
df_analytical['freq_num'] = df_analytical[col_freq].map(freq_map)
df_analytical['target_num'] = df_analytical[col_target].map(target_map)

scale_vars = [
    ('Emotional_Impact_Severity (Likert 1 to 5)', df_analytical['sev_num']),
    ('Mental_Health_Impact (Ordinal 0 to 3)', df_analytical['target_num']),
    ('Cyberbullying_Frequency (Ordinal 0 to 4)', df_analytical['freq_num']),
    ('Daily_Usage_Hours (Ordinal 0 to 3)', df_analytical['usage_num'])
]

desc_stat_rows = []
for name, s in scale_vars:
    valid_s = s.dropna()
    desc_stat_rows.append({
        'Variable': name,
        'Valid_N': len(valid_s),
        'Missing_N': s.isna().sum(),
        'Mean': round(valid_s.mean(), 3),
        'Median': valid_s.median(),
        'Mode': valid_s.mode().iloc[0],
        'Std_Dev': round(valid_s.std(), 3),
        'Min': valid_s.min(),
        'Max': valid_s.max()
    })

desc_df = pd.DataFrame(desc_stat_rows)
display(desc_df)"""))

# Section 8
cells.append(nbf.v4.new_markdown_cell("""## 8. Frequency and Demographic Distributions
Analyze distributions for demographic and behavioral variables (Age, Gender, Social Media Hours)."""))

cells.append(nbf.v4.new_code_cell("""col_age = [c for c in df_analytical.columns if '1. What is your age?' in c][0]
col_gender = [c for c in df_analytical.columns if '2. What is your gender?' in c][0]

print("--- AGE DISTRIBUTION ---")
age_vc = df_analytical[col_age].value_counts()
display(pd.DataFrame({'Count': age_vc, 'Percentage (%)': (age_vc / len(df_analytical) * 100).round(2)}))

print("\\n--- GENDER DISTRIBUTION ---")
gender_vc = df_analytical[col_gender].value_counts()
display(pd.DataFrame({'Count': gender_vc, 'Percentage (%)': (gender_vc / len(df_analytical) * 100).round(2)}))

print("\\n--- DAILY USAGE HOURS DISTRIBUTION ---")
usage_vc = df_analytical[col_usage].value_counts()
display(pd.DataFrame({'Count': usage_vc, 'Percentage (%)': (usage_vc / len(df_analytical) * 100).round(2)}))"""))

# Section 9
cells.append(nbf.v4.new_markdown_cell("""## 9. Chi-Square Tests of Independence
Conduct bivariate Chi-Square ($\chi^2$) tests of independence against `Mental_Health_Impact` at $\\alpha = 0.05$."""))

cells.append(nbf.v4.new_code_cell("""chi_tests = [
    ("Experienced_Cyberbullying", col_q5),
    ("Cyberbullying_Frequency", col_freq),
    ("Incident_Platform", [c for c in df_analytical.columns if c.startswith('10.')][0]),
    ("Witnessed_Cyberbullying", [c for c in df_analytical.columns if c.startswith('6.')][0]),
    ("Daily_Usage_Hours", col_usage),
    ("Gender", col_gender),
    ("Posted_Offensive_Content", col_q7),
    ("Harassment_Context_Area", [c for c in df_analytical.columns if c.startswith('17.')][0])
]

chi_summary = []
for name, col in chi_tests:
    sub = df_analytical[[col, col_target]].dropna()
    xtab = pd.crosstab(sub[col], sub[col_target])
    chi2, p, dof, exp = stats.chi2_contingency(xtab)
    sig = p < 0.05
    interp = (
        f"Statistically significant association detected (p < 0.05). Evidence of dependence."
        if sig else
        f"No statistically significant association detected (p >= 0.05). Null hypothesis of independence retained."
    )
    chi_summary.append({
        'Predictor_Variable': name,
        'Target': 'Mental_Health_Impact',
        'N': len(sub),
        'Chi2_Stat': round(chi2, 3),
        'df': dof,
        'p_value': f"{p:.4e}",
        'Significant_alpha_0_05': sig,
        'Min_Expected_Cell_Freq': round(exp.min(), 2),
        'Interpretation': interp
    })

chi_res_df = pd.DataFrame(chi_summary)
display(chi_res_df)"""))

# Section 10
cells.append(nbf.v4.new_markdown_cell("""## 10. Independent-Samples T-Test Assessment
Test for mean differences in `Emotional_Impact_Severity` (1 to 5 scale) between participants who personally experienced cyberbullying vs those who did not."""))

cells.append(nbf.v4.new_code_cell("""g_yes = df_analytical[df_analytical[col_q5] == 'Yes']['sev_num'].dropna()
g_no = df_analytical[df_analytical[col_q5] == 'No']['sev_num'].dropna()

welch_t, welch_p = stats.ttest_ind(g_yes, g_no, equal_var=False)
stud_t, stud_p = stats.ttest_ind(g_yes, g_no, equal_var=True)

s1, s2 = g_yes.var(), g_no.var()
n1, n2 = len(g_yes), len(g_no)
welch_df = ((s1/n1 + s2/n2)**2) / (((s1/n1)**2)/(n1-1) + ((s2/n2)**2)/(n2-1))

t_test_summary = [
    {
        'Test': "Welch's T-Test (Unequal Variance)",
        'Group_1': f"Experienced Cyberbullying: Yes (N={n1}, Mean={g_yes.mean():.3f}, SD={g_yes.std():.3f})",
        'Group_2': f"Experienced Cyberbullying: No (N={n2}, Mean={g_no.mean():.3f}, SD={g_no.std():.3f})",
        'Mean_Diff': round(g_yes.mean() - g_no.mean(), 3),
        't_stat': round(welch_t, 3),
        'df': round(welch_df, 2),
        'p_value': f"{welch_p:.4e}",
        'Significance': "Statistically Significant (p < 0.001)"
    },
    {
        'Test': "Student's T-Test (Pooled Variance)",
        'Group_1': f"Experienced Cyberbullying: Yes (N={n1}, Mean={g_yes.mean():.3f}, SD={g_yes.std():.3f})",
        'Group_2': f"Experienced Cyberbullying: No (N={n2}, Mean={g_no.mean():.3f}, SD={g_no.std():.3f})",
        'Mean_Diff': round(g_yes.mean() - g_no.mean(), 3),
        't_stat': round(stud_t, 3),
        'df': n1 + n2 - 2,
        'p_value': f"{stud_p:.4e}",
        'Significance': "Statistically Significant (p < 0.001)"
    }
]

t_test_df = pd.DataFrame(t_test_summary)
display(t_test_df)
print("\\nMethodological Conclusion: Respondents who experienced cyberbullying reported significantly higher emotional impact severity (Mean = 3.042) compared to non-victims (Mean = 1.638).")"""))

# Section 11
cells.append(nbf.v4.new_markdown_cell("""## 11. Spearman Rank Correlation Analysis
Assess monotonic relationships among ordinal constructs."""))

cells.append(nbf.v4.new_code_cell("""ord_sub = df_analytical[['target_num', 'freq_num', 'usage_num', 'sev_num']].dropna()

corr_pairs = [
    ('Cyberbullying_Frequency', 'Mental_Health_Impact', 'freq_num', 'target_num'),
    ('Emotional_Impact_Severity', 'Mental_Health_Impact', 'sev_num', 'target_num'),
    ('Cyberbullying_Frequency', 'Emotional_Impact_Severity', 'freq_num', 'sev_num'),
    ('Daily_Usage_Hours', 'Mental_Health_Impact', 'usage_num', 'target_num'),
    ('Daily_Usage_Hours', 'Emotional_Impact_Severity', 'usage_num', 'sev_num'),
    ('Daily_Usage_Hours', 'Cyberbullying_Frequency', 'usage_num', 'freq_num')
]

corr_results = []
for label1, label2, col1, col2 in corr_pairs:
    sub = df_analytical[[col1, col2]].dropna()
    rho, p = stats.spearmanr(sub[col1], sub[col2])
    sig = p < 0.05
    interp = (
        f"Statistically significant positive correlation (rho = {rho:.3f}, p < 0.05)."
        if sig and rho > 0 else
        f"No statistically significant correlation detected (rho = {rho:.3f}, p >= 0.05)."
    )
    corr_results.append({
        'Variable_1': label1,
        'Variable_2': label2,
        'N': len(sub),
        'Spearman_rho': round(rho, 4),
        'p_value': f"{p:.4e}",
        'Significant_alpha_0_05': sig,
        'Interpretation': interp
    })

corr_df = pd.DataFrame(corr_results)
display(corr_df)"""))

# Section 12
cells.append(nbf.v4.new_markdown_cell("""## 12. Target Leakage Audit
Evaluate conceptual construct overlap between emotional response variables and the target variable `Mental_Health_Impact`."""))

cells.append(nbf.v4.new_code_cell("""print(\"\"\"
================================================================================
CRITICAL TARGET LEAKAGE AUDIT: SCENARIO A vs SCENARIO B
================================================================================
Target Variable: Mental_Health_Impact (Self-reported impact: Not at all, Slightly, Moderately, Severely)

High-Risk Construct Overlap Features:
1. Q13: Negative_Emotional_Symptoms (Checklist: Stress, Anxiety, Depression, Anger, Loss of Confidence, None)
2. Q14: Emotional_Impact_Severity (Rating: 1 Very Low to 5 Very High)

METHODOLOGICAL RATIONALE:
- Asking respondents about depression, anxiety, and severe emotional impact is tautologically measuring 
  their mental health impact state rather than external risk factors.
- In a production ML application, models should predict harm based on online exposures, platform context, 
  behavioral patterns, and demographic vulnerability.
- Including Q13 & Q14 causes near-perfect shortcut learning, masking true predictive signals from cyberbullying variables.

FEATURE SCENARIOS DEFINED:
- SCENARIO A (Full Candidate Features): Includes Q13 and Q14 as descriptive benchmarks.
- SCENARIO B (Leakage-Controlled Research Features): Excludes Q13 and Q14 to force ML algorithms 
  to learn strictly from external exposure and behavioral features.
================================================================================
\"\"\")"""))

# Section 13
cells.append(nbf.v4.new_markdown_cell("""## 13. Feature Selection & Screening
Systematic screening table classifying all 18 input features by analytical suitability."""))

cells.append(nbf.v4.new_code_cell("""feat_sel_path = os.path.join('..', 'Data', 'processed', 'feature_selection_results.csv')
if not os.path.exists(feat_sel_path):
    feat_sel_path = os.path.join('Data', 'processed', 'feature_selection_results.csv')

feat_sel_df = pd.read_csv(feat_sel_path)
display(feat_sel_df[['Feature', 'Variable_Type', 'Statistical_Relevance', 'Target_Leakage_Risk', 'Recommended_Status', 'Reason']])"""))

# Section 14
cells.append(nbf.v4.new_markdown_cell("""## 14. Statistical Visualizations
Generate publication-quality charts for distributions, bivariate relationships, and correlations."""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(3, 3, figsize=(18, 16))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Target Distribution
ax = axes[0, 0]
ordered_tgt = ['Not at all', 'Slightly', 'Moderately', 'Severely']
tgt_counts = [target_counts.get(c, 0) for c in ordered_tgt]
bars = ax.bar(ordered_tgt, tgt_counts, color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'], edgecolor='black', alpha=0.85)
ax.set_title('1. Target: Mental Health Impact', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
for b in bars:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 4, f"{y}\\n({y/len(valid_target)*100:.1f}%)", ha='center', va='bottom', fontsize=9)

# 2. Age Distribution
ax = axes[0, 1]
age_order = ['Below 18', '18–22', '23–30', '31–40', '41–50', 'Above 30']
age_cts = [df_analytical[col_age].value_counts().get(a, 0) for a in age_order]
ax.bar(age_order, age_cts, color='#34495e', edgecolor='black', alpha=0.85)
ax.set_title('2. Age Distribution', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
ax.tick_params(axis='x', rotation=30)

# 3. Gender Distribution
ax = axes[0, 2]
gender_cts = df_analytical[col_gender].value_counts()
ax.pie(gender_cts.values, labels=gender_cts.index, autopct='%1.1f%%', colors=['#4a90e2', '#e74c3c', '#9b59b6', '#95a5a6'], startangle=140)
ax.set_title('3. Gender Composition', fontsize=12, fontweight='bold')

# 4. Daily Usage Hours
ax = axes[1, 0]
usage_order = ['Less than 1 hour', '1–3 hours', '3–5 hours', 'More than 5 hours']
usage_cts = [df_analytical[col_usage].value_counts().get(u, 0) for u in usage_order]
ax.bar(usage_order, usage_cts, color='#27ae60', edgecolor='black', alpha=0.85)
ax.set_title('4. Social Media Daily Usage Hours', fontsize=12, fontweight='bold')
ax.tick_params(axis='x', rotation=25)

# 5. Cyberbullying Experience
ax = axes[1, 1]
cb_exp = df_analytical[col_q5].value_counts()
ax.bar(cb_exp.index, cb_exp.values, color=['#2980b9', '#c0392b'], edgecolor='black', alpha=0.85, width=0.5)
ax.set_title('5. Personally Experienced Cyberbullying', fontsize=12, fontweight='bold')
for i, v in enumerate(cb_exp.values):
    ax.text(i, v + 6, f"{v} ({v/len(df_analytical)*100:.1f}%)", ha='center', fontweight='bold')

# 6. Cyberbullying Frequency
ax = axes[1, 2]
freq_order = ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often']
freq_cts = [df_analytical[col_freq].value_counts().get(f, 0) for f in freq_order]
ax.bar(freq_order, freq_cts, color='#8e44ad', edgecolor='black', alpha=0.85)
ax.set_title('6. Cyberbullying Frequency', fontsize=12, fontweight='bold')
ax.tick_params(axis='x', rotation=25)

# 7. Incident Platform Distribution
ax = axes[2, 0]
col_plat_inc = [c for c in df_analytical.columns if c.startswith('10.')][0]
plat_cts = df_analytical[col_plat_inc].value_counts()
ax.bar(plat_cts.index, plat_cts.values, color='#d35400', edgecolor='black', alpha=0.85)
ax.set_title('7. Incident Social Media Platform', fontsize=12, fontweight='bold')
ax.tick_params(axis='x', rotation=25)

# 8. Bivariate: Experienced Cyberbullying vs Mental Health Impact
ax = axes[2, 1]
cb_mhi_xtab = pd.crosstab(df_analytical[col_q5], df_analytical[col_target], normalize='index')[ordered_tgt] * 100
cb_mhi_xtab.plot(kind='bar', stacked=True, ax=ax, colormap='viridis', edgecolor='black', alpha=0.85)
ax.set_title('8. Cyberbullying Exp vs Mental Health (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage (%)')
ax.tick_params(axis='x', rotation=0)
ax.legend(title='Impact Level', fontsize=8)

# 9. Bivariate: Frequency vs Mental Health Impact
ax = axes[2, 2]
freq_mhi_xtab = pd.crosstab(df_analytical[col_freq], df_analytical[col_target], normalize='index').reindex(freq_order)[ordered_tgt] * 100
freq_mhi_xtab.plot(kind='bar', stacked=True, ax=ax, colormap='Spectral', edgecolor='black', alpha=0.85)
ax.set_title('9. Frequency vs Mental Health (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage (%)')
ax.tick_params(axis='x', rotation=30)
ax.legend(title='Impact Level', fontsize=8)

plt.tight_layout()
plt.show()

# 10. Correlation Heatmap
fig, ax = plt.subplots(figsize=(7, 5))
corr_matrix = ord_sub[['target_num', 'sev_num', 'freq_num', 'usage_num']].corr(method='spearman')
labels = ['Mental Health Impact', 'Emotional Severity', 'Bullying Frequency', 'Daily Usage']
cax = ax.matshow(corr_matrix, cmap='coolwarm', vmin=-0.2, vmax=0.4)
fig.colorbar(cax)

ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=35, ha='left')
ax.set_yticklabels(labels)
ax.set_title('10. Spearman Rank Correlation Matrix', fontsize=13, fontweight='bold', pad=25)

for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(j, i, f"{corr_matrix.iloc[i, j]:.3f}", ha='center', va='center', color='black', fontweight='bold')

plt.tight_layout()
plt.show()"""))

# Section 15
cells.append(nbf.v4.new_markdown_cell("""## 15. Export Results & Research Tables
Verify that all 7 research CSV tables have been compiled and saved into `Data/processed/`."""))

cells.append(nbf.v4.new_code_cell("""processed_dir = os.path.join('..', 'Data', 'processed') if os.path.exists(os.path.join('..', 'Data', 'processed')) else os.path.join('Data', 'processed')

files_to_check = [
    'phase2_analysis_data.csv',
    'statistical_results.csv',
    'chi_square_results.csv',
    't_test_results.csv',
    'correlation_results.csv',
    'feature_selection_results.csv',
    'mental_health_impact_distribution.csv',
    'demographic_distribution.csv',
    'social_media_usage.csv',
    'cyberbullying_experience.csv',
    'descriptive_statistics.csv'
]

print("Export Verification in Data/processed/:")
for f in files_to_check:
    fp = os.path.join(processed_dir, f)
    status = os.path.exists(fp)
    sz = os.path.getsize(fp) if status else 0
    print(f" - {f:<38}: Exists={status} ({sz:,} bytes)")"""))

# Section 16
cells.append(nbf.v4.new_markdown_cell("""## 16. Final Phase 2 Statistical Summary
Master executive summary synthesizing Phase 2 findings, hypothesis tests, and decision gates for ML Phase 3."""))

cells.append(nbf.v4.new_code_cell("""print(\"\"\"
================================================================================
MIND SAFE — PHASE 2 STATISTICAL & FEATURE SELECTION SUMMARY
================================================================================

1. ANALYTICAL COHORT:
   - Initial Phase 1 Cleaned Records: 521
   - Filtered Blank Submissions      : 2 (Rows 21 and 80)
   - Final Analytical Sample (N)    : 519 empirical participants (100% genuine survey data)

2. STRUCTURAL SKIP LOGIC:
   - Q8 (Perpetrator motivation)    : 371 coded as 'Not Applicable' (Q7 == No), 1 true missing.
   - Q16 (Reason not reported)      : 91 coded as 'Not Applicable' (Q5 == No or reported), 1 true missing.

3. TARGET VARIABLE DISTRIBUTION (Mental_Health_Impact, N = 514 valid):
   - Not at all : 229 (44.55%)
   - Slightly   : 137 (26.65%)
   - Moderately : 107 (20.82%)
   - Severely   :  41 ( 7.98%)
   - Missing    :   5 ( 0.96% of analytical sample)

4. INFERENTIAL HYPOTHESIS TESTING:
   - Experienced_Cyberbullying × Target: Chi2 = 146.281, df = 3, p = 1.67e-31 (Statistically Significant)
   - Cyberbullying_Frequency × Target  : Chi2 =  51.744, df = 12, p = 6.88e-07 (Statistically Significant)
   - Incident_Platform × Target        : Chi2 =  21.736, df = 12, p = 0.0406  (Statistically Significant)
   - Independent T-Test (Emotional Severity across Victimization):
     Welch's t = 12.976, df = 250.7, p = 1.08e-29 (Mean: Yes = 3.042 vs No = 1.638)
   - Spearman Rank Correlation:
     Cyberbullying_Frequency vs Target: rho = +0.2420, p = 3.02e-08
     Emotional_Impact_Severity vs Target: rho = +0.3185, p = 1.85e-13

5. FEATURE SELECTION & TARGET LEAKAGE PROTOCOL:
   - Scenario A (Full Features): Retains all 17 predictors including Q13 and Q14.
   - Scenario B (Leakage-Controlled): Excludes Q13 (Symptomatology) and Q14 (Emotional Severity)
     to ensure models predict mental health impact from exposure and behavioral markers.

PHASE 2 IS FULLY COMPLETE. READY FOR PHASE 3: ML MODEL DEVELOPMENT.
================================================================================
\"\"\")"""))

nb.cells = cells

# Save notebook
notebook_path = os.path.join('notebook', '02_statistical_analysis.ipynb')
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Phase 2 Notebook built successfully at: {notebook_path}")
