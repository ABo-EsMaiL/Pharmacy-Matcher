# خطة العمل المعمارية: محرك استخراج البيانات بالرؤية البصرية (Pharmacy Vision Extraction Engine)

تهدف هذه الخطة إلى الانتقال الجذري والكامل من محرك الـ OCR القديم (`Unstructured.io`) إلى محرك **Google Gemini Vision** فائق الدقة، لمعالجة قوائم ومطابقات الأدوية صفحة بصفحة مع استخراج عربي سليم 100%، وبناء بنية تحتية منظمة تدعم ملفات (PDF, Excel, Markdown) مع نظام كاش واستئناف ذكي (Resume & Cache) وهيكلة مجلدات معزولة لكل مشروع/عملية.

---

## User Review Required

> [!IMPORTANT]
> **الحفاظ على الأصل (Safe Baseline):**
> سيتم نسخ المشروع الحالي `D:\AI_Engineer\Pharmacy-agy` بالكامل إلى المسار المستقل `D:\AI_Engineer\Pharmacy-agy-vision`. النسخة الأصلية لن يتم لمسها أو تعديل أي سطر فيها، لتظل بمثابة بيئة احتياطية آمنة (Fallback/Rollback).

> [!NOTE]
> **ثبات منظومة المطابقة والتصنيف:**
> لن يتم المساس بخوارزميات المطابقة والتصنيف الدوائي (`FastCoordinator` و `Coordinator` و `text_match`)؛ التغيير يتركز فقط في طبقة الاستخراج وتغذية المطابقة ببيانات نقية بصيغة الموحدة:
> `{"items": [{"item_name_raw": "...", "source_page": N, "source_file": "..."}]}`.

---

## Open Questions

> [!NOTE]
> لا توجد أسئلة معلقة حالياً حيث تم التحقق بنجاح من الـ Vision Gateway محلياً على البورت 8001، ومطابقة النتائج الأولية للأدوية بدقة 100%. إذا كان لديك أي تفضيل إضافي لمسميات المجلدات أو بنية الكاش، يرجى توضيحه.

---

## الهيكلية المعمارية الجديدة (Architecture Overview)

```
D:\AI_Engineer\Pharmacy-agy-vision/
├── src/
│   ├── extract/
│   │   ├── file_handler.py           # الموجه العام لكافة صيغ الملفات (PDF, XLSX, MD)
│   │   ├── gemini_vision_extractor.py # [NEW] محرك الاستخراج البصري صفحة بصفحة
│   │   ├── excel_reader.py            # قراءة الإكسيل الذكية وكشف أعمدة الأصناف
│   │   └── markdown_reader.py         # [NEW] قراءة الجداول والقوائم من ملفات Markdown
│   ├── fast_match/                   # محرك المطابقة السريع (ثابت بدون تعديل)
│   ├── match/                        # محرك المطابقة المتقدم (ثابت بدون تعديل)
│   └── output/                       # تصدير النتائج للإكسيل (ثابت)
├── data/
│   └── processes/
│       └── PROC-XXX/                 # مجلد مستقل لكل عملية
│           ├── input_shortages/      # ملفات النواقص (Excel, PDF, MD)
│           ├── input_warehouses/     # ملفات المخازن (Excel, PDF, MD)
│           ├── cache/                # [NEW] كاش منظم معزول داخل كل عملية
│           │   └── vision/
│           │       └── <file_hash>/
│           │           ├── manifest.json         # تتبع حالة الاستئناف والصفحات المكتملة
│           │           ├── pages/
│           │           │   ├── page_1.webp       # صور الصفحات عالية الدقة
│           │           │   └── page_2.webp
│           │           └── results/
│           │               ├── page_1.json       # استخراج الـ Vision لكل صفحة
│           │               └── page_2.json
│           └── output/               # تقارير الإكسيل الناتجة عن العملية
```

---

## Proposed Changes

### 1. النسخ والتهيئة الأولية للمشروع الجديد (Cloning & Setup)
- نسخ المجلد `D:\AI_Engineer\Pharmacy-agy` إلى `D:\AI_Engineer\Pharmacy-agy-vision` مع استبعاد الملفات المؤقتة القديمة ومجلدات الكاش المنتهية.
- ضبط التبعيات والمجلدات في النسخة الجديدة.

---

### 2. طبقة الاستخراج والمعالجة (Extraction Layer)

#### [NEW] [gemini_vision_extractor.py](file:///d:/AI_Engineer/Pharmacy-agy-vision/src/extract/gemini_vision_extractor.py)
* **المسؤولية:**
  1. حساب بصمة الملف الرقمية (`SHA-256`) للتأكد من هوية الملف وحالته.
  2. إنشاء وإدارة مجلد الكاش المعزول داخل العملية:
     `data/processes/PROC-XXX/cache/vision/<file_hash>/`
  3. قراءة ملف المانيفست `manifest.json`:
     - فحص ما إذا كانت بعض الصفحات قد استُخرجت سابقاً (Resume Capability).
     - إذا تم استخراج جميع الصفحات مسبقاً، يتم تحميل النتيجة فوراً خلال أقل من ثانية واحدة دون استهلاك الـ Gateway.
  4. لكل صفحة غير مستخرجة بعد:
     - تحويل الصفحة إلى صورة WebP عالية الدقة بحجم مضغوط (`pypdfium2` بمقياس `scale=2.5`, `quality=85`، حجم ~250-300KB).
     - حفظ الصورة في `pages/page_N.webp`.
     - تحويلها إلى Base64 وإرسال طلب مستقل إلى `http://127.0.0.1:8001/v1/chat/completions`.
     - حفظ استجابة الصفحة كملف JSON مستقل في `results/page_N.json`.
     - تحديث `manifest.json` بالصفحة المكتملة فوراً (حتى لو انقطع الاتصال أو أُغلق البرنامج عند الصفحة 10 من 22، يستأنف فوراً من الصفحة 11).
  5. دمج نتائج جميع الصفحات بترتيبها الأصلي وإرجاع قائمة موحدة ومطابقة لمعيار السيستم.

#### [NEW] [markdown_reader.py](file:///d:/AI_Engineer/Pharmacy-agy-vision/src/extract/markdown_reader.py)
* **المسؤولية:**
  - استخراج أسماء الأدوية من ملفات الـ Markdown (`.md`, `.markdown`).
  - دعم الجداول (Markdown Tables) بالتعرف التلقائي على عمود اسم الصنف.
  - دعم القوائم النقطية والرقمية (Bullet & Numbered lists).
  - إرجاع مخرجات موحدة: `{"item_name_raw": str, "source_page": 1, "source_file": str}`.

#### [MODIFY] [file_handler.py](file:///d:/AI_Engineer/Pharmacy-agy-vision/src/extract/file_handler.py)
* **التعديل:**
  - إضافة امتدادات Markdown (`.md`, `.markdown`).
  - توجيه ملفات PDF مباشرة إلى `gemini_vision_extractor.py` بدلاً من Unstructured القديم.
  - تمرير سياق العملية (Process Context / Output Directory) لضمان حفظ الكاش في مجلد العملية المناسب بدلاً من الـ temp العشوائي.

#### [MODIFY] [config.py](file:///d:/AI_Engineer/Pharmacy-agy-vision/src/config.py)
* **التعديل:**
  - إضافة إعدادات الـ Vision Gateway:
    - `vision_api_url`: القيمة الافتراضية `http://127.0.0.1:8001/v1/chat/completions`.
    - `vision_model`: `gemini-3.8-flash`.

---

### 3. التطبيق المكتبي وإدارة السيرفرات (Desktop App & Integration)

#### [MODIFY] [server_manager.py](file:///d:/AI_Engineer/Pharmacy-agy-vision/desktop_app/server_manager.py)
* **التعديل:**
  - إضافة تعريف سيرفر الرؤية البصرية `MSEMAX-GAIStudio-vision` على البورت `8001`.
  - التحقق من جهوزيته والتعرف عليه ضمن قائمة السيرفرات النشطة.

---

## آلية الاستئناف والكاش الذكي (Resumability & Cache Manifesto)

```json
{
  "file_name": "المكرومي المنصورة.pdf",
  "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "total_pages": 4,
  "completed_pages": [1, 2],
  "status": "in_progress",
  "items_extracted_so_far": 48,
  "last_updated": "2026-09-25T16:30:00"
}
```
* **عند بدء المعالجة:** يفحص السيستم `completed_pages`.
* إذا وُجدت الصفحة 1 و 2، يتم تجاوز إرسالهما للمتصفح/الـ AI Studio، ويتم استئناف الصفحة 3 مباشرة.
* عند اكتمال الصفحة الأخيرة، تتغير الحالة إلى `"completed"`.
* إذا تم تشغيل نفس الملف مستقبلاً في أي مكان أو عملية، يكتشف السيستم تطابق الـ Hash ويحمل النتائج فورياً دون أي استهلاك للوقت أو الـ Token.

---

## Verification Plan

### 1. الاختبار الآلي والوظيفي (Automated & Unit Testing)
- تشغيل اختبار لقراءة وتحويل PDF تجريبي إلى WebP والتحقق من الأحجام والدقة وجودة النص.
- تشغيل اختبار لقارئ الـ Markdown الجديد على ملف تجريبي يحتوي على جداول وقوائم والتأكد من استخراج الأصناف بدقة.

### 2. اختبار الاستئناف والكاش (Resume & Interruption Test)
- محاكاة تشغيل ملف متعدد الصفحات وإيقافه بعد استخراج صفحة، ثم إعادة تشغيله للتأكد من أنه يستأنف من الصفحة التالية دون إعادة استخراج الصفحة الأولى.

### 3. الاختبار الحقيقي المتكامل (End-to-End Real Test)
- تشغيل استخراج الـ 4 صفحات الكاملة لملف `المكرومي المنصورة.pdf` في بيئة `Pharmacy-agy-vision`.
- مراجعة تقرير الاستخراج الكامل ومقارنته بالأصناف المرجعية.
- تمرير المخرجات لمحرك المطابقة `FastCoordinator` والتأكد من إتمام العملية بالكامل وإصدار ملف الإكسيل النهائي بنجاح.
