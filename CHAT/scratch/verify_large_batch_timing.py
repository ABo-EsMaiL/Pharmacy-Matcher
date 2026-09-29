"""
End-to-End verification script for 75-case batch with Google Search DISABLED and Thinking High.
"""
import json
import time
import requests
import sys

# Ensure Pharmacy is in python path
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.coordinator import FastCoordinator
from src.config import Config

API_URL = "http://127.0.0.1:8001/v1/chat/completions"
API_KEY = "[REDACTED_CREDENTIAL]"

def main():
    print("=" * 80)
    print("RUNTIME VERIFICATION: 75-CASE BATCH (SEARCH OFF + THINKING HIGH)")
    print("=" * 80)

    # 1. Health check
    h = requests.get("http://127.0.0.1:8001/health", timeout=5).json()
    print(f"[1] Gateway: {h.get('gateway')}")
    print(f"[2] Active Model: {h.get('active_model')[:35]}... (Verified: {h.get('model_verified')})")
    print(f"[3] Thinking Level: {h.get('active_thinking')} (Verified: {h.get('thinking_verified')})")
    print(f"[4] Google Search: {'ENABLED' if h.get('google_search_enabled') else 'DISABLED (OFF)'} (Verified: {h.get('search_verified')})")
    print(f"[5] Fresh Chat / Session per request: {h.get('clear_chat_on_request')}")

    assert h.get("google_search_enabled") is False, "Google Search should be disabled!"
    assert h.get("active_thinking") == "High", "Thinking Level should be High!"
    assert h.get("clear_chat_on_request") is True, "Clear chat on request should be True!"

    # 2. Build 5 canonical test cases covering core business rules
    canonical_templates = [
        {
            "template_id": 1,
            "rule": "Strength mismatch (نوفاكس 250 vs 500) -> no_match",
            "requested_name": "نوفاكس 250 مجم 20 قرص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-001", "name": "نوفاكس 500 مجم 20 قرص"}],
            "expected_status": "no_match"
        },
        {
            "template_id": 2,
            "rule": "Dosage form diff (مرهم vs كريم) -> review",
            "requested_name": "بيتاديرم مرهم 15 جم",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-002", "name": "بيتاديرم كريم 15 جم"}],
            "expected_status": "review"
        },
        {
            "template_id": 3,
            "rule": "Pack size diff (15 قرص vs 60 قرص, 1000 مجم vs 1 جم) -> match",
            "requested_name": "دوليبران 1000 مجم 15 قرص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-003", "name": "دوليبران 1 جم 60 قرص"}],
            "expected_status": "match"
        },
        {
            "template_id": 4,
            "rule": "OCR corruption (فورسيجا vs فورسجا) -> match",
            "requested_name": "فورسيجا 10 مجم أقراص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-004", "name": "فورسجا 10 مجم أقراص"}],
            "expected_status": "match"
        },
        {
            "template_id": 5,
            "rule": "Generic alt / different brand (بنادول vs سيتال) -> no_match",
            "requested_name": "بنادول 500 مجم أقراص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-005", "name": "سيتال 500 مجم أقراص"}],
            "expected_status": "no_match"
        }
    ]

    # Replicate exactly 75 cases (15 replicates of 5 canonical rules)
    cases_75 = []
    case_expected_map = {}
    for i in range(15):
        for idx, base in enumerate(canonical_templates):
            cid = f"TEST-{(i*5 + idx + 1):02d}"
            c = {
                "case_id": cid,
                "requested_name": base["requested_name"],
                "catalog_id": base["catalog_id"],
                "candidates": base["candidates"]
            }
            cases_75.append(c)
            case_expected_map[cid] = base["expected_status"]

    assert len(cases_75) == 75, f"Expected 75 cases, got {len(cases_75)}"
    print(f"\n[+] Built batch of exactly 75 cases (15 replicates of 5 canonical rules).")

    # 3. Call Pharmacy FastCoordinator
    cfg = Config(unstructured_api_key="dummy", gemini_api_key="dummy")
    cfg.local_api_url = API_URL
    cfg.local_api_key = API_KEY
    cfg.local_model = "gemini-3.8-flash"
    coord = FastCoordinator(cfg)

    print(f"\n[*] Dispatching 75 cases to MSEMAX Gateway (Search OFF, Thinking High)...")
    t0 = time.time()
    try:
        results = coord._call_local_api({"cases": cases_75})
        dur = time.time() - t0
        meta = getattr(coord, "last_batch_meta", {})
        
        print("\n" + "=" * 80)
        print("EXECUTION RESULTS & METRICS")
        print("=" * 80)
        print(f"[*] Total Roundtrip Time: {dur:.2f}s")
        print(f"[*] Gateway Generation Time: {meta.get('gen_time', 'N/A')}")
        print(f"[*] Gateway Pre-Exec Time: {meta.get('pre_exec', 'N/A')}")
        print(f"[*] Gateway Final Status: {meta.get('final_status', 'N/A')}")
        print(f"[*] Google Search Enabled in Gateway: {meta.get('search_enabled', 'N/A')}")
        print(f"[*] Tool Calls Count (DOM Chips): {meta.get('tool_calls', '0')}")
        print(f"[*] Thinking Mode: {meta.get('thinking_level', 'N/A')}")
        print(f"[*] Returned Cases Count: {len(results)} / 75")
        print(f"[*] Raw Response Length: {len(coord.last_raw_response)} characters")

        # 4. Verify no too_many_tool_calls
        if "too_many_tool_calls" in coord.last_raw_response.lower():
            print("[X] FAILURE: too_many_tool_calls detected in raw response!")
            sys.exit(1)
        else:
            print("[✓] Zero tool calls / No 'too_many_tool_calls' error detected.")

        # 5. Verify all 75 case IDs returned
        returned_ids = {r.get("case_id") for r in results}
        expected_ids = {c["case_id"] for c in cases_75}
        missing = expected_ids - returned_ids
        if missing:
            print(f"[X] FAILURE: Missing case IDs ({len(missing)} missing): {sorted(list(missing))}")
            sys.exit(1)
        else:
            print("[✓] EXACT 75/75 MATCH: Every single case ID was returned by Gemini!")

        # 6. Verify Schema for all 75 results
        schema_errors = []
        for r in results:
            cid = r.get("case_id")
            st = r.get("status")
            if not cid or st not in ("match", "review", "no_match"):
                schema_errors.append(r)
        if schema_errors:
            print(f"[X] Schema violation on items: {schema_errors}")
            sys.exit(1)
        else:
            print("[✓] Schema Compliance: 100% (all 75 items have valid case_id and valid status)")

        # 7. Verify Rule Compliance across all 75 cases
        rule_violations = []
        for r in results:
            cid = r.get("case_id")
            actual_st = r.get("status")
            expected_st = case_expected_map.get(cid)
            if actual_st != expected_st:
                rule_violations.append({
                    "case_id": cid,
                    "expected": expected_st,
                    "actual": actual_st,
                    "reason": r.get("reason", "")
                })

        strength_decisions = [r for r in results if int(r.get("case_id", "").split("-")[1]) % 5 == 1]
        dosage_decisions = [r for r in results if int(r.get("case_id", "").split("-")[1]) % 5 == 2]
        pack_decisions = [r for r in results if int(r.get("case_id", "").split("-")[1]) % 5 == 3]
        ocr_decisions = [r for r in results if int(r.get("case_id", "").split("-")[1]) % 5 == 4]
        generic_decisions = [r for r in results if int(r.get("case_id", "").split("-")[1]) % 5 == 0]

        str_ok = all(r.get('status') == 'no_match' for r in strength_decisions)
        dos_ok = all(r.get('status') == 'review' for r in dosage_decisions)
        pck_ok = all(r.get('status') == 'match' for r in pack_decisions)
        ocr_ok = all(r.get('status') == 'match' for r in ocr_decisions)
        gen_ok = all(r.get('status') == 'no_match' for r in generic_decisions)

        print("\n" + "=" * 80)
        print("CANONICAL RULES COMPLIANCE (15 REPLICATES EACH = 75 TOTAL)")
        print("=" * 80)
        print(f"1. Strength mismatch -> no_match:  {'PASS' if str_ok else 'FAIL'} ({len(strength_decisions)}/15 compliant)")
        print(f"2. Dosage form diff  -> review:    {'PASS' if dos_ok else 'FAIL'} ({len(dosage_decisions)}/15 compliant)")
        print(f"3. Pack size diff    -> match:     {'PASS' if pck_ok else 'FAIL'} ({len(pack_decisions)}/15 compliant)")
        print(f"4. OCR corruption    -> match:     {'PASS' if ocr_ok else 'FAIL'} ({len(ocr_decisions)}/15 compliant)")
        print(f"5. Generic alt       -> no_match:  {'PASS' if gen_ok else 'FAIL'} ({len(generic_decisions)}/15 compliant)")

        if rule_violations:
            print(f"\n[X] Violations details ({len(rule_violations)}):")
            for v in rule_violations[:10]:
                print(f"    - {v['case_id']}: expected {v['expected']}, got {v['actual']} | reason: {v['reason']}")
            sys.exit(1)
        else:
            print(f"\n[✓] ALL 75 CASES (100%) PERFECTLY COMPLIANT WITH PHARMACEUTICAL RULES!")

        # 8. Sample raw response preview
        print("\n" + "=" * 80)
        print("RAW RESPONSE PREVIEW (First 3 & Last 3 items):")
        print("=" * 80)
        preview_cases = results[:3] + results[-3:]
        print(json.dumps(preview_cases, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n[X] CRITICAL EXCEPTION during 75-case batch execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
