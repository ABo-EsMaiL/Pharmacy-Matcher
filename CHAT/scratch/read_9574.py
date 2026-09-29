import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in [9532, 9573]:
            d = json.loads(line)
            c = d.get('content', '')
            print(f"=== STEP {idx+1} ===")
            print(c[:2500])
            print('='*50)
