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

# Now test preprocessor logic with str(x).strip() not in {'', 'nan'}
nominal_keys = {
    'gender': [c for c in valid_df.columns if '2. What is your gender?' in c][0],
    'q7_post': [c for c in valid_df.columns if c.startswith('7.')][0],
    'q10_plat': [c for c in valid_df.columns if c.startswith('10.')][0],
    'q17_area': [c for c in valid_df.columns if c.startswith('17.')][0]
}

nominal_categories = {}
for k, col_str in nominal_keys.items():
    cats = sorted([str(x) for x in valid_df[col_str].dropna().unique() if str(x).strip() not in {'', 'nan'}])
    nominal_categories[k] = cats
    print(f"{k} ({len(cats)} categories): {cats}")

multiselect_keys = {
    'platforms': [c for c in valid_df.columns if '3. Which social media' in c][0],
    'q9_types': [c for c in valid_df.columns if c.startswith('9.')][0],
    'q15_help': [c for c in valid_df.columns if c.startswith('15.')][0],
    'q18_act': [c for c in valid_df.columns if c.startswith('18.')][0]
}

multiselect_tokens = {}
for k, col_str in multiselect_keys.items():
    tokens = set()
    for val in valid_df[col_str].dropna():
        for t in str(val).split(','):
            ct = t.strip()
            if ct and ct.lower() not in {'', 'nan', 'null'}:
                tokens.add(ct)
    multiselect_tokens[k] = sorted(list(tokens))
    print(f"{k} ({len(tokens)} tokens): {multiselect_tokens[k]}")

total_b = 5 + sum(len(c) for c in nominal_categories.values()) + sum(len(t) for t in multiselect_tokens.values())
print(f"\nScenario B Total features: {total_b}")
assert total_b == 54, f"Expected 54, got {total_b}"

# Test Scenario A
q13_sym = [c for c in valid_df.columns if c.startswith('13.')][0]
tokens_13 = set()
for val in valid_df[q13_sym].dropna():
    for t in str(val).split(','):
        ct = t.strip()
        if ct and ct.lower() not in {'', 'nan', 'null'}:
            tokens_13.add(ct)
print(f"q13_sym ({len(tokens_13)} tokens): {sorted(list(tokens_13))}")
total_a = total_b + len(tokens_13) + 1
print(f"Scenario A Total features: {total_a}")
assert total_a == 61, f"Expected 61, got {total_a}"
print("VERIFICATION SUCCEEDED: Exactly 54 features for Scenario B and 61 for Scenario A!")
