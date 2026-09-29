import openpyxl
import os

P14_PATH = r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\results_PROC-014.xlsx"
wb = openpyxl.load_workbook(P14_PATH, data_only=True)
ws_nf = wb['لم يُعثر عليه']
nf_items = set([str(r[0]).strip() for r in ws_nf.iter_rows(values_only=True) if r and r[0]])

# Let's inspect known items from past runs and high-scoring candidates
candidates_to_evaluate = [
    # (shortage, wh_item, wh_file, expected_status, reason)
    ("لبن هيرو بيبي 2", "هيرو بيبي ٢", "المكرومي المنصورة.pdf", "match", "تطابق تام (لبن هيرو بيبي 2 هو هيرو بيبي 2) - حجبته كلمة لبن ومطابقة الحرف الأول"),
    ("تربتيزول10 مجم اقراص", "تریپتازول 10 مج اقراس/باکت 200", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام Tryptizol 10mg - حجبته عتبة تشابه الاسم التجاري 63% < 72%"),
    ("تورسامولكس10مجم اقراص س ج", "تورساموکس ۱۰ جم اقراص", "كيور فارما خاص.pdf", "match", "تطابق تام Torsamox 10mg - حجبه خطأ تحويل 'جم' إلى 10,000 مجم"),
    ("بقدونس وكرفس ايزيس", "ایزیز بقدونس وکرکس 20 فلتر", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام مع تصحيف OCR - حجبته قاعدة الحرف الأول (ب ضد ا)"),
    ("ينسون ايزيس س ج", "زيس ينسون 12 فلتر صغير ج/باكو 6", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام مع تصحيف OCR (زيس بدل إيزيس) - حجبته عتبة 50%"),
    ("سكينورين كريم", "سکینوریتش کریم", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام مع تصحيف OCR (سكينوريتش بدل سكينورين) - سقط في تقييم الباتش الكبير"),
    ("نيوروفيت اقراص  3 شريط", "نیروفيت اقراص سعر جديد", "المكرومي المنصورة.pdf", "match", "تطابق تام Neurovit اقراص - سقط في تقييم الباتش الكبير"),
    ("نيوروفيت اقراص  3 شريط", "نیروپفیت اقراص/باكت 15", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام Neurovit اقراص - سقط في تقييم الباتش الكبير"),
    ("نيوكاربون30قرص س ج", "نیوکاربن ۳۰کپسول", "كيور فارما خاص.pdf", "review", "نفس الدواء والتركيز ولكن الهيئة مختلفة (أقراص ضد كبسول) - سقط في تقييم الباتش الكبير"),
    ("ابيفيناك قطرة س ج", "ابيفيناك حقن", "كيور فارما خاص.pdf", "review", "نفس الدواء والتركيز ولكن الهيئة مختلفة (قطرة ضد حقن) - لم يتم جلبه بالمرشحات"),
    ("ليمتلس كروماكس كت30كيس س ج", "يمتليس كروماتكس كت 30 كيس جديد", "الهضبة الاثنين نقدى0.pdf", "match", "تطابق تام (مع مطابقة المخزن الأخرى) - حجبته قاعدة الحرف الأول (ل ضد ي)")
]

print("=" * 80)
print("AUDITING CONFIRMED MISSED ITEMS IN 'لم يُعثر عليه'")
print("=" * 80)

confirmed_misses = []
for sh, wh, wh_f, exp, rsn in candidates_to_evaluate:
    in_nf = sh in nf_items
    print(f"Shortage: '{sh}'")
    print(f"  -> WH Item: '{wh}' in [{wh_f}]")
    print(f"  -> Expected: {exp.upper()} | In 'لم يُعثر عليه': {in_nf}")
    print(f"  -> Diagnostic: {rsn}\n")
    if in_nf:
        confirmed_misses.append((sh, wh, wh_f, exp, rsn))

print(f"Total Confirmed True Misses in Not Found: {len(confirmed_misses)} items.")
