import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 9443: # step 9444
            d = json.loads(line)
            c = d.get('content', '')
            import re
            m = re.findall(r'<ms-chat-turn.*?</ms-chat-turn>', c, re.DOTALL)
            print(f"Total turns found: {len(m)}")
            for t in m:
                # print text inside
                text_clean = re.sub(r'<[^>]+>', ' ', t)
                text_clean = ' '.join(text_clean.split())
                print("TURN SNIPPET:", text_clean[:500])
            break
