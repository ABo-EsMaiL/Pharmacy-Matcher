target_file = r"d:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py"
with open(target_file, "r", encoding="utf-8") as f:
    text = f.read()

old_s = """    - If the trade brand name is a completely different commercial brand or generic substitute (e.g. Panadol is NOT Cetal, Brufen is NOT Cataflam, Augmentin is NOT Curam, Ricoxen is NOT Etoricox, Antopral is NOT Pantoprazole, Serovar is NOT Ciprobay, New Carbon is NOT Eucarbon), YOU MUST RETURN "status": "no_match" (or omit it). NEVER mark different brands as "match" or "review"!"""
new_s = """    - If the trade brand name is a completely different commercial brand or generic substitute, YOU MUST RETURN "status": "no_match" (or omit it). NEVER mark different brands as "match" or "review"!"""

text = text.replace(old_s, new_s)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(text)

print("Line 20 cleaned.")
