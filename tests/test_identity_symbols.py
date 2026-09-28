"""Synthetic-only regressions for language-level identity hypotheses."""
import unittest

from src.fast_match.search import FastCandidateFinder, unified_item, name_evidence
from src.fast_match.coordinator import classify_pair, validate_llm_decision
from src.fast_match.identity_symbols import symbolic_identity_views


def candidate(name, **fields):
    return {'id': 'W', 'item_name_raw': name, 'trade_name': name, **fields}


class SymbolicIdentityTests(unittest.TestCase):
    def assert_candidate(self, request, name):
        finder = FastCandidateFinder()
        row = candidate(name)
        finder.fit([row])
        self.assertIn('W', {c['id'] for c in finder.search(request)})
        self.assertEqual(classify_pair(request, row)[0], 'ambiguous')
        self.assertFalse(name_evidence(request, row).exact)

    def test_attached_and_spaced_latin_code(self):
        self.assert_candidate('BRANDA-D3', 'BRANDA D 3')

    def test_latin_arabic_letter_code(self):
        for left, right in [('BRANDA K2', 'BRANDA كي 2'),
                            ('BRANDA D3', 'BRANDA دي 3'),
                            ('BRANDA B6', 'BRANDA بي سكس')]:
            with self.subTest(left=left):
                self.assert_candidate(left, right)
                self.assert_candidate(right, left)

    def test_spoken_numbers(self):
        for digit, word in [('3', 'ثري'), ('2', 'تو'), ('7', 'سبعه'), ('9', 'nine')]:
            with self.subTest(word=word):
                self.assert_candidate('BRANDA ' + digit, 'BRANDA ' + word)

    def test_arabic_attached_codes(self):
        for name in ['BRANDA دي3', 'BRANDA دي 3', 'BRANDA دي ثري']:
            self.assert_candidate(name, 'BRANDA D 3')

    def test_persian_digits_and_presentation_forms(self):
        self.assert_candidate('BRANDA كي۲', 'BRANDA K 2')
        self.assert_candidate('BRANDA ﺩﻱ ثري', 'BRANDA D 3')

    def test_descriptor_and_package_removed_only_in_hypothesis(self):
        raw = 'ZORVENA دي ثري4000ميكروفيلم'
        row = {'id': 'W', 'item_name_raw': 'ZORVENA د 3 4000 لزقة باكت 200',
               'trade_name': 'ZORVENA د 3', 'strength': '4000', 'form': 'لزقة'}
        finder = FastCandidateFinder()
        finder.fit([row])
        self.assertIn('W', {r['id'] for r in finder.search(raw)})
        self.assertEqual(classify_pair(raw, row)[0], 'ambiguous')
        self.assertEqual(unified_item(raw)['raw_name'], raw)
        self.assertIn('ميكروفيلم', unified_item(raw)['trade_name'])
        self.assertEqual(unified_item(row)['extracted_fields']['strength'], '4000')

    def test_extra_spoken_letters_remain_uncertain(self):
        self.assert_candidate('كازمورين دي3+كي2 نقط', 'كازمورين في اي دي ثري كيه')

    def test_new_descriptor_without_code_is_also_only_a_hypothesis(self):
        for word in ['ميكروفيلم', 'لزقة', 'microfilm', 'patch']:
            self.assert_candidate('BRANDA ' + word, 'BRANDA')

    def test_different_names_cannot_match_on_codes(self):
        for left, right in [('velunatrix D3', 'atrix دي ثري'),
                            ('velunatrix K2', 'velu كي تو'),
                            ('velunatrix D3', 'kobunatrix دي ثري'),
                            ('BRANDA D3', 'OTHERBRAND دي ثري'),
                            ('alpha unrelated D3', 'alpha medication دي ثري')]:
            with self.subTest(left=left):
                f = FastCandidateFinder()
                f.fit([candidate(right)])
                self.assertEqual(f.search(left), [])

    def test_code_only_has_no_product_name_anchor(self):
        for text in ['D3 K2', 'دي ثري كي تو', '3 2']:
            self.assertEqual(symbolic_identity_views(text, frozenset()), ())

    def test_no_substring_rewriting_inside_brand(self):
        view = symbolic_identity_views('threeliven twomora D3', frozenset())[0]
        self.assertEqual(view.anchor, 'threeliven twomora')
        self.assertIn('threeliven twomora', view.identity)

    def test_numeric_variants_are_not_erased_from_hypothesis(self):
        a = symbolic_identity_views('BRANDA ثري', frozenset())[0]
        b = symbolic_identity_views('BRANDA تو', frozenset())[0]
        self.assertEqual(a.identity, 'branda 3')
        self.assertEqual(b.identity, 'branda 2')
        self.assertNotEqual(a.identity, b.identity)
        self.assertNotEqual(classify_pair('BRANDA 3', candidate('BRANDA تو'))[0], 'match')

    def test_original_attributes_are_not_converted(self):
        parsed = unified_item('BRANDA دي ثري 500mg powder60ml')
        self.assertEqual(parsed['_strength_values'], ('500',))
        self.assertIn('ثري', parsed['trade_name'])
        self.assertEqual(parsed['_forms'], ('powder',))

    def test_python_strength_guard_still_overrides_llm(self):
        request = {'item_name_raw': 'BRANDA D3 500mg tablet', 'trade_name': 'BRANDA D3',
                   'strength': '500mg', 'form': 'tablet'}
        row = {'id': 'W', 'item_name_raw': 'BRANDA دي ثري 250mg tablet',
               'trade_name': 'BRANDA دي ثري', 'strength': '250mg', 'form': 'tablet'}
        case = {'case_id': 'Q', 'requested_name': request['item_name_raw'],
                'requested_item': request, 'candidates': [row]}
        result = validate_llm_decision(case, {'case_id': 'Q', 'item_id': 'W',
                                             'status': 'match', 'identity_same': True})
        self.assertEqual(result['status'], 'review')

    def test_secondary_slash_text_is_not_alias(self):
        f = FastCandidateFinder()
        f.fit([candidate('BRANDA D3')])
        self.assertEqual(f.search('OTHERBRAND / BRANDA دي ثري'), [])


if __name__ == '__main__':
    unittest.main()
