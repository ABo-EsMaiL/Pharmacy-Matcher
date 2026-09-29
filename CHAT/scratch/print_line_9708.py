import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx in (9708, 9709, 9710, 9711, 9712):
            data = json.loads(line)
            print(f"=== LINE {idx} ===")
            print(data.get("content", "")[:1500])
