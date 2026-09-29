from pathlib import Path

file_path = Path(r"D:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py")
content = file_path.read_text(encoding="utf-8")

# 1. Add Liquids vs Solid Strengths rule to SYSTEM_PROMPT
target_prompt = "      - Sprays (بخاخ, سبراي) ONLY match Sprays.\n   - COMBINATION PRODUCTS"
replacement_prompt = """      - Sprays (بخاخ, سبراي) ONLY match Sprays.
   - LIQUIDS VS SOLID STRENGTHS (Syrups vs Plain mg):
     - Liquid dosage forms (شراب, معلق, نقط) are formulated by volume (مل) or concentration per dose (/5مل). Plain numeric strengths (like 400mg, 500mg, 1000mg) without "/5ml" or "شراب" or "مل" signify solid tablets/capsules.
     - If one side explicitly specifies a syrup (شراب), it MUST NEVER match a candidate that specifies a plain tablet strength (like 400مجم, 500مجم) without the word "شراب" or "مل" or "/5مل". This is a strict form conflict -> return "status": "no_match".
   - COMBINATION PRODUCTS"""

if target_prompt in content:
    content = content.replace(target_prompt, replacement_prompt, 1)
    print("[✓] Added Liquids vs Solid rule to SYSTEM_PROMPT")
else:
    print("[!] Target for prompt not found")

# 2. Add deterministic post-filter checks
target_post = """                                req_form = extract_form_group(shortage_name)
                                wh_form = extract_form_group(warehouse_item)
                                if req_form and wh_form and req_form != wh_form:
                                    status = "no_match" """

# Let's search by a unique substring around req_form
old_form_check = """                                req_form = extract_form_group(shortage_name)
                                wh_form = extract_form_group(warehouse_item)
                                if req_form and wh_form and req_form != wh_form:
                                    status = "no_match" """

new_form_check = """                                req_form = extract_form_group(shortage_name)
                                wh_form = extract_form_group(warehouse_item)
                                if req_form and wh_form and req_form != wh_form:
                                    status = "no_match"
                                    
                                # 1b. Liquids vs Plain Solid Tablet Strength conflict
                                is_req_syrup = bool(re.search(r'\\b(شراب|شرب|معلق)\\b', shortage_name))
                                is_wh_syrup = bool(re.search(r'\\b(شراب|شرب|معلق)\\b', warehouse_item))
                                norm_wh = warehouse_item
                                for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
                                    norm_wh = norm_wh.replace(e, w)
                                norm_req = shortage_name
                                for e, w in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
                                    norm_req = norm_req.replace(e, w)
                                has_wh_solid_mg = bool(re.search(r'\\b(100|125|200|250|300|400|500|600|800|1000)\\s*(?:مجم|مج|mg)\\b', norm_wh)) and not re.search(r'\\b(مل|ملل|ml|/5|5مل)\\b', norm_wh)
                                has_req_solid_mg = bool(re.search(r'\\b(100|125|200|250|300|400|500|600|800|1000)\\s*(?:مجم|مج|mg)\\b', norm_req)) and not re.search(r'\\b(مل|ملل|ml|/5|5مل)\\b', norm_req)
                                if (is_req_syrup and not is_wh_syrup and has_wh_solid_mg) or (is_wh_syrup and not is_req_syrup and has_req_solid_mg):
                                    status = "no_match" """

if old_form_check.strip() in content:
    content = content.replace(old_form_check.strip(), new_form_check.strip(), 1)
    print("[✓] Added Liquids vs Solid check to post-filter")
else:
    print("[!] Target for form check not found")

# 3. Add brand prefix integrity check
old_sim_check = """                                    if first_r and first_w and (first_r == first_w or fuzz.ratio(first_r, first_w) >= 80):
                                        b_sim = max(b_sim, 80)
                                    elif req_b.startswith(wh_b) or wh_b.startswith(req_b):
                                        b_sim = max(b_sim, 80)
                                    if b_sim < 65:
                                        status = "no_match" """

new_sim_check = """                                    if first_r and first_w and (first_r == first_w or fuzz.ratio(first_r, first_w) >= 80):
                                        b_sim = max(b_sim, 80)
                                    elif req_b.startswith(wh_b) or wh_b.startswith(req_b):
                                        b_sim = max(b_sim, 80)
                                    
                                    # Brand Prefix Integrity check (e.g. ابيكوتيل vs البوتيل)
                                    if first_r and first_w:
                                        has_al_r = first_r.startswith('ال')
                                        has_al_w = first_w.startswith('ال')
                                        if has_al_r != has_al_w:
                                            r_strip = first_r[2:] if has_al_r else first_r
                                            w_strip = first_w[2:] if has_al_w else first_w
                                            if fuzz.ratio(r_strip, w_strip) < 85:
                                                b_sim = min(b_sim, 50)
                                                
                                    if b_sim < 65:
                                        status = "no_match" """

if old_sim_check.strip() in content:
    content = content.replace(old_sim_check.strip(), new_sim_check.strip(), 1)
    print("[✓] Added Brand Prefix check to post-filter")
else:
    print("[!] Target for sim check not found")

file_path.write_text(content, encoding="utf-8")
print("[SUCCESS] coordinator.py updated.")
