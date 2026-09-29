with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if "أنت لما بتيجي تبعت الرسالة" in line:
            import json
            data = json.loads(line)
            content = data.get("content", "")
            print("Content length:", len(content))
            # Find the position of 'loaded-image'
            pos = content.find("loaded-image")
            print("Pos of loaded-image:", pos)
            # Find where src ends: find '></div>' or find 'button'
            src_end = content.find('">', pos)
            if src_end != -1:
                tail = content[src_end:src_end + 3000]
                print("Tail after image:")
                print(tail)
            else:
                print("Could not find '> after loaded-image")
