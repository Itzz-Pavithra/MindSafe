import os
import io
import pandas as pd
import numpy as np

csv_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()

clean_bytes = raw_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)
clean_col_names = [' '.join(col.split()) for col in df.columns]
df.columns = clean_col_names

for c in df.columns:
    df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

col_target = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_df = df[df[col_target] != ''].copy().reset_index(drop=True)

import sys
sys.path.insert(0, '.')
from models.preprocessor import SurveyFeaturePreprocessor

prep = SurveyFeaturePreprocessor(scenario='B')
prep.fit(valid_df)
X = prep.transform(valid_df)

print(f"Total features extracted: {len(prep.feature_names_)}")
print("Feature names:")
for i, fn in enumerate(prep.feature_names_):
    print(f"  {i+1:2d}. {fn}")

print("\n--- Check Scenario A (Benchmark) ---")
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(valid_df)
X_a = prep_a.transform(valid_df)
print(f"Scenario A total features: {len(prep_a.feature_names_)}")
