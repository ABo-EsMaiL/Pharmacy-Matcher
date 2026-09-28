"""
Gemini Vision Extraction Engine.
Extracts pharmaceutical items from PDF files page-by-page using Google AI Studio Vision Gateway.
Features:
- WebP high-resolution compressed rendering (pypdfium2 at scale 2.5)
- Content-addressed global cache (manifest.json, pages/, results/)
- Full resume & interruption capability (resumes from incomplete page)
- SHA-256 fingerprinting for instant cache reloads
"""

import base64
import hashlib
import json
import re
import time
import os
from contextlib import contextmanager, closing
from datetime import datetime
from pathlib import Path
import threading
import pypdfium2 as pdfium
import requests
from ..config import gateway_api_key

_GATEWAY_MUTEX = threading.Lock()
VISION_CACHE_ROOT = Path(__file__).resolve().parents[2] / 'data' / 'cache' / 'vision'
PROCESS_ROOT = Path(__file__).resolve().parents[2] / 'data' / 'processes'
_CACHE_LOCKS = {}
_CACHE_LOCKS_GUARD = threading.Lock()


def _compute_file_hash(filepath: Path) -> str:
    """Computes SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _get_cache_dir(filepath: Path, file_hash: str | None = None) -> Path:
    """Filename, source directory and process number are metadata only."""
    cache_dir = VISION_CACHE_ROOT / (file_hash or _compute_file_hash(filepath))
    (cache_dir / "pages").mkdir(parents=True, exist_ok=True)
    (cache_dir / "results").mkdir(parents=True, exist_ok=True)
    return cache_dir


@contextmanager
def _cache_lock(cache_dir: Path):
    """Serialize identical content across threads and app processes.

    OS locks are released on process exit; no stale lock-file deletion needed.
    """
    with _CACHE_LOCKS_GUARD:
        local_lock = _CACHE_LOCKS.setdefault(str(cache_dir), threading.Lock())
    with local_lock, open(cache_dir / '.lock', 'a+b') as handle:
        if os.name == 'nt':
            import msvcrt
            if handle.seek(0, 2) == 0:
                handle.write(b'0')
                handle.flush()
            while True:
                handle.seek(0)
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(.1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


def _save_json(path: Path, data: dict):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def _cached_page(path: Path, page: int):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data.get('page') == page and isinstance(data.get('items'), list) and data['items']
                and all(isinstance(it, dict) and isinstance(it.get('item_name_raw'), str)
                        and it['item_name_raw'].strip() for it in data['items'])):
            return data
    except (OSError, ValueError, AttributeError):
        pass
    return None


def _import_legacy_pages(filepath, cache_dir, file_hash, total_pages):
    """Reuse historical process caches by full manifest hash, without editing them."""
    manifests = list(PROCESS_ROOT.glob('*/cache/vision/*/manifest.json'))
    manifests += list((filepath.parent / '.vision_cache').glob('*/manifest.json'))
    for path in manifests:
        try:
            manifest = json.loads(path.read_text(encoding='utf-8'))
            if manifest.get('file_hash') != file_hash or manifest.get('total_pages') != total_pages:
                continue
        except (OSError, ValueError, AttributeError):
            continue
        for page in range(1, total_pages + 1):
            dest = cache_dir / 'results' / f'page_{page}.json'
            if _cached_page(dest, page) is None:
                data = _cached_page(path.parent / 'results' / dest.name, page)
                if data is not None:
                    _save_json(dest, data)


def _clean_json_response(raw_text: str) -> dict:
    """Cleans markdown fences or surrounding noise to extract valid JSON."""
    text = raw_text.strip()
    if not text:
        raise ValueError("Empty response text received from model.")
    if text.startswith("[Error:"):
        raise RuntimeError(f"Gateway reported error: {text}")

    # Strip markdown codeblocks
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()

    # Find enclosing json object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]

    return json.loads(text)


def extract_items_from_pdf_vision(
    filepath: Path,
    api_url: str = "http://127.0.0.1:8001/v1/chat/completions",
    api_key: str = gateway_api_key(),
    model: str = "gemini-3.8-flash",
    scale: float = 2.5,
    quality: int = 85,
    max_retries: int = 10,
) -> list[dict]:
    """
    Extracts all drug items from a PDF using page-by-page Gemini Vision.
    Supports page-level resumption and global content-addressed caching.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    print(f"\n{'='*60}")
    print(f"[*] [VISION EXTRACTOR] File: {filepath.name}")
    print(f"{'='*60}")

    file_hash = _compute_file_hash(filepath)
    cache_dir = _get_cache_dir(filepath, file_hash)
    with _cache_lock(cache_dir), closing(pdfium.PdfDocument(filepath)) as pdf:
        return _extract_pdf_pages(filepath, pdf, cache_dir, file_hash, api_url, api_key,
                                  model, scale, quality, max_retries)


def _extract_pdf_pages(filepath, pdf, cache_dir, file_hash, api_url, api_key,
                       model, scale, quality, max_retries):
    manifest_path = cache_dir / "manifest.json"

    # Read PDF metadata
    total_pages = len(pdf)
    print(f"  -> Total pages: {total_pages}")
    print(f"  -> Cache location: {cache_dir}")

    # Load or initialize manifest
    manifest = {
        "file_name": filepath.name,
        "file_hash": file_hash,
        "total_pages": total_pages,
        "completed_pages": [],
        "status": "in_progress",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                loaded_manifest = json.load(f)
            if loaded_manifest.get("file_hash") == file_hash and loaded_manifest.get("total_pages") == total_pages:
                manifest = loaded_manifest
                print(f"  -> Found existing cache manifest (Completed pages: {len(manifest.get('completed_pages', []))}/{total_pages})")
        except Exception as e:
            print(f"  [!] Could not parse manifest, re-initializing: {e}")

    # Check if completely finished
    if any(_cached_page(cache_dir / 'results' / f'page_{p}.json', p) is None
           for p in range(1, total_pages + 1)):
        _import_legacy_pages(filepath, cache_dir, file_hash, total_pages)
    # Recover successful atomic page writes even if interrupted before the
    # manifest update; invalid pages alone must be extracted again.
    completed_set = {p for p in range(1, total_pages + 1)
                     if _cached_page(cache_dir / 'results' / f'page_{p}.json', p) is not None}
    all_pages_cached = len(completed_set) == total_pages
    manifest.update(file_name=filepath.name, completed_pages=sorted(completed_set),
                    status='completed' if all_pages_cached else 'in_progress',
                    updated_at=datetime.now().isoformat())
    manifest['file_names'] = sorted(set(manifest.get('file_names', [])) | {filepath.name})
    _save_json(manifest_path, manifest)

    if all_pages_cached:
        print(f"[+] All {total_pages} pages previously extracted in cache. Loading instantly...")
        all_items = []
        for p in range(1, total_pages + 1):
            res_file = cache_dir / "results" / f"page_{p}.json"
            with open(res_file, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                items = p_data.get("items", [])
                for it in items:
                    it["source_file"] = filepath.name
                    it["source_page"] = p
                all_items.extend(items)
        print(f"[+] Loaded {len(all_items)} items from cache in 0.05s.")
        return all_items

    # Process pending pages
    print(f"[*] Starting/Resuming Vision extraction across {total_pages} page(s)...")

    for page_num in range(1, total_pages + 1):
        page_res_path = cache_dir / "results" / f"page_{page_num}.json"
        page_img_path = cache_dir / "pages" / f"page_{page_num}.webp"

        # Check if this page is already completed
        if page_num in completed_set and page_res_path.exists():
            print(f"  -> [Page {page_num}/{total_pages}] Already in cache, skipping extraction.")
            continue

        print(f"\n  -> [Page {page_num}/{total_pages}] Rendering & extracting...")

        # 1. Render page to WebP if image does not exist
        if not page_img_path.exists():
            with closing(pdf[page_num - 1]) as page_obj, closing(page_obj.render(scale=scale)) as bitmap:
                with closing(bitmap.to_pil()) as img:
                    image_tmp = page_img_path.with_suffix('.webp.tmp')
                    img.save(image_tmp, format="WEBP", quality=quality)
                    image_tmp.replace(page_img_path)
            print(f"     [+] Rendered WebP: {page_img_path.stat().st_size / 1024:.1f} KB")

        # 2. Read image as Base64
        with open(page_img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 3. Prompt setup
        prompt = (
            "أنت خبير صيدلي متخصص في استخراج وتحليل بيانات فواتير وقوائم الأدوية.\n"
            "قم باستخراج جميع الأدوية والمنتجات الطبية الموجودة في هذه الصورة بدقة صيدلانية كاملة.\n"
            "القواعد الصارمة:\n"
            "1. استخرج كل صنف أو سطر منتج دوائي يظهر في الصورة كعنصر مستقل.\n"
            "2. (item_name_raw): انقل اسم الصنف كاملاً كما هو في الفاتورة بالحرف دون أي تعديل أو اختصار مع الاحتفاظ بالاسم والتركيز والهيئة الدوائية والشركة.\n"
            "3. (trade_name): الاسم التجاري الصافي للدواء فقط بدون التركيز أو الهيئة الدوائية (مثال: دوليبرين، كيتولاك، كونكور، اوجمنتين).\n"
            "4. (strength): تركيز الدواء كما هو مكتوب في الصورة (مثال: 1000 مجم، 500 mg، 1 جم، 20/40) أو اتركه فارغاً إذا لم يذكر.\n"
            "5. (form): الهيئة الدوائية (أقراص، كبسول، شراب، حقن، أمبول، نقط، كريم، مرهم، جل، بخاخ...) أو اتركها فارغة إذا لم تذكر.\n"
            "6. تجنب تصحيح الأخطاء الإملائية أو ترجمة الكلمات أو تغيير الأرقام. لا تُدرج أسعار أو كميات أو خصومات أو أرقام أكواد.\n"
            "7. الحروف باللغة العربية والإنجليزية السليمة فقط.\n"
            f"8. الرد يجب أن يكون كائن JSON صالح فقط بدون أي نصوص تمهيدية:\\n"
            "{\\n"
            '  "items": [\\n'
            "    {\\n"
            '      "item_name_raw": "الاسم المكتوب كاملاً بالتركيز والهيئة كما هو",\\n'
            '      "trade_name": "الاسم التجاري فقط",\\n'
            '      "strength": "التركيز",\\n'
            '      "form": "الهيئة",\\n'
            f'      "source_page": {page_num}\\n'
            "    }\\n"
            "  ]\\n"
            "}"
        )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/webp;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ],
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 4. Send request with retry loop
        success = False
        for attempt in range(1, max_retries + 1):
            t0 = time.time()
            try:
                print(f"     [*] Sending Vision request to gateway (Attempt {attempt}/{max_retries})...")
                with _GATEWAY_MUTEX:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=900)
                elapsed = time.time() - t0

                if resp.status_code == 200:
                    data = resp.json()
                    raw_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if raw_content.strip().startswith("[Error:"):
                        raise RuntimeError(f"Gateway returned error: {raw_content.strip()}")
                    parsed = _clean_json_response(raw_content)

                    items = parsed.get("items", [])
                    if not isinstance(items, list):
                        raise ValueError(f"Vision response missing 'items' array: {raw_content[:200]}")
                    if len(items) == 0:
                        raise ValueError(f"Extracted items empty from gateway response: {raw_content[:200]}")

                    # Verify page number
                    for item in items:
                        item["source_page"] = page_num
                        item["source_file"] = filepath.name

                    # Save to page result cache
                    page_data = {"page": page_num, "items": items}
                    if not all(isinstance(it.get('item_name_raw'), str) and it['item_name_raw'].strip() for it in items):
                        raise ValueError('Vision response has invalid item_name_raw')
                    _save_json(page_res_path, page_data)

                    # Update manifest
                    if page_num not in completed_set:
                        completed_set.add(page_num)
                    manifest["completed_pages"] = sorted(list(completed_set))
                    manifest["updated_at"] = datetime.now().isoformat()
                    _save_json(manifest_path, manifest)

                    print(f"     [+] [Page {page_num}] Succeeded in {elapsed:.1f}s -> {len(items)} items extracted.")
                    success = True
                    break
                elif resp.status_code == 429:
                    print(f"     [!] [Page {page_num}] Gateway busy (browser tab in use). Waiting 5s before attempt {attempt+1}/{max_retries}...")
                    time.sleep(5.0)
                    continue
                else:
                    print(f"     [!] [Page {page_num}] HTTP Error {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"     [!] [Page {page_num}] Exception on attempt {attempt}: {e}")

            time.sleep(2.0)

        if not success:
            raise RuntimeError(f"Failed to extract page {page_num} of {filepath.name} after {max_retries} attempts.")

    # All pages finished!
    manifest["status"] = "completed"
    manifest["updated_at"] = datetime.now().isoformat()
    _save_json(manifest_path, manifest)

    # Collect and return all items
    all_items = []
    for p in range(1, total_pages + 1):
        res_file = cache_dir / "results" / f"page_{p}.json"
        if res_file.exists():
            with open(res_file, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                for item in p_data.get('items', []):
                    item['source_file'] = filepath.name
                    item['source_page'] = p
                all_items.extend(p_data.get("items", []))

    print(f"\n[+] [VISION EXTRACTOR] Successfully completed all {total_pages} pages for {filepath.name}!")
    print(f"[+] Total items extracted: {len(all_items)}")
    return all_items
