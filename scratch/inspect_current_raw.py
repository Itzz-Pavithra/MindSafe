import os
import io
import pandas as pd
import numpy as np

csv_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()

print(f"File size: {len(raw_bytes)} bytes")

# Test encoding
clean_bytes = raw_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)

print(f"Shape: {df.shape}")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")

print("\n--- COLUMNS ---")
for i, col in enumerate(df.columns):
    cleaned_col = ' '.join(col.split())
    print(f"{i}: {cleaned_col}")

# Check exact duplicate rows across all columns
exact_dupes = df.duplicated().sum()
print(f"\nExact duplicate rows: {exact_dupes}")

# Check blank rows
survey_cols = df.columns[1:]
blank_mask = df[survey_cols].apply(lambda col: col.str.strip() == '').all(axis=1)
print(f"Completely blank rows (survey questions empty): {blank_mask.sum()}")
if blank_mask.sum() > 0:
    print(f"Blank row indices: {df[blank_mask].index.tolist()}")

# Check target column
col_target = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
target_series = df[col_target].apply(lambda x: x.strip())
print(f"\nTarget column: {col_target}")
print("Target value counts (including empty):")
print(target_series.value_counts(dropna=False))

# Unique values per column
print("\n--- UNIQUE VALUES / EXAMPLES PER COLUMN ---")
for i, col in enumerate(df.columns):
    cleaned_col = ' '.join(col.split())
    non_empty = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    non_empty = non_empty[non_empty != '']
    print(f"\n[{i}] {cleaned_col}:")
    print(f"  Valid non-empty: {len(non_empty)} / {len(df)} (Missing: {len(df) - len(non_empty)})")
    print(f"  Unique count: {non_empty.nunique()}")
    print(f"  Sample values: {list(non_empty.unique()[:6])}")
