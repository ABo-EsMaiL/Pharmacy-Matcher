import json
import re

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "أنت لما بتيجي تبعت الرسالة" in content:
                # Remove base64 data to keep it small
                cleaned = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', 'data:image/...[BASE64]...', content)
                with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\user_run_btn_dom_clean.txt", "w", encoding="utf-8") as out:
                    out.write(cleaned)
                print("Cleaned saved, len:", len(cleaned))
