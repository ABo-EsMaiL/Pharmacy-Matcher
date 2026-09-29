import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from src.fast_match.search import extract_brand_tokens
from rapidfuzz import fuzz

req = 'لاكتيز 15 ملل نقط 750مجم'
cand = 'لاكتيز نقط بالفم ٥ مل ١٩٠'
b1 = extract_brand_tokens(req)
b2 = extract_brand_tokens(cand)
print('b1:', b1)
print('b2:', b2)
print('fuzz ratio:', fuzz.ratio(b1, b2))
print('fuzz token sort:', fuzz.token_sort_ratio(b1, b2))
