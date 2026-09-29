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

print(f"Total user messages: {len(user_msgs)}")
for idx, (l_num, msg) in enumerate(user_msgs[-12:]):
    print(f"==================== USER MESSAGE {len(user_msgs)-12+idx} (line {l_num}) ====================")
    print(msg[:500])
    print("\n")
