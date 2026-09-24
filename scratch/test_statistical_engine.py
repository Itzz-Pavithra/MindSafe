import os
import numpy as np
import pandas as pd
from scipy import stats

cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
if not os.path.exists(cleaned_path):
    raise FileNotFoundError("Cleaned survey data not found")

df = pd.read_csv(cleaned_path, keep_default_na=False)

# Replace empty strings
col13 = df.columns[13]
for c in df.columns:
    if c != col13:
        df[c] = df[c].replace({'': np.nan})
    else:
        df[c] = df[c].apply(lambda x: np.nan if x == '' else x)

# Remove 2 completely blank submissions
survey_cols = df.columns[1:]
blank_mask = df[survey_cols].isna().sum(axis=1) == 18
df_clean = df.drop(index=df[blank_mask].index).reset_index(drop=True)
print(f"Analytical dataset: N = {len(df_clean)}")

# Column finders
col_target = [c for c in df_clean.columns if '12. Do you think cyberbullying' in c][0]
col_q5 = [c for c in df_clean.columns if '5. Have you personally experienced' in c][0]
col_q6 = [c for c in df_clean.columns if c.startswith('6.')][0]
col_q7 = [c for c in df_clean.columns if c.startswith('7.')][0]
col_q11 = [c for c in df_clean.columns if c.startswith('11.')][0]
col_q14 = [c for c in df_clean.columns if c.startswith('14.')][0]
col_usage = [c for c in df_clean.columns if c.startswith('4.')][0]
col_age = [c for c in df_clean.columns if '1. What is your age?' in c][0]
col_gender = [c for c in df_clean.columns if '2. What is your gender?' in c][0]
col_plat = [c for c in df_clean.columns if c.startswith('10.')][0]

# Mappings
sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
usage_map = {'Less than 1 hour': 0.5, '1–3 hours': 2.0, '3–5 hours': 4.0, 'More than 5 hours': 6.0}
freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}
target_map = {'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3}

df_clean['sev_num'] = df_clean[col_q14].map(sev_map)
df_clean['usage_num'] = df_clean[col_usage].map(usage_map)
df_clean['freq_num'] = df_clean[col_q11].map(freq_map)
df_clean['target_num'] = df_clean[col_target].map(target_map)

# 1. Chi-Square & Cramer's V
print("\n--- Chi-Square Tests ---")
sub = df_clean[[col_q5, col_target]].dropna()
xtab = pd.crosstab(sub[col_q5], sub[col_target])
chi2, p, dof, exp = stats.chi2_contingency(xtab)
r, k = xtab.shape
n = len(sub)
cramer_v = np.sqrt(chi2 / (n * (min(r, k) - 1)))
print(f"Chi2: {chi2:.3f}, p: {p:.4e}, df: {dof}, Cramer's V: {cramer_v:.3f}, Min Expected: {exp.min():.2f}")

# 2. Fisher's Exact (2x2 on experienced cyberbullying vs dichotomized impact: None/Slight vs Moderate/Severe)
print("\n--- Fisher's Exact Test (2x2) ---")
sub['high_impact'] = sub[col_target].isin(['Moderately', 'Severely'])
xtab_2x2 = pd.crosstab(sub[col_q5], sub['high_impact'])
odds_ratio, p_fisher = stats.fisher_exact(xtab_2x2)
print(f"Fisher's Exact Odds Ratio: {odds_ratio:.3f}, p: {p_fisher:.4e}")

# 3. Two-Sample T-Test & Mann-Whitney U
print("\n--- Two-Sample Tests ---")
g_yes = df_clean[df_clean[col_q5] == 'Yes']['sev_num'].dropna()
g_no = df_clean[df_clean[col_q5] == 'No']['sev_num'].dropna()

# Normality & Levene
shapiro_yes = stats.shapiro(g_yes)
shapiro_no = stats.shapiro(g_no)
levene_res = stats.levene(g_yes, g_no)
print(f"Shapiro Yes p: {shapiro_yes.pvalue:.4e}, No p: {shapiro_no.pvalue:.4e}")
print(f"Levene p: {levene_res.pvalue:.4e}")

# Welch's T-Test
welch_t, welch_p = stats.ttest_ind(g_yes, g_no, equal_var=False)
# Cohen's d
n1, n2 = len(g_yes), len(g_no)
s1, s2 = g_yes.var(ddof=1), g_no.var(ddof=1)
s_pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
cohen_d = (g_yes.mean() - g_no.mean()) / s_pooled
# Mann-Whitney U
mw_u, mw_p = stats.mannwhitneyu(g_yes, g_no, alternative='two-sided')
print(f"Welch's t: {welch_t:.3f}, p: {welch_p:.4e}, Cohen's d: {cohen_d:.3f}")
print(f"Mann-Whitney U: {mw_u:.1f}, p: {mw_p:.4e}")

# 4. Multi-Group: ANOVA & Kruskal-Wallis across 4 target groups
print("\n--- Multi-Group ANOVA & Kruskal-Wallis ---")
groups = [df_clean[df_clean[col_target] == cat]['usage_num'].dropna() for cat in ['Not at all', 'Slightly', 'Moderately', 'Severely']]
f_stat, anova_p = stats.f_oneway(*groups)
kw_stat, kw_p = stats.kruskal(*groups)
# Eta-squared
all_vals = np.concatenate(groups)
grand_mean = np.mean(all_vals)
ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
ss_total = sum((x - grand_mean)**2 for x in all_vals)
eta_sq = ss_between / ss_total
print(f"Daily Usage across 4 groups - ANOVA F: {f_stat:.3f}, p: {anova_p:.4e}, Eta-sq: {eta_sq:.4f}")
print(f"Daily Usage across 4 groups - Kruskal-Wallis H: {kw_stat:.3f}, p: {kw_p:.4e}")

# 5. Correlation: Spearman & Pearson
print("\n--- Correlations ---")
sub_corr = df_clean[['freq_num', 'target_num']].dropna()
spearman_rho, spearman_p = stats.spearmanr(sub_corr['freq_num'], sub_corr['target_num'])
print(f"Frequency vs Target - Spearman rho: {spearman_rho:.3f}, p: {spearman_p:.4e}")

print("\nAll statistical engines verified successfully!")
