import os
import io
import pandas as pd
import numpy as np

csv_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()

clean_bytes = raw_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)

print(f"1. Total raw rows: {len(df)}")
print(f"2. Total columns: {len(df.columns)}")

clean_col_names = [' '.join(col.split()) for col in df.columns]
df.columns = clean_col_names

# Clean strings
for c in df.columns:
    df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Check exact duplicate rows
exact_dupes = df.duplicated().sum()
print(f"3. Exact duplicate rows: {exact_dupes}")

# Check blank rows across all survey questions (cols 1..18)
survey_cols = df.columns[1:]
blank_mask = (df[survey_cols] == '').all(axis=1)
blank_indices = df[blank_mask].index.tolist()
print(f"4. Completely blank submissions (all 18 survey questions empty): {len(blank_indices)} (Indices: {blank_indices})")

# Check target column
col_target = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
missing_target_mask = (df[col_target] == '')
missing_target_indices = df[missing_target_mask].index.tolist()
print(f"5. Records with missing target variable: {len(missing_target_indices)} (Indices: {missing_target_indices})")

# Check if any other records have missing survey questions
for idx in missing_target_indices:
    non_blank_cnt = (df.loc[idx] != '').sum()
    print(f"   Row {idx}: {non_blank_cnt}/19 fields populated. Timestamp={df.loc[idx, 'Timestamp']}")

# Check valid records after dropping missing target
valid_df = df[~missing_target_mask].copy().reset_index(drop=True)
print(f"\n6. Final analytical dataset size: {len(valid_df)} valid responses")

# Target class distribution
target_counts = valid_df[col_target].value_counts()
target_pcts = (target_counts / len(valid_df) * 100).round(2)
print("\n7. Target class distribution:")
for c in ['Not at all', 'Slightly', 'Moderately', 'Severely']:
    cnt = target_counts.get(c, 0)
    pct = target_pcts.get(c, 0.0)
    print(f"   {c:12s}: {cnt:4d} ({pct:6.2f}%)")

# Date range / Timestamp analysis
ts_series = pd.to_datetime(valid_df['Timestamp'], errors='coerce', format='mixed')
print(f"\n8. Timestamp range: {ts_series.min()} to {ts_series.max()} (Parsed: {ts_series.notna().sum()}/{len(valid_df)})")

# Check categorical unique values across all columns
print("\n9. Unique values per column:")
for i, col in enumerate(valid_df.columns):
    uniq = valid_df[col][valid_df[col] != ''].unique()
    print(f"   Col {i:2d} [{col[:40]}...]: {len(uniq)} unique values")
    if len(uniq) <= 10:
        print(f"        Values: {list(uniq)}")
