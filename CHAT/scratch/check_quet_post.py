import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import extract_brand_tokens
from rapidfuzz import fuzz

req = "كويتابين 25مجم 30قرص س ج"
cand = "کوتیاپین 25 مج اقراص"

rb = extract_brand_tokens(req)
wb = extract_brand_tokens(cand)

print("req brand:", rb)
print("wh brand:", wb)
print("fuzz ratio:", fuzz.ratio(rb, wb))
print("token sort:", fuzz.token_sort_ratio(rb, wb))
print("fuzz ratio with normalized spaces/farsi:", fuzz.ratio(rb.replace(' ', ''), wb.replace(' ', '')))

# line 271-284 simulation:
words_r = rb.split()
words_w = wb.split()
first_r = words_r[0] if words_r else ""
first_w = words_w[0] if words_w else ""
if len(words_r) > 1 or len(words_w) > 1:
    b_sim = fuzz.token_sort_ratio(rb, wb)
else:
    b_sim = fuzz.ratio(rb, wb)
if first_r and first_w and (first_r == first_w or fuzz.ratio(first_r, first_w) >= 80):
    b_sim = max(b_sim, 80)
elif rb.startswith(wb) or wb.startswith(rb):
    b_sim = max(b_sim, 80)
print("b_sim:", b_sim)
if b_sim < 65:
    print("STATUS KILLED TO NO_MATCH!")
else:
    print("STATUS KEPT AS MATCH!")
