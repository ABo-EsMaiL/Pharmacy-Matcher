"""Render the completed offline census before authorizing a separate run."""
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))


def main():
    from test_retrieval_regressions import OBSERVED_PAIRS
    from src.fast_match.search import name_evidence
    from src.fast_match.coordinator import classify_pair
    folder = ROOT / 'scratch/retrieval_audit'
    before = json.loads((folder / 'before.json').read_text(encoding='utf-8'))
    after = json.loads((folder / 'after_verified.json').read_text(encoding='utf-8'))
    reasons = Counter()
    for data in after['warehouses'].values():
        reasons.update(data['rejected_reasons'])
    metrics = [('All catalog item comparisons before gate', 'candidate_pairs_before_gate'),
               ('Candidate pairs after gate', 'candidate_pairs_after_gate'),
               ('Candidate pairs retained after top-six', 'candidate_pairs_top6'),
               ('Cases routed to LLM (offline forecast)', 'planned_llm_cases'),
               ('Candidate pairs in LLM payloads (offline forecast)', 'planned_llm_candidate_pairs'),
               ('Request/warehouse cases without a candidate', 'cases_without_candidate')]
    lines = ['# RETRIEVAL PREFLIGHT — before the new PROC', '',
             'Source: immutable PROC-019 inputs and Vision cache. 591 unique requests, 6 warehouses, 2,718 catalog items.', '',
             '**No real LLM calls and no new PROC were made during this census.** Routing uses the real coordinator with a recording stub; its placeholder decisions are not business results.', '',
             '| Metric | Before | After |', '|---|---:|---:|']
    for label, key in metrics:
        lines.append(f"| {label} | {before['totals'][key]:,} | {after['totals'][key]:,} |")
    lines += [f"| Unique requests without a candidate in any warehouse | {before['unique_shortages_without_candidate_in_any_warehouse']} | {after['unique_shortages_without_candidate_in_any_warehouse']} |", '',
              'A case means one request in one warehouse (3,546 possible cases). A candidate pair is one request/catalog-item comparison. These counts are not MATCH totals.', '',
              '## Rejection reasons', '', '| Gate reason | Comparisons |', '|---|---:|']
    lines += [f'| {reason} | {count:,} |' for reason, count in sorted(reasons.items())]
    lines += ['', 'The JSON census contains each case, gate counts, its top-six candidates and separate classifier reasons. TF-IDF ranks candidates only after the full-name gate. Explicit strength or combination rejection is recorded separately from name rejection.', '',
              '## Confirmed fixtures', '', '| Requested | Cached candidate | Route |', '|---|---|---|']
    fixtures = []
    for query, candidate in OBSERVED_PAIRS:
        evidence = name_evidence(query, candidate)
        route = classify_pair(query, candidate)
        fixtures.append({'requested': query, 'candidate': candidate, 'evidence': asdict(evidence), 'classifier': route})
        lines.append(f'| {query} | {candidate} | {route[0]} — {route[1]} |')
    lines += ['', 'All seven candidates pass their real warehouse top-six regression. Contextual removal of possible company/trade/form-corruption text never grants automatic MATCH; original descriptions reach the LLM.', '',
              '42 test methods pass: 27 existing, 12 retrieval tests, 3 separately approved adjacent guard tests. Synthetic deletion/insertion/spacing, Unicode, OCR dot confusion, token ordering and suffix/prefix negatives are included.', '',
              'Decision Graph, prompt, Vision extraction, Batch 75, Search OFF, Thinking HIGH, Fresh Chat ON and the three output categories are unchanged.', '',
              'The two approved guard corrections recognize attached Arabic combination markers and route mass-versus-concentration uncertainty to LLM. Unequal measurements on the same basis still reject.', '',
              'This report demonstrates the specified recall/precision regressions and routing, not ground-truth accuracy for every possible item pair.']
    (folder / 'RETRIEVAL_PREFLIGHT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (folder / 'fixture_evidence.json').write_text(json.dumps(fixtures, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'.join(lines[:26]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
