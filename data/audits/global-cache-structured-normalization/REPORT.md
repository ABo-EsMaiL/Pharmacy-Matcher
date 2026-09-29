# Global Vision cache and conservative structured attributes

## Files changed

- `src/extract/gemini_vision_extractor.py`
- `src/fast_match/attributes.py`
- `src/fast_match/search.py` (unified attributes / payload only; retrieval functions unchanged)
- `src/fast_match/coordinator.py` (structured attribute uncertainty guard)
- Added `tests/test_global_vision_cache.py` and `tests/test_structured_attribute_normalization.py`.
- Updated the existing structured-volume expectation in `tests/test_structured_presence.py` to REVIEW, as explicitly requested. Raw package-volume and topical package-mass tests retain their existing expectations.

## Tests passed

123/123 official tests passed with `D:/miniconda3/envs/venv/python.exe -B -m unittest discover -s tests`.
23 new synthetic tests: 9 for caching, 14 for structured attribute normalization. Root pytest/scratch was not used or claimed green.
Cache fixtures are real synthetic PDFs rendered by PDFium; Gemini HTTP responses are mocked. No live Gemini or new PROC was run.

## Global cache behavior

Primary lookup: `data/cache/vision/<full SHA-256>/`. Source path, filename, process number and mtime do not define identity.
The one-page synthetic PDF copied to path A, renamed at path B, and copied into two different PROC input folders caused exactly ONE mocked Gemini extraction request across all four loads.
A changed PDF with preserved mtime caused a new cache/extraction. Added/removed pages change content identity; restoring identical bytes correctly reuses the old cache.
Per-page resume, manifest recovery, atomic result/image writes, corrupted-page repair, and concurrent identical-content calls are covered. OS locks also serialize shared-cache writers across processes; automated concurrency coverage uses threads.
Legacy per-process caches are imported lazily by full manifest hash and page count, without changing historical files. Returned source_file follows the current filename; source_page remains correct.

## Attribute normalization behavior

An explicitly supplied strength field containing 500, 500 mg, 500مجم or ٥٠٠ مجم shares the same internal numeric evidence. Numeric JSON fields and decimal separators are supported. The original value and unspecified-unit provenance remain available; no unit is invented in the source field.
This rule does not parse arbitrary raw-name numbers as strength, and does not infer unitless 500 equals 0.5 g, a volume, a percentage or a concentration. Existing explicit-unit arithmetic remains unchanged.

## 42-target recall result

42/42 selected historical targets retrieved across all 2,718 warehouse rows on 46 cached pages. Candidate pairs after gate remain 134; no-candidate cases remain zero. Local routes remain 7 MATCH, 7 REVIEW and 28 ambiguous; no LLM adjudication was performed.
All cache source hashes match the preceding check. All 686 protected historical/process/configuration files match the pre-edit snapshot. The Decision Graph, retrieval algorithms, symbolic identity module, Gemini configuration, Batch 75, Search OFF, Thinking HIGH, Fresh Chat ON and MSEMAX were not changed.
Detailed recall evidence: `../PROC-020-raw-views-recall/global_cache_attributes.json`.

## Anything intentionally left REVIEW

- 500 mg versus 250 mg: explicit strength conflict.
- 500 mg versus 500 ml: incompatible measurement type.
- Explicit structured volume 60 ml versus 120 ml: REVIEW.
- Volume written inside the structured strength field: REVIEW for uncertain field meaning, even though it is retained as package metadata too.
- 30 mg versus 30 mg / 2 ml: uncertain measurement basis; Python prevents a final automatic MATCH.
- Unknown/missing structured volume, unsupported strength notation and structured/raw disagreements remain conservative.

No full PROC was launched.
