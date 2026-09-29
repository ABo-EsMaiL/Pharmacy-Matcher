import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from src.fast_match.search import extract_form_group, extract_brand_tokens
from rapidfuzz import fuzz
import re

cases = [
    {"cid": "C1", "shortage": "اولفن100مجم اس ار10كبسول س ج", "cand": "البيران اس ار اقراص / باكت 10", "llm_status": "match"},
    {"cid": "C2", "shortage": "زانوجليد4/30اقراص س ج", "cand": "زانوچيلد 4 مج اقراص/باكت 60", "llm_status": "match"},
    {"cid": "C3", "shortage": "امبوفير 5امبول س ج", "cand": "اميفير امبول", "llm_status": "match"},
    {"cid": "C4", "shortage": "ديباكين كرونو500مجم اقراص", "cand": "ديبيكان اقراص/العامرية", "llm_status": "match"},
    {"cid": "C5", "shortage": "جرانتريل 3مجم 6 امبول س ج", "cand": "جرانتيل امبول مجم تاريخ بعيد", "llm_status": "match"},
    {"cid": "C6", "shortage": "دوليبران1000مجم 15قرص", "cand": "دوليبيران ١جم، ٦٠قرص", "llm_status": "match"},
    {"cid": "C7", "shortage": "باروفين 30قرص س ج", "cand": "باروفين ٢٠ قرص", "llm_status": "match"},
    {"cid": "C8", "shortage": "افيروكوكسيب90مجم20قرص س ج", "cand": "افيرو كوكسبيب 90مجم-32ب", "llm_status": "match"},
    {"cid": "C9", "shortage": "نيوكاربون30قرص س ج", "cand": "نیوکاربن ۳۰کپسول", "llm_status": "match"},
    {"cid": "C10", "shortage": "ليفانوكس2شريط س ج", "cand": "ليفانوكس كبسول/باكت 200", "llm_status": "match"},
    {"cid": "C11", "shortage": "لاكتيز 15 ملل نقط 750مجم", "cand": "لاكتيز نقط بالفم ٥ مل ١٩٠", "llm_status": "review"},
]

for c in cases:
    shortage_name = c["shortage"]
    warehouse_item = c["cand"]
    status = c["llm_status"]
    
    if status in ("match", "review"):
        req_form = extract_form_group(shortage_name)
        wh_form = extract_form_group(warehouse_item)
        if req_form and wh_form and req_form != wh_form:
            status = "no_match"
            
        slash_req = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', shortage_name)
        slash_wh = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', warehouse_item)
        if slash_req and not slash_wh:
            status = "no_match"
        elif slash_wh and not slash_req:
            status = "no_match"
        elif slash_req and slash_wh and slash_req.group(1) != slash_wh.group(1):
            status = "no_match"
            
        is_req_co = bool(re.search(r'\b(كو|بلس|بلاس|كومب|co|plus|comp)\b', shortage_name.lower()))
        is_wh_co = bool(re.search(r'\b(كو|بلس|بلاس|كومب|co|plus|comp)\b', warehouse_item.lower()))
        if is_req_co != is_wh_co:
            status = "no_match"
            
        is_req_new = bool(re.search(r'\b(نيو|new)\b', shortage_name.lower()))
        is_wh_new = bool(re.search(r'\b(نيو|new)\b', warehouse_item.lower()))
        if is_req_new != is_wh_new:
            status = "no_match"
            
        req_b = extract_brand_tokens(shortage_name)
        wh_b = extract_brand_tokens(warehouse_item)
        if req_b and wh_b:
            words_r = req_b.split()
            words_w = wh_b.split()
            first_r = words_r[0] if words_r else ""
            first_w = words_w[0] if words_w else ""
            if len(words_r) > 1 or len(words_w) > 1:
                b_sim = fuzz.token_sort_ratio(req_b, wh_b)
            else:
                b_sim = fuzz.ratio(req_b, wh_b)
            if first_r and first_w and (first_r == first_w or fuzz.ratio(first_r, first_w) >= 80):
                b_sim = max(b_sim, 80)
            elif req_b.startswith(wh_b) or wh_b.startswith(req_b):
                b_sim = max(b_sim, 80)
            if b_sim < 65:
                status = "no_match"
                
    print(f"[{c['cid']}] {status.upper():<10} | Shortage: '{shortage_name}' vs Cand: '{warehouse_item}'")
