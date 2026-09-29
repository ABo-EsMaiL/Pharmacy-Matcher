import sys
sys.path.insert(0, ".")
sys.path.insert(0, r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a")
from scratch.calibrate_matcher import is_safe_auto_match_calibrated

tests = [
    ('سينوبريت اقراص', 'سينوبريل 2 مجم اقراص/باکت 90'),
    ('ديوزمين 30 قرص', 'ديبوزين 500مجم اقراص'),
    ('فيتا زنك  كبسول', 'فیتا زون قرص قدیم'),
    ('سيتال1جم اقراص س ج', 'سيتال اقراص 500 س ج'),
    ('كتافلام  نقط', 'كتافلام ٥٠ س.ج ٨٦ج'),
    ('الكابرس تريو5/160/12.5مجم س ج', 'الكابرس تربو ١٠/١٦/١٢٤٠ قرص'),
    ('زنكترون 30كبسولة س ج', 'زنكترون اقراص باكت 160'),
    ('ب ك ميرز كبسول س ج', 'ميرز كبسول/باكت 30'),
    ('ماريفان3مجم3شريط س ج', 'ماريفان ٣ مجم/جلاكسو'),
    ('انسولين نوفورابيد', 'انسولين اكترابيد'),
]

for req, cand in tests:
    res, reason = is_safe_auto_match_calibrated(req, cand)
    print(f"'{req}' vs '{cand}' => {res} ({reason})")
