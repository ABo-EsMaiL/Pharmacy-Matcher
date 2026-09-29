# Raw request identity views — PROC-020 recall check

## Files changed

- Production: `src/fast_match/search.py`, `src/fast_match/attributes.py`.
- Synthetic tests: `tests/test_raw_identity_views.py` (21 new tests).
- Offline audit utility: `scratch/check_raw_views_recall.py`.

## What changed

Raw requests retain their original text, normalized full reference, span-masked reference, and multiple identity hypotheses. Known forms, usage descriptions, count/volume/price spans, attached combination/form tokens and pre-slash descriptions are handled generically. Only meaningful name hypotheses supply name evidence; full raw text or a shared usage descriptor cannot bypass the gate.
Warehouse structured trade names remain primary and explicitly supplied descriptive words are preserved. Whole-token extensions, reordered tokens, and nearby OCR transpositions are uncertain candidates, never automatic aliases. Original fields and identity views remain in provider payloads. No medicine-specific names or pairs were added to production or the new tests.

## Old flow / New flow

Old: one extracted raw trade name → whole-name comparison → candidate loss when descriptions remain.
New: raw request → identity hypotheses → comparison with structured warehouse trade name / raw fallback → deduplicated candidate set → existing attribute evaluation and LLM adjudication for uncertainty.

## Regression tests

`D:/miniconda3/envs/venv/python.exe -B -m unittest discover -s tests`
85 tests passed: existing 64 plus 21 synthetic tests. Includes the Desktop App’s FastCoordinator path with live provider calls blocked. No GUI/live-provider validation was performed. Root pytest was not run and is not claimed green.

## Results

All 2,718 actual structured warehouse rows from 46 cached pages were searched for each of the 42 historical audit cases. The selected historical target must itself survive; a different candidate does not count as recovery.

| Metric | Before | After |
|---|---:|---:|
| Audited target retrieved | 20/42 | 40/42 |
| Candidate pairs after gate | 67 | 131 |
| Cases with no candidate at all | 19 | 1 |

Candidate pairs examined: 114156. Local routes for the 40 recovered targets: 7 MATCH, 7 REVIEW, 26 ambiguous. These are local routes, not new LLM-adjudicated outcomes. Actual LLM calls: 0. No new PROC was run.

## Remaining blockers

| Request | Historical target in cache | Rejection |
|---|---|---|
| فيتا دي ثري4000ميكروفيلم | فيتا د 3 4000 لزقة باكت 200 | insufficient_full_name_coverage |
| هيرو دي3+كي2 نقط | هيرو فى اى دى ثرى كيه نقط"جديد | insufficient_full_name_coverage |

These two names contain compounded letter/number spellings and extra identity words. The first also retains an unrecognized microfilm description and an unlabelled number; the second contains additional short tokens in the structured trade name. Current whole-name evidence does not establish a plausible alignment. No guessed phonetic aliases or special acceptance rules were added to force these cases through.

## Remaining risk / release gate

**NOT READY FOR FULL PROC: 40/42 is an improvement, not a pass of the requested 42/42 recall gate.** Candidate recall here applies only to the 42 historical selected targets. Precision and live LLM outcomes for the expanded candidate set have not been measured. The two misses remain blockers.
All 46 cache fingerprints match before/after. All 117 protected files from the preceding baseline (PROC-020 artifacts, settings, Config, Vision extractor) are unchanged. No Decision Graph, coordinator, model, batch, Search, Thinking, Fresh Chat, or MSEMAX changes were made in this iteration.

Aggregate gate rejections: `{"full_name_edit_budget_exceeded": 66023, "insufficient_full_name_coverage": 47993, "weak_full_name_character_evidence": 9}`.

Detailed evidence: `before.json`, `verified_final.json`, `regression.log`.
