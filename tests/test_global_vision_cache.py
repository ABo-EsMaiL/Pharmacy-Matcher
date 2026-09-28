"""Real synthetic PDFs and rendering; gateway calls are always mocked."""
import contextlib
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch

import pypdfium2 as pdfium
from src.extract import gemini_vision_extractor as vision


def response():
    return Mock(status_code=200, json=lambda: {'choices': [{'message': {'content': json.dumps({
        'items': [{'item_name_raw': 'BRANDA 500mg tablet', 'trade_name': 'BRANDA',
                   'strength': '500mg', 'form': 'tablet'}]})}}]})


class GlobalVisionCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / 'data/cache/vision'
        self.processes = self.root / 'data/processes'
        for target, value in [('VISION_CACHE_ROOT', self.cache), ('PROCESS_ROOT', self.processes)]:
            p = patch.object(vision, target, value)
            p.start()
            self.addCleanup(p.stop)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        sleep = patch.object(vision.time, 'sleep')
        sleep.start()
        self.addCleanup(sleep.stop)
        network = patch.object(vision.requests, 'post', return_value=response())
        self.post = network.start()
        self.addCleanup(network.stop)

    def pdf(self, relative='path_A/input.pdf', pages=1, width=120):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with contextlib.closing(pdfium.PdfDocument.new()) as doc:
            for _ in range(pages):
                doc.new_page(width, 160).close()
            doc.save(path)
        return path

    def copy(self, source, relative):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
        return path

    def extract(self, path):
        return vision.extract_items_from_pdf_vision(path, api_key='synthetic-test', max_retries=1)

    def test_same_content_paths_names_and_processes_extract_once(self):
        a = self.pdf()
        b = self.copy(a, 'path_B/renamed.pdf')
        c = self.copy(a, 'data/processes/PROC-0001/input_warehouses/third.pdf')
        d = self.copy(a, 'data/processes/PROC-0002/input_warehouses/fourth.pdf')
        for path in (a, b, c, d):
            items = self.extract(path)
            self.assertEqual(items[0]['source_file'], path.name)
            self.assertEqual(items[0]['source_page'], 1)
        self.assertEqual(self.post.call_count, 1)
        folder = vision._get_cache_dir(a)
        self.assertEqual(folder, self.cache / hashlib.sha256(a.read_bytes()).hexdigest())
        self.assertEqual(vision._get_cache_dir(b), folder)
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['completed_pages'], [1])
        self.assertEqual(manifest['status'], 'completed')
        self.assertTrue({'file_name', 'file_hash', 'total_pages', 'created_at', 'updated_at'} <= manifest.keys())
        self.assertEqual(set(manifest['file_names']), {p.name for p in (a, b, c, d)})

    def test_changed_bytes_with_identical_mtime_do_not_reuse(self):
        path = self.pdf()
        original_mtime = path.stat().st_mtime_ns
        self.extract(path)
        old_cache = vision._get_cache_dir(path)
        self.pdf(width=140)
        os.utime(path, ns=(original_mtime, original_mtime))
        self.extract(path)
        self.assertNotEqual(vision._get_cache_dir(path), old_cache)
        self.assertEqual(self.post.call_count, 2)

    def test_added_and_removed_pages_change_content_identity(self):
        a, b = self.pdf(pages=1), self.pdf('other/two.pdf', pages=2)
        self.extract(a)
        self.extract(b)
        self.assertNotEqual(vision._get_cache_dir(a), vision._get_cache_dir(b))
        # Removing a page to the original bytes correctly returns to its cache.
        shutil.copyfile(a, b)
        self.extract(b)
        self.assertEqual(self.post.call_count, 3)

    def test_interruption_resume_from_renamed_copy(self):
        path = self.pdf(pages=2)
        self.post.side_effect = [response(), RuntimeError('interrupted'), response()]
        with self.assertRaises(RuntimeError):
            self.extract(path)
        manifest = json.loads((vision._get_cache_dir(path) / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['completed_pages'], [1])
        self.assertEqual(manifest['status'], 'in_progress')
        renamed = self.copy(path, 'data/processes/PROC-0002/input_warehouses/resumed.pdf')
        items = self.extract(renamed)
        self.assertEqual(self.post.call_count, 3)
        self.assertEqual([i['source_page'] for i in items], [1, 2])
        self.assertTrue(all(i['source_file'] == renamed.name for i in items))

    def test_corrupt_page_is_repaired_without_rerunning_good_pages(self):
        path = self.pdf(pages=2)
        self.extract(path)
        folder = vision._get_cache_dir(path)
        (folder / 'results/page_2.json').write_text('{interrupted', encoding='utf-8')
        self.extract(path)
        self.assertEqual(self.post.call_count, 3)

    def test_atomic_result_is_recovered_when_manifest_update_was_interrupted(self):
        path = self.pdf()
        self.extract(path)
        manifest_path = vision._get_cache_dir(path) / 'manifest.json'
        manifest_path.write_text('{interrupted', encoding='utf-8')
        self.extract(path)
        self.assertEqual(self.post.call_count, 1)

    def test_legacy_process_cache_import_uses_hash_not_name(self):
        path = self.pdf()
        legacy = self.processes / 'PROC-0000/cache/vision/unrelated_filename_deadbeef00'
        (legacy / 'results').mkdir(parents=True)
        manifest = {'file_hash': vision._compute_file_hash(path), 'total_pages': 1,
                    'completed_pages': [1], 'status': 'completed'}
        (legacy / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        (legacy / 'results/page_1.json').write_text(json.dumps({'page': 1, 'items': [
            {'item_name_raw': 'BRANDA', 'source_file': 'old.pdf', 'source_page': 1}]}), encoding='utf-8')
        saved = {p: p.read_bytes() for p in legacy.rglob('*') if p.is_file()}
        self.assertEqual(self.extract(path)[0]['source_file'], path.name)
        self.post.assert_not_called()
        self.assertTrue(all(p.read_bytes() == value for p, value in saved.items()))

    def test_legacy_cache_with_wrong_hash_is_not_reused(self):
        path = self.pdf()
        legacy = self.processes / 'PROC-0000/cache/vision/same_name'
        (legacy / 'results').mkdir(parents=True)
        (legacy / 'manifest.json').write_text(json.dumps({'file_hash': '0' * 64, 'total_pages': 1}), encoding='utf-8')
        (legacy / 'results/page_1.json').write_text(json.dumps({'page': 1, 'items': [{'item_name_raw': 'WRONG'}]}))
        self.assertEqual(self.extract(path)[0]['trade_name'], 'BRANDA')
        self.assertEqual(self.post.call_count, 1)

    def test_concurrent_identical_content_extracts_once(self):
        a = self.pdf()
        b = self.copy(a, 'path_B/renamed.pdf')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.extract, [a, b]))
        self.assertEqual(self.post.call_count, 1)
        self.assertEqual([r[0]['source_file'] for r in results], [a.name, b.name])


if __name__ == '__main__':
    unittest.main()
