import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import FastCandidateFinder
from src.match.text_match import normalize_text

cand_finder = FastCandidateFinder(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-004\input_warehouses\السلام شبين.pdf")
cands = cand_finder.find_candidates("ديكساتوبرين مرهم س ج", limit=5)
print("Candidates found for ديكساتوبرين مرهم س ج:")
for c in cands:
    print("  -", c)
