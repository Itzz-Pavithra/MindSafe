import os

csv_path = os.path.join("Data", "raw", "Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv")

with open(csv_path, 'rb') as f:
    raw_bytes = f.read()

# find byte sequences around "18"
pos = 0
found = []
while True:
    pos = raw_bytes.find(b'18', pos)
    if pos == -1 or len(found) >= 10:
        break
    snippet = raw_bytes[pos:pos+10]
    found.append(snippet)
    pos += 2

print("Sample 18... snippets in raw bytes:")
for s in found:
    print(repr(s))
