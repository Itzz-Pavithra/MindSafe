import os
import glob
import pandas as pd
import numpy as np

raw_path = 'Data/raw/Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv'
df = pd.read_csv(raw_path, encoding='cp1252')

print(f"Dataset shape: {df.shape}")
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")

# Duplicate check
exact_dupes = df.duplicated().sum()
dupes_no_time = df.duplicated(subset=[c for c in df.columns if c != 'Timestamp']).sum()
print(f"Exact duplicate rows (all columns including Timestamp): {exact_dupes}")
print(f"Duplicate rows (excluding Timestamp): {dupes_no_time}")

# Missing value summary
print("\n--- MISSING VALUE ANALYSIS ---")
missing_df = pd.DataFrame({
    'Column': df.columns,
    'Total': len(df),
    'Missing': df.isnull().sum().values,
    'Missing_Pct': ((df.isnull().sum() / len(df)) * 100).round(2).values,
    'Dtype': [str(t) for t in df.dtypes.values]
})
print(missing_df.to_string())

# Detailed Column Inspection
print("\n--- COLUMN VALUES BREAKDOWN ---")
for idx, col in enumerate(df.columns, 1):
    vals = df[col].value_counts(dropna=False)
    print(f"\n[Col {idx}]: {repr(col)}")
    print(f"Missing count: {df[col].isnull().sum()} ({(df[col].isnull().sum()/len(df))*100:.2f}%)")
    print(f"Unique count: {len(vals)}")
    print("Top unique values:")
    for v, c in vals.head(10).items():
        print(f"   {repr(v)}: {c}")
