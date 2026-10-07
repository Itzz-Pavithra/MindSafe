import os
import io
import pandas as pd
import numpy as np

print("==================================================")
print("PHASE 1: DATA CLEANING AND PREPROCESSING")
print("==================================================")

raw_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

if not os.path.exists(raw_path):
    raise FileNotFoundError(f"Raw CSV not found at {raw_path}")

with open(raw_path, 'rb') as f:
    raw_bytes = f.read()

print(f"Read {len(raw_bytes):,} bytes from raw CSV.")

# 1. Normalize encoding (mixed UTF-8 and CP1252)
clean_bytes = raw_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df_raw = pd.read_csv(io.StringIO(text), keep_default_na=False)
raw_row_count = len(df_raw)
print(f"Total raw rows parsed: {raw_row_count}")
print(f"Total columns: {len(df_raw.columns)}")

# 2. Standardize column names (strip unnecessary leading/trailing whitespace, normalize newlines to single space)
raw_col_names = list(df_raw.columns)
clean_col_names = [' '.join(col.split()) for col in raw_col_names]
df_raw.columns = clean_col_names

# 3. Standardize whitespace in all cell values
for col in df_raw.columns:
    df_raw[col] = df_raw[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

# 4. Standardize missing values
col13_name = clean_col_names[13] # "Which of the following did you experience?"
null_tokens = {'', 'na', 'n/a', 'null', 'nan', 'nil'}

for col in df_raw.columns:
    if col == col13_name:
        # In Col 13, "None" is a valid questionnaire option; only empty string is missing
        df_raw[col] = df_raw[col].apply(lambda x: np.nan if isinstance(x, str) and x.lower() in {'', 'na', 'n/a', 'null', 'nan'} else x)
    else:
        df_raw[col] = df_raw[col].apply(lambda x: np.nan if isinstance(x, str) and x.lower() in null_tokens else x)

# 5. Check exact duplicate rows across all columns
exact_dupes = df_raw.duplicated().sum()
print(f"Exact duplicate rows detected: {exact_dupes}")

# 6. Audit completely blank submissions (where all 18 survey questions are missing)
survey_cols = df_raw.columns[1:]
blank_mask = df_raw[survey_cols].isna().all(axis=1)
blank_indices = df_raw[blank_mask].index.tolist()
print(f"Completely blank survey submissions: {len(blank_indices)} (Indices: {blank_indices})")

# 7. Audit target variable missing values
col12_target = clean_col_names[12]
missing_target_mask = df_raw[col12_target].isna()
missing_target_indices = df_raw[missing_target_mask].index.tolist()
print(f"Total missing target records: {len(missing_target_indices)} (Indices: {missing_target_indices})")

# Records to remove: any record with missing target (which includes the blank rows)
remove_mask = missing_target_mask
removed_indices = df_raw[remove_mask].index.tolist()
print(f"Total records removed: {len(removed_indices)}")
for idx in removed_indices:
    non_nulls = df_raw.loc[idx].notna().sum()
    if idx in blank_indices:
        reason = "Completely blank survey submission (all 18 survey questions empty)"
    else:
        reason = f"Incomplete submission missing target variable (only {non_nulls}/19 questions answered)"
    print(f"  - Record Index {idx}: {reason}")

# 8. Create Analytical Dataset
df_clean = df_raw[~remove_mask].copy().reset_index(drop=True)
final_analytical_count = len(df_clean)
print(f"\nFinal Analytical Dataset Size: {final_analytical_count} valid records")

# 9. Verify Target Distribution
target_series = df_clean[col12_target]
target_counts = target_series.value_counts()
target_pcts = (target_counts / final_analytical_count * 100).round(2)
target_dist_df = pd.DataFrame({
    'Target_Class': target_counts.index,
    'Count': target_counts.values,
    'Percentage': target_pcts.values
})

print("\n--- TARGET VARIABLE DISTRIBUTION (Mental_Health_Impact) ---")
for idx, r in target_dist_df.iterrows():
    print(f"  {r['Target_Class']:12s}: {r['Count']:4d} ({r['Percentage']:.2f}%)")

# Verify all four classes exist
expected_classes = {'Not at all', 'Slightly', 'Moderately', 'Severely'}
actual_classes = set(target_counts.index)
assert expected_classes.issubset(actual_classes), f"Missing target classes! Expected {expected_classes}, got {actual_classes}"
print("All four target classes are fully represented!")

# 10. Save cleaned datasets
os.makedirs(os.path.join('Data', 'processed'), exist_ok=True)
os.makedirs('results', exist_ok=True)

for out_dir in [os.path.join('Data', 'processed'), 'results']:
    df_clean.to_csv(os.path.join(out_dir, 'cleaned_survey_data.csv'), index=False, encoding='utf-8')
    target_dist_df.to_csv(os.path.join(out_dir, 'target_distribution.csv'), index=False, encoding='utf-8')

# 11. Generate Data Quality Report
short_names = [
    "Timestamp", "Age", "Gender", "Platforms_Used", "Daily_Usage_Hours",
    "Experienced_Cyberbullying", "Witnessed_Cyberbullying", "Posted_Offensive_Content",
    "Offensive_Action_Reason", "Cyberbullying_Types_Observed", "Incident_Platform",
    "Cyberbullying_Frequency", "Mental_Health_Impact", "Negative_Emotional_Symptoms",
    "Emotional_Impact_Severity", "Sought_Help", "Reason_Not_Reported",
    "Harassment_Context_Area", "Action_Taken"
]

question_types = [
    "Metadata / Timestamp",
    "Demographic (Categorical/Ordinal)",
    "Demographic (Categorical/Nominal)",
    "Survey Feature (Multiselect)",
    "Survey Feature (Usage Intensity/Ordinal)",
    "Survey Feature (Victimization/Binary)",
    "Survey Feature (Bystander/Binary)",
    "Survey Feature (Perpetration/Categorical)",
    "Survey Feature (Conditional Reason/Skip-Logic)",
    "Survey Feature (Bullying Types/Multiselect)",
    "Survey Feature (Incident Context/Nominal)",
    "Survey Feature (Frequency/Ordinal)",
    "Primary Target Variable (Ordinal Categorical)",
    "Survey Feature (Symptomatology/Multiselect)",
    "Survey Feature (Emotional Severity/Ordinal 1-5)",
    "Survey Feature (Coping Support/Multiselect)",
    "Survey Feature (Legal/Reporting Barriers/Skip-Logic)",
    "Survey Feature (Incident Environment/Nominal)",
    "Survey Feature (Response Action/Multiselect)"
]

report_rows = []
for i, col in enumerate(df_clean.columns):
    total_val = len(df_clean)
    missing_val = df_clean[col].isna().sum()
    valid_val = total_val - missing_val
    missing_pct = round((missing_val / total_val) * 100, 2)
    unique_cnt = df_clean[col].nunique(dropna=True)
    sample_cats = " | ".join([str(v) for v in df_clean[col].dropna().unique()[:4]])
    
    report_rows.append({
        'Column_Index': i,
        'Short_Name': short_names[i],
        'Clean_Column_Name': col,
        'Raw_Column_Name': raw_col_names[i],
        'Data_Type': str(df_clean[col].dtype),
        'Question_Type': question_types[i],
        'Total_Responses': total_val,
        'Valid_Responses': valid_val,
        'Missing_Count': missing_val,
        'Missing_Percentage': missing_pct,
        'Unique_Categories_Count': unique_cnt,
        'Sample_Categories': sample_cats
    })

report_df = pd.DataFrame(report_rows)
for out_dir in [os.path.join('Data', 'processed'), 'results']:
    report_df.to_csv(os.path.join(out_dir, 'data_quality_report.csv'), index=False, encoding='utf-8')

# 12. Preprocessing summary
summary_df = pd.DataFrame([
    {'Metric': 'Raw Survey Responses Collected', 'Value': raw_row_count},
    {'Metric': 'Exact Duplicate Records Removed', 'Value': exact_dupes},
    {'Metric': 'Completely Blank Submissions Removed', 'Value': len(blank_indices)},
    {'Metric': 'Incomplete Missing Target Records Removed', 'Value': len(missing_target_indices) - len(blank_indices)},
    {'Metric': 'Total Dropped Records', 'Value': len(removed_indices)},
    {'Metric': 'Final Analytical Dataset Size', 'Value': final_analytical_count},
    {'Metric': 'Target Variable', 'Value': 'Mental_Health_Impact'},
    {'Metric': 'Target Class Not at all', 'Value': f"{target_counts.get('Not at all', 0)} ({target_pcts.get('Not at all', 0):.2f}%)"},
    {'Metric': 'Target Class Slightly', 'Value': f"{target_counts.get('Slightly', 0)} ({target_pcts.get('Slightly', 0):.2f}%)"},
    {'Metric': 'Target Class Moderately', 'Value': f"{target_counts.get('Moderately', 0)} ({target_pcts.get('Moderately', 0):.2f}%)"},
    {'Metric': 'Target Class Severely', 'Value': f"{target_counts.get('Severely', 0)} ({target_pcts.get('Severely', 0):.2f}%)"}
])

for out_dir in [os.path.join('Data', 'processed'), 'results']:
    summary_df.to_csv(os.path.join(out_dir, 'preprocessing_summary.csv'), index=False, encoding='utf-8')

print("\nPhase 1 Data Preprocessing completed successfully!")
