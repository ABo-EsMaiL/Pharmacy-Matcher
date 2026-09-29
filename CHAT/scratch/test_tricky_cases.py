import sys
sys.path.insert(0, ".")
from src.fast_match.coordinator import is_safe_auto_match
from src.fast_match.search import extract_brand_tokens

tests = [
    ('سينوبريت اقراص', 'سينوبريل 2 مجم اقراص/باکت 90'),
    ('ديوزمين 30 قرص', 'ديبوزين 500مجم اقراص'),
    ('فيتا زنك  كبسول', 'فیتا زون قرص قدیم'),
    ('سيتال1جم اقراص س ج', 'سيتال اقراص 500 س ج'),
    ('كتافلام  نقط', 'كتافلام ٥٠ س.ج ٨٦ج'),
    ('الكابرس تريو5/160/12.5مجم س ج', 'الكابرس تربو ١٠/١٦/١٢٤٠ قرص'),
]

for req, cand in tests:
    res, reason = is_safe_auto_match(req, cand)
    b_r = extract_brand_tokens(req)
    b_c = extract_brand_tokens(cand)
    print(f"'{req}' vs '{cand}':")
    print(f"  Brand: '{b_r}' vs '{b_c}'")
    print(f"  Result: {res}, Reason: {reason}\n")
