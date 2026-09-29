import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/AI_Engineer/Pharmacy-agy")))
import json
import re
import difflib
from src.extract.pdf_reader import _get_file_hash, parse_structured_result

wh_dir = Path("data/processes/PROC-015/input_warehouses")
cache_dir = Path("data/processes/data/.unstructured_cache")

warehouse_items = {}
for pdf in wh_dir.glob("*.pdf"):
    h = _get_file_hash(pdf)
    cfile = cache_dir / f"{h}_extract.json"
    if cfile.exists():
        with open(cfile, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = parse_structured_result(data, pdf.name)
        warehouse_items[pdf.name] = items
        print(f"Loaded {len(items)} items for {pdf.name}")

# Load 4-way comparison data
with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\extracted_4way_data.json", "r", encoding="utf-8") as fp:
    full_data = json.load(fp)

p15_matches = {row["اسم الصنف المطلوب"].strip(): row for row in full_data["PROC-015"]["matches"]}
p15_review = {row["اسم الصنف المطلوب"].strip(): row for row in full_data["PROC-015"]["reviews"]}
p15_not_found = [row["اسم الصنف"].strip() for row in full_data["PROC-015"]["not_found"] if row.get("اسم الصنف")]

p16_matches = {row["اسم الصنف المطلوب"].strip(): row for row in full_data["PROC-016"]["matches"]}
p16_review = {row["اسم الصنف المطلوب"].strip(): row for row in full_data["PROC-016"]["reviews"]}
p16_not_found = [row["اسم الصنف"].strip() for row in full_data["PROC-016"]["not_found"] if row.get("اسم الصنف")]

print(f"\nPROC-015 Not Found: {len(p15_not_found)}")
print(f"PROC-016 Not Found: {len(p16_not_found)}")

# Normalization
def clean_str(s):
    if not s:
        return ""
    s = str(s).lower()
    for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        s = s.replace(e, w)
    rep = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ئ': 'ي', 'ی': 'ي',
        'ة': 'ه', 'گ': 'ك', 'ک': 'ك', 'پ': 'ب', 'ژ': 'ز', 'چ': 'ج',
        'ڤ': 'ف', 'ف': 'ف', 'ؤ': 'و', 'ء': '', 'ـ': '', '-': ' ', '_': ' ',
        '/': ' ', '\\': ' ', '+': ' ', '(': ' ', ')': ' ', '[': ' ', ']': ' '
    }
    for k, v in rep.items():
        s = s.replace(k, v)
    s = re.sub(r'[^a-z0-9\u0600-\u06FF\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

dosage_words = {
    'اقراص', 'قرص', 'كبسول', 'كبسولة', 'شريط', 'امبول', 'حقن', 'نقط', 'قطرة', 
    'شراب', 'معلق', 'كريم', 'مرهم', 'جل', 'سبراي', 'بخاخ', 'اكياس', 'كيس', 
    'س', 'ج', 'جديد', 'سعر', 'قديم', 'باكت', 'باكو', 'كرتونة', 'مل', 'ملل', 
    'جم', 'جرام', 'مجم', 'مج', 'مكجم', 'فوار', 'لبوس', 'شمع', 'محلول', 'غسول',
    'لوشن', 'مضمضة', 'سبراى', 'مرطب', 'كبار', 'اطفال', 'رضع', 'مستورد', 'محلي',
    'تابلت', 'كبسولات', 'امبولات', 'شرايط', 'اكياس'
}

def get_tokens(s):
    norm = clean_str(s)
    words = [w for w in norm.split() if w not in dosage_words and not w.isdigit()]
    return words

# Audit items that were NOT FOUND in PROC-015
missed_candidates = []

for shortage in p15_not_found:
    s_tokens = get_tokens(shortage)
    if not s_tokens:
        continue
    s_brand = s_tokens[0]
    s_norm = clean_str(shortage)
    
    # Check against all warehouse items
    for wh_name, items in warehouse_items.items():
        for cand_dict in items:
            cand_raw = cand_dict.get("item_name_raw", "").strip() if isinstance(cand_dict, dict) else str(cand_dict).strip()
            if not cand_raw:
                continue
            c_norm = clean_str(cand_raw)
            c_tokens = get_tokens(cand_raw)
            if not c_tokens:
                continue
            c_brand = c_tokens[0]
            
            # Check 1: Brand exact match or Brand prefix match (min 4 chars)
            brand_match = False
            sim = 0
            
            if s_brand == c_brand:
                brand_match = True
                sim = int(difflib.SequenceMatcher(None, s_norm, c_norm).ratio() * 100)
            elif len(s_brand) >= 4 and len(c_brand) >= 4:
                if s_brand in c_brand or c_brand in s_brand:
                    brand_match = True
                    sim = int(difflib.SequenceMatcher(None, s_norm, c_norm).ratio() * 100)
                else:
                    b_ratio = int(difflib.SequenceMatcher(None, s_brand, c_brand).ratio() * 100)
                    if b_ratio >= 80:
                        brand_match = True
                        sim = b_ratio
            
            if brand_match and sim >= 65:
                # Check status in P15 and P16
                p15_stat = "MATCHED" if shortage in p15_matches else ("REVIEW" if shortage in p15_review else "NOT_FOUND")
                p16_stat = "MATCHED" if shortage in p16_matches else ("REVIEW" if shortage in p16_review else "NOT_FOUND")
                
                missed_candidates.append({
                    "shortage": shortage,
                    "warehouse": wh_name,
                    "candidate_raw": cand_raw,
                    "sim": sim,
                    "s_brand": s_brand,
                    "c_brand": c_brand,
                    "p15_status": p15_stat,
                    "p16_status": p16_stat
                })

# Deduplicate
dedup = {}
for m in missed_candidates:
    key = (m["shortage"], m["warehouse"], m["candidate_raw"])
    if key not in dedup or m["sim"] > dedup[key]["sim"]:
        dedup[key] = m

unique_missed = list(dedup.values())
unique_missed.sort(key=lambda x: x["sim"], reverse=True)

# Separate into:
# 1. Missed by BOTH P15 and P16 (True potential discoveries!)
both_missed = [m for m in unique_missed if m["p15_status"] == "NOT_FOUND" and m["p16_status"] == "NOT_FOUND"]

# 2. Missed by P15 but caught or in review by P16
p16_only = [m for m in unique_missed if m["p15_status"] == "NOT_FOUND" and m["p16_status"] != "NOT_FOUND"]

print(f"\n==================================================")
print(f"Total candidate pairs found for Not Found items: {len(unique_missed)}")
print(f"Candidates missed by BOTH Gemini (P15) and ChatGPT (P16): {len(both_missed)}")
print(f"Candidates missed by Gemini (P15) but present in ChatGPT (P16): {len(p16_only)}")
print(f"==================================================\n")

print("--- TOP 30 CANDIDATES MISSED BY BOTH MODELS ---")
for i, m in enumerate(both_missed[:30], 1):
    print(f"{i}. [{m['warehouse']}]")
    print(f"   Shortage:  '{m['shortage']}'")
    print(f"   Warehouse: '{m['candidate_raw']}'")
    print(f"   Sim: {m['sim']}% | Brands: '{m['s_brand']}' vs '{m['c_brand']}'\n")

# Save full results to scratch json
with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\forensic_not_found_results.json", "w", encoding="utf-8") as fp:
    json.dump({
        "both_missed": both_missed,
        "p16_only": p16_only,
        "all": unique_missed
    }, fp, ensure_ascii=False, indent=2)
print("Saved to forensic_not_found_results.json")
