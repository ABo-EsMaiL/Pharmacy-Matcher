"""Audit alternative candidates after a model's selected pair fails a hard guard."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))


def main():
    import requests
    from no_match_recall_audit import OUT, call_batch, save
    from src.config import load_config
    from src.fast_match.attributes import compare_strengths
    from src.fast_match.coordinator import has_co
    from report_no_match_recall_audit import retained_variant_numbers, audit_has_co
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    decisions = {r['case_id']: r for f in OUT.glob('decisions_[0-9][0-9].json') for r in json.loads(f.read_text(encoding='utf-8'))}
    assert len(decisions) == len(plan['cases']), 'Finish the main recall audit first'
    decisions.update({r['case_id']: r for r in json.loads((OUT / 'decisions_verified.json').read_text(encoding='utf-8'))})
    def blocked(query, candidate):
        if compare_strengths(query, candidate) == 'conflict': return True
        if audit_has_co(query) != audit_has_co(candidate): return True
        a, b = retained_variant_numbers(query), retained_variant_numbers(candidate)
        return bool(a and b and a != b)
    cases = []
    for case in plan['cases']:
        d = decisions[case['case_id']]
        if d['status'] == 'no_match':
            if d['no_match_basis'] != 'explicit_strength_conflict': continue
            chosen = None
            pool = [c for c in case['candidates'] if c['id'] in d['plausible_ids']]
        else:
            chosen = next(c for c in case['candidates'] if c['id'] == d['item_id'])
            if not blocked(case['requested_name'], chosen['name']): continue
            pool = case['candidates']
        candidates = [c for c in pool if not blocked(case['requested_name'], c['name'])]
        if candidates:
            cases.append({'case_id': 'F' + case['case_id'][1:], 'requested_name': case['requested_name'],
                          'scope': 'guard_followup', 'candidates': candidates,
                          'previous_excluded_candidate': chosen})
    save(OUT / 'guard_followup_plan.json', {'cases': cases})
    if not cases:
        save(OUT / 'decisions_guard_followup.json', []); return
    assert len(cases) <= 75
    config = load_config()
    settings = json.loads((ROOT / 'data/settings.json').read_text(encoding='utf-8'))
    for key in ('local_api_url', 'local_api_key', 'local_model'):
        if settings.get(key): setattr(config, key, settings[key])
    health = requests.get('http://127.0.0.1:8001/health', timeout=10).json()
    assert health['active_thinking'].lower() == 'high' and health['google_search_enabled'] is False and health['clear_chat_on_request']
    target = OUT / 'decisions_guard_followup.json'
    if target.exists(): raise RuntimeError('Preserve completed follow-up audit')
    print(f'Guard follow-up: {len(cases)} cases, alternative candidates only', flush=True)
    save(target, call_batch(cases, config, 9))
    print('Guard follow-up complete', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
