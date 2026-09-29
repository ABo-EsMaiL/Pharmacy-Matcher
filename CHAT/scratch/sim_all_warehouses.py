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

wh_files = [
    'السلام شبين.pdf',
    'كيور فارما خاص.pdf',
    'جملة العمروووو.pdf',
    'المكرومي المنصورة.pdf',
    'مخزن الحياة فارم اسكندريه-170.pdf',
    'الهضبة الاثنين نقدى0.pdf'
]

print(f"Total Unique Shortages: {len(shortage_names)}")
print("="*75)

for wh_name in wh_files:
    pdf_path = Path(r'data/processes/PROC-001/input_warehouses') / wh_name
    wh_items = extract_items_from_pdf(pdf_path, api_key="")
    wh_input = [{"id": f"wh_{i}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]
    
    finder = FastCandidateFinder()
    finder.fit(wh_input)
    
    cands_for_llm = 0
    for req in shortage_names:
        raw_cands = finder.search(req, top_k=6)
        req_brand = extract_brand_tokens(req)
        req_form = extract_form_group(req)
        
        valid = []
        for c in raw_cands:
            cand_name = c["name"]
            cand_brand = extract_brand_tokens(cand_name)
            cand_form = extract_form_group(cand_name)
            
            # Form check
            if req_form and cand_form and req_form != cand_form:
                continue
                
            # Brand check
            if len(req_brand.split()) > 1 or len(cand_brand.split()) > 1:
                sim = fuzz.token_sort_ratio(req_brand, cand_brand)
            else:
                sim = fuzz.ratio(req_brand, cand_brand)
                
            if req_brand and cand_brand:
                if req_brand.startswith(cand_brand) or cand_brand.startswith(req_brand):
                    sim = max(sim, 80)
                    
            if sim >= 60 or c["score"] >= 0.50:
                valid.append(cand_name)
                
        if valid:
            cands_for_llm += 1
            
    print(f"Warehouse: {wh_name:32s} | Items: {len(wh_items):4d} | Sent to LLM: {cands_for_llm:3d} (was ~580!)")
