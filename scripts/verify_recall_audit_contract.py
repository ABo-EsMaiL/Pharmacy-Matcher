"""Re-adjudicate inconsistent audit records; original decisions remain intact."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))


def main():
    import requests
    import no_match_recall_audit as audit
    from src.config import load_config
    from src.fast_match.attributes import compare_strengths
    target = audit.OUT / 'decisions_verified.json'
    if target.exists():
        raise RuntimeError('Preserve completed verification')
    plan = json.loads((audit.OUT / 'plan.json').read_text(encoding='utf-8'))
    decisions = {d['case_id']: d for f in audit.OUT.glob('decisions_[0-9][0-9].json')
                 for d in json.loads(f.read_text(encoding='utf-8'))}
    cases = []
    reasons = {}
    for c in plan['cases']:
        d = decisions[c['case_id']]
        if d['status'] != 'no_match':
            continue
        if d['no_match_basis'] == 'no_name_evidence' and d['plausible_ids']:
            reasons[c['case_id']] = 'inconsistent_nonempty_plausible_ids'
        elif d['no_match_basis'] == 'explicit_strength_conflict' and any(
            x['id'] in d['plausible_ids'] and compare_strengths(c['requested_name'], x['name']) != 'conflict'
            for x in c['candidates']
        ):
            reasons[c['case_id']] = 'at_least_one_plausible_pair_without_python_strength_conflict'
        else:
            continue
        cases.append(c)
    assert len(cases) <= 75
    audit.save(audit.OUT / 'verification_plan.json', {'cases': cases, 'reasons': reasons})
    config = load_config()
    settings = json.loads((ROOT / 'data/settings.json').read_text(encoding='utf-8'))
    for key in ('local_api_url', 'local_api_key', 'local_model'):
        if settings.get(key): setattr(config, key, settings[key])
    health = requests.get('http://127.0.0.1:8001/health', timeout=10).json()
    assert health['active_thinking'].lower() == 'high' and not health['google_search_enabled'] and health['clear_chat_on_request']
    audit.AUDIT_PROMPT += '''\nAudit data consistency: plausible_ids must contain only real name-related
candidates, NEVER all input IDs by default. If no_match_basis is no_name_evidence,
plausible_ids MUST be []. A nearest neighbor is not necessarily plausible.
For an explicit_strength_conflict rejection, examine EVERY plausible candidate:
one conflicting pair does not rule out another with missing strength or a
different form. Do not reinterpret package volume as mg. If rejection depends
on a variant difference, use combination_or_variant_conflict, not strength.
'''
    print(f'Audit verification: {len(cases)} cases', flush=True)
    result = audit.call_batch(cases, config, 10)
    audit.save(audit.OUT / 'verification_response.json', result)
    assert all(not (d['no_match_basis'] == 'no_name_evidence' and d['plausible_ids']) for d in result)
    audit.save(target, result)
    print('Audit verification complete', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
