import sys
sys.path.insert(0, ".")
sys.path.insert(0, r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a")
from scratch.sim_full_run import *

# Let's collect and print the auto matches
with open("scratch_auto_matches.txt", "w", encoding="utf-8") as f:
    for wh_name, wh_items in wh_data.items():
        finder = FastCandidateFinder()
        wh_catalog = [{"id": f"W-{i:05}", "name": item.get("item_name_raw", "")} for i, item in enumerate(wh_items)]
        finder.fit(wh_catalog)
        wh_normalized = {normalize_text(name): name for name in [i["name"] for i in wh_catalog]}
        
        f.write(f"\n==================== {wh_name} ====================\n")
        count = 0
        for item in deduped_shortages:
            s_name = item["item_name_raw"]
            norm_name = normalize_text(s_name)
            if norm_name in wh_normalized:
                count += 1
                f.write(f"{count}. [EXACT] [{s_name}] <---> [{wh_normalized[norm_name]}]\n")
            else:
                top_candidates = finder.search(s_name, top_k=3)
                if not top_candidates:
                    continue
                best = top_candidates[0]
                ok, reason = is_deterministic_auto_match(s_name, best["name"])
                if ok:
                    count += 1
                    f.write(f"{count}. [AUTO] [{s_name}] <---> [{best['name']}]\n")

print("Saved all auto matches to scratch_auto_matches.txt")
