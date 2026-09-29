import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import extract_brand_tokens
from rapidfuzz import fuzz

req = "ديكساتوبرين مرهم س ج"
cand = "ديكسا توبيرين مرهم/ايكو"

rb = extract_brand_tokens(req)
wb = extract_brand_tokens(cand)

print("req brand:", rb)
print("wh brand:", wb)
print("fuzz ratio:", fuzz.ratio(rb, wb))
print("token sort:", fuzz.token_sort_ratio(rb, wb))
words_r = rb.split()
words_w = wb.split()
first_r = words_r[0] if words_r else ""
first_w = words_w[0] if words_w else ""
print("first_r:", first_r, "first_w:", first_w)
print("first ratio:", fuzz.ratio(first_r, first_w))
