"""Retrieval recall/precision fixtures, independent of provider output."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from src.fast_match.search import FastCandidateFinder, name_evidence
from src.fast_match.coordinator import classify_pair, validate_llm_decision

OBSERVED_PAIRS = [
    ('فلوبادكس 8مجم اقراص', 'فلوبادكس ۸ مجم اقراص جديد/ايفا'),
    ('ديوراسيف 250مجم شراب', 'ديوراسيف ٢٥٠ شراب/سكويب'),
    ('فايركتا بلاس 4قرص', 'فايركتابلاس 4قرص/باكت72'),
    ('ديسبركام 20مجم اقراص', 'ديسبركام 20 مج اقراص/المهن'),
    ('ادولور 30مجم 3امبول', 'ادولور ۳۰مج/۲ مللي۳امبول'),
    ('فنتال بخاخ العربية', 'فنتال بخاخ الجديده /العربيه'),
    ('كوفي زنك شامبو', 'كوفى زنك شامبوج'),
]


class RetrievalRecallTests(unittest.TestCase):
    def assert_retrieved(self, requested, candidate):
        finder = FastCandidateFinder()
        finder.fit([{'id': 'real', 'name': candidate}])
        self.assertEqual([c['id'] for c in finder.search(requested)], ['real'])

    def test_seven_observed_pairs(self):
        for requested, candidate in OBSERVED_PAIRS:
            with self.subTest(requested=requested):
                self.assert_retrieved(requested, candidate)
                self.assertNotEqual(classify_pair(requested, candidate)[0], 'review')

    def test_observed_pairs_survive_real_catalog_top_six(self):
        root = Path(__file__).resolve().parents[1] / 'data/processes/PROC-019/cache/vision'
        catalogs = [[r for f in sorted((folder / 'results').glob('page_*.json'))
                     for r in json.loads(f.read_text(encoding='utf-8'))['items']]
                    for folder in sorted(root.iterdir())]
        for requested, candidate in OBSERVED_PAIRS:
            with self.subTest(requested=requested):
                present = [rows for rows in catalogs if any(r['item_name_raw'] == candidate for r in rows)]
                self.assertTrue(present, 'Fixture must exist in immutable Vision cache')
                for rows in present:
                    finder = FastCandidateFinder()
                    finder.fit([{'id': str(i), 'name': r['item_name_raw']} for i, r in enumerate(rows)])
                    self.assertIn(candidate, [c['name'] for c in finder.search(requested)])

    def test_synthetic_deletion_insertion_and_spaces(self):
        for name in ['velunatrix', 'morzaliven', 'فينترالوس', 'كازمورين']:
            for i in range(1, len(name) - 1):
                for variant in [name[:i] + name[i+1:], name[:i] + 'ا' + name[i:], name[:i] + ' ' + name[i:]]:
                    with self.subTest(name=name, variant=variant):
                        self.assert_retrieved(name + ' 5mg syrup', variant + ' 5mg syrup 60ml')

    def test_equivalent_unicode_and_presentation_forms(self):
        for left, right in [('كارديكسين امبول', 'ﻛﺎردﯾﻛﺳﯾن اﻣﺑول'),
                            ('كيزاروفين 8mg', 'کيزاروفين ۸mg'),
                            ('velunatrix 5mg', 'ｖｅｌｕｎａｔｒｉｘ ５ｍｇ')]:
            self.assert_retrieved(left, right)

    def test_ocr_dot_substitution_remains_ambiguous(self):
        left, right = 'سورابتين 5mg', 'شورابتين 5mg'
        self.assert_retrieved(left, right)
        evidence = name_evidence(left, right)
        self.assertLess(evidence.weighted_edits, evidence.edits)
        self.assertEqual(classify_pair(left, right)[0], 'ambiguous')

    def test_contextual_supplier_qualifier_and_form_corruption(self):
        pairs = [('velunatrix 5mg tablets', 'velunatrix 5mg tablets / Novalabs'),
                 ('فينترالوس 5مجم اقراص', 'فينترالوس ٥ مجم اقراص جديد/مصنع تجريبي'),
                 ('كازمورين بخاخ', 'كازمورين بخاخ الجديده'),
                 ('فينترالوس زنك شامبو', 'فينترالوس زنك شامبوج')]
        for left, right in pairs:
            with self.subTest(left=left):
                self.assert_retrieved(left, right)
                self.assertEqual(classify_pair(left, right)[0], 'ambiguous')

    def test_missing_details_and_form_differences_survive(self):
        for left, right in [('بروفين 400mg', 'بروفين'),
                            ('velunatrix 5mg syrup', 'velunatrix'),
                            ('velunatrix 5mg syrup', 'velunatrix 5mg cream')]:
            self.assert_retrieved(left, right)
        self.assertEqual(classify_pair('بروفين 400mg', 'بروفين')[0], 'ambiguous')
        self.assertEqual(classify_pair('بروفين 400mg', 'بروفين 600mg')[0], 'review')


class RetrievalPrecisionTests(unittest.TestCase):
    def test_partial_only_shared_suffix_prefix_and_different_names(self):
        pairs = [('كارديكسين', 'جراميسين'), ('كارديكسين', 'جرامايسين'),
                 ('velunatrix', 'atrix'), ('velunatrix', 'velu'),
                 ('velunatrix', 'kobunatrix'), ('morzaliven', 'xudgaliven'),
                 ('فينترالوس', 'هامكرالوس'), ('alpha medication', 'alpha unrelated')]
        for left, right in pairs:
            with self.subTest(left=left, right=right):
                finder = FastCandidateFinder()
                finder.fit([{'id': 'garbage', 'name': right + ' 5mg syrup / Supplier'}])
                self.assertEqual(finder.search(left + ' 5mg syrup'), [])
                self.assertEqual(sum(finder.last_diagnostics['rejected_reasons'].values()), 1)

    def test_tfidf_cannot_admit_garbage(self):
        finder = FastCandidateFinder()
        finder.fit([{'id': 'garbage', 'name': 'جراميسين 50mg syrup'}])
        import numpy as np
        with patch('src.fast_match.search.cosine_similarity', return_value=np.array([[1.0]])):
            self.assertEqual(finder.search('كارديكسين 50mg syrup'), [])

    def test_token_reordering_requires_correspondence(self):
        self.assertFalse(name_evidence('zal vorem', 'voremzal').plausible)
        self.assertFalse(name_evidence('ون تو ثري', 'توبرين').plausible)
        self.assertTrue(name_evidence('velunatrix zinc', 'zinc velunatri').plausible)

    def test_protected_tail_and_variant_numbers_are_not_dropped(self):
        for tail in ['plus', 'بلس', 'XR', '2']:
            left, right = 'velunatrix syrup', 'velunatrix syrup/' + tail
            self.assertNotEqual(classify_pair(left, right)[0], 'match')
        # Dose fields may be removed from the name, but remain guard evidence.
        self.assertEqual(classify_pair('velunatrix syrup', 'velunatrix syrup/5mg/2ml')[0], 'ambiguous')
        self.assertEqual(classify_pair('Hero Baby 2', 'Hero Baby 1')[0], 'review')
        self.assertFalse(name_evidence('velunatrix', 'unrelated/velunatrix').plausible)

    def test_gate_accounting_and_top_k_are_distinct(self):
        finder = FastCandidateFinder()
        finder.fit([{'id': str(i), 'name': f'velunatrix {i+1}mg syrup'} for i in range(8)] +
                   [{'id': 'bad', 'name': 'xupodrem syrup'}])
        self.assertEqual(len(finder.search('velunatrix syrup')), 8)
        self.assertEqual(finder.last_diagnostics['before_gate'], 9)
        self.assertEqual(finder.last_diagnostics['after_gate'], 8)
        self.assertEqual(sum(finder.last_diagnostics['rejected_reasons'].values()), 1)


class AdjacentGuardFixTests(unittest.TestCase):
    def test_attached_combination_marker(self):
        for name in ['فينترالوس', 'كازمورين']:
            for marker in ['بلاس', 'بلس', 'كومب']:
                with self.subTest(name=name, marker=marker):
                    left, right = f'{name} {marker} 4قرص', f'{name}{marker} 4قرص/باكت72'
                    self.assertEqual(classify_pair(left, right)[0], 'match')
                    self.assertEqual(classify_pair(left, f'{name} 4قرص')[0], 'review')

    def test_total_mass_vs_concentration_is_uncertain_not_conflicting(self):
        for left, right in [('ادولور 30مجم 3امبول', 'ادولور ۳۰مج/۲ مللي۳امبول'),
                            ('velunatrix 30mg ampoules', 'velunatrix 30mg/2ml ampoules'),
                            ('velunatrix 30mg ampoules', 'velunatrix 15mg/ml ampoules')]:
            with self.subTest(left=left):
                self.assertEqual(classify_pair(left, right), ('ambiguous', 'strength_measurement_basis_uncertain'))
                case = {'case_id': 'Q', 'requested_name': left, 'candidates': [{'id': 'W', 'name': right}]}
                self.assertEqual(validate_llm_decision(case, {'case_id': 'Q', 'item_id': 'W', 'status': 'match'})['status'], 'review')

    def test_like_for_like_strength_conflicts_still_block(self):
        for left, right in [('30mg', '15mg'), ('30mg/2ml', '30mg/ml'), ('1%', '2%'),
                            ('30mg 2%', '15mg/ml 1%')]:
            with self.subTest(left=left):
                self.assertEqual(classify_pair('velunatrix ' + left, 'velunatrix ' + right)[0], 'review')


if __name__ == '__main__':
    unittest.main()
