import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"

turns = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i < 9420:
            continue
        data = json.loads(line)
        tp = data.get("type", "")
        src = data.get("source", "")
        cnt = data.get("content", "").strip()
        
        if not cnt:
            continue
            
        if tp == "USER_INPUT" or src == "USER_EXPLICIT":
            turns.append(("USER", i, cnt))
        elif tp == "PLANNER_RESPONSE" and cnt:
            turns.append(("ASSISTANT", i, cnt))

print(f"Total non-empty turns: {len(turns)}")

for role, line_no, content in turns:
    print(f"\n{'='*35} [{role}] (Line {line_no}) {'='*35}")
    lines = content.splitlines()
    clean = []
    for l in lines:
        if not l.strip().startswith("<") and not "span class" in l:
            clean.append(l)
    clean_txt = "\n".join(clean)
    print(clean_txt[:800])
    if len(clean_txt) > 800:
        print(f"... [Truncated {len(clean_txt)-800} chars]")
