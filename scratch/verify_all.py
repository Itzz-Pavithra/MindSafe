import os
import hashlib
import json
import pandas as pd

raw_path = os.path.join('Data', 'raw', 'Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv')
cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
report_path = os.path.join('Data', 'processed', 'data_quality_report.csv')
nb_path = os.path.join('notebook', '01_data_preprocessing.ipynb')

# 1. Raw checksum
with open(raw_path, 'rb') as f:
    h = hashlib.sha256(f.read()).hexdigest()
print(f"1. Raw CSV SHA256: {h}")
assert h == '090fa5883977de148bc01489b999f88ee02af7ed4132f7c53f785c61b25b46bf', 'Raw CSV hash mismatch!'
print("   VERIFIED: Raw CSV is 100% UNMODIFIED.")

# 2. Cleaned CSV
df_clean = pd.read_csv(cleaned_path, encoding='utf-8', keep_default_na=False)
print(f"2. Cleaned CSV Shape: {df_clean.shape} (Rows: {len(df_clean)}, Cols: {len(df_clean.columns)})")
assert df_clean.shape == (521, 19), f"Unexpected shape {df_clean.shape}"
none_cnt = (df_clean.iloc[:, 13] == 'None').sum()
print(f"   Q13 'None' responses preserved: {none_cnt}")
assert none_cnt == 222, f"Expected 222 None responses, got {none_cnt}"

# 3. Quality report CSV
df_rep = pd.read_csv(report_path)
print(f"3. Data Quality Report Shape: {df_rep.shape}")
assert len(df_rep) == 19, f"Expected 19 report rows, got {len(df_rep)}"

# 4. Notebook check
with open(nb_path, 'r', encoding='utf-8') as f:
    nb_json = json.load(f)
cells = nb_json['cells']
code_cells = [c for c in cells if c['cell_type'] == 'code']
executed_code_cells = [c for c in code_cells if c.get('outputs') and len(c['outputs']) > 0]
print(f"4. Notebook Total Cells: {len(cells)}, Code Cells: {len(code_cells)}, Executed with Outputs: {len(executed_code_cells)}")
assert len(executed_code_cells) == len(code_cells), "Not all code cells have outputs!"

print("\n>>> ALL VERIFICATION CHECKS PASSED 100% PERFECTLY! <<<")
