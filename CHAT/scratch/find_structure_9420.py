import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if 9420 <= i <= 9600:
            data = json.loads(line)
            c = data.get("content", "")
            if "structure" in c.lower() or "هيكل" in c or "حقول" in c or "schema" in c.lower():
                tp = data.get("type", "")
                src = data.get("source", "")
                print(f"Line {i} ({src}/{tp}): {c[:300]}...\n")
