import sys
from pathlib import Path

PROJECT_ROOT = Path(r"D:\AI_Engineer\Pharmacy-agy")
sys.path.insert(0, str(PROJECT_ROOT))

from src.fast_match.coordinator import (
    FastCoordinator, classify_pair, extract_brand_tokens, extract_form_group,
    get_strength_pattern, has_co, BRAND_FAMILIES
)
from src.config import Config
from rapidfuzz import fuzz

def test_guardrails_unit():
    print("=" * 70)
    print("1. TESTING POST-GEMINI GUARDRAIL ON AMBIGUOUS PAIRS")
    print("=" * 70)
    
    test_pairs = [
        ("بقدونس وكرفس ايزيس", "ایزیز بقدونس وکرکس 20 فلتر", "Inverted word order (Isis parsley)"),
        ("يمتليس كروماكس كت30كيس س ج", "يمتليس كروماتكس كت 30 كيس جديد", "OCR missing leading letter"),
        ("تربتيزول10 مجم اقراص", "تریپتازول 10 مج اقراس/باکت 200", "Arabic transliteration variant"),
        ("سكينورين كريم", "سکینوریتش کریم", "OCR typo in last letters"),
        ("كارنيفيتا ادفانس للرجال30كيس س ج", "کارنتینا ادفانس رجال/باکت16", "OCR typo"),
        ("لبن هيرو بيبي 2", "هيرو بيبي ٢", "Milk stopword stripped"),
        ("نيوروفيت اقراص 3 شريط", "نيروفيت اقراص سعر جديد", "Phonetic variation"),
        ("نوفالدول 1000 مجم 15 قرص", "نوفالدول 1000", "Paracetamol 1000mg"),
        ("كونجستال اقراص", "كونجستال", "Congestal brand match"),
    ]
    
    for req, cand, note in test_pairs:
        # Simulate what post-Gemini guardrail in coordinator does:
        # Assume Gemini returned "match"
        status = "match"
        
        # 1. Strength check
        str_r = get_strength_pattern(req)
        str_w = get_strength_pattern(cand)
        if str_r and str_w:
            try:
                if float(str_r) != float(str_w):
                    status = "no_match"
            except:
                if str_r != str_w:
                    status = "no_match"
                    
        # 2. Combination suffix mismatch
        if has_co(req) != has_co(cand):
            status = "no_match"
            
        # 3. Commercial prefix mismatch (commented out)
        # is_r_neo = 'نيو' in req or 'new' in req.lower()
        # is_w_neo = 'نيو' in cand or 'new' in cand.lower()
        # if is_r_neo != is_w_neo:
        #     status = "no_match"
            
        # 4. Brand family check
        req_b = extract_brand_tokens(req)
        wh_b = extract_brand_tokens(cand)
        if req_b and wh_b:
            words_r = req_b.split()
            words_w = wh_b.split()
            first_r = words_r[0] if words_r else ""
            first_w = words_w[0] if words_w else ""
            
            if (first_r in BRAND_FAMILIES or first_w in BRAND_FAMILIES):
                fam_sim = max(fuzz.ratio(req_b, wh_b), fuzz.token_set_ratio(req_b, wh_b))
                if fam_sim < 80:
                    status = "no_match"
                    
        # 5. Dosage form check
        if status == "match":
            form_r = extract_form_group(req)
            wh_form = extract_form_group(cand)
            is_r_drops = 'نقط' in req or 'قطره' in req or 'قطرة' in req
            is_wh_drops = 'نقط' in cand or 'قطره' in cand or 'قطرة' in cand
            is_r_syrup = bool(('شراب' in req) or ('شرب' in req) or ('معلق' in req))
            is_wh_syrup = bool(('شراب' in cand) or ('شرب' in cand) or ('معلق' in cand))
            
            if form_r and wh_form and form_r != wh_form:
                status = "review"
            elif is_r_drops != is_wh_drops or is_r_syrup != is_wh_syrup:
                status = "review"
                
        print(f"Req: '{req}'")
        print(f"Cand: '{cand}'")
        print(f"Note: {note}")
        print(f"--> Post-Gemini status: {status.upper()}\n")

def test_summary_sync():
    print("=" * 70)
    print("2. TESTING SUMMARY REVIEW_COUNT CALCULATION")
    print("=" * 70)
    
    # Simulate warehouse results where 2 items are in review in WH1, but 1 of them was matched in WH2
    # and 3 items are in review in WH3, one duplicate with WH1
    shortage_items = [
        {"item_name_raw": "دواء أ"},
        {"item_name_raw": "دواء ب"},
        {"item_name_raw": "دواء ج"},
        {"item_name_raw": "دواء د"},
        {"item_name_raw": "دواء هـ"},
    ]
    deduped_shortages = shortage_items
    all_shortage_names = {item["item_name_raw"] for item in deduped_shortages}
    
    # Warehouse 1: matched "دواء أ", review "دواء ب" and "دواء ج"
    # Warehouse 2: matched "دواء ب", review "دواء ج"
    all_warehouse_results = {
        "مخزن 1": {
            "matched": [{"shortage_item": "دواء أ", "warehouse_item": "دواء أ مخزن 1"}],
            "needs_review": [
                {"shortage_item": "دواء ب", "warehouse_item": "دواء ب شراب"},
                {"shortage_item": "دواء ج", "warehouse_item": "دواء ج شراب"},
            ]
        },
        "مخزن 2": {
            "matched": [{"shortage_item": "دواء ب", "warehouse_item": "دواء ب أقراص"}],
            "needs_review": [
                {"shortage_item": "دواء ج", "warehouse_item": "دواء ج شراب"},
                {"shortage_item": "دواء د", "warehouse_item": "دواء د شراب"},
            ]
        }
    }
    
    found_in = {"دواء أ": ["مخزن 1"], "دواء ب": ["مخزن 2"]}
    found_names = set(found_in.keys())
    
    # Run the new deduplicated logic:
    actual_review_items = []
    seen_review_pairs = set()
    for wh_name, wh_result in all_warehouse_results.items():
        for rev in wh_result["needs_review"]:
            req_item = rev.get("shortage_item", "").strip()
            wh_item = rev.get("warehouse_item", "").strip()
            if req_item in found_names:
                continue
            pair_key = (req_item, wh_item, wh_name)
            if pair_key in seen_review_pairs:
                continue
            seen_review_pairs.add(pair_key)
            actual_review_items.append(rev)

    review_only_names = {rev["shortage_item"].strip() for rev in actual_review_items}
    not_found_names = all_shortage_names - found_names - review_only_names
    
    total_wh_matched = sum(len(wh["matched"]) for wh in all_warehouse_results.values())
    total_review_items = len(actual_review_items)
    total_not_found = len(not_found_names)
    
    summary = {
        "total_shortages": len(shortage_items),
        "unique_shortages": len(deduped_shortages),
        "matched_count": total_wh_matched,
        "not_found_count": total_not_found,
        "review_count": total_review_items,
    }
    
    print(f"Matched count: {total_wh_matched} (2 matches across warehouses)")
    print(f"Raw review sum across warehouses would have been: 4")
    print(f"Deduplicated review_count: {summary['review_count']} (expected: 2 -> دواء ج in WH1 and WH2 is 2 rows, or distinct shortage items)")
    print(f"Not found: {not_found_names} (expected: 1 -> دواء هـ)")
    print(f"Summary dict: {summary}")

if __name__ == "__main__":
    test_guardrails_unit()
    test_summary_sync()
