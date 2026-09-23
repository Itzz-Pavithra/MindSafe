import os
import glob
import pandas as pd
import numpy as np

# Locate CSV in Data/raw
raw_dir = os.path.join(os.getcwd(), 'Data', 'raw')
csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))
print(f"Found CSV files: {csv_files}")

if not csv_files:
    print("No CSV found in Data/raw")
    exit(1)

csv_path = csv_files[0]
print(f"Loading: {csv_path}\n")

# Try UTF-8 first
encoding_used = 'utf-8'
try:
    df = pd.read_csv(csv_path, encoding='utf-8')
    print("Loaded with utf-8 encoding successfully.")
except Exception as e:
    print(f"UTF-8 failed: {e}. Trying utf-8-sig / latin1 / cp1252...")
    for enc in ['utf-8-sig', 'cp1252', 'latin1', 'iso-8859-1']:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            encoding_used = enc
            print(f"Successfully loaded with {enc}")
            break
        except Exception as e2:
            pass

print(f"\n==================================================")
print(f"1. DATASET SHAPE")
print(f"==================================================")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

print(f"\n==================================================")
print(f"2. ACTUAL COLUMN NAMES")
print(f"==================================================")
for idx, col in enumerate(df.columns, 1):
    print(f"[{idx}] {repr(col)}")

print(f"\n==================================================")
print(f"3. FIRST 3 ROWS")
print(f"==================================================")
print(df.head(3).to_string())

print(f"\n==================================================")
print(f"4. COLUMN DATA TYPES")
print(f"==================================================")
for col, dtype in df.dtypes.items():
    print(f"{col}: {dtype}")

print(f"\n==================================================")
print(f"5 & 6. MISSING VALUES PER COLUMN")
print(f"==================================================")
missing_counts = df.isnull().sum()
missing_pcts = (df.isnull().sum() / len(df)) * 100
for col in df.columns:
    count = missing_counts[col]
    pct = missing_pcts[col]
    print(f"{col} -> Count: {count} ({pct:.2f}%)")

print(f"\n==================================================")
print(f"7. DUPLICATE ROWS")
print(f"==================================================")
num_duplicates = df.duplicated().sum()
print(f"Exact duplicate rows: {num_duplicates}")

print(f"\n==================================================")
print(f"8. UNIQUE VALUES AND VALUE COUNTS FOR ALL COLUMNS")
print(f"==================================================")
for idx, col in enumerate(df.columns, 1):
    print(f"\n--- Column [{idx}]: {col} ---")
    val_counts = df[col].value_counts(dropna=False)
    print(f"Number of unique values (including NaN): {len(val_counts)}")
    for val, cnt in val_counts.items():
        print(f"  {repr(val)}: {cnt}")
