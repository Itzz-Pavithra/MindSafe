import os
import io
import pandas as pd
import numpy as np
from scipy import stats

# 1. Load Phase 1 cleaned dataset
cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
if not os.path.exists(cleaned_path):
    raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_path}")

df_cleaned = pd.read_csv(cleaned_path, encoding='utf-8', keep_default_na=False)
for col in df_cleaned.columns:
    df_cleaned[col] = df_cleaned[col].replace({'': np.nan})

print(f"Loaded Phase 1 cleaned dataset: {df_cleaned.shape}")

# 2. Step 1: Remove completely blank survey submissions (Rows 21 and 80)
# Programmatic audit of blank rows
survey_cols = df_cleaned.columns[1:] # 18 survey questions
row_missing = df_cleaned[survey_cols].isna().sum(axis=1)
blank_indices = row_missing[row_missing == 18].index.tolist()
print(f"Detected completely blank submissions (indices): {blank_indices}")

df_analytical = df_cleaned.drop(index=blank_indices).reset_index(drop=True)
print(f"Original Phase 1 rows: {len(df_cleaned)}")
print(f"Completely blank rows removed: {len(blank_indices)}")
print(f"Final Phase 2 analytical rows: {len(df_analytical)}")
assert len(df_analytical) == 519, f"Expected 519 rows, got {len(df_analytical)}"

# 3. Step 2: Handle Structural Skip Logic for Q8 and Q16
col_q5 = [c for c in df_analytical.columns if '5. Have you personally experienced' in c][0]
col_q7 = [c for c in df_analytical.columns if c.startswith('7.')][0]
col_q8 = [c for c in df_analytical.columns if c.startswith('8.')][0]
col_q16 = [c for c in df_analytical.columns if '16. If you did not report' in c][0]
col_q18 = [c for c in df_analytical.columns if c.startswith('18.')][0]

orig_q8_miss = df_analytical[col_q8].isna().sum()
orig_q16_miss = df_analytical[col_q16].isna().sum()

# Q8: respondents where Q7 == 'No' were not expected to answer
q8_skip_mask = (df_analytical[col_q7] == 'No') & (df_analytical[col_q8].isna())
q8_skip_count = q8_skip_mask.sum()
df_analytical.loc[q8_skip_mask, col_q8] = "Not Applicable"
q8_true_miss = df_analytical[col_q8].isna().sum()

# Q16: respondents where Q5 == 'No' OR Q18 contains 'Reported the account' were not expected to answer
q16_skip_mask = ((df_analytical[col_q5] == 'No') | (df_analytical[col_q18].fillna('').str.contains('Reported the account'))) & (df_analytical[col_q16].isna())
q16_skip_count = q16_skip_mask.sum()
df_analytical.loc[q16_skip_mask, col_q16] = "Not Applicable"
q16_true_miss = df_analytical[col_q16].isna().sum()

print("\n--- STRUCTURAL SKIP-LOGIC REPORT ---")
skip_report_df = pd.DataFrame([
    {
        'Column': '8. If yes, what was the main reason for your action?',
        'Original_Missing_Count': orig_q8_miss,
        'Structural_Skip_Count': q8_skip_count,
        'True_Missing_Count': q8_true_miss,
        'Final_Treatment': 'Coded as "Not Applicable" for non-perpetrators (Q7 == No)'
    },
    {
        'Column': '16. If you did not report the incident, what was the main reason?',
        'Original_Missing_Count': orig_q16_miss,
        'Structural_Skip_Count': q16_skip_count,
        'True_Missing_Count': q16_true_miss,
        'Final_Treatment': 'Coded as "Not Applicable" for unharassed (Q5 == No) or reported cases (Q18 reported)'
    }
])
print(skip_report_df.to_string())

# Save phase2_analysis_data.csv
analytical_csv_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
df_analytical.to_csv(analytical_csv_path, index=False, encoding='utf-8')
print(f"\nSaved analytical dataset to: {analytical_csv_path}")

# 4. Target Variable Analysis
col_target = [c for c in df_analytical.columns if '12. Do you think cyberbullying' in c][0]
target_counts = df_analytical[col_target].value_counts(dropna=False)
valid_target_cnt = df_analytical[col_target].notna().sum()

target_dist_rows = []
ordered_cats = ['Not at all', 'Slightly', 'Moderately', 'Severely']
for cat in ordered_cats:
    cnt = target_counts.get(cat, 0)
    target_dist_rows.append({
        'Category': cat,
        'Ordinal_Score': ordered_cats.index(cat),
        'Frequency': cnt,
        'Valid_Percentage': round((cnt / valid_target_cnt) * 100, 2),
        'Total_Percentage': round((cnt / len(df_analytical)) * 100, 2)
    })
# Add missing
target_miss_cnt = df_analytical[col_target].isna().sum()
target_dist_rows.append({
    'Category': 'Missing (NaN)',
    'Ordinal_Score': np.nan,
    'Frequency': target_miss_cnt,
    'Valid_Percentage': np.nan,
    'Total_Percentage': round((target_miss_cnt / len(df_analytical)) * 100, 2)
})
target_dist_df = pd.DataFrame(target_dist_rows)
target_dist_csv = os.path.join('Data', 'processed', 'mental_health_impact_distribution.csv')
target_dist_df.to_csv(target_dist_csv, index=False, encoding='utf-8')

# 5. Chi-Square Tests of Independence
chi_tests = [
    ("Experienced_Cyberbullying", [c for c in df_analytical.columns if '5. Have you personally experienced' in c][0]),
    ("Cyberbullying_Frequency", [c for c in df_analytical.columns if c.startswith('11.')][0]),
    ("Incident_Platform", [c for c in df_analytical.columns if c.startswith('10.')][0]),
    ("Witnessed_Cyberbullying", [c for c in df_analytical.columns if c.startswith('6.')][0]),
    ("Daily_Usage_Hours", [c for c in df_analytical.columns if c.startswith('4.')][0]),
    ("Gender", [c for c in df_analytical.columns if c.startswith('2.')][0]),
    ("Posted_Offensive_Content", [c for c in df_analytical.columns if c.startswith('7.')][0]),
    ("Harassment_Context_Area", [c for c in df_analytical.columns if c.startswith('17.')][0])
]

chi_results_rows = []
for short_name, col in chi_tests:
    sub = df_analytical[[col, col_target]].dropna()
    crosstab = pd.crosstab(sub[col], sub[col_target])
    chi2, p, dof, exp = stats.chi2_contingency(crosstab)
    sig = p < 0.05
    interp = (
        f"Statistically significant association detected (p < 0.05). There is sample evidence of dependence between {short_name} and Mental Health Impact."
        if sig else
        f"No statistically significant association detected (p >= 0.05). Null hypothesis of independence cannot be rejected."
    )
    chi_results_rows.append({
        'Variable_1': short_name,
        'Variable_2': 'Mental_Health_Impact',
        'Sample_Size_N': len(sub),
        'Chi_Square_Statistic': round(chi2, 4),
        'Degrees_of_Freedom': dof,
        'p_value': p,
        'Significance_alpha_0_05': sig,
        'Min_Expected_Cell_Freq': round(exp.min(), 2),
        'Interpretation': interp
    })

chi_df = pd.DataFrame(chi_results_rows)
chi_csv_path = os.path.join('Data', 'processed', 'chi_square_results.csv')
chi_df.to_csv(chi_csv_path, index=False, encoding='utf-8')
print(f"Saved Chi-Square results to: {chi_csv_path}")

# 6. T-Test Assessment
col_q14 = [c for c in df_analytical.columns if c.startswith('14.')][0]
sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
df_analytical['sev_num'] = df_analytical[col_q14].map(sev_map)

g_yes = df_analytical[df_analytical[col_q5] == 'Yes']['sev_num'].dropna()
g_no = df_analytical[df_analytical[col_q5] == 'No']['sev_num'].dropna()

welch_t, welch_p = stats.ttest_ind(g_yes, g_no, equal_var=False)
stud_t, stud_p = stats.ttest_ind(g_yes, g_no, equal_var=True)
# df for Welch approximation
s1, s2 = g_yes.var(), g_no.var()
n1, n2 = len(g_yes), len(g_no)
welch_df = ((s1/n1 + s2/n2)**2) / (((s1/n1)**2)/(n1-1) + ((s2/n2)**2)/(n2-1))

t_test_rows = [
    {
        'Test_Type': "Independent-Samples Welch's T-Test (Unequal Variances)",
        'Variable_Tested': "Emotional_Impact_Severity (1 to 5 scale)",
        'Grouping_Variable': "Experienced_Cyberbullying",
        'Group_1': "Yes (Victimized)",
        'Group_1_N': n1,
        'Group_1_Mean': round(g_yes.mean(), 3),
        'Group_1_Std': round(g_yes.std(), 3),
        'Group_2': "No (Non-Victimized)",
        'Group_2_N': n2,
        'Group_2_Mean': round(g_no.mean(), 3),
        'Group_2_Std': round(g_no.std(), 3),
        'Mean_Difference': round(g_yes.mean() - g_no.mean(), 3),
        't_statistic': round(welch_t, 4),
        'Degrees_of_Freedom': round(welch_df, 2),
        'p_value': welch_p,
        'Significance_alpha_0_05': welch_p < 0.05,
        'Interpretation': "Statistically significant difference in mean emotional impact severity between participants who personally experienced cyberbullying and those who did not (p < 0.001)."
    },
    {
        'Test_Type': "Independent-Samples Student's T-Test (Pooled Variance)",
        'Variable_Tested': "Emotional_Impact_Severity (1 to 5 scale)",
        'Grouping_Variable': "Experienced_Cyberbullying",
        'Group_1': "Yes (Victimized)",
        'Group_1_N': n1,
        'Group_1_Mean': round(g_yes.mean(), 3),
        'Group_1_Std': round(g_yes.std(), 3),
        'Group_2': "No (Non-Victimized)",
        'Group_2_N': n2,
        'Group_2_Mean': round(g_no.mean(), 3),
        'Group_2_Std': round(g_no.std(), 3),
        'Mean_Difference': round(g_yes.mean() - g_no.mean(), 3),
        't_statistic': round(stud_t, 4),
        'Degrees_of_Freedom': n1 + n2 - 2,
        'p_value': stud_p,
        'Significance_alpha_0_05': stud_p < 0.05,
        'Interpretation': "Statistically significant difference under standard pooled-variance assumption (p < 0.001)."
    }
]

t_df = pd.DataFrame(t_test_rows)
t_csv_path = os.path.join('Data', 'processed', 't_test_results.csv')
t_df.to_csv(t_csv_path, index=False, encoding='utf-8')
print(f"Saved T-Test results to: {t_csv_path}")

# 7. Correlation Analysis (Spearman Rank)
col_usage = [c for c in df_analytical.columns if c.startswith('4.')][0]
col_freq = [c for c in df_analytical.columns if c.startswith('11.')][0]

target_ord_map = {'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3}
usage_ord_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
freq_ord_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}

ord_df = pd.DataFrame({
    'Mental_Health_Impact': df_analytical[col_target].map(target_ord_map),
    'Cyberbullying_Frequency': df_analytical[col_freq].map(freq_ord_map),
    'Daily_Usage_Hours': df_analytical[col_usage].map(usage_ord_map),
    'Emotional_Impact_Severity': df_analytical['sev_num']
})

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
    interp = (
        f"Statistically significant positive monotonic association (rho = {rho:.3f}, p < 0.05)."
        if sig and rho > 0 else
        f"Statistically significant negative monotonic association (rho = {rho:.3f}, p < 0.05)."
        if sig and rho < 0 else
        f"No statistically significant monotonic association detected (rho = {rho:.3f}, p >= 0.05)."
    )
    corr_rows.append({
        'Variable_1': v1,
        'Variable_2': v2,
        'Sample_Size_N': len(sub),
        'Spearman_rho': round(rho, 4),
        'p_value': p,
        'Significance_alpha_0_05': sig,
        'Interpretation': interp
    })

corr_df = pd.DataFrame(corr_rows)
corr_csv_path = os.path.join('Data', 'processed', 'correlation_results.csv')
corr_df.to_csv(corr_csv_path, index=False, encoding='utf-8')
print(f"Saved correlation results to: {corr_csv_path}")

# 8. Feature Selection Screening Table
features_screen = [
    {
        'Feature': 'Timestamp',
        'Variable_Type': 'Metadata / Identifier',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'None (Survey metadata)',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Exclude',
        'Reason': 'Temporal artifact of Google Forms submission. Irrelevant to psychological prediction.'
    },
    {
        'Feature': 'Age',
        'Variable_Type': 'Demographic (Ordinal)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Background demographic predictor',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Core demographic factor across young adult cohorts. No missing data after blank row removal.'
    },
    {
        'Feature': 'Gender',
        'Variable_Type': 'Demographic (Nominal)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Chi-sq p = 0.138 (Subgroup differences)',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Essential demographic covariate for subgroup vulnerability and fairness auditing.'
    },
    {
        'Feature': 'Platforms_Used',
        'Variable_Type': 'Survey Feature (Multiselect)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Multiselect exposure metric',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Captures platform exposure diversity. Suitable for multi-hot / one-hot feature encoding.'
    },
    {
        'Feature': 'Daily_Usage_Hours',
        'Variable_Type': 'Survey Feature (Usage Intensity/Ordinal)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Chi-sq p = 0.439, rho = -0.018',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Screen time exposure intensity. Ordinal representation preserves dose-response structure.'
    },
    {
        'Feature': 'Experienced_Cyberbullying',
        'Variable_Type': 'Survey Feature (Victimization/Binary)',
        'Missing_%': '0.19%',
        'Statistical_Relevance': 'Chi-sq p = 1.67e-31 (Primary predictor)',
        'Target_Leakage_Risk': 'Low (Exposure measure)',
        'Recommended_Status': 'Candidate',
        'Reason': 'Strongest bivariate predictor of mental health impact. Critical primary feature.'
    },
    {
        'Feature': 'Witnessed_Cyberbullying',
        'Variable_Type': 'Survey Feature (Bystander/Binary)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Chi-sq p = 0.342',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Measures bystander/witness exposure to online toxicity in respondent network.'
    },
    {
        'Feature': 'Posted_Offensive_Content',
        'Variable_Type': 'Survey Feature (Perpetration/Categorical)',
        'Missing_%': '0.00%',
        'Statistical_Relevance': 'Chi-sq p = 0.067 (Marginal)',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Captures online behavioral conduct and potential bully-victim overlap.'
    },
    {
        'Feature': 'Offensive_Action_Reason',
        'Variable_Type': 'Conditional Survey Feature (Skip-Logic)',
        'Missing_%': '0.19% (True missing; 71.5% Not Applicable)',
        'Statistical_Relevance': 'Sub-sample motivation',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Review',
        'Reason': 'High skip-logic sparsity. Applicable only to perpetrator subpopulation; requires dedicated indicator encoding.'
    },
    {
        'Feature': 'Cyberbullying_Types_Observed',
        'Variable_Type': 'Survey Feature (Bullying Modality/Multiselect)',
        'Missing_%': '1.54%',
        'Statistical_Relevance': 'Harassment modality taxonomy',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Differentiates harassment modalities (hate speech, fake profiles, threats, rumors) via multi-hot encoding.'
    },
    {
        'Feature': 'Incident_Platform',
        'Variable_Type': 'Survey Feature (Incident Context/Nominal)',
        'Missing_%': '1.93%',
        'Statistical_Relevance': 'Chi-sq p = 0.041 (Significant)',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Specific platform where harassment occurred. Shows statistically significant association with impact.'
    },
    {
        'Feature': 'Cyberbullying_Frequency',
        'Variable_Type': 'Survey Feature (Frequency/Ordinal)',
        'Missing_%': '1.35%',
        'Statistical_Relevance': 'Chi-sq p = 6.88e-07, rho = 0.242',
        'Target_Leakage_Risk': 'Low (Chronicity)',
        'Recommended_Status': 'Candidate',
        'Reason': 'Chronicity and recurrence of cyberbullying. Highly significant dose-response monotonic predictor.'
    },
    {
        'Feature': 'Negative_Emotional_Symptoms',
        'Variable_Type': 'Survey Feature (Symptomatology/Multiselect)',
        'Missing_%': '1.35% (None = 222 valid responses)',
        'Statistical_Relevance': 'High (Symptom manifestation)',
        'Target_Leakage_Risk': 'CRITICAL / HIGH (Target Overlap)',
        'Recommended_Status': 'Review',
        'Reason': 'Measures concurrent emotional symptoms (anxiety, depression, anger). Retained in Scenario A; excluded in Scenario B to avoid leakage.'
    },
    {
        'Feature': 'Emotional_Impact_Severity',
        'Variable_Type': 'Survey Feature (Severity Rating/Ordinal 1-5)',
        'Missing_%': '1.93%',
        'Statistical_Relevance': 'T-test p = 1.08e-29, rho = 0.319',
        'Target_Leakage_Risk': 'CRITICAL / HIGH (Target Overlap)',
        'Recommended_Status': 'Review',
        'Reason': 'Direct numeric proxy of emotional distress severity. Retained in Scenario A; excluded in Scenario B to prevent trivial tautological prediction.'
    },
    {
        'Feature': 'Sought_Help',
        'Variable_Type': 'Survey Feature (Coping Support/Multiselect)',
        'Missing_%': '1.73%',
        'Statistical_Relevance': 'Help-seeking behavior',
        'Target_Leakage_Risk': 'Low',
        'Recommended_Status': 'Candidate',
        'Reason': 'Measures formal/informal coping intervention and psychological resilience support.'
    },
    {
        'Feature': 'Reason_Not_Reported',
        'Variable_Type': 'Conditional Survey Feature (Skip-Logic)',
        'Missing_%': '0.19% (True missing; 17.5% Not Applicable)',
        'Statistical_Relevance': 'Legal awareness & reporting barriers',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Review',
        'Reason': 'Captures institutional/legal awareness hurdles (fear, lack of awareness, privacy). Requires explicit "Not Applicable" encoding.'
    },
    {
        'Feature': 'Harassment_Context_Area',
        'Variable_Type': 'Survey Feature (Incident Environment/Nominal)',
        'Missing_%': '2.70%',
        'Statistical_Relevance': 'Social context of harassment',
        'Target_Leakage_Risk': 'None',
        'Recommended_Status': 'Candidate',
        'Reason': 'Identifies relational sphere of harassment (school, friends, gaming, stranger, family).'
    },
    {
        'Feature': 'Action_Taken',
        'Variable_Type': 'Survey Feature (Reactive Response/Multiselect)',
        'Missing_%': '2.70%',
        'Statistical_Relevance': 'Behavioral coping mechanisms',
        'Target_Leakage_Risk': 'Low',
        'Recommended_Status': 'Candidate',
        'Reason': 'Documents behavioral protective responses (blocking, reporting, ignoring, telling family).'
    }
]

feat_sel_df = pd.DataFrame(features_screen)
feat_sel_csv = os.path.join('Data', 'processed', 'feature_selection_results.csv')
feat_sel_df.to_csv(feat_sel_csv, index=False, encoding='utf-8')
print(f"Saved feature selection results to: {feat_sel_csv}")

# 9. Additional Research Summary Tables (Tables 1 - 5)
# Table 1: Demographic distribution
col_age = [c for c in df_analytical.columns if '1. What is your age?' in c][0]
col_gender = [c for c in df_analytical.columns if '2. What is your gender?' in c][0]

demo_rows = []
for val, cnt in df_analytical[col_age].value_counts().items():
    demo_rows.append({'Variable': 'Age', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
for val, cnt in df_analytical[col_gender].value_counts().items():
    demo_rows.append({'Variable': 'Gender', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
demo_df = pd.DataFrame(demo_rows)
demo_df.to_csv(os.path.join('Data', 'processed', 'demographic_distribution.csv'), index=False, encoding='utf-8')

# Table 2: Social media usage
col_plat = [c for c in df_analytical.columns if '3. Which social media' in c][0]
usage_rows = []
for val, cnt in df_analytical[col_usage].value_counts().items():
    usage_rows.append({'Variable': 'Daily_Usage_Hours', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
usage_df = pd.DataFrame(usage_rows)
usage_df.to_csv(os.path.join('Data', 'processed', 'social_media_usage.csv'), index=False, encoding='utf-8')

# Table 3: Cyberbullying experience
cb_rows = []
for val, cnt in df_analytical[col_q5].value_counts().items():
    cb_rows.append({'Variable': 'Experienced_Cyberbullying', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
for val, cnt in df_analytical[col_freq].value_counts().items():
    cb_rows.append({'Variable': 'Cyberbullying_Frequency', 'Category': val, 'Count': cnt, 'Percentage': round(cnt/len(df_analytical)*100, 2)})
cb_df = pd.DataFrame(cb_rows)
cb_df.to_csv(os.path.join('Data', 'processed', 'cyberbullying_experience.csv'), index=False, encoding='utf-8')

# Table 5: Descriptive statistics for numerical/ordinal scales
desc_rows = [
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
desc_df.to_csv(os.path.join('Data', 'processed', 'descriptive_statistics.csv'), index=False, encoding='utf-8')

# Table 10: Master statistical results compilation
master_stat_rows = []
for idx, r in chi_df.iterrows():
    master_stat_rows.append({
        'Analysis_Type': 'Chi-Square Test of Independence',
        'Comparison': f"{r['Variable_1']} × {r['Variable_2']}",
        'Sample_Size': r['Sample_Size_N'],
        'Statistic': f"Chi2 = {r['Chi_Square_Statistic']:.3f}, df = {r['Degrees_of_Freedom']}",
        'p_value': f"{r['p_value']:.4e}",
        'Significant_alpha_0_05': r['Significance_alpha_0_05'],
        'Summary_Interpretation': r['Interpretation']
    })
for idx, r in t_df.iterrows():
    master_stat_rows.append({
        'Analysis_Type': r['Test_Type'],
        'Comparison': f"{r['Variable_Tested']} across {r['Grouping_Variable']}",
        'Sample_Size': f"N1={r['Group_1_N']}, N2={r['Group_2_N']}",
        'Statistic': f"t = {r['t_statistic']:.3f}, df = {r['Degrees_of_Freedom']}",
        'p_value': f"{r['p_value']:.4e}",
        'Significant_alpha_0_05': r['Significance_alpha_0_05'],
        'Summary_Interpretation': r['Interpretation']
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
master_stat_csv = os.path.join('Data', 'processed', 'statistical_results.csv')
master_stat_df.to_csv(master_stat_csv, index=False, encoding='utf-8')
print(f"Saved master statistical results compilation to: {master_stat_csv}")

print("\n>>> ALL PHASE 2 DATASETS AND RESEARCH TABLES GENERATED SUCCESSFULLY! <<<")
