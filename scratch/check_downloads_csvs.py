import os
import io
import pandas as pd

for fn in ['cyberbullying_mental_health_1321_rows.csv', 'mental_health_cyberbullying_1321_rows.csv']:
    path = os.path.join(r"C:\Users\pavit\Downloads", fn)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            b = f.read()
        print(f"\n--- {fn} ---")
        print(f"Size: {len(b)} bytes")
        clean = b.replace(b'\x96', '\u2013'.encode('utf-8'))
        text = clean.decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(text), keep_default_na=False)
        print(f"Rows: {len(df)}, Cols: {len(df.columns)}")
        target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
        valid = df[df[target_col].str.strip() != '']
        print(f"Valid target rows: {len(valid)}")
