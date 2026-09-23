import sys
import io
import os
import glob
import pandas as pd
import numpy as np

# Reconfigure stdout for utf-8
sys.stdout.reconfigure(encoding='utf-8')

raw_dir = os.path.join(os.getcwd(), 'Data', 'raw')
csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))
print(f"Found CSV files: {csv_files}")
csv_path = csv_files[0]

# Check Approach A vs Approach B
df_cp1252 = pd.read_csv(csv_path, encoding='cp1252')
df_a = df_cp1252.map(lambda x: x.replace('â€“', '–') if isinstance(x, str) else x)

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()
clean_bytes = raw_bytes.replace(b'\x96', b'\xe2\x80\x93')
df_b = pd.read_csv(io.BytesIO(clean_bytes), encoding='utf-8')

print("Approach A shape:", df_a.shape)
print("Approach B shape:", df_b.shape)
print("Approach A and B identical:", df_a.equals(df_b))

# Let's inspect df_b in detail
df = df_b
print(f"\nTotal rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\n--- ALL COLUMNS ---")
for idx, col in enumerate(df.columns):
    print(f"[{idx}] {repr(col)}")

print("\n--- EXACT DUPLICATES ---")
dupes = df.duplicated()
print(f"Number of exact duplicate rows: {dupes.sum()}")
if dupes.sum() > 0:
    print("Duplicate indices:", df[dupes].index.tolist())
    print("\nDuplicate rows content:")
    print(df[dupes].to_string())

print("\n--- DUPLICATES EXCLUDING TIMESTAMP ---")
non_time_cols = [c for c in df.columns if 'Timestamp' not in c]
dupes_no_time = df.duplicated(subset=non_time_cols)
print(f"Duplicates excluding Timestamp: {dupes_no_time.sum()}")

print("\n--- MISSING VALUES ---")
missing_df = pd.DataFrame({
    'Column': df.columns,
    'Total': len(df),
    'Missing': df.isnull().sum().values,
    'Missing_Pct': ((df.isnull().sum() / len(df)) * 100).round(2).values,
    'Dtype': [str(t) for t in df.dtypes.values],
    'Unique_Count': [df[c].nunique(dropna=True) for c in df.columns]
})
print(missing_df.to_string())

print("\n--- VALUE COUNTS FOR ALL COLUMNS ---")
for idx, col in enumerate(df.columns):
    print(f"\n==============================")
    print(f"Col [{idx}]: {col}")
    print(f"==============================")
    vc = df[col].value_counts(dropna=False)
    for k, v in vc.items():
        print(f"  {repr(k)}: {v}")
