import os
import io
import pandas as pd

raw_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(raw_path, 'rb') as f:
    raw = f.read()

# Replace mojibake and legacy byte sequences
clean_bytes = raw.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))

text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)

col_usage = [c for c in df.columns if '4.' in c][0]
col_age = [c for c in df.columns if '1.' in c][0]
print("Usage unique:", df[col_usage].unique())
print("Age unique:", df[col_age].unique())
