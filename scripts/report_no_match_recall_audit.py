"""Evidence report for the separate recall audit; never updates PROC results."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))


def retained_variant_numbers(raw):
    """Audit diagnostic: distinguish surviving explicit count spans from variants."""
    from src.fast_match.attributes import numeric_evidence, COUNT_FORM, PACK, NUMBER
    text = numeric_evidence(raw).identity_text
    # Removing dose spans can expose counts that the original parser missed
    # when directly attached to a preceding unit. This is not a runtime fix.
    text = re.sub(rf'{NUMBER}\s*(?:{COUNT_FORM}|{PACK})(?![a-z])', ' ', text)
    # Hyphen + quantity + commercial b-marker is explicitly packaging/price
    # notation in the supplied evidence; do not confuse it with prefix B12.
    text = re.sub(r'-\s*\d+\s*ب(?=\W|$)', ' ', text)
    return re.findall(r'\b\d+\b', text)


def audit_has_co(raw):
    """Audit the literal combination marker with adjacent quantity separated.

    This diagnoses the runtime word-boundary bug without altering its code.
    """
    from src.fast_match.coordinator import has_co
    return has_co(re.sub(r'(?<=[^\W\d_])(?=\d)', ' ', raw))


def main():
    from no_match_recall_audit import OUT, fingerprints, save
    from src.fast_match.attributes import compare_strengths
    from src.fast_match.coordinator import has_co, extract_form_group, are_forms_identical, classify_pair
    from src.fast_match.search import extract_brand_tokens
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    historic = []
    for line in (ROOT / 'data/processes/PROC-020/llm_batches.jsonl').read_text(encoding='utf-8').splitlines():
        batch = json.loads(line)
        by_case = {d['case_id']: d for d in batch['decisions']}
        for c in batch['inputs']['cases']:
            historic.append((c, by_case[c['case_id']]))
    decisions = {}
    for f in sorted(OUT.glob('decisions_[0-9][0-9].json')):
        for d in json.loads(f.read_text(encoding='utf-8')):
            assert d['case_id'] not in decisions
            decisions[d['case_id']] = d
    assert set(decisions) == {c['case_id'] for c in plan['cases']}, 'Audit incomplete; do not publish totals'
    verified = json.loads((OUT / 'decisions_verified.json').read_text(encoding='utf-8'))
    for d in verified:
        assert d['case_id'] in decisions
        decisions[d['case_id']] = d
    assert all(not (d['no_match_basis'] == 'no_name_evidence' and d['plausible_ids']) for d in decisions.values())
    amr_plan = json.loads((OUT / 'amr_plan.json').read_text(encoding='utf-8'))
    amr_decisions = {d['case_id']: d for d in json.loads((OUT / 'decisions_amr.json').read_text(encoding='utf-8'))}
    assert set(amr_decisions) == {c['case_id'] for c in amr_plan['cases']}
    extra_cases = []
    extra_decisions = {}
    if (OUT / 'decisions_guard_followup.json').exists():
        extra_cases = json.loads((OUT / 'guard_followup_plan.json').read_text(encoding='utf-8'))['cases']
        extra_decisions = {d['case_id']: d for d in json.loads((OUT / 'decisions_guard_followup.json').read_text(encoding='utf-8'))}
        assert set(extra_decisions) == {c['case_id'] for c in extra_cases}
    all_rows = []
    manual_notes = {r['case_id']: r for r in json.loads((OUT / 'manual_audit_notes.json').read_text(encoding='utf-8'))}
    for case in plan['cases'] + amr_plan['cases'] + extra_cases:
        d = (amr_decisions if case['scope'] == 'amr_only' else extra_decisions if case['scope'] == 'guard_followup' else decisions)[case['case_id']]
        candidates = {c['id']: c for c in case['candidates']}
        row = {'case_id': case['case_id'], 'requested': case['requested_name'], 'scope': case['scope'],
               'llm_decision': d, 'plausible_candidates': [candidates[i] for i in d['plausible_ids']],
               'audit_status': d['status'], 'guard_notes': [], 'selected': candidates.get(d['item_id'])}
        if row['selected']:
            candidate = row['selected']['name']
            current = classify_pair(row['requested'], candidate)
            row['current_classifier'] = current
            previous = [d for c, d in historic if c['requested_name'] == row['requested']
                        and any(x['name'] == candidate for x in c['candidates'])]
            row['previous_llm_decisions_for_candidate'] = previous
            row['loss_stage'] = ('retrieval_name_gate' if current[1] == 'no_meaningful_name_evidence' else
                                 'parser_or_final_guard' if current[0] == 'reject' else
                                 'llm_adjudication' if previous else 'candidate_ranking_or_routing')
            # A changed model opinion alone is not proof of recovered identity.
            # Unicode/spacing-equivalent names provide independent evidence;
            # unresolved spelling disagreements remain visible in this audit.
            identity_disagreement = any(p['status'] == 'no_match' and
                (('اختلاف' in p.get('reason', '') and 'اسم' in p.get('reason', '')) or
                 'براند مختلف' in p.get('reason', '')) for p in previous)
            if (identity_disagreement and
                    re.sub(r'[\s\d]+', '', extract_brand_tokens(row['requested'])) !=
                    re.sub(r'[\s\d]+', '', extract_brand_tokens(candidate))):
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('llm_identity_disagreement_needs_source_evidence')
            relation = compare_strengths(row['requested'], candidate)
            if relation == 'conflict':
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('explicit_strength_guard_blocked_positive')
            if has_co(row['requested']) != has_co(candidate) and audit_has_co(row['requested']) == audit_has_co(candidate):
                row['runtime_parser_diagnostic'] = 'combination_marker_followed_by_quantity_missed'
            if audit_has_co(row['requested']) != audit_has_co(candidate):
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('combination_guard_blocked_positive')
            va, vb = retained_variant_numbers(row['requested']), retained_variant_numbers(candidate)
            if va and vb and va != vb:
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('product_variant_or_numeric_context_unresolved')
            a, b = extract_form_group(row['requested']), extract_form_group(candidate)
            if row['audit_status'] == 'match' and a and b and not are_forms_identical(a, b):
                row['audit_status'] = 'review'
                row['guard_notes'].append('known_different_form_requires_review')
            elif row['audit_status'] == 'review' and a and b and are_forms_identical(a, b):
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('review_without_form_difference_unresolved')
        if row['case_id'] in manual_notes:
            row['manual_audit_note'] = manual_notes[row['case_id']]
            if manual_notes[row['case_id']]['assessment'] == 'unresolved':
                row['audit_status'] = 'no_match'
                row['guard_notes'].append('audit_evidence_unresolved')
        all_rows.append(row)
    global_rows = []
    for case in plan['cases']:
        if case['scope'] != 'global_no_match': continue
        evidence = [r for r in all_rows if r['requested'] == case['requested_name']]
        positive = [r for r in evidence if r['audit_status'] in {'match', 'review'}]
        plausible = any(r['plausible_candidates'] for r in evidence)
        if any(r['audit_status'] == 'match' for r in positive): category = 'recovered_match'
        elif positive: category = 'recovered_review'
        elif not plausible: category = 'no_plausible_candidate_found'
        elif any(r['llm_decision']['no_match_basis'] == 'insufficient_information' or r['guard_notes'] for r in evidence):
            category = 'unresolved'
        else: category = 'supported_no_match'
        global_rows.append({'requested': case['requested_name'], 'category': category,
                            'has_plausible_candidate': plausible, 'evidence': evidence})
    counts = Counter(r['category'] for r in global_rows)
    unchanged = fingerprints() == json.loads((OUT / 'source_fingerprints.json').read_text(encoding='utf-8'))
    assert unchanged
    summary = {'total_no_match': len(global_rows),
               'no_match_with_no_plausible_candidate': sum(not r['has_plausible_candidate'] for r in global_rows),
               'no_match_with_plausible_candidate': sum(r['has_plausible_candidate'] for r in global_rows),
               'recovered_match': counts['recovered_match'], 'recovered_review': counts['recovered_review'],
               'supported_true_no_match_after_audit': counts['supported_no_match'],
               'unresolved_with_plausible_candidate': counts['unresolved'],
               'no_plausible_candidate_is_not_proven_absence': counts['no_plausible_candidate_found'],
               'pages': plan['page_count'], 'catalog_items': plan['catalog_count'],
               'all_pairs_scored': plan['all_pair_comparisons'], 'source_runtime_unchanged': unchanged,
               'new_proc_created': False}
    assert sum(counts.values()) == 461
    save(OUT / 'report.json', {'summary': summary, 'rows': global_rows, 'all_adjudications': all_rows})
    save(OUT / 'recovered.json', [r for r in global_rows if r['category'].startswith('recovered_')])
    save(OUT / 'guard_disagreements.json', [r for r in all_rows if r['guard_notes']])
    lines = ['# NO_MATCH RECALL AUDIT — PROC-020', '',
             'Audit only. No matching code, Decision Graph or original process files were changed; no new PROC was created.', '',
             '| Metric | Count |', '|---|---:|']
    lines += [f'| {k} | {v} |' for k, v in summary.items()]
    lines += ['', 'Counts are unique requests. A recovered MATCH takes precedence over REVIEW across warehouses. Amr-only discoveries for requests already matched elsewhere are reported separately, not added to the 461 denominator.', '',
              'No plausible candidate found is not proof that the item is absent. Supported NO_MATCH means plausible audited candidates were rejected for explicit conflicting evidence; unresolved cases are not counted as confirmed negatives.', '',
              'All 46 cached pages / 2,718 rows were scored using independent character n-grams, length-normalized edit distance, full-character alignment, Arabic OCR dot-shape similarity and token coverage. Rank unions, every exact/one-edit name and the nearest two per warehouse were retained without the production gate. Raw original names were sent to the same configured gateway, Batch 75, Search OFF, Thinking HIGH, Fresh Chat ON.', '',
              'This is an evidence-based recall audit, not an externally labeled ground-truth corpus or a proof that all possible false negatives were eliminated.', '',
              'Audit response validation: inconsistent plausible-ID lists were re-adjudicated. Swapped empty item-ID/list fields were normalized with a separate provenance log; no business status or nonempty ID was changed by that normalization. Conflicting positive/negative judgments across those replies remain unresolved. Provider failures are not item decisions.', '',
              '## Recovered requests', '', '| Requested | Audit outcome | Warehouse item | Warehouse / page | Current rejection / route |', '|---|---|---|---|---|']
    for row in global_rows:
        if not row['category'].startswith('recovered_'): continue
        positive = sorted([e for e in row['evidence'] if e['audit_status'] in {'match', 'review'}], key=lambda e: e['audit_status'] != 'match')[0]
        c = positive['selected']
        lines.append(f"| {row['requested']} | {positive['audit_status']} | {c['name']} | {c['warehouse']} / {c['page']} | {positive.get('current_classifier')} |")
    lines += ['', '## Amr-only adjudications', '', '| Requested | Outcome | Warehouse item | Reason |', '|---|---|---|---|']
    for row in all_rows:
        if row['scope'] != 'amr_only': continue
        outcome = 'unresolved' if row['guard_notes'] and row['audit_status'] == 'no_match' else row['audit_status']
        lines.append(f"| {row['requested']} | {outcome} | {(row['selected'] or {}).get('name','')} | {row['llm_decision']['reason']} |")
    lines += ['', '## All 19 Amr warehouse rows', '', '| Warehouse item | Relevant requested item | Audit finding |', '|---|---|---|']
    inventory = json.loads((OUT / 'amr_inventory.json').read_text(encoding='utf-8'))
    for item in inventory:
        relevant = [e for e in all_rows if e['scope'] == 'amr_only' and e['selected'] and e['selected']['id'] == item['id']]
        if relevant:
            for e in relevant:
                outcome = 'unresolved' if e['guard_notes'] and e['audit_status'] == 'no_match' else e['audit_status']
                lines.append(f"| {item['name']} | {e['requested']} | {outcome}; {e.get('current_classifier')}; {'; '.join(e['guard_notes'])} |")
        else:
            lines.append(f"| {item['name']} | — | No supported requested counterpart found in the reverse audit; this is not evidence that a requested item was rejected. |")
    lines += ['', '## Unresolved cases', '', '| Requested | Candidate / evidence | Why not counted as recovered or true NO_MATCH |', '|---|---|---|']
    for row in global_rows:
        if row['category'] != 'unresolved': continue
        names = list(dict.fromkeys(c['name'] for e in row['evidence'] for c in e['plausible_candidates']))
        reasons = list(dict.fromkeys(note for e in row['evidence'] for note in (e['guard_notes'] or [e['llm_decision']['reason']])))
        reasons += [e['manual_audit_note']['reason'] for e in row['evidence'] if 'manual_audit_note' in e]
        lines.append(f"| {row['requested']} | {'; '.join(names)} | {'; '.join(reasons)} |")
    lines += ['', '## Every original NO_MATCH request', '', '| Requested | Audit category | Plausible warehouse items | Audit reason |', '|---|---|---|---|']
    for row in global_rows:
        names = list(dict.fromkeys(c['name'] + ' — ' + c['warehouse'] + ' p.' + str(c['page']) for e in row['evidence'] for c in e['plausible_candidates']))
        reasons = list(dict.fromkeys(e['llm_decision']['reason'] for e in row['evidence']))
        lines.append(f"| {row['requested']} | {row['category']} | {'; '.join(names) or 'None found in this audit'} | {'; '.join(reasons)} |")
    (OUT / 'NO_MATCH_RECALL_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
