import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line_idx, line in enumerate(f):
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if any(k in content.lower() for k in ["<button", "run-button", "run_button", "runcontrol", "run-control", "stop", "class="]):
                print(f"--- Line {line_idx} ---")
                print(content[:1000])
                print("\n")
