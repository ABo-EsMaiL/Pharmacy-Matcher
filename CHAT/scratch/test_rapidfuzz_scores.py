import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))
from rapidfuzz import fuzz
from src.match.text_match import normalize_text

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

for req, wh in matches:
    n_req = normalize_text(req)
    n_wh = normalize_text(wh)
    ratio = fuzz.ratio(n_req, n_wh)
    token_sort = fuzz.token_sort_ratio(n_req, n_wh)
    token_set = fuzz.token_set_ratio(n_req, n_wh)
    # first word ratio
    first_req = n_req.split()[0] if n_req.split() else ""
    first_wh = n_wh.split()[0] if n_wh.split() else ""
    first_ratio = fuzz.ratio(first_req, first_wh)
    print(f"{first_req:12s} vs {first_wh:12s} -> 1st_word: {first_ratio:.0f} | token_set: {token_set:.0f} | token_sort: {token_sort:.0f}")
