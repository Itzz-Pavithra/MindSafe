import os
import io
import pandas as pd

f1321_path = r"C:\Users\pavit\Downloads\cyberbullying_mental_health_1321_rows.csv"
f1521_path = r"C:\Users\pavit\OneDrive\Desktop\Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv"

with open(f1321_path, 'rb') as f:
    b1321 = f.read().replace(b'\x96', '\u2013'.encode('utf-8'))
df1321 = pd.read_csv(io.StringIO(b1321.decode('utf-8', errors='replace')), keep_default_na=False)

with open(f1521_path, 'rb') as f:
    b1521 = f.read().replace(b'\x96', '\u2013'.encode('utf-8'))
df1521 = pd.read_csv(io.StringIO(b1521.decode('utf-8', errors='replace')), keep_default_na=False)

print(f"File 1 (Downloads): {len(df1321)} rows")
print(f"File 2 (Desktop): {len(df1521)} rows")
print(f"Difference in rows: {len(df1521) - len(df1321)} rows")

# Check if df1321 is an exact subset of df1521:
ts1321 = set(df1321['Timestamp'])
ts1521 = set(df1521['Timestamp'])
overlap = ts1321.intersection(ts1521)
print(f"Timestamp overlap: {len(overlap)} / {len(ts1321)}")
print(f"Timestamps unique to df1521: {len(ts1521 - ts1321)}")

# Check timestamps in df1521 that are not in df1321:
diff_df = df1521[~df1521['Timestamp'].isin(ts1321)]
print(f"Non-overlapping rows in 1521 file: {len(diff_df)}")
if len(diff_df) > 0:
    print("Sample extra timestamps in 1521 file:")
    print(diff_df['Timestamp'].head(5).tolist())
