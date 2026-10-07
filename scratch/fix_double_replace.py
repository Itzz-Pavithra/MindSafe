import os
import json

for nb_name in ['01_data_preprocessing.ipynb', '02_statistical_analysis.ipynb', '03_ml_training_evaluation.ipynb']:
    nb_path = os.path.join('notebook', nb_name)
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb['cells']:
        src = ''.join(cell.get('source', []))
        if '11514' in src or '11519' in src:
            src = src.replace('11514', '1514').replace('11519', '1519')
            cell['source'] = src.splitlines(keepends=True)
            modified = True
            
    if modified:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=2)
        print(f"Fixed {nb_name} successfully.")
    else:
        print(f"No double-replacements in {nb_name}.")
