import os
import shutil
import io
import pandas as pd
import numpy as np

src_csv = r"C:\Users\pavit\OneDrive\Desktop\Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv"
dest_csv = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

if os.path.exists(src_csv):
    print(f"Copying {src_csv} to {dest_csv}...")
    shutil.copy2(src_csv, dest_csv)
    print("Copy completed successfully.")
else:
    print(f"Source file not found at {src_csv}, checking existing {dest_csv}...")

# Read bytes and handle encoding
with open(dest_csv, 'rb') as f:
    raw_bytes = f.read()

print(f"Total raw bytes: {len(raw_bytes)}")
clean_utf8_bytes = raw_bytes.replace(b'\x96', b'\xe2\x80\x93')

df = pd.read_csv(io.BytesIO(clean_utf8_bytes), encoding='utf-8', keep_default_na=False)
print(f"Raw parsed DataFrame shape: {df.shape}")
print(f"Total rows in raw CSV: {len(df)}")
print(f"Total columns in raw CSV: {len(df.columns)}")

print("\n--- COLUMN NAMES ---")
for i, col in enumerate(df.columns):
    print(f"Col {i:2d}: {repr(col)}")

# Check duplicate rows
exact_dupes = df.duplicated().sum()
print(f"\nExact duplicate rows: {exact_dupes}")

# Check blank rows (where all survey questions after timestamp are empty)
survey_cols = df.columns[1:]
is_blank_survey = (df[survey_cols].apply(lambda s: s.str.strip().eq('')).all(axis=1))
print(f"Completely blank survey submissions (after timestamp): {is_blank_survey.sum()}")
if is_blank_survey.sum() > 0:
    print(f"Blank submission row indices: {df[is_blank_survey].index.tolist()}")

# Check timestamp range
ts_col = df.columns[0]
valid_ts = df[ts_col][df[ts_col].str.strip() != '']
print(f"\nTimestamp valid entries: {len(valid_ts)}")
print(f"First 3 timestamps: {valid_ts.iloc[:3].tolist()}")
print(f"Last 3 timestamps: {valid_ts.iloc[-3:].tolist()}")

# Identify target column
target_candidates = [c for c in df.columns if '12.' in c or 'mental health' in c.lower()]
print(f"\nTarget column candidates: {target_candidates}")
if target_candidates:
    t_col = target_candidates[0]
    raw_target_vals = df[t_col].str.strip()
    print(f"Raw target value counts (including empty):")
    print(raw_target_vals.value_counts(dropna=False))
