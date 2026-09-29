import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "في مشكلة ومبعتش صورة" in content:
                with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\last_dom_snippet.txt", "w", encoding="utf-8") as out:
                    out.write(content)
                print("Saved snippet, len:", len(content))
