import glob
import json

for nb_path in glob.glob('notebook/*.ipynb'):
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print(nb_path, len(nb['cells']))
    for i, c in enumerate(nb['cells']):
        src = "".join(c.get('source', []))
        if 'benchmark' in src.lower() or 'model_comparison' in src.lower():
            fl = src.strip().split('\n')[0]
            print(f"  Cell {i}: {fl[:80]}")
