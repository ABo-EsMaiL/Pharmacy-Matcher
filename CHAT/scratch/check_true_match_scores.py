import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

import json
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder, normalize_for_search

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/السلام شبين.pdf'), api_key="")
wh_input = [{"id": f"wh_{i}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]

finder = FastCandidateFinder()
finder.fit(wh_input)

# The 19 true matches from earlier:
matches = [
    ('ماريفان3مجم3شريط س ج', 'ماريفان ٣ مجم/جلاكسو'),
    ('ديوراسيف  250مجم شراب س ج', 'ديوراسيف ٢٥٠ شراب/سكويب'),
    ('ديكساتوبرين مرهم س ج', 'ديكسا توبيرين مرهم/ايكو'),
    ('رانديل10مجم اقراص', 'رانديل ١٠ مجم'),
    ('بيتادين  مطهر النيل 60مل صغير س ج', 'بيتادين مطهر/النيل'),
    ('نيتروماك ريتارد2.5مجم كبسول', 'نيتروماك ريتارد كبسول/التنشيط'),
    ('ديجستين 20قرص س ج', 'ديجستين اقراص/فاركو'),
    ('ايفاستين اقراص2 شريط س ج', 'ايفاستين اقراص/ايفا فارم'),
    ('ادولور 30مجم 3امبول', 'ادولور - ٣٠مجم/٢ مللي ٣ امبول'),
    ('كوللوماك محلول س ج', 'كولومالك مس'),
    ('برونشيكم شراب س ج', 'برونشيكم شراب الكيسير/افنتس'),
    ('جوسبرين اقراص 3شريط', 'جوسبرين اقراص/اجفار'),
    ('سيديبروكت كريم س ج', 'سيديبروك كريم/المهن'),
    ('كلوسول سبراي س ج', 'كولوسول بخاخة/الاوروبيه'),
    ('برايم روز بلاس اقراص', 'برايم روز بلاس اقراص/ايفافارم'),
    ('توب جنج ادفانس30كبسوله س ج', 'توب جينج كبسول/ماش'),
    ('كيتولاك 5 امبوله', 'كيتولاك امبول/العامريه'),
    ('سبازموفري امبول', 'سبازموفري ٣امبول/ادوبا')
]

print("=== SCORES OF TRUE MATCHES ===")
min_score = 1.0
for req, wh in matches:
    cands = finder.search(req, top_k=10)
    found_score = None
    rank = None
    for r, c in enumerate(cands, 1):
        if normalize_for_search(c["name"]) == normalize_for_search(wh) or c["name"] == wh:
            found_score = c["score"]
            rank = r
            break
    if found_score is not None:
        min_score = min(min_score, found_score)
        print(f"Match: {req[:25]:25s} -> {wh[:25]:25s} | Rank: {rank} | Score: {found_score:.3f}")
    else:
        print(f"NOT FOUND: {req} -> {wh}")
        print("  Top candidates was:")
        for c in cands[:3]:
            print(f"    {c['name']} ({c['score']:.3f})")

print(f"\nMinimum score among all true matches: {min_score:.3f}")
