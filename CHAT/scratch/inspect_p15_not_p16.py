import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

p15_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-015"]["matches"] }
p16_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-016"]["matches"] }

p15_not_16 = set(p15_matches.keys()) - set(p16_matches.keys())

print(f"=== ITEMS IN PROC-015 (GEMINI) BUT NOT IN PROC-016 (CHATGPT) (Total: {len(p15_not_16)}) ===")
for wh, req in sorted(p15_not_16):
    wh_item = p15_matches[(wh, req)]
    # Check if in P16 review
    rev_matches = [r for r in data["PROC-016"]["reviews"] if r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh]
    p16_loc = f"IN P16 REVIEW (reason: {rev_matches[0].get('السبب','')[:60]})" if rev_matches else "IN P16 NOT FOUND"
    print(f"  [{wh}] {req} -> {wh_item} | P16 Status: {p16_loc}")
