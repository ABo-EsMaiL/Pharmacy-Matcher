import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

p15_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-015"]["matches"] }
p16_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-016"]["matches"] }

p16_not_15 = set(p16_matches.keys()) - set(p15_matches.keys())

print(f"=== ITEMS IN PROC-016 (CHATGPT) BUT NOT IN PROC-015 (GEMINI) (Total: {len(p16_not_15)}) ===")
for wh, req in sorted(p16_not_15):
    wh_item = p16_matches[(wh, req)]
    rev_15 = [r for r in data["PROC-015"]["reviews"] if r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh]
    p15_loc = f"IN P15 REVIEW (reason: {rev_15[0].get('السبب','')[:60]})" if rev_15 else "IN P15 NOT FOUND"
    print(f"  [{wh}] {req} -> {wh_item} | P15 Status: {p15_loc}")
