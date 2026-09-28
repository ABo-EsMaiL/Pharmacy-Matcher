"""Independent, read-only PROC-020 recall audit. Never creates a PROC or edits runtime code."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCE = ROOT / 'data/processes/PROC-020'
OUT = ROOT / 'data/audits/PROC-020-no-match-recall'


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def fingerprints():
    paths = [*SOURCE.rglob('*'), *(ROOT / 'src').rglob('*.py'), ROOT / 'SYSTEM_ARCHITECTURE_GRAPH.md']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file() and '__pycache__' not in str(p)}


def views(raw, trade=''):
    from src.match.text_match import normalize_text
    from src.fast_match.search import extract_brand_tokens, PHARMA_STOPWORDS
    from rapidfuzz.distance import Levenshtein
    normalized = normalize_text(raw).lower()
    # Independent removal of numeric fields for *ranking only*. Original text
    # remains authoritative; no strength/variant conclusions use these views.
    words = re.sub(r'[\d\W_]+', ' ', normalized).split()
    stop = {normalize_text(w).lower() for w in PHARMA_STOPWORDS}
    clean = [w for w in words if w not in stop]
    metadata = ['جديد', 'قديم', 'كبير', 'صغير', 'وسط', 'سعر', 'شريط', 'اقراص', 'شامبو', 'اسبراي']
    relaxed = [w for i, w in enumerate(clean) if i == 0 or not any(
        len(w) >= 4 and Levenshtein.distance(w, m) <= 1 for m in metadata)]
    values = [extract_brand_tokens(raw), ' '.join(clean), ' '.join(relaxed)]
    if trade:
        values.append(normalize_text(trade).lower())
    # The prefix before explicit dosage/form metadata is an additional name
    # hypothesis, never a business identity or an automatic acceptance.
    prefix = re.split(r'\d|\b(?:' + '|'.join(re.escape(w) for w in stop if len(w) >= 3) + r')\b', normalized, maxsplit=1)[0]
    if len(re.sub(r'\W', '', prefix)) >= 3:
        values.append(prefix)
    return list(dict.fromkeys(' '.join(re.findall(r'[^\W\d_]+', v)) for v in values if any(c.isalpha() for c in v)))


def compact(text):
    return re.sub(r'\W', '', text)


def skeleton(text):
    for group in ('بتث', 'جحخ', 'دذ', 'رز', 'سش', 'صض', 'طظ', 'عغ', 'فق'):
        text = text.translate(str.maketrans({c: group[0] for c in group}))
    return text


def prepare():
    import numpy as np
    from rapidfuzz import process, fuzz
    from rapidfuzz.distance import Levenshtein
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from src.fast_match.coordinator import classify_pair
    if (OUT / 'plan.json').exists():
        raise RuntimeError('Audit plan already exists; use run/report to resume it')
    OUT.mkdir(parents=True, exist_ok=True)
    save(OUT / 'source_fingerprints.json', fingerprints())
    original = json.loads((SOURCE / 'results.json').read_text(encoding='utf-8'))
    catalog, pages = [], []
    for manifest in sorted((SOURCE / 'cache/vision').glob('*/manifest.json')):
        info = json.loads(manifest.read_text(encoding='utf-8'))
        files = sorted((manifest.parent / 'results').glob('page_*.json'), key=lambda p: int(p.stem.split('_')[-1]))
        assert len(files) == info['total_pages']
        assert set(info['completed_pages']) == set(range(1, info['total_pages'] + 1))
        for f in files:
            page = json.loads(f.read_text(encoding='utf-8'))
            pages.append({'warehouse': info['file_name'], 'page': page['page'], 'items': len(page['items']), 'cache': str(f.relative_to(ROOT))})
            for row in page['items']:
                catalog.append({'id': f"I{len(catalog):04}", 'name': row['item_name_raw'],
                                'warehouse': info['file_name'], 'page': page['page'],
                                'cache': str(f.relative_to(ROOT)), 'trade_name': row.get('trade_name', '')})
    assert len(pages) == 46 and len(catalog) == 2718
    shortages = [n['name'] for n in original['not_found']]
    assert len(shortages) == len(set(shortages)) == 461
    # User-provided supplemental positive controls are audit fixtures, not rules.
    supplemental = ['امبوفير 5امبول س ج', 'افيروكوكسيب90مجم20قرص س ج']
    all_queries = shortages + supplemental
    owner, flat = [], []
    for i, item in enumerate(catalog):
        for v in views(item['name'], item['trade_name']):
            flat.append(v); owner.append(i)
    owners = np.asarray(owner)
    flat_compact = [compact(v) for v in flat]
    flat_skeleton = [skeleton(v) for v in flat_compact]
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(flat)
    cases = []
    for qi, query in enumerate(all_queries):
        qv = views(query)
        qc = [compact(v) for v in qv]
        methods_flat = {
            'char_ngrams': cosine_similarity(vectorizer.transform(qv), matrix).max(axis=0),
            'normalized_edit': process.cdist(qc, flat_compact, scorer=Levenshtein.normalized_similarity).max(axis=0),
            'character_alignment': process.cdist(qc, flat_compact, scorer=fuzz.ratio).max(axis=0) / 100,
            'ocr_dot_shape': process.cdist([skeleton(v) for v in qc], flat_skeleton, scorer=Levenshtein.normalized_similarity).max(axis=0),
            'token_coverage': process.cdist(qv, flat, scorer=fuzz.token_set_ratio).max(axis=0) / 100,
        }
        methods = {}
        for key, scores in methods_flat.items():
            aggregate = np.zeros(len(catalog)); np.maximum.at(aggregate, owners, scores)
            methods[key] = aggregate
        chosen, evidence = set(), {}
        def retain(i, method, rank):
            chosen.add(int(i)); evidence.setdefault(int(i), []).append({'method': method, 'rank': rank})
        # No production gate, no minimum similarity cutoff. Rank unions keep
        # alternatives; exact and one-edit full-name evidence are never capped.
        for key, scores in methods.items():
            seen_names = set(); rank = 0
            for i in np.argsort(-scores, kind='stable'):
                name = catalog[int(i)]['name']
                if name in seen_names:
                    continue
                seen_names.add(name); rank += 1
                if rank <= 6:
                    retain(i, key, rank)
                else:
                    break
        full_distance = process.cdist(qc, flat_compact, scorer=Levenshtein.distance).min(axis=0)
        for view_id in np.where(full_distance <= 1)[0]:
            if min(len(flat_compact[view_id]), max(map(len, qc))) >= 4:
                retain(owners[view_id], 'full_name_exact_or_single_edit', 0)
        ensemble = sum(methods.values()) / len(methods)
        for warehouse in sorted({i['warehouse'] for i in catalog}):
            ids = [i for i, item in enumerate(catalog) if item['warehouse'] == warehouse]
            for rank, i in enumerate(sorted(ids, key=lambda i: ensemble[i], reverse=True)[:2], 1):
                retain(i, 'warehouse_best', rank)
        ordered = sorted(chosen, key=lambda i: ensemble[i], reverse=True)
        candidates = [{**catalog[i], 'scores': {k: round(float(v[i]), 4) for k, v in methods.items()},
                       'retrieval_methods': evidence[i], 'current_classifier': classify_pair(query, catalog[i]['name'])}
                      for i in ordered]
        cases.append({'case_id': f'A{qi:04}', 'requested_name': query,
                      'scope': 'global_no_match' if qi < len(shortages) else 'supplemental_warehouse_control',
                      'candidates': candidates})
        if qi % 50 == 0:
            print(f'Prepared {qi+1}/{len(all_queries)}', flush=True)
    plan = {'source': 'PROC-020', 'created_at': datetime.now(timezone.utc).isoformat(),
            'total_no_match': len(shortages), 'page_count': len(pages), 'catalog_count': len(catalog),
            'all_pair_comparisons': len(shortages) * len(catalog), 'pages': pages,
            'method': 'Five independent rank unions, all exact/one-edit names, two nearest per warehouse; no production threshold',
            'cases': cases}
    save(OUT / 'plan.json', plan)
    save(OUT / 'catalog.json', catalog)
    print(json.dumps({'no_match': len(shortages), 'pages': len(pages), 'catalog': len(catalog),
                      'audit_cases': len(cases), 'candidate_pairs': sum(len(c['candidates']) for c in cases),
                      'max_candidates_per_case': max(len(c['candidates']) for c in cases)}, ensure_ascii=False))


AUDIT_PROMPT = '''You audit item-presence recall in pharmaceutical warehouse text extracted by OCR.
This is an independent audit, not a production matching run. Candidate lists are
the union of several broad retrieval methods; many candidates are unrelated.
For EACH request, examine ALL its supplied candidates. Determine which have a
plausible full-product name relationship (ignoring dosage differences at this
first step). Return their IDs as plausible_ids. A small shared prefix/suffix or
an active ingredient/medical alternative is not evidence of the same product.
Consider OCR dropped/extra letters, Arabic/Persian glyphs, Unicode, joined/split
words, repeated letters, and corrupt packaging/form/commercial descriptions.
Do not require an alias registry or outside brand verification. Use only the
given raw text; do not infer medical alternatives or invent missing strengths.

Apply this unchanged decision graph to plausible candidates:
- Same item and compatible relevant information -> match.
- Explicit conflicting strength/concentration on a comparable basis -> no_match.
- Same item, compatible strength, clearly different dosage form -> review.
- Tablets/capsules compatible; injection/ampoule compatible.
- Pack count, strips/ampoules/boxes, package-only volume, size, price markers and
  old/new price descriptions do not prevent match.
- A missing warehouse strength/form is NOT an explicit conflict, and must not
  cause automatic rejection. Judge same-item evidence without inventing values.
- Different commercial identity, explicit Co/Plus or meaningful variant conflict
  -> no_match. OCR spelling differences alone do not prove a different identity.
- Never return review simply for uncertainty. Review needs a real form difference.

Audit priority is discovering missed real matches/reviews, not forcing matches.
Choose match if any candidate is a supported match; otherwise choose review if
one supports review; otherwise no_match. Do not select a different brand as an
alternative. Missing information that truly prevents judgment is unresolved.
For no_match, distinguish no_name_evidence, explicit_strength_conflict,
different_product, combination_or_variant_conflict, or insufficient_information.

Return COMPACT JSON only, using arrays to avoid truncated long responses:
{"results":[["case_id","match|review|no_match","item_id or empty",
["plausible_id", "..."],"no_match_basis or empty","Arabic reason, MAXIMUM 8 words"]]}.
Each row has exactly six values in that order. Do not repeat field names per row.
Return exactly one result per case_id. IDs must belong to that case. Include ALL
plausible IDs, even if strength conflicts or another warehouse matches better.
Original names must not be rewritten in your reasoning to hide conflicts.
'''


def call_batch(cases, config, batch_index):
    import requests
    payload = {'cases': [{'case_id': c['case_id'], 'requested_name': c['requested_name'],
                          'candidates': [{'id': x['id'], 'name': x['name']} for x in c['candidates']]}
                         for c in cases]}
    prior_attempts = [int(p.stem.rsplit('_', 1)[1]) for p in OUT.glob(f'batch_{batch_index:02}_attempt_*.json')]
    first_attempt = max(prior_attempts, default=0) + 1
    for attempt in range(first_attempt, first_attempt + 3):
        started = time.time()
        response = requests.post(config.local_api_url,
            headers={'Authorization': 'Bearer ' + config.local_api_key,
                     'X-Batch-Size': str(len(cases)), 'X-Google-Search-Enabled': 'false'},
            json={'model': config.local_model, 'stream': False,
                  'messages': [{'role': 'system', 'content': AUDIT_PROMPT},
                               {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]},
            timeout=(30, 1500))
        record = {'batch': batch_index, 'attempt': attempt, 'elapsed': time.time() - started,
                  'response_contract': 'compact_array_v1',
                  'audit_prompt_sha256': hashlib.sha256(AUDIT_PROMPT.encode()).hexdigest(),
                  'case_ids': [c['case_id'] for c in cases], 'status_code': response.status_code,
                  'headers': {k: v for k, v in response.headers.items() if k.lower().startswith('x-')},
                  'body': response.text}
        save(OUT / f'batch_{batch_index:02}_attempt_{attempt}.json', record)
        response.raise_for_status()
        try:
            content = response.json()['choices'][0]['message']['content'].strip()
            content = re.sub(r'^```(?:json)?\s*|\s*```$', '', content)
            result = json.loads(content)['results']
            if result and isinstance(result[0], list):
                assert all(len(row) == 6 for row in result)
                fields = ('case_id', 'status', 'item_id', 'plausible_ids', 'no_match_basis', 'reason')
                result = [dict(zip(fields, row)) for row in result]
            assert len(result) == len(cases)
            by_id = {r['case_id']: r for r in result}
            assert set(by_id) == {c['case_id'] for c in cases}
            for c in cases:
                r = by_id[c['case_id']]; ids = {x['id'] for x in c['candidates']}
                assert r['status'] in {'match', 'review', 'no_match'}
                assert isinstance(r['plausible_ids'], list) and set(r['plausible_ids']) <= ids
                assert (r['item_id'] == '' if r['status'] == 'no_match' else r['item_id'] in ids)
                if r['status'] != 'no_match':
                    assert r['item_id'] in r['plausible_ids']
                else:
                    assert r['no_match_basis'] in {'no_name_evidence', 'explicit_strength_conflict', 'different_product', 'combination_or_variant_conflict', 'insufficient_information'}
            return [by_id[c['case_id']] for c in cases]
        except (AssertionError, KeyError, ValueError) as error:
            print(f'Batch {batch_index} invalid response attempt {attempt}: {error}', flush=True)
            if attempt == first_attempt + 2:
                raise
    raise RuntimeError('No valid response')


def run():
    import requests
    from src.config import load_config
    config = load_config()
    settings = json.loads((ROOT / 'data/settings.json').read_text(encoding='utf-8'))
    for key in ('local_api_url', 'local_api_key', 'local_model'):
        if settings.get(key):
            setattr(config, key, settings[key])
    assert config.local_model == 'gemini-3.8-flash' and ':8001/' in config.local_api_url
    health = requests.get('http://127.0.0.1:8001/health', timeout=10).json()
    assert health['browser_ready'] and health['model_verified'] and health['thinking_verified']
    assert health['active_thinking'].lower() == 'high' and health['search_verified']
    assert health['google_search_enabled'] is False and health['clear_chat_on_request'] is True
    save(OUT / 'gateway_preflight.json', health)
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    assert fingerprints() == json.loads((OUT / 'source_fingerprints.json').read_text(encoding='utf-8'))
    cases = plan['cases']
    for start in range(0, len(cases), 75):
        batch_id = start // 75 + 1
        destination = OUT / f'decisions_{batch_id:02}.json'
        if destination.exists():
            print(f'Batch {batch_id}: retained prior completed audit decision', flush=True)
            continue
        print(f'AUDIT batch {batch_id}: {len(cases[start:start+75])} cases, '
              f"{sum(len(c['candidates']) for c in cases[start:start+75])} candidates", flush=True)
        result = call_batch(cases[start:start+75], config, batch_id)
        save(destination, result)
        print(f'AUDIT batch {batch_id} complete: {dict(Counter(r["status"] for r in result))}', flush=True)
    assert fingerprints() == json.loads((OUT / 'source_fingerprints.json').read_text(encoding='utf-8'))
    print('AUDIT complete; source/runtime unchanged; no PROC created', flush=True)


def prepare_amr():
    """Reverse search all 19 warehouse rows against all 591 original requests."""
    import contextlib
    import io
    import numpy as np
    from rapidfuzz import process, fuzz
    from rapidfuzz.distance import Levenshtein
    from src.extract.file_handler import read_input_files
    from src.fast_match.coordinator import classify_pair
    with contextlib.redirect_stdout(io.StringIO()):
        inputs = read_input_files(sorted((SOURCE / 'input_shortages').iterdir()), role='shortages')
    shortages = list(dict.fromkeys(r['item_name_raw'] for rows in inputs.values() for r in rows))
    catalog = json.loads((OUT / 'catalog.json').read_text(encoding='utf-8'))
    amr = [c for c in catalog if c['warehouse'] == 'جملة العمروووو.pdf']
    assert len(amr) == 19 and len(shortages) == 591
    qviews, owners = [], []
    for i, query in enumerate(shortages):
        for view in views(query):
            qviews.append(view); owners.append(i)
    selected, inventory = set(), []
    for item in amr:
        iv = views(item['name'], item['trade_name'])
        edit = process.cdist([compact(v) for v in iv], [compact(v) for v in qviews], scorer=Levenshtein.normalized_similarity).max(axis=0)
        token = process.cdist(iv, qviews, scorer=fuzz.token_set_ratio).max(axis=0) / 100
        score = np.zeros(len(shortages)); np.maximum.at(score, np.asarray(owners), .7 * edit + .3 * token)
        nearest = [int(i) for i in np.argsort(-score, kind='stable')[:3]]
        selected.update(nearest)
        inventory.append({**item, 'nearest_requests': [{'requested': shortages[i], 'score': round(float(score[i]), 4),
                                                        'current_classifier': classify_pair(shortages[i], item['name'])}
                                                       for i in nearest]})
    cases = [{'case_id': f'W{i:04}', 'requested_name': shortages[i], 'scope': 'amr_only', 'candidates': amr}
             for i in sorted(selected)]
    save(OUT / 'amr_inventory.json', inventory)
    save(OUT / 'amr_plan.json', {'catalog_items': 19, 'all_requests': 591, 'comparisons': 19 * 591, 'cases': cases})
    print(json.dumps({'amr_catalog_items': 19, 'requests_scanned': 591, 'focused_cases': len(cases)}, ensure_ascii=False))


def run_amr():
    import requests
    from src.config import load_config
    config = load_config()
    settings = json.loads((ROOT / 'data/settings.json').read_text(encoding='utf-8'))
    for key in ('local_api_url', 'local_api_key', 'local_model'):
        if settings.get(key): setattr(config, key, settings[key])
    health = requests.get('http://127.0.0.1:8001/health', timeout=10).json()
    assert health['active_thinking'].lower() == 'high' and health['google_search_enabled'] is False and health['clear_chat_on_request']
    cases = json.loads((OUT / 'amr_plan.json').read_text(encoding='utf-8'))['cases']
    assert len(cases) <= 75
    path = OUT / 'decisions_amr.json'
    if path.exists(): raise RuntimeError('Preserve completed Amr decisions')
    print(f'Amr-only audit: {len(cases)} requests against all 19 warehouse items', flush=True)
    save(path, call_batch(cases, config, 8))
    print('Amr-only audit completed', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'prepare': prepare, 'run': run, 'prepare_amr': prepare_amr, 'run_amr': run_amr}[sys.argv[1]]()
