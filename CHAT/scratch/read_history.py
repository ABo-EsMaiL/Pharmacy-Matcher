import json

indices = [9574, 9641, 9683]
with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in indices:
            d = json.loads(line)
            c = d.get('content', '')
            print(f'=== LINE {idx+1} ===')
            print(c)
            print('='*50)
