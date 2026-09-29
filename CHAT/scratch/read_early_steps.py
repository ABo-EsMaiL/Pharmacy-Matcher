import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in [9442, 9443, 9474, 9475]:
            d = json.loads(line)
            c = d.get('content', '')
            t = d.get('type', '')
            print(f"=== STEP {idx+1} ({t}) ===")
            print(c[:1500])
            print('='*50)
