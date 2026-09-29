import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if 9422 <= i < 9443:
            data = json.loads(line)
            tp = data.get("type", "")
            if tp == "PLANNER_RESPONSE":
                print(f"=== STEP {i} ===")
                print(data.get("content", ""))
                print("\n" + "="*80)
