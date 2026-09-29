import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from rapidfuzz import fuzz
from src.fast_match.search import extract_brand_tokens

req = "ميبو مرهم 15جم صغير س ج"
cand = "ميو صغير"
b1 = extract_brand_tokens(req)
b2 = extract_brand_tokens(cand)
print(f"'{b1}' vs '{b2}' -> ratio: {fuzz.ratio(b1, b2)}")
