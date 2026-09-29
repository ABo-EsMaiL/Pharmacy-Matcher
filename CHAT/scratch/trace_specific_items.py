import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")

from src.match.text_match import normalize_text, find_candidates
from src.fast_match.search import FastCandidateFinder
from src.fast_match.coordinator import (
    classify_pair, extract_strength, extract_brand_tokens, extract_form_group
)
from rapidfuzz import fuzz

# Trace items
items_to_trace = [
    ("لبن هيرو بيبي 2", "هيرو بيبي ٢", "المكرومي المنصورة.pdf"),
    ("نيوروفيت اقراص  3 شريط", "نيروفيت اقراص سعر جديد", "المكرومي المنصورة.pdf"),
    ("نيوروفيت اقراص  3 شريط", "نیروپفیت اقراص/باكت 15", "الهضبة الاثنين نقدى0.pdf"),
    ("تربتيزول10 مجم اقراص", "تریپتازول 10 مج اقراس/باکت 200", "الهضبة الاثنين نقدى0.pdf"),
    ("بقدونس وكرفس ايزيس", "ایزیز بقدونس وکرکس 20 فلتر", "الهضبة الاثنين نقدى0.pdf"),
    ("ينسون ايزيس س ج", "زيس ينسون 12 فلتر صغير ج/باكو 6", "الهضبة الاثنين نقدى0.pdf"),
    ("تورسامولكس10مجم اقراص س ج", "تورساموکس ۱۰ جم اقراص", "كيور فارما خاص.pdf"),
    ("سكينورين كريم", "سکینوریتش کریم", "الهضبة الاثنين نقدى0.pdf"),
    ("ابيفيناك قطرة س ج", "ابيفيناك حقن", "كيور فارما خاص.pdf"),
    ("كارنيفيتا ادفانس للرجال30كيس س ج", "کارنتینا ادفانس رجال/باکت16", "مخزن الحياة فارم اسكندريه-170.pdf"),
    ("ليمتلس كروماكس كت30كيس س ج", "يمتليس كروماتكس كت 30 كيس جديد", "الهضبة الاثنين نقدى0.pdf"),
    ("نيوكاربون30قرص س ج", "نیوکاربن ۳۰کپسول", "كيور فارما خاص.pdf")
]

def main():
    print("=" * 80)
    print("TRACING PIPELINE STAGES FOR SUSPICIOUS ITEMS")
    print("=" * 80)
    
    for shortage, wh_item, wh_file in items_to_trace:
        print(f"\n[Shortage]: '{shortage}'")
        print(f"[WH Item ]: '{wh_item}' (in {wh_file})")
        
        # 1. Normalization
        ns = normalize_text(shortage)
        nw = normalize_text(wh_item)
        print(f"  -> Normalized Shortage: '{ns}'")
        print(f"  -> Normalized WH:       '{nw}'")
        
        # 2. classify_pair (Deterministic check)
        status, reason = classify_pair(shortage, wh_item)
        print(f"  -> classify_pair() Status: {status} | Reason: {reason}")
        
        # 3. Brand tokens & similarity
        req_b = extract_brand_tokens(shortage)
        wh_b = extract_brand_tokens(wh_item)
        b_sim = max(
            fuzz.ratio(req_b, wh_b),
            fuzz.token_sort_ratio(req_b, wh_b),
            fuzz.ratio(req_b.replace(' ', ''), wh_b.replace(' ', ''))
        )
        print(f"  -> Brand Tokens: '{req_b}' vs '{wh_b}' | Brand Sim: {b_sim}")
        
        # 4. Strength check
        s_req = extract_strength(shortage)
        s_wh = extract_strength(wh_item)
        print(f"  -> Strengths: Shortage='{s_req}' | WH='{s_wh}'")
        
        # 5. Form check
        f_req = extract_form_group(shortage)
        f_wh = extract_form_group(wh_item)
        print(f"  -> Form Groups: Shortage='{f_req}' | WH='{f_wh}'")

if __name__ == "__main__":
    main()
