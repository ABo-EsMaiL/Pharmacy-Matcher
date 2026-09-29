import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

p12_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-012"]["matches"] }
p14_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-014"]["matches"] }
p15_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-015"]["matches"] }
p16_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-016"]["matches"] }

dropped_in_14 = set(p12_matches.keys()) - set(p14_matches.keys())

print(f"=== THE 10 DROPPED ITEMS IN PROC-014 (Total: {len(dropped_in_14)}) ===")
for wh, req in sorted(dropped_in_14):
    cand_12 = p12_matches.get((wh, req), "NONE")
    cand_15 = p15_matches.get((wh, req), "NOT FOUND")
    cand_16 = p16_matches.get((wh, req), "NOT FOUND")
    
    # check review
    in_15_rev = [r for r in data["PROC-015"]["reviews"] if r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh]
    in_16_rev = [r for r in data["PROC-016"]["reviews"] if r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh]
    
    status_15 = f"MATCH: {cand_15}" if cand_15 != "NOT FOUND" else (f"REVIEW: {in_15_rev[0]['اسم المرشح في المخزن']}" if in_15_rev else "NOT FOUND")
    status_16 = f"MATCH: {cand_16}" if cand_16 != "NOT FOUND" else (f"REVIEW: {in_16_rev[0]['اسم المرشح في المخزن']}" if in_16_rev else "NOT FOUND")
    
    print(f"\nShortage: {req} | Warehouse: {wh}")
    print(f"  PROC-012: {cand_12}")
    print(f"  PROC-014: DROPPED")
    print(f"  PROC-015 (Gemini): {status_15}")
    print(f"  PROC-016 (ChatGPT): {status_16}")
