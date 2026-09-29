import json

full_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"
with open(full_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 9985:
            data = json.loads(line)
            content = data.get("content", "")
            start = content.find("concurrency_limit")
            print(content[start:start+4000])
            break
