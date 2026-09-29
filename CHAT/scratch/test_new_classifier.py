import sys
sys.path.insert(0, ".")
import re
from rapidfuzz import fuzz
from src.fast_match.search import extract_brand_tokens, extract_form_group

def norm_num(s: str) -> str:
    s = str(s)
    for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        s = s.replace(e, w)
    return s

def get_strength_pattern(text: str) -> str | None:
    text = norm_num(text.lower())
    m = re.search(r'(\d+(?:\.\d+)?)\s*(مجم|مج|جم|جرام|gm|mg|mcg|مكجم)', text)
    if m:
        val = m.group(1)
        unit = m.group(2)
        if unit in ['جم', 'جرام', 'gm']:
            try:
                val = str(float(val) * 1000)
            except:
                pass
        return val
    m2 = re.search(r'\b(1000|875|625|500|400|300|250|200|150|125|100|80|75|50|40|25|20|15|10|5|2.5|1)\b', text)
    if m2:
        return m2.group(1)
    if 'ربع' in text or '25.' in text:
        return '0.25'
    if 'نص' in text or 'نصف' in text or '.5' in text or '0.5' in text:
        return '0.5'
    return None

def has_co(text: str) -> bool:
    t = text.lower()
    return bool(re.search(r'(?:^|[^\w])(كو|بلس|بلاس|كومب|co|plus|comp)(?:[^\w]|$)|كواقراص|كوأقراص|بلساقراص|بلسكبسول', t))

def are_forms_identical(form1: str | None, form2: str | None) -> bool:
    if not form1 or not form2:
        return True
    if form1 == form2:
        return True
    # Tablets and capsules are commercially identical oral solid units
    if (form1, form2) in {('tablet', 'capsule'), ('capsule', 'tablet')}:
        return True
    return False

BRAND_FAMILIES = {'بيتادين', 'هيرو', 'انسولين', 'ليمتلس', 'سيتال', 'لبن'}

def classify_pair(req: str, cand: str) -> tuple[str, str]:
    """
    Classifies a (requested, candidate) pair according to the user's exact algorithm:
    - 'match': Same brand, same strength, same form.
    - 'review': Same brand, same strength, but DIFFERENT form (e.g. cream vs ointment, drops vs tablets).
    - 'reject': Different strength (التركيز خط أحمر), or different combination, or brand family violation.
    - 'ambiguous': Brand similarity 60%-85% (OCR typos like برونفين vs بروفين) -> send to LLM.
    """
    brand_r = extract_brand_tokens(req)
    brand_c = extract_brand_tokens(cand)
    if not brand_r or not brand_c:
        return "reject", "no_brand"
        
    words_r = brand_r.split()
    words_c = brand_c.split()
    first_r = words_r[0] if words_r else ""
    first_c = words_c[0] if words_c else ""
    
    # 1. Brand Family Protection
    if first_r in BRAND_FAMILIES or first_c in BRAND_FAMILIES:
        if fuzz.ratio(brand_r, brand_c) < 85:
            return "reject", "brand_family_conflict"
            
    # 2. Combination check (كو / بلس)
    if has_co(req) != has_co(cand):
        return "reject", "combination_mismatch"
        
    # 3. Strength check (التركيز خط أحمر - no tolerance)
    str_r = get_strength_pattern(req)
    str_c = get_strength_pattern(cand)
    if str_r and str_c:
        try:
            if float(str_r) != float(str_c):
                return "reject", f"strength_conflict_{str_r}_vs_{str_c}"
        except:
            if str_r != str_c:
                return "reject", f"strength_conflict_{str_r}_vs_{str_c}"
                
    slash_r = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', norm_num(req))
    slash_c = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', norm_num(cand))
    if slash_r and slash_c and slash_r.group(1) != slash_c.group(1):
        return "reject", "slash_strength_conflict"
    if (slash_r and not slash_c) or (slash_c and not slash_r):
        return "reject", "slash_missing_conflict"

    # 4. Brand Similarity & Identity
    b_sim = fuzz.ratio(brand_r, brand_c)
    is_exact_brand = (brand_r == brand_c)
    
    if len(words_r) == 1 and len(words_c) == 1:
        if first_r == first_c:
            is_exact_brand = True
        elif fuzz.ratio(first_r, first_c) >= 90:
            is_exact_brand = True
            
    if len(words_r) == len(words_c) and len(words_r) > 1:
        words_match = all(w_r == w_c or fuzz.ratio(w_r, w_c) >= 85 for w_r, w_c in zip(words_r, words_c))
        if words_match:
            is_exact_brand = True
            
    # If brand has 60% <= sim < 85% and not exact -> Ambiguous (needs LLM to check OCR)
    if not is_exact_brand:
        if b_sim >= 60:
            return "ambiguous", f"ocr_check_needed_{b_sim}%"
        else:
            return "reject", f"low_brand_sim_{b_sim}%"

    # 5. Form check for confirmed brand:
    # If same brand and same strength:
    form_r = extract_form_group(req)
    form_c = extract_form_group(cand)
    
    is_r_drops = 'نقط' in req or 'قطره' in req or 'قطرة' in req
    is_c_drops = 'نقط' in cand or 'قطره' in cand or 'قطرة' in cand
    is_drops_conflict = (is_r_drops != is_c_drops)
    
    is_req_syrup = bool(re.search(r'\b(شراب|شرب|معلق)\b', req))
    is_cand_syrup = bool(re.search(r'\b(شراب|شرب|معلق)\b', cand))
    is_syrup_conflict = (is_req_syrup != is_cand_syrup)
    
    # Are forms identical?
    if are_forms_identical(form_r, form_c) and not is_drops_conflict and not is_syrup_conflict:
        return "match", "exact_brand_and_form"
    else:
        # Different form with same brand and non-conflicting strength -> REVIEW!
        return "review", f"different_form_{form_r}_vs_{form_c}"

# Test cases
test_cases = [
    ("زنكترون 30 كبسولة", "زنكترون أقراص باكت 160"),
    ("سيتال 1جم أقراص", "سيتال 500 أقراص"),
    ("نويوريك 300 مجم", "نو-يوريك 100 مجم"),
    ("ميبو كريم 15جم", "ميبو مرهم 15جم"),
    ("كتافلام نقط", "كتافلام 50 اقراص"),
    ("انسولين نوفورابيد", "انسولين اكترابيد"),
    ("سينوبريت اقراص", "سينوبريل 2 مجم اقراص"),
    ("برونفين 400مجم", "بروفين 400مجم"),
    ("ماريفان 3مجم 3شريط س ج", "ماريفان ٣ مجم/جلاكسو"),
    ("كلاريتين اقراص", "ترايكيتين اقراص"),
]

print("=== Testing New Classifier ===")
for r, c in test_cases:
    res, reason = classify_pair(r, c)
    print(f"'{r}' vs '{c}'")
    print(f"  -> [{res.upper()}]: {reason}\n")
