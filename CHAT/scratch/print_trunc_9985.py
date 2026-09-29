import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 9985:
            data = json.loads(line)
            content = data.get("content", "")
            # print between 0913.xlsx and Connection to local LLM
            start = content.find("Processing Warehouse")
            if start == -1:
                start = content.find("0913.xlsx")
            print(content[start:start+4000])
            break
