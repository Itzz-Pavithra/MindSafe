import os
import io
import glob
import pandas as pd
import numpy as np

# 1. Locate raw CSV
raw_dir = os.path.join('Data', 'raw')
csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))
if not csv_files:
    raise FileNotFoundError("No CSV file found in Data/raw/")
raw_path = csv_files[0]
print(f"Located raw survey CSV: {raw_path}")

# 2. Read raw bytes and normalize mixed encoding
with open(raw_path, 'rb') as f:
    raw_bytes = f.read()

# Replace Windows-1252 byte 0x96 with UTF-8 bytes 0xE2 0x80 0x93
# This resolves mixed CP1252/UTF-8 en-dashes into 100% valid UTF-8
clean_utf8_bytes = raw_bytes.replace(b'\x96', b'\xe2\x80\x93')

# Parse with keep_default_na=False to prevent "None" in Col 13 from becoming NaN
df = pd.read_csv(io.BytesIO(clean_utf8_bytes), encoding='utf-8', keep_default_na=False)
print(f"Initial raw parsed shape: {df.shape}")

# 3. Clean column names (strip unnecessary leading/trailing whitespace, normalize internal newlines to spaces)
raw_col_names = list(df.columns)
clean_col_names = [' '.join(col.split()) for col in raw_col_names]
df.columns = clean_col_names

# 4. Standardize whitespace in all cell values
for col in df.columns:
    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

# 5. Standardize missing values: empty strings and null tokens to pd.NA,
# BUT explicitly preserve "None" in Column 13 ("Which of the following did you experience?")
col13_name = clean_col_names[13]

null_tokens = {'', 'na', 'n/a', 'null', 'nan', 'nil'}

for col in df.columns:
    if col == col13_name:
        # In Col 13, "None" is a valid option meaning "No negative emotional symptoms"
        # Only empty string is missing
        df[col] = df[col].apply(lambda x: np.nan if isinstance(x, str) and x.lower() in {'', 'na', 'n/a', 'null', 'nan'} else x)
    else:
        df[col] = df[col].apply(lambda x: np.nan if isinstance(x, str) and x.lower() in null_tokens else x)

# 6. Duplicate row analysis
exact_dupes = df.duplicated().sum()
print(f"Exact duplicate rows: {exact_dupes}")

# 7. Create short/standardized variable names dictionary for research reference
short_names = [
    "Timestamp",
    "Age",
    "Gender",
    "Platforms_Used",
    "Daily_Usage_Hours",
    "Experienced_Cyberbullying",
    "Witnessed_Cyberbullying",
    "Posted_Offensive_Content",
    "Offensive_Action_Reason",
    "Cyberbullying_Types_Observed",
    "Incident_Platform",
    "Cyberbullying_Frequency",
    "Mental_Health_Impact",
    "Negative_Emotional_Symptoms",
    "Emotional_Impact_Severity",
    "Sought_Help",
    "Reason_Not_Reported",
    "Harassment_Context_Area",
    "Action_Taken"
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

potential_roles = [
    "Metadata / Identifier",
    "Feature (Demographic)",
    "Feature (Demographic)",
    "Feature (Platform Exposure)",
    "Feature (Usage Intensity)",
    "Feature (Victimization)",
    "Feature (Bystander Exposure)",
    "Feature (Online Behavior)",
    "Feature (Conditional Perpetration Reason)",
    "Feature (Bullying Modality)",
    "Feature (Platform Context)",
    "Feature (Chronicity / Frequency)",
    "Target",
    "Feature (Symptom Manifestation)",
    "Feature (Emotional Impact Severity)",
    "Feature (Help Seeking / Coping)",
    "Feature (Reporting Barrier / Legal Awareness)",
    "Feature (Contextual Environment)",
    "Feature (Coping Response Action)"
]

# 8. Save Data/processed/cleaned_survey_data.csv
os.makedirs(os.path.join('Data', 'processed'), exist_ok=True)
cleaned_csv_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
df.to_csv(cleaned_csv_path, index=False, encoding='utf-8')
print(f"Successfully saved cleaned dataset to: {cleaned_csv_path}")

# 9. Generate data_quality_report.csv
report_rows = []
for i in range(len(df.columns)):
    col = df.columns[i]
    total_val = len(df)
    missing_val = df[col].isna().sum()
    valid_val = total_val - missing_val
    missing_pct = round((missing_val / total_val) * 100, 2)
    unique_cnt = df[col].nunique(dropna=True)
    sample_cats = " | ".join([str(v) for v in df[col].dropna().unique()[:4]])
    
    report_rows.append({
        'Column_Index': i,
        'Short_Name': short_names[i],
        'Clean_Column_Name': col,
        'Raw_Column_Name': raw_col_names[i],
        'Data_Type': str(df[col].dtype),
        'Question_Type': question_types[i],
        'Potential_Role': potential_roles[i],
        'Total_Responses': total_val,
        'Valid_Responses': valid_val,
        'Missing_Count': missing_val,
        'Missing_Percentage': missing_pct,
        'Unique_Categories_Count': unique_cnt,
        'Sample_Categories': sample_cats
    })

report_df = pd.DataFrame(report_rows)
report_csv_path = os.path.join('Data', 'processed', 'data_quality_report.csv')
report_df.to_csv(report_csv_path, index=False, encoding='utf-8')
print(f"Successfully saved data quality report to: {report_csv_path}")

# 10. Verify outputs
print("\n--- PIPELINE EXECUTION VERIFICATION ---")
print(f"Cleaned CSV exists: {os.path.exists(cleaned_csv_path)}")
print(f"Report CSV exists: {os.path.exists(report_csv_path)}")
df_clean_check = pd.read_csv(cleaned_csv_path, encoding='utf-8')
print(f"Cleaned DataFrame Shape: {df_clean_check.shape}")
print(f"Exact row count: {len(df_clean_check)}")
print(f"Exact column count: {len(df_clean_check.columns)}")
print(f"Q13 'None' count preserved: {(df_clean_check.iloc[:, 13] == 'None').sum()}")
target_clean = df_clean_check.iloc[:, 12]
print(f"Target variable name: {df_clean_check.columns[12]}")
print(f"Target valid count: {target_clean.notna().sum()}, missing count: {target_clean.isna().sum()}")
print("Target distribution:")
print(target_clean.value_counts(dropna=False))
