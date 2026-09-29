import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

import re
import json
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder
from src.match.text_match import normalize_text
from rapidfuzz import fuzz

PHARMA_STOPWORDS = {
    # forms
    'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'شراب', 'شرب', 'معلق', 'سائل', 'مرهم', 'كريم', 
    'جل', 'جيل', 'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال', 'لبوس', 'لبوسة', 'لبوسه',
    'نقط', 'قطرة', 'قطره', 'بخاخ', 'بخاخة', 'بخاخه', 'سبراي', 'فوار', 'اكياس', 'كيس',
    'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه', 'محلول', 'مس', 'دهان', 'فيلم',
    # units & numbers
    'مجم', 'جم', 'جرام', 'مل', 'مللي', 'لتر', 'ميكرو', 'شريط', 'علبه', 'علبة',
    'باكت', 'باكو', 'كرتونه', 'كرتونة', 'فلتر',
    # trade metadata
    'س', 'ج', 'سعر', 'جديد', 'قديم', 'تاريخ', 'بعيد', 'قريب', 'صغير', 'كبير', 'وسط',
    'محلي', 'مستورد', 'خاص', 'نقدى', 'اجل'
}

FORM_GROUPS = {
    'tablet': {'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'حبوب', 'فيلم'},
    'syrup': {'شراب', 'شرب', 'معلق', 'سائل'},
    'cream_ointment': {'كريم', 'مرهم', 'دهان'},
    'gel': {'جل', 'جيل'},
    'suppository': {'لبوس', 'لبوسه', 'لبوسة', 'تحاميل', 'اقماع'},
    'injection': {'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال'},
    'drops': {'نقط', 'قطرة', 'قطره'},
    'spray': {'بخاخ', 'بخاخة', 'بخاخه', 'سبراي'},
    'sachet': {'فوار', 'اكياس', 'كيس'},
    'wash': {'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه'},
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

shortages_raw = extract_item_names(read_excel(Path(r'data/processes/PROC-001/input_shortages/0913.xlsx')))
unique_shortages = {}
for s in shortages_raw:
    n = s.get("item_name_raw", "")
    if n and n not in unique_shortages:
        unique_shortages[n] = s
shortage_names = list(unique_shortages.keys())

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/السلام شبين.pdf'), api_key="")
wh_input = [{"id": f"wh_{i}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]

finder = FastCandidateFinder()
finder.fit(wh_input)

true_matches = {
    'ماريفان3مجم3شريط س ج': 'ماريفان ٣ مجم/جلاكسو',
    'ديوراسيف  250مجم شراب س ج': 'ديوراسيف ٢٥٠ شراب/سكويب',
    'ديكساتوبرين مرهم س ج': 'ديكسا توبيرين مرهم/ايكو',
    'رانديل10مجم اقراص': 'رانديل ١٠ مجم',
    'بيتادين  مطهر النيل 60مل صغير س ج': 'بيتادين مطهر/النيل',
    'نيتروماك ريتارد2.5مجم كبسول': 'نيتروماك ريتارد كبسول/التنشيط',
    'ديجستين 20قرص س ج': 'ديجستين اقراص/فاركو',
    'ايفاستين اقراص2 شريط س ج': 'ايفاستين اقراص/ايفا فارم',
    'ادولور 30مجم 3امبول': 'ادولور - ٣٠مجم/٢ مللي ٣ امبول',
    'كوللوماك محلول س ج': 'كولومالك مس',
    'برونشيكم شراب س ج': 'برونشيكم شراب الكيسير/افنتس',
    'جوسبرين اقراص 3شريط': 'جوسبرين اقراص/اجفار',
    'سيديبروكت كريم س ج': 'سيديبروك كريم/المهن',
    'كلوسول سبراي س ج': 'كولوسول بخاخة/الاوروبيه',
    'برايم روز بلاس اقراص': 'برايم روز بلاس اقراص/ايفافارم',
    'توب جنج ادفانس30كبسوله س ج': 'توب جينج كبسول/ماش',
    'كيتولاك 5 امبوله': 'كيتولاك امبول/العامريه',
    'سبازموفري امبول': 'سبازموفري ٣امبول/ادوبا'
}

candidates_for_llm = {}
missed_true_matches = []

for req in shortage_names:
    raw_cands = finder.search(req, top_k=8)
    req_brand = extract_brand_tokens(req)
    req_form = extract_form_group(req)
    
    valid_cands = []
    for c in raw_cands:
        cand_name = c["name"]
        cand_brand = extract_brand_tokens(cand_name)
        cand_form = extract_form_group(cand_name)
        
        # 1. Dosage form conflict check
        if req_form and cand_form and req_form != cand_form:
            continue
            
        # 2. Brand similarity check
        brand_ratio = fuzz.ratio(req_brand, cand_brand)
        token_set = fuzz.token_set_ratio(req_brand, cand_brand)
        max_sim = max(brand_ratio, token_set)
        
        # If both have brand names, we require at least 50% brand similarity OR high TF-IDF
        if (req_brand and cand_brand and max_sim >= 50) or c["score"] >= 0.40:
            valid_cands.append({
                "id": c["id"],
                "name": cand_name,
                "score": c["score"],
                "brand_sim": max_sim
            })
            
    if valid_cands:
        candidates_for_llm[req] = valid_cands
        
    if req in true_matches:
        expected = true_matches[req]
        if not any(c["name"] == expected for c in valid_cands):
            missed_true_matches.append((req, expected, [c["name"] for c in valid_cands]))

print(f"\n==========================================")
print(f"Total unique shortages: {len(shortage_names)}")
print(f"Shortages sent to LLM: {len(candidates_for_llm)} (was 567 in old logic!)")
print(f"Missed true matches: {len(missed_true_matches)}")
if missed_true_matches:
    for m in missed_true_matches:
        print("  MISSED:", m)

print("\nSample 15 items sent to LLM:")
for i, (req, cands) in enumerate(list(candidates_for_llm.items())[:15]):
    b_req = extract_brand_tokens(req)
    cand_strs = [f"'{c['name']}' (sim={c['brand_sim']}%, tfidf={c['score']:.2f})" for c in cands]
    print(f"{i+1:2d}. '{req}' [Brand: '{b_req}']")
    for cs in cand_strs:
        print(f"    -> {cs}")

