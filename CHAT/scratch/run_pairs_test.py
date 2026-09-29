import sys
sys.path.insert(0, ".")
sys.path.insert(0, r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a")
from scratch.sim_rules import is_deterministic_auto_match

test_pairs = [
    # Should Auto Match (Level 2)
    ("زنكترون 30كبسولة س ج", "زنكترون اقراص باكت 160"),
    ("ماريفان3مجم3شريط س ج", "ماريفان ٣ مجم/جلاكسو"),
    ("باروفين 30قرص س ج", "باروفين ٢٠ قرص"),
    ("ب ك ميرز كبسول س ج", "ميرز كبسول/باكت 30"),
    ("ديوراسيف  250مجم شراب س ج", "ديوراسيف ٢٥٠ شراب/سكويب"),
    ("ادولور 30مجم 3امبول", "ادولور - ٣٠مجم/٢ مللي ٣ امبول"),
    ("جوسبرين اقراص 3شريط", "جوسبرين اقراص/اجفار"),
    ("سيديبروكت كريم س ج", "سيديبروك كريم/المهن"),
    ("نيتروماك ريتارد2.5مجم كبسول", "نيتروماك ريتارد كبسول/التنشيط"),
    ("كلوسول سبراي س ج", "كولوسول بخاخة/الاوروبيه"),
    ("فانو كريم", "فانو کریم/باکت 50"),
    ("كوفي زنك شامبو", "کوف زنگ شامپو ج"),
    ("اسبوسيد 20قرص اطفال س ج", "اسبوبسيد 75 مج اقراص/باكت 120"),
    
    # Should NOT Auto Match (Must go to Level 3 / Review)
    ("سينوبريل كواقراص س ج", "سینوبریل 2 مجم اقراص/باکت 90"), # co mismatch
    ("تادالاندرو5جم30قرص", "تادالونج 5 مج 30 قرص/باکت 25"),     # brand mismatch
    ("بروتولوك40مجم اقراص س ج", "کونترولوک ۴۰مجم اقراص"),      # brand mismatch
    ("برونكوفين شراب", "برونفين 400مجم"),                    # syrup vs 400mg solid
    ("كابرجامون 5مجم اقراص س ج", "کابریامون ۰.۵ جم اقراص"),     # strength 5 vs 0.5
    ("سكينورين كريم", "سکینوریتش کریم"),                     # OCR typo -> needs Level 3
    ("بالموكورت  25. مجم امبول س ج", "بالمكيرت ربع"),          # fraction -> Level 2 or 3
]

print("=== TEST PAIRS RESULTS ===")
for req, cand in test_pairs:
    ok, reason = is_deterministic_auto_match(req, cand)
    print(f"[{req}]  <--->  [{cand}]")
    print(f"   -> Result: {'AUTO MATCH (Level 2)' if ok else 'SEND TO LEVEL 3 (LLM/Review)'} (Reason: {reason})\n")
