import json
import requests
import sys

sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.coordinator import (
    FastCoordinator, SYSTEM_PROMPT, BRAND_FAMILIES, extract_brand_tokens, extract_form_group
)
from src.config import Config
from rapidfuzz import fuzz

API_URL = "http://127.0.0.1:8001/v1/chat/completions"
API_KEY = "[REDACTED_CREDENTIAL]"

def main():
    test_cases = [
        {
            "case_id": "TEST-NEURO-1",
            "requested_name": "نيوروفيت اقراص  3 شريط",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-01", "name": "نيروفيت اقراص سعر جديد"}]
        },
        {
            "case_id": "TEST-NEURO-2",
            "requested_name": "نيوروفيت اقراص  3 شريط",
            "catalog_id": "W2",
            "candidates": [{"id": "W2-01", "name": "نیروپفیت اقراص/باكت 15"}]
        },
        {
            "case_id": "TEST-TRYPT",
            "requested_name": "تربتيزول10 مجم اقراص",
            "catalog_id": "W2",
            "candidates": [{"id": "W2-02", "name": "تریپتازول 10 مج اقراس/باکت 200"}]
        },
        {
            "case_id": "TEST-PARSLEY",
            "requested_name": "بقدونس وكرفس ايزيس",
            "catalog_id": "W2",
            "candidates": [{"id": "W2-03", "name": "ایزیز بقدونس وکرکس 20 فلتر"}]
        },
        {
            "case_id": "TEST-SKINOREN",
            "requested_name": "سكينورين كريم",
            "catalog_id": "W2",
            "candidates": [{"id": "W2-04", "name": "سکینوریتش کریم"}]
        },
        {
            "case_id": "TEST-CARNIVITA",
            "requested_name": "كارنيفيتا ادفانس للرجال30كيس س ج",
            "catalog_id": "W3",
            "candidates": [{"id": "W3-01", "name": "کارنتینا ادفانس رجال/باکت16"}]
        },
        {
            "case_id": "TEST-CHROMAX",
            "requested_name": "ليمتلس كروماكس كت30كيس س ج",
            "catalog_id": "W2",
            "candidates": [{"id": "W2-05", "name": "يمتليس كروماتكس كت 30 كيس جديد"}]
        },
        {
            "case_id": "TEST-NEOCARBON",
            "requested_name": "نيوكاربون30قرص س ج",
            "catalog_id": "W4",
            "candidates": [{"id": "W4-01", "name": "نیوکاربن ۳۰کپسول"}]
        },
        {
            "case_id": "TEST-HERO",
            "requested_name": "لبن هيرو بيبي 2",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-02", "name": "هيرو بيبي ٢"}]
        }
    ]

    cfg = Config(unstructured_api_key="dummy", gemini_api_key="dummy")
    cfg.local_api_url = API_URL
    cfg.local_api_key = API_KEY
    cfg.local_model = "gemini-3.8-flash"
    coord = FastCoordinator(cfg)

    print("=" * 80)
    print("SENDING AMBIGUOUS CASES DIRECTLY TO GEMINI VIA LOCAL API")
    print("=" * 80)

    raw_results = coord._call_local_api({"cases": test_cases})
    print(f"Received {len(raw_results)} results from Gemini:\n")

    for case, dec in zip(test_cases, raw_results):
        cid = case["case_id"]
        req = case["requested_name"]
        cand = case["candidates"][0]["name"]
        st = dec.get("status")
        item_id = dec.get("item_id")
        reason = dec.get("reason", "")
        
        print(f"[{cid}] Shortage: '{req}' vs Candidate: '{cand}'")
        print(f"       -> Gemini returned: status='{st}', item_id='{item_id}', reason='{reason}'")
        
        # Test guardrail on this decision:
        req_b = extract_brand_tokens(req)
        wh_b = extract_brand_tokens(cand)
        words_r = req_b.split() if req_b else []
        words_w = wh_b.split() if wh_b else []
        first_r = words_r[0] if words_r else ""
        first_w = words_w[0] if words_w else ""
        
        r_clean = first_r[2:] if first_r.startswith('ال') else first_r
        w_clean = first_w[2:] if first_w.startswith('ال') else first_w
        confusables = {'ب', 'ت', 'ث', 'ن', 'ي'}
        
        letter_check_failed = False
        if r_clean and w_clean and r_clean[0] != w_clean[0]:
            if not (r_clean[0] in confusables and w_clean[0] in confusables):
                letter_check_failed = True
                
        b_sim = max(
            fuzz.ratio(req_b, wh_b),
            fuzz.token_sort_ratio(req_b, wh_b),
            fuzz.ratio(req_b.replace(' ', ''), wh_b.replace(' ', ''))
        ) if req_b and wh_b else 0
        if first_r and first_w and (first_r == first_w or fuzz.ratio(first_r, first_w) >= 85):
            b_sim = max(b_sim, 85)
            
        guardrail_st = st
        override_reason = ""
        if (first_r in BRAND_FAMILIES or first_w in BRAND_FAMILIES) and fuzz.ratio(req_b, wh_b) < 80:
            guardrail_st = "no_match"
            override_reason = "brand_family_override"
        elif letter_check_failed:
            guardrail_st = "no_match"
            override_reason = f"first_letter_mismatch ({r_clean[0]} vs {w_clean[0]})"
        elif b_sim < 72:
            guardrail_st = "no_match"
            override_reason = f"b_sim_too_low ({b_sim:.1f} < 72)"
            
        print(f"       -> Guardrail result: status='{guardrail_st}' (Override: {override_reason if override_reason else 'NONE'})\n")

if __name__ == "__main__":
    main()
