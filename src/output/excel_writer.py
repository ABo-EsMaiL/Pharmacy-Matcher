"""
وحدة كتابة نتائج المطابقة إلى ملف Excel.
Write the final Excel output with per-warehouse sheets and summary.
"""

from pathlib import Path
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


# ──────────────────────────────────────────────
# أنماط التنسيق
# ──────────────────────────────────────────────
_HEADER_FILL = PatternFill(start_color="00695C", end_color="00695C", fill_type="solid")
_HEADER_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=11)
_HEADER_ALIGNMENT = Alignment(
    horizontal="center", vertical="center", wrap_text=True
)
_CELL_FONT = Font(name="Arial", size=10)
_CELL_ALIGNMENT = Alignment(horizontal="right", vertical="center", wrap_text=True)
_THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def _apply_header_style(ws, num_cols: int) -> None:
    """تطبيق تنسيق الرأس على الصف الأول."""
    for col_idx in range(1, num_cols + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = _HEADER_ALIGNMENT
        cell.border = _THIN_BORDER


def _format_sheet(ws, num_cols: int) -> None:
    """تنسيق الورقة: تجميد الصف الأول، فلتر تلقائي، RTL، عرض الأعمدة."""
    # تجميد الصف الأول
    ws.freeze_panes = "A2"

    # فلتر تلقائي
    if ws.max_row > 0 and num_cols > 0:
        last_col_letter = get_column_letter(num_cols)
        ws.auto_filter.ref = f"A1:{last_col_letter}{ws.max_row}"

    # اتجاه الورقة من اليمين لليسار
    ws.sheet_view.rightToLeft = True

    # عرض الأعمدة التلقائي (تقدير بسيط)
    for col_idx in range(1, num_cols + 1):
        max_length = 0
        col_letter = get_column_letter(col_idx)
        for row in ws.iter_rows(
            min_col=col_idx, max_col=col_idx, min_row=1, max_row=ws.max_row
        ):
            for cell in row:
                if cell.value:
                    # حساب العرض التقريبي (الحروف العربية أعرض)
                    cell_len = len(str(cell.value))
                    max_length = max(max_length, cell_len)
        # حد أدنى 12، حد أقصى 60
        adjusted_width = min(max(max_length + 4, 12), 60)
        ws.column_dimensions[col_letter].width = adjusted_width


def _add_data_rows(ws, rows: list[list], start_row: int = 2) -> None:
    """إضافة صفوف البيانات مع التنسيق."""
    for row_idx, row_data in enumerate(rows, start=start_row):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = _CELL_FONT
            cell.alignment = _CELL_ALIGNMENT
            cell.border = _THIN_BORDER


def _truncate_sheet_name(name: str, max_len: int = 31) -> str:
    """
    اقتطاع اسم الورقة ليتوافق مع حد Excel (31 حرفاً).
    يزيل أيضاً الأحرف غير المسموح بها في أسماء الأوراق.
    """
    # إزالة الأحرف غير المسموح بها في أسماء أوراق Excel
    invalid_chars = r"[]:*?/\\"
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name[:max_len]


def _format_confidence(conf_raw: str) -> str:
    """تحويل قيم درجة التطابق الإنجليزية والتقنية إلى مصطلحات عربية واضحة."""
    if not conf_raw:
        return ""
    conf_str = str(conf_raw).strip()
    conf_lower = conf_str.lower()
    if conf_lower == "exact":
        return "تطابق تام (100%)"
    elif conf_lower == "llm":
        return "مطابقة ذكية (AI)"
    elif conf_lower.startswith("high"):
        m = re.search(r"([\d\.]+)", conf_str)
        if m:
            pct = int(float(m.group(1)) * 100)
            return f"تطابق نصي دقيق ({pct}%)"
        return "تطابق نصي دقيق"
    elif conf_str == "تأكيد يدوي (مراجعة)":
        return conf_str
    return conf_str


def write_results_excel(results: dict, output_path: Path) -> Path:
    """
    إنشاء ملف Excel منظم يحتوي على:
        - ملخص ديناميكي مربوط بمعادلات Excel التلقائية
        - ورقة لكل مخزن تحتوي على المطابقات المؤكدة
        - ورقة للأصناف التي تحتاج مراجعة
        - ورقة للأصناف التي لم يُعثر عليها

    المعاملات:
        results: قاموس يحتوي على:
            - warehouse_results: نتائج كل مخزن
            - not_found: الأصناف غير الموجودة
            - summary: ملخص إحصائي
        output_path: مسار ملف Excel الناتج.
    """
    wb = Workbook()

    # ────────────────────────────────────────
    # ورقة الملخص (ديناميكية مربوطة بالمعادلات)
    # ────────────────────────────────────────
    ws_summary = wb.active
    ws_summary.title = "ملخص"

    summary = results.get("summary", {})
    warehouse_results = results.get("warehouse_results", {})

    summary_headers = ["البند", "العدد", "النسبة"]
    ws_summary.append(summary_headers)
    _apply_header_style(ws_summary, len(summary_headers))

    raw_total = summary.get("total_shortages", 0)
    unique_total = summary.get("unique_shortages", 0)

    # Row 2: إجمالي طلبات النواقص (الأسطر الأصلية)
    ws_summary.append(["إجمالي طلبات النواقص (الأسطر)", raw_total, "-"])

    # Row 3: إجمالي الأصناف الفريدة
    ws_summary.append(["إجمالي الأصناف الفريدة (المطلوبة)", unique_total, "100%"])

    # Row 4: تم مطابقتها (مجموع مطابقة المخازن)
    num_wh = len(warehouse_results)
    wh_sum_formula = f"=SUM(B9:B{8 + num_wh})" if num_wh > 0 else "0"
    ws_summary.append(["تم مطابقتها (مجموع المخازن)", wh_sum_formula, "=IF(B3>0, B4/B3, 0)"])

    # Row 5: لم يُعثر عليها
    ws_summary.append(["لم يُعثر عليها", "=MAX(0, COUNTA('لم يُعثر عليه'!A:A)-1)", "=IF(B3>0, B5/B3, 0)"])

    # Row 6: تحتاج مراجعة
    ws_summary.append(["تحتاج مراجعة", "=MAX(0, COUNTA('يحتاج مراجعة'!B:B)-1)", "=IF(B3>0, B6/B3, 0)"])

    # Row 7: صف فارغ
    ws_summary.append([])

    # Row 8: جدول تفاصيل كل مخزن
    ws_summary.append(["─── تفاصيل المخازن ───", "عدد المطابقات", "أصناف للمراجعة"])
    for c_idx in range(1, 4):
        c = ws_summary.cell(row=8, column=c_idx)
        c.fill = _HEADER_FILL
        c.font = _HEADER_FONT
        c.alignment = _HEADER_ALIGNMENT
        c.border = _THIN_BORDER

    # صفوف المخازن (Rows 9+)
    detail_row = 9
    for wh_name in warehouse_results.keys():
        sheet_name = _truncate_sheet_name(wh_name)
        matched_formula = f"=MAX(0, COUNTA('{sheet_name}'!A:A)-1)"
        review_formula = f'=COUNTIF(\'يحتاج مراجعة\'!D:D, "{wh_name}")'
        ws_summary.append([wh_name, matched_formula, review_formula])
        detail_row += 1

    # تطبيق التنسيق والخطوط على كل خلايا الملخص
    for r in range(2, detail_row):
        if r == 7 or r == 8:
            continue
        for c in range(1, 4):
            cell = ws_summary.cell(row=r, column=c)
            cell.font = _CELL_FONT
            cell.alignment = _CELL_ALIGNMENT
            cell.border = _THIN_BORDER

    # تنسيق النسب المئوية كـ %
    ws_summary.cell(row=2, column=3).alignment = _CELL_ALIGNMENT
    ws_summary.cell(row=3, column=3).alignment = _CELL_ALIGNMENT
    ws_summary.cell(row=4, column=3).number_format = "0.0%"
    ws_summary.cell(row=5, column=3).number_format = "0.0%"
    ws_summary.cell(row=6, column=3).number_format = "0.0%"

    _format_sheet(ws_summary, len(summary_headers))

    # ────────────────────────────────────────
    # ورقة لكل مخزن (المطابقات المؤكدة فقط)
    # ────────────────────────────────────────
    for wh_name, wh_data in warehouse_results.items():
        sheet_name = _truncate_sheet_name(wh_name)
        ws_wh = wb.create_sheet(title=sheet_name)

        headers = ["اسم الصنف المطلوب", "اسم الصنف في المخزن", "درجة التطابق"]
        ws_wh.append(headers)
        _apply_header_style(ws_wh, len(headers))

        matched_items = wh_data.get("matched", [])
        rows = []
        for match in matched_items:
            shortage_name = match.get("shortage_item", "")
            warehouse_item = match.get("warehouse_item", "")
            confidence = _format_confidence(match.get("confidence", ""))
            rows.append([shortage_name, warehouse_item, confidence])

        _add_data_rows(ws_wh, rows)
        _format_sheet(ws_wh, len(headers))

    # ────────────────────────────────────────
    # ورقة "لم يُعثر عليه"
    # ────────────────────────────────────────
    ws_not_found = wb.create_sheet(title="لم يُعثر عليه")
    nf_headers = ["اسم الصنف", "الملف المصدر"]
    ws_not_found.append(nf_headers)
    _apply_header_style(ws_not_found, len(nf_headers))

    not_found_items = results.get("not_found", [])
    nf_rows = []
    for item in not_found_items:
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        source = item.get("source", "") if isinstance(item, dict) else ""
        nf_rows.append([name, source])

    _add_data_rows(ws_not_found, nf_rows)
    _format_sheet(ws_not_found, len(nf_headers))

    # ────────────────────────────────────────
    # ورقة "يحتاج مراجعة"
    # ────────────────────────────────────────
    ws_review = wb.create_sheet(title="يحتاج مراجعة")
    review_headers = [
        "القرار (اختر)",
        "اسم الصنف المطلوب",
        "اسم المرشح في المخزن",
        "المخزن",
        "السبب",
    ]
    ws_review.append(review_headers)
    _apply_header_style(ws_review, len(review_headers))

    # تجميع جميع الأصناف التي تمت مطابقتها بالفعل في أي مخزن لتجنب إشغال الصيدلي بها
    all_confirmed_shortages = set()
    for wh_data in warehouse_results.values():
        for match in wh_data.get("matched", []):
            name = match.get("shortage_item", "")
            if name:
                all_confirmed_shortages.add(name.strip())

    review_rows = []
    seen_review_pairs = set()
    for wh_name, wh_data in warehouse_results.items():
        for item in wh_data.get("needs_review", []):
            req_item = item.get("shortage_item", "").strip()
            wh_item = item.get("warehouse_item", "").strip()
            if req_item in all_confirmed_shortages:
                continue
            pair_key = (req_item, wh_item, wh_name)
            if pair_key in seen_review_pairs:
                continue
            seen_review_pairs.add(pair_key)
            review_rows.append(
                [
                    "", # خانة القرار فارغة ليختار منها الصيدلي
                    req_item,
                    wh_item,
                    wh_name,
                    item.get("reason", ""),
                ]
            )

    _add_data_rows(ws_review, review_rows)
    _format_sheet(ws_review, len(review_headers))

    # إضافة Dropdown List (Data Validation) لعمود القرار
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1='"✅ مطابق,❌ غير مطابق"', allow_blank=True)
    ws_review.add_data_validation(dv)
    
    # تطبيق الـ Dropdown على كل الخلايا في العمود الأول (تحت الرأس)
    if len(review_rows) > 0:
        dv.add(f"A2:A{len(review_rows) + 1}")

    # ────────────────────────────────────────
    # حفظ الملف
    # ────────────────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(output_path))
    print(f"[+] Results successfully saved to: {output_path}")

create_excel_report = write_results_excel
