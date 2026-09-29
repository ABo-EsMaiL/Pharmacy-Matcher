confusables = {'ب', 'ت', 'ث', 'ن', 'ي'}
from rapidfuzz import fuzz

def is_valid_brand_match(r, w):
    r_c = r[2:] if r.startswith('ال') else r
    w_c = w[2:] if w.startswith('ال') else w
    
    # 1. First letter check
    if r_c and w_c and r_c[0] != w_c[0]:
        if not (r_c[0] in confusables and w_c[0] in confusables):
            return False, "first_letter_mismatch"
            
    # 2. Neo/New check
    is_r_neo = 'نيو' in r or 'new' in r.lower()
    is_w_neo = 'نيو' in w or 'new' in w.lower()
    if is_r_neo != is_w_neo:
        return False, "neo_prefix_mismatch"
        
    # 3. Overall similarity
    sim = max(fuzz.ratio(r, w), fuzz.token_sort_ratio(r, w))
    if sim < 75:
        return False, f"low_sim_{sim}"
        
    return True, f"valid_{sim}"

tests = [
    ('بروتولوك', 'كونترولوك'),
    ('نيوكاربون', 'اوكاربون'),
    ('زنكترون', 'زنكتون'),
    ('كارنيفيتا', 'كارنتينا'),
    ('جنتازون', 'جينتازون'),
    ('بروفين', 'برونفين'),
    ('زيثروماكس', 'زيثرون'),
    ('افيروكوكسيب', 'افيروكوسيب'),
    ('مكسيدرم', 'ميكسيدرم')
]

for r, w in tests:
    ok, res = is_valid_brand_match(r, w)
    print(f"{r} vs {w} -> {ok} ({res})")
