import json

with open(r'C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 9735:
            d = json.loads(line)
            c = d.get('content', '')
            chunk_size = 1500
            for i in range(0, len(c), chunk_size):
                print(f"--- CHUNK {i//chunk_size + 1} ---")
                print(c[i:i+chunk_size])
            break
