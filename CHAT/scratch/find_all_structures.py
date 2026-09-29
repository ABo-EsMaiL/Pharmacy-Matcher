import json

transcript_path = r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\.system_generated\logs\transcript_full.jsonl"

matches = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        tp = data.get("type", "")
        src = data.get("source", "")
        cnt = data.get("content", "")
        
        # We are looking for PLANNER_RESPONSE containing json structure or schema or response format
        if tp == "PLANNER_RESPONSE":
            lower = cnt.lower()
            if "structure" in lower or "structure" in cnt or "json" in lower or "item_name" in lower or "schema" in lower:
                # check if there is a json code block
                if "```json" in cnt or "```" in cnt:
                    matches.append((i, cnt))

print(f"Total structure matches in PLANNER_RESPONSE: {len(matches)}")
for line_no, cnt in matches:
    # Look for code blocks in cnt
    import re
    blocks = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", cnt)
    if blocks:
        print(f"\n==================== Line {line_no} ====================")
        for b in blocks:
            print(b[:500])
            print("---")
