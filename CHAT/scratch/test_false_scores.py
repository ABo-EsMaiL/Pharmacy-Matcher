import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))
from rapidfuzz import fuzz
from src.match.text_match import normalize_text
import re

false_matches = [
    ('كونفاجران100مجم30قرص', 'فياجرا ١٠٠ مجم - قرص'),
    ('انتودين 20مجم30قرص س ج', 'فاستلام ٢٠مجم'),
    ('ميبو مرهم 15جم صغير س ج', 'برناسورس مرهم ١٥ جرام'),
    ('دولفين 50مجم لبوس 2شريط', 'اندوميثاسين لبوس العربيه'),
    ('نويوريك300مجم اقراص س ج', 'دالاسين سي ٣٠٠مجم'),
    ('سينوبريت اقراص', 'سينوبريل 2 مجم اقراص/باكت 90'),
    ('ب ك ميرز كبسول س ج', 'ميرز كبسول/باكت 30'),
    ('ابيكوتيل  5لبوسة ث', 'البوتيل بوس س.ج،٣٤ج'),
    ('سيتال1جم اقراص س ج', 'سيتال شراب قديم'),
    ('جينوزول كريم س ج', 'جينوزول ٤٠٠ مجم لبوس جديد')
]

def clean_brand(text):
    # space numbers
    text = re.sub(r'(\d+)', r' \1 ', text)
    norm = normalize_text(text)
    # remove common pharmaceutical words
    stop_words = {'اقراص', 'كبسول', 'كبسولات', 'شراب', 'مرهم', 'كريم', 'جل', 'جيل', 'امبول', 'امبولات', 'لبوس', 'نقط', 'بخاخ', 'فوار', 'س', 'ج', 'سعر', 'جديد', 'قديم', 'شريط', 'قرص', 'مل', 'مجم', 'جم', 'جرام', 'باكت', 'علبه', 'باكو'}
    tokens = [w for w in norm.split() if w not in stop_words and not w.isdigit()]
    return " ".join(tokens)

for req, wh in false_matches:
    b_req = clean_brand(req)
    b_wh = clean_brand(wh)
    ratio = fuzz.ratio(b_req, b_wh)
    token_set = fuzz.token_set_ratio(b_req, b_wh)
    print(f"'{b_req}' vs '{b_wh}' -> Brand Ratio: {ratio:.0f} | Token Set: {token_set:.0f}")
