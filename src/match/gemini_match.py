"""
وحدة المطابقة الذكية باستخدام Gemini لحل الحالات الغامضة.
Use Gemini to resolve ambiguous drug name matches.
"""

import json
import logging
from typing import Any

from google import genai

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# النص التوجيهي لنموذج Gemini (عربي)
# ──────────────────────────────────────────────
_SINGLE_MATCH_PROMPT = """\
أنت خبير صيدلاني متخصص في مطابقة أسماء الأدوية.

**المهمة:** قارن اسم الصنف المطلوب (المفقود) مع قائمة الأصناف المرشحة من المخزن، وحدد أيهم يطابق الصنف المطلوب.

**اسم الصنف المطلوب:**
{shortage_name}

**الأصناف المرشحة:**
{candidates_text}

**قواعد المطابقة:**
1. قارن بين: اسم الصنف، التركيز (مثل 500 مجم)، الشكل الدوائي (أقراص، شراب، حقن، إلخ)، وحجم العبوة.
2. الاختلاف في الإملاء أو الأخطاء الكتابية مقبول (نفس الدواء بكتابة مختلفة = تطابق).
3. اختلاف التركيز = منتج مختلف (ليس تطابقاً). مثال: باراسيتامول 500 ≠ باراسيتامول 200.
4. اختلاف الشكل الدوائي = منتج مختلف (ليس تطابقاً). مثال: أقراص ≠ شراب.
5. إذا كانت المعلومات ناقصة (لا يوجد تركيز أو شكل دوائي) = غامض، لا تعتبره تطابقاً تلقائياً.
6. إذا كان هناك تطابق واضح (نفس الدواء، نفس التركيز، نفس الشكل) = تطابق.

**أجب بصيغة JSON فقط:**
{{
  "matched_index": <رقم المرشح المطابق (يبدأ من 0) أو -1 إذا لم يوجد تطابق>,
  "confidence": "<high أو medium أو low>",
  "reason": "<سبب القرار باللغة العربية>"
}}
"""

_BATCH_MATCH_PROMPT = """\
أنت خبير صيدلاني متخصص في مطابقة أسماء الأدوية.

**المهمة:** لكل صنف من الأصناف المطلوبة أدناه، ابحث عن أفضل تطابق في قائمة أصناف المخزن.

**الأصناف المطلوبة (المفقودة):**
{shortage_items_text}

**أصناف المخزن المتاحة:**
{warehouse_items_text}

**قواعد المطابقة:**
1. قارن بين: اسم الصنف، التركيز (مثل 500 مجم)، الشكل الدوائي (أقراص، شراب، حقن، إلخ)، وحجم العبوة.
2. الاختلاف في الإملاء أو الأخطاء الكتابية مقبول (نفس الدواء بكتابة مختلفة = تطابق).
3. اختلاف التركيز = منتج مختلف (ليس تطابقاً).
4. اختلاف الشكل الدوائي = منتج مختلف (ليس تطابقاً).
5. إذا كانت المعلومات ناقصة = غامض، لا تعتبره تطابقاً تلقائياً.

**أجب بصيغة JSON فقط — قائمة من النتائج:**
[
  {{
    "shortage_index": <رقم الصنف المطلوب (يبدأ من 0)>,
    "matched_warehouse_index": <رقم صنف المخزن المطابق (يبدأ من 0) أو -1 إذا لم يوجد>,
    "confidence": "<high أو medium أو low>",
    "reason": "<سبب القرار باللغة العربية>"
  }},
  ...
]
"""


def match_with_gemini(
    shortage_name: str,
    candidates: list[dict],
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> dict:
    """
    مطابقة صنف واحد مع قائمة مرشحين باستخدام Gemini.

    Args:
        shortage_name: اسم الصنف المطلوب (المفقود).
        candidates: قائمة المرشحين، كل عنصر يحتوي على:
            - item_name_raw: اسم الصنف الخام
            - source: اسم الملف المصدر (المخزن)
        api_key: مفتاح Gemini API.
        model: اسم النموذج المستخدم.

    Returns:
        قاموس يحتوي على:
            - matched: هل تم العثور على تطابق (bool)
            - matched_item: اسم الصنف المطابق أو None
            - confidence: درجة الثقة (high/medium/low)
            - reason: سبب القرار
    """
    if not candidates:
        return {
            "matched": False,
            "matched_item": None,
            "confidence": "low",
            "reason": "لا توجد أصناف مرشحة للمقارنة.",
        }

    # بناء نص المرشحين
    candidates_lines = []
    for i, cand in enumerate(candidates):
        name = cand.get("item_name_raw", "غير معروف")
        source = cand.get("source", "")
        candidates_lines.append(f"  [{i}] {name}  (المصدر: {source})")
    candidates_text = "\n".join(candidates_lines)

    prompt = _SINGLE_MATCH_PROMPT.format(
        shortage_name=shortage_name,
        candidates_text=candidates_text,
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )

        result = json.loads(response.text)

        matched_index = result.get("matched_index", -1)
        confidence = result.get("confidence", "low")
        reason = result.get("reason", "لم يُحدَّد سبب.")

        if matched_index >= 0 and matched_index < len(candidates):
            return {
                "matched": True,
                "matched_item": candidates[matched_index].get("item_name_raw"),
                "confidence": confidence,
                "reason": reason,
            }
        else:
            return {
                "matched": False,
                "matched_item": None,
                "confidence": confidence,
                "reason": reason,
            }

    except json.JSONDecodeError as e:
        logger.error("فشل تحليل استجابة Gemini كـ JSON: %s", e)
        return {
            "matched": False,
            "matched_item": None,
            "confidence": "low",
            "reason": f"خطأ في تحليل استجابة النموذج: {e}",
        }
    except Exception as e:
        logger.error("خطأ أثناء استدعاء Gemini API: %s", e)
        return {
            "matched": False,
            "matched_item": None,
            "confidence": "low",
            "reason": f"خطأ في الاتصال بالنموذج: {e}",
        }


def batch_match_with_gemini(
    shortage_items: list[str],
    warehouse_items: list[str],
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> list[dict]:
    """
    مطابقة دفعة من الأصناف المطلوبة مع أصناف المخزن في استدعاء واحد.

    يتم إرسال حتى 10 أصناف مطلوبة في كل استدعاء مع قائمة المخزن الكاملة.

    Args:
        shortage_items: قائمة أسماء الأصناف المطلوبة.
        warehouse_items: قائمة أسماء أصناف المخزن.
        api_key: مفتاح Gemini API.
        model: اسم النموذج المستخدم.

    Returns:
        قائمة نتائج المطابقة لكل صنف مطلوب.
    """
    if not shortage_items or not warehouse_items:
        return [
            {
                "matched": False,
                "matched_item": None,
                "confidence": "low",
                "reason": "قائمة فارغة.",
            }
            for _ in shortage_items
        ]

    all_results: list[dict] = []
    batch_size = 10

    # تقسيم الأصناف المطلوبة إلى دفعات
    for batch_start in range(0, len(shortage_items), batch_size):
        batch = shortage_items[batch_start : batch_start + batch_size]

        # بناء نص الأصناف المطلوبة
        shortage_lines = [f"  [{i}] {name}" for i, name in enumerate(batch)]
        shortage_items_text = "\n".join(shortage_lines)

        # بناء نص أصناف المخزن
        warehouse_lines = [
            f"  [{i}] {name}" for i, name in enumerate(warehouse_items)
        ]
        warehouse_items_text = "\n".join(warehouse_lines)

        prompt = _BATCH_MATCH_PROMPT.format(
            shortage_items_text=shortage_items_text,
            warehouse_items_text=warehouse_items_text,
        )

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )

            batch_results = json.loads(response.text)

            # ضمان أن النتيجة قائمة
            if not isinstance(batch_results, list):
                batch_results = [batch_results]

            # ترتيب النتائج حسب shortage_index
            results_map: dict[int, dict] = {}
            for r in batch_results:
                idx = r.get("shortage_index", -1)
                if 0 <= idx < len(batch):
                    results_map[idx] = r

            # بناء نتائج الدفعة بالترتيب
            for i, shortage_name in enumerate(batch):
                if i in results_map:
                    r = results_map[i]
                    wh_idx = r.get("matched_warehouse_index", -1)
                    confidence = r.get("confidence", "low")
                    reason = r.get("reason", "لم يُحدَّد سبب.")

                    if 0 <= wh_idx < len(warehouse_items):
                        all_results.append(
                            {
                                "matched": True,
                                "matched_item": warehouse_items[wh_idx],
                                "confidence": confidence,
                                "reason": reason,
                            }
                        )
                    else:
                        all_results.append(
                            {
                                "matched": False,
                                "matched_item": None,
                                "confidence": confidence,
                                "reason": reason,
                            }
                        )
                else:
                    all_results.append(
                        {
                            "matched": False,
                            "matched_item": None,
                            "confidence": "low",
                            "reason": "لم يتم تضمين هذا الصنف في استجابة النموذج.",
                        }
                    )

        except json.JSONDecodeError as e:
            logger.error("فشل تحليل استجابة Gemini كـ JSON (دفعة): %s", e)
            for _ in batch:
                all_results.append(
                    {
                        "matched": False,
                        "matched_item": None,
                        "confidence": "low",
                        "reason": f"خطأ في تحليل استجابة النموذج: {e}",
                    }
                )
        except Exception as e:
            logger.error("خطأ أثناء استدعاء Gemini API (دفعة): %s", e)
            for _ in batch:
                all_results.append(
                    {
                        "matched": False,
                        "matched_item": None,
                        "confidence": "low",
                        "reason": f"خطأ في الاتصال بالنموذج: {e}",
                    }
                )

    return all_results
