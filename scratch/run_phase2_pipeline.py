import os
import io
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt
import seaborn as sns

print("==================================================")
print("PHASE 2: STATISTICAL ANALYSIS AND ANALYTICS")
print("==================================================")

# 1. Load cleaned data
cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
df = pd.read_csv(cleaned_path, encoding='utf-8')
print(f"Loaded cleaned dataset: {df.shape}")

# Column aliases
col_age = df.columns[1]
col_gender = df.columns[2]
col_plat = df.columns[3]
col_usage = df.columns[4]
col_q5 = df.columns[5]
col_q6 = df.columns[6]
col_q7 = df.columns[7]
col_q8 = df.columns[8]
col_q9 = df.columns[9]
col_q10 = df.columns[10]
col_q11 = df.columns[11]
col_target = df.columns[12]
col_q13 = df.columns[13]
col_q14 = df.columns[14]
col_q15 = df.columns[15]
col_q16 = df.columns[16]
col_q17 = df.columns[17]
col_q18 = df.columns[18]

# 2. Handle Structural Skip Logic for Q8 and Q16
df_analytical = df.copy()

# Q8: respondents where Q7 == 'No' were not expected to answer
q8_skip_mask = (df_analytical[col_q7] == 'No') & (df_analytical[col_q8].isna())
df_analytical.loc[q8_skip_mask, col_q8] = "Not Applicable"

# Q16: respondents where Q5 == 'No' OR Q18 contains 'Reported the account' were not expected to answer
q16_skip_mask = ((df_analytical[col_q5] == 'No') | (df_analytical[col_q18].fillna('').str.contains('Reported the account'))) & (df_analytical[col_q16].isna())
df_analytical.loc[q16_skip_mask, col_q16] = "Not Applicable"

# Map numerical severity for analysis
sev_map = {'1 (Very Low)': 1.0, '2': 2.0, '3': 3.0, '4': 4.0, '5 (Very High)': 5.0}
df_analytical['sev_num'] = df_analytical[col_q14].map(sev_map)

# Save phase2_analysis_data.csv
for out_dir in [os.path.join('Data', 'processed'), 'results']:
    df_analytical.to_csv(os.path.join(out_dir, 'phase2_analysis_data.csv'), index=False, encoding='utf-8')
print("Saved phase2_analysis_data.csv")

# 3. Target Distribution
target_counts = df_analytical[col_target].value_counts()
target_dist_df = pd.DataFrame({
    'Target_Class': target_counts.index,
    'Count': target_counts.values,
    'Percentage': (target_counts.values / len(df_analytical) * 100).round(2)
})

# 4. Ordinal Scale Mapping for Correlation & Statistics
target_ord_map = {'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3}
usage_ord_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
freq_ord_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}

ord_df = pd.DataFrame({
    'Mental_Health_Impact': df_analytical[col_target].map(target_ord_map),
    'Cyberbullying_Frequency': df_analytical[col_q11].map(freq_ord_map),
    'Daily_Usage_Hours': df_analytical[col_usage].map(usage_ord_map),
    'Emotional_Impact_Severity': df_analytical['sev_num']
})

# 5. Descriptive Statistics for Numerical/Ordinal Scales
desc_rows = [
    {
        'Scale_Variable': 'Mental_Health_Impact (Score 0 to 3)',
        'Valid_N': ord_df['Mental_Health_Impact'].notna().sum(),
        'Missing_N': ord_df['Mental_Health_Impact'].isna().sum(),
        'Mean': round(ord_df['Mental_Health_Impact'].mean(), 3),
        'Median': ord_df['Mental_Health_Impact'].median(),
        'Mode': ord_df['Mental_Health_Impact'].mode().iloc[0],
        'Std_Dev': round(ord_df['Mental_Health_Impact'].std(), 3),
        'Min': ord_df['Mental_Health_Impact'].min(),
        'Max': ord_df['Mental_Health_Impact'].max()
    },
    {
        'Scale_Variable': 'Emotional_Impact_Severity (1 to 5)',
        'Valid_N': df_analytical['sev_num'].notna().sum(),
        'Missing_N': df_analytical['sev_num'].isna().sum(),
        'Mean': round(df_analytical['sev_num'].mean(), 3),
        'Median': df_analytical['sev_num'].median(),
        'Mode': df_analytical['sev_num'].mode().iloc[0],
        'Std_Dev': round(df_analytical['sev_num'].std(), 3),
        'Min': df_analytical['sev_num'].min(),
        'Max': df_analytical['sev_num'].max()
    },
    {
        'Scale_Variable': 'Cyberbullying_Frequency (Score 0 to 4)',
        'Valid_N': ord_df['Cyberbullying_Frequency'].notna().sum(),
        'Missing_N': ord_df['Cyberbullying_Frequency'].isna().sum(),
        'Mean': round(ord_df['Cyberbullying_Frequency'].mean(), 3),
        'Median': ord_df['Cyberbullying_Frequency'].median(),
        'Mode': ord_df['Cyberbullying_Frequency'].mode().iloc[0],
        'Std_Dev': round(ord_df['Cyberbullying_Frequency'].std(), 3),
        'Min': ord_df['Cyberbullying_Frequency'].min(),
        'Max': ord_df['Cyberbullying_Frequency'].max()
    },
    {
        'Scale_Variable': 'Daily_Usage_Hours (Score 0 to 3)',
        'Valid_N': ord_df['Daily_Usage_Hours'].notna().sum(),
        'Missing_N': ord_df['Daily_Usage_Hours'].isna().sum(),
        'Mean': round(ord_df['Daily_Usage_Hours'].mean(), 3),
        'Median': ord_df['Daily_Usage_Hours'].median(),
        'Mode': ord_df['Daily_Usage_Hours'].mode().iloc[0],
        'Std_Dev': round(ord_df['Daily_Usage_Hours'].std(), 3),
        'Min': ord_df['Daily_Usage_Hours'].min(),
        'Max': ord_df['Daily_Usage_Hours'].max()
    }
]
desc_df = pd.DataFrame(desc_rows)
print("\n--- DESCRIPTIVE STATISTICS ---")
print(desc_df[['Scale_Variable', 'Valid_N', 'Mean', 'Std_Dev', 'Median', 'Mode']])

# 6. Chi-Square Tests of Independence & Cramér's V
chi_tests = [
    ('Experienced Cyberbullying (Q5)', col_q5),
    ('Witnessed Cyberbullying (Q6)', col_q6),
    ('Posted Offensive Content (Q7)', col_q7),
    ('Incident Platform (Q10)', col_q10),
    ('Cyberbullying Frequency (Q11)', col_q11),
    ('Gender Identity (Q2)', col_gender),
    ('Daily Usage Hours (Q4)', col_usage),
    ('Harassment Context Area (Q17)', col_q17)
]

chi_rows = []
for label, col in chi_tests:
    ct = pd.crosstab(df_analytical[col], df_analytical[col_target])
    chi2, p, dof, exp = stats.chi2_contingency(ct)
    n = ct.values.sum()
    min_dim = min(ct.shape[0] - 1, ct.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    
    sig = p < 0.05
    interp = (
        f"Statistically significant association (p < 0.05, V = {cramers_v:.3f}). Reject null hypothesis."
        if sig else
        f"No statistically significant association (p >= 0.05, V = {cramers_v:.3f}). Retain null hypothesis."
    )
    
    chi_rows.append({
        'Predictor_Variable': label,
        'Outcome_Variable': 'Mental Health Impact',
        'Sample_Size_N': n,
        'Chi_Square_Statistic': round(chi2, 4),
        'Degrees_of_Freedom': dof,
        'p_value': p,
        'Cramers_V': round(cramers_v, 4),
        'Significance_alpha_0_05': sig,
        'Interpretation': interp
    })

chi_df = pd.DataFrame(chi_rows)
print("\n--- CHI-SQUARE TESTS ---")
for idx, r in chi_df.iterrows():
    print(f"  {r['Predictor_Variable']:30s}: chi2={r['Chi_Square_Statistic']:8.3f}, dof={r['Degrees_of_Freedom']:2d}, p={r['p_value']:.4e}, V={r['Cramers_V']:.3f}")

# 7. Two-Group Comparisons: T-Test (Student & Welch) & Mann-Whitney U
t_test_rows = []
# Group 1: Experienced Cyberbullying (Q5 = Yes vs No)
g_yes = df_analytical[df_analytical[col_q5] == 'Yes']['sev_num'].dropna()
g_no = df_analytical[df_analytical[col_q5] == 'No']['sev_num'].dropna()

t_stat, p_t = stats.ttest_ind(g_yes, g_no, equal_var=False)
u_stat, p_u = stats.mannwhitneyu(g_yes, g_no, alternative='two-sided')

# Cohen's d
pooled_sd = np.sqrt(((len(g_yes) - 1) * g_yes.var() + (len(g_no) - 1) * g_no.var()) / (len(g_yes) + len(g_no) - 2))
cohens_d = (g_yes.mean() - g_no.mean()) / pooled_sd if pooled_sd > 0 else 0

t_test_rows.append({
    'Grouping_Variable': 'Experienced Cyberbullying (Q5: Yes vs No)',
    'Outcome_Metric': 'Emotional Impact Severity (1-5)',
    'Group_1_Name': 'Yes (Victims)',
    'Group_1_N': len(g_yes),
    'Group_1_Mean': round(g_yes.mean(), 3),
    'Group_1_SD': round(g_yes.std(), 3),
    'Group_2_Name': 'No (Non-Victims)',
    'Group_2_N': len(g_no),
    'Group_2_Mean': round(g_no.mean(), 3),
    'Group_2_SD': round(g_no.std(), 3),
    'Mean_Difference': round(g_yes.mean() - g_no.mean(), 3),
    'Welch_t_statistic': round(t_stat, 4),
    'p_value_welch': p_t,
    'Mann_Whitney_U': round(u_stat, 2),
    'p_value_mann_whitney': p_u,
    'Cohens_d': round(cohens_d, 4),
    'Significant_alpha_0_05': p_t < 0.05
})

# Also compare Mental Health Impact score (0-3) between Experienced Q5 Yes vs No
mhi_yes = ord_df.loc[df_analytical[col_q5] == 'Yes', 'Mental_Health_Impact'].dropna()
mhi_no = ord_df.loc[df_analytical[col_q5] == 'No', 'Mental_Health_Impact'].dropna()
t_mhi, p_mhi = stats.ttest_ind(mhi_yes, mhi_no, equal_var=False)
u_mhi, p_u_mhi = stats.mannwhitneyu(mhi_yes, mhi_no, alternative='two-sided')
pooled_sd_mhi = np.sqrt(((len(mhi_yes) - 1) * mhi_yes.var() + (len(mhi_no) - 1) * mhi_no.var()) / (len(mhi_yes) + len(mhi_no) - 2))
d_mhi = (mhi_yes.mean() - mhi_no.mean()) / pooled_sd_mhi if pooled_sd_mhi > 0 else 0

t_test_rows.append({
    'Grouping_Variable': 'Experienced Cyberbullying (Q5: Yes vs No)',
    'Outcome_Metric': 'Mental Health Impact Score (0-3)',
    'Group_1_Name': 'Yes (Victims)',
    'Group_1_N': len(mhi_yes),
    'Group_1_Mean': round(mhi_yes.mean(), 3),
    'Group_1_SD': round(mhi_yes.std(), 3),
    'Group_2_Name': 'No (Non-Victims)',
    'Group_2_N': len(mhi_no),
    'Group_2_Mean': round(mhi_no.mean(), 3),
    'Group_2_SD': round(mhi_no.std(), 3),
    'Mean_Difference': round(mhi_yes.mean() - mhi_no.mean(), 3),
    'Welch_t_statistic': round(t_mhi, 4),
    'p_value_welch': p_mhi,
    'Mann_Whitney_U': round(u_mhi, 2),
    'p_value_mann_whitney': p_u_mhi,
    'Cohens_d': round(d_mhi, 4),
    'Significant_alpha_0_05': p_mhi < 0.05
})

t_df = pd.DataFrame(t_test_rows)
print("\n--- TWO-GROUP COMPARISONS (WELCH T-TEST & MANN-WHITNEY U) ---")
for idx, r in t_df.iterrows():
    print(f"  {r['Outcome_Metric']}: diff={r['Mean_Difference']}, t={r['Welch_t_statistic']:.3f}, p={r['p_value_welch']:.4e}, d={r['Cohens_d']:.3f}")

# 8. Multi-Group Comparisons: One-Way ANOVA across Age and Daily Usage
anova_rows = []
for grp_col, name in [(col_age, 'Age Cohorts'), (col_usage, 'Daily Usage Hours')]:
    grps = [grp['sev_num'].dropna().values for _, grp in df_analytical.groupby(grp_col) if len(grp['sev_num'].dropna()) > 1]
    f_stat, p_val = stats.f_oneway(*grps)
    # Eta squared
    all_vals = np.concatenate(grps)
    ss_total = np.sum((all_vals - np.mean(all_vals))**2)
    ss_between = sum(len(g) * (np.mean(g) - np.mean(all_vals))**2 for g in grps)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0
    anova_rows.append({
        'Factor': name,
        'Outcome_Metric': 'Emotional Impact Severity (1-5)',
        'F_Statistic': round(f_stat, 4),
        'p_value': p_val,
        'Eta_Squared': round(eta_sq, 4),
        'Significant_alpha_0_05': p_val < 0.05
    })
anova_df = pd.DataFrame(anova_rows)

# 9. Spearman Rank Correlation
corr_pairs = [
    ('Cyberbullying_Frequency', 'Mental_Health_Impact'),
    ('Emotional_Impact_Severity', 'Mental_Health_Impact'),
    ('Cyberbullying_Frequency', 'Emotional_Impact_Severity'),
    ('Daily_Usage_Hours', 'Mental_Health_Impact'),
    ('Daily_Usage_Hours', 'Emotional_Impact_Severity'),
    ('Daily_Usage_Hours', 'Cyberbullying_Frequency')
]

corr_rows = []
for v1, v2 in corr_pairs:
    sub = ord_df[[v1, v2]].dropna()
    rho, p = stats.spearmanr(sub[v1], sub[v2])
    sig = p < 0.05
    corr_rows.append({
        'Variable_1': v1,
        'Variable_2': v2,
        'Sample_Size_N': len(sub),
        'Spearman_rho': round(rho, 4),
        'p_value': p,
        'Significance_alpha_0_05': sig,
        'Interpretation': f"{'Statistically significant' if sig else 'No significant'} monotonic association (rho = {rho:.4f}, p = {p:.4e})"
    })
corr_df = pd.DataFrame(corr_rows)
print("\n--- SPEARMAN CORRELATION MATRIX ---")
for idx, r in corr_df.iterrows():
    print(f"  {r['Variable_1']:26s} vs {r['Variable_2']:26s}: rho = {r['Spearman_rho']:7.4f}, p = {r['p_value']:.4e}")

# 10. False Discovery Rate (Benjamini-Hochberg)
all_p_tests = []
for idx, r in chi_df.iterrows():
    all_p_tests.append(('Chi-Square: ' + r['Predictor_Variable'], r['p_value']))
for idx, r in t_df.iterrows():
    all_p_tests.append(('Welch t-test: ' + r['Outcome_Metric'], r['p_value_welch']))
for idx, r in anova_df.iterrows():
    all_p_tests.append(('ANOVA: ' + r['Factor'], r['p_value']))
for idx, r in corr_df.iterrows():
    all_p_tests.append(('Spearman: ' + r['Variable_1'] + ' vs ' + r['Variable_2'], r['p_value']))

all_p_tests.sort(key=lambda x: x[1])
m_tests = len(all_p_tests)
fdr_records = []
for rank, (test_name, p_val) in enumerate(all_p_tests, start=1):
    bh_thresh = (rank / m_tests) * 0.05
    fdr_records.append({
        'Rank': rank,
        'Hypothesis_Test': test_name,
        'Raw_p_value': p_val,
        'BH_Critical_Value': bh_thresh,
        'Significant_FDR_0_05': p_val <= bh_thresh
    })
fdr_df = pd.DataFrame(fdr_records)

# 11. Demographic, Social Media Usage, Cyberbullying Experience Summaries
demo_rows = []
for val, cnt in df_analytical[col_age].value_counts().items():
    demo_rows.append({'Variable': 'Age', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
for val, cnt in df_analytical[col_gender].value_counts().items():
    demo_rows.append({'Variable': 'Gender', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
demo_df = pd.DataFrame(demo_rows)

usage_rows = []
for val, cnt in df_analytical[col_usage].value_counts().items():
    usage_rows.append({'Variable': 'Daily_Usage_Hours', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
usage_df = pd.DataFrame(usage_rows)

cb_rows = []
for val, cnt in df_analytical[col_q5].value_counts().items():
    cb_rows.append({'Variable': 'Experienced_Cyberbullying', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
for val, cnt in df_analytical[col_q11].value_counts().items():
    cb_rows.append({'Variable': 'Cyberbullying_Frequency', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
cb_df = pd.DataFrame(cb_rows)

# Compile Master Statistical Results table
master_stat_rows = []
for idx, r in chi_df.iterrows():
    master_stat_rows.append({
        'Analysis_Type': 'Chi-Square Test of Independence',
        'Comparison': f"{r['Predictor_Variable']} × {r['Outcome_Variable']}",
        'Sample_Size': r['Sample_Size_N'],
        'Statistic': f"Chi2 = {r['Chi_Square_Statistic']:.3f}, df = {r['Degrees_of_Freedom']}",
        'p_value': f"{r['p_value']:.4e}",
        'Significant_alpha_0_05': r['Significance_alpha_0_05'],
        'Summary_Interpretation': r['Interpretation']
    })
for idx, r in t_df.iterrows():
    master_stat_rows.append({
        'Analysis_Type': "Independent-Samples Welch's T-Test",
        'Comparison': f"{r['Outcome_Metric']} across {r['Grouping_Variable']}",
        'Sample_Size': f"N1={r['Group_1_N']}, N2={r['Group_2_N']}",
        'Statistic': f"t = {r['Welch_t_statistic']:.3f}",
        'p_value': f"{r['p_value_welch']:.4e}",
        'Significant_alpha_0_05': r['Significant_alpha_0_05'],
        'Summary_Interpretation': f"Welch t-test diff = {r['Mean_Difference']}, Cohen's d = {r['Cohens_d']:.3f}"
    })
for idx, r in corr_df.iterrows():
    master_stat_rows.append({
        'Analysis_Type': 'Spearman Rank Correlation',
        'Comparison': f"{r['Variable_1']} vs {r['Variable_2']}",
        'Sample_Size': r['Sample_Size_N'],
        'Statistic': f"Spearman rho = {r['Spearman_rho']:.4f}",
        'p_value': f"{r['p_value']:.4e}",
        'Significant_alpha_0_05': r['Significance_alpha_0_05'],
        'Summary_Interpretation': r['Interpretation']
    })
master_stat_df = pd.DataFrame(master_stat_rows)

# 12. Save All Research CSVs in Data/processed/ and results/
all_csv_exports = [
    ('descriptive_statistics.csv', desc_df),
    ('target_distribution.csv', target_dist_df),
    ('chi_square_results.csv', chi_df),
    ('t_test_results.csv', t_df),
    ('two_group_comparison_results.csv', t_df),
    ('anova_results.csv', anova_df),
    ('multigroup_comparison_results.csv', anova_df),
    ('spearman_correlation_results.csv', corr_df),
    ('correlation_results.csv', corr_df),
    ('fdr_corrected_results.csv', fdr_df),
    ('demographic_distribution.csv', demo_df),
    ('social_media_usage.csv', usage_df),
    ('cyberbullying_experience.csv', cb_df),
    ('statistical_results.csv', master_stat_df)
]

for out_dir in [os.path.join('Data', 'processed'), 'results']:
    os.makedirs(out_dir, exist_ok=True)
    for fname, data_obj in all_csv_exports:
        data_obj.to_csv(os.path.join(out_dir, fname), index=False, encoding='utf-8')

print("All research CSV tables exported successfully!")

# 13. Generate Figures in results/figures/
os.makedirs(os.path.join('results', 'figures'), exist_ok=True)

# Figure 1: 4-Panel Statistical Visualizations Grid
fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# Panel A: Target Class Distribution
palette = ['#601D49', '#BD5579', '#EA9D9D', '#FFEBB8']
sns.barplot(x=target_dist_df['Target_Class'], y=target_dist_df['Count'], ax=axes[0, 0], palette='Blues_r')
axes[0, 0].set_title(f'A: Mental Health Impact Distribution (N = {len(df_analytical)})', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Number of Respondents')
axes[0, 0].set_xlabel('Self-Reported Impact Class')
for p in axes[0, 0].patches:
    axes[0, 0].annotate(f"{int(p.get_height())}\n({p.get_height()/len(df_analytical)*100:.1f}%)",
                        (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                        ha='center', va='center', color='black', fontsize=9, fontweight='semibold')

# Panel B: Cyberbullying Experience vs Mental Health Impact
ct_exp = pd.crosstab(df_analytical[col_q5], df_analytical[col_target], normalize='index') * 100
ct_exp.plot(kind='bar', stacked=True, ax=axes[0, 1], colormap='Purples')
axes[0, 1].set_title('B: Mental Health Impact by Victimization Status (Q5)', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Percentage of Respondents (%)')
axes[0, 1].set_xlabel('Experienced Cyberbullying')
axes[0, 1].legend(title='Impact Class', bbox_to_anchor=(1.02, 1), loc='upper left')

# Panel C: Incident Platform Distribution
plat_counts = df_analytical[col_q10].value_counts()
sns.barplot(x=plat_counts.index, y=plat_counts.values, ax=axes[1, 0], palette='crest')
axes[1, 0].set_title('C: Reported Incident Platforms (Q10)', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_xlabel('Platform')
axes[1, 0].tick_params(axis='x', rotation=25)

# Panel D: Daily Social Media Usage Hours
usage_order = ['Less than 1 hour', '1–3 hours', '3–5 hours', 'More than 5 hours']
usage_counts = df_analytical[col_usage].value_counts().reindex(usage_order).dropna()
sns.barplot(x=usage_counts.index, y=usage_counts.values, ax=axes[1, 1], palette='mako')
axes[1, 1].set_title('D: Daily Social Media Usage Distribution', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_xlabel('Usage Bracket')
axes[1, 1].tick_params(axis='x', rotation=15)

plt.tight_layout()
grid_path = os.path.join('results', 'figures', 'statistical_visualizations_grid.png')
plt.savefig(grid_path, dpi=300)
plt.close()
print(f"Saved: {grid_path}")

# Figure 2: Spearman Correlation Heatmap
plt.figure(figsize=(8, 6))
corr_mat = ord_df.corr(method='spearman')
mask = np.triu(np.ones_like(corr_mat, dtype=bool))
sns.heatmap(corr_mat, annot=True, fmt='.3f', cmap='coolwarm', vmin=-0.1, vmax=0.6,
            square=True, linewidths=.5, cbar_kws={'label': "Spearman's Rank Correlation (rho)"})
plt.title('Spearman Rank Correlation Heatmap (Ordinal Variables)', fontsize=12, fontweight='bold')
plt.tight_layout()
heatmap_path = os.path.join('results', 'figures', 'correlation_heatmap.png')
plt.savefig(heatmap_path, dpi=300)
plt.close()
print(f"Saved: {heatmap_path}")

# Figure 3: Normality Assumption Q-Q Plot
fig, ax = plt.subplots(figsize=(7, 5))
stats.probplot(df_analytical['sev_num'].dropna(), dist="norm", plot=ax)
ax.set_title('Q-Q Plot for Emotional Impact Severity Scale', fontsize=12, fontweight='bold')
plt.tight_layout()
qq_path = os.path.join('results', 'figures', 'assumption_qq_plots.png')
plt.savefig(qq_path, dpi=300)
plt.close()
print(f"Saved: {qq_path}")

print("\nPhase 2 Statistical Analysis completed successfully!")
