"""
وحدة تنظيف النصوص والمطابقة الضبابية لأسماء الأدوية العربية.
Text cleaning and fuzzy matching for Arabic drug names.
"""

import re
import unicodedata
from rapidfuzz import fuzz


# ──────────────────────────────────────────────
# خريطة الأرقام العربية-الهندية والفارسية إلى الأرقام الغربية
# ──────────────────────────────────────────────
_ARABIC_INDIC_MAP = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
    "01234567890123456789",
)

# أحرف الألف المختلفة → ا
_ALEF_VARIANTS = re.compile(r"[أإآٱ]")

# التشكيل (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين)
_TASHKEEL = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC"
    r"\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]"
)

# التطويل / الكشيدة
_TATWEEL = "\u0640"


def normalize_text(text: str) -> str:
    """
    تنظيف وتوحيد نص اسم الدواء العربي للمقارنة مع دعم معالجة أخطاء الـ OCR واليونيكود.
    """
    if not text:
        return ""

    # 1. تحويل الأرقام العربية-الهندية والفارسية إلى غربية
    result = unicodedata.normalize("NFKC", str(text)).translate(_ARABIC_INDIC_MAP)
    # Presentation forms must be decomposed before Arabic/Persian mappings.
    result = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]', '', result)

    # 2. إزالة التطويل/الكشيدة
    result = result.replace(_TATWEEL, "")

    # 3. إزالة التشكيل
    result = _TASHKEEL.sub("", result)

    # 4. توحيد أشكال الألف
    result = _ALEF_VARIANTS.sub("ا", result)

    # 5. توحيد الياء والألف المقصورة والياء الفارسية (OCR)
    result = re.sub(r"[ىي\u06CC]", "ي", result)

    # 6. توحيد حروف الـ OCR الشائعة في ملفات PDF (الكاف والباء والتاء والدال والجيم والهاء والفاء الفارسية/الأردية)
    ocr_replacements = {
        "\u06A9": "ك",  # ک -> ك
        "\u067E": "ب",  # پ -> ب
        "\u06AF": "ك",  # گ -> ك (مثل کوف زنگ -> كوف زنك)
        "\u0686": "ج",  # چ -> ج (مثل زانوچيلد -> زانوجيلد)
        "\u06A4": "ف",  # ڤ -> ف (مثل ڤولترين -> فولترين)
        "\u06A5": "ف",  # ڥ -> ف
        "\u06BA": "ن",  # ں -> ن
        "\u0679": "ت",  # ٹ -> ت
        "\u0688": "د",  # ڈ -> د
        "\u0691": "ر",  # ڑ -> ر
        "\u0698": "ز",  # ژ -> ز
        "\u06C0": "ه",  # ۀ -> ه
        "\u06C1": "ه",  # ہ -> ه
    }
    for k_char, v_char in ocr_replacements.items():
        result = result.replace(k_char, v_char)

    # 7. تحويل التاء المربوطة إلى هاء
    result = result.replace("ة", "ه")

    # 8. تصحيح أخطاء OCR صيدلانية شائعة الحدوث في الهيئات
    result = re.sub(r"\bاقراض\b", "اقراص", result)

    # 9. توحيد المسافات
    result = re.sub(r"\s+", " ", result)

    # 10. حذف المسافات من البداية والنهاية
    result = result.strip()

    return result


def find_candidates(
    query: str,
    items: list[str],
    threshold: float = 0.60,
    max_results: int = 5,
) -> list[tuple[str, float]]:
    """
    البحث عن أقرب المرشحين لاسم دواء باستخدام المطابقة الضبابية.

    يستخدم كلاً من token_sort_ratio و partial_ratio من مكتبة rapidfuzz
    ويأخذ الأعلى بينهما لكل عنصر.

    Args:
        query: اسم الدواء المطلوب البحث عنه.
        items: قائمة أسماء الأدوية المتاحة في المخزن.
        threshold: الحد الأدنى لدرجة التشابه (0.0 إلى 1.0).
        max_results: الحد الأقصى لعدد النتائج المُرجَعة.

    Returns:
        قائمة من (اسم_الدواء_الأصلي, درجة_التشابه) مرتبة تنازلياً.
        الدرجة من 0.0 إلى 1.0.
    """
    if not query or not items:
        return []

    normalized_query = normalize_text(query)
    scored: list[tuple[str, float]] = []

    for original_item in items:
        normalized_item = normalize_text(original_item)

        # حساب درجة التشابه بطريقتين واختيار الأعلى
        score_token = fuzz.token_sort_ratio(normalized_query, normalized_item)
        score_partial = fuzz.partial_ratio(normalized_query, normalized_item)
        best_score = max(score_token, score_partial)

        # تحويل الدرجة من 0-100 إلى 0-1
        normalized_score = best_score / 100.0

        if normalized_score >= threshold:
            scored.append((original_item, normalized_score))

    # ترتيب تنازلي حسب الدرجة وأخذ أعلى النتائج
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max_results]


def quick_match(query: str, item: str) -> float:
    """
    حساب سريع لدرجة التشابه بين اسمي دواء.

    Args:
        query: اسم الدواء الأول.
        item: اسم الدواء الثاني.

    Returns:
        درجة التشابه من 0.0 إلى 1.0.
    """
    if not query or not item:
        return 0.0

    normalized_query = normalize_text(query)
    normalized_item = normalize_text(item)

    score_token = fuzz.token_sort_ratio(normalized_query, normalized_item)
    score_partial = fuzz.partial_ratio(normalized_query, normalized_item)

    return max(score_token, score_partial) / 100.0
