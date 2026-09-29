import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line_idx, line in enumerate(f):
        data = json.loads(line)
        content = data.get("content", "")
        # Look for run button or prompt container in html
        for needle in ["ms-run-button", "run-button", "run_button", "prompt-container", "input-container", "mat-icon"]:
            if needle in content and ("<button" in content or "<div" in content):
                print(f"Match at line {line_idx} ({needle}):")
                idx = content.find(needle)
                print(content[max(0, idx-200):min(len(content), idx+500)])
                print("="*60)
                break
