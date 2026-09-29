import json
from pathlib import Path

p = Path(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl")
with open(p, "rb") as f:
    f.seek(max(0, f.seek(0, 2) - 1000000), 0)
    chunk = f.read().decode("utf-8", errors="ignore")

lines = chunk.strip().split("\n")
# find the last line that has type USER_INPUT
for line in reversed(lines):
    try:
        obj = json.loads(line)
        if obj.get("type") == "USER_INPUT":
            content = obj.get("content", "")
            print("Found USER_INPUT! Length:", len(content))
            with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\user_raw_dom.txt", "w", encoding="utf-8") as out:
                out.write(content)
            print("Saved to scratch/user_raw_dom.txt")
            break
    except Exception as e:
        continue
