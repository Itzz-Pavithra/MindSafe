import json

with open('notebook/01_data_preprocessing.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx in [4, 12, 20, 24]:
    print(f"=== CELL {idx} ===")
    src = ''.join(nb['cells'][idx]['source'])
    print(repr(src))
