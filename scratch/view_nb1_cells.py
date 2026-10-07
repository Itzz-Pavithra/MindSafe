import json

with open('notebook/01_data_preprocessing.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx in [2, 3, 4, 12, 13, 20, 21, 23, 24]:
    if idx < len(nb['cells']):
        print(f"--- Cell {idx} ({nb['cells'][idx]['cell_type']}) ---")
        print(''.join(nb['cells'][idx]['source']))
