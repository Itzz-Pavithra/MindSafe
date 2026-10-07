import json

with open('notebook/01_data_preprocessing.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

src4 = ''.join(nb['cells'][4]['source'])
for line in src4.splitlines():
    if 'assert' in line or 'len(' in line or '1319' in line:
        print(line)
