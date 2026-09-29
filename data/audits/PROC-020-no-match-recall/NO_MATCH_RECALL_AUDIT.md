# NO_MATCH RECALL AUDIT — PROC-020

Audit only. No matching code, Decision Graph or original process files were changed; no new PROC was created.

| Metric | Count |
|---|---:|
| total_no_match | 461 |
| no_match_with_no_plausible_candidate | 337 |
| no_match_with_plausible_candidate | 124 |
| recovered_match | 27 |
| recovered_review | 15 |
| supported_true_no_match_after_audit | 68 |
| unresolved_with_plausible_candidate | 14 |
| no_plausible_candidate_is_not_proven_absence | 337 |
| pages | 46 |
| catalog_items | 2718 |
| all_pairs_scored | 1252998 |
| source_runtime_unchanged | True |
| new_proc_created | False |

Counts are unique requests. A recovered MATCH takes precedence over REVIEW across warehouses. Amr-only discoveries for requests already matched elsewhere are reported separately, not added to the 461 denominator.

No plausible candidate found is not proof that the item is absent. Supported NO_MATCH means plausible audited candidates were rejected for explicit conflicting evidence; unresolved cases are not counted as confirmed negatives.

All 46 cached pages / 2,718 rows were scored using independent character n-grams, length-normalized edit distance, full-character alignment, Arabic OCR dot-shape similarity and token coverage. Rank unions, every exact/one-edit name and the nearest two per warehouse were retained without the production gate. Raw original names were sent to the same configured gateway, Batch 75, Search OFF, Thinking HIGH, Fresh Chat ON.

This is an evidence-based recall audit, not an externally labeled ground-truth corpus or a proof that all possible false negatives were eliminated.

Audit response validation: inconsistent plausible-ID lists were re-adjudicated. Swapped empty item-ID/list fields were normalized with a separate provenance log; no business status or nonempty ID was changed by that normalization. Conflicting positive/negative judgments across those replies remain unresolved. Provider failures are not item decisions.

## Recovered requests

| Requested | Audit outcome | Warehouse item | Warehouse / page | Current rejection / route |
|---|---|---|---|---|
| انوكسيكام 20مجم 20قرص س ج | review | انوكسيكام لبوس باكت 54 | الهضبة الاثنين نقدى0.pdf / 3 | ('ambiguous', 'missing_strength') |
| اوجرام457مجم بودره60مل | match | اوجرام ٤٥٧مجم شراب | كيور فارما خاص.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| اورامكس 30مل اسبراي س ج | match | اورامكس بخاخ كبار/باكت 56 | الهضبة الاثنين نقدى0.pdf / 4 | ('reject', 'no_meaningful_name_evidence') |
| ايجيكوستات بلس /مينالاكس | match | ايجيكيوستات بلس اقراص بديل مينالاكس | كيور فارما خاص.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| ايفرزين لوشن | review | ايفرزين كريم | كيور فارما خاص.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| بانثينول النيل2%كريم وسط | match | بانثينول كريم كبييير سعر قدييم باكو 25 | جملة العمروووو.pdf / 1 | ('reject', 'no_meaningful_name_evidence') |
| برونشيكم شراب س ج | match | برونشيكم شراب اليكسير/افنتس | السلام شبين.pdf / 1 | ('reject', 'no_meaningful_name_evidence') |
| بيتادين دش مهبلي س ج | review | بيتادين مطهر/النيل | السلام شبين.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| بيتادين شامبو120مل س ج | review | بيتادين مطهر/النيل | السلام شبين.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| بيتادين شامبو60مل س ج | review | بيتادين مطهر/النيل | السلام شبين.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| بيدرو اسبراي مطهر س ق | match | بيدرو سبراى للفم /باكت 96 | الهضبة الاثنين نقدى0.pdf / 7 | ('reject', 'no_meaningful_name_evidence') |
| بيدرو كريم تفتيح | review | بيدرو غسول/بليزا | الهضبة الاثنين نقدى0.pdf / 7 | ('reject', 'no_meaningful_name_evidence') |
| دابسوكيرل 50مجم جيل | match | دابسوكيريل جيل 30 جم | الهضبة الاثنين نقدى0.pdf / 10 | ('ambiguous', 'ocr_or_incomplete_name') |
| ديكلوفين 100مجم5لبوسة كبار ث س ج | review | ديكلوفين امبول سعر جديد ٣٦ ج | المكرومي المنصورة.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| ديورافوس 1 امبول | match | ديورافوس امبول = ديبروفوس | كيور فارما خاص.pdf / 4 | ('reject', 'no_meaningful_name_evidence') |
| ريبايون اسبراي | review | ريبايون ان جيل بديل ريباريل ٥٠ جم | المكرومي المنصورة.pdf / 2 | ('reject', 'no_meaningful_name_evidence') |
| زانوجليد4/30اقراص س ج | match | زانوجليد 4 مج اقراص/ باكت 60 | الهضبة الاثنين نقدى0.pdf / 12 | ('ambiguous', 'ocr_or_incomplete_name') |
| زوفيراكس10 مجم كريم جلد س ج | review | زوفيراكس شراب/باكو24 | مخزن الحياة فارم اسكندريه-170.pdf / 3 | ('reject', 'no_meaningful_name_evidence') |
| سولو لوسيون مرطب | match | سولو لوسيون/باكت 25 | الهضبة الاثنين نقدى0.pdf / 13 | ('reject', 'no_meaningful_name_evidence') |
| سيبروفلوكساسين محلول وريدي | review | بيروفلوكساسين 500 مج قرص اورجانو | الهضبة الاثنين نقدى0.pdf / 13 | ('reject', 'no_meaningful_name_evidence') |
| سيفيتيل 1جم | match | سيفيتيل اجم اقراص فوار | كيور فارما خاص.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |
| سينوبريل كواقراص س ج | match | سينوبريل كو اقراص/جلوبال باكت 90 | الهضبة الاثنين نقدى0.pdf / 14 | ('reject', 'no_meaningful_name_evidence') |
| فلابو 600 اقراص | review | فلابو نقط/دلتا فارم | السلام شبين.pdf / 4 | ('ambiguous', 'ocr_or_incomplete_name') |
| فيتا دي ثري4000ميكروفيلم | match | فيتا د 3 4000 لزقة باكت 200 | الهضبة الاثنين نقدى0.pdf / 15 | ('reject', 'no_meaningful_name_evidence') |
| فيتا زنك  كبسول | match | فيتازنك ان كبسول\ايبيكو | الهضبة الاثنين نقدى0.pdf / 15 | ('reject', 'no_meaningful_name_evidence') |
| قرفة بالجنزبيل ايزيس | match | ايزيس زنجبيل بالقرفه 12 فلتر | الهضبة الاثنين نقدى0.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |
| كارنيتول بلس برطمان س ج | match | كارنيتول بلس كبسول جديد | كيور فارما خاص.pdf / 6 | ('reject', 'no_meaningful_name_evidence') |
| كانديكيور لبوس مهبلي | review | كاندكيور كريم عادي/باكت 10 | الهضبة الاثنين نقدى0.pdf / 17 | ('reject', 'no_meaningful_name_evidence') |
| لاكسيول بي ملين اقراص | match | لاكسيول بي ۲ شريط | كيور فارما خاص.pdf / 7 | ('reject', 'no_meaningful_name_evidence') |
| لبن بيبيلاك 3 بيبي جونيور | match | بيبيلاك 3 بيبي جونيور/باكت 12 تشغيل | الهضبة الاثنين نقدى0.pdf / 7 | ('reject', 'no_meaningful_name_evidence') |
| ليليبل10مجم اقراص | review | ليلبيل اكياس /باكت42 | الهضبة الاثنين نقدى0.pdf / 19 | ('reject', 'no_meaningful_name_evidence') |
| ماريفان3مجم3شريط س ج | match | ماريفان 3 مجم/جلاكسو | السلام شبين.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |
| موفليكس نانو اسبراي | match | موف ليكس سبراى /باكت41 | الهضبة الاثنين نقدى0.pdf / 20 | ('reject', 'no_meaningful_name_evidence') |
| ميلجا ماكس30قرص | match | ليمتلس ميلجا ماكس | كيور فارما خاص.pdf / 7 | ('reject', 'no_meaningful_name_evidence') |
| ميوكوسول شراب اطفال س ج | review | ميوكوسول كبسول/ باكت 20 | الهضبة الاثنين نقدى0.pdf / 20 | ('reject', 'no_meaningful_name_evidence') |
| ناتريلكس اس ار 30قرص س ج | match | ناتريليكس اس ار سعرجديد | مخزن الحياة فارم اسكندريه-170.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |
| نيتروماك ريتارد2.5مجم كبسول | match | نيتروماك ريتارد كبسول/التنشيط | السلام شبين.pdf / 5 | ('ambiguous', 'ocr_or_incomplete_name') |
| نيتروماك ريتارد2.5مجم كبسول س ج | match | نيتروماك ريتارد كبسول/التنشيط | السلام شبين.pdf / 5 | ('ambiguous', 'ocr_or_incomplete_name') |
| نيفيلوب12.5/5مجم بلاس20قرص | match | نيفيلوب بلس ١٢٫٥/٥مجم قرص | كيور فارما خاص.pdf / 7 | ('reject', 'combination_mismatch') |
| هيدروكين 200مجم 20قرص س ج | match | هيدروكين\مينا | السلام شبين.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |
| هيرو دي3+كي2 نقط | match | هيرو فى اى دى ثرى كيه نقط"جديد | كيور فارما خاص.pdf / 8 | ('reject', 'no_meaningful_name_evidence') |
| ون تو ثري 20قرص س ج | review | وان تو ثرى شراب\الكان فارما | السلام شبين.pdf / 5 | ('reject', 'no_meaningful_name_evidence') |

## Amr-only adjudications

| Requested | Outcome | Warehouse item | Reason |
|---|---|---|---|
| سيريلاك 150جم قمح ساده | no_match |  | لا يوجد منتج مطابق في المستودع |
| روزاسيف 30 كبسوله/ برايم روز | no_match |  | لا يوجد منتج مطابق في المستودع |
| سيريلاك 125جم تمر وقمح | no_match |  | لا يوجد منتج مطابق في المستودع |
| ديوراسيف  250مجم شراب س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| ديبوفيت  5امبول س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| فيرنيلار اقراص | no_match |  | لا يوجد منتج مطابق في المستودع |
| ليفوفلوكساسين750مجم 5قرص س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| ريبايون اسبراي | no_match |  | لا يوجد منتج مطابق في المستودع |
| رانديل10مجم اقراص | no_match |  | لا يوجد منتج مطابق في المستودع |
| ميوكوسول شراب اطفال س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| سكروفير امبول | no_match |  | لا يوجد منتج مطابق في المستودع |
| ديكسافين شراب | no_match |  | لا يوجد منتج مطابق في المستودع |
| هيرو دي3+كي2 نقط | no_match |  | لا يوجد منتج مطابق في المستودع |
| كارنيتول بلس برطمان س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| ترايلبتال300مجم50قرص | no_match |  | لا يوجد منتج مطابق في المستودع |
| افروزوليد150 مل شراب | no_match |  | لا يوجد منتج مطابق في المستودع |
| فاركوسين مرهم س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| امبوفير 5امبول س ج | match | امبوفير حقن جديدد | تطابق تام للمنتج امبوفير حقن |
| زانثيبوكس 80مجم اقراص | no_match |  | لا يوجد منتج مطابق في المستودع |
| نيوكلاف642اكسترا شراب100مل س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| موفليكس نانو اسبراي | no_match |  | لا يوجد منتج مطابق في المستودع |
| سيبروفلوكسميت 500مجم | no_match |  | لا يوجد منتج مطابق في المستودع |
| ليفوفلوكساسين500مجم اقراص | no_match |  | لا يوجد منتج مطابق في المستودع |
| مينرو10كيس | no_match |  | لا يوجد منتج مطابق في المستودع |
| ريتشي بانثينول كريم ادفانس | no_match |  | لا يوجد منتج مطابق في المستودع |
| لبن هيرو بيبي 2 | unresolved | هيرو 222 نيوتراديفنس 384 | تطابق هيرو 2 واختلاف السعر لا يمنع |
| جيت وايت كريم | no_match |  | لا يوجد منتج مطابق في المستودع |
| رايوفيت شراب س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| بانثينول النيل2%كريم وسط | match | بانثينول كريم كبييير سعر قدييم باكو 25 | تطابق المنتج واختلاف الحجم لا يمنع |
| بيدرو اسبراي مطهر س ق | no_match |  | لا يوجد منتج مطابق في المستودع |
| نيوروتون30قرص س ق | no_match |  | لا يوجد منتج مطابق في المستودع |
| بوديكسان 0.5مجم حقن | no_match |  | لا يوجد منتج مطابق في المستودع |
| ايبويتين4000وحدة  امبول ث س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| يوريفين فوار | no_match |  | لا يوجد منتج مطابق في المستودع |
| افيروكوكسيب90مجم20قرص س ج | match | افيروكوكسيب 90مجم-32ب | تطابق تام في الاسم والتركيز |
| ترايتكت اطفال صابونه | no_match |  | لا يوجد منتج مطابق في المستودع |
| اسيكلوفير 5%10 جم كريم س ج | no_match |  | لا يوجد منتج مطابق في المستودع |
| ستيمولان امبول | review | ستيميولان 400مجم كبسول | اختلاف الشكل الصيدلي امبول مقابل كبسول |

## All 19 Amr warehouse rows

| Warehouse item | Relevant requested item | Audit finding |
|---|---|---|
| افيروكوكسيب 90مجم-32ب | افيروكوكسيب90مجم20قرص س ج | match; ('reject', 'product_variant_conflict');  |
| امبوفير حقن جديدد | امبوفير 5امبول س ج | match; ('reject', 'no_meaningful_name_evidence');  |
| ايزوتريتينوين 10 مجم 3 شرييبط -28 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| ايزوتريتينوين 20م جديديد -50 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| بانادول اكسترا 48 قرص-96ب | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| بانثينول كريم كبييير سعر قدييم باكو 25 | بانثينول النيل2%كريم وسط | match; ('reject', 'no_meaningful_name_evidence');  |
| ترايكوبافيت 100مجم 3شريط | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| رانسيف 500 مجم قرص جديديد45 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| ستيميولان 400مجم كبسول | ستيمولان امبول | review; ('ambiguous', 'ocr_or_incomplete_name');  |
| كليكسان 40مجم-84 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| لوفير 400 سعر جديديد باكو 45 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| لوفير 800 سعرجدديد-باكو25 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| ليفوفلوتانيت 750 فيال باكو 12 كرتونه 144 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| هيرو 111 عادى جديد -12ب لا يفرط | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| هيرو 222 نيوتراديفنس 384 | لبن هيرو بيبي 2 | unresolved; ('reject', 'no_meaningful_name_evidence'); product_variant_or_numeric_context_unresolved; audit_evidence_unresolved |
| هيرو اتش ايه جديد 499 | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| هيرو اف ال جديدج ك 12 لايفرط | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| هيرو ايه ار جديددد لايفرط | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |
| هيرو دايجست 12 لايفرط | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |

## Unresolved cases

| Requested | Candidate / evidence | Why not counted as recovered or true NO_MATCH |
|---|---|---|
| املوسازايد40/12.5/5مجم30قرص س ج | املوساز اید ٥/١٢,٥/٤٠ | explicit_strength_guard_blocked_positive; لا توجد أسماء مطابقة للمنتج المطلوب |
| انتودين 20مجم30قرص س ج | انتودين 40 مج 30 قرص/ باكت 35; انتودین ٤٠ مجم اقراص; انتودين 40 م ج م 3ش ي ط / باكو 35; انتودين ۲۰جم ۳۰ قرص جدید; انتودين ٤٠مجم قرص | explicit_strength_guard_blocked_positive; اختلاف في التركيز بين 20 و 40 |
| ايزوميم 40مجم اقراص | ايزومومب 40 مج اقراص باكت 144 | llm_identity_disagreement_needs_source_evidence |
| ايموكسكلاف642مجم شراب | ايموكسكلاف ٦٤٢,٩ شراب; ايموكسكلاف 1 جرام /باكو10; ايموكسكلاف ۳۱۲ شراب / ايبكو; ايموكسكلاف ٤٥٧ مجم شراب; ايموكسكلاف 1 جم اقراص/باكت 90; ايموكسكلاف ١جم قرص | explicit_strength_guard_blocked_positive; لا توجد أسماء مطابقة للمنتج المطلوب |
| بيليبوسيس 20 قرص | اليمبوسيس 2.5 مج اقراص; اليمبوسيس 5 مج اقراص | الاسم المحتمل هو اليمبوسيس لكن الطلب يفتقر للتركيز ويتوفر تركيزان مختلفان (2.5 و5 مج) |
| تورسامولكس10مجم اقراص س ج | تورسامولكس ۱۰جم اقراص; تورسامولكس ۲۰ جم اقراص; تورسامولكس 20 مج اقراص/باكت 52 | explicit_strength_guard_blocked_positive; لا توجد أسماء مطابقة للمنتج المطلوب |
| ريتشي بانثينول كريم ادفانس | ريتشى بانثينول 20جم كريم/باكت 25; وريتشى بانثينول 50جم كريم/باكت 10; يوريتشى بانثينول ادفانس كريم جيل; يوريتشى بانثينول جيل/باكت90 | llm_identity_disagreement_needs_source_evidence; لا يوجد منتج مطابق في المستودع; توجد اختلافات في بدايات الاسم عبر الصفوف مع قص عند حدود الجدول. المعاينة لا تثبت وحدها قراءة موحدة لكل الصفوف؛ يبقى تعارض حكم الهوية السابق والحالي معلنًا وغير محسوم. |
| زوركال20مجم14قرص س ج | زوركال ٤٠ مجم ١٤ قرص ٩٦ ج; زوركال ۲۰ جم اقراص; زوركال ٤٠ جم ١٤ اقراص; زوركال ٤٠ مجم اقراص ۲۸ قرص | explicit_strength_guard_blocked_positive; لا توجد أسماء مطابقة للمنتج المطلوب |
| ستلاسيل 5 جم اقراص س ج | ستلاسيل 5 مج اقراص/باكت 150 | explicit_strength_guard_blocked_positive; لا توجد أسماء مطابقة للمنتج المطلوب |
| سيتال1جم اقراص س ج | سيتال اقراص 500 س ج; سيتال شراب/ايبيكو; سيتال شراب س ج باكت20; سيتال ٥٠٠ مجم اقراص; سيتال لبوس /باكت 65; سيتال شراب باكت 20; سيتال شراب قديم; سيتال نقط; سيتال شراب س.ج ۳۱ج; سيتال اكسترا /ايبيكو | audit_evidence_unresolved; اختلاف في التركيز بين 1جم و 500مجم; رفض LLM جميع مرشحي سيتال بسبب 500mg في الأقراص، رغم أن قائمة plausible تتضمن شرابًا ولبوسًا ونقطًا بلا تركيز مذكور. تعارض الأقراص صحيح لكنه لا يثبت رفض بقية الهيئات؛ لا يُحتسب الطلب true NO_MATCH بعد التدقيق. |
| سيترونوميت 4 مجم اقراص س ج | سيترونوميت 8 مل 4 قرص | audit_evidence_unresolved; اختلاف في التركيز بين 4 و 8; النص المخزني هو سيترونوميت 8 مل 4 قرص. سبب رفض LLM أعاد كتابة 8 مل على أنها 8 مجم. لا يثبت النص تعارض strength مع 4mg؛ تبقى دلالة الرقم/الوحدة غير محسومة ولا تُحتسب true NO_MATCH. |
| فلوب شراب س ج | فلابو نقط/دلتا فارم | audit_evidence_unresolved; اقتراح REVIEW اعتمد على افتراض أن فلوب وفلابو نفس الاسم، دون دليل مستقل كافٍ من النص على هذا الربط. لا يُحكم بأنهما مختلفان تلقائيًا، لكن لا يُعد الاقتراح استرجاعًا مؤكدًا. المرشح يبقى ظاهرًا في نتائج التدقيق. |
| فيوسيدل كريم | فيوسيدين ۲۰جم كريم/ وسط; فيوسيدين كريم كبير; فيوسيدين كريم 20 جرام وسط | llm_identity_disagreement_needs_source_evidence; audit_evidence_unresolved; اختلف حكم استجابات تدقيق نفس المرشحين بين الرفض والقبول. حُفظ المرشح المحتمل ولم يُحسب استرجاعًا مؤكدًا أو غيابًا مؤكدًا. |
| ليبانتيل145اقراص س ج | ليبانتيل 160سوبرا اقراص/باكت 100; ليبانتيل سوبرا اقراص | نقص بيانات التركيز يمنع تأكيد المطابقة |

## Every original NO_MATCH request

| Requested | Audit category | Plausible warehouse items | Audit reason |
|---|---|---|---|
| XXكال فود د3 30قرص برطمانXX | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة لـ كال فود د3 بين المرشحين |
| ابيتنس اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ابيتنس بين المرشحين |
| ابيسفين 1جم عضل فيال | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ابيسفين بين المرشحين |
| ابيكوفلوسين200مجم10قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ابيكوفلوسين بين المرشحين |
| ابيماج فوار | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ابيماج بين المرشحين |
| ابيمول اطفال 5 لبوسه | supported_no_match | ابيمول اكسترا اقراص — المكرومي المنصورة.pdf p.1 | ابيمول اكسترا اقراص يختلف في التركيبة والشكل عن ابيمول اطفال لبوس المطلوب |
| ابيمول اطفال 5 لبوسه س ج | supported_no_match | ابيمول اكسترا اقراص — المكرومي المنصورة.pdf p.1 | ابيمول اكسترا اقراص يختلف في التركيبة والشكل عن ابيمول اطفال لبوس المطلوب |
| اتلابسلس نقط | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اتلابسلس نقط بين المرشحين |
| اتلانتو ثري كبسولات | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اتلانتو ثري بين المرشحين |
| اتلانتيكو30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اتلانتيكو بين المرشحين |
| اتميبرازول 40مجم 20 قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اتميبرازول وتشابه اللاحقة برازول لا يعد دليلاً كافياً |
| اجيولاكس  حبيبات | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اجيولاكس بين المرشحين |
| ادرينوكورتين1مجم امبول ث س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ادرينوكورتين بين المرشحين |
| ادويفلام50مجم جل س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ادويفلام بين المرشحين |
| اريببركس100مل شراب | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اريببركس بين المرشحين |
| اريثركس200مجم2شريط | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اريثركس بين المرشحين |
| ازارجا قطره س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ازارجا قطرة بين المرشحين |
| ازمازون اسبراي للفطريات | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ازمازون بين المرشحين |
| اسبروتكت100مجم30قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اسبروتكت بين المرشحين |
| اسبرين بروتكت 100مجم3شريط | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اسبرين بروتكت بين المرشحين |
| اسبوسيد سي 12قرص فوار | supported_no_match | اسبوسيد ٧٥ مجم اقراص / سيد — المكرومي المنصورة.pdf p.1; اسبوسيد 75 مج اقراص/باكت 120 — الهضبة الاثنين نقدى0.pdf p.1; اسبوسيد اطفال سعر جديد باكت 60 — مخزن الحياة فارم اسكندريه-170.pdf p.1; اسبوسيد اطفال ٣٥ جنية — المكرومي المنصورة.pdf p.1 | المرشحون اسبوسيد عادي وأطفال بدون فيتامين سي فوار المطلوب |
| استرامارك21قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم استرامارك بين المرشحين |
| استربسلز  عسل وليمون س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم استربسلز بين المرشحين |
| استربسلز  فيتامين سي س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم استربسلز بين المرشحين |
| افاندروكس شراب | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم افاندروكس بين المرشحين |
| افروزوليد150 مل شراب | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم افروزوليد بين المرشحين; لا يوجد منتج مطابق في المستودع |
| افروزوليد600مجم10قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم افروزوليد بين المرشحين |
| افيل حقن  6امبول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم افيل حقن بين المرشحين |
| اكسبتو برو كريم | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اكسبتو برو بين المرشحين |
| اكسترا بروتين اكياس فانيليا | supported_no_match | اكسترا بروتين شيكولاته باكت 27 — الهضبة الاثنين نقدى0.pdf p.2 | اكسترا بروتين شيكولاته يختلف في النكهة عن فانيليا المطلوب |
| اكسفورج 10مجم اتش سي تي س ج | supported_no_match | اكسفورج ١٦٠/٥ عادى س. ج ۲۱۸ ج — المكرومي المنصورة.pdf p.1; اكسفورج 5اتش سى كبسول/باكو100 — مخزن الحياة فارم اسكندريه-170.pdf p.1; اكسفورج10/160سعر جديديد — مخزن الحياة فارم اسكندريه-170.pdf p.1; اكسفورج اتش ١٦٠/٥ س. ج ۲۷۰ ج — المكرومي المنصورة.pdf p.1 | اختلاف في نوع المستحضر والتركيز |
| اكني اكت كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اكني اكت بين المرشحين |
| البيوستكس 8مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم البيوستكس بين المرشحين |
| التراسولف شراب | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم التراسولف بين المرشحين |
| الفابرينزيما قطره | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم الفابرينزيما بين المرشحين |
| الفاثرومب5مجم20قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم الفاثرومب بين المرشحين |
| الكابرس تريو5/160/12.5مجم س ج | supported_no_match | الكابرس تريو ١٦٠/١٢,٥/١٠-١٤قرص — كيور فارما خاص.pdf p.1; الكابرس ٥ مجم اقراص ۲ شريط — المكرومي المنصورة.pdf p.1 | الكابرس تريو متوفر بتركيز 10/160/12.5 وهو مختلف صراحة عن التركيز المطلوب 5/160/12.5 |
| الكابرس10مجم30قرص | supported_no_match | الكابرس ٥ مجم اقراص ۲ شريط — المكرومي المنصورة.pdf p.1; الكابرس تريو ١٦٠/١٢,٥/١٠-١٤قرص — كيور فارما خاص.pdf p.1 | الكابرس متاح بتركيز 5 مجم وهو مختلف صراحة عن التركيز المطلوب 10 مجم |
| الكابرس160/5 بلاس س ج | supported_no_match | الكابرس ٥ مجم اقراص ۲ شريط — المكرومي المنصورة.pdf p.1; الكابرس تريو ١٦٠/١٢,٥/١٠-١٤قرص — كيور فارما خاص.pdf p.1 | الكابرس المتاح إما أحادي أو تريو بتركيز مختلف ولا يطابق الكابرس بلاس 5/160 |
| الكافتابرو قطره | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم الكافتابرو بين المرشحين |
| الليرديب بخاخ للانف 60 ملل | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم الليرديب بين المرشحين |
| املوسازايد40/12.5/5مجم30قرص س ج | unresolved | املوساز اید ٥/١٢,٥/٤٠ — المكرومي المنصورة.pdf p.1 | تطابق تام في اسم المنتج املوسازايد والتركيز 5/12.5/40; لا توجد أسماء مطابقة للمنتج المطلوب |
| اميبريد50مجم اقراص س ج | supported_no_match | اميبرايد 200 مج اقراص/باكت 25 — الهضبة الاثنين نقدى0.pdf p.3 | اميبرايد متاح بتركيز 200 مجم وهو مختلف صراحة عن التركيز المطلوب 50 مجم |
| انترستو 100مجم 28قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم انترستو بين المرشحين |
| انتودين 20مجم30قرص س ج | unresolved | انتودين 40 مج 30 قرص/ باكت 35 — الهضبة الاثنين نقدى0.pdf p.3; انتودین ٤٠ مجم اقراص — المكرومي المنصورة.pdf p.1; انتودين 40 م ج م 3ش ي ط / باكو 35 — مخزن الحياة فارم اسكندريه-170.pdf p.1; انتودين ۲۰جم ۳۰ قرص جدید — كيور فارما خاص.pdf p.1; انتودين ٤٠مجم قرص — كيور فارما خاص.pdf p.1 | تطابق تام مع انتودين 20 مجم 30 قرص في المرشح I1817; اختلاف في التركيز بين 20 و 40 |
| انتي كرامب حقن | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم انتي كرامب بين المرشحين |
| اندرال10مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اندرال بين المرشحين |
| اندوديرما صن سكرين لوشن | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اندوديرما صن سكرين بين المرشحين |
| انزيماتريبس30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم انزيماتريبس بين المرشحين |
| انزيماكس ديوبايوتكس كبسول | supported_no_match | انزيماكس دوال ريليس/باكت66 — الهضبة الاثنين نقدى0.pdf p.3 | انزيماكس دوال ريليس يختلف عن انزيماكس ديوبايوتكس المطلوب |
| انسولين لانتوس سولوستار 1قلم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم لانتوس سولوستار بين المرشحين |
| انسولين نوفورابيد قلم خرطوشه | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم انسولين نوفورابيد بين المرشحين |
| انسيلاكوكس 60 مجم 30 قرص س ج | supported_no_match | نسيلاكوكس 90 مج اقراص/باكت 60 — الهضبة الاثنين نقدى0.pdf p.3; سيلاكوكس 120 مج اقراص/باكت 60 — الهضبة الاثنين نقدى0.pdf p.3 | انسيلاكوكس متاح بتركيز 90 مجم و120 مجم وهو تعارض صريح مع تركيز 60 مجم |
| انوكسيكام 20مجم 20قرص س ج | recovered_review | انوكسيكام لبوس باكت 54 — الهضبة الاثنين نقدى0.pdf p.3 | نفس المنتج انوكسيكام ولكن الشكل الصيدلي مختلف (لبوس بدلاً من أقراص) |
| انونا لوسيون للشعر | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم انونا لوسيون بين المرشحين |
| اوبتاديرول بلس 30كبسوله س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوبتاديرول بلس بين المرشحين |
| اوبتك سالين قطرة س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوبتك سالين قطرة بين المرشحين |
| اوجرام312.5مجم10قرص مضغ | supported_no_match | اوجرام 1 جم 14 قرص /باكت 32 — الهضبة الاثنين نقدى0.pdf p.3; اوجرام 228 مج شراب/باكت 48 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام 457 شراب 80 مل ج باكت 20 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام 642 مج شراب قديم /باكت 48 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام ۱جم ١٤ قرص ١٥٢ج — المكرومي المنصورة.pdf p.1; اوجرام ۱مجم ۲شريط — كيور فارما خاص.pdf p.2; اوجرام ٤٥٧مجم شراب — كيور فارما خاص.pdf p.2; اوجرام شراب ٦٤٢ مجم قديم — كيور فارما خاص.pdf p.2 | اوجرام المتاح أقراص 1 جم أو شراب بتركيزات أخرى وتتعارض مع 312.5 مجم |
| اوجرام457مجم بودره60مل | recovered_match | اوجرام 1 جم 14 قرص /باكت 32 — الهضبة الاثنين نقدى0.pdf p.3; اوجرام 228 مج شراب/باكت 48 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام 457 شراب 80 مل ج باكت 20 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام 642 مج شراب قديم /باكت 48 — الهضبة الاثنين نقدى0.pdf p.4; اوجرام ۱جم ١٤ قرص ١٥٢ج — المكرومي المنصورة.pdf p.1; اوجرام ۱مجم ۲شريط — كيور فارما خاص.pdf p.2; اوجرام ٤٥٧مجم شراب — كيور فارما خاص.pdf p.2; اوجرام شراب ٦٤٢ مجم قديم — كيور فارما خاص.pdf p.2 | تطابق تام في الاسم اوجرام والتركيز 457 مجم شراب معلق في المرشح I1936 |
| اورامكس 30مل اسبراي س ج | recovered_match | اورامكس بخاخ كبار/باكت 56 — الهضبة الاثنين نقدى0.pdf p.4; اورامكس بي سبراي/باكت 56 — الهضبة الاثنين نقدى0.pdf p.4 | تطابق تام لـ اورامكس بخاخ (اسبراي) في المرشح I0840 |
| اوسوبان800مجم 20قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوسوبان بين المرشحين |
| اوفيونهيبيتا28قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوفيونهيبيتا بين المرشحين |
| اوكسازوليد600مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوكسازوليد بين المرشحين |
| اوكيوسيليرج فورت قطره | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوكيوسيليرج فورت بين المرشحين |
| اوكيوميثيل  نقط | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوكيوميثيل بين المرشحين |
| اولانفيكسا10مجم30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اولانفيكسا بين المرشحين |
| اولفن100مجم اس ار10كبسول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اولفن بين المرشحين |
| اولوجنت اكياس | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اولوجنت بين المرشحين |
| اولوهيستين فورت محلول عين | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اولوهيستين فورت بين المرشحين |
| اومنيك 0.4مجم30قرص | supported_no_match | اومنيك اوكايس قرص — كيور فارما خاص.pdf p.2 | اومنيك اوكايس يمثل صيغة مختلفة (اوكاس) عن اومنيك العادي |
| اوني 5مجم مل شراب | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اوني شراب بين المرشحين |
| اي يست كبسول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم اي يست كبسول بين المرشحين |
| ايبويتين4000وحدة  امبول ث س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ايبويتين بين المرشحين; لا يوجد منتج مطابق في المستودع |
| ايبياكتو كريم | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ايبياكتو كريم بين المرشحين |
| ايتوريكوكس90مجم30قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد تطابق لاسم ايتوريكوكس بين المرشحين والبدائل العلاجية لا تطابق المنتج |
| ايجيكوستات بلس /مينالاكس | recovered_match | ايجيكيوستات بلس اقراص بديل مينالاكس — كيور فارما خاص.pdf p.2; يجيكيبوسات بلاس اقراص/ باكت 90 — الهضبة الاثنين نقدى0.pdf p.4 | تطابق تام في اسم المنتج (ايجيكيوستات بلس اقراص بديل مينالاكس) والشكل الصيدلي |
| ايرون جلور | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج يطابق اسم ايرون جلور بين المرشحين |
| ايرون ليبوزومال شراب | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم ايرون ليبوزومال شراب |
| ايزوميم 40مجم اقراص | unresolved | ايزومومب 40 مج اقراص باكت 144 — الهضبة الاثنين نقدى0.pdf p.5 | تطابق المنتج والتركيز 40 مج والشكل أقراص مع وجود خطأ قراءة بسيط في الحروف (ايزومومب / ايزوميم) |
| ايستوزا اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح يحمل اسماً مطابقاً لايستوزا اقراص |
| ايفرزين لوشن | recovered_review | ايفرزين كريم — كيور فارما خاص.pdf p.2; ايفرزين 24 قرص باكت 180 — الهضبة الاثنين نقدى0.pdf p.5; ايفرزين كريم/باكت 100 — الهضبة الاثنين نقدى0.pdf p.5 | نفس المنتج ايفرزين متوفر كشكل صيدلي مختلف (كريم وأقراص بدلاً من لوشن) |
| ايكاندرا بلس اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج يطابق ايكاندرا بلس بين المرشحين المتاحين |
| ايليديل 1% 15جم كريم | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم ايليديل كريم |
| ايليديل كريم30جم كبير | no_plausible_candidate_found | None found in this audit | لا يوجد منتج باسم ايليديل بين المرشحين |
| ايموكس 250مجم شراب س ج | supported_no_match | ايموكس 500 مج كبسول/ باكت 200 — الهضبة الاثنين نقدى0.pdf p.6 | اختلاف صريح في التركيز: المطلوب 250مجم والمتوفر 500 مج كبسول |
| ايموكسكلاف 625 مجم اقراص س ج | supported_no_match | ايموكسكلاف 1 جرام /باكو10 — مخزن الحياة فارم اسكندريه-170.pdf p.2; ايموكسكلاف ۳۱۲ شراب / ايبكو — المكرومي المنصورة.pdf p.1; ايموكسكلاف ٤٥٧ مجم شراب — المكرومي المنصورة.pdf p.1; ايموكسكلاف ٦٤٢,٩ شراب — المكرومي المنصورة.pdf p.1; ايموكسكلاف 1 جم اقراص/باكت 90 — الهضبة الاثنين نقدى0.pdf p.6; ايموكسكلاف ١جم قرص — كيور فارما خاص.pdf p.2; ايموكسكلاف ٤٥٧ مجم شراب — كيور فارما خاص.pdf p.2 | اختلاف صريح في التركيز: المطلوب 625 مجم والمتوفر 1 جم وتراكيز شراب أخرى |
| ايموكسكلاف642مجم شراب | unresolved | ايموكسكلاف ٦٤٢,٩ شراب — المكرومي المنصورة.pdf p.1; ايموكسكلاف 1 جرام /باكو10 — مخزن الحياة فارم اسكندريه-170.pdf p.2; ايموكسكلاف ۳۱۲ شراب / ايبكو — المكرومي المنصورة.pdf p.1; ايموكسكلاف ٤٥٧ مجم شراب — المكرومي المنصورة.pdf p.1; ايموكسكلاف 1 جم اقراص/باكت 90 — الهضبة الاثنين نقدى0.pdf p.6; ايموكسكلاف ١جم قرص — كيور فارما خاص.pdf p.2; ايموكسكلاف ٤٥٧ مجم شراب — كيور فارما خاص.pdf p.2 | تطابق اسم المنتج ايموكسكلاف والشكل الصيدلي شراب والتركيز (642,9 مقابل 642); لا توجد أسماء مطابقة للمنتج المطلوب |
| ايميرست اقراص 8 مجم 10 قرص | supported_no_match | اميرست حقن ٤ مجم — المكرومي المنصورة.pdf p.1 | اختلاف صريح في التركيز: المطلوب 8 مجم والمتوفر اميرست حقن 4 مجم |
| اينوفاجار نقط | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج مطابق لاسم اينوفاجار نقط |
| ب ك ميرز كبسول س ج | no_plausible_candidate_found | None found in this audit | لا توجد أدلة اسمية مطابقة لمنتج ب ك ميرز بين المرشحين |
| باروكسيديب37.5اكس ار اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم باروكسيديب |
| بانتروجلوب40مجم فيال | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بانتروجلوب فيال |
| بانتوبرازول 40 مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح يحمل الاسم التجاري بانتوبرازول (المرشحون أسماء تجارية بديلة مختلفة) |
| بانثينول النيل2%كريم وسط | recovered_match | بانثينول كريم كبييير سعر قدييم باكو 25 — جملة العمروووو.pdf p.1; بانثينول ۳۰ جم كريم /روتكس جديد — كيور فارما خاص.pdf p.2 | تطابق في اسم المنتج والشكل الصيدلي (بانثينول كريم) واختلاف الحجم لا يمنع التطابق; تطابق المنتج واختلاف الحجم لا يمنع |
| باولوكير نقط س ج/بيكولاكس | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح باسم باولوكير، وبيكولاكس بديل تجاري مستقل لا يطابق المطلوب |
| براديبيكت 5 مجم 28 قرص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم براديبيكت |
| برايم روز اي اقراص س ج | supported_no_match | برايم روز بلاس اقراص/ايمافارم — السلام شبين.pdf p.1; برايم روز بلاس كبسول جديد — كيور فارما خاص.pdf p.2 | تعارض في المتغير التجاري: المطلوب برايم روز اي والمتوفر برايم روز بلاس |
| بروستيترول 10مجم | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بروستيترول، والمرشح I1248 بديل تجاري وليس نفس المنتج |
| بروليفز شراب | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج مطابق لاسم بروليفز شراب |
| برونشيكم شراب س ج | recovered_match | برونشيكم شراب اليكسير/افنتس — السلام شبين.pdf p.1 | تطابق تام في اسم المنتج برونشيكم والشكل الصيدلي شراب (اليكسير) |
| برونكوفين شراب | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم برونكوفين شراب |
| برونكوفين شراب س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح باسم برونكوفين بين الخيارات المعروضة |
| برونكولين اس بخاخ/فنتال | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم برونكولين اس، وفنتال بديل تجاري مستقل |
| بريجناستيب 2 30قرص | supported_no_match | بريجناستيب 1 اقراص — الهضبة الاثنين نقدى0.pdf p.6; بريجناستيب ١ مجم اقراص — كيور فارما خاص.pdf p.2 | تعارض في رقم المرحلة/المتغير: المطلوب بريجناستيب 2 والمتوفر بريجناستيب 1 |
| بليتال 50مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بليتال أقراص |
| بنتافليكس كريم مساج100جم | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بنتافليكس كريم |
| بنتافليكس كريم مساج50جم | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بنتافليكس |
| بنتاكولد120مل شراب س ج | no_plausible_candidate_found | None found in this audit | لا يوجد أي مرشح باسم بنتاكولد شراب |
| بنتاكولد120مل شراب س ق | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بنتاكولد |
| بوديكسان 0.5مجم حقن | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بوديكسان حقن; لا يوجد منتج مطابق في المستودع |
| بون كير .5ميكروجرام 30كبسوله س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج باسم بون كير بين المرشحين |
| بي كوم 6 امبولات س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بي كوم امبولات |
| بيا 400مجم اقراص | supported_no_match | بيا 300 مج اقراص — الهضبة الاثنين نقدى0.pdf p.7; بيا 600 مج اقراص بيوميد — الهضبة الاثنين نقدى0.pdf p.7 | اختلاف صريح في التركيز: المطلوب بيا 400مجم والمتوفر 300 مج و600 مج |
| بيتابرونيت بلس كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بيتابرونيت بلس كريم |
| بيتادين دش مهبلي س ج | recovered_review | بيتادين مطهر/النيل — السلام شبين.pdf p.2; بيتادين منظف جلد/النيل — السلام شبين.pdf p.2; بيتادين غرغرة — المكرومي المنصورة.pdf p.2 | نفس المنتج بيتادين ولكن باختلاف واضح في الشكل الصيدلي والاستخدام (دش مهبلي مقابل مطهر/غرغرة) |
| بيتادين شامبو120مل س ج | recovered_review | بيتادين مطهر/النيل — السلام شبين.pdf p.2; بيتادين منظف جلد/النيل — السلام شبين.pdf p.2; بيتادين غرغرة — المكرومي المنصورة.pdf p.2 | نفس العلامة التجارية بيتادين مع اختلاف الشكل الصيدلي (شامبو مقابل مطهر ومنظف جلد) |
| بيتادين شامبو60مل س ج | recovered_review | بيتادين مطهر/النيل — السلام شبين.pdf p.2; بيتادين منظف جلد/النيل — السلام شبين.pdf p.2; بيتادين غرغرة — المكرومي المنصورة.pdf p.2 | نفس منتج بيتادين ولكن الشكل الصيدلي مختلف (شامبو مقابل مطهر/منظف جلد) |
| بيتافوس امبول | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بيتافوس، والمرشح I1657 بديل تجاري وليس نفس المنتج |
| بيتاكاروتين فورت 20كبسوله | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بيتاكاروتين فورت |
| بيدرو اسبراي مطهر س ق | recovered_match | بيدرو سبراى للفم /باكت 96 — الهضبة الاثنين نقدى0.pdf p.7; بيدرو غسول/بليزا — الهضبة الاثنين نقدى0.pdf p.7 | تطابق في اسم المنتج بيدرو والشكل الصيدلي اسبراي (سبراى للفم مطهر); لا يوجد منتج مطابق في المستودع |
| بيدرو كريم تفتيح | recovered_review | بيدرو سبراى للفم /باكت 96 — الهضبة الاثنين نقدى0.pdf p.7; بيدرو غسول/بليزا — الهضبة الاثنين نقدى0.pdf p.7 | نفس المنتج بيدرو ولكن بشكل صيدلي مختلف (غسول بدلاً من كريم) |
| بيدورا كالسيوم 20 كبسوله | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم بيدورا كالسيوم |
| بيرافين امبول | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم بيرافين امبول |
| بيسلفون120مل شراب س ج | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج مطابق لاسم بيسلفون شراب |
| بيكوزيم امبول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح باسم بيكوزيم امبول |
| بيليبوسيس 20 قرص | unresolved | اليمبوسيس 2.5 مج اقراص — الهضبة الاثنين نقدى0.pdf p.2; اليمبوسيس 5 مج اقراص — الهضبة الاثنين نقدى0.pdf p.2 | الاسم المحتمل هو اليمبوسيس لكن الطلب يفتقر للتركيز ويتوفر تركيزان مختلفان (2.5 و5 مج) |
| تادالاندرو5جم30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم تادالاندرو بين المرشحين |
| تاريفلوكس200مجم10قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح باسم تاريفلوكس (المرشحون منتجات أخرى تشترك في المقطع فلوكس) |
| تاريفيد 200مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم تاريفيد 200مجم |
| تاموكسيفين 10مجم30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج يطابق تاموكسيفين بين المرشحين |
| تجريتول200 سي ار 20قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم تجريتول سي ار |
| تجريتول400 سي ار 20قرص | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج مطابق لتجريتول بين الخيارات المتاحة |
| تراي بيتابرونات كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم تراي بيتابرونات كريم |
| ترايتكت اطفال صابونه | supported_no_match | ترای تكت حب شباب — المكرومي المنصورة.pdf p.2 | تعارض في المتغير: المطلوب ترايتكت أطفال صابونة والمتوفر تراي تكت حب شباب; لا يوجد منتج مطابق في المستودع |
| ترايلبتال300مجم50قرص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم ترايلبتال; لا يوجد منتج مطابق في المستودع |
| ترايمدفلو 20قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ترايمدفلو |
| تربين كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم تربين كريم |
| ترياكور 5مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح يطابق ترياكور أقراص |
| تريامريكان500مجم فيال س ج | no_plausible_candidate_found | None found in this audit | لا يوجد أي منتج مطابق لاسم تريامريكان فيال |
| تريتاس 1.25مجم 14قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم تريتاس أقراص |
| تريتاس 2.5 مجم 14قرص | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح مطابق لاسم تريتاس |
| تشيكس اميون شراب | supported_no_match | تشيكس جروى ٢٥٠مل شراب — كيور فارما خاص.pdf p.3 | تعارض في المتغير التجاري: المطلوب تشيكس اميون والمتوفر تشيكس جروى |
| توب جنج ادفانس30كبسوله س ج | supported_no_match | توب جينج كبسول/ماش — السلام شبين.pdf p.2 | تعارض في المتغير: المطلوب توب جنج ادفانس والمتوفر توب جينج العادي |
| تورسامولكس10مجم اقراص س ج | unresolved | تورسامولكس ۱۰جم اقراص — كيور فارما خاص.pdf p.3; تورسامولكس ۲۰ جم اقراص — كيور فارما خاص.pdf p.3; تورسامولكس 20 مج اقراص/باكت 52 — الهضبة الاثنين نقدى0.pdf p.9 | تطابق في اسم المنتج تورسامولكس والشكل أقراص والتركيز 10 (مع كتابتها ۱۰جم بدلاً من مجم في OCR); لا توجد أسماء مطابقة للمنتج المطلوب |
| توسيستوب شراب س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج باسم توسيستوب شراب بين المرشحين |
| تي 4 ثيرو100ميكرو100قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج باسم تي 4 ثيرو (يوثيروكس بديل تجاري وليس نفس المنتج) |
| جابتن 300مجم 30كبسوله | no_plausible_candidate_found | None found in this audit | لا يوجد مرشح باسم جابتن كبسول |
| جابتن 300مجم 30كبسوله س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم جابتن بين الخيارات |
| جابتن400مجم 30كبسوله | no_plausible_candidate_found | None found in this audit | لا توجد أي أدلة اسمية مطابقة لمنتج جابتن |
| جاستروبيوتك 550 مج 20 قرص | supported_no_match | جاستروبيوتيك 200 مج 20 قرص ب 5 — الهضبة الاثنين نقدى0.pdf p.9 | اختلاف صريح في التركيز: المطلوب جاستروبيوتك 550 مج والمتوفر 200 مج |
| جانوفيا 100مجم 28قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر جانوفيا بين المرشحين |
| جانيوميت1000/50مجم 56قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر جانيوميت بين المرشحين |
| جانيوميت500/50مجم 56قرص | no_plausible_candidate_found | None found in this audit | عدم توفر جانيوميت بين المرشحين |
| جاوتيفيد80مجم  3 شريط س ج | no_plausible_candidate_found | None found in this audit | عدم توفر جاوتيفيد بين المرشحين |
| جراليبنتين300مجم اقراص | no_plausible_candidate_found | None found in this audit | عدم توفر جراليبنتين بين المرشحين |
| جرانتريل 3مجم 6 امبول س ج | supported_no_match | جرانتيل ۲ ملجم تاريخ بعيد — المكرومي المنصورة.pdf p.2 | اختلاف في التركيز ۲ ملجم مقابل ۳; اختلاف في التركيز بين 3 و 2 |
| جلوتاثايون 16كبسولة | no_plausible_candidate_found | None found in this audit | عدم توفر جلوتاثايون بين المرشحين |
| جليبوفين500/5مجم30قرص | supported_no_match | جليبيوفين ٥ / ١٠٠٠ قرص — كيور فارما خاص.pdf p.3 | اختلاف في التركيز 5/1000 مقابل 5/500; اختلاف في التركيز بين 500 و 1000 |
| جلينسيرت 20مجم كريم س ج | no_plausible_candidate_found | None found in this audit | عدم توفر جلينسيرت كريم بين المرشحين |
| جي سي فارم غسول | no_plausible_candidate_found | None found in this audit | عدم توفر جي سي فارم بالمرشحين |
| جيت وايت كريم | no_plausible_candidate_found | None found in this audit | عدم توفر جيت وايت كريم بالمرشحين; لا يوجد منتج مطابق في المستودع |
| جيوكاند بلس21قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر جيوكاند بلس بين المرشحين |
| دابسوكيرل 50مجم جيل | recovered_match | دابسوكيريل جيل 30 جم — الهضبة الاثنين نقدى0.pdf p.10 | تطابق تام للمنتج والشكل الصيدلي |
| دال دروب نقط | no_plausible_candidate_found | None found in this audit | عدم توفر دال دروب بين المرشحين |
| دايسينون 3امبول س ق | no_plausible_candidate_found | None found in this audit | عدم توفر دايسينون بين المرشحين |
| دورفين 30كبسولة | no_plausible_candidate_found | None found in this audit | عدم توفر دورفين كبسول بين المرشحين |
| دوزين2مجم20قرص | supported_no_match | دوزين ٤ مجم / ايبكو — المكرومي المنصورة.pdf p.2 | اختلاف التركيز 4 مجم مقابل 2 مجم |
| دولفين 12.5مجم لبوس 2شريط س ق | supported_no_match | دولفين 25لبوس 2شريط/باكو90 — مخزن الحياة فارم اسكندريه-170.pdf p.3; دولفين ك6 امبول — مخزن الحياة فارم اسكندريه-170.pdf p.3 | اختلاف في التركيز 25 مجم مقابل 12.5; اختلاف نوع المستحضر لوجود دولفين ك |
| دولفين 50مجم لبوس 2شريط | supported_no_match | دولفين 25لبوس 2شريط/باكو90 — مخزن الحياة فارم اسكندريه-170.pdf p.3; دولفين ك6 امبول — مخزن الحياة فارم اسكندريه-170.pdf p.3 | اختلاف في التركيز 25 مجم مقابل 50; اختلاف نوع المستحضر لوجود دولفين ك |
| دولفين 75مجم لبوس س ج | supported_no_match | دولفين 25لبوس 2شريط/باكو90 — مخزن الحياة فارم اسكندريه-170.pdf p.3; دولفين ك6 امبول — مخزن الحياة فارم اسكندريه-170.pdf p.3 | اختلاف في التركيز 25 مجم مقابل 75; اختلاف نوع المستحضر لوجود دولفين ك |
| دي 3 تاج نقط | no_plausible_candidate_found | None found in this audit | عدم توفر دي 3 تاج بالمرشحين |
| دي جي كير مضمضه س ج | no_plausible_candidate_found | None found in this audit | عدم توفر دي جي كير بالمرشحين |
| ديافانس 5مجم 30قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر ديافانس بين المرشحين |
| ديافانس 5مجم 30قرص س ق | no_plausible_candidate_found | None found in this audit | عدم توفر ديافانس بين المرشحين |
| ديباكين كرونو500مجم اقراص | supported_no_match | ديباكين ۲۰۰ مجم اقراص — المكرومي المنصورة.pdf p.2; ديباكين 200 مج اقراص باكت 60 — الهضبة الاثنين نقدى0.pdf p.11; ديباكين ۲۰۰ مجم اقراص — كيور فارما خاص.pdf p.4 | اختلاف التركيز 200 مجم مقابل 500 |
| ديبوفيت  5امبول | supported_no_match | ديبوفيت بلس اقراص — المكرومي المنصورة.pdf p.2; ديبوفيت بلس اقراص استحلاب — الهضبة الاثنين نقدى0.pdf p.11; ديبوفيت بلس ۳۰ قرص — كيور فارما خاص.pdf p.4 | تعارض إضافة بلس واختلاف الشكل الصيدلي |
| ديبوفيت  5امبول س ج | supported_no_match | ديبوفيت بلس اقراص — المكرومي المنصورة.pdf p.2; ديبوفيت بلس اقراص استحلاب — الهضبة الاثنين نقدى0.pdf p.11; ديبوفيت بلس ۳۰ قرص — كيور فارما خاص.pdf p.4 | تعارض إضافة بلس واختلاف الشكل الصيدلي; لا يوجد منتج مطابق في المستودع |
| ديديرا نقط | no_plausible_candidate_found | None found in this audit | عدم توفر ديديرا نقط بين المرشحين |
| ديرموفيت  كريم س ج | no_plausible_candidate_found | None found in this audit | عدم توفر ديرموفيت كريم بين المرشحين |
| ديسبروديرم كريم 30 جرام | no_plausible_candidate_found | None found in this audit | عدم توفر ديسبروديرم كريم بين المرشحين |
| ديفارول امبول س ج | no_plausible_candidate_found | None found in this audit | عدم توفر ديفارول امبول بين المرشحين |
| ديفلوكان 2مجم 50ملل فيال | supported_no_match | ديفلوكان ١٥٠ سعر ١١١ — المكرومي المنصورة.pdf p.2; ديفلوكان ٥٠ مجم كبسول فايزر — المكرومي المنصورة.pdf p.2; ديفلوكان ١٥٠ مجم قرص — كيور فارما خاص.pdf p.4; ديفلوكان 150 مج اقراص/باكت12 — الهضبة الاثنين نقدى0.pdf p.11 | اختلاف في التركيز والشكل الصيدلي; اختلاف في التركيز بين 2 و 150 |
| ديكابرينو200مجم2امبول س ج | no_plausible_candidate_found | None found in this audit | عدم توفر ديكابرينو امبول بالمرشحين |
| ديكسافين شراب | no_plausible_candidate_found | None found in this audit | عدم توفر ديكسافين شراب بين المرشحين; لا يوجد منتج مطابق في المستودع |
| ديكلوتازين 10كيس | no_plausible_candidate_found | None found in this audit | عدم توفر ديكلوتازين بين المرشحين |
| ديكلوفلام10قرص | no_plausible_candidate_found | None found in this audit | عدم توفر ديكلوفلام بين المرشحين |
| ديكلوفين 100مجم5لبوسة كبار ث س ج | recovered_review | ديكلوفين امبول سعر جديد ٣٦ ج — المكرومي المنصورة.pdf p.2 | اختلاف الشكل الصيدلي أمبول بدلا من لبوس |
| ديمانكورتيل امبول/ديبروفوس | no_plausible_candidate_found | None found in this audit | عدم توفر ديمانكورتيل بين المرشحين |
| ديورافوس 1 امبول | recovered_match | ديورافوس امبول = ديبروفوس — كيور فارما خاص.pdf p.4 | تطابق تام للمنتج ديورافوس أمبول |
| ديوزمين 30 قرص | no_plausible_candidate_found | None found in this audit | عدم توفر ديوزمين بين المرشحين |
| راميكسول 1جم30قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر راميكسول بين المرشحين |
| راميكسول25مجم30قرص س ج | no_plausible_candidate_found | None found in this audit | عدم توفر راميكسول بين المرشحين |
| رايوفيت شراب س ج | no_plausible_candidate_found | None found in this audit | عدم توفر رايوفيت شراب بين المرشحين; لا يوجد منتج مطابق في المستودع |
| روزاسيف 30 كبسوله/ برايم روز | supported_no_match | برايم روز بلاس اقراص/ايمافارم — السلام شبين.pdf p.1; برايم روز بلاس كبسول جديد — كيور فارما خاص.pdf p.2 | اختلاف تجاري وإضافة بلس للمنتج; لا يوجد منتج مطابق في المستودع |
| روزوكوليست 10 مجم اقراص | no_plausible_candidate_found | None found in this audit | عدم توفر روزوكوليست بين المرشحين |
| روزينول   كبسول | no_plausible_candidate_found | None found in this audit | عدم توفر روزينول كبسول بين المرشحين |
| روكسيكام 8مجم 20قرص | no_plausible_candidate_found | None found in this audit | عدم توفر روكسيكام بين المرشحين |
| رونكس دش مهبلي س ج | no_plausible_candidate_found | None found in this audit | عدم توفر رونكس دش مهبلي بالمرشحين |
| رويال جيلي1000مجم12كبسولة س ج | no_plausible_candidate_found | None found in this audit | عدم توفر رويال جيلي بين المرشحين |
| رويال ريجيم كبير50كيس س ج | no_plausible_candidate_found | None found in this audit | عدم توفر رويال ريجيم بين المرشحين |
| ريبايون اسبراي | recovered_review | ريبايون ان جيل بديل ريباريل ٥٠ جم — المكرومي المنصورة.pdf p.2 | اختلاف الشكل الصيدلي جيل بدلا من سبراي; لا يوجد منتج مطابق في المستودع |
| ريتشي بانثينول كريم ادفانس | unresolved | ريتشى بانثينول 20جم كريم/باكت 25 — الهضبة الاثنين نقدى0.pdf p.22; وريتشى بانثينول 50جم كريم/باكت 10 — الهضبة الاثنين نقدى0.pdf p.22; يوريتشى بانثينول ادفانس كريم جيل — الهضبة الاثنين نقدى0.pdf p.22; يوريتشى بانثينول جيل/باكت90 — الهضبة الاثنين نقدى0.pdf p.22 | تطابق ريتشي بانثينول أدفانس كريم جيل; لا يوجد منتج مطابق في المستودع |
| ريستيبرو نقط | no_plausible_candidate_found | None found in this audit | عدم توفر ريستيبرو نقط بين المرشحين |
| ريلاكومب جيل مساج100جم | no_plausible_candidate_found | None found in this audit | عدم توفر ريلاكومب جيل بين المرشحين |
| ريلاكومب جيل مساج50جم | no_plausible_candidate_found | None found in this audit | عدم توفر ريلاكومب جيل بين المرشحين |
| رينومول شراب س ج | no_plausible_candidate_found | None found in this audit | عدم توفر رينومول شراب بين المرشحين |
| زادميسن20مجم مرهم/جاراميسين | no_plausible_candidate_found | None found in this audit | عدم توفر زادميسن بين المرشحين |
| زاكاجلون امبول س ج | no_plausible_candidate_found | None found in this audit | عدم توفر زاكاجلون بين المرشحين |
| زانثيبوكس 80مجم اقراص | no_plausible_candidate_found | None found in this audit | عدم توفر زانثيبوكس بين المرشحين; لا يوجد منتج مطابق في المستودع |
| زانوجليد4/30اقراص س ج | recovered_match | زانوجليد 4 مج اقراص/ باكت 60 — الهضبة الاثنين نقدى0.pdf p.12 | تطابق المنتج زانوجليد مع توافق التركيز |
| زنكو بلاس شراب | no_plausible_candidate_found | None found in this audit | عدم توفر زنكو بلاس شراب بالمرشحين |
| زوركال20مجم14قرص س ج | unresolved | زوركال ٤٠ مجم ١٤ قرص ٩٦ ج — المكرومي المنصورة.pdf p.2; زوركال ۲۰ جم اقراص — كيور فارما خاص.pdf p.4; زوركال ٤٠ جم ١٤ اقراص — كيور فارما خاص.pdf p.4; زوركال ٤٠ مجم اقراص ۲۸ قرص — كيور فارما خاص.pdf p.4 | تطابق تام للمنتج والتركيز زوركال 20; لا توجد أسماء مطابقة للمنتج المطلوب |
| زوفيراكس10 مجم كريم جلد س ج | recovered_review | زوفيراكس شراب/باكو24 — مخزن الحياة فارم اسكندريه-170.pdf p.3; زوفيراكس ٤٠٠مجم اقراص/جلاكسو — السلام شبين.pdf p.3; زوفيراكس شراب/جلاكسو — السلام شبين.pdf p.3; زوفيراكس ۱۰۰ مل شراب — كيور فارما خاص.pdf p.4 | اختلاف الشكل الصيدلي شراب بدلا من كريم |
| زولمسولان5مجم6فيلم | no_plausible_candidate_found | None found in this audit | عدم توفر زولمسولان بين المرشحين |
| زيستريل 20مجم 20قرص س ج | supported_no_match | زيستريل ٥ مجم قرص — كيور فارما خاص.pdf p.4; زيستريل ۱۰ مجم قرص — كيور فارما خاص.pdf p.4 | اختلاف التركيز 5 و10 مقابل 20 |
| سالبين  1500 مجم فيال | no_plausible_candidate_found | None found in this audit | عدم توفر سالبين فيال بين المرشحين |
| سالميتوكورت50/500ميكرو60ك | no_plausible_candidate_found | None found in this audit | عدم توفر سالميتوكورت بين المرشحين |
| سانسو بي كومبلكس 3شريط س ج | supported_no_match | سانسو انتى اوكسيدانت ۲۸ قرص — كيور فارما خاص.pdf p.5 | تعارض في الصنف انتي اوكسيدانت |
| سانسو نيوروتيك28قرص | supported_no_match | سانسو انتى اوكسيدانت ۲۸ قرص — كيور فارما خاص.pdf p.5 | تعارض في نوع الصنف انتي اوكسيدانت |
| سايبنتولا قطره | no_plausible_candidate_found | None found in this audit | عدم توفر سايبنتولا قطرة بين المرشحين |
| سبازموفين امبول س ج | no_plausible_candidate_found | None found in this audit | عدم توفر سبازموفين امبول بين المرشحين |
| سباسكولون 100مجم اقراص س ج | supported_no_match | سباسيكولون ٥٠ جم ۳ شريط — كيور فارما خاص.pdf p.5 | اختلاف التركيز 50 مجم مقابل 100 |
| سبكتراسيف 1 مجم امبول | no_plausible_candidate_found | None found in this audit | عدم توفر سبكتراسيف بين المرشحين |
| سبلفكت 30كبسولة | no_plausible_candidate_found | None found in this audit | عدم توفر سبلفكت بين المرشحين |
| ستارفيل رول اون لايت بينك | no_plausible_candidate_found | None found in this audit | عدم توفر ستارفيل رول اون بالمرشحين |
| ستارفيل كريم تفتيح60مل س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات ستارفيل تفتيح |
| ستاركوبينا5مجم20قرص | supported_no_match | سترا كوبينا ٢,٥ مجم ۳۰ قرص — المكرومي المنصورة.pdf p.2 | اختلاف التركيز 2.5 مجم عن 5 مجم |
| ستاركوبينا5مجم3شريط س ج | supported_no_match | سترا كوبينا ٢,٥ مجم ۳۰ قرص — المكرومي المنصورة.pdf p.2 | اختلاف التركيز 2.5 مجم عن 5 مجم |
| سترونج فيل سبراي | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سترونج فيل سبراي |
| ستلاسيل 5 جم اقراص س ج | unresolved | ستلاسيل 5 مج اقراص/باكت 150 — الهضبة الاثنين نقدى0.pdf p.12 | تطابق تام للمنتج والتركيز والشكل; لا توجد أسماء مطابقة للمنتج المطلوب |
| سفيرا لوشن | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سفيرا لوشن |
| سكروفير امبول | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سكروفير امبول; لا يوجد منتج مطابق في المستودع |
| سكينورين كريم | supported_no_match | سكينوريتش كريم — الهضبة الاثنين نقدى0.pdf p.13 | سكينوريتش منتج تجاري مختلف عن سكينورين |
| سليب ايز 3مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سليب ايز اقراص |
| سنوليفا اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سنوليفا اقراص |
| سوبرانيل 25مجم كبسول س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سوبرانيل كبسول |
| سوكابريكسام5/1.25/10مجم30قرص | supported_no_match | سوكابريكسام 10/2.5 مج اقراص — الهضبة الاثنين نقدى0.pdf p.13; سوكابريكسام ٥/١,٢٥/٥ — المكرومي المنصورة.pdf p.3 | اختلاف تركيز الدواء الثلاثي |
| سوكير اسبري للفم اطفال س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سوكير اسبري للفم |
| سولو لوسيون مرطب | recovered_match | سولو لوسيون/باكت 25 — الهضبة الاثنين نقدى0.pdf p.13; سولو كريم 60 جم/باكت 12 — الهضبة الاثنين نقدى0.pdf p.13 | تطابق تام للاسم وسولو لوسيون |
| سوليوبريد 5مجم30قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سوليوبريد |
| سومازينا سوبرا كبسول | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سومازينا سوبرا |
| سومازينا نقط س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سومازينا نقط |
| سوميناليتا شراب | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سوميناليتا شراب |
| سي اتش الفا بلس س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سي اتش الفا بلس |
| سيالونج5مجم30قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيالونج اقراص |
| سيبانوين جيل | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيبانوين جيل |
| سيبروباي 750مجم10قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيبروباي |
| سيبروفلوكساسين محلول وريدي | recovered_review | سيبروفلوكساسين 750 مج اورجانو — الهضبة الاثنين نقدى0.pdf p.13; بيروفلوكساسين 500 مج قرص اورجانو — الهضبة الاثنين نقدى0.pdf p.13 | اختلاف الشكل الصيدلي اقراص بدلا محلول |
| سيبروفلوكسميت 500مجم | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيبروفلوكسميت; لا يوجد منتج مطابق في المستودع |
| سيتال1جم اقراص س ج | unresolved | سيتال اقراص 500 س ج — مخزن الحياة فارم اسكندريه-170.pdf p.3; سيتال شراب/ايبيكو — السلام شبين.pdf p.3; سيتال شراب س ج باكت20 — مخزن الحياة فارم اسكندريه-170.pdf p.3; سيتال ٥٠٠ مجم اقراص — كيور فارما خاص.pdf p.5; سيتال لبوس /باكت 65 — الهضبة الاثنين نقدى0.pdf p.13; سيتال شراب باكت 20 — الهضبة الاثنين نقدى0.pdf p.13; سيتال شراب قديم — كيور فارما خاص.pdf p.5; سيتال نقط — كيور فارما خاص.pdf p.5; سيتال شراب س.ج ۳۱ج — المكرومي المنصورة.pdf p.3; سيتال اكسترا /ايبيكو — المكرومي المنصورة.pdf p.3 | اختلاف في التركيز 500 مجم مقابل 1 جم; اختلاف في التركيز بين 1جم و 500مجم |
| سيترونوميت 4 مجم اقراص س ج | unresolved | سيترونوميت 8 مل 4 قرص — الهضبة الاثنين نقدى0.pdf p.13 | اختلاف في التركيز 8 مجم مقابل 4; اختلاف في التركيز بين 4 و 8 |
| سيرازيت اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيرازيت اقراص |
| سيرباس 50مجم اقراص س ج | supported_no_match | سيرباس ۱۰۰ مجم ۲۰ قرص جديد — كيور فارما خاص.pdf p.5 | اختلاف التركيز 100 مجم عن 50 مجم |
| سيردالود 2 مجم اقراص س ج | supported_no_match | كيردالود اس ار ۳۰ قرص — كيور فارما خاص.pdf p.6 | اختلاف النوع ممتد المفعول اس ار |
| سيردالود 4 مجم20قرص | supported_no_match | كيردالود اس ار ۳۰ قرص — كيور فارما خاص.pdf p.6 | اختلاف النوع ممتد المفعول اس ار |
| سيريلاك 125جم تمر وقمح | supported_no_match | سيريلاك ارز وحديد125مجم — مخزن الحياة فارم اسكندريه-170.pdf p.4 | اختلاف نكهة ونوع السيريلاك; لا يوجد منتج مطابق في المستودع |
| سيريلاك 150جم قمح ساده | supported_no_match | سيريلاك ارز وحديد125مجم — مخزن الحياة فارم اسكندريه-170.pdf p.4 | اختلاف نوع السيريلاك ارز بدلا قمح; لا يوجد منتج مطابق في المستودع |
| سيستان قطره | supported_no_match | سیستان الترا سعر قديم — المكرومي المنصورة.pdf p.3 | اختلاف النوع سيستان الترا عن العادي |
| سيفاثرد 300 مجم 10 كبسول س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفاثرد |
| سيفاكسون  1جم عضل فيال | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفاكسون |
| سيفاكسون  500مجم عضل فيال | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفاكسون |
| سيفاكسون1جرام وريد فيال | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفاكسون |
| سيفزيم 1 جم فيال س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفزيم فيال |
| سيفيبم 1جم  فيال عضل فاركو | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفيبم فيال |
| سيفيتيل 1جم | recovered_match | سيفيتيل اجم اقراص فوار — كيور فارما خاص.pdf p.5; سيفيتيل فوار ايبكو — المكرومي المنصورة.pdf p.3 | تطابق تام للمنتج والتركيز |
| سيفيكسيم 100مجم 30مل شرب س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيفيكسيم شراب |
| سيكلوبروجينوفا اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيكلوبروجينوفا اقراص |
| سيكلور  125مل شراب س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيكلور شراب |
| سيكلور 250مل شراب س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيكلور شراب |
| سيكوسيتام 500مجم20قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيكوسيتام اقراص |
| سيلجون لبوس س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيلجون لبوس |
| سيلفازين كريم حروق | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيلفازين كريم |
| سيلفر سيز شراب | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيلفر سيز شراب |
| سيلكتيفال كبسول | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيلكتيفال كبسول |
| سيلينيكس شامبو س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سيلينيكس شامبو |
| سيلينيوم فيت 30قرص | supported_no_match | سيلينيوم ايه سى قرص جديد — كيور فارما خاص.pdf p.5 | سيلينيوم ايه سى منتج مختلف |
| سينتروباكس ادفانس اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سينتروباكس ادفانس |
| سينمت  250/25مجم 20قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات سينمت اقراص |
| سينوبريل كواقراص س ج | recovered_match | سينوبريل كو اقراص/جلوبال باكت 90 — الهضبة الاثنين نقدى0.pdf p.14; سينوبريل 5 مجم اقراص/باكت 90 — الهضبة الاثنين نقدى0.pdf p.14 | تطابق تام للمنتج سينوبريل كو اقراص |
| شان سيكا كريم | no_plausible_candidate_found | None found in this audit | لا توجد منتجات شان سيكا كريم |
| صابون سنسودرم س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات صابون سنسودرم |
| صابون هاي ديرم مرطب80جم | no_plausible_candidate_found | None found in this audit | لا توجد منتجات صابون هاي ديرم |
| صن توب كريم50مجم س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات صن توب كريم |
| صن دراي صن سكرين كريم جيل | no_plausible_candidate_found | None found in this audit | لا توجد منتجات صن دراي |
| فاتروكسيم200مجم10قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فاتروكسيم اقراص |
| فاردي 20مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فاردي اقراص |
| فاركولين محلول | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فاركولين محلول |
| فاموتاك 40مجم 20قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فاموتاك اقراص |
| فانج رير جل شاور | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فانج رير جل شاور |
| فاينال تو شامبو 240ملل س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فاينال تو شامبو |
| فلابو 600 اقراص | recovered_review | فلابو نقط/دلتا فارم — السلام شبين.pdf p.4 | اختلاف الشكل الصيدلي نقط بدلا اقراص |
| فلوادجست25مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلوادجست اقراص |
| فلوب شراب س ج | unresolved | فلابو نقط/دلتا فارم — السلام شبين.pdf p.4 | اختلاف الشكل الصيدلي نقط بدلا شراب |
| فلوتاك 75مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلوتاك اقراص |
| فلوتن 14 كبسول | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلوتن كبسول |
| فلورست ان اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلورست ان اقراص |
| فلوروكينومكس .5 نقط | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلوروكينومكس نقط |
| فلوكسيبسي400مجم اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فلوكسيبسي اقراص |
| فليبوتون حقن 3امبولات س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات فليبوتون حقن |
| فليبوفينال جل40جم/ريباريل | supported_no_match | ريباريل ٤٠ جم جيل جديد — كيور فارما خاص.pdf p.4; ريبارييل جيل — المكرومي المنصورة.pdf p.2 | ريباريل بديل تجاري مختلف عن فليبوفينال |
| فنستيل 15مجم نقط س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فور كيدز باروت شراب | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فوراديل كبسول 3شرايط بخاخ | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فوراديل كبسول 6شرايط بخاخ | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فورتازيديم 1جم فيال عضل | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فورتيفيروم14كيس س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فوركيدز 3د 15نقط مل/دايفيتون | supported_no_match | ديفيتون ۲۰۰ نقط سعر جديد — المكرومي المنصورة.pdf p.2; ديفيتون دى نقط — كيور فارما خاص.pdf p.4; ديفيتون دى نقط جديد باكت 80 — الهضبة الاثنين نقدى0.pdf p.11; ديفيتون د فورت نقط/ باكت 40 — الهضبة الاثنين نقدى0.pdf p.11; بون ديفيتون ٥٠٠٠٠ امبول كبار — المكرومي المنصورة.pdf p.2 | منتج تجاري مختلف وبديل دوائي |
| في اند كريم | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيتا دي ثري4000ميكروفيلم | recovered_match | فيتا د 3 4000 لزقة باكت 200 — الهضبة الاثنين نقدى0.pdf p.15; فيتا دى ٣- ٤٠٠٠ مجم لصقات — كيور فارما خاص.pdf p.6 | تطابق الصنف والتركيز والشكل الدوائي |
| فيتا زنك  كبسول | recovered_match | فيتازنك ان كبسول\ايبيكو — الهضبة الاثنين نقدى0.pdf p.15 | تطابق الصنف والشكل الدوائي |
| فيرنيلار اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب; لا يوجد منتج مطابق في المستودع |
| فيروديونال كبسوله | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيزومير بيبي يونيدوز امبولات س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيفيدول سبراي | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيلافوريا20مجم30قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيلدافورمين50/1000مجم 30قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيلكسوفان كبسول س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيلوسيف 1جم 8قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيلوسيف500مجم كبسول س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيوتابان 1فيال س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيوتك نقط س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| فيوسيدل كريم | unresolved | فيوسيدين ۲۰جم كريم/ وسط — كيور فارما خاص.pdf p.6; فيوسيدين كريم كبير — كيور فارما خاص.pdf p.6; فيوسيدين كريم 20 جرام وسط — مخزن الحياة فارم اسكندريه-170.pdf p.4 | تطابق الصنف والشكل الصيدلي مع خطأ بصري |
| قرفة بالجنزبيل ايزيس | recovered_match | ايزيس زنجبيل بالقرفه 12 فلتر — الهضبة الاثنين نقدى0.pdf p.5; ايزيس زنجبيل بالقرفه 20 فلتر جديد — الهضبة الاثنين نقدى0.pdf p.5 | تطابق شاي زنجبيل بالقرفة ايزيس |
| كابرجامون 5مجم اقراص س ج | supported_no_match | كابريجامون ٠,٥ جم ٢ قرص — كيور فارما خاص.pdf p.6 | اختلاف التركيز 5 مجم مقابل 0.5 |
| كابوتن 25مجم 20قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كابوزايد 30قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كاتونيك مضمضه | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كاتيفاروكس10مجم شراب | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كارديوتون اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كارفيبرس25مجم2شريط | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كارفيد 25مجم 2شريط | supported_no_match | كارفيد ٦,٢٥ ق سعر جديد — المكرومي المنصورة.pdf p.3 | اختلاف في التركيز 6.25 مجم مقابل 25; اختلاف في التركيز بين 25 و 6.25 |
| كارنيتول بلس برطمان س ج | recovered_match | كارنيتول بلس كبسول جديد — كيور فارما خاص.pdf p.6; كارنيتول ٥٠٠ مجم ۳۰ ك"جديد — كيور فارما خاص.pdf p.6 | تطابق صنف كارنيتول بلس والشكل; لا يوجد منتج مطابق في المستودع |
| كالدين سي كي اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كالسيزوم د 60 كبسوله | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كالوبين  نقط س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كاندي بلوك دي 20اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كانديكيور لبوس مهبلي | recovered_review | كاندكيور كريم عادي/باكت 10 — الهضبة الاثنين نقدى0.pdf p.17 | اختلاف الشكل الدوائي كريم مقابل لبوس |
| كلاريتين اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كلاريتين شراب | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كلافوران 1جم فيال | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كلوزابكس 25 مجم س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كلوزابين100 اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كوادريدرم كريم30جم س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كورتكس شامبو للقشره | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كورتوبكت 30كبسوله س ج | supported_no_match | كورتوبكت ادفانس اقراص — الهضبة الاثنين نقدى0.pdf p.17; كورتوبكت بلس كبسول ج — الهضبة الاثنين نقدى0.pdf p.17 | اختلاف نوع الصنف بلس وادفانس |
| كورفيبيك20كبسوله س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كوفرسيل 5مجم 30قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كوفرسيل1.25/5 بلس اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كوفرسيل2.5/10 بلس اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كولشيسين0.5مجم100قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كولوفيرين  أيه 30قرص س ج | supported_no_match | كولوفرين د ۳۰ قرص — المكرومي المنصورة.pdf p.3; لوفرين دي اقراص ركز تشغيلة/باكت 0 — الهضبة الاثنين نقدى0.pdf p.17; كولوفرين د قرص — كيور فارما خاص.pdf p.6; كولوفرين دى اقراص/باكو60 — مخزن الحياة فارم اسكندريه-170.pdf p.4 | اختلاف النوع كولوفرين أيه مقابل د |
| كونجي كلير فورت قطرة س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونجيستال شراب س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونجيستال20قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونفاجران100مجم30قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونفنتين300اقراص اكس ار3شريط س ق | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونفنتين300اقراص3شريط س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونفنتين400مجم 30كبسوله | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كونفنتين400مجم 30كبسوله س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كويتابين 25مجم 30قرص س ج | supported_no_match | كويتابين 200 مج اقراص ج — الهضبة الاثنين نقدى0.pdf p.18 | اختلاف التركيز 25 مجم مقابل 200 |
| كويتكول200مجم30قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كيتاديل25مجم30قرص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كيتوبريك 75مجم 20كبسولة س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| كيتوفان25مجم30قرص س ج | supported_no_match | كيتوفان 50 مج كبسول ج — الهضبة الاثنين نقدى0.pdf p.18 | اختلاف التركيز 25 مجم مقابل 50 |
| كيمبوكسون 1جم فيال عضل | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لاكتوديل20قرص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لاكسيول بي ملين اقراص | recovered_match | لاكسيول بي ۲ شريط — كيور فارما خاص.pdf p.7 | تطابق تام لصنف لاكسيول بي |
| لبن ابتاميل 1 ادفانس | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لبن ان شور فانيليا 400 مجم | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لبن انفاتريني | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لبن بيبيلاك 3 بيبي جونيور | recovered_match | بيبيلاك ١ لين — المكرومي المنصورة.pdf p.2; بيبيلاك 1 لبن باكت 12 سعر 345جنيا — الهضبة الاثنين نقدى0.pdf p.7; بيبيلاك 2 لبن جديد/باكت 12 — الهضبة الاثنين نقدى0.pdf p.7; بيبيلاك 3 بيبي جونيور/باكت 12 تشغيل — الهضبة الاثنين نقدى0.pdf p.7 | تطابق تام لصنف بيبيلاك 3 |
| لبن بيبيلاك بريماتيور | supported_no_match | بيبيلاك ١ لين — المكرومي المنصورة.pdf p.2; بيبيلاك 1 لبن باكت 12 سعر 345جنيا — الهضبة الاثنين نقدى0.pdf p.7; بيبيلاك 2 لبن جديد/باكت 12 — الهضبة الاثنين نقدى0.pdf p.7; بيبيلاك 3 بيبي جونيور/باكت 12 تشغيل — الهضبة الاثنين نقدى0.pdf p.7; بيبيلاك اف ال لبن — الهضبة الاثنين نقدى0.pdf p.7 | اختلاف نوع الحليب بريماتيور غير متوفر |
| لبن بيديا ستارت 2 | supported_no_match | لبن بيديا ستارت رقم 1/ باكت 24 — الهضبة الاثنين نقدى0.pdf p.18 | اختلاف في المرحلة رقم 1 مقابل 2 |
| لوبيكونت8مجم اقراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لورنوكسيكام 8 مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة للاسم المطلوب |
| لوسيدريل250مجم 20قرص | supported_no_match | لوسيدريل ٥٠٠ مجم قرص — كيور فارما خاص.pdf p.7; لوسيدريل ٥٠٠ — المكرومي المنصورة.pdf p.3; لوسيدريل 500 مج اقراص — الهضبة الاثنين نقدى0.pdf p.19 | اختلاف في التركيز 500 مجم مقابل 250; اختلاف في التركيز بين 250 و 500 |
| ليبانتيل 300مجم 3شريط س ج | supported_no_match | ليبانتيل 160سوبرا اقراص/باكت 100 — الهضبة الاثنين نقدى0.pdf p.19; ليبانتيل سوبرا اقراص — كيور فارما خاص.pdf p.7 | اختلاف في نوع المستحضر سوبرا والتركيز |
| ليبانتيل145اقراص س ج | unresolved | ليبانتيل 160سوبرا اقراص/باكت 100 — الهضبة الاثنين نقدى0.pdf p.19; ليبانتيل سوبرا اقراص — كيور فارما خاص.pdf p.7 | نقص بيانات التركيز يمنع تأكيد المطابقة |
| ليبترين 10/10مجم 14قراص | no_plausible_candidate_found | None found in this audit | لا توجد منتجات مطابقة لاسم ليبترين |
| ليبراكس اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليبراكس |
| ليبوفيريك فوليك 120 مل شرب | supported_no_match | ليبوفيريك كبسول — الهضبة الاثنين نقدى0.pdf p.19 | اختلاف في التركيبة والشكل الدوائي |
| ليبونكس 25مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليبونكس |
| ليسيد  لوسيون | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليسيد |
| ليفانيك500مجم 7قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليفانيك |
| ليفوفلوكساسين500مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليفوفلوكساسين; لا يوجد منتج مطابق في المستودع |
| ليفوفلوكساسين750مجم 5قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ليفوفلوكساسين; لا يوجد منتج مطابق في المستودع |
| ليليبل10مجم اقراص | recovered_review | ليلبيل اكياس /باكت42 — الهضبة الاثنين نقدى0.pdf p.19 | نفس المنتج مع اختلاف الشكل أكياس |
| ليمتلس بي كومبلكس لزقه | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لليمتلس بي كومبلكس |
| ليمتلس ليبوفيركس40مجم كبسولات | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لليمتلس ليبوفيركس |
| لينتوجيستون250مجم1امبول | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم لينتوجيستون |
| ماء غريب سمايل س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لماء غريب |
| ماء نونو شراب س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لماء نونو |
| مارفيل كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لمارفيل كريم |
| مارفيلون 21قرص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مارفيلون |
| ماريفان3مجم3شريط س ج | recovered_match | ماريفان 1ملجم/جلاكسو — السلام شبين.pdf p.5; ماريفان 3 مجم/جلاكسو — السلام شبين.pdf p.5; ماريفان 5 ملجم/جلاكسو — السلام شبين.pdf p.5 | تطابق تام في الاسم والتركيز والشكل |
| ماكسفول كبسول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ماكسفول |
| ماكسوفاج1جم اكس ار اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ماكسوفاج |
| مالكون كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مالكون |
| مامي كير50جم كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لمامي كير |
| مانوفيبركين بلس اسبراي س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مانوفيبركين |
| موفليكس نانو اسبراي | recovered_match | موف ليكس ادفانس كبسول دولاب — الهضبة الاثنين نقدى0.pdf p.20; موف ليكس التراكبسول — الهضبة الاثنين نقدى0.pdf p.20; موف ليكس سبراى /باكت41 — الهضبة الاثنين نقدى0.pdf p.20 | تطابق تام في المنتج والشكل الدوائي; لا يوجد منتج مطابق في المستودع |
| موكسيسيارو بلس قطرة | supported_no_match | موكسيسارو محلول/باكت 60 — الهضبة الاثنين نقدى0.pdf p.20; سينارو بلس قطرة — كيور فارما خاص.pdf p.5 | تعارض في إضافة بلس للمنتج |
| مونتيلوراما 10مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مونتيلوراما |
| مونودكسين 1% قطرة عين | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مونودكسين |
| مويست 1 كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لمويست 1 |
| مياكلسيك 100  وحدةامبول ث | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مياكلسيك |
| ميثوريلاكس 30 قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ميثوريلاكس |
| ميديفا ميون شراب | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لميديفا ميون |
| ميراج 500مجم حقن | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ميراج |
| ميلجا ماكس30قرص | recovered_match | ليمتلس ميلجا ماكس — كيور فارما خاص.pdf p.7; ميلجا عاديه ۱۰۸ج — المكرومي المنصورة.pdf p.4; ميلجا ادفانس اقراص/ باكت 78 — الهضبة الاثنين نقدى0.pdf p.20; ميلجا ادفانس س.ج باكت78 — مخزن الحياة فارم اسكندريه-170.pdf p.5; ميلجا ادفانس — كيور فارما خاص.pdf p.7 | تطابق تام مع ليمتلس ميلجا ماكس |
| ميلوسكار جل15جم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم ميلوسكار |
| مينرو10كيس | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مينرو; لا يوجد منتج مطابق في المستودع |
| مينوفللين ان امبول | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم مينوفللين |
| ميوكوسول شراب اطفال س ج | recovered_review | ميوكوسول كبسول/ باكت 20 — الهضبة الاثنين نقدى0.pdf p.20 | نفس المنتج مع اختلاف الشكل كبسول; لا يوجد منتج مطابق في المستودع |
| ناتريلكس اس ار 30قرص س ج | recovered_match | ناتريليكس اس ار سعرجديد — مخزن الحياة فارم اسكندريه-170.pdf p.5 | تطابق تام في المنتج والاسم التجاري |
| نايت كالم 3جرام اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لنايت كالم |
| نت لوك 20مجم اقراص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نت لوك |
| نت لوك40مجم20قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نت لوك |
| نودي بخاخ انف | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نودي |
| نورجيستادول21قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نورجيستادول |
| نورجيسك اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نورجيسك |
| نوريجنسين امبول/ميزوسيبت | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نوريجنسين |
| نوفالجين ابلونج 10قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نوفالجين |
| نوفوكوبال30قرص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نوفوكوبال |
| نوليفر كريم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نوليفر |
| نويوريك300مجم اقراص س ج | supported_no_match | نو - يوريك 100 مجم اقراص\ايبيكو — السلام شبين.pdf p.5 | اختلاف في التركيز 100 مقابل 300 |
| نيبليت 5مجم 14قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيبليت |
| نيتروماك ريتارد2.5مجم كبسول | recovered_match | نيتروماك 5 مج اقراص/باكت 60 — الهضبة الاثنين نقدى0.pdf p.21; نيتروماك ريتارد كبسول/التنشيط — السلام شبين.pdf p.5 | تطابق الاسم والشكل الدوائي دون تعارض |
| نيتروماك ريتارد2.5مجم كبسول س ج | recovered_match | نيتروماك 5 مج اقراص/باكت 60 — الهضبة الاثنين نقدى0.pdf p.21; نيتروماك ريتارد كبسول/التنشيط — السلام شبين.pdf p.5 | تطابق الاسم والشكل الصيدلي دون تعارض |
| نيرهافلكس40مجم20فيلم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيرهافلكس |
| نيفروميد ادفانس 14كيس س ج | supported_no_match | نفروميد اقراص عادى — الهضبة الاثنين نقدى0.pdf p.21 | اختلاف نوع ادفانس والشكل الصيدلي |
| نيفيلوب12.5/5مجم بلاس20قرص | recovered_match | نيفيلوب ٢٫٥مجم قرص — كيور فارما خاص.pdf p.7; نيفيلوب ٥ مجم اقراص — كيور فارما خاص.pdf p.7; نيفيلوب 2.5 مج اقراص ج/باكت 48 — الهضبة الاثنين نقدى0.pdf p.21; نيفيلوب 5 مج قرص عادى/باكت 48 — الهضبة الاثنين نقدى0.pdf p.21; نيفيلوب 5/25 مج بلاس اقراص — الهضبة الاثنين نقدى0.pdf p.21; نيفيلوب ٢,٥ سعر جديد ٤٦ ج — المكرومي المنصورة.pdf p.4; نيفيلوب ٥ ساده سعر جديد — المكرومي المنصورة.pdf p.4; نيفيلوب بلس ١٢٫٥/٥مجم قرص — كيور فارما خاص.pdf p.7; نيفيلوب بلس ٥/٢٥ مجم قرص — كيور فارما خاص.pdf p.7 | تطابق تام للاسم والتركيز نيفيلوب بلس |
| نيكسكيور10مجم14كيس | supported_no_match | نيكسكيور ٤٠ مجم قرص ۲ شريط — كيور فارما خاص.pdf p.7; نيكسيكور ۲۰ مجم ١٤ قرص — المكرومي المنصورة.pdf p.4; نيكسيكور ٤٠ مجم ۲۰ قرص ١٥٢ج — المكرومي المنصورة.pdf p.4; نكسيكيور 40 مج اقراص/باكت 96 — الهضبة الاثنين نقدى0.pdf p.21 | اختلاف في التركيز والشكل الصيدلي |
| نيكسكيور5مجم28كيس | supported_no_match | نيكسكيور ٤٠ مجم قرص ۲ شريط — كيور فارما خاص.pdf p.7; نيكسيكور ۲۰ مجم ١٤ قرص — المكرومي المنصورة.pdf p.4; نيكسيكور ٤٠ مجم ۲۰ قرص ١٥٢ج — المكرومي المنصورة.pdf p.4; نكسيكيور 40 مج اقراص/باكت 96 — الهضبة الاثنين نقدى0.pdf p.21 | اختلاف التركيز 20 و40 مقابل 5 |
| نيكسيبرازول 40مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيكسيبرازول |
| نيكسيبرونش شراب200مل بالعسل س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيكسيبرونش |
| نيل 15مل محلول اظافر س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لمحلول نيل |
| نيورازين25مجم اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيورازين |
| نيوروتون30قرص س ق | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيوروتون; لا يوجد منتج مطابق في المستودع |
| نيوزوليد 600 مجم3قرص س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيوزوليد |
| نيوكلاف642اكسترا شراب100مل س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم نيوكلاف; لا يوجد منتج مطابق في المستودع |
| هيالوكونكس سيرم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لهيالوكونكس سيرم |
| هيباتوفورت 30كبسولة امون س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم هيباتوفورت |
| هيدروكين 200مجم 20قرص س ج | recovered_match | هيدروكين\مينا — السلام شبين.pdf p.5 | تطابق تام للمنتج هيدروكين مينافارم |
| هيرباك 5% لوسيون اخضر | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم هيرباك |
| هيرباك بلس فوم | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لهيرباك بلس |
| هيرو دي3+كي2 نقط | recovered_match | هيرو في د 3 نقط/باكت12 — الهضبة الاثنين نقدى0.pdf p.21; هيرو فى دى ثرى نقط"جديد — كيور فارما خاص.pdf p.8; هيرو فى اى دى ثرى كيه نقط"جديد — كيور فارما خاص.pdf p.8 | تطابق تام مع هيرو في دي كيه; لا يوجد منتج مطابق في المستودع |
| هيستازين نقط  للفم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم هيستازين |
| هيلاريوم 15جم كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم هيلاريوم |
| هيلسك 20مجم14كبسول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق لاسم هيلسك |
| هيمالتوز شراب120مل | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| هيموجيت 6  امبول س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| هيموستوب 3امبول | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| هيموكلار كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| ون تو ثري 20قرص س ج | recovered_review | وان تو ثرى شراب\الكان فارما — السلام شبين.pdf p.5 | اختلاف الشكل الدوائي من أقراص لشراب |
| ويستابريث.5مجم20قرص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| يورينكس كبسول | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| يوكيراتو كريم س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| يونايتد فيت اقراص | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
| يونيبريدول100مل شراب | supported_no_match | يونى بريدول فورت شراب/باكت25 — الهضبة الاثنين نقدى0.pdf p.22 | تعارض لاختلاف المتغير بوجود كلمة فورت |
| يونيلوكسام500مجم2شريط س ج | no_plausible_candidate_found | None found in this audit | لا يوجد منتج مطابق للاسم المطلوب |
