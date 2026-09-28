"""Offline synthetic regressions for structured item-presence semantics."""
import contextlib
import io
import json
import unittest
from unittest.mock import Mock, patch

from src.config import Config
from src.fast_match.search import FastCandidateFinder, unified_item
from src.fast_match.coordinator import FastCoordinator, classify_pair, validate_llm_decision


def item(trade='zulvatrix', strength='500mg', form='tablet', raw=None, **extra):
    return {'item_name_raw': raw if raw is not None else ' '.join(x for x in (trade, strength, form) if x),
            'trade_name': trade, 'strength': strength, 'form': form, **extra}


class StructuredPresenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = FastCoordinator(Config('', '', local_api_url='http://127.0.0.1:8001/v1/chat/completions',
                                             local_model='gemini-3.8-flash'))
        silence = contextlib.redirect_stdout(io.StringIO())
        silence.__enter__()
        self.addCleanup(silence.__exit__, None, None, None)
        sleep = patch('src.fast_match.coordinator.time.sleep')
        sleep.start()
        self.addCleanup(sleep.stop)
        network = patch('src.fast_match.coordinator.http_requests.post', side_effect=AssertionError('Live network forbidden'))
        network.start()
        self.addCleanup(network.stop)

    def run_pair(self, requested, warehouse, decision=None):
        with patch.object(self.engine, '_call_local_api', return_value=[decision] if decision else [],
                          side_effect=None if decision else AssertionError('Unexpected LLM')):
            return self.engine.process([requested], {'fixture': [warehouse]})

    def test_structured_primary_ignores_raw_commercial_noise(self):
        q = item(trade='كازمولين', form='cream')
        w = item(trade='كازمولين', form='cream', raw='كازمولين كريم كبييير سعر قدييم باكو 25',
                 source_file='catalog.pdf', source_page=7)
        finder = FastCandidateFinder()
        finder.fit([{**w, 'id': 'W'}])
        candidate = finder.search(q)[0]
        self.assertEqual(candidate['trade_name'], 'كازمولين')
        self.assertEqual(candidate['source_page'], 7)
        self.assertEqual(candidate['source_file'], 'catalog.pdf')
        self.assertEqual(self.run_pair(q, w)['summary']['matched_count'], 1)

    def test_raw_only_fallback_and_local_schema(self):
        raw = 'zulvatrix 500mg20 tablets'
        parsed = unified_item(raw)
        self.assertEqual(parsed['raw_name'], raw)
        self.assertEqual(parsed['trade_name'], 'zulvatrix')
        self.assertEqual(parsed['_strength_values'], ('500',))
        self.assertEqual(parsed['form'], 'tablet')
        self.assertIn('20 tablets', parsed['package'])
        result = self.run_pair({'item_name_raw': raw}, {'item_name_raw': 'zulvatrix 500mg 40 tablets'})
        self.assertEqual(result['summary']['matched_count'], 1)

    def test_strength_conflict_is_review_and_not_not_found(self):
        result = self.run_pair(item(), item(strength='250mg'))
        self.assertEqual(result['summary']['review_count'], 1)
        self.assertEqual(result['not_found'], [])
        self.assertIn('strength', result['warehouse_results']['fixture']['needs_review'][0]['reason'])

    def test_form_conflict_is_review(self):
        result = self.run_pair(item(), item(form='ampoule'))
        self.assertEqual(result['summary']['review_count'], 1)
        self.assertEqual(result['not_found'], [])

    def test_package_volume_count_and_price_do_not_change_identity(self):
        for form, a, b in [('tablet', '20 tablets old price', '40 tablets new price'),
                           ('syrup', '30ml', '60ml'), ('ampoule', '3 ampoules', '6 ampoules')]:
            with self.subTest(form=form):
                result = self.run_pair(item(form=form, raw=f'zulvatrix 500mg {a}'),
                                       item(form=form, raw=f'zulvatrix 500mg {b}'))
                self.assertEqual(result['summary']['matched_count'], 1)

    def test_attached_counts_and_pack_markers_are_not_variants(self):
        for raw in ['كازمولين 500مجم20قرص', 'كازمولين 500مجم -32ب', 'كازمولين 500mg -32 pack']:
            with self.subTest(raw=raw):
                self.assertEqual(unified_item(raw)['trade_name'], 'كازمولين')
                self.assertEqual(unified_item(raw)['_strength_values'], ('500',))

    def test_package_volume_or_tube_mass_in_vision_strength_field(self):
        for form, a, b in [('syrup', '30ml', '60ml'), ('cream', '20g', '40g'),
                           ('syrup', '۳۰،۰مل', '60مل')]:
            result = self.run_pair(item(form=form, strength=a), item(form=form, strength=b))
            # Explicit volume inside structured strength is uncertain per the
            # current user policy; topical package mass keeps existing behavior.
            self.assertEqual(result['summary']['matched_count' if form == 'cream' else 'review_count'], 1)
            parsed = unified_item(item(form=form, strength=a))
            self.assertIsNone(parsed['strength'])
            self.assertEqual(parsed['extracted_fields']['strength'], a)

    def test_missing_strength_both_directions_survives_llm_no_match(self):
        for requested, warehouse in [(item(), item(strength=None)), (item(strength=None), item())]:
            with self.subTest(requested=requested):
                d = {'case_id': 'Q00000', 'status': 'no_match', 'item_id': '', 'identity_same': False}
                result = self.run_pair(requested, warehouse, d)
                self.assertEqual(result['not_found'], [])
                self.assertEqual(result['summary']['review_count'], 1)

    def test_missing_fields_can_be_adjudicated_match(self):
        d = {'case_id': 'Q00000', 'status': 'match', 'item_id': 'W-00000', 'identity_same': True}
        self.assertEqual(self.run_pair(item(), item(strength=None), d)['summary']['matched_count'], 1)

    def test_distinct_names_shared_attributes_do_not_retrieve(self):
        finder = FastCandidateFinder()
        finder.fit([{**item(trade='mornetalis'), 'id': 'bad'}])
        self.assertEqual(finder.search(item()), [])
        self.assertEqual(self.run_pair(item(), item(trade='mornetalis'))['summary']['not_found_count'], 1)

    def test_ocr_noise_survives_structured_retrieval(self):
        for name in ['zulvatrix', 'كازمولين']:
            for altered in [name[1:], name[:3] + 'x' + name[3:], name[:3] + ' ' + name[3:]]:
                with self.subTest(name=name, altered=altered):
                    f = FastCandidateFinder()
                    f.fit([{**item(trade=altered), 'id': 'ocr'}])
                    self.assertEqual([c['id'] for c in f.search(item(trade=name))], ['ocr'])

    def test_unicode_and_persian_normalization(self):
        for a, b in [('كازمولين', 'کازمولین'), ('zulvatrix', 'ｚｕｌｖａｔｒｉｘ'), ('كازمولين', 'ﻛﺎﺯﻣﻮﻟﻴﻦ')]:
            with self.subTest(a=a):
                self.assertEqual(self.run_pair(item(trade=a), item(trade=b))['summary']['matched_count'], 1)

    def test_all_same_trade_rows_survive_top_k_then_attributes_choose(self):
        warehouse = [item(strength=f'{i}mg') for i in range(1, 13)]
        finder = FastCandidateFinder()
        finder.fit([{**v, 'id': str(i)} for i, v in enumerate(warehouse)])
        self.assertEqual(len(finder.search(item(strength='12mg'), top_k=1)), 12)
        with patch.object(self.engine, '_call_local_api', side_effect=AssertionError('Matching row exists')):
            result = self.engine.process([item(strength='12mg')], {'fixture': warehouse})
        self.assertEqual(result['summary']['matched_count'], 1)
        self.assertEqual(result['warehouse_results']['fixture']['matched'][0]['warehouse_item'], warehouse[-1]['item_name_raw'])

    def test_structured_data_reaches_actual_http_payload(self):
        w = item(strength=None, source_file='test.pdf', source_page=3)
        response = Mock(status_code=200, headers={})
        response.text = '{}'
        response.json.return_value = {'choices': [{'message': {'content': json.dumps({'results': [
            {'case_id': 'Q00000', 'item_id': 'W-00000', 'status': 'match', 'identity_same': True}]})}}]}
        with patch('src.fast_match.coordinator.http_requests.post', return_value=response) as post:
            result = self.engine.process([item()], {'fixture': [w]})
        wire = post.call_args.kwargs
        case = json.loads(wire['json']['messages'][1]['content'])['cases'][0]
        self.assertEqual(case['requested_item']['trade_name'], 'zulvatrix')
        self.assertEqual(case['requested_item']['strength'], '500mg')
        self.assertIsNone(case['candidates'][0]['strength'])
        self.assertEqual(case['candidates'][0]['source_page'], 3)
        self.assertEqual(case['candidates'][0]['source_file'], 'test.pdf')
        self.assertEqual(wire['headers']['X-Google-Search-Enabled'], 'false')
        self.assertEqual(wire['json']['model'], 'gemini-3.8-flash')
        self.assertEqual(result['summary']['matched_count'], 1)

    def test_python_blocks_llm_match_on_attribute_conflict(self):
        for candidate in [item(strength='250mg'), item(form='ampoule'), item(trade='zulvatrix plus')]:
            case = {'case_id': 'Q', 'requested_name': item()['item_name_raw'], 'requested_item': item(),
                    'candidates': [{**candidate, 'id': 'W'}]}
            decision = {'case_id': 'Q', 'item_id': 'W', 'status': 'match', 'identity_same': True}
            self.assertEqual(validate_llm_decision(case, decision)['status'], 'review')

    def test_structured_raw_attribute_disagreement_is_not_auto_match(self):
        for w in [item(strength='500mg', raw='zulvatrix 250mg tablet'),
                  item(form='tablet', raw='zulvatrix 500mg syrup')]:
            self.assertEqual(classify_pair(item(), w)[0], 'review')

    def test_unusable_structured_trade_uses_raw_fallback(self):
        q = item()
        w = {**item(), 'trade_name': 'tablets'}
        finder = FastCandidateFinder()
        finder.fit([{**w, 'id': 'W'}])
        self.assertEqual(finder.search(q)[0]['trade_name'], 'zulvatrix')
        self.assertNotEqual(classify_pair(q, w)[0], 'reject')

    def test_mixed_structured_and_raw_fallback_views_are_merged(self):
        a = item(raw='zulvatrix commercial descriptor')
        b = {'item_name_raw': 'zulvatrix 500mg tablets / SampleLab'}
        for requested, warehouse in [(a, b), (b, a)]:
            finder = FastCandidateFinder()
            finder.fit([{**warehouse, 'id': 'W'}])
            self.assertEqual([c['id'] for c in finder.search(requested)], ['W'])
            self.assertNotEqual(classify_pair(requested, warehouse)[0], 'reject')

    def test_no_external_substitution_from_llm(self):
        case = {'case_id': 'Q', 'requested_name': item()['item_name_raw'], 'requested_item': item(),
                'candidates': [{**item(trade='mornetalis'), 'id': 'W'}]}
        self.assertEqual(validate_llm_decision(case, {'case_id': 'Q', 'item_id': 'W', 'status': 'match'})['status'], 'no_match')
        with self.assertRaisesRegex(ValueError, 'outside case candidates'):
            validate_llm_decision(case, {'case_id': 'Q', 'item_id': 'invented', 'status': 'match'})

    def test_variant_numbers_preserved_as_attribute_conflict(self):
        a, b = item(trade='nurvalen 1'), item(trade='nurvalen 2')
        self.assertNotEqual(unified_item(a)['trade_name'], unified_item(b)['trade_name'])
        self.assertEqual(classify_pair(a, b), ('review', 'product_variant_conflict'))

    def test_provider_failure_is_neither_review_nor_absence(self):
        with patch.object(self.engine, '_call_local_api', side_effect=RuntimeError('HTTP 429')):
            with self.assertRaisesRegex(RuntimeError, 'Provider failed'):
                self.engine.process([item()], {'fixture': [item(strength=None)]})

    def test_ocr_identity_can_be_rejected_explicitly(self):
        q, w = item(), item(trade='zulvatrik')
        d = {'case_id': 'Q00000', 'status': 'no_match', 'item_id': '', 'identity_same': False}
        self.assertEqual(self.run_pair(q, w, d)['summary']['not_found_count'], 1)


if __name__ == '__main__':
    unittest.main()
