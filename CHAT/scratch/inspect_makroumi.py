import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

p15_mak = { m["اسم الصنف المطلوب"].strip(): m["اسم الصنف في المخزن"].strip() for m in data["PROC-015"]["matches"] if m["المخزن"] == "المكرومي المنصورة.pdf" }
p16_mak = { m["اسم الصنف المطلوب"].strip(): m["اسم الصنف في المخزن"].strip() for m in data["PROC-016"]["matches"] if m["المخزن"] == "المكرومي المنصورة.pdf" }

print(f"P15 Makroumi matches: {len(p15_mak)}")
print(f"P16 Makroumi matches: {len(p16_mak)}")

print("\n--- Items matched in P16 (ChatGPT) but NOT in P15 (Gemini) in Makroumi ---")
for req, cand in p16_mak.items():
    if req not in p15_mak:
        print(f"  Shortage: {req} -> Warehouse: {cand}")

print("\n--- Items matched in P15 (Gemini) but NOT in P16 (ChatGPT) in Makroumi ---")
for req, cand in p15_mak.items():
    if req not in p16_mak:
        print(f"  Shortage: {req} -> Warehouse: {cand}")
