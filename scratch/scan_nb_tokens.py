import json
import os

for nb_name in ['01_data_preprocessing.ipynb', '02_statistical_analysis.ipynb', '03_ml_training_evaluation.ipynb']:
    nb_path = os.path.join('notebook', nb_name)
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print(f"\n=== {nb_name} ===")
    for idx, cell in enumerate(nb['cells']):
        src = ''.join(cell.get('source', []))
        for token in ['assert', '514', '1314', '1,314', '1051', '263', '411', '103', '48.54']:
            if token in src:
                print(f"Cell {idx} ({cell['cell_type']}) has token '{token}':")
                for line in src.splitlines():
                    if token in line:
                        print(f"   {line[:100]}")
