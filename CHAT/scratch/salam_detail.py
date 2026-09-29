import sys
sys.path.insert(0, r'd:\AI_Engineer\Pharmacy-agy')
import openpyxl, json
from src.extract.pdf_reader import parse_structured_result
from src.match.text_match import normalize_text
from rapidfuzz import fuzz

wb = openpyxl.load_workbook('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/input_shortages/0913.xlsx')
ws = wb['ورقة2']
shortages = [(r, str(ws.cell(r, 2).value).strip()) for r in range(7, ws.max_row + 1) if ws.cell(r, 2).value]

salam_data = json.load(open('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/input_warehouses/السلام شبين.json', encoding='utf-8'))
salam_items = [i['item_name_raw'] for i in parse_structured_result(salam_data, 'salam')]

matched_salam = []
unmatched_salam = []

# Non-drug stop words in Arabic pharma
STOP_WORDS = {'اقراص', 'كبسول', 'كبسولات', 'شراب', 'امبول', 'حقن', 'مرهم', 'كريم', 'فوار', 'لبوس', 'نقط', 'سعر', 'جديد', 'قديم', 'باكو', 'شريط', 'س', 'ج', 'ق', 'مجم', 'ملجم', 'مل', 'ملل', 'جم', 'كبير', 'صغير', 'وسط'}

def get_core_tokens(text):
    tokens = normalize_text(text).replace('/', ' ').replace('-', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    return [t for t in tokens if t not in STOP_WORDS and not t.isdigit()]

for idx, s in enumerate(salam_items, 1):
    s_core = get_core_tokens(s)
    if not s_core:
        continue
    best_candidate = None
    best_score = 0
    
    for r, sh in shortages:
        sh_core = get_core_tokens(sh)
        if not sh_core: continue
        
        # Check if the primary brand token matches
        primary_s = s_core[0]
        # Allow prefix/substring match of primary brand (at least 4 chars)
        brand_match = False
        for sh_t in sh_core:
            if primary_s == sh_t or (len(primary_s) >= 4 and (primary_s in sh_t or sh_t in primary_s)):
                brand_match = True
                break
                
        if brand_match:
            score = fuzz.token_set_ratio(normalize_text(s), normalize_text(sh))
            if score > best_score:
                best_score = score
                best_candidate = (r, sh, score)
                
    if best_candidate and best_score >= 50:
        matched_salam.append((idx, s, best_candidate[0], best_candidate[1], best_score))
    else:
        unmatched_salam.append((idx, s))

print(f"Total Salam Items: {len(salam_items)}")
print(f"Matched with a shortage having the SAME primary drug brand: {len(matched_salam)}")
print(f"Unmatched (Brand NOT present in shortages): {len(unmatched_salam)}")

print("\n--- MATCHED EXAMPLES ---")
for idx, s, r, sh, score in matched_salam[:25]:
    print(f"[{idx}] Salam: {s} <===> Shortage (Row {r}): {sh} (Score: {score:.1f})")

print("\n--- UNMATCHED EXAMPLES (First 20) ---")
for idx, s in unmatched_salam[:20]:
    print(f"[{idx}] {s}")
