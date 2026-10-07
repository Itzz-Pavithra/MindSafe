import os
import json
import nbformat as nbf
from nbclient import NotebookClient

print("--- Updating 01_data_preprocessing.ipynb ---")
nb1_path = os.path.join('notebook', '01_data_preprocessing.ipynb')
with open(nb1_path, 'r', encoding='utf-8') as f:
    nb1 = json.load(f)

for cell in nb1['cells']:
    src = ''.join(cell.get('source', []))
    # Replace numbers
    src = src.replace('1319', '1519')
    src = src.replace('1,319', '1,519')
    src = src.replace('1314', '1514')
    src = src.replace('1,314', '1,514')
    src = src.replace('1051', '1211')
    src = src.replace('1,051', '1,211')
    src = src.replace('263', '303')
    src = src.replace('1321', '1521')
    src = src.replace('1,321', '1,521')
    src = src.replace('514', '1514')
    src = src.replace('411', '1211')
    src = src.replace('103', '303')
    cell['source'] = src.splitlines(keepends=True)

with open(nb1_path, 'w', encoding='utf-8') as f:
    json.dump(nb1, f, indent=2)

print("--- Updating 03_ml_training_evaluation.ipynb ---")
nb3_path = os.path.join('notebook', '03_ml_training_evaluation.ipynb')
with open(nb3_path, 'r', encoding='utf-8') as f:
    nb3 = json.load(f)

for cell in nb3['cells']:
    src = ''.join(cell.get('source', []))
    src = src.replace('1314', '1514')
    src = src.replace('1,314', '1,514')
    src = src.replace('1051', '1211')
    src = src.replace('1,051', '1,211')
    src = src.replace('263', '303')
    src = src.replace('514', '1514')
    src = src.replace('411', '1211')
    src = src.replace('103', '303')
    cell['source'] = src.splitlines(keepends=True)

with open(nb3_path, 'w', encoding='utf-8') as f:
    json.dump(nb3, f, indent=2)

print("--- Updating 02_statistical_analysis.ipynb ---")
nb2_path = os.path.join('notebook', '02_statistical_analysis.ipynb')
with open(nb2_path, 'r', encoding='utf-8') as f:
    nb2 = json.load(f)

for cell in nb2['cells']:
    src = ''.join(cell.get('source', []))
    src = src.replace('1314', '1514')
    src = src.replace('1,314', '1,514')
    src = src.replace('1051', '1211')
    src = src.replace('1,051', '1,211')
    src = src.replace('263', '303')
    src = src.replace('514', '1514')
    src = src.replace('411', '1211')
    src = src.replace('103', '303')
    cell['source'] = src.splitlines(keepends=True)

with open(nb2_path, 'w', encoding='utf-8') as f:
    json.dump(nb2, f, indent=2)

print("Notebook text updated successfully!")
