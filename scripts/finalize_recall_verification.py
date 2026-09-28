"""Validate saved audit replies and retain disagreement rather than hide it."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'data/audits/PROC-020-no-match-recall'


def main():
    cases = {c['case_id']: c for c in json.loads((OUT / 'verification_plan.json').read_text(encoding='utf-8'))['cases']}
    fields = ('case_id', 'status', 'item_id', 'plausible_ids', 'no_match_basis', 'reason')
    history = {key: [] for key in cases}
    repairs = []
    for path in sorted(OUT.glob('batch_10_attempt_*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        try:
            rows = json.loads(json.loads(record['body'])['choices'][0]['message']['content'])['results']
        except (KeyError, ValueError):
            continue
        assert len(rows) == len(cases) and {r[0] for r in rows} == set(cases)
        for r in rows:
            assert len(r) == 6
            # Both values are empty: this repairs field ordering only, never a
            # status, item ID, plausible candidate, or business interpretation.
            if r[1] == 'no_match' and r[2] == [] and r[3] == '':
                r[2], r[3] = '', []
                repairs.append({'file': path.name, 'case_id': r[0], 'repair': 'swap_empty_item_id_and_empty_plausible_list'})
            d = dict(zip(fields, r))
            ids = {c['id'] for c in cases[r[0]]['candidates']}
            assert d['status'] in {'match', 'review', 'no_match'}
            assert isinstance(d['plausible_ids'], list) and set(d['plausible_ids']) <= ids
            assert d['item_id'] == '' if d['status'] == 'no_match' else d['item_id'] in ids and d['item_id'] in d['plausible_ids']
            assert not (d['no_match_basis'] == 'no_name_evidence' and d['plausible_ids'])
            history[r[0]].append(d)
    assert all(history.values())
    notes_path = OUT / 'manual_audit_notes.json'
    notes = json.loads(notes_path.read_text(encoding='utf-8'))
    final = []
    for key, responses in history.items():
        chosen = responses[-1]
        if len({d['status'] for d in responses}) > 1:
            chosen = next((d for d in reversed(responses) if d['status'] != 'no_match'), chosen)
            if not any(n['case_id'] == key for n in notes):
                notes.append({'case_id': key, 'assessment': 'unresolved', 'reason': 'اختلف حكم استجابات تدقيق نفس المرشحين بين الرفض والقبول. حُفظ المرشح المحتمل ولم يُحسب استرجاعًا مؤكدًا أو غيابًا مؤكدًا.', 'audit_response_statuses': [d['status'] for d in responses]})
        final.append(chosen)
    for name, data in [('decisions_verified.json', final), ('verification_schema_repairs.json', repairs), ('manual_audit_notes.json', notes)]:
        (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Validated {len(final)} cases; recorded {len(repairs)} empty-field ordering repairs')


if __name__ == '__main__':
    main()
