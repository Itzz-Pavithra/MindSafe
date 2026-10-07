import os
import io
import pandas as pd

desktop_csv = r"C:\Users\pavit\OneDrive\Desktop\Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv"

with open(desktop_csv, 'rb') as f:
    raw_bytes = f.read()

print(f"Desktop CSV Size: {len(raw_bytes)} bytes")

clean_bytes = raw_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

col_target = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
target_series = df[col_target].apply(lambda x: x.strip())
print("\nTarget value counts:")
print(target_series.value_counts(dropna=False))
