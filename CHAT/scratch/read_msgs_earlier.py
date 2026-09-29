import json
from pathlib import Path

transcript_path = Path(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl")

user_msgs = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line_idx, line in enumerate(f):
        try:
            data = json.loads(line)
            if data.get("source") == "USER_EXPLICIT" or data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                if content:
                    user_msgs.append((line_idx, content))
        except Exception:
            pass

for idx in range(160, 174):
    if idx < len(user_msgs):
        l_num, msg = user_msgs[idx]
        print(f"==================== USER MESSAGE {idx} (line {l_num}) ====================")
        print(msg)
        print("\n" + "="*80 + "\n")
