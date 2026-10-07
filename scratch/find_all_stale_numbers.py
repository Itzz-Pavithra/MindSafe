import os

EXCLUDE_DIRS = {'.git', 'node_modules', '.svelte-kit', 'scratch', '__pycache__'}
SEARCH_TERMS = ['514', '411', '103', '48.54', '0.3275', '0.4177', '44.66', '1314', '1,314', '1051', '263']

matches = []

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        if file.endswith(('.png', '.joblib', '.jpg', '.ico', '.woff', '.woff2')):
            continue
        path = os.path.join(root, file)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for term in SEARCH_TERMS:
                    if term in content:
                        matches.append((path, term))
        except Exception as e:
            pass

print(f"Total matching file-term pairs: {len(matches)}")
for path, term in sorted(set(matches)):
    print(f"  {path} contains '{term}'")
