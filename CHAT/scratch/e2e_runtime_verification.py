"""
End-to-End Runtime Verification Script
Strict Contract Verification:
Pharmacy -> Local MSEMAX -> Google AI Studio -> Gemini -> JSON Response -> Pharmacy Parser & Guards
"""

import json
import time
import requests
import sys
import os
import re

# Ensure project root is in path
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.coordinator import FastCoordinator, SYSTEM_PROMPT
from src.config import Config

API_URL = "http://127.0.0.1:8001/v1/chat/completions"
API_KEY = "[REDACTED_CREDENTIAL]"

def run_verification():
    print("=" * 80)
    print("        PHARMACY & MSEMAX END-TO-END STRICT RUNTIME VERIFICATION")
    print("=" * 80)

    # 1. Wait for Gateway Health & Browser Readiness
    print("\n[Step 1] Connecting to MSEMAX Gateway & Polling Browser Readiness...")
    health_resp = {}
    for attempt in range(45):
        try:
            r = requests.get("http://127.0.0.1:8001/health", timeout=3)
            if r.status_code == 200:
                health_resp = r.json()
                if health_resp.get("browser_ready"):
                    print(f"  -> Browser context is READY after {attempt+1}s!")
                    break
        except Exception:
            pass
        time.sleep(1)
    else:
        print("[FAIL] MSEMAX Gateway or Browser did not become ready in 45s.")
        return

    print("  -> Gateway:               ", health_resp.get("gateway"))
    print("  -> Browser Ready:          ", health_resp.get("browser_ready"))
    print("  -> Target Model:           ", health_resp.get("default_model"))
    print("  -> Active Model (DOM):     ", health_resp.get("active_model"))
    print("  -> Model Verified:         ", health_resp.get("model_verified"))
    print("  -> Active Thinking Level:  ", health_resp.get("active_thinking"))
    print("  -> Thinking Verified:      ", health_resp.get("thinking_verified"))
    print("  -> Fresh Chat per Batch:   ", health_resp.get("clear_chat_on_request"))

    # 2. Build the 5 Critical Test Cases
    cases = [
        {
            "case_id": "TEST-01-STRENGTH",
            "requested_name": "نوفاكس 250 مجم 20 قرص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-001", "name": "نوفاكس 500 مجم 20 قرص"}],
            "expected": "no_match",
            "rule": "Strength conflict -> NO_MATCH (Red line)"
        },
        {
            "case_id": "TEST-02-DOSAGE-FORM",
            "requested_name": "بيتاديرم مرهم 15 جم",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-002", "name": "بيتاديرم كريم 15 جم"}],
            "expected": "review",
            "rule": "Dosage form difference with same product & strength -> REVIEW"
        },
        {
            "case_id": "TEST-03-PACK-SIZE",
            "requested_name": "دوليبران 1000 مجم 15 قرص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-003", "name": "دوليبران 1 جم 60 قرص"}],
            "expected": "match",
            "rule": "Pack size difference only -> MATCH"
        },
        {
            "case_id": "TEST-04-OCR-CORRUPTION",
            "requested_name": "فورسيجا 10 مجم أقراص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-004", "name": "فورسجا 10 مجم أقراص"}],
            "expected": "match",
            "rule": "OCR corruption in name (same commercial brand) -> MATCH"
        },
        {
            "case_id": "TEST-05-GENERIC-ALT",
            "requested_name": "بنادول 500 مجم أقراص",
            "catalog_id": "W1",
            "candidates": [{"id": "W1-005", "name": "سيتال 500 مجم أقراص"}],
            "expected": "no_match",
            "rule": "Generic/Alternative brand -> NO_MATCH"
        }
    ]

    inputs = {
        "cases": [
            {
                "case_id": c["case_id"],
                "requested_name": c["requested_name"],
                "candidates": c["candidates"]
            }
            for c in cases
        ]
    }

    prompt_json = json.dumps(inputs, ensure_ascii=False)
    final_prompt = f"[System Instructions]\n{SYSTEM_PROMPT}\n\n{prompt_json}"

    print(f"\n[Step 2] Sending {len(cases)} Test Cases through Pharmacy Coordinator...")
    print(f"  -> Total final prompt length: {len(final_prompt)} characters")
    print(f"  -> Target URL: {API_URL}")
    print(f"  -> Model: gemini-3.8-flash")

    # Instantiate Pharmacy Coordinator
    dummy_config = Config(
        unstructured_api_key="dummy",
        gemini_api_key="dummy"
    )
    dummy_config.local_api_url = API_URL
    dummy_config.local_model = "gemini-3.8-flash"
    dummy_config.local_api_key = API_KEY

    coordinator = FastCoordinator(dummy_config)

    t0 = time.time()
    call_error = None
    raw_decisions = []
    raw_response_text = ""
    try:
        raw_decisions = coordinator._call_local_api(inputs)
        elapsed = time.time() - t0
        print(f"\n[Step 3] Pharmacy Coordinator Call Completed in {elapsed:.2f} seconds!")
        raw_response_text = getattr(coordinator, 'last_raw_response', '')
    except Exception as e:
        call_error = e
        elapsed = time.time() - t0
        print(f"\n[Step 3] Coordinator call encountered error: {e}")
        raw_response_text = getattr(coordinator, 'last_raw_response', '')

    # Check updated gateway state after call
    post_health = requests.get("http://127.0.0.1:8001/health", timeout=5).json()

    print("\n" + "=" * 80)
    print("                    STRICT RUNTIME AUDIT REPORT")
    print("=" * 80)
    print(f"1. Target Model:                  {post_health.get('default_model')}")
    print(f"   Actual Model in Browser:       {post_health.get('active_model')}")
    print(f"   Model Verified in Browser DOM: {post_health.get('model_verified')}")
    print(f"2. Actual Thinking Level:         {post_health.get('active_thinking')}")
    print(f"   Thinking Level Verified:       {post_health.get('thinking_verified')}")
    print(f"3. Fresh Chat/Session per Batch:  {post_health.get('clear_chat_on_request')}")
    print(f"4. Final Prompt Length:           {len(final_prompt)} characters")
    
    print("\n" + "-" * 80)
    print("5. RAW TEXT TRACE & JSON PARSING AUDIT")
    print("-" * 80)
    print(f"[*] Raw Text Received by Pharmacy Coordinator:\n{raw_response_text.strip()}")

    # Determine exact text passed to json.loads()
    clean_no_md = re.sub(r"^```(?:json)?\s*", "", raw_response_text.strip(), flags=re.MULTILINE)
    clean_no_md = re.sub(r"```\s*$", "", clean_no_md, flags=re.MULTILINE).strip()
    m_json = re.search(r'\{.*\}', clean_no_md, re.DOTALL) or re.search(r'\[.*\]', clean_no_md, re.DOTALL)
    exact_text_to_json = m_json.group(0) if m_json else clean_no_md

    print(f"\n[*] Exact Text Passed to json.loads():\n{exact_text_to_json.strip()}")

    is_valid_json = False
    parsed_json_obj = None
    try:
        parsed_json_obj = json.loads(exact_text_to_json)
        is_valid_json = True
    except Exception as je:
        is_valid_json = False
        print(f"[!] json.loads error: {je}")

    print(f"\n[*] Valid JSON: {is_valid_json}")

    # Extract returned cases
    returned_cases = []
    if isinstance(parsed_json_obj, dict):
        returned_cases = parsed_json_obj.get("results", [])
    elif isinstance(parsed_json_obj, list):
        returned_cases = parsed_json_obj

    sent_case_ids = [c["case_id"] for c in cases]
    returned_case_ids = [d.get("case_id") for d in returned_cases if isinstance(d, dict) and d.get("case_id")]
    missing_case_ids = sorted(list(set(sent_case_ids) - set(returned_case_ids)))
    extra_case_ids = sorted(list(set(returned_case_ids) - set(sent_case_ids)))

    print(f"[*] Sent Case IDs ({len(sent_case_ids)}):     {sent_case_ids}")
    print(f"[*] Returned Case IDs ({len(returned_case_ids)}): {returned_case_ids}")
    print(f"[*] Missing Case IDs:             {missing_case_ids if missing_case_ids else 'None (0 missing)'}")
    print(f"[*] Extra/Unexpected Case IDs:    {extra_case_ids if extra_case_ids else 'None (0 extra)'}")

    # Explicit Strict Assertion Check
    contract_passed = (returned_case_ids == sent_case_ids) and is_valid_json and (call_error is None)
    print(f"[*] Strict Contract Assertion (returned_case_ids == sent_case_ids): {contract_passed}")

    if call_error and not contract_passed:
        print(f"\n[!] RUNTIME EXCEPTION RAISED AS EXPECTED: {call_error}")

    print("\n" + "-" * 80)
    print("6. TEST CASES VERIFICATION (EVALUATING ALL 5 RULES)")
    print("-" * 80)

    res_map = {d.get("case_id"): d for d in returned_cases if isinstance(d, dict)}
    all_cases_passed = True and contract_passed

    for c in cases:
        cid = c["case_id"]
        exp = c["expected"]
        dec = res_map.get(cid)
        
        if dec is None:
            icon = "[X] FAILED (MISSING FROM MODEL OUTPUT)"
            all_cases_passed = False
            print(f"\n{icon} | Case: {cid}")
            print(f"    Rule:     {c['rule']}")
            print(f"    Expected: status='{exp}'")
            print(f"    Got:      MISSING — model never returned this case!")
            continue

        status = dec.get("status", "")
        item_id = dec.get("item_id", "")
        reason = dec.get("reason", "")
        
        passed = (status == exp)
        if not passed:
            all_cases_passed = False
            icon = "[X] FAILED (STATUS MISMATCH)"
        else:
            icon = "[✓] PASSED"

        print(f"\n{icon} | Case: {cid}")
        print(f"    Rule:     {c['rule']}")
        print(f"    Expected: status='{exp}'")
        print(f"    Got:      status='{status}', item_id='{item_id}', reason='{reason}'")

    print("\n" + "=" * 80)
    if all_cases_passed:
        print(">>> OVERALL RESULT: 100% STRICT END-TO-END PASS! ALL 5 CASES PRESENT & CORRECT <<<")
    else:
        print(">>> OVERALL RESULT: FAILED STRICT VERIFICATION — SEE DETAILS ABOVE <<<")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
