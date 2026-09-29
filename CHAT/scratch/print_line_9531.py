import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 9531:
            data = json.loads(line)
            print(data.get("content", ""))
            break
