# Symbolic identity investigation — final offline report

## Files changed

- `src/fast_match/identity_symbols.py`: bounded whole-token spoken-digit/letter hypotheses; independent product-name anchor; optional generic film/patch descriptor removal.
- `src/fast_match/search.py`: compare those hypotheses with the existing whole-name gates, always returning uncertain identity evidence.
- `tests/test_identity_symbols.py`: 15 new synthetic tests.

## Behavior

Original raw text, structured trade_name, strength, form, package and numeric parsing are unchanged. The language lexicon covers generic digit/letter spellings, not products. Arabic/Latin/Persian digits and attached/spaced codes are compared only in optional hypotheses. Ambiguous letter spellings retain alternatives (bounded to 16 views). Shared codes cannot admit names that fail the independent full-name anchor comparison. No thresholds, Decision Graph, coordinator, model settings, Batch 75, Search OFF, Thinking HIGH, Fresh Chat ON or MSEMAX were changed.
Every decision relying on a new hypothesis is non-exact and goes to adjudication; it is never an automatic MATCH.

## Validation

`D:/miniconda3/envs/venv/python.exe -B -m unittest discover -s tests`: **100 tests passed**, comprising the existing 85 and 15 new synthetic tests. The suite covers raw and structured inputs, D3/K2 and other letter/digit representations, OCR Unicode, retained variants/attributes, uncertain descriptors, invalid partial/suffix evidence, and the final Python strength guard.
Root pytest was not run or claimed green. No Desktop GUI or live provider run was performed.

| Recall metric | Before | After |
|---|---:|---:|
| Historical selected targets retrieved | 40/42 | 42/42 |
| Candidate pairs after gate | 131 | 134 |
| Requests with no candidate | 1 | 0 |

All 2,718 actual structured rows across 46 PROC-020 cached pages were searched, with 114,156 request/candidate pairs examined. Zero LLM calls; zero new PROC runs. All 46 cache fingerprints and all 123 protected file hashes are unchanged.
Local routes for the 42 selected historical targets: 7 MATCH, 7 REVIEW, 28 ambiguous. These are local routes, not LLM-adjudicated final outcomes.

## Previously missing targets

| Requested | Warehouse target | Route |
|---|---|---|
| فيتا دي ثري4000ميكروفيلم | فيتا د 3 4000 لزقة باكت 200 | ambiguous / ocr_or_incomplete_name |
| هيرو دي3+كي2 نقط | هيرو فى اى دى ثرى كيه نقط"جديد | ambiguous / ocr_or_incomplete_name |

Both missing targets now survive retrieval. There are no remaining misses in this 42-target check.

## Remaining limits

The generic spelling rule resolves retrieval, not the true product identity. In particular, extra spoken letters and missing variant information in the second case still require adjudication from supplied data. No equivalence of those fields was asserted. The third additional candidate is another cached row for the first previously missing request; it is also uncertain.
Passing this historical recall set and synthetic negatives does not establish population-wide precision or final matching accuracy. Full PROC remains unrun as requested.

Evidence: `symbolic_identity_final.json`, `symbolic_identity_traces.json`, `symbolic_regression.log`.
