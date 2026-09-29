import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        if data.get("source") == "USER_EXPLICIT" or data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "vision" in content.lower() or "صورة" in content or "صور" in content or "استخراج" in content:
                print(f"Line {i}: {content[:150]}...")
