import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

import json
import time
import requests as http_requests
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder
from src.match.text_match import normalize_text
PHARMA_STOPWORDS = {
    'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'شراب', 'شرب', 'معلق', 'سائل', 'مرهم', 'كريم', 
    'جل', 'جيل', 'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال', 'لبوس', 'لبوسة', 'لبوسه',
    'نقط', 'قطرة', 'قطره', 'بخاخ', 'بخاخة', 'بخاخه', 'سبراي', 'فوار', 'اكياس', 'كيس',
    'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه', 'محلول', 'مس', 'دهان', 'فيلم',
    'مجم', 'جم', 'جرام', 'مل', 'مللي', 'لتر', 'ميكرو', 'شريط', 'علبه', 'علبة',
    'باكت', 'باكو', 'كرتونه', 'كرتونة', 'فلتر',
    'س', 'ج', 'سعر', 'جديد', 'قديم', 'تاريخ', 'بعيد', 'قريب', 'صغير', 'كبير', 'وسط',
    'محلي', 'مستورد', 'خاص', 'نقدى', 'اجل'
}

FORM_GROUPS = {
    'tablet': {'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'حبوب', 'فيلم', 'شريط'},
    'syrup': {'شراب', 'شرب', 'معلق', 'سائل'},
    'cream_ointment': {'كريم', 'مرهم', 'دهان'},
    'gel': {'جل', 'جيل'},
    'suppository': {'لبوس', 'لبوسه', 'لبوسة', 'تحاميل', 'اقماع'},
    'injection': {'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال'},
    'drops': {'نقط', 'قطرة', 'قطره'},
    'spray': {'بخاخ', 'بخاخة', 'بخاخه', 'سبراي'},
    'sachet': {'فوار', 'اكياس', 'كيس'},
    'wash': {'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه'},
    'topical_solution': {'مس', 'محلول', 'لوشن', 'لوسيون'},
}

def extract_form_group(text: str) -> str | None:
    norm = normalize_text(text)
    words = set(norm.split())
    for group_name, group_words in FORM_GROUPS.items():
        if words & group_words:
            return group_name
    return None

def extract_brand_tokens(text: str) -> str:
    text = re.sub(r'(\d+)', r' \1 ', text)
    norm = normalize_text(text)
    norm = re.sub(r'/.*', '', norm)
    words = [w for w in norm.split() if w not in PHARMA_STOPWORDS and not w.isdigit() and len(w) > 1]
    return " ".join(words)
from rapidfuzz import fuzz

NEW_SYSTEM_PROMPT = """You are an expert clinical and Egyptian pharmaceutical matching assistant.
You match requested drug names from pharmacy shortages with candidate items available in wholesale drug warehouses.

CRITICAL PHARMACEUTICAL RULES:
1. STRICT BRAND IDENTITY (NO GENERICS / NO ALTERNATIVES):
   - You MUST match the EXACT SAME trade brand name (e.g. Mebo matching Mebo, Dolphin matching Dolphin, Confragran matching Confragran).
   - NEVER suggest or accept alternative brand names, different trade names, or generics (e.g. Mebo != Bernasource, Dolphin != Indomethacin, Confragran != Viagra, Bronchophane != Brufen, Sinupret != Sinopril, PK-Merz != Merz Spezial, E-Moxclav != Curam, Averocoxib != Arcoxia, Herobaby != Bebelac).
   - If the trade brand name is different or unrelated, YOU MUST RETURN "status": "no_match" (or omit it). NEVER mark different brands as "match" or "review"!
   - Allow ONLY minor spelling variants or OCR typos of the SAME brand (e.g. كوللوماك vs كولومالك, سيديبروكت vs سيديبروك, ينسون ايزيس vs زيس ينسون, اسبوسيد vs اسبوبسيد).

2. DOSAGE FORM (ZERO TOLERANCE FOR CONFLICTS):
   - Dosage forms MUST be compatible:
     - Tablets/Capsules (اقراص, كبسول, حبوب, فيلم) ONLY match Tablets/Capsules.
     - Syrups/Suspensions (شراب, شرب, معلق) ONLY match Syrups. NEVER match tablets with syrup (e.g. Cetal tablets != Cetal syrup).
     - Creams/Ointments (كريم, مرهم) ONLY match Creams/Ointments. NEVER match cream with suppository (e.g. Gynozol cream != Gynozol suppository).
     - Injections/Ampoules (امبول, حقن, فيال) ONLY match Injections.
     - Suppositories (لبوس) ONLY match Suppositories.
     - Drops (نقط, قطرة) ONLY match Drops.
     - Sprays (بخاخ, سبراي) ONLY match Sprays.
   - If dosage forms conflict, YOU MUST RETURN "status": "no_match".

3. STRENGTH / CONCENTRATION (ZERO TOLERANCE FOR MISMATCH):
   - If the requested drug specifies a strength (e.g. 457mg, 600mg, 500mg, 1000mg/1gm, 20mg, 40mg) and the candidate has a DIFFERENT numeric strength:
     YOU MUST RETURN "status": "no_match".
   - Note equivalencies: 1000mg = 1gm (1000مجم = 1جم), 500mg = 0.5gm, 0.25mg = ربع (250mcg).

4. PACKAGING, PACK SIZE & WHOLESALE UNITS (MATCH vs REVIEW):
   - "match": Same brand, same form, same strength.
     - STANDARD PACKS: If requested shortage specifies standard pack count (e.g. "ديجستين 20قرص", "كيتولاك 5 امبوله", "كولونا 3شريط", "ايفاستين 2 شريط", "ماريفان 3شريط") and warehouse candidate has the same drug, form, and strength but does not explicitly state the pack size (e.g. "ديجستين اقراص/فاركو", "كيتولاك امبول/العامريه", "كولونا اقراص"):
       THIS IS A 100% MATCH ("status": "match")! NEVER mark this as review!
     - Suffixes like "/فاركو", "/جلاكسو", "س ج", "سعر جديد", "سعر قديم" do not change the product.
   - "review": ONLY for the SAME EXACT medicine brand when there is an EXPLICIT, CONFLICTING pack count on BOTH sides (e.g. requested 15 tablets vs candidate explicitly writes 60 tablets of Doliprane).
     - Wholesale bundles like "باكت 120" (meaning a carton of 120 boxes) or "باكت 50" are wholesale lot sizes, NOT the blister/tablet count inside a single box! Do not confuse wholesale carton count with tablet count.

SCHEMA:
Return ONLY a valid JSON object matching this schema:
{
  "results": [
    {
      "case_id": "string",
      "status": "match" | "review",
      "item_id": "string (the matching candidate ID)",
      "reason": "string (Arabic explanation when review, otherwise empty string)"
    }
  ]
}

CRITICAL RULES FOR RESPONSE:
- ONLY include cases that are "match" or "review".
- DO NOT return cases that are "no_match" (any omitted case_id is automatically considered no_match).
- DO NOT return markdown blocks (no ```json). Return ONLY the raw JSON starting with { and ending with }.
"""

shortages_raw = extract_item_names(read_excel(Path(r'data/processes/PROC-001/input_shortages/0913.xlsx')))
unique_shortages = {}
for s in shortages_raw:
    n = s.get("item_name_raw", "")
    if n and n not in unique_shortages:
        unique_shortages[n] = s
shortage_names = list(unique_shortages.keys())

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/السلام شبين.pdf'), api_key="")
wh_catalog = [{"id": f"W-{i:05}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]
catalog_by_id = {item["id"]: item["name"] for item in wh_catalog}

finder = FastCandidateFinder()
finder.fit(wh_catalog)

llm_cases = []
for idx, req in enumerate(shortage_names):
    raw_cands = finder.search(req, top_k=6)
    req_brand = extract_brand_tokens(req)
    req_form = extract_form_group(req)
    
    valid = []
    for c in raw_cands:
        cand_name = c["name"]
        cand_brand = extract_brand_tokens(cand_name)
        cand_form = extract_form_group(cand_name)
        
        if req_form and cand_form and req_form != cand_form:
            continue
            
        words_req = req_brand.split()
        words_cand = cand_brand.split()
        if len(words_req) > 1 or len(words_cand) > 1:
            sim = fuzz.token_sort_ratio(req_brand, cand_brand)
        else:
            sim = fuzz.ratio(req_brand, cand_brand)
            
        if req_brand and cand_brand:
            if req_brand.startswith(cand_brand) or cand_brand.startswith(req_brand):
                sim = max(sim, 80)
                
        if sim >= 60 or c["score"] >= 0.50:
            valid.append({"id": c["id"], "name": cand_name})
            
    if valid:
        llm_cases.append({
            "case_id": f"Q{idx:05}",
            "requested_name": req,
            "candidates": valid[:3]
        })

print(f"Total shortages: {len(shortage_names)}")
print(f"Filtered cases for LLM: {len(llm_cases)}")

# Let's send to MSEMAX
url = "http://127.0.0.1:8000/v1/chat/completions"
api_key = "[REDACTED_CREDENTIAL]"

batch_size = 75
batches = [llm_cases[i:i + batch_size] for i in range(0, len(llm_cases), batch_size)]
print(f"Divided into {len(batches)} batch(es).")

all_matched = []
all_review = []

for b_idx, batch in enumerate(batches):
    print(f"\n[*] Sending Batch {b_idx+1}/{len(batches)} ({len(batch)} items)...")
    body = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": NEW_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"cases": batch}, ensure_ascii=False)}
        ]
    }
    t0 = time.time()
    resp = http_requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=120)
    elapsed = time.time() - t0
    print(f"    Status: {resp.status_code} in {elapsed:.1f}s")
    
    if resp.status_code == 200:
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        # parse json
        import re
        m = re.search(r'\{[\s\S]*\}', content)
        if m:
            res_obj = json.loads(m.group(0))
            items = res_obj.get("results", [])
            for it in items:
                cid = it.get("case_id")
                # find case
                c_item = next((c for c in batch if c["case_id"] == cid), None)
                if not c_item: continue
                req_name = c_item["requested_name"]
                wh_name = catalog_by_id.get(it.get("item_id"), "")
                st = it.get("status")
                
                # Double-check safety:
                rf = extract_form_group(req_name)
                wf = extract_form_group(wh_name)
                if rf and wf and rf != wf:
                    continue
                    
                if st == "match":
                    all_matched.append((req_name, wh_name))
                elif st == "review":
                    all_review.append((req_name, wh_name, it.get("reason", "")))
        print(f"    Done: {len(all_matched)} matches so far, {len(all_review)} reviews so far.")

print("\n" + "="*60)
print(f"FINAL RESULTS FOR السلام شبين: {len(all_matched)} Matches, {len(all_review)} Reviews")
print("="*60)
print("MATCHES:")
for i, (r, w) in enumerate(all_matched, 1):
    print(f"{i:2d}. Req: '{r}' <---> WH: '{w}'")
print("\nREVIEWS:")
for i, (r, w, reas) in enumerate(all_review, 1):
    print(f"{i:2d}. Req: '{r}' <---> WH: '{w}' | السبب: {reas}")
