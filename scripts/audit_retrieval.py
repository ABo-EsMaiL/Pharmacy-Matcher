"""Offline retrieval census: immutable cached inputs, no provider, no PROC creation."""
import contextlib
from collections import Counter
from dataclasses import asdict
import hashlib
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_inputs():
    from src.extract.file_handler import read_input_files
    source = ROOT / 'data/processes/PROC-019'
    with contextlib.redirect_stdout(io.StringIO()):
        inputs = read_input_files(sorted((source / 'input_shortages').iterdir()), role='shortages')
    shortages = {r['item_name_raw']: r for rows in inputs.values() for r in rows}
    warehouses = {}
    for folder in sorted((source / 'cache/vision').iterdir()):
        for page in sorted((folder / 'results').glob('page_*.json'), key=lambda p: int(p.stem.split('_')[-1])):
            for row in json.loads(page.read_text(encoding='utf-8'))['items']:
                warehouses.setdefault(row['source_file'], []).append(row)
    return list(shortages.values()), warehouses


def main():
    from src.config import Config
    from src.fast_match.search import FastCandidateFinder, name_evidence
    from src.fast_match.coordinator import FastCoordinator, classify_pair
    destination = Path(sys.argv[1])
    if destination.exists():
        raise ValueError('Use a new report path; historical reports are immutable')
    with patch('requests.sessions.Session.request', side_effect=AssertionError('Offline audit forbids network')):
        shortages, warehouses = load_inputs()
        report = {'source': 'PROC-019', 'mode': 'offline_retrieval_census',
                  'actual_llm_requests': 0, 'unique_shortages': len(shortages),
                  'code_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted((ROOT / 'src/fast_match').glob('*.py'))},
                  'warehouses': {}, 'cases': []}
        zero_everywhere = {r['item_name_raw'] for r in shortages}
        for warehouse, rows in warehouses.items():
            finder = FastCandidateFinder()
            finder.fit([{'id': f'W-{i:05}', 'name': r['item_name_raw']} for i, r in enumerate(rows)])
            counts, rejects = Counter(), Counter()
            for requested in shortages:
                query = requested['item_name_raw']
                # All name comparisons, before top-six truncation or classifier.
                accepted = finder.search(query, top_k=len(rows))
                reasons = Counter()
                if hasattr(finder, 'last_diagnostics'):
                    reasons.update(finder.last_diagnostics['rejected_reasons'])
                else:
                    reasons['no_meaningful_name_evidence'] = len(rows) - len(accepted)
                rejects.update(reasons)
                counts['candidate_pairs_before_gate'] += len(rows)
                counts['candidate_pairs_after_gate'] += len(accepted)
                counts['candidate_pairs_top6'] += len(accepted[:6])
                counts['cases_without_candidate'] += not accepted
                if accepted:
                    zero_everywhere.discard(query)
                report['cases'].append({'warehouse': warehouse, 'requested': query,
                    'before_gate': len(rows), 'after_gate': len(accepted),
                    'rejected_reasons': dict(reasons),
                    'top6': [{**c, 'classifier': classify_pair(query, c['name'])} for c in accepted[:6]]})
            planned = []
            engine = FastCoordinator(Config('', '', local_api_url='http://127.0.0.1:8001/v1/chat/completions', local_model='gemini-3.8-flash'))
            def capture(payload):
                planned.extend(payload['cases'])
                # Placeholder used only to complete the dry-run routing; never exported as results.
                return [{'case_id': c['case_id'], 'status': 'no_match', 'item_id': ''} for c in payload['cases']]
            with patch.object(engine, '_call_local_api', side_effect=capture), patch('src.fast_match.coordinator.time.sleep'), contextlib.redirect_stdout(io.StringIO()):
                engine._match_warehouse(shortages, rows, warehouse)
            counts['planned_llm_cases'] = len(planned)
            counts['planned_llm_candidate_pairs'] = sum(len(c['candidates']) for c in planned)
            report['warehouses'][warehouse] = {'catalog_items': len(rows), **dict(counts), 'rejected_reasons': dict(rejects)}
            print(warehouse, dict(counts), flush=True)
        totals = Counter()
        for data in report['warehouses'].values():
            totals.update({k: v for k, v in data.items() if isinstance(v, int)})
        report['totals'] = dict(totals)
        report['unique_shortages_without_candidate_in_any_warehouse'] = len(zero_everywhere)
        report['no_candidate_names'] = sorted(zero_everywhere)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'totals': report['totals'], 'unique_without_candidate': len(zero_everywhere)}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
