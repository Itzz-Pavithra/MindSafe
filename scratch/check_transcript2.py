import json

with open(r'C:\Users\pavit\.gemini\antigravity-ide\brain\e8b22332-4564-4aec-930f-ce4cd2cd0d2d\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('type') == 'USER_INPUT':
            content = obj.get('content', '')
            lines = content.splitlines()
            for idx, l in enumerate(lines[:50]):
                if 'Timestamp' in l:
                    print(f"Line {idx}: {l[:60]}")
            for idx, l in enumerate(lines[-50:]):
                if 'Timestamp' in l or 'SECTION' in l or '10-2026' in l or '09-2026' in l:
                    print(f"End line {idx}: {l[:60]}")
            print(f"Total lines: {len(lines)}")
            print("First line:", lines[0] if lines else "Empty")
            print("Last line:", lines[-1] if lines else "Empty")
