import os

csv_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()

print("Count of \\x96:", raw_bytes.count(b'\x96'))
print("Count of UTF8 en dash:", raw_bytes.count('\u2013'.encode('utf-8')))
print("Count of double-encoded en dash:", raw_bytes.count(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c'))
