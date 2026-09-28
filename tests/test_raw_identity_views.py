"""Synthetic-only coverage of raw requests against structured Vision identity."""
import contextlib
import io
import unittest
from unittest.mock import patch

from src.config import Config
from src.fast_match.search import FastCandidateFinder, unified_item, item_payload
from src.fast_match.coordinator import FastCoordinator, classify_pair


def warehouse(trade='branda', strength='500mg', form='powder', **extra):
    return {'id': 'W', 'item_name_raw': f'{trade} {strength} {form}',
            'trade_name': trade, 'strength': strength, 'form': form, **extra}


class RawIdentityViewsTests(unittest.TestCase):
    def retrieve(self, request, candidate):
        finder = FastCandidateFinder()
        finder.fit([candidate])
        return finder.search(request)

    def test_powder_and_attached_volume(self):
        for raw in ['BRANDA 500mg POWDER 60ml', 'BRANDA500mg powder60ml',
                    'كازمولين۵۰۰مجم بودره۶۰مل']:
            with self.subTest(raw=raw):
                trade = 'كازمولين' if raw.startswith('ك') else 'branda'
                parsed = unified_item(raw)
                self.assertIn(trade, parsed['identity_views'])
                self.assertEqual(parsed['raw_name'], raw)
                self.assertIn('full', parsed['retrieval_reference'])
                self.assertEqual(parsed['_strength_values'], ('500',))
                self.assertEqual(parsed['_forms'], ('powder',))
                self.assertTrue(self.retrieve(raw, warehouse(trade)))
                self.assertEqual(classify_pair(raw, warehouse(trade))[0], 'match')

    def test_attribute_decision_table(self):
        for request, candidate, expected in [
            ('BRANDA 500mg TABLET', warehouse(form='tablet', strength='250mg'), 'review'),
            ('BRANDA 500mg TABLET', warehouse(form='ampoule'), 'review'),
            ('BRANDA 500mg 20 tablets', warehouse(form='tablet', package='40 tablets'), 'match'),
            ('BRANDA 500mg', warehouse(trade='OTHERBRAND'), 'reject'),
            ('BRANDA 500mg', warehouse(strength='', form=''), 'ambiguous'),
            ('BRANDA', warehouse(), 'ambiguous'),
        ]:
            with self.subTest(request=request, candidate=candidate):
                self.assertEqual(classify_pair(request, candidate)[0], expected)
                self.assertEqual(bool(self.retrieve(request, candidate)), expected != 'reject')

    def test_usage_descriptors_are_hypotheses_not_canonical_aliases(self):
        for descriptor in ['مطهر', 'مرطب', 'ملين', 'مهبلي', 'جلد', 'اطفال',
                           'moisturizer', 'antiseptic', 'children']:
            raw = f'كازمولين {descriptor}'
            with self.subTest(descriptor=descriptor):
                self.assertIn('كازمولين', unified_item(raw)['identity_views'])
                self.assertTrue(self.retrieve(raw, warehouse('كازمولين')))
                self.assertEqual(classify_pair(raw, warehouse('كازمولين'))[0], 'ambiguous')
                structured = unified_item(warehouse('كازمولين ' + descriptor))
                self.assertEqual(structured['trade_name'], 'كازمولين ' + descriptor)
                self.assertEqual(structured['field_sources']['trade_name'], 'structured')

    def test_known_form_then_unknown_description_keeps_prefix_hypothesis(self):
        raw = 'velunatrix 500mg cream unfamiliar description'
        self.assertIn('velunatrix', unified_item(raw)['identity_views'])
        self.assertTrue(self.retrieve(raw, warehouse('velunatrix', form='cream')))
        self.assertEqual(classify_pair(raw, warehouse('velunatrix', form='cream'))[0], 'ambiguous')

    def test_slash_primary_only_and_no_tail_alias(self):
        candidate = warehouse('velunatrix')
        self.assertTrue(self.retrieve('velunatrix / secondary supplier description', candidate))
        self.assertEqual(classify_pair('velunatrix / secondary supplier description', candidate)[0], 'ambiguous')
        self.assertFalse(self.retrieve('morzaliven / velunatrix', candidate))
        self.assertFalse(self.retrieve('morzaliven powder / velunatrix', candidate))

    def test_strength_ratio_is_not_supplier_separator(self):
        raw = 'velunatrix 500mg/5ml syrup'
        parsed = unified_item(raw)
        self.assertEqual(parsed['_strength_values'], ('100mg/ml',))
        self.assertEqual(parsed['trade_name'], 'velunatrix')

    def test_whole_name_required_even_when_attributes_identical(self):
        for other in ['atrix', 'velu', 'kobunatrix', 'xupodrem']:
            for suffix in ['500mg powder60ml', '500mg lotion / supplier']:
                with self.subTest(other=other, suffix=suffix):
                    self.assertFalse(self.retrieve('velunatrix ' + suffix, warehouse(other)))
        self.assertFalse(self.retrieve('alpha medication 500mg powder', warehouse('alpha unrelated')))

    def test_full_raw_reference_cannot_bypass_name_gate(self):
        with patch('src.fast_match.search.cosine_similarity', return_value=__import__('numpy').array([[1.0]])):
            self.assertFalse(self.retrieve('xupodrem 500mg powder60ml', warehouse('velunatrix', raw_name='unused')))

    def test_shared_usage_description_does_not_supply_name_evidence(self):
        for descriptor in ['moisturizer', 'antiseptic', 'مرطب']:
            self.assertFalse(self.retrieve(f'abc {descriptor}',
                             {'id': 'W', 'item_name_raw': f'xyz {descriptor}'}))

    def test_attached_count_does_not_become_variant(self):
        parsed = unified_item('velunatrix40tablets')
        self.assertEqual(parsed['trade_name'], 'velunatrix')
        self.assertEqual(parsed['_strength_values'], ())
        self.assertEqual(unified_item('velunatrix2')['trade_name'], 'velunatrix 2')

    def test_extension_is_whole_token_evidence_and_always_uncertain(self):
        for raw, trade in [('velunatrix lab', 'velunatrix'),
                           ('velunatrix', 'lab velunatrix')]:
            self.assertTrue(self.retrieve(raw, warehouse(trade)))
            self.assertEqual(classify_pair(raw, warehouse(trade))[0], 'ambiguous')
        self.assertFalse(self.retrieve('alpha unknown', warehouse('alpha unrelated')))
        self.assertFalse(self.retrieve('velunatrix', warehouse('big unrelated name velunatrix')))

    def test_form_word_in_explicit_trade_field_is_preserved(self):
        parsed = unified_item(warehouse('velunatrix powder'))
        self.assertEqual(parsed['trade_name'], 'velunatrix powder')
        self.assertEqual(parsed['field_sources']['trade_name'], 'structured')
        self.assertEqual(classify_pair('velunatrix', parsed)[0], 'ambiguous')

    def test_attached_variant_before_drops_is_not_guessed_strength(self):
        parsed = unified_item('كازمولين دي3+كي2 نقط')
        self.assertEqual(parsed['_strength_values'], ())
        self.assertIn('3', parsed['trade_name'])
        self.assertIn('2', parsed['trade_name'])

    def test_generic_arabic_preposition_and_reordered_whole_tokens(self):
        raw = 'كازمورين بالفيلتران'
        self.assertTrue(self.retrieve(raw, warehouse('فيلتران كازمورين')))
        self.assertEqual(classify_pair(raw, warehouse('فيلتران كازمورين'))[0], 'ambiguous')

    def test_release_spacing_view_is_uncertain(self):
        self.assertTrue(self.retrieve('كازمولين اس ار اقراص', warehouse('كازمولين اسار')))
        self.assertEqual(classify_pair('كازمولين اس ار اقراص', warehouse('كازمولين اسار'))[0], 'ambiguous')

    def test_ocr_transposition_not_two_independent_substitutions(self):
        self.assertTrue(self.retrieve('zarliv 500mg powder', warehouse('zalriv')))
        self.assertEqual(classify_pair('zarliv 500mg powder', warehouse('zalriv'))[0], 'ambiguous')

    def test_nearby_swapped_letters_and_reordered_tokens(self):
        raw = 'كازمورين بالزركفين'
        candidate = warehouse('كرزفين كازمورين')
        self.assertTrue(self.retrieve(raw, candidate))
        self.assertEqual(classify_pair(raw, candidate)[0], 'ambiguous')

    def test_attached_price_description_is_optional_view(self):
        raw = 'كازمورين سعرجديد'
        self.assertIn('كازمورين', unified_item(raw)['identity_views'])
        self.assertEqual(classify_pair(raw, warehouse('كازمورين'))[0], 'ambiguous')

    def test_all_same_trade_rows_survive_with_raw_request(self):
        finder = FastCandidateFinder()
        finder.fit([{**warehouse(strength=f'{n}mg'), 'id': str(n)} for n in range(1, 15)])
        results = finder.search('BRANDA 14mg powder60ml', top_k=1)
        self.assertEqual(len(results), 14)
        self.assertIn('14', {r['id'] for r in results})

    def test_desktop_coordinator_path_uses_raw_views_without_network(self):
        engine = FastCoordinator(Config('', '', local_api_url='http://127.0.0.1:8001/v1/chat/completions',
                                        local_model='gemini-3.8-flash'))
        with contextlib.redirect_stdout(io.StringIO()), patch.object(engine, '_call_local_api',
                side_effect=AssertionError('Clear raw request must not call LLM')):
            result = engine.process([{'item_name_raw': 'BRANDA500mg powder60ml'}], {'fixture': [warehouse()]})
        self.assertEqual(result['summary']['matched_count'], 1)
        self.assertEqual(result['not_found'], [])

    def test_ambiguous_views_preserve_full_raw_in_provider_payload(self):
        raw = 'velunatrix 500mg powder / secondary description'
        payload = item_payload(raw)
        self.assertEqual(payload['raw_name'], raw)
        self.assertIn('velunatrix', payload['identity_views'])
        self.assertEqual(payload['strength'], '500 mg')
        self.assertEqual(classify_pair(raw, warehouse('velunatrix'))[0], 'ambiguous')


if __name__ == '__main__':
    unittest.main()
