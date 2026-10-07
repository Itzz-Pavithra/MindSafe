import os
import re

EXCLUDE_DIRS = {'.git', 'node_modules', '.svelte-kit', 'scratch', '__pycache__'}
PATTERNS = [
    r'\b514\b',
    r'\b411\b',
    r'\b103\b',
    r'48\.54',
    r'0\.3275',
    r'0\.4177',
    r'44\.66',
    r'\b1314\b',
    r'1,314',
    r'\b1051\b',
    r'1,051',
    r'\b263\b'
]
combined_regex = re.compile('|'.join(PATTERNS))

exact_matches = []

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        if file.endswith(('.png', '.joblib', '.jpg', '.ico', '.woff', '.woff2')):
            continue
        path = os.path.join(root, file)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_no, line in enumerate(f, 1):
                    found = combined_regex.findall(line)
                    if found:
                        exact_matches.append((path, line_no, found, line.strip()))
        except Exception as e:
            pass

print(f"Total exact word-boundary matches: {len(exact_matches)}")
for path, line_no, found, line in exact_matches:
    print(f"{path}:{line_no} [{found}] -> {line[:100]}")
