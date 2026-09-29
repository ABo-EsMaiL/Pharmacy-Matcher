import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))
from src.match.text_match import normalize_text
from rapidfuzz import fuzz

PHARMA_STOPWORDS = {
    # forms
    'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'شراب', 'شرب', 'مرهم', 'كريم', 
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
    # Separate numbers from text: e.g. "ماريفان3مجم" -> "ماريفان 3 مجم"
    text = re.sub(r'(\d+)', r' \1 ', text)
    norm = normalize_text(text)
    # Remove slash company: /جلاكسو or /فاركو
    norm = re.sub(r'/.*', '', norm)
    # Filter stopwords and numbers
    words = [w for w in norm.split() if w not in PHARMA_STOPWORDS and not w.isdigit() and len(w) > 1]
    return " ".join(words)

# Test on true matches
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

print("=== TRUE MATCHES BRAND EXTRACTION & SIMILARITY ===")
for req, wh in matches:
    b_req = extract_brand_tokens(req)
    b_wh = extract_brand_tokens(wh)
    f_req = extract_form_group(req)
    f_wh = extract_form_group(wh)
    sim = max(fuzz.ratio(b_req, b_wh), fuzz.token_sort_ratio(b_req, b_wh))
    print(f"Req: '{b_req}' ({f_req})  vs  WH: '{b_wh}' ({f_wh})  -> Sim: {sim:.0f}%")

print("\n=== FALSE MATCHES ===")
false_pairs = [
    ('كونفاجران100مجم30قرص', 'فياجرا ١٠٠ مجم - قرص'),
    ('انتودين 20مجم30قرص س ج', 'فاستلام ٢٠مجم'),
    ('ميبو مرهم 15جم صغير س ج', 'برناسورس مرهم ١٥ جرام'),
    ('دولفين 50مجم لبوس 2شريط', 'اندوميثاسين لبوس العربيه'),
    ('سيتال1جم اقراص س ج', 'سيتال شراب قديم'),
    ('جينوزول كريم س ج', 'جينوزول ٤٠٠ مجم لبوس جديد')
]

for req, wh in false_pairs:
    b_req = extract_brand_tokens(req)
    b_wh = extract_brand_tokens(wh)
    f_req = extract_form_group(req)
    f_wh = extract_form_group(wh)
    sim = max(fuzz.ratio(b_req, b_wh), fuzz.token_sort_ratio(b_req, b_wh))
    form_conflict = (f_req is not None and f_wh is not None and f_req != f_wh)
    print(f"Req: '{b_req}' ({f_req}) vs WH: '{b_wh}' ({f_wh}) -> Sim: {sim:.0f}% | Form Conflict: {form_conflict}")
