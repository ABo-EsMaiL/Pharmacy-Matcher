"""Run a new process from PROC-019 after regressions and an offline retrieval census.

Copies the unchanged Vision cache into the new process, preserving OCR evidence
so this run measures matching fixes. Never writes into the source process.
"""
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def fingerprints(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file()}


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    import requests
    from desktop_app.database import HistoryDB
    from src.config import load_config
    from src.extract.file_handler import read_input_files
    from src.fast_match.coordinator import FastCoordinator
    from src.output.excel_writer import write_results_excel

    test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                           '-s', 'tests', '-p', 'test_*regressions.py', '-v'],
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    print(test.stdout + test.stderr, flush=True)
    if test.returncode:
        raise RuntimeError('Regression gate failed; no process created')

    census_path = ROOT / 'scratch/retrieval_audit/after_verified.json'
    census = json.loads(census_path.read_text(encoding='utf-8'))
    assert census['mode'] == 'offline_retrieval_census' and census['actual_llm_requests'] == 0
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
               for path, digest in census['code_hashes'].items()), 'Retrieval census is stale'

    config = load_config()
    settings = json.loads((ROOT / 'data/settings.json').read_text(encoding='utf-8'))
    for key in ('local_api_url', 'local_api_key', 'local_model', 'vision_api_url', 'vision_api_key', 'vision_model'):
        if settings.get(key):
            setattr(config, key, settings[key])
    assert config.local_api_url == 'http://127.0.0.1:8001/v1/chat/completions'
    assert config.local_model == 'gemini-3.8-flash'
    health = requests.get('http://127.0.0.1:8001/health', timeout=10).json()
    assert health.get('browser_ready') and health.get('model_verified')
    assert 'gemini-3.8-flash' in health.get('active_model', '').lower()
    assert health.get('thinking_verified') and health.get('active_thinking', '').lower() == 'high'
    assert health.get('search_verified') and health.get('google_search_enabled') is False
    assert health.get('clear_chat_on_request') is True

    source = ROOT / 'data/processes/PROC-019'
    before = fingerprints(source)
    shortages = sorted((source / 'input_shortages').iterdir())
    warehouses = sorted((source / 'input_warehouses').iterdir())
    db = HistoryDB()
    next_dir = db.get_process_dir(db.get_next_id())
    if next_dir.exists():
        raise RuntimeError(f'Refusing to reuse existing process directory: {next_dir}')
    process_id = db.create_process([p.name for p in shortages], [p.name for p in warehouses])
    proc = db.get_process_dir(process_id)
    print(f'NEW PROCESS: {process_id}', flush=True)
    metadata = {'process_id': process_id, 'source_process': 'PROC-019',
                'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'processing',
                'regressions_passed': True, 'source_hashes_before': before,
                'vision_cache_reused': True, 'gateway_preflight': health,
                'batch_size': 75, 'google_search': False, 'thinking': 'high', 'fresh_chat': True,
                'code_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [*sorted((ROOT / 'src/fast_match').glob('*.py')),
                                          ROOT / 'src/output/excel_writer.py', ROOT / 'src/match/text_match.py']}}
    save_json(proc / 'run_metadata.json', metadata)
    shutil.copy2(census_path, proc / 'retrieval_preflight.json')
    (proc / 'regression_tests.log').write_text(test.stdout + test.stderr, encoding='utf-8')
    try:
        for folder, paths in [('input_shortages', shortages), ('input_warehouses', warehouses)]:
            for path in paths:
                shutil.copy2(path, proc / folder / path.name)
        shutil.copytree(source / 'cache', proc / 'cache')

        with (proc / 'run.log').open('w', encoding='utf-8', buffering=1) as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                kwargs = dict(vision_api_url=config.vision_api_url, vision_api_key=config.vision_api_key,
                              vision_model=config.vision_model)
                shortage_data = read_input_files([proc / 'input_shortages' / p.name for p in shortages], role='shortages', **kwargs)
                warehouse_data = read_input_files([proc / 'input_warehouses' / p.name for p in warehouses], role='warehouse', **kwargs)
                if any(not rows for rows in [*shortage_data.values(), *warehouse_data.values()]):
                    raise RuntimeError('Input extraction returned an empty file; aborting incomplete process')
                all_shortages = [item for rows in shortage_data.values() for item in rows]
                metadata['input_counts'] = {'shortages': len(all_shortages),
                                            'warehouses': {name: len(rows) for name, rows in warehouse_data.items()}}
                save_json(proc / 'run_metadata.json', metadata)
                engine = FastCoordinator(config)
                original_call = engine._call_local_api
                def recorded_call(inputs):
                    answer = original_call(inputs)
                    with (proc / 'llm_batches.jsonl').open('a', encoding='utf-8') as batch_log:
                        batch_log.write(json.dumps({'inputs': inputs, 'decisions': answer,
                                                    'gateway': engine.last_batch_meta}, ensure_ascii=False) + '\n')
                    return answer
                engine._call_local_api = recorded_call
                results = engine.process(all_shortages, warehouse_data)
                save_json(proc / 'results.json', results)
                output = proc / f'results_{process_id}.xlsx'
                write_results_excel(results, output)
                summary = results['summary']
                status = 'reviewing' if summary['review_count'] else 'completed'
                db.update_process(process_id, status=status, output_file=str(output),
                                  **{k: summary[k] for k in ('total_shortages', 'matched_count', 'not_found_count', 'review_count')})
                metadata.update(status=status, summary=summary)
    except Exception as exc:
        db.update_process(process_id, status='error')
        metadata.update(status='error', error=str(exc))
        (proc / 'error.log').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        metadata['source_unchanged'] = fingerprints(source) == before
        metadata['finished_at'] = datetime.now(timezone.utc).isoformat()
        save_json(proc / 'run_metadata.json', metadata)
        db.conn.close()
    print(json.dumps({'process_id': process_id, 'status': metadata['status'], 'summary': metadata.get('summary'),
                      'source_unchanged': metadata['source_unchanged']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
