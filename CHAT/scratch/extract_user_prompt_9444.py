import json
import re

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 9443: # step 9444
            d = json.loads(line)
            c = d.get('content', '')
            user_turns = re.findall(r'<div[^>]*class="[^"]*user[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', c, re.DOTALL)
            print(f"User turns count: {len(user_turns)}")
            for ut in user_turns:
                text_clean = re.sub(r'<[^>]+>', ' ', ut)
                text_clean = ' '.join(text_clean.split())
                print("USER PROMPT:", text_clean)
            break
