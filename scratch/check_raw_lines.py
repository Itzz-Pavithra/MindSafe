import os

raw_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(raw_path, 'r', encoding='utf-8-sig', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines in Data/raw CSV: {len(lines)}")
print("Line count:", len(lines))
print("Last line:", repr(lines[-1][:60]))
