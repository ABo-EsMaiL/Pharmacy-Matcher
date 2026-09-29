target_file = r"d:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py"

with open(target_file, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update SYSTEM_PROMPT rule 2 for drops
old_drops = '      - Drops (نقط, قطرة) ONLY match Drops.\n'
new_drops = '      - Drops (نقط, قطرة) ONLY match Drops. NEVER match drops with tablets or plain numbers without drops (e.g. كتافلام نقط does NOT match كتافلام 50).\n'

old_form_fallback = '   - If dosage form is not mentioned on one side, assume compatible if brand matches.\n'
new_form_fallback = '   - If dosage form is not mentioned on one side, assume compatible if brand matches, EXCEPT for Drops (نقط/قطرة) which strictly require drops on both sides.\n'

if old_drops in text:
    text = text.replace(old_drops, new_drops)
    print("Updated drops rule in SYSTEM_PROMPT.")
else:
    print("Warning: old_drops not found directly.")

if old_form_fallback in text:
    text = text.replace(old_form_fallback, new_form_fallback)
    print("Updated form fallback in SYSTEM_PROMPT.")
else:
    print("Warning: old_form_fallback not found directly.")

# 2. Update b_sim calculation to include ratio without spaces
old_bsim = """                                    if len(words_r) > 1 or len(words_w) > 1:
                                        b_sim = fuzz.token_sort_ratio(req_b, wh_b)
                                    else:
                                        b_sim = fuzz.ratio(req_b, wh_b)"""

new_bsim = """                                    b_sim = max(
                                        fuzz.ratio(req_b, wh_b),
                                        fuzz.token_sort_ratio(req_b, wh_b),
                                        fuzz.ratio(req_b.replace(' ', ''), wh_b.replace(' ', ''))
                                    )"""

if old_bsim in text:
    text = text.replace(old_bsim, new_bsim)
    print("Updated b_sim calculation.")
else:
    print("Warning: old_bsim not found directly.")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(text)

print("Coordinator update completed.")
