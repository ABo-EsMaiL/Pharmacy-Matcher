"""
File handler module - detects file type and routes to appropriate reader.
"""

import json
from pathlib import Path
from ..config import gateway_api_key

from .excel_reader import read_excel, extract_item_names
from .markdown_reader import read_markdown_file
from .gemini_vision_extractor import extract_items_from_pdf_vision
from .pdf_reader import parse_structured_result

_EXCEL_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
_PDF_EXTENSIONS = {".pdf"}
_JSON_EXTENSIONS = {".json"}


from concurrent.futures import ThreadPoolExecutor, as_completed


def _process_single_file(
    filepath: Path,
    vision_api_url: str = "http://127.0.0.1:8001/v1/chat/completions",
    vision_api_key: str = gateway_api_key(),
    vision_model: str = "gemini-3.8-flash",
    api_key: str | None = None,
    base_url: str = "https://transform.unstructured.io",
    gemini_api_key: str | None = None,
    profile: str = "balanced"
) -> tuple[str, list[dict]]:
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    print(f"\n  -> [START] Processing file: {filepath.name} (Type: {ext})")
    try:
        if ext in _EXCEL_EXTENSIONS:
            items = _process_excel_file(filepath)
        elif ext in _MARKDOWN_EXTENSIONS:
            items = _process_markdown_file(filepath)
        elif ext in _PDF_EXTENSIONS:
            items = _process_pdf_file(
                filepath,
                vision_api_url=vision_api_url,
                vision_api_key=vision_api_key,
                vision_model=vision_model,
                legacy_api_key=api_key,
                legacy_base_url=base_url
            )
        elif ext in _JSON_EXTENSIONS:
            items = _process_json_file(filepath)
        else:
            print(f"[!] Unsupported extension: {ext} for {filepath.name}")
            return filepath.name, []

        print(f"  -> [DONE] {filepath.name}: {len(items)} items extracted.")
        return filepath.name, items
    except Exception as e:
        print(f"[!] Exception processing {filepath.name}: {e}")
        return filepath.name, []


def read_input_files(
    filepaths: list[Path],
    role: str,
    vision_api_url: str = "http://127.0.0.1:8001/v1/chat/completions",
    vision_api_key: str = gateway_api_key(),
    vision_model: str = "gemini-3.8-flash",
    api_key: str | None = None,
    base_url: str = "https://transform.unstructured.io",
    gemini_api_key: str | None = None,
    profile: str = "balanced",
) -> dict[str, list[dict]]:
    role_label = "Shortages" if role == "shortages" else "Warehouse"
    print(f"\n{'='*60}")
    print(f"[*] Processing {role_label} files ({len(filepaths)} file(s)) [PARALLEL WORKERS]")
    print(f"{'='*60}")

    results: dict[str, list[dict]] = {}

    if not filepaths:
        return results

    # Process files sequentially so single-tab browser gateway processes one file/page at a time cleanly
    for idx, fp in enumerate(filepaths, start=1):
        print(f"\n[{role_label} {idx}/{len(filepaths)}] Starting file: {Path(fp).name}")
        fname, items = _process_single_file(
            fp,
            vision_api_url=vision_api_url,
            vision_api_key=vision_api_key,
            vision_model=vision_model,
            api_key=api_key,
            base_url=base_url,
            gemini_api_key=gemini_api_key,
            profile=profile
        )
        results[fname] = items

    total = sum(len(items) for items in results.values())
    print(f"\n{'='*60}")
    print(f"[+] Completed {role_label}: {total} items from {len(results)} file(s)")
    print(f"{'='*60}\n")

    return results


def _process_excel_file(filepath: Path) -> list[dict]:
    rows = read_excel(filepath)
    items = extract_item_names(rows, source_file=filepath.name)
    return items


def _process_markdown_file(filepath: Path) -> list[dict]:
    return read_markdown_file(filepath)


def _process_pdf_file(
    filepath: Path,
    vision_api_url: str = "http://127.0.0.1:8001/v1/chat/completions",
    vision_api_key: str = gateway_api_key(),
    vision_model: str = "gemini-3.8-flash",
    legacy_api_key: str | None = None,
    legacy_base_url: str = "https://transform.unstructured.io"
) -> list[dict]:
    # Pure Gemini Vision Extraction
    return extract_items_from_pdf_vision(
        filepath=filepath,
        api_url=vision_api_url,
        api_key=vision_api_key,
        model=vision_model
    )


def _process_json_file(filepath: Path) -> list[dict]:
    """Process cached Unstructured JSON to save API limits."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    # We now assume the JSON is a saved ExtractionResult
    items = parse_structured_result(data, filepath.name)
    
    return items
