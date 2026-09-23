import os
import nbformat as nbf
from nbclient import NotebookClient

notebook_path = os.path.join('notebook', '02_statistical_analysis.ipynb')
print(f"Reading {notebook_path}...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

print("Executing Phase 2 notebook with NotebookClient...")
client = NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebook'}})
client.execute()

print("Writing executed notebook back to disk...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Phase 2 Notebook execution completed successfully with all outputs populated!")
