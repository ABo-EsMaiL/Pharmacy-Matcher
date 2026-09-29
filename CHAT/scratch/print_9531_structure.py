import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 9531:
            data = json.loads(line)
            cnt = data.get("content", "")
            start = cnt.find("trade_name")
            if start != -1:
                print(cnt[start-400:start+1200])
            break
