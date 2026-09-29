import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"

turns = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        tp = data.get("type", "")
        src = data.get("source", "")
        cnt = data.get("content", "")
        
        if tp == "USER_INPUT" or src == "USER_EXPLICIT":
            turns.append(("USER", i, cnt))
        elif tp == "PLANNER_RESPONSE":
            turns.append(("ASSISTANT", i, cnt))

print(f"Total turns: {len(turns)}")

# Print from where vision started
# Let's find index where line >= 9420
start_idx = 0
for idx, (role, line_no, content) in enumerate(turns):
    if line_no >= 9420:
        start_idx = idx
        break

for idx in range(start_idx, len(turns)):
    role, line_no, content = turns[idx]
    print(f"\n{'='*40} [{role}] TURN {idx} (Line {line_no}) {'='*40}")
    # Strip huge DOM / html if any
    lines = content.splitlines()
    clean_lines = []
    for l in lines:
        if not l.strip().startswith("<") and not "span class" in l:
            clean_lines.append(l)
    clean_content = "\n".join(clean_lines)
    print(clean_content[:1200])
    if len(clean_content) > 1200:
        print(f"... [Truncated {len(clean_content)-1200} chars]")
