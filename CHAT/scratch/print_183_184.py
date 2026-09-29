import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in (9979, 9985):
            data = json.loads(line)
            print(f"=== STEP {i} ===")
            print(data.get("content", "")[:2500])
            print("\n" + "="*80)
