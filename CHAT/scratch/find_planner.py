import json
from pathlib import Path

transcript_path = Path(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if 9470 <= i <= 9535:
            d = json.loads(line)
            st = d.get("source", "")
            tp = d.get("type", "")
            cnt = d.get("content", "")
            if cnt:
                print(f"Line {i} | Source: {st} | Type: {tp} | Content len: {len(cnt)}")
                if tp == "PLANNER_RESPONSE" or st == "MODEL":
                    print(cnt[:600])
                    print("\n" + "-"*40)
