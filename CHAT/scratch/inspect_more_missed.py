import json

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\forensic_not_found_results.json", "r", encoding="utf-8") as fp:
    data = json.load(fp)

both_missed = data["both_missed"]
by_shortage = {}
for m in both_missed:
    s = m["shortage"]
    if s not in by_shortage:
        by_shortage[s] = []
    by_shortage[s].append(m)

print(f"Items 36 to 70:")
for s, candidates in list(by_shortage.items())[35:70]:
    print(f"\nShortage: '{s}'")
    for c in candidates[:2]:
        print(f"  -> [{c['warehouse']}] '{c['candidate_raw']}' (Sim: {c['sim']}%)")
