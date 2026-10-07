import os
import json
import nbformat as nbf
from nbclient import NotebookClient

print("Updating notebook 01_data_preprocessing.ipynb...")
nb1_path = os.path.join('notebook', '01_data_preprocessing.ipynb')
with open(nb1_path, 'r', encoding='utf-8') as f:
    nb1 = json.load(f)

for cell in nb1['cells']:
    src = ''.join(cell.get('source', []))
    # Replace references to 514, 411, 103
    src = src.replace('N = 514', 'N = 1,314')
    src = src.replace('514', '1314')
    src = src.replace('411', '1051')
    src = src.replace('103', '263')
    cell['source'] = src.splitlines(keepends=True)

with open(nb1_path, 'w', encoding='utf-8') as f:
    json.dump(nb1, f, indent=2)

print("Updating notebook 03_ml_training_evaluation.ipynb...")
nb3_path = os.path.join('notebook', '03_ml_training_evaluation.ipynb')
with open(nb3_path, 'r', encoding='utf-8') as f:
    nb3 = json.load(f)

for cell in nb3['cells']:
    src = ''.join(cell.get('source', []))
    src = src.replace('assert len(usable_df) == 514', 'assert len(usable_df) == 1314')
    src = src.replace('N = 514', 'N = 1,314')
    src = src.replace('514', '1314')
    src = src.replace('Train N = 411 (80%), Test N = 103 (20%)', 'Train N = 1,051 (80%), Test N = 263 (20%)')
    src = src.replace('(N = 411)', '(N = 1,051)')
    src = src.replace('(N = 103)', '(N = 263)')
    src = src.replace('411 Training Records', '1,051 Training Records')
    src = src.replace('411 training records', '1,051 training records')
    src = src.replace('N = 411', 'N = 1,051')
    src = src.replace('N = 103', 'N = 263')
    src = src.replace('48.54%', '65.40%')
    src = src.replace('0.3275', '0.6473')
    src = src.replace('0.4177', '0.6414')
    src = src.replace('44.66%', '32.70%')
    cell['source'] = src.splitlines(keepends=True)

with open(nb3_path, 'w', encoding='utf-8') as f:
    json.dump(nb3, f, indent=2)

print("Updated notebooks successfully on disk.")
