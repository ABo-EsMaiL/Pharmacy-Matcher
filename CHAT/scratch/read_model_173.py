import json
from pathlib import Path

transcript_path = Path(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl")

lines = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line_idx, line in enumerate(f):
        if line_idx >= 9475 and line_idx <= 9520:
            try:
                data = json.loads(line)
                if data.get("type") == "PLANNER_RESPONSE":
                    content = data.get("content", "")
                    if content:
                        print(f"=== STEP {line_idx} PLANNER RESPONSE ===")
                        print(content[:1500])
                        print("\n" + "="*80)
            except Exception:
                pass
