import sys
sys.path.insert(0, ".")
import re
import json
from pathlib import Path
from rapidfuzz import fuzz

from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.file_handler import read_input_files
from src.fast_match.search import (
    FastCandidateFinder,
    extract_brand_tokens,
    extract_form_group,
    normalize_text,
    FORM_GROUPS
)

# Helper to normalize arabic numbers
def norm_num(s: str) -> str:
    s = str(s)
    for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        s = s.replace(e, w)
    return s

def get_strength_pattern(text: str) -> str | None:
    text = norm_num(text.lower())
    # Match number with unit
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:مجم|مج|جم|جرام|gm|mg|mcg|مكجم)', text)
    if m:
        val = m.group(1)
        # convert 1جم or 1 gm to 1000 mg if needed, or keep as string
        if 'جم' in m.group(0) or 'جرام' in m.group(0) or 'gm' in m.group(0):
            try:
                val = str(float(val) * 1000)
            except:
                pass
        return val
    # Match standalone 3 or 4 digit numbers likely to be strengths (e.g. 500, 1000, 250, 400)
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

def are_forms_compatible(form1: str | None, form2: str | None) -> bool:
    if not form1 and not form2:
        return True
    if form1 == form2:
        return True
    compat = {
        ('tablet', 'capsule'), ('capsule', 'tablet'),
        ('cream', 'ointment'), ('ointment', 'cream'),
        ('cream', 'gel'), ('gel', 'cream'),
        ('injection', 'ampoule'), ('ampoule', 'injection'),
    }
    if (form1, form2) in compat:
        return True
    # If one is specified and incompatible (e.g. drops vs tablet, syrup vs cream)
    if form1 and form2 and form1 != form2:
        return False
    return True

# Brand Family Stopwords that need secondary tokens to match
BRAND_FAMILIES = {'بيتادين', 'هيرو', 'انسولين', 'ليمتلس', 'سيتال', 'لبن'}

def is_safe_auto_match_calibrated(req: str, cand: str) -> tuple[bool, str]:
    brand_r = extract_brand_tokens(req)
    brand_c = extract_brand_tokens(cand)
    if not brand_r or not brand_c:
        return False, "no_brand"
        
    words_r = brand_r.split()
    words_c = brand_c.split()
    
    first_r = words_r[0]
    first_c = words_c[0]
    
    # 1. Wide brand family protection
    if first_r in BRAND_FAMILIES or first_c in BRAND_FAMILIES:
        if fuzz.ratio(brand_r, brand_c) < 85:
            return False, "brand_family_ambiguity"
            
    # 2. Strict brand match: For auto-match, brand MUST match exactly or identical root!
    # Do NOT allow single-character fuzzy changes on short brand names (e.g. سينوبريت vs سينوبريل, ديوزمين vs ديبوزين)
    if len(words_r) == 1 and len(words_c) == 1:
        if first_r != first_c:
            if fuzz.ratio(first_r, first_c) < 90:
                return False, f"brand_diff_{first_r}_vs_{first_c}"
    elif len(words_r) == len(words_c):
        for w_r, w_c in zip(words_r, words_c):
            if w_r != w_c and fuzz.ratio(w_r, w_c) < 85:
                return False, f"brand_word_diff_{w_r}_vs_{w_c}"
    else:
        if fuzz.ratio(brand_r, brand_c) < 85:
            return False, "low_brand_sim"
            
    # 3. Form compatibility
    form_r = extract_form_group(req)
    form_c = extract_form_group(cand)
    if not are_forms_compatible(form_r, form_c):
        return False, "form_conflict"
        
    # Check drops (نقط) vs tablets
    is_r_drops = 'نقط' in req or 'قطره' in req or 'قطرة' in req
    is_c_drops = 'نقط' in cand or 'قطره' in cand or 'قطرة' in cand
    if is_r_drops != is_c_drops:
        return False, "drops_conflict"
        
    is_req_syrup = bool(re.search(r'\b(شراب|شرب|معلق)\b', req))
    is_cand_syrup = bool(re.search(r'\b(شراب|شرب|معلق)\b', cand))
    norm_c = norm_num(cand)
    norm_r = norm_num(req)
    has_c_solid_mg = bool(re.search(r'\b(100|125|200|250|300|400|500|600|800|1000)\s*(?:مجم|مج|mg)\b', norm_c)) and not re.search(r'\b(مل|ملل|ml|/5|5مل)\b', norm_c)
    has_r_solid_mg = bool(re.search(r'\b(100|125|200|250|300|400|500|600|800|1000)\s*(?:مجم|مج|mg)\b', norm_r)) and not re.search(r'\b(مل|ملل|ml|/5|5مل)\b', norm_r)
    if (is_req_syrup and not is_cand_syrup and has_c_solid_mg) or (is_cand_syrup and not is_req_syrup and has_r_solid_mg):
        return False, "syrup_solid_conflict"
        
    if has_co(req) != has_co(cand):
        return False, "co_mismatch"
        
    str_r = get_strength_pattern(req)
    str_c = get_strength_pattern(cand)
    if str_r and str_c:
        try:
            if float(str_r) != float(str_c):
                return False, f"strength_mismatch_{str_r}_vs_{str_c}"
        except:
            if str_r != str_c:
                return False, f"strength_mismatch_{str_r}_vs_{str_c}"
                
    slash_r = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', norm_num(req))
    slash_c = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', norm_num(cand))
    if (slash_r and not slash_c) or (slash_c and not slash_r):
        return False, "slash_strength_mismatch"
    if slash_r and slash_c and slash_r.group(1) != slash_c.group(1):
        return False, "slash_strength_mismatch"
        
    return True, "auto_matched"

print("Calibrated auto-match function loaded.")
