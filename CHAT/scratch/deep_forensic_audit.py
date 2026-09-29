import json
from pathlib import Path
import re
from rapidfuzz import fuzz

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

p12_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-012"]["matches"] }
p14_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-014"]["matches"] }
p15_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-015"]["matches"] }
p16_matches = { (m["المخزن"], m["اسم الصنف المطلوب"].strip()): m["اسم الصنف في المخزن"].strip() for m in data["PROC-016"]["matches"] }

p15_set = set(p15_matches.keys())
p16_set = set(p16_matches.keys())
p14_set = set(p14_matches.keys())
p12_set = set(p12_matches.keys())

print("=== 1. ITEMS FOUND IN PROC-015 (GEMINI) BUT NOT IN PROC-016 (CHATGPT) ===")
in_15_not_16 = p15_set - p16_set
print(f"Total: {len(in_15_not_16)}")
for wh, req in sorted(in_15_not_16):
    wh_item = p15_matches[(wh, req)]
    # check where it went in p16 (review or not found)
    in_p16_rev = any(r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh for r in data["PROC-016"]["reviews"])
    print(f"  [{wh}] {req} -> {wh_item} (In P16 Review? {in_p16_rev})")

print("\n=== 2. ITEMS FOUND IN PROC-016 (CHATGPT) BUT NOT IN PROC-015 (GEMINI) ===")
in_16_not_15 = p16_set - p15_set
print(f"Total: {len(in_16_not_15)}")
for wh, req in sorted(in_16_not_15):
    wh_item = p16_matches[(wh, req)]
    in_p15_rev = any(r["اسم الصنف المطلوب"].strip() == req and r.get("المخزن", "").strip() == wh for r in data["PROC-015"]["reviews"])
    print(f"  [{wh}] {req} -> {wh_item} (In P15 Review? {in_p15_rev})")

print("\n=== 3. WHAT HAPPENED TO THE 10 ITEMS DROPPED IN PROC-014? ===")
dropped_in_14 = p12_set - p14_set
print(f"Total items dropped in P14 vs P12: {len(dropped_in_14)}")
for wh, req in sorted(dropped_in_14):
    item_p12 = p12_matches[(wh, req)]
    in_p15 = (wh, req) in p15_set
    in_p16 = (wh, req) in p16_set
    print(f"  [{wh}] {req} (P12: {item_p12}) -> In P15 (Gemini)? {in_p15} | In P16 (ChatGPT)? {in_p16}")

print("\n=== 4. PHARMACEUTICAL QUALITY AUDIT OF P15 MATCHES ===")
# Check for any potential red lines: strength mismatch, combo mismatch
def norm_num(s):
    s = str(s)
    for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        s = s.replace(e, w)
    return s

def extract_str(t):
    m = re.search(r'(\d+(?:\.\d+)?)\s*(مجم|مج|جم|جرام|gm|mg|mcg|مكجم)?', norm_num(t.lower()))
    return m.group(1) if m else None

p15_suspicious = []
for (wh, req), wh_item in p15_matches.items():
    s_req = extract_str(req)
    s_wh = extract_str(wh_item)
    # Check co / plus
    co_r = bool(re.search(r'\b(co|plus|كو|بلس)\b', req.lower()))
    co_w = bool(re.search(r'\b(co|plus|كو|بلس)\b', wh_item.lower()))
    if co_r != co_w:
        p15_suspicious.append((wh, req, wh_item, "CO/PLUS mismatch"))
    elif s_req and s_wh and s_req != s_wh:
        try:
            if float(s_req) != float(s_wh):
                p15_suspicious.append((wh, req, wh_item, f"Strength mismatch: {s_req} vs {s_wh}"))
        except:
            p15_suspicious.append((wh, req, wh_item, f"Strength mismatch: {s_req} vs {s_wh}"))

print(f"P15 Potential Suspicious Matches: {len(p15_suspicious)}")
for item in p15_suspicious:
    print("  ", item)

print("\n=== 5. PHARMACEUTICAL QUALITY AUDIT OF P16 MATCHES ===")
p16_suspicious = []
for (wh, req), wh_item in p16_matches.items():
    s_req = extract_str(req)
    s_wh = extract_str(wh_item)
    co_r = bool(re.search(r'\b(co|plus|كو|بلس)\b', req.lower()))
    co_w = bool(re.search(r'\b(co|plus|كو|بلس)\b', wh_item.lower()))
    if co_r != co_w:
        p16_suspicious.append((wh, req, wh_item, "CO/PLUS mismatch"))
    elif s_req and s_wh and s_req != s_wh:
        try:
            if float(s_req) != float(s_wh):
                p16_suspicious.append((wh, req, wh_item, f"Strength mismatch: {s_req} vs {s_wh}"))
        except:
            p16_suspicious.append((wh, req, wh_item, f"Strength mismatch: {s_req} vs {s_wh}"))

print(f"P16 Potential Suspicious Matches: {len(p16_suspicious)}")
for item in p16_suspicious:
    print("  ", item)
