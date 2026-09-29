import sys
sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")

from src.fast_match.search import extract_brand_tokens
from rapidfuzz import fuzz

pairs = [
    ('جرانتريل', 'جرانتيل'),
    ('امبوفير', 'اميفير'),
    ('ديباكين 500', 'ديبيكان 500'),
    ('اولفن 100 اس ار', 'البيران اس ار')
]
for r, w in pairs:
    rb = extract_brand_tokens(r)
    wb = extract_brand_tokens(w)
    sim = fuzz.ratio(rb, wb)
    print(f"'{r}' ({rb}) vs '{w}' ({wb}) -> sim: {sim}")
