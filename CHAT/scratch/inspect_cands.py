import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

from scratch.test_enhanced_search import candidates_for_llm, extract_brand_tokens

print("Sample candidates:")
for i, (req, cands) in enumerate(list(candidates_for_llm.items())[:20]):
    b_req = extract_brand_tokens(req)
    cand_strs = [f"{c['name']} (sim={c['brand_sim']}, tfidf={c['score']:.2f})" for c in cands]
    print(f"{i+1}. '{req}' [Brand: '{b_req}']")
    for cs in cand_strs:
        print(f"    -> {cs}")
