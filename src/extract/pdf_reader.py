"""
PDF extraction module using Unstructured Transform Client.
Handles direct single-step extraction, server-side caching, and local caching.
"""

from pathlib import Path
import json
import hashlib
import time

def _get_file_hash(filepath: Path) -> str:
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def extract_items_from_pdf(
    filepath: Path,
    api_key: str,
    base_url: str = "https://transform.unstructured.io",
    gemini_api_key: str = None,
    profile: str = "balanced",
) -> list[dict]:
    """
    Extract drug product items from PDF using Unstructured API.
    Checks local cache first, then existing server jobs, and finally uploads if new.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    print(f"[*] Processing PDF file: {filepath.name}")

    # 0. Alongside JSON Check (Instant load from previous runs)
    alongside_json = filepath.with_suffix('.json')
    if alongside_json.exists():
        try:
            with open(alongside_json, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            cached_items = parse_structured_result(result_data, filepath.name)
            if len(cached_items) > 0:
                print(f"[+] Loaded {len(cached_items)} items from alongside JSON: {alongside_json.name}")
                return cached_items
        except Exception as e:
            print(f"[*] Could not read alongside JSON: {e}")

    # 1. Local Cache Check
    file_hash = _get_file_hash(filepath)
    cache_dir = filepath.parent.parent.parent / 'data' / '.unstructured_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{file_hash}_extract.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            cached_items = parse_structured_result(result_data, filepath.name)
            if len(cached_items) > 0:
                print(f"[+] Loaded {len(cached_items)} items from local cache: {filepath.name}")
                return cached_items
            else:
                print(f"[*] Local cache has 0 items for {filepath.name}. Checking server...")
        except Exception:
            print(f"[*] Local cache invalid for {filepath.name}. Checking server...")

    try:
        from unstructured_transform_client import TransformClient
    except ImportError:
        print("⚠️ unstructured-transform-client not found. Please install it:")
        print("pip install unstructured-transform-client")
        raise RuntimeError("unstructured-transform-client is required to process PDFs")

    client = TransformClient(
        api_key=api_key,
        server_url=base_url,
    )

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Supplier Product Names",
        "description": "Extract product entries from all pages as source data only. Return one entry per source product row, preserving duplicates and different strengths. Include products even when price or quantity is blank or zero. Copy names faithfully without spelling repair or inferred digits. Do not infer stock, requested quantities or shortage matches.",
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "Every product entry from every page, in document order. Keep repeated entries. Exclude document headers, footers, contact details, column labels and totals.",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_name_raw": {
                            "type": "string",
                            "description": "Copy the complete product name/description exactly as present in the source, preserving Arabic, English, mixed text, spelling, strengths, units, dosage form, pack numbers, punctuation and manufacturer text. Do not correct, translate or complete it. Exclude values belonging to separate price, discount or quantity columns, but retain numbers written inside the name itself.",
                        },
                        "source_page": {
                            "type": [
                                "integer",
                                "null",
                            ],
                            "description": "The 1-based source page containing this product entry, taken from the source page metadata. Return null when unavailable; do not guess.",
                        },
                    },
                    "required": [
                        "item_name_raw",
                        "source_page",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "items",
        ],
        "additionalProperties": False,
    }

    # 2. Check Existing Completed Jobs on Server (Avoid re-uploading!)
    print(f"[*] Checking if {filepath.name} is already processed on Unstructured server...")
    try:
        for job in client.jobs.iterate():
            source = getattr(job, "source", None)
            fname = getattr(source, "filename", None) if source else None
            st = str(getattr(job, "status", "")).lower()
            if fname == filepath.name and "completed" in st:
                job_id = getattr(job, "id", None)
                if job_id:
                    print(f"[+] Found existing completed job on server (ID: {job_id}) for {filepath.name}!")
                    server_job = client.jobs.get(job_id)
                    job_data = server_job.model_dump() if hasattr(server_job, "model_dump") else dict(server_job)
                    items = parse_structured_result(job_data, filepath.name)
                    if len(items) > 0:
                        print(f"[+] Downloaded {len(items)} items directly from server without re-uploading!")
                        # Cache locally
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(job_data, f, ensure_ascii=False, indent=2, default=str)
                        return items
    except Exception as e:
        print(f"[*] Note: Server job lookup skipped: {e}")

    # 3. Upload and Extract in One Single Operation
    try:
        print(f"[*] Uploading and extracting {filepath.name} via Unstructured AI (Profile: {profile.upper()})...")
        try:
            with open(filepath, "rb") as f:
                result = client.extract.from_document(
                    input=f,
                    schema=schema,
                    profile=profile,
                    wait_seconds=20
                )
        except Exception as err:
            err_msg = str(err).lower()
            if profile != "balanced":
                print(f"[*] Profile {profile.upper()} failed ({err}). Retrying automatically with BALANCED profile...")
                return extract_items_from_pdf(filepath, api_key, base_url, profile="balanced")
            else:
                raise

        if hasattr(result, 'model_dump'):
            result_data = result.model_dump()
        elif hasattr(result, '__dict__'):
            result_data = result.__dict__
        else:
            result_data = dict(result)

        # Handle asynchronous job if returned 202 Accepted
        status_str = str(result_data.get("status", "")).lower()
        if any(s in status_str for s in ("queued", "processing", "in_progress")):
            job_id = result_data.get("id") or result_data.get("job_id")
            if job_id:
                print(f"[*] Processing on server (Job ID: {job_id}). Waiting for completion...")
                attempts = 0
                while attempts < 180:  # Up to 24 minutes
                    time.sleep(8)
                    attempts += 1
                    try:
                        job_res = client.jobs.get(job_id)
                        if hasattr(job_res, 'model_dump'):
                            job_data = job_res.model_dump()
                        elif hasattr(job_res, '__dict__'):
                            job_data = job_res.__dict__
                        else:
                            job_data = dict(job_res)
                    except Exception as poll_err:
                        print(f"[*] Polling note ({filepath.name}): {poll_err}")
                        continue

                    cur_status = str(job_data.get("status", "")).lower()
                    if "completed" in cur_status:
                        result_data = job_data
                        break
                    elif "failed" in cur_status or "error" in cur_status:
                        err_text = str(job_data.get("error", ""))
                        print(f"[!] Server job failed for {filepath.name}: {err_text}")
                        return []

                    if attempts % 3 == 0:
                        print(f"[*] {filepath.name} status: {job_data.get('status')} ... ({attempts * 8}s)")

                if attempts >= 180:
                    print(f"[!] Timeout reached (24 minutes) for {filepath.name}. Continuing with remaining files...")
                    return []

        items = parse_structured_result(result_data, filepath.name)

        if len(items) == 0 and gemini_api_key:
            print(f"[*] 0 items from Unstructured for {filepath.name}. Trying Gemini fallback...")
            items = _extract_with_gemini_fallback(filepath, gemini_api_key)
            if items:
                result_data = {"extracted_data": [{"data": {"items": items}}]}

        # Cache only if items extracted
        if len(items) > 0:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"[+] Saved valid local cache for: {filepath.name} ({len(items)} items)")

        # Save local json copy
        json_path = filepath.with_suffix(".json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            pass

        print(f"[+] Successfully extracted {len(items)} items from {filepath.name}")
        return items

    except Exception as e:
        print(f"[!] Extraction error for {filepath.name}: {e}")
        if gemini_api_key:
            print(f"[*] Trying Gemini fallback extraction for {filepath.name}...")
            items = _extract_with_gemini_fallback(filepath, gemini_api_key)
            if items:
                res_dict = {"extracted_data": [{"data": {"items": items}}]}
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(res_dict, f, ensure_ascii=False, indent=2, default=str)
                    with open(filepath.with_suffix(".json"), "w", encoding="utf-8") as f:
                        json.dump(res_dict, f, ensure_ascii=False, indent=2, default=str)
                    print(f"[+] Saved valid local cache via Gemini for: {filepath.name} ({len(items)} items)")
                except Exception:
                    pass
                return items
        return []


def _extract_with_gemini_fallback(filepath: Path, gemini_api_key: str) -> list[dict]:
    """Fallback extraction using Gemini 3.6 Flash if Unstructured fails or returns unparseable content."""
    try:
        from google import genai
        from google.genai import types
        print(f"[*] Calling Gemini 3.6 Flash fallback for {filepath.name}...")
        client = genai.Client(api_key=gemini_api_key)
        with open(filepath, "rb") as f:
            pdf_bytes = f.read()

        prompt = (
            "Extract all drug product names from this pharmacy invoice/catalog PDF.\n"
            "Preserve the correct Arabic drug names, dosage forms and strengths.\n"
            "Return JSON with a list of items:\n"
            "{\"items\": [{\"item_name_raw\": \"...\", \"source_page\": 1}]}"
        )
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        raw_items = data.get("items", [])
        items = []
        for it in raw_items:
            name = it.get("item_name_raw")
            if name:
                items.append({
                    "item_name_raw": str(name).strip(),
                    "source_page": it.get("source_page", 1),
                    "source_file": filepath.name
                })
        print(f"[+] Gemini fallback successfully extracted {len(items)} items from {filepath.name}")
        return items
    except Exception as gemini_err:
        print(f"[!] Gemini fallback failed for {filepath.name}: {gemini_err}")
        return []

def parse_structured_result(result_data: dict, filename: str) -> list[dict]:
    """
    Parse structured items from extraction response.
    Supports:
    1. Direct extracted_data / job.result.extracted_data (JSON schema output)
    2. Markdown HTML tables in result_data["markdown"] (Fallback table output)
    """
    import re
    items = []

    # Handle direct list of items or strings
    if isinstance(result_data, list):
        for item in result_data:
            if isinstance(item, dict):
                name = item.get("item_name_raw") or item.get("name") or item.get("اسم الصنف")
                if name:
                    items.append({
                        "item_name_raw": str(name).strip(),
                        "source_page": item.get("source_page", 1),
                        "source_file": filename
                    })
            elif isinstance(item, str) and item.strip():
                items.append({
                    "item_name_raw": item.strip(),
                    "source_page": 1,
                    "source_file": filename
                })
        return items

    if not isinstance(result_data, dict):
        return items

    # If wrapped in job result (e.g. from client.jobs.get)
    if "result" in result_data and isinstance(result_data["result"], dict):
        result_data = result_data["result"]

    # 1. Try direct top-level "items" list
    if "items" in result_data and isinstance(result_data["items"], list):
        for item in result_data["items"]:
            if isinstance(item, dict):
                name = item.get("item_name_raw") or item.get("name") or item.get("اسم الصنف")
                if name:
                    items.append({
                        "item_name_raw": str(name).strip(),
                        "source_page": item.get("source_page", 1),
                        "source_file": filename
                    })
            elif isinstance(item, str) and item.strip():
                items.append({
                    "item_name_raw": item.strip(),
                    "source_page": 1,
                    "source_file": filename
                })
        if items:
            return items

    # 2. Try extracted_data (Unstructured schema output)
    extracted_data = result_data.get("extracted_data", [])
    if isinstance(extracted_data, list) and len(extracted_data) > 0:
        for block in extracted_data:
            data = block.get("data", {}) if isinstance(block, dict) else getattr(block, "data", {})
            if isinstance(data, dict) and "items" in data:
                for item in data.get("items", []):
                    if not isinstance(item, dict):
                        continue
                    name = item.get("item_name_raw") or item.get("name") or item.get("اسم الصنف")
                    if name:
                        items.append({
                            "item_name_raw": str(name).strip(),
                            "source_page": item.get("source_page", 1),
                            "source_file": filename
                        })
        if items:
            return items

    # 2. Try markdown HTML tables if no items extracted yet
    if not items and "markdown" in result_data and result_data["markdown"]:
        md = str(result_data["markdown"])
        rows = re.findall(r"<tr>(.*?)</tr>", md, re.DOTALL | re.IGNORECASE)
        if rows:
            name_col_idx = 1
            header_cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", rows[0], re.DOTALL | re.IGNORECASE)]
            for idx, col in enumerate(header_cells):
                col_lower = col.lower()
                if any(k in col_lower for k in ["اسم الصنف", "اسم الدواء", "item name", "product name", "description", "اسم"]):
                    if not any(nk in col_lower for nk in ["رقم", "كود", "code", "id", "number"]):
                        name_col_idx = idx
                        break

            for r in rows[1:]:
                cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", r, re.DOTALL | re.IGNORECASE)]
                if len(cells) > name_col_idx:
                    val = cells[name_col_idx]
                    if val and not val.isdigit() and len(val) >= 2 and val not in header_cells:
                        items.append({
                            "item_name_raw": val,
                            "source_page": None,
                            "source_file": filename
                        })

    return items
