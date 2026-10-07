import subprocess
import io
import pandas as pd

p = subprocess.run(
    ['git', 'show', 'HEAD:Data/raw/Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv'],
    capture_output=True
)
raw_bytes = p.stdout
print("HEAD raw bytes:", len(raw_bytes))

clean_bytes = raw_bytes.replace(b'\x96', '\u2013'.encode('utf-8'))
clean_bytes = clean_bytes.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', '\u2013'.encode('utf-8'))
text = clean_bytes.decode('utf-8', errors='replace')
text = text.replace('â€“', '–')

df = pd.read_csv(io.StringIO(text), keep_default_na=False)
print(f"HEAD row count: {len(df)}")
