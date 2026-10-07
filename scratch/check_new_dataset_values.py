import os
import io
import pandas as pd
import numpy as np

raw_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(raw_path, 'rb') as f:
    raw_bytes = f.read()
clean_utf8_bytes = raw_bytes.replace(b'\x96', b'\xe2\x80\x93')

df = pd.read_csv(io.BytesIO(clean_utf8_bytes), encoding='utf-8', keep_default_na=False)

# Normalize column names
clean_cols = [' '.join(c.split()) for c in df.columns]
df.columns = clean_cols

# Clean string values
for c in df.columns:
    df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]

# Filter valid target
valid_df = df[df[target_col] != ''].copy().reset_index(drop=True)
print(f"Total rows: {len(df)}")
print(f"Valid target rows: {len(valid_df)}")

print("\n--- COLUMN VALUE DISTRIBUTIONS (Valid Target Rows) ---")
for i, col in enumerate(valid_df.columns):
    print(f"\nCol {i}: {col}")
    vals = valid_df[col].replace({'': np.nan}).dropna()
    print(f"  Non-null count: {len(vals)} / {len(valid_df)} ({len(vals)/len(valid_df)*100:.1f}%)")
    unique_vals = vals.unique()
    print(f"  Unique count: {len(unique_vals)}")
    if len(unique_vals) <= 15:
        vc = vals.value_counts()
        for k, v in vc.items():
            print(f"    {repr(k)}: {v}")
    else:
        # Multi-select or high cardinality
        tokens = set()
        for v in vals:
            for t in str(v).split(','):
                tokens.add(t.strip())
        print(f"  Parsed {len(tokens)} unique comma-separated tokens:")
        for t in sorted(tokens):
            print(f"    - {repr(t)}")
