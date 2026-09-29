import json
import os
import openpyxl
import re
from rapidfuzz import fuzz

import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.match.text_match import normalize_text
from src.fast_match.search import FastCandidateFinder
from src.fast_match.coordinator import (
    classify_pair, norm_num, get_strength_pattern, has_co, are_forms_identical,
    extract_form_group, extract_brand_tokens, BRAND_FAMILIES
)
from src.extract.file_handler import read_input_files

def main():
    settings_path = r"D:\AI_Engineer\Pharmacy-agy\data\settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    api_key = settings.get("unstructured_api_key")

    wh_dir = r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\input_warehouses"
    wh_files = [os.path.join(wh_dir, f) for f in os.listdir(wh_dir) if f.endswith('.pdf')]
    wh_data = read_input_files(wh_files, role='warehouse', api_key=api_key)

    # Let's check each suspicious item:
    targets = [
        ("لبن هيرو بيبي 2", "المكرومي المنصورة.pdf"),
        ("نيوروفيت اقراص  3 شريط", "المكرومي المنصورة.pdf"),
        ("نيوروفيت اقراص  3 شريط", "الهضبة الاثنين نقدى0.pdf"),
        ("تربتيزول10 مجم اقراص", "الهضبة الاثنين نقدى0.pdf"),
        ("بقدونس وكرفس ايزيس", "الهضبة الاثنين نقدى0.pdf"),
        ("ينسون ايزيس س ج", "الهضبة الاثنين نقدى0.pdf"),
        ("تورسامولكس10مجم اقراص س ج", "كيور فارما خاص.pdf"),
        ("سكينورين كريم", "الهضبة الاثنين نقدى0.pdf"),
        ("ابيفيناك قطرة س ج", "كيور فارما خاص.pdf"),
        ("كارنيفيتا ادفانس للرجال30كيس س ج", "مخزن الحياة فارم اسكندريه-170.pdf"),
        ("ليمتلس كروماكس كت30كيس س ج", "الهضبة الاثنين نقدى0.pdf"),
        ("نيوكاربون30قرص س ج", "كيور فارما خاص.pdf")
    ]

    print("=" * 80)
    print("SIMULATING CANDIDATE RETRIEVAL & CLASSIFICATION")
    print("=" * 80)

    for shortage, wh_file in targets:
        items = wh_data.get(wh_file) or wh_data.get(os.path.join(wh_dir, wh_file), [])
        wh_catalog = [{"id": f"W-{i:05}", "name": it.get("item_name_raw", "")} for i, it in enumerate(items)]
        
        finder = FastCandidateFinder()
        finder.fit(wh_catalog)
        
        cands = finder.search(shortage, top_k=10)
        print(f"\nShortage: '{shortage}' -> Warehouse: [{wh_file}]")
        print(f"  Top candidates found ({len(cands)}):")
        for rank, c in enumerate(cands, 1):
            st, reason = classify_pair(shortage, c['name'])
            # Check guardrails
            req_b = extract_brand_tokens(shortage)
            wh_b = extract_brand_tokens(c['name'])
            b_sim = max(
                fuzz.ratio(req_b, wh_b),
                fuzz.token_sort_ratio(req_b, wh_b),
                fuzz.ratio(req_b.replace(' ', ''), wh_b.replace(' ', ''))
            ) if req_b and wh_b else 0
            
            print(f"    {rank}. [Score: {c.get('score', 0):.2f}] '{c['name']}' => Status: {st} ({reason}) | BrandSim: {b_sim:.1f}")

if __name__ == "__main__":
    main()
