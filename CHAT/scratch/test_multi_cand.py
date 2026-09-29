import sys
sys.path.insert(0, ".")
sys.path.insert(0, r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a")
from scratch.test_new_classifier import classify_pair

# Suppose warehouse has both forms or different strengths:
wh_items_sample = [
    "كتافلام ٥٠ س.ج ٨٦ج",
    "كتافلام نقط بالفم",
    "سيتال اقراص 500 س ج",
    "سيتال اقراص 1 جم",
    "زنكترون اقراص باكت 160",
]

req = "كتافلام  نقط"
print(f"Shortage item: '{req}'")
for cand in wh_items_sample:
    res, reason = classify_pair(req, cand)
    print(f"  vs '{cand}' -> [{res}] ({reason})")
