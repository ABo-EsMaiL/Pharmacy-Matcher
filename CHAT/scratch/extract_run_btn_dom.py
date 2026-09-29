import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "أنت لما بتيجي تبعت الرسالة" in content:
                with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\user_run_btn_dom.txt", "w", encoding="utf-8") as out:
                    out.write(content)
                print("Saved, len:", len(content))
