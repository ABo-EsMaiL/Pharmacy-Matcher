"""Conservative structured-field spelling normalization, synthetic only."""
import unittest

from src.fast_match.attributes import structured_scalar
from src.fast_match.search import unified_item, FastCandidateFinder, item_payload
from src.fast_match.coordinator import classify_pair, validate_llm_decision


def item(strength=None, **extra):
    return {'id': 'W', 'item_name_raw': 'BRANDA', 'trade_name': 'BRANDA',
            'strength': strength, 'form': 'tablet', **extra}


class StructuredAttributeNormalizationTests(unittest.TestCase):
    def test_formatting_only_variants_share_internal_strength(self):
        for value in [500, 500.0, '500', '500.00', '٥٠٠', '۵۰۰', '500 mg',
                      '500مجم', '٥٠٠ مجم', '۵۰۰،۰mg']:
            with self.subTest(value=value):
                parsed = unified_item(item(value))
                self.assertEqual(parsed['_strength_values'], ('500',))
                self.assertEqual(parsed['extracted_fields']['strength'], value)
                self.assertEqual(classify_pair(item(value), item('500mg'))[0], 'match')

    def test_decimal_dots_commas_and_arabic_digits(self):
        for value in ['12.5', '۱۲،۵', '١٢٫٥', '12,50mg', '۱۲.۵ مجم']:
            self.assertEqual(classify_pair(item(value), item('12.5mg'))[0], 'match')

    def test_scalar_unit_is_not_invented(self):
        self.assertEqual(structured_scalar('۵۰۰'), ('500', ''))
        self.assertEqual(structured_scalar('٥٠٠ مجم'), ('500', 'mg'))
        self.assertEqual(structured_scalar('٥٠٠ مل'), ('500', 'ml'))
        self.assertIsNone(structured_scalar('30mg/2ml'))

    def test_explicit_strength_difference_is_review(self):
        for a, b in [('500mg', '250mg'), (500, '250mg'), ('500', '250')]:
            self.assertEqual(classify_pair(item(a), item(b))[0], 'review')

    def test_mg_vs_ml_is_review_even_with_same_number(self):
        for a, b in [('500mg', '500ml'), ('500', '500ml')]:
            self.assertEqual(classify_pair(item(a), item(b))[0], 'review')

    def test_volume_in_strength_field_is_not_automatically_a_package_match(self):
        self.assertEqual(classify_pair(item('60ml'), item('120ml'))[0], 'review')
        self.assertIn('structured_strength_contains_volume', unified_item(item('60ml'))['attribute_warnings'])

    def test_explicit_volume_attribute_preserves_difference(self):
        a, b = item(volume='60 ml'), item(volume='120 مل')
        self.assertEqual(classify_pair(a, b), ('review', 'structured_volume_difference'))
        self.assertEqual(item_payload(a)['volume'], '60 ml')
        f = FastCandidateFinder()
        f.fit([b])
        self.assertTrue(f.search(a))

    def test_volume_formatting_does_not_create_a_difference(self):
        self.assertEqual(classify_pair(item(volume='٦٠مل'), item(volume='60.0 ml'))[0], 'match')

    def test_missing_or_untrusted_volume_stays_review(self):
        for a, b in [(item(volume='60ml'), item()),
                     (item(volume=60), item(volume='60ml')),
                     (item(volume='unclear'), item(volume='60ml'))]:
            self.assertEqual(classify_pair(a, b)[0], 'review')

    def test_mass_and_concentration_remain_uncertain_then_final_review(self):
        a, b = item('30mg'), item('30mg/2ml')
        self.assertEqual(classify_pair(a, b), ('ambiguous', 'strength_measurement_basis_uncertain'))
        case = {'case_id': 'Q', 'requested_name': a['item_name_raw'], 'requested_item': a, 'candidates': [b]}
        decision = {'case_id': 'Q', 'item_id': 'W', 'status': 'match', 'identity_same': True}
        self.assertEqual(validate_llm_decision(case, decision)['status'], 'review')

    def test_missing_unit_does_not_authorize_gram_or_concentration_inference(self):
        for value in ['0.5g', '500g', '500mcg', '500%']:
            self.assertEqual(classify_pair(item('500'), item(value))[0], 'review')
        raw = {'item_name_raw': 'BRANDA 0.5g tablet'}
        self.assertEqual(classify_pair(item('500'), raw)[0], 'review')

    def test_raw_unitless_numbers_are_not_strength_fields(self):
        parsed = unified_item('BRANDA 500')
        self.assertEqual(parsed['_strength_values'], ())
        self.assertIn('500', parsed['trade_name'])

    def test_raw_pack_volume_does_not_get_new_semantics(self):
        a = item('500mg', form='syrup', item_name_raw='BRANDA 500mg syrup30ml')
        b = item('500mg', form='syrup', item_name_raw='BRANDA 500mg syrup60ml')
        self.assertEqual(classify_pair(a, b)[0], 'match')

    def test_untrusted_structured_field_stays_review(self):
        for a in [item('unknown notation'), item('500', item_name_raw='BRANDA 250mg tablet')]:
            self.assertEqual(classify_pair(a, item('500mg'))[0], 'review')


if __name__ == '__main__':
    unittest.main()
