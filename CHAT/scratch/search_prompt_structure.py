import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx >= 9440 and idx <= 9600:
            d = json.loads(line)
            c = d.get('content', '')
            t = d.get('type', '')
            if 'structure' in c.lower() or 'البرومبت' in c or 'prompt' in c.lower() or 'استخراج' in c:
                if t in ['USER_INPUT', 'PLANNER_RESPONSE']:
                    print(f"=== STEP {idx+1} ({t}) ===")
                    # print first 500 chars
                    print(c[:600])
                    print('='*50)
