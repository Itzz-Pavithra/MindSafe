import re

with open('scratch/paper_full_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

brackets = re.findall(r'\[([^\]]{1,100})\]', text)
print('Unique brackets found in text:')
for b in sorted(set(brackets)):
    print(f'  [{b}]')

print('\nSearching for missing / placeholder phrases:')
phrases = ['not available', 'data not available', 'unavailable', 'tbd', 'to be added', 'placeholder']
for p in phrases:
    found = list(re.finditer(re.escape(p), text, re.IGNORECASE))
    print(f'Phrase "{p}": {len(found)} matches')
    for m in found:
        snippet = text[max(0, m.start()-80):min(len(text), m.end()+80)].replace('\n', ' ')
        print(f'   -> ...{snippet}...')
