import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        d = json.loads(line)
        c = d.get('content', '')
        t = d.get('type', '')
        if t in ['USER_INPUT', 'PLANNER_RESPONSE']:
            lower_c = c.lower()
            if ('structure' in lower_c or 'json schema' in lower_c or 'بنية' in c or 'حقول' in c) and ('صنف' in c or 'extract' in lower_c):
                # check if there is discussion of fields
                if 'item_name_raw' in c or 'تركيز' in c or 'trade_name' in c or 'unstructured' in lower_c:
                    print(f"=== STEP {idx+1} ({t}) ===")
                    lines = [l for l in c.split('\n') if any(k in l for k in ['structure', 'Structure', 'حقول', 'بنية', 'JSON', 'schema', 'قواعد'])]
                    print("\n".join(lines[:10]))
                    print('='*50)
