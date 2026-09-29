import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from rapidfuzz import fuzz
from src.match.text_match import normalize_text
from src.fast_match.search import extract_brand_tokens, extract_form_group

pairs = [
    ("اولفن100مجم اس ار10كبسول س ج", "البيران اس ار اقراص / باكت 10"),
    ("زانوجليد4/30اقراص س ج", "زانوچيلد 4 مج اقراص/باكت 60"),
    ("امبوفير 5امبول س ج", "اميفير امبول"),
    ("جرانتريل 3مجم 6 امبول س ج", "جرانتيل امبول مجم تاريخ بعيد"),
    ("ديباكين كرونو500مجم اقراص", "ديبيكان اقراص/العامرية"),
    ("نيوكاربون30قرص س ج", "نیوکاربن ۳۰کپسول"),
    ("ليفانوكس2شريط س ج", "ليفانوكس كبسول/باكت 200"),
    ("لانتانون30مجم 10كبسوله س ج", "لاتانون کپسول"),
]

for req, cand in pairs:
    b1 = extract_brand_tokens(req)
    b2 = extract_brand_tokens(cand)
    f1 = extract_form_group(req)
    f2 = extract_form_group(cand)
    sim = fuzz.ratio(b1, b2)
    print(f"Req: '{req}' (brand='{b1}', form='{f1}')")
    print(f"Cand: '{cand}' (brand='{b2}', form='{f2}')")
    print(f"Brand sim: {sim}%")
    print("-" * 50)
