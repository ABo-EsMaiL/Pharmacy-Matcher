"""
Main Coordinator - Matches shortages against all warehouses.
Uses three phases: Exact Text -> Fuzzy -> LLM (OpenRouter)
"""

import json
import time
import getpass
import os
import re
import requests as http_requests

from ..config import Config
from .text_match import normalize_text, find_candidates


SYSTEM_PROMPT = """You are a pharmaceutical matching assistant.
Compare requested pharmaceutical product descriptions with a supplied catalog.

Return ONLY a valid JSON object matching this exact schema:
{
  "results": [
    {
      "case_id": "string",
      "status": "match or no_match or review",
      "item_ids": ["string"]
    }
  ]
}

Rules:
1. "match" means the exact same product, strength, dosage form, and pack size. Return the ID in "item_ids".
2. "no_match" means no exact or highly plausible match exists. "item_ids" must be empty [].
3. "review" means there is a plausible candidate but details are ambiguous or slightly mismatched.
4. DO NOT return markdown blocks. Return ONLY the raw JSON starting with { and ending with }.
5. ONLY return results for cases you are provided.
"""


class Coordinator:
    def __init__(self, config: Config):
        self.config = config
        self.openrouter_api_key = getattr(config, 'openrouter_api_key', None)

    def process(
        self,
        shortage_items: list[dict],
        warehouse_data: dict[str, list[dict]],
    ) -> dict:
        
        unique_shortages = {}
        for item in shortage_items:
            name = item.get("item_name_raw", "")
            if name and name not in unique_shortages:
                unique_shortages[name] = item
                
        deduped_shortages = list(unique_shortages.values())

        print(f"\n{'='*60}")
        print(f"[*] Starting Match: {len(shortage_items)} raw -> {len(deduped_shortages)} UNIQUE shortages x {len(warehouse_data)} warehouses")
        print(f"{'='*60}\n")

        all_warehouse_results = {}
        found_in: dict[str, list[str]] = {}

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
        
        review_only_names = set()
        for wh_result in all_warehouse_results.values():
            for rev in wh_result["needs_review"]:
                review_only_names.add(rev["shortage_item"])

        not_found_names = all_shortage_names - found_names - review_only_names
        not_found_items = [
            {"name": name, "source": next(
                (item.get("source_file", "") for item in deduped_shortages
                 if item.get("item_name_raw") == name), ""
            )}
            for name in sorted(not_found_names)
        ]

        summary = {
            "total_shortages": len(shortage_items),
            "unique_shortages": len(deduped_shortages),
            "matched_count": len(found_names),
            "not_found_count": len(not_found_names),
            "review_count": len(review_only_names - found_names),
        }

        print(f"\n{'='*60}")
        print(f"[*] Match Summary:")
        print(f"    Total Shortages: {summary['total_shortages']}")
        print(f"    Unique Names:    {summary['unique_shortages']}")
        print(f"    Matched:         {summary['matched_count']}")
        print(f"    Not Found:       {summary['not_found_count']}")
        print(f"    Needs Review:    {summary['review_count']}")
        print(f"{'='*60}\n")

        return {
            "warehouse_results": all_warehouse_results,
            "not_found": not_found_items,
            "summary": summary,
        }

    def _match_warehouse(
        self,
        shortage_items: list[dict],
        warehouse_items: list[dict],
        warehouse_name: str,
    ) -> dict:
        matched: list[dict] = []
        needs_review: list[dict] = []
        remaining = list(shortage_items)

        wh_names = [item.get("item_name_raw", "") for item in warehouse_items]
        wh_normalized = {normalize_text(name): name for name in wh_names}

        still_remaining = []
        exact_count = 0
        for item in remaining:
            shortage_name = item.get("item_name_raw", "")
            normalized = normalize_text(shortage_name)
            if normalized in wh_normalized:
                matched.append({
                    "shortage_item": shortage_name,
                    "warehouse_item": wh_normalized[normalized],
                    "confidence": "exact",
                    "method": "exact_text",
                })
                exact_count += 1
            else:
                still_remaining.append(item)
        remaining = still_remaining
        print(f"  -> Exact Text Match: {exact_count}")

        if remaining and self.openrouter_api_key:
            llm_results = self._llm_batch_match(remaining, warehouse_items, warehouse_name)
            for result in llm_results:
                if result["status"] == "match":
                    matched.append({
                        "shortage_item": result["shortage_name"],
                        "warehouse_item": result.get("warehouse_item", ""),
                        "confidence": "llm",
                        "method": "llm",
                        "reason": "",
                    })
                elif result["status"] == "review":
                    needs_review.append({
                        "shortage_item": result["shortage_name"],
                        "warehouse_item": result.get("warehouse_item", ""),
                        "reason": "",
                    })

        print(f"  -> Final Result: {len(matched)} matched, {len(needs_review)} review")
        return {"matched": matched, "needs_review": needs_review}

    def _llm_batch_match(
        self,
        shortage_items: list[dict],
        warehouse_items: list[dict],
        warehouse_name: str,
    ) -> list[dict]:
        import concurrent.futures

        batch_size = 50
        all_results = []

        wid = "W1"
        catalog = [
            {"id": f"{wid}-{i:05}", "name": item.get("item_name_raw", "")}
            for i, item in enumerate(warehouse_items, 1)
        ]
        catalog_by_id = {item["id"]: item["name"] for item in catalog}

        cases = []
        for i, item in enumerate(shortage_items, 1):
            cases.append({
                "case_id": f"Q{i:05}-{wid}",
                "requested_name": item.get("item_name_raw", ""),
                "catalog_id": wid,
            })

        total_batches = (len(cases) + batch_size - 1) // batch_size
        batches = []
        for batch_idx in range(total_batches):
            start = batch_idx * batch_size
            end = min(start + batch_size, len(cases))
            batches.append((batch_idx, cases[start:end]))

        print(f"  -> [OpenRouter] Executing {total_batches} batches in parallel... This will be MUCH faster!")

        def process_batch(batch_data):
            batch_idx, batch_cases = batch_data
            inputs = {"catalogs": {wid: catalog}, "cases": batch_cases}
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    results = self._call_openrouter(inputs)
                    parsed_results = []
                    for case, decision in zip(batch_cases, results):
                        shortage_name = case["requested_name"]
                        status = decision.get("status", "no_match")
                        item_ids = decision.get("item_ids", [])
                        warehouse_item = ""
                        if isinstance(item_ids, list) and item_ids:
                            warehouse_item = catalog_by_id.get(item_ids[0], "")
                        parsed_results.append({
                            "shortage_name": shortage_name,
                            "status": status,
                            "warehouse_item": warehouse_item,
                        })
                    print(f"      [✓] Batch {batch_idx+1}/{total_batches} completed.")
                    return parsed_results
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(3.0)
                    else:
                        print(f"      [!] Batch {batch_idx+1} failed: {e}")
            
            # Fallback if completely failed
            return [{
                "shortage_name": case["requested_name"],
                "status": "no_match",
                "warehouse_item": ""
            } for case in batch_cases]

        # Use ThreadPoolExecutor to run multiple requests at the same time
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # Map returns results in the same order
            results_list = list(executor.map(process_batch, batches))

        for res in results_list:
            all_results.extend(res)

        return all_results

    def _call_openrouter(self, inputs: dict) -> list[dict]:
        model = getattr(self.config, 'openrouter_model', 'openrouter/free')
        
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(inputs, ensure_ascii=False)}
            ],
            # Removed response_format json_object because many openrouter/free models do not support it
        }

        url = "https://openrouter.ai/api/v1/chat/completions"
        response = http_requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost",
                "X-Title": "PharmacyMatcher",
            },
            json=body,
            timeout=(30, 300),
        )

        if response.status_code != 200:
            try:
                detail = response.json().get("error", {}).get("message", "")
            except:
                detail = response.text[:200]
            raise RuntimeError(f"HTTP {response.status_code}: {detail}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
            
            # Robust JSON extraction for generic models that ignore 'no markdown' rules
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            answer = json.loads(content)
        except Exception as e:
            raise RuntimeError(f"Failed to parse OpenRouter response: {e}")

        if not isinstance(answer, dict) or "results" not in answer:
            answer = {"results": []}

        results = answer.get("results", [])
        case_ids = {c["case_id"] for c in inputs["cases"]}
        validated = {}
        for decision in results:
            cid = decision.get("case_id")
            if cid in case_ids and cid not in validated:
                validated[cid] = decision

        # Default to "no_match" for any case ID not returned by the model
        return [validated.get(c["case_id"], {"status": "no_match", "item_ids": []})
                for c in inputs["cases"]]
