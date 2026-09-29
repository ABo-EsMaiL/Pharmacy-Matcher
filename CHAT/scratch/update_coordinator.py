import re

target_file = r"d:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update SYSTEM_PROMPT rule 1
old_rule = """   - If the trade brand name is a completely different commercial brand or generic substitute (e.g. Olfen is NOT Albiran, Depakine is NOT Depacan, Ampover is NOT Amevir, Grantril is NOT Grantil, Ricoxen is NOT Etoricox, Antopral is NOT Pantoprazole, Serovar is NOT Ciprobay, New Carbon is NOT Eucarbon), YOU MUST RETURN "status": "no_match" (or omit it). NEVER mark different brands as "match" or "review"!
   - Distinct commercial prefixes (like "نيو" / "New") or distinct trade endings/suffixes signify different trade brands (e.g. "New X" is NOT "X", a brand ending in "-rich" is NOT "-ren"). Return "no_match".
   - Allow common OCR scanning artifacts, dropped letters/syllables, and Arabic/Persian letter substitutions of the SAME exact brand (e.g. dropped initial letters like 'ا', dropped single letters or missing dots like 'ن' or 'ب', Persian/Urdu letters like پ for ب or ک for ك or گ for ك/ج, visually confused OCR letters like 'ف' vs 'د', or slight vowel variations)."""

new_rule = """   - If the trade brand name is a completely different commercial brand or generic substitute (e.g. Panadol is NOT Cetal, Brufen is NOT Cataflam, Augmentin is NOT Curam, Ricoxen is NOT Etoricox, Antopral is NOT Pantoprazole, Serovar is NOT Ciprobay, New Carbon is NOT Eucarbon), YOU MUST RETURN "status": "no_match" (or omit it). NEVER mark different brands as "match" or "review"!
   - Distinct commercial prefixes (like "نيو" / "New") or distinct trade endings/suffixes signify different trade brands (e.g. "New X" is NOT "X", a brand ending in "-rich" is NOT "-ren"). Return "no_match".
   - Allow common OCR scanning artifacts, dropped letters/syllables, phonetic variants, and Arabic/Persian letter substitutions of the SAME exact brand (like جرانتريل/جرانتيل, امبوفير/اميفير, ديباكين/ديبيكان, or dropped initial 'ا', dropped single letters or missing dots like 'ن' or 'ب', Persian/Urdu letters like پ for ب or ک for ك or گ for ك/ج, visually confused OCR letters like 'ف' vs 'د', or slight vowel variations)."""

if old_rule in content:
    content = content.replace(old_rule, new_rule)
    print("Updated SYSTEM_PROMPT successfully.")
else:
    # try normalized line endings
    content_norm = content.replace("\r\n", "\n")
    old_norm = old_rule.replace("\r\n", "\n")
    new_norm = new_rule.replace("\r\n", "\n")
    if old_norm in content_norm:
        content_norm = content_norm.replace(old_norm, new_norm)
        content = content_norm
        print("Updated SYSTEM_PROMPT with normalized endings.")
    else:
        print("WARNING: old_rule not found!")

# 2. Remove distinct_pairs block
old_distinct = """                                # 6. Known distinct look-alike brand pairs (strict zero tolerance)
                                distinct_pairs = {
                                    ('امبوفير', 'اميفير'), ('اميفير', 'امبوفير'),
                                    ('جرانتريل', 'جرانتيل'), ('جرانتيل', 'جرانتريل'),
                                    ('ديباكين', 'ديبيكان'), ('ديبيكان', 'ديباكين'),
                                    ('اولفن', 'البيران'), ('البيران', 'اولفن'),
                                }
                                for p1, p2 in distinct_pairs:
                                    if p1 in req_b and p2 in wh_b:
                                        status = "no_match"
"""

content_norm = content.replace("\r\n", "\n")
old_distinct_norm = old_distinct.replace("\r\n", "\n")

if old_distinct_norm in content_norm:
    content_norm = content_norm.replace(old_distinct_norm, "")
    print("Removed distinct_pairs block successfully.")
    content = content_norm
else:
    print("WARNING: distinct_pairs block not found!")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished writing", target_file)
