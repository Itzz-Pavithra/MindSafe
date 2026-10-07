import json

with open(r'C:\Users\pavit\.gemini\antigravity-ide\brain\e8b22332-4564-4aec-930f-ce4cd2cd0d2d\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('type') == 'USER_INPUT':
            content = obj.get('content', '')
            lines = content.splitlines()
            print('User content total lines in full:', len(lines))
            start_idx = -1
            for i, l in enumerate(lines):
                if 'Timestamp,' in l and 'SECTION A' in l:
                    start_idx = i
                    break
            print('CSV header at line:', start_idx)
            if start_idx != -1:
                csv_sub = lines[start_idx:]
                print('Total lines from CSV header onwards:', len(csv_sub))
