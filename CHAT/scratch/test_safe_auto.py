import sys
sys.path.insert(0, ".")
import json
import re
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
from src.config import load_config

# Helper to normalize arabic numbers
def norm_num(s: str) -> str:
    s = str(s)
    for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        s = s.replace(e, w)
    return s

def get_strength_pattern(text: str) -> str | None:
    text = norm_num(text.lower())
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:مجم|مج|جم|جرام|gm|mg|mcg|مكجم)', text)
    if m:
        return m.group(1)
    if 'ربع' in text or '25.' in text:
        return '0.25'
    if 'نص' in text or 'نصف' in text or '.5' in text or '0.5' in text:
        return '0.5'
    return None

def has_co(text: str) -> bool:
    t = text.lower()
    return bool(re.search(r'(?:^|[^\w])(كو|بلس|بلاس|كومب|co|plus|comp)(?:[^\w]|$)|كواقراص|كوأقراص|بلساقراص|بلسكبسول', t))

def are_forms_compatible(form1: str | None, form2: str | None) -> bool:
    if not form1 or not form2:
        return True
    if form1 == form2:
        return True
    compat = {
        ('tablet', 'capsule'), ('capsule', 'tablet'),
        ('cream', 'ointment'), ('ointment', 'cream'),
        ('cream', 'gel'), ('gel', 'cream'),
        ('injection', 'ampoule'), ('ampoule', 'injection'),
    }
    return (form1, form2) in compat

# Brand Family Stopwords that need secondary tokens to match
BRAND_FAMILIES = {'بيتادين', 'هيرو', 'انسولين', 'ليمتلس', 'سيتال', 'لبن'}

def is_safe_auto_match(req: str, cand: str) -> tuple[bool, str]:
    brand_r = extract_brand_tokens(req)
    brand_c = extract_brand_tokens(cand)
    if not brand_r or not brand_c:
        return False, "no_brand"
        
    words_r = brand_r.split()
    words_c = brand_c.split()
    
    # If brand belongs to a wide family, brand must match beyond the first word
    first_r = words_r[0]
    first_c = words_c[0]
    if first_r in BRAND_FAMILIES or first_c in BRAND_FAMILIES:
        # Full brand string must match well
        if fuzz.ratio(brand_r, brand_c) < 85:
            return False, "brand_family_ambiguity"
            
    b_sim = fuzz.ratio(brand_r, brand_c)
    if words_r and words_c and (words_r[0] == words_c[0] or fuzz.ratio(words_r[0], words_c[0]) >= 85):
        if len(words_r) == 1 and len(words_c) == 1:
            b_sim = max(b_sim, 90)
            
    if b_sim < 85:
        return False, "low_brand_sim"
        
    form_r = extract_form_group(req)
    form_c = extract_form_group(cand)
    if not are_forms_compatible(form_r, form_c):
        return False, "form_conflict"
        
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
                
    slash_r = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', req)
    slash_c = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', cand)
    if (slash_r and not slash_c) or (slash_c and not slash_r):
        return False, "slash_strength_mismatch"
    if slash_r and slash_c and slash_r.group(1) != slash_c.group(1):
        return False, "slash_strength_mismatch"
        
    return True, "auto_matched"

print("Safety Auto-Match function defined successfully.")
