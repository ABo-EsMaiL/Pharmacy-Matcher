# Pharmacy Matcher

Desktop item-presence matching for pharmacy shortage lists and warehouse PDFs.
The current application uses `FastCoordinator`, structured Gemini Vision
extraction, candidate retrieval, Python validation, and Excel output.

## Run on Windows

1. Install Python 3.10+ and the requirements (`setup.bat` can prepare a local venv).
2. Copy `.env.example` to `.env` and set `MSEMAX_API_KEY` to your local gateway key.
3. Configure and start the separate MSEMAX-GAIStudio-vision gateway on port 8001.
4. Launch `run.bat` and check gateway paths and credentials in Desktop App settings.

Current matching settings: Gemini 3.8 Flash, batch 75, Thinking HIGH,
Google Search OFF, Fresh Chat ON. MSEMAX itself is a separate project and is not
included here. `main.py` is the legacy entry point; use `run.bat` for the current app.

## Matching and extraction

- Structured warehouse trade names are primary; raw-name hypotheses support OCR variants.
- Presence and attribute compatibility are evaluated separately.
- Final outputs are MATCH, REVIEW and NO_MATCH; Python validates candidate selection.
- The approved decision graph is documented in [SYSTEM_ARCHITECTURE_GRAPH.md](SYSTEM_ARCHITECTURE_GRAPH.md).
- Vision processes pages individually, with resumable global cache at
  `data/cache/vision/<SHA-256>/`. Identical PDF bytes reuse extraction across paths,
  filenames and process runs. Historical per-process caches can be imported by hash.

## Tests

```powershell
python -m unittest discover -s tests
```

The full local suite currently has 123 tests. One historical retrieval test reads
the included PROC-019 cache fixtures. The new cache and attribute tests use synthetic
fixtures and mocked gateway responses:

```powershell
python -m unittest discover -s tests -p test_global_vision_cache.py
python -m unittest discover -s tests -p test_structured_attribute_normalization.py
```

Run the official `tests/` directory explicitly; root-level discovery may include
historical scratch scripts on a development machine.

## Data, outputs and development history

`data/`, `output/`, and `CHAT/` include warehouse inputs, process results,
OCR caches, audit reports, Excel outputs and archived development sessions.
Historical credential strings in `CHAT/` are replaced with `[REDACTED_CREDENTIAL]`.
Some archived transcript chunks split UTF-8 characters across files; they are
kept as archival chunks rather than rewritten or treated as standalone JSON.

Live credentials remain local: `.env` and `data/settings.json` are ignored.
Use `.env.example` and `data/settings.example.json` as configuration templates.
Top-level scratch work, original unredacted backups, bytecode, transient locks
and build output are not published.
