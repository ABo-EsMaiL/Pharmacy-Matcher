import json
import time
import re
import logging
import concurrent.futures
import requests as http_requests

logger = logging.getLogger("pharmacy.fast_match")

from ..config import Config
from ..config import gateway_api_key
from .search import (FastCandidateFinder, extract_form_group, extract_form_groups,
                     extract_brand_tokens, name_evidence, unified_item, item_payload, normalize_for_search)
from ..match.text_match import normalize_text
from .attributes import (norm_num, get_strength_pattern, compare_strengths,
                         compare_strength_values, structured_attribute_uncertainty)


SYSTEM_PROMPT = """You perform item presence matching using supplied structured items and raw text.
Decide whether a warehouse candidate represents the requested product identity.
Use trade_name first, then raw_name for OCR evidence. Strength, form and package
are separate attributes, not proof of product identity. Do not use external
medical knowledge, active ingredients, alternatives, aliases, databases or search.

DECISION GRAPH (presence semantics):
- No plausible same-product identity: no_match, identity_same=false.
- Same product with explicit strength/concentration conflict: review, NEVER match.
- Same product with different dosage form: review. Tablets/capsules compatible.
- Same product with combination/variant conflict: review, NEVER match.
- Missing strength/form is not a conflict and never proves product absence.
  Return match if available evidence supports compatibility; otherwise review.
- Pack/count/strips/boxes, package-only volume/mass, price do not prevent match.
- Raw/structured field disagreements or uncertain attributes: review unless the
  supplied data resolves them. Do not invent missing units or concentrations.
- OCR name uncertainty must use whole-name evidence, not a shared small fragment.

Return JSON only:
{"results":[{"case_id":"...","status":"match|review|no_match",
"item_id":"...","identity_same":true,"reason":"concise Arabic explanation"}]}
Return one result per case. For match/review select only an item_id from that
case. For no_match use an empty item_id and identity_same=false; this means all
candidates have different product identities, NOT incompatible attributes.
"""


def has_co(text: str) -> bool:
    t = re.sub(r'(?<=[^\W\d_])(?=\d)', ' ', normalize_text(text).lower())
    return bool(re.search(r'(?:^|[^\w])(كو|بلس|بلاس|كومب|co|plus|comp)(?:[^\w]|$)|كواقراص|كوأقراص|بلساقراص|بلسكبسول', t)
                or re.search(r'[\u0621-\u064a]{3,}(?:بلاس|بلس|كومب)(?=\W|\d|$)', t))

def are_forms_identical(form1: str | None, form2: str | None) -> bool:
    if not form1 or not form2:
        return True
    if form1 == form2:
        return True
    if (form1, form2) in {('tablet', 'capsule'), ('capsule', 'tablet')}:
        return True
    return False

def are_forms_compatible(form1: str | None, form2: str | None) -> bool:
    if not form1 and not form2:
        return True
    if form1 == form2:
        return True
    compat = {
        ('tablet', 'capsule'), ('capsule', 'tablet'),
        ('cream', 'ointment'), ('ointment', 'cream'),
        ('cream', 'gel'), ('gel', 'cream'),
        ('injection', 'ampoule'), ('ampoule', 'injection'),
    }
    if (form1, form2) in compat:
        return True
    if form1 and form2 and form1 != form2:
        return False
    return True

def classify_pair(req: str | dict, cand: str | dict, *, identity_confirmed=False) -> tuple[str, str]:
    """Existence first; incompatible or uncertain attributes never erase it."""
    req, cand = unified_item(req), unified_item(cand)
    evidence = name_evidence(req, cand)
    if not evidence.plausible:
        return "reject", "no_meaningful_name_evidence"
    clear_identity = evidence.exact or (evidence.edits == 0 and evidence.reason == 'full_name_evidence')
    if not clear_identity and not identity_confirmed:
        return "ambiguous", "ocr_or_incomplete_name"
    if req['attribute_warnings'] or cand['attribute_warnings']:
        return "review", "structured_raw_fields_uncertain"
    uncertainty = structured_attribute_uncertainty(req, cand)
    if uncertainty:
        return 'review', uncertainty
    variants_r = re.findall(r'\d+(?:\.\d+)?', normalize_for_search(req['trade_name'] or ''))
    variants_c = re.findall(r'\d+(?:\.\d+)?', normalize_for_search(cand['trade_name'] or ''))
    if variants_r and variants_c and variants_r != variants_c:
        known_variants = req['field_sources']['trade_name'] == cand['field_sources']['trade_name'] == 'structured'
        return "review", "product_variant_conflict" if known_variants else "numeric_identity_uncertain"
    if has_co(req['raw_name'] + ' ' + (req['trade_name'] or '')) != has_co(cand['raw_name'] + ' ' + (cand['trade_name'] or '')):
        return "review", "combination_mismatch"
    strength_relation = compare_strength_values(req['_strength_values'], cand['_strength_values'])
    if strength_relation == 'conflict':
        return "review", "explicit_strength_conflict"
    forms_r, forms_c = req['_forms'], cand['_forms']
    if len(forms_r) > 1 or len(forms_c) > 1:
        return "ambiguous", "uncertain_form"
    if forms_r and forms_c and not are_forms_identical(forms_r[0], forms_c[0]):
        return "review", f"different_form_{forms_r[0]}_vs_{forms_c[0]}"
    if strength_relation == 'incomparable':
        return "ambiguous", "strength_measurement_basis_uncertain"
    if bool(variants_r) != bool(variants_c):
        return "ambiguous", "missing_product_variant"
    if bool(req['_strength_values']) != bool(cand['_strength_values']):
        return "ambiguous", "missing_strength"
    if bool(forms_r) != bool(forms_c):
        return "ambiguous", "missing_form"
    return "match", "same_item_compatible_fields"


def is_safe_auto_match(req: str | dict, cand: str | dict) -> tuple[bool, str]:
    status, reason = classify_pair(req, cand)
    return (status == "match", reason)


def validate_llm_decision(case: dict, decision: dict) -> dict:
    """Python owns candidate membership and attribute conflicts after identity."""
    if decision.get('case_id') != case['case_id']:
        raise ValueError('PROVIDER_RESPONSE_INVALID: case_id mismatch')
    status = decision.get('status')
    if status not in {'match', 'review', 'no_match'}:
        raise ValueError('PROVIDER_RESPONSE_INVALID: invalid status')
    if 'identity_same' in decision and not isinstance(decision['identity_same'], bool):
        raise ValueError('PROVIDER_RESPONSE_INVALID: identity_same must be boolean')
    if status != 'no_match' and decision.get('identity_same') is False:
        raise ValueError('PROVIDER_RESPONSE_INVALID: positive status with rejected identity')
    req = unified_item(case.get('requested_item', case['requested_name']))
    candidates = {c['id']: unified_item(c) for c in case['candidates']}
    item_id = decision.get('item_id', '')
    if status == 'no_match' and item_id == '':
        # An LLM cannot call an established trade name absent on account of
        # strength/form/missing data. OCR identity rejections must be explicit.
        for candidate in candidates.values():
            evidence = name_evidence(req, candidate)
            clear_identity = evidence.exact or (evidence.edits == 0 and evidence.reason == 'full_name_evidence')
            if evidence.plausible and (clear_identity or decision.get('identity_same') is not False):
                route, why = classify_pair(req, candidate)
                return {'status': 'match' if route == 'match' else 'review',
                        'warehouse_item': candidate['raw_name'], 'reason': why}
        return {'status': 'no_match', 'warehouse_item': '', 'reason': decision.get('reason', '')}
    if not isinstance(item_id, str) or item_id not in candidates:
        raise ValueError('PROVIDER_RESPONSE_INVALID: item_id outside case candidates')
    candidate = candidates[item_id]
    route, reason = classify_pair(req, candidate, identity_confirmed=True)
    if route == 'reject':
        status = 'no_match'
    elif route == 'review':
        status = 'review'
    elif status == 'no_match':
        status = 'review'
    elif route == 'match':
        status = 'match'
    else:
        if reason == 'strength_measurement_basis_uncertain':
            status = 'review'
        reason = decision.get('reason', '') or reason
    return {'status': status, 'warehouse_item': candidate['raw_name'], 'reason': reason}


class FastCoordinator:
    def __init__(self, config: Config):
        self.config = config

    def process(self, shortage_items: list[dict], warehouse_data: dict[str, list[dict]]) -> dict:
        unique_shortages = {}
        for raw_item in shortage_items:
            item = unified_item(raw_item)
            name = item["raw_name"]
            if name and name not in unique_shortages:
                unique_shortages[name] = item
                
        deduped_shortages = list(unique_shortages.values())

        print(f"\n{'='*60}")
        print(f"[FAST ENGINE] Starting Match: {len(shortage_items)} raw -> {len(deduped_shortages)} UNIQUE shortages x {len(warehouse_data)} warehouses")
        print(f"{'='*60}\n")

        all_warehouse_results = {}
        found_in = {}

        for wh_name, wh_items in warehouse_data.items():
            print(f"\n{'-'*40}")
            print(f"[Warehouse] {wh_name} ({len(wh_items)} items)")
            print(f"{'-'*40}")

            wh_result = self._match_warehouse(deduped_shortages, wh_items, wh_name)
            all_warehouse_results[wh_name] = wh_result

            for match in wh_result["matched"]:
                name = match["shortage_item"]
                found_in.setdefault(name, []).append(wh_name)

        all_shortage_names = {item["item_name_raw"] for item in deduped_shortages}
        found_names = set(found_in.keys())
        
        # Deduplicated needs_review calculation to match the Excel sheet 'يحتاج مراجعة':
        # 1. Skip items that are already confirmed/matched in another warehouse (don't burden pharmacist)
        # 2. Deduplicate identical (shortage_item, warehouse_item, warehouse_name) triplets
        actual_review_items = []
        seen_review_pairs = set()
        for wh_name, wh_result in all_warehouse_results.items():
            for rev in wh_result["needs_review"]:
                req_item = rev.get("shortage_item", "").strip()
                wh_item = rev.get("warehouse_item", "").strip()
                if req_item in found_names:
                    continue
                pair_key = (req_item, wh_item, wh_name)
                if pair_key in seen_review_pairs:
                    continue
                seen_review_pairs.add(pair_key)
                actual_review_items.append(rev)

        review_only_names = {rev["shortage_item"].strip() for rev in actual_review_items}
        not_found_names = all_shortage_names - found_names - review_only_names
        not_found_items = [
            {"name": name, "source": next(
                (item.get("source_file", "") for item in deduped_shortages
                 if item.get("item_name_raw") == name), ""
            )}
            for name in sorted(not_found_names)
        ]

        total_wh_matched = sum(len(wh["matched"]) for wh in all_warehouse_results.values())
        total_review_items = len(actual_review_items)
        total_not_found = len(not_found_items)
        summary = {
            "total_shortages": len(shortage_items),
            "unique_shortages": len(deduped_shortages),
            "matched_count": total_wh_matched,
            "not_found_count": total_not_found,
            "review_count": total_review_items,
        }

        return {
            "warehouse_results": all_warehouse_results,
            "not_found": not_found_items,
            "summary": summary,
        }

    def _match_warehouse(self, shortage_items: list[dict], warehouse_items: list[dict], warehouse_name: str) -> dict:
        matched = []
        needs_review = []
        
        # 1. Prepare fast search index
        print("  -> Indexing warehouse for Fast Search...")
        finder = FastCandidateFinder()
        wh_catalog = [unified_item({**item, "id": f"W-{i:05}",
                       "source_file": item.get("source_file") or warehouse_name})
                      for i, item in enumerate(warehouse_items)]
        finder.fit(wh_catalog)
        exact_count = 0
        auto_match_count = 0
        llm_cases = []
        candidates_by_shortage = {}

        for idx, raw_item in enumerate(shortage_items):
            item = unified_item(raw_item)
            shortage_name = item['raw_name']
            candidates = finder.search(item, top_k=6)
            routed = [(cand, *classify_pair(item, cand)) for cand in candidates]
            clear_matches = [c for c, status, _ in routed if status == 'match']
            if clear_matches:
                best = clear_matches[0]
                matched.append({'shortage_item': shortage_name, 'warehouse_item': best['name'],
                                'confidence': 'high', 'method': 'structured_auto_rule'})
                auto_match_count += 1
                continue
            reviews = [(c, reason) for c, status, reason in routed if status == 'review']
            ambiguous = [c for c, status, _ in routed if status == 'ambiguous']
            if ambiguous:
                llm_cases.append({'case_id': f'Q{idx:05}', 'requested_name': shortage_name,
                                  'requested_item': item,
                                  'candidates': ambiguous})
                candidates_by_shortage[shortage_name] = (item, reviews)
            elif reviews:
                best, reason = reviews[0]
                needs_review.append({'shortage_item': shortage_name, 'warehouse_item': best['name'],
                                     'reason': reason})

        print(f"  -> Exact Matches: {exact_count}")
        print(f"  -> Deterministic Auto-Matches: {auto_match_count}")
        
        # 3. Process via LLM in optimal chunks (100 items for ChatGPT, 75 for Google AI Studio)
        if llm_cases and not getattr(self.config, 'local_api_url', None):
            raise RuntimeError('Provider unavailable for ambiguous candidates')
        if llm_cases and hasattr(self.config, 'local_api_url'):
            url_str = str(getattr(self.config, 'local_api_url', ''))
            model_str = str(getattr(self.config, 'local_model', '')).lower()
            is_chatgpt = ('8000' in url_str or 'gpt' in model_str)
            
            if is_chatgpt:
                batch_size = 100
                # If total ambiguous items <= 125, group into 1 single message to strictly save ChatGPT prompt quota
                if len(llm_cases) <= 125:
                    batches = [llm_cases]
                else:
                    batches = [llm_cases[i:i + batch_size] for i in range(0, len(llm_cases), batch_size)]
            else:
                batch_size = 75
                batches = [llm_cases[i:i + batch_size] for i in range(0, len(llm_cases), batch_size)]

            provider_label = "ChatGPT" if is_chatgpt else "Google AI Studio"
            print(f"  -> Sending {len(llm_cases)} ambiguous items to Local API ({provider_label}) in {len(batches)} batch(es) (Max ~{batch_size} items/msg)...")
            
            def process_chunk(cases_chunk, chunk_name):
                max_retries = 5 if is_chatgpt else 3
                for attempt in range(max_retries):
                    try:
                        inter_wait = 5 if is_chatgpt else 2
                        time.sleep(inter_wait)
                        raw_results = self._call_local_api({"cases": cases_chunk})
                        parsed = []
                        matched_in_chunk = 0
                        review_in_chunk = 0
                        for case, decision in zip(cases_chunk, raw_results):
                            shortage_name = case["requested_name"]
                            validated = validate_llm_decision(case, decision)
                            status = validated['status']
                            warehouse_item = validated['warehouse_item']
                            reason = validated['reason']
                            if status == "match":
                                matched_in_chunk += 1
                            elif status == "review":
                                review_in_chunk += 1
                                
                            parsed.append({
                                "shortage_name": shortage_name,
                                "status": status,
                                "warehouse_item": warehouse_item,
                                "reason": reason
                            })
                        meta = getattr(self, "last_batch_meta", {})
                        search_flag = meta.get("search_enabled", "false")
                        tool_calls = meta.get("tool_calls", "0")
                        thinking_lvl = meta.get("thinking_level", "High")
                        gen_time = meta.get("gen_time", "N/A")
                        no_match_in_chunk = len(cases_chunk) - (matched_in_chunk + review_in_chunk)

                        print(f"      [✓] Batch {chunk_name} ({len(cases_chunk)} items) done in {gen_time}:")
                        print(f"          - Google Search: {search_flag.upper()} | Tool Calls: {tool_calls} | Thinking: {thinking_lvl}")
                        print(f"          - Results: {matched_in_chunk} matched, {review_in_chunk} review, {no_match_in_chunk} no_match.")
                        return parsed
                    except Exception as e:
                        last_error = e
                        err_str = str(e)
                        if "too_many_tool_calls" in err_str.lower():
                            print(f"      [!] CRITICAL: too_many_tool_calls error on batch {chunk_name}: {err_str}")
                        if "session might be expired" in err_str or "Session expired" in err_str:
                            print(f"      [!] خطأ في جلسة MSEMAX: انتهت صلاحية الجلسة على السيرفر.")
                            print(f"      [!] يرجى تشغيل python get_session.py في مجلد MSEMAX لتحديث الجلسة.")
                            raise RuntimeError(f"Session expired on Batch {chunk_name}: {e}")
                        if "413" in err_str and len(cases_chunk) > 20:
                            mid = len(cases_chunk) // 2
                            print(f"      [!] 413 Payload too large on batch {chunk_name}. Adaptively splitting into ({mid} + {len(cases_chunk)-mid})...")
                            return process_chunk(cases_chunk[:mid], f"{chunk_name}.1") + process_chunk(cases_chunk[mid:], f"{chunk_name}.2")
                        if "429" in err_str or "Rate Limited" in err_str or "RateLimit" in err_str:
                            wait_sec = 45 + (attempt * 25)
                            print(f"      [!] HTTP 429 Rate Limit on batch {chunk_name}. Waiting {wait_sec}s before retry ({attempt+1}/{max_retries})...")
                            time.sleep(wait_sec)
                        elif "NO_RESPONSE_STARTED" in err_str or "NETWORK_CONNECTION_FAILED" in err_str or "Connection to local LLM failed" in err_str or "STREAM_TRUNCATED" in err_str or "PROVIDER_RESPONSE_INCOMPLETE" in err_str or "HARD_CEILING_TIMEOUT" in err_str:
                            print(f"      [!] Batch {chunk_name} attempt {attempt+1}/{max_retries} encountered transient issue ({e}). Retrying with fresh turn...")
                            time.sleep(5)
                        else:
                            print(f"      [!] Batch {chunk_name} attempt {attempt+1}/{max_retries} error: {e}")
                            time.sleep(5)

                # Provider errors, including 429, are operational failures, not drug decisions.
                print(f"      [X] PROVIDER FAILURE on Batch {chunk_name} after {max_retries} attempts ({last_error}).")
                raise RuntimeError(f"Provider failed on Batch {chunk_name}: {last_error}")

            for idx, batch in enumerate(batches):
                print(f"      [*] Sending Batch {idx + 1}/{len(batches)} ({len(batch)} items)...")
                chunk_results = process_chunk(batch, str(idx + 1))
                for result in chunk_results:
                    shortage_name = result["shortage_name"]
                    status = result["status"]
                    warehouse_item = result["warehouse_item"]
                    reason = result.get("reason", "")
                    
                    if status == "match":
                        matched.append({
                            "shortage_item": shortage_name,
                            "warehouse_item": warehouse_item,
                            "confidence": "llm",
                            "method": "fast_llm"
                        })
                    elif status == "review":
                        needs_review.append({
                            "shortage_item": shortage_name,
                            "warehouse_item": warehouse_item,
                            "reason": reason
                        })
                    else:
                        # A rejected OCR candidate cannot erase a separately
                        # established same-trade-name attribute conflict.
                        _, reviews = candidates_by_shortage.get(shortage_name, (None, []))
                        if reviews:
                            candidate, why = reviews[0]
                            needs_review.append({'shortage_item': shortage_name,
                                                 'warehouse_item': candidate['name'], 'reason': why})

        print(f"  -> Final Warehouse Result: {len(matched)} matched, {len(needs_review)} review")
        return {"matched": matched, "needs_review": needs_review}

    def _call_local_api(self, inputs: dict) -> list[dict]:
        model = getattr(self.config, 'local_model', 'gpt-4o')
        
        wire_inputs = {"cases": [{"case_id": c['case_id'], "requested_name": c['requested_name'],
                        "requested_item": item_payload(c.get('requested_item', c['requested_name'])),
                        "candidates": [{"id": x['id'], "name": unified_item(x)['raw_name'],
                                        **item_payload(x)} for x in c['candidates']]}
                       for c in inputs.get('cases', [])]}
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(wire_inputs, ensure_ascii=False)}
            ],
            "stream": False
        }

        raw_url = getattr(self.config, 'local_api_url', "http://127.0.0.1:8000/v1/chat/completions")
        url = str(raw_url).strip().rstrip("/")
        if not url.endswith("/chat/completions"):
            if url.endswith("/v1"):
                url = f"{url}/chat/completions"
            else:
                url = f"{url}/v1/chat/completions"
                
        api_key = getattr(self.config, 'local_api_key', gateway_api_key())
        case_count = len(inputs.get("cases", []))
        url_str = str(url)
        is_chatgpt = ('8000' in url_str or 'gpt' in str(model).lower())
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if not is_chatgpt:
            headers["X-Batch-Size"] = str(case_count)
            headers["X-Google-Search-Enabled"] = "false"
            
        read_timeout = max(360, case_count * 5 + 60) if is_chatgpt else max(900, case_count * 15 + 300)
        
        t_call_start = time.time()
        try:
            response = http_requests.post(
                url,
                headers=headers,
                json=body,
                timeout=(30, read_timeout),
            )
        except Exception as conn_err:
            self._log_provider_error(url, model, inputs, str(conn_err), "NETWORK_CONNECTION_FAILED")
            raise RuntimeError(f"Connection to local LLM failed ({url}): {conn_err}")

        t_call_dur = time.time() - t_call_start
        pre_exec = response.headers.get("X-Timing-PreExec", "N/A")
        gen_time = response.headers.get("X-Timing-Generation", "N/A")
        gw_total = response.headers.get("X-Timing-Total", "N/A")
        search_flag = response.headers.get("X-Google-Search-Enabled", "false")
        tool_calls = response.headers.get("X-Tool-Calls-Count", "0")
        thinking_lvl = response.headers.get("X-Thinking-Mode", "High")
        final_status = response.headers.get("X-Final-Status", "SUCCESS")

        self.last_batch_meta = {
            "case_count": case_count,
            "gen_time": gen_time,
            "pre_exec": pre_exec,
            "gw_total": gw_total,
            "search_enabled": search_flag,
            "tool_calls": tool_calls,
            "thinking_level": thinking_lvl,
            "final_status": final_status,
        }

        logger.info(
            f"[{case_count} cases] Local API roundtrip: {t_call_dur:.2f}s | "
            f"Google Search: {search_flag} | Tool Calls: {tool_calls} | "
            f"Thinking: {thinking_lvl} | Gateway Total: {gw_total}"
        )

        if response.status_code != 200:
            err_msg = f"HTTP {response.status_code}: {response.text[:300]}"
            self._log_provider_error(url, model, inputs, response.text, f"HTTP_{response.status_code}")
            raise RuntimeError(err_msg)

        content = ""
        resp_text = response.text.strip()
        if resp_text.startswith("data:"):
            # Handle unexpected SSE stream gracefully
            parts = []
            for line in resp_text.splitlines():
                line = line.strip()
                if line.startswith("data:") and line != "data: [DONE]":
                    data_str = line[5:].strip()
                    try:
                        chunk_obj = json.loads(data_str)
                        delta = chunk_obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            parts.append(delta)
                    except:
                        pass
            content = "".join(parts)
        else:
            try:
                resp_json = response.json()
            except Exception as e:
                self._log_provider_error(url, model, inputs, response.text, "INVALID_HTTP_JSON")
                raise RuntimeError(f"Local API did not return valid HTTP JSON: {response.text[:300]}")

            choices = resp_json.get("choices")
            if not choices or not isinstance(choices, list):
                self._log_provider_error(url, model, inputs, response.text, "EMPTY_CHOICES")
                raise RuntimeError(f"Local API returned no choices: {response.text[:300]}")

            content = choices[0].get("message", {}).get("content", "")
            if not isinstance(content, str):
                content = str(content or "")

        # Check if MSEMAX returned an error string inside content
        if content.strip().startswith("[Error:"):
            self._log_provider_error(url, model, inputs, content, "MSEMAX_ERROR_STRING")
            if "expired" in content.lower() or "chat-requirements" in content.lower():
                raise RuntimeError(f"انتهت صلاحية جلسة {model} (Session Expired). يرجى فتح تبويب سيرفرات الذكاء الاصطناعي والضغط على 'فتح الجلسة (Login)' لتسجيل الدخول مجدداً: {content.strip()}")
            raise RuntimeError(f"MSEMAX Error: {content.strip()}")

        if "too_many_tool_calls" in content.lower():
            self._log_provider_error(url, model, inputs, content, "TOO_MANY_TOOL_CALLS")
            raise RuntimeError(f"too_many_tool_calls error from provider: {content[:400]}")

        # Robust JSON extraction
        clean = content.strip()
        # 1. Try markdown code block extraction
        md_match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", clean, re.DOTALL)
        if md_match:
            clean = md_match.group(1).strip()
        else:
            # 2. Try outermost curly braces
            curly_match = re.search(r'\{.*\}', clean, re.DOTALL)
            if curly_match:
                clean = curly_match.group(0).strip()
            else:
                # 3. Try outermost square brackets
                bracket_match = re.search(r'\[.*\]', clean, re.DOTALL)
                if bracket_match:
                    clean = bracket_match.group(0).strip()

        self.last_raw_response = clean
        try:
            answer = json.loads(clean)
        except json.JSONDecodeError as jde:
            # Fallback: if extra data or multiple concatenated JSONs exist, decode the first valid JSON
            try:
                decoder = json.JSONDecoder()
                answer, _ = decoder.raw_decode(clean)
            except Exception:
                self._log_provider_error(url, model, inputs, content, f"JSON_DECODE_ERROR: {jde}")
                raise RuntimeError(f"JSON Parse Error ({jde}): Model output was: {content[:300]}")

        # If answer is a list of results directly
        if isinstance(answer, list):
            results = answer
        elif isinstance(answer, dict):
            results = answer.get("results", [])
        else:
            results = []

        sent_case_ids = [c["case_id"] for c in inputs.get("cases", [])]
        returned_case_ids = [d.get("case_id") for d in results if isinstance(d, dict) and d.get("case_id")]
        
        # Check for duplicates
        if len(returned_case_ids) != len(set(returned_case_ids)):
            err_msg = f"PROVIDER_RESPONSE_INVALID: Duplicate case_ids returned: {returned_case_ids}"
            self._log_provider_error(url, model, inputs, content, "PROVIDER_RESPONSE_INVALID")
            raise RuntimeError(err_msg)

        # Check for missing cases (STRICT: no silent fallback to no_match)
        missing_ids = set(sent_case_ids) - set(returned_case_ids)
        if missing_ids:
            err_msg = f"PROVIDER_RESPONSE_INCOMPLETE: Model returned {len(returned_case_ids)}/{len(sent_case_ids)} cases. Missing: {sorted(list(missing_ids))}"
            self._log_provider_error(url, model, inputs, content, "PROVIDER_RESPONSE_INCOMPLETE")
            raise RuntimeError(err_msg)

        # Check for unexpected extra cases
        extra_ids = set(returned_case_ids) - set(sent_case_ids)
        if extra_ids:
            err_msg = f"PROVIDER_RESPONSE_INVALID: Unexpected extra case_ids: {sorted(list(extra_ids))}"
            self._log_provider_error(url, model, inputs, content, "PROVIDER_RESPONSE_INVALID")
            raise RuntimeError(err_msg)

        # Map by case_id strictly
        decision_map = {d["case_id"]: d for d in results}
        return [decision_map[c["case_id"]] for c in inputs["cases"]]

    def _log_provider_error(self, url: str, model: str, inputs: dict, raw_response: str, error_type: str):
        try:
            from datetime import datetime
            import os
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "provider_errors.log")
            
            case_ids = [c.get("case_id") for c in inputs.get("cases", [])]
            entry = (
                f"\n{'='*70}\n"
                f"TIMESTAMP: {datetime.now().isoformat()}\n"
                f"ERROR TYPE: {error_type}\n"
                f"URL: {url} | MODEL: {model}\n"
                f"CASE COUNT: {len(case_ids)} | CASES: {case_ids}\n"
                f"RAW RESPONSE:\n{raw_response}\n"
                f"{'='*70}\n"
            )
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as log_err:
            print(f"[!] Warning: Failed to write to provider_errors.log: {log_err}")

