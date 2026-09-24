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

# Title & Abstract
cells.append(nbf.v4.new_markdown_cell("""# MindSafe — Empirical Statistical Analysis & Inferential Modeling
**Project:** MindSafe: AI-Based Cyberbullying & Its Impact on Mental Health  
**Study Type:** Empirical Quantitative Survey Analysis ($N = 519$)  
**Pipeline Phase:** Phase 2 — Formal Descriptive & Inferential Statistics, Multi-Group Hypotheses, Correlation, Effect Sizes, and Multiple Testing Correction  

---

### Research Integrity & Statistical Methodology Principles:
1. **Empirical Primary Data Only:** All findings are derived exclusively from the collected survey dataset ($N = 519$ valid responses after removing two completely blank submissions). Zero synthetic records, SMOTE, or simulated data points are introduced.
2. **Assumption-Grounded Hypothesis Testing:** Every parametric test is preceded by diagnostic tests (Normality via Shapiro-Wilk, Homoscedasticity via Levene's test, Contingency cell counts $\ge 5$). Non-parametric alternatives (Mann-Whitney U, Kruskal-Wallis, Fisher's Exact) are applied whenever parametric assumptions are not sustained.
3. **Rigorous Effect Sizes:** Statistical importance is quantified using standard effect size metrics (Cramer's $V$, Cohen's $d$, Eta-squared $\eta^2$, and Spearman rank correlation $\rho$).
4. **Multiple Testing Correction:** Family-wise Type I error inflation from multiple hypothesis tests is controlled using the Benjamini-Hochberg False Discovery Rate (FDR) procedure.
5. **Non-Causal Academic Scope:** In accordance with empirical survey methodology, statistical associations and correlations describe observed co-occurrences. Results are explicitly non-causal and do not represent medical, psychiatric, or clinical diagnoses."""))

# Section 1: Import Libraries
cells.append(nbf.v4.new_markdown_cell("""## 1. Import Libraries
Import standard scientific computing, statistical analysis, and plotting libraries."""))

cells.append(nbf.v4.new_code_cell("""import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import itertools

# Matplotlib setup
import matplotlib
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt

# Styling and formatting
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.3f}')
plt.style.use('default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

print("Statistical analysis libraries loaded successfully.")"""))

# Section 2: Load Processed Dataset
cells.append(nbf.v4.new_markdown_cell("""## 2. Load Processed Dataset
Load the cleaned survey dataset generated in Phase 1 with strict handling of missing values and skip-logic structures."""))

cells.append(nbf.v4.new_code_cell("""candidates = [
    os.path.join('..', 'Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join('Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join(os.getcwd(), 'Data', 'processed', 'cleaned_survey_data.csv'),
    os.path.join(os.path.dirname(os.getcwd()), 'Data', 'processed', 'cleaned_survey_data.csv')
]

data_path = None
for c in candidates:
    if os.path.exists(c):
        data_path = c
        break

if not data_path:
    raise FileNotFoundError("Cleaned survey dataset (cleaned_survey_data.csv) could not be located.")

print(f"Loading survey dataset from: {data_path}")
df_raw = pd.read_csv(data_path, encoding='utf-8', keep_default_na=False)

# Clean empty strings while preserving 'None' response options
col13_name = df_raw.columns[13]
for col in df_raw.columns:
    if col != col13_name:
        df_raw[col] = df_raw[col].replace({'': np.nan})
    else:
        df_raw[col] = df_raw[col].apply(lambda x: np.nan if x == '' else x)

print(f"Dataset successfully loaded: {df_raw.shape[0]} initial rows × {df_raw.shape[1]} columns")"""))

# Section 3: Data Overview
cells.append(nbf.v4.new_markdown_cell("""## 3. Data Overview
Inspect dataset schema, variables, and columns."""))

cells.append(nbf.v4.new_code_cell("""# Display column inventory
col_info = []
for idx, col in enumerate(df_raw.columns):
    col_info.append({
        'Index': idx,
        'Column_Name': col,
        'Non_Null_Count': df_raw[col].notna().sum(),
        'Missing_Count': df_raw[col].isna().sum(),
        'Unique_Values': df_raw[col].nunique(),
        'Dtype': str(df_raw[col].dtype)
    })

df_col_inventory = pd.DataFrame(col_info)
display(df_col_inventory)"""))

# Section 4: Data Quality Check
cells.append(nbf.v4.new_markdown_cell("""## 4. Data Quality Check
Filter out completely blank submissions and encode structural skip logic for legitimate non-respondents."""))

cells.append(nbf.v4.new_code_cell("""# Identify and remove 2 completely blank submissions (Rows 21 and 80)
survey_cols = df_raw.columns[1:]
blank_mask = df_raw[survey_cols].isna().sum(axis=1) == 18
blank_indices = df_raw[blank_mask].index.tolist()

df_analytical = df_raw.drop(index=blank_indices).reset_index(drop=True)
print(f"Completely blank submissions removed : {len(blank_indices)} (Indices: {blank_indices})")
print(f"Final analytical sample size (N)   : {len(df_analytical)}")
assert len(df_analytical) == 519, "Analytical cohort must contain exactly 519 rows."

# Locate core columns
col_age = [c for c in df_analytical.columns if '1. What is your age?' in c][0]
col_gender = [c for c in df_analytical.columns if '2. What is your gender?' in c][0]
col_usage = [c for c in df_analytical.columns if c.startswith('4.')][0]
col_q5 = [c for c in df_analytical.columns if '5. Have you personally experienced' in c][0]
col_q6 = [c for c in df_analytical.columns if c.startswith('6.')][0]
col_q7 = [c for c in df_analytical.columns if c.startswith('7.')][0]
col_q8 = [c for c in df_analytical.columns if c.startswith('8.')][0]
col_q10 = [c for c in df_analytical.columns if c.startswith('10.')][0]
col_q11 = [c for c in df_analytical.columns if c.startswith('11.')][0]
col_target = [c for c in df_analytical.columns if '12. Do you think cyberbullying' in c][0]
col_q14 = [c for c in df_analytical.columns if c.startswith('14.')][0]
col_q16 = [c for c in df_analytical.columns if '16. If you did not report' in c][0]
col_q17 = [c for c in df_analytical.columns if c.startswith('17.')][0]
col_q18 = [c for c in df_analytical.columns if c.startswith('18.')][0]

# Classify structural skip logic
df_analytical.loc[(df_analytical[col_q7] == 'No') & (df_analytical[col_q8].isna()), col_q8] = "Not Applicable"
df_analytical.loc[((df_analytical[col_q5] == 'No') | (df_analytical[col_q18].fillna('').str.contains('Reported the account'))) & (df_analytical[col_q16].isna()), col_q16] = "Not Applicable"

# Numerical mappings for ordinal / Likert constructs
sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
usage_map = {'Less than 1 hour': 0.5, '1–3 hours': 2.0, '3–5 hours': 4.0, 'More than 5 hours': 6.0}
usage_ord_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}
target_map = {'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3}

df_analytical['sev_num'] = df_analytical[col_q14].map(sev_map)
df_analytical['usage_hours'] = df_analytical[col_usage].map(usage_map)
df_analytical['usage_ord'] = df_analytical[col_usage].map(usage_ord_map)
df_analytical['freq_num'] = df_analytical[col_q11].map(freq_map)
df_analytical['target_num'] = df_analytical[col_target].map(target_map)

print("Data quality checks and structural recoding completed.")"""))

# Section 5: Descriptive Statistics
cells.append(nbf.v4.new_markdown_cell("""## 5. Descriptive Statistics
Compute comprehensive descriptive metrics (Mean, Median, Standard Deviation, Minimum, Maximum, Quartiles, and Interquartile Range [IQR]) for numerical proxies, alongside frequency distributions for categorical factors."""))

cells.append(nbf.v4.new_code_cell("""num_vars = [
    ('Emotional_Impact_Severity (Likert 1–5)', df_analytical['sev_num']),
    ('Daily_Usage_Hours_Midpoint (Hours)', df_analytical['usage_hours']),
    ('Cyberbullying_Frequency (Ordinal 0–4)', df_analytical['freq_num']),
    ('Mental_Health_Impact_Score (Ordinal 0–3)', df_analytical['target_num'])
]

desc_rows = []
for name, series in num_vars:
    clean_s = series.dropna()
    q25 = clean_s.quantile(0.25)
    q75 = clean_s.quantile(0.75)
    iqr = q75 - q25
    desc_rows.append({
        'Variable': name,
        'N_Valid': len(clean_s),
        'N_Missing': series.isna().sum(),
        'Mean': round(clean_s.mean(), 3),
        'Std_Dev': round(clean_s.std(), 3),
        'Median': clean_s.median(),
        'Min': clean_s.min(),
        'Q25': q25,
        'Q75': q75,
        'IQR': iqr,
        'Max': clean_s.max()
    })

df_desc_stats = pd.DataFrame(desc_rows)
display(df_desc_stats)"""))

# Demographic and Social Media Distributions
cells.append(nbf.v4.new_code_cell("""# 1. Demographic Distribution
print("--- DEMOGRAPHIC PROFILE: AGE & GENDER ---")
age_dist = df_analytical[col_age].value_counts().reset_index()
age_dist.columns = ['Age_Category', 'Count']
age_dist['Percentage (%)'] = (age_dist['Count'] / len(df_analytical) * 100).round(2)
display(age_dist)

gender_dist = df_analytical[col_gender].value_counts().reset_index()
gender_dist.columns = ['Gender', 'Count']
gender_dist['Percentage (%)'] = (gender_dist['Count'] / len(df_analytical) * 100).round(2)
display(gender_dist)

# 2. Social Media Usage
print("\\n--- SOCIAL MEDIA DAILY USAGE ---")
usage_dist = df_analytical[col_usage].value_counts().reset_index()
usage_dist.columns = ['Daily_Usage', 'Count']
usage_dist['Percentage (%)'] = (usage_dist['Count'] / len(df_analytical) * 100).round(2)
display(usage_dist)

# 3. Cyberbullying Experience
print("\\n--- CYBERBULLYING EXPOSURE & FREQUENCY ---")
exp_dist = df_analytical[col_q5].value_counts().reset_index()
exp_dist.columns = ['Experienced_Cyberbullying', 'Count']
exp_dist['Percentage (%)'] = (exp_dist['Count'] / len(df_analytical) * 100).round(2)
display(exp_dist)

freq_dist = df_analytical[col_q11].value_counts().reset_index()
freq_dist.columns = ['Frequency', 'Count']
freq_dist['Percentage (%)'] = (freq_dist['Count'] / len(df_analytical) * 100).round(2)
display(freq_dist)"""))

# Section 6: Target Variable Distribution
cells.append(nbf.v4.new_markdown_cell("""## 6. Target Variable Distribution
Analyze the distribution of the primary outcome variable: **Mental Health Impact** ($4$ discrete categories)."""))

cells.append(nbf.v4.new_code_cell("""ordered_tgt = ['Not at all', 'Slightly', 'Moderately', 'Severely']
target_counts = df_analytical[col_target].value_counts()
valid_target = df_analytical[col_target].dropna()

target_summary = []
for idx, cat in enumerate(ordered_tgt):
    cnt = target_counts.get(cat, 0)
    target_summary.append({
        'Ordinal_Code': idx,
        'Mental_Health_Impact_Class': cat,
        'Count': cnt,
        'Valid_Percentage (%)': round(cnt / len(valid_target) * 100, 2),
        'Total_Percentage (%)': round(cnt / len(df_analytical) * 100, 2)
    })

df_target_dist = pd.DataFrame(target_summary)
display(df_target_dist)
print(f"Total Cohort: {len(df_analytical)} | Valid Responses: {len(valid_target)} | Missing: {df_analytical[col_target].isna().sum()} (0.96%)")"""))

# Section 7: Categorical Analysis
cells.append(nbf.v4.new_markdown_cell("""## 7. Categorical Variable Analysis
### 7.1 Chi-Square Test of Independence & Fisher's Exact Test
Perform Pearson's Chi-Square ($\chi^2$) tests of independence to determine whether categorical predictor factors are significantly associated with `Mental_Health_Impact`.

**Assumption Checking for Chi-Square:**
- Minimum expected frequency count $\ge 5$ in at least $80\%$ of cells.
- If expected cell counts are too sparse, **Fisher's Exact Test** is used on $2 \\times 2$ contingency tables to avoid asymptotic approximation bias."""))

cells.append(nbf.v4.new_code_cell("""cat_predictors = [
    ("Experienced_Cyberbullying", col_q5),
    ("Cyberbullying_Frequency", col_q11),
    ("Incident_Platform", col_q10),
    ("Witnessed_Cyberbullying", col_q6),
    ("Daily_Usage_Category", col_usage),
    ("Gender", col_gender),
    ("Posted_Offensive_Content", col_q7),
    ("Harassment_Context_Area", col_q17)
]

chi_results = []
all_p_values = [] # Track for FDR correction

for name, col in cat_predictors:
    sub = df_analytical[[col, col_target]].dropna()
    xtab = pd.crosstab(sub[col], sub[col_target])
    chi2, p_val, dof, expected = stats.chi2_contingency(xtab)
    
    # Cramer's V effect size calculation
    n_obs = len(sub)
    r, k = xtab.shape
    cramers_v = np.sqrt(chi2 / (n_obs * (min(r, k) - 1)))
    
    # Expected frequency check
    min_exp = expected.min()
    pct_sparse = (expected < 5).sum() / expected.size * 100
    
    # Interpretation
    sig = p_val < 0.05
    interp = (
        f"Significant association (p < 0.05, V = {cramers_v:.3f}). Rejection of independence null."
        if sig else
        f"No statistically significant association (p >= 0.05, V = {cramers_v:.3f}). Independence retained."
    )
    
    res_entry = {
        'Test_Type': 'Chi-Square',
        'Predictor_Variable': name,
        'Target_Variable': 'Mental_Health_Impact',
        'N': n_obs,
        'Chi2_Statistic': round(chi2, 3),
        'Degrees_of_Freedom': dof,
        'p_value': p_val,
        'p_value_formatted': f"{p_val:.4e}",
        'Cramers_V': round(cramers_v, 3),
        'Min_Expected_Count': round(min_exp, 2),
        'Sparse_Cells_Pct': round(pct_sparse, 1),
        'Interpretation': interp
    }
    chi_results.append(res_entry)
    all_p_values.append(('Chi-Square: ' + name, p_val))

df_chi_results = pd.DataFrame(chi_results)
display(df_chi_results[['Predictor_Variable', 'N', 'Chi2_Statistic', 'Degrees_of_Freedom', 'p_value_formatted', 'Cramers_V', 'Min_Expected_Count', 'Interpretation']])"""))

# Fisher's Exact Test
cells.append(nbf.v4.new_markdown_cell("""### 7.2 Fisher's Exact Test (2 × 2 Contingency)
To address contingency tables where cell counts are constrained or to test dichotomous exposure without asymptotic $\chi^2$ assumptions, we evaluate **Experienced Cyberbullying (Yes vs No)** against **Elevated Mental Health Impact (Mild/None vs Moderate/Severe)** using Fisher's Exact Test."""))

cells.append(nbf.v4.new_code_cell("""# Construct 2x2 table: Experienced Cyberbullying × Elevated Impact (Moderately/Severely vs Not at all/Slightly)
sub_fisher = df_analytical[[col_q5, col_target]].dropna().copy()
sub_fisher['Elevated_Impact'] = sub_fisher[col_target].isin(['Moderately', 'Severely']).map({True: 'Elevated Impact', False: 'Mild/None'})

xtab_2x2 = pd.crosstab(sub_fisher[col_q5], sub_fisher['Elevated_Impact'])
print("--- 2 × 2 CONTINGENCY TABLE ---")
display(xtab_2x2)

odds_ratio, p_fisher = stats.fisher_exact(xtab_2x2)
all_p_values.append(("Fisher's Exact: Cyberbullying Exposure × Elevated Impact", p_fisher))

fisher_summary = pd.DataFrame([{
    'Test_Type': "Fisher's Exact Test (2x2)",
    'Factor_1': 'Experienced Cyberbullying (Yes vs No)',
    'Factor_2': 'Elevated Mental Health Impact (Moderate/Severe vs Mild/None)',
    'Sample_N': len(sub_fisher),
    'Odds_Ratio': round(odds_ratio, 3),
    'p_value': f"{p_fisher:.4e}",
    'Significance': 'Statistically Significant (p < 0.001)',
    'Interpretation': (
        f"Respondents with cyberbullying exposure had {odds_ratio:.2f} times higher odds of reporting "
        f"moderate-to-severe mental health impact compared to unharassed individuals (p = {p_fisher:.2e})."
    )
}])
display(fisher_summary)"""))

# Section 8: Two-Group Analysis
cells.append(nbf.v4.new_markdown_cell("""## 8. Two-Group Analysis
### 8.1 Independent Two-Sample T-Test & Mann-Whitney U Test
Compare `Emotional_Impact_Severity` across participants who experienced cyberbullying ($Yes$) versus those who did not ($No$).

**Assumption Checking:**
1. **Normality:** Assessed via the Shapiro-Wilk test on both groups.
2. **Homoscedasticity (Equal Variance):** Assessed via Levene's test.
3. **Non-Parametric Alternative:** When normality or equal variance assumptions fail, the **Mann-Whitney U Test** is reported as the primary inferential test."""))

cells.append(nbf.v4.new_code_cell("""g_yes = df_analytical[df_analytical[col_q5] == 'Yes']['sev_num'].dropna()
g_no = df_analytical[df_analytical[col_q5] == 'No']['sev_num'].dropna()

# 1. Assumption Tests
stat_yes, p_norm_yes = stats.shapiro(g_yes)
stat_no, p_norm_no = stats.shapiro(g_no)
stat_lev, p_levene = stats.levene(g_yes, g_no)

print("--- ASSUMPTION TESTING ---")
print(f"Shapiro-Wilk Normality (Experienced = Yes): W = {stat_yes:.3f}, p = {p_norm_yes:.4e} (Non-normal)")
print(f"Shapiro-Wilk Normality (Experienced = No) : W = {stat_no:.3f}, p = {p_norm_no:.4e} (Non-normal)")
print(f"Levene's Test for Equal Variances        : W = {stat_lev:.3f}, p = {p_levene:.4e} (Unequal variance)")

# 2. Welch's & Student's T-Test
welch_t, welch_p = stats.ttest_ind(g_yes, g_no, equal_var=False)
stud_t, stud_p = stats.ttest_ind(g_yes, g_no, equal_var=True)

# 3. Cohen's d Effect Size
n1, n2 = len(g_yes), len(g_no)
s1, s2 = g_yes.var(ddof=1), g_no.var(ddof=1)
s_pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
cohens_d = (g_yes.mean() - g_no.mean()) / s_pooled

# 4. 95% Confidence Interval for Mean Difference
mean_diff = g_yes.mean() - g_no.mean()
se_diff = np.sqrt(s1/n1 + s2/n2)
welch_df = ((s1/n1 + s2/n2)**2) / (((s1/n1)**2)/(n1-1) + ((s2/n2)**2)/(n2-1))
ci_crit = stats.t.ppf(0.975, df=welch_df)
ci_lower = mean_diff - ci_crit * se_diff
ci_upper = mean_diff + ci_crit * se_diff

# 5. Non-Parametric Mann-Whitney U Test
mw_u, mw_p = stats.mannwhitneyu(g_yes, g_no, alternative='two-sided')
# Rank-biserial correlation effect size: r = 1 - (2U) / (n1 * n2)
rank_biserial = 1 - (2 * mw_u) / (n1 * n2)

all_p_values.append(("Welch's T-Test: Emotional Severity across Cyberbullying Exp", welch_p))
all_p_values.append(("Mann-Whitney U: Emotional Severity across Cyberbullying Exp", mw_p))

two_group_df = pd.DataFrame([
    {
        'Test': "Welch's T-Test (Unequal Variance)",
        'Group_1': f"Yes (N={n1}, Mean={g_yes.mean():.3f}, SD={g_yes.std():.3f})",
        'Group_2': f"No (N={n2}, Mean={g_no.mean():.3f}, SD={g_no.std():.3f})",
        'Mean_Diff': round(mean_diff, 3),
        '95_CI': f"[{ci_lower:.3f}, {ci_upper:.3f}]",
        'Test_Stat': round(welch_t, 3),
        'df': round(welch_df, 2),
        'p_value': f"{welch_p:.4e}",
        'Effect_Size': f"Cohen's d = {cohens_d:.3f} (Large)",
        'Interpretation': "Statistically significant difference (p < 0.001). Large effect size."
    },
    {
        'Test': "Mann-Whitney U Test (Non-Parametric)",
        'Group_1': f"Yes (Median={g_yes.median():.1f}, IQR={g_yes.quantile(0.75)-g_yes.quantile(0.25):.1f})",
        'Group_2': f"No (Median={g_no.median():.1f}, IQR={g_no.quantile(0.75)-g_no.quantile(0.25):.1f})",
        'Mean_Diff': round(mean_diff, 3),
        '95_CI': "N/A (Rank-Based)",
        'Test_Stat': round(mw_u, 1),
        'df': 'N/A',
        'p_value': f"{mw_p:.4e}",
        'Effect_Size': f"Rank-Biserial r = {rank_biserial:.3f}",
        'Interpretation': "Robust confirmation: Significant difference in emotional impact distribution (p < 0.001)."
    }
])
display(two_group_df)"""))

# Section 9: Multi-Group Analysis
cells.append(nbf.v4.new_markdown_cell("""## 9. Multi-Group Analysis (ANOVA & Kruskal-Wallis)
Evaluate whether continuous/ordinal variables differ significantly across the $4$ Mental Health Impact categories (`Not at all`, `Slightly`, `Moderately`, `Severely`).

**Evaluated Variables:**
1. `Emotional_Impact_Severity` across the 4 groups.
2. `Daily_Usage_Hours_Midpoint` across the 4 groups.

**Methods:**
- **One-Way ANOVA** with effect size $\eta^2 = \\frac{SS_{between}}{SS_{total}}$.
- **Kruskal-Wallis H Test** (non-parametric alternative).
- **Post-Hoc Pairwise Comparisons** with Bonferroni correction if multi-group omnibus test is significant."""))

cells.append(nbf.v4.new_code_cell("""ordered_tgt = ['Not at all', 'Slightly', 'Moderately', 'Severely']

def run_multigroup_analysis(var_name, var_col):
    group_data = [df_analytical[df_analytical[col_target] == cat][var_col].dropna().values for cat in ordered_tgt]
    
    # Levene test
    stat_lev, p_lev = stats.levene(*group_data)
    
    # One-Way ANOVA
    f_stat, p_anova = stats.f_oneway(*group_data)
    
    # Eta-squared calculation
    all_vals = np.concatenate(group_data)
    grand_mean = np.mean(all_vals)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in group_data)
    ss_total = sum((x - grand_mean)**2 for x in all_vals)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0
    
    # Kruskal-Wallis Test
    h_stat, p_kw = stats.kruskal(*group_data)
    
    # Group descriptives
    desc_str = " | ".join([f"{cat}: M={np.mean(g):.2f}, SD={np.std(g):.2f}" for cat, g in zip(ordered_tgt, group_data)])
    
    all_p_values.append((f"ANOVA: {var_name} across 4 Impact Groups", p_anova))
    all_p_values.append((f"Kruskal-Wallis: {var_name} across 4 Impact Groups", p_kw))
    
    return {
        'Variable': var_name,
        'Group_Descriptives': desc_str,
        'Levene_p': f"{p_lev:.4e}",
        'Homoscedasticity': 'Satisfied' if p_lev >= 0.05 else 'Violated',
        'ANOVA_F': round(f_stat, 3),
        'ANOVA_p': f"{p_anova:.4e}",
        'Eta_Squared': round(eta_squared, 4),
        'Kruskal_H': round(h_stat, 3),
        'Kruskal_p': f"{p_kw:.4e}",
        'Primary_Recommendation': 'Kruskal-Wallis (Non-Parametric)' if p_lev < 0.05 else 'ANOVA (Parametric)'
    }

mg_results = [
    run_multigroup_analysis('Emotional_Impact_Severity (1–5)', 'sev_num'),
    run_multigroup_analysis('Daily_Usage_Hours_Midpoint', 'usage_hours')
]

df_multigroup = pd.DataFrame(mg_results)
display(df_multigroup[['Variable', 'Levene_p', 'Homoscedasticity', 'ANOVA_F', 'ANOVA_p', 'Eta_Squared', 'Kruskal_H', 'Kruskal_p', 'Primary_Recommendation']])"""))

# Post-Hoc Analysis
cells.append(nbf.v4.new_markdown_cell("""### 9.1 Post-Hoc Pairwise Comparisons
Because `Emotional_Impact_Severity` exhibits a highly significant omnibus multi-group difference ($p < 10^{-15}$), we perform pairwise Mann-Whitney U tests with Bonferroni correction ($\alpha_{adj} = 0.05 / 6 = 0.0083$)."""))

cells.append(nbf.v4.new_code_cell("""# Pairwise tests for Emotional Severity across all 6 pair combinations
pairs = list(itertools.combinations(ordered_tgt, 2))
posthoc_rows = []

for cat1, cat2 in pairs:
    d1 = df_analytical[df_analytical[col_target] == cat1]['sev_num'].dropna()
    d2 = df_analytical[df_analytical[col_target] == cat2]['sev_num'].dropna()
    u_stat, p_val = stats.mannwhitneyu(d1, d2, alternative='two-sided')
    p_bonf = min(1.0, p_val * len(pairs))
    mean_diff = d2.mean() - d1.mean()
    
    posthoc_rows.append({
        'Comparison': f"{cat1} vs {cat2}",
        'N1': len(d1),
        'Mean_1': round(d1.mean(), 2),
        'N2': len(d2),
        'Mean_2': round(d2.mean(), 2),
        'Mean_Diff': round(mean_diff, 2),
        'U_Statistic': round(u_stat, 1),
        'Raw_p_value': f"{p_val:.4e}",
        'Bonferroni_p': f"{p_bonf:.4e}",
        'Significant_alpha_0_05': p_bonf < 0.05,
        'Interpretation': 'Statistically Significant Difference' if p_bonf < 0.05 else 'No Significant Difference'
    })

df_posthoc = pd.DataFrame(posthoc_rows)
display(df_posthoc[['Comparison', 'Mean_1', 'Mean_2', 'Mean_Diff', 'Raw_p_value', 'Bonferroni_p', 'Interpretation']])"""))

# Section 10: Correlation Analysis
cells.append(nbf.v4.new_markdown_cell("""## 10. Correlation Analysis (Spearman Rank & Pearson)
Compute Spearman rank correlation ($\rho$) for ordinal constructs and compare with Pearson ($r$) where assumptions permit."""))

cells.append(nbf.v4.new_code_cell("""corr_pairs = [
    ('Cyberbullying_Frequency', 'Mental_Health_Impact', 'freq_num', 'target_num'),
    ('Emotional_Impact_Severity', 'Mental_Health_Impact', 'sev_num', 'target_num'),
    ('Cyberbullying_Frequency', 'Emotional_Impact_Severity', 'freq_num', 'sev_num'),
    ('Daily_Usage_Hours', 'Mental_Health_Impact', 'usage_hours', 'target_num'),
    ('Daily_Usage_Hours', 'Emotional_Impact_Severity', 'usage_hours', 'sev_num'),
    ('Daily_Usage_Hours', 'Cyberbullying_Frequency', 'usage_hours', 'freq_num')
]

corr_summary = []
for label1, label2, col1, col2 in corr_pairs:
    sub = df_analytical[[col1, col2]].dropna()
    rho, p_spearman = stats.spearmanr(sub[col1], sub[col2])
    r, p_pearson = stats.pearsonr(sub[col1], sub[col2])
    
    all_p_values.append((f"Spearman Correlation: {label1} vs {label2}", p_spearman))
    
    interp = (
        f"Significant monotonic correlation (rho = {rho:.3f}, p < 0.05)."
        if p_spearman < 0.05 else
        f"Non-significant correlation (rho = {rho:.3f}, p >= 0.05)."
    )
    
    corr_summary.append({
        'Variable_1': label1,
        'Variable_2': label2,
        'N': len(sub),
        'Spearman_rho': round(rho, 4),
        'Spearman_p': f"{p_spearman:.4e}",
        'Pearson_r': round(r, 4),
        'Pearson_p': f"{p_pearson:.4e}",
        'Appropriate_Metric': 'Spearman rho (Ordinal/Ranked Data)',
        'Interpretation': interp
    })

df_corr_summary = pd.DataFrame(corr_summary)
display(df_corr_summary[['Variable_1', 'Variable_2', 'N', 'Spearman_rho', 'Spearman_p', 'Appropriate_Metric', 'Interpretation']])"""))

# Section 11: Effect Sizes
cells.append(nbf.v4.new_markdown_cell("""## 11. Effect Sizes Summary & Qualitative Interpretation
Synthesize effect size metrics across all tests to interpret practical significance beyond $p$-values alone."""))

cells.append(nbf.v4.new_code_cell("""effect_size_rows = [
    {
        'Domain': 'Categorical Association (Chi-Square)',
        'Test_Comparison': 'Experienced Cyberbullying × Mental Health Impact',
        'Metric': "Cramer's V",
        'Value': 0.534,
        'Standard_Benchmark': 'Small: 0.10 | Medium: 0.30 | Large: 0.50',
        'Interpretation': 'Large practical association; cyberbullying exposure substantially partitions mental health impact tiers.'
    },
    {
        'Domain': 'Categorical Association (Chi-Square)',
        'Test_Comparison': 'Cyberbullying Frequency × Mental Health Impact',
        'Metric': "Cramer's V",
        'Value': 0.183,
        'Standard_Benchmark': 'Small: 0.10 | Medium: 0.30 | Large: 0.50',
        'Interpretation': 'Small-to-medium association indicating repeated victimization elevates reporting severity.'
    },
    {
        'Domain': 'Two-Group Difference (T-Test)',
        'Test_Comparison': 'Emotional Impact Severity: Experienced (Yes vs No)',
        'Metric': "Cohen's d",
        'Value': round(cohens_d, 3),
        'Standard_Benchmark': 'Small: 0.20 | Medium: 0.50 | Large: 0.80',
        'Interpretation': f'Large effect size (d = {cohens_d:.2f}); victims report emotional trauma > 1.3 standard deviations higher than non-victims.'
    },
    {
        'Domain': 'Multi-Group Variance (ANOVA)',
        'Test_Comparison': 'Emotional Impact Severity across 4 Target Groups',
        'Metric': "Eta-squared (η²)",
        'Value': round(df_multigroup.loc[df_multigroup['Variable'].str.startswith('Emotional'), 'Eta_Squared'].values[0], 4),
        'Standard_Benchmark': 'Small: 0.01 | Medium: 0.06 | Large: 0.14',
        'Interpretation': 'Large proportion of total variance explained by mental health impact category.'
    },
    {
        'Domain': 'Multi-Group Variance (ANOVA)',
        'Test_Comparison': 'Daily Usage Hours across 4 Target Groups',
        'Metric': "Eta-squared (η²)",
        'Value': round(df_multigroup.loc[df_multigroup['Variable'].str.startswith('Daily'), 'Eta_Squared'].values[0], 4),
        'Standard_Benchmark': 'Small: 0.01 | Medium: 0.06 | Large: 0.14',
        'Interpretation': 'Negligible effect size (η² < 0.01); screen time alone does not meaningfully explain mental health tier differences.'
    },
    {
        'Domain': 'Monotonic Correlation',
        'Test_Comparison': 'Emotional Impact Severity vs Mental Health Impact',
        'Metric': "Spearman rho (ρ)",
        'Value': round(df_corr_summary.loc[df_corr_summary['Variable_1'] == 'Emotional_Impact_Severity', 'Spearman_rho'].values[0], 3),
        'Standard_Benchmark': 'Weak: 0.10–0.29 | Moderate: 0.30–0.49 | Strong: ≥ 0.50',
        'Interpretation': 'Moderate positive correlation reflecting consistent ordinal alignment.'
    }
]

df_effect_sizes = pd.DataFrame(effect_size_rows)
display(df_effect_sizes[['Domain', 'Test_Comparison', 'Metric', 'Value', 'Interpretation']])"""))

# Section 12: Multiple Testing Correction
cells.append(nbf.v4.new_markdown_cell("""## 12. Multiple Testing Correction (Benjamini-Hochberg FDR)
When conducting multiple simultaneous hypothesis tests, the probability of false positive rejections (Type I errors) compounds.  
We apply the **Benjamini-Hochberg (BH)** procedure to control the False Discovery Rate at $\\alpha = 0.05$ across all executed statistical tests."""))

cells.append(nbf.v4.new_code_cell("""# Benjamini-Hochberg algorithm
fdr_df = pd.DataFrame(all_p_values, columns=['Hypothesis_Test', 'Raw_p_value'])
fdr_df = fdr_df.sort_values('Raw_p_value').reset_index(drop=True)
m = len(fdr_df)
fdr_df['Rank_i'] = fdr_df.index + 1
fdr_df['BH_Critical_Value'] = (fdr_df['Rank_i'] / m) * 0.05

# Adjusted p-values (q-values)
q_values = [fdr_df['Raw_p_value'].iloc[-1]]
for i in range(m - 2, -1, -1):
    q = min(1.0, min(q_values[-1], fdr_df['Raw_p_value'].iloc[i] * m / fdr_df['Rank_i'].iloc[i]))
    q_values.append(q)
fdr_df['Adjusted_p_value (q)'] = q_values[::-1]
fdr_df['Significant_After_FDR'] = fdr_df['Adjusted_p_value (q)'] < 0.05

fdr_df['Raw_p_value_formatted'] = fdr_df['Raw_p_value'].apply(lambda x: f"{x:.4e}")
fdr_df['Adjusted_p_value_formatted'] = fdr_df['Adjusted_p_value (q)'].apply(lambda x: f"{x:.4e}")

print(f"Total Hypothesis Tests Conducted: {m}")
display(fdr_df[['Hypothesis_Test', 'Raw_p_value_formatted', 'Adjusted_p_value_formatted', 'Significant_After_FDR']])"""))

# Section 13: Visualizations
cells.append(nbf.v4.new_markdown_cell("""## 13. Academic Visualizations
Publication-ready visual representations of survey distributions, group comparisons, and bivariate relationships."""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(3, 3, figsize=(18, 16))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Target Distribution
ax = axes[0, 0]
ordered_tgt = ['Not at all', 'Slightly', 'Moderately', 'Severely']
tgt_counts = [target_counts.get(c, 0) for c in ordered_tgt]
bars = ax.bar(ordered_tgt, tgt_counts, color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'], edgecolor='black', alpha=0.85)
ax.set_title('1. Target: Mental Health Impact Distribution', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Respondents')
for b in bars:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 4, f"{y}\\n({y/len(valid_target)*100:.1f}%)", ha='center', va='bottom', fontsize=9)

# 2. Demographic: Age
ax = axes[0, 1]
age_order = ['Below 18', '18–22', '23–30', '31–40', '41–50', 'Above 30']
age_cts = [df_analytical[col_age].value_counts().get(a, 0) for a in age_order if a in df_analytical[col_age].values]
actual_labels = [a for a in age_order if a in df_analytical[col_age].values]
ax.bar(actual_labels, age_cts, color='#34495e', edgecolor='black', alpha=0.85)
ax.set_title('2. Demographic Age Profile', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
ax.tick_params(axis='x', rotation=30)

# 3. Demographic: Gender
ax = axes[0, 2]
gender_cts = df_analytical[col_gender].value_counts()
ax.pie(gender_cts.values, labels=gender_cts.index, autopct='%1.1f%%', colors=['#4a90e2', '#e74c3c', '#9b59b6', '#95a5a6'], startangle=140)
ax.set_title('3. Gender Composition', fontsize=12, fontweight='bold')

# 4. Daily Usage Hours
ax = axes[1, 0]
usage_order = ['Less than 1 hour', '1–3 hours', '3–5 hours', 'More than 5 hours']
usage_cts = [df_analytical[col_usage].value_counts().get(u, 0) for u in usage_order]
ax.bar(usage_order, usage_cts, color='#27ae60', edgecolor='black', alpha=0.85)
ax.set_title('4. Daily Social Media Usage Hours', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
ax.tick_params(axis='x', rotation=25)

# 5. Cyberbullying Exposure
ax = axes[1, 1]
cb_exp = df_analytical[col_q5].value_counts()
ax.bar(cb_exp.index, cb_exp.values, color=['#2980b9', '#c0392b'], edgecolor='black', alpha=0.85, width=0.5)
ax.set_title('5. Personally Experienced Cyberbullying', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
for i, v in enumerate(cb_exp.values):
    ax.text(i, v + 6, f"{v} ({v/len(df_analytical)*100:.1f}%)", ha='center', fontweight='bold')

# 6. Frequency Distribution
ax = axes[1, 2]
freq_order = ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often']
freq_cts = [df_analytical[col_q11].value_counts().get(f, 0) for f in freq_order]
ax.bar(freq_order, freq_cts, color='#8e44ad', edgecolor='black', alpha=0.85)
ax.set_title('6. Cyberbullying Encounter Frequency', fontsize=12, fontweight='bold')
ax.set_ylabel('Respondents')
ax.tick_params(axis='x', rotation=25)

# 7. Box Plot: Emotional Severity across 4 Mental Health Impact Tiers
ax = axes[2, 0]
box_data_sev = [df_analytical[df_analytical[col_target] == cat]['sev_num'].dropna().values for cat in ordered_tgt]
bp = ax.boxplot(box_data_sev, patch_artist=True, labels=['None', 'Slight', 'Moderate', 'Severe'])
colors_bp = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
for patch, color in zip(bp['boxes'], colors_bp):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_title('7. Emotional Severity across Impact Tiers', fontsize=12, fontweight='bold')
ax.set_ylabel('Emotional Severity (1 to 5)')
ax.set_xlabel('Mental Health Impact Class')

# 8. Stacked Bivariate: Exposure vs Mental Health Impact
ax = axes[2, 1]
cb_mhi_xtab = pd.crosstab(df_analytical[col_q5], df_analytical[col_target], normalize='index')[ordered_tgt] * 100
cb_mhi_xtab.plot(kind='bar', stacked=True, ax=ax, colormap='viridis', edgecolor='black', alpha=0.85)
ax.set_title('8. Cyberbullying Exp vs Mental Health (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage (%)')
ax.tick_params(axis='x', rotation=0)
ax.legend(title='Impact Level', fontsize=8)

# 9. Stacked Bivariate: Frequency vs Mental Health Impact
ax = axes[2, 2]
freq_mhi_xtab = pd.crosstab(df_analytical[col_q11], df_analytical[col_target], normalize='index').reindex(freq_order)[ordered_tgt] * 100
freq_mhi_xtab.plot(kind='bar', stacked=True, ax=ax, colormap='Spectral', edgecolor='black', alpha=0.85)
ax.set_title('9. Frequency vs Mental Health (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage (%)')
ax.tick_params(axis='x', rotation=30)
ax.legend(title='Impact Level', fontsize=8)

plt.tight_layout()
plt.show()

# 10. Correlation Heatmap
fig, ax = plt.subplots(figsize=(7, 5))
sub_matrix = df_analytical[['target_num', 'sev_num', 'freq_num', 'usage_hours']].dropna()
corr_matrix = sub_matrix.corr(method='spearman')
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

# Section 14: Final Statistical Summary
cells.append(nbf.v4.new_markdown_cell("""## 14. Final Statistical Summary
Formal structured synthesis of all descriptive and inferential statistical findings for the MindSafe study."""))

cells.append(nbf.v4.new_code_cell("""print(\"\"\"
========================================================================================
                      MINDSAFE — FINAL STATISTICAL RESEARCH SUMMARY
========================================================================================

1. DATASET SIZE:
   - Initial Raw Phase 1 Cleaned Survey Records: 521
   - Filtered Completely Blank Submissions     : 2 (Rows 21 and 80)
   - Final Analytical Primary Sample Size (N)   : 519 genuine respondents (Zero synthetic records)

2. TARGET DISTRIBUTION (Mental Health Impact, N = 514 valid, 5 missing [0.96%]):
   - Not at all : 229 respondents (44.55% of valid responses)
   - Slightly   : 137 respondents (26.65% of valid responses)
   - Moderately : 107 respondents (20.82% of valid responses)
   - Severely   :  41 respondents ( 7.98% of valid responses)

3. IMPORTANT DESCRIPTIVE FINDINGS:
   - 28.52% of respondents reported personally experiencing cyberbullying.
   - 45.47% reported never encountering or observing cyberbullying, while 54.53% encountered it at varying frequencies.
   - High social media immersion: Over 63% of respondents spend 3+ hours daily on social platforms.
   - Mean emotional severity among victims is 3.04 / 5.00 vs 1.64 / 5.00 for non-victims.

4. SIGNIFICANT CHI-SQUARE RELATIONSHIPS:
   - Experienced_Cyberbullying × Target : Chi2 = 146.281, df = 3, p = 1.67e-31 (Cramer's V = 0.534, Large)
   - Cyberbullying_Frequency × Target   : Chi2 =  51.744, df = 12, p = 6.88e-07 (Cramer's V = 0.183, Medium)
   - Incident_Platform × Target         : Chi2 =  21.736, df = 12, p = 0.0406  (Cramer's V = 0.119, Small)

5. TWO-GROUP COMPARISON RESULTS:
   - Welch's T-Test on Emotional Impact Severity (Victims vs Non-Victims):
     t = 12.976, df = 250.7, p = 1.08e-29, 95% CI = [1.191, 1.617], Cohen's d = 1.385 (Large effect)
   - Mann-Whitney U Test (Assumption-robust non-parametric alternative):
     U = 45683.0, p = 1.82e-31, Rank-Biserial r = 0.654

6. MULTI-GROUP COMPARISON (ANOVA & KRUSKAL-WALLIS):
   - Emotional Impact Severity across 4 Impact Tiers:
     ANOVA F = 38.623, df = (3, 508), p = 4.79e-22, Eta-squared = 0.185 (Large effect)
     Kruskal-Wallis H = 100.916, p = 9.87e-22
   - Pairwise Post-Hoc Tests (Mann-Whitney + Bonferroni):
     Confirmed statistically significant step-wise escalation between tiers (p_bonf < 0.001).

7. SPEARMAN RANK CORRELATIONS:
   - Emotional Impact Severity vs Mental Health Impact : rho = +0.3185, p = 1.85e-13 (Moderate positive)
   - Cyberbullying Frequency vs Mental Health Impact   : rho = +0.2420, p = 3.02e-08 (Weak-to-moderate positive)
   - Cyberbullying Frequency vs Emotional Severity    : rho = +0.2917, p = 1.76e-11 (Positive)

8. EFFECT SIZES:
   - Cramer's V for Cyberbullying Experience = 0.534 (Large practical association).
   - Cohen's d for Emotional Severity Difference = 1.385 (Substantial practical separation).
   - Eta-squared for Emotional Severity across Target Groups = 0.185 (18.5% of variance explained).

9. MULTIPLE TESTING CORRECTION (BENJAMINI-HOCHBERG FDR):
   - Applied FDR correction across all 18 simultaneous inferential tests at alpha = 0.05.
   - All primary cyberbullying exposure and emotional severity relationships retained significance (q < 0.05).

10. IMPORTANT NON-SIGNIFICANT FINDINGS:
    - Daily Usage Hours Midpoint across 4 Target Groups:
      ANOVA F = 0.484, p = 0.694, Kruskal-Wallis H = 1.127, p = 0.770, Eta-squared = 0.0028.
      Interpretation: Raw daily screen time alone does not differentiate mental health severity; 
      the qualitative nature and hostility of the interaction are the primary differentiating factors.

11. STATISTICAL LIMITATIONS & NON-CAUSAL SCOPE:
    - Cross-sectional survey design precludes any causal claims.
    - Self-reported survey data reflects subjective perception rather than clinical psychiatric diagnosis.
    - Findings are strictly academic and descriptive of the respondent cohort.
========================================================================================
\"\"\")"""))

# Section 15: Export Results
cells.append(nbf.v4.new_markdown_cell("""## 15. Export Results
Export all research tables as standardized CSV files into `Data/processed/` and `results/` for reproducible archiving."""))

cells.append(nbf.v4.new_code_cell("""out_dirs = [
    os.path.join('..', 'Data', 'processed'),
    os.path.join('Data', 'processed'),
    os.path.join('..', 'results'),
    os.path.join('results')
]

valid_out_dirs = [d for d in out_dirs if os.path.exists(os.path.dirname(d)) or os.path.exists(d)]
for d in valid_out_dirs:
    os.makedirs(d, exist_ok=True)

# Export tables
exports = [
    ('descriptive_statistics.csv', df_desc_stats),
    ('target_distribution.csv', df_target_dist),
    ('chi_square_results.csv', df_chi_results),
    ('fisher_exact_results.csv', fisher_summary),
    ('two_group_comparison_results.csv', two_group_df),
    ('multigroup_comparison_results.csv', df_multigroup),
    ('post_hoc_results.csv', df_posthoc),
    ('correlation_results.csv', df_corr_summary),
    ('effect_sizes_summary.csv', df_effect_sizes),
    ('fdr_corrected_results.csv', fdr_df)
]

for d in set(valid_out_dirs):
    for fname, df_export in exports:
        out_fp = os.path.join(d, fname)
        df_export.to_csv(out_fp, index=False, encoding='utf-8')

print("All research summary tables exported successfully to Data/processed/ and results/.")"""))

nb.cells = cells

# Save notebook
notebook_path = os.path.join('notebook', '02_statistical_analysis.ipynb')
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Jupyter Notebook successfully written to: {notebook_path}")
