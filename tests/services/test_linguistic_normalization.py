import unittest
from src.services.linguistic_service import LinguisticService

class TestLinguisticNormalization(unittest.TestCase):
    def test_generate_sort_lx_leading_numerals(self):
        # Basic case
        self.assertEqual(LinguisticService.generate_sort_lx("123 apple"), "apple")
        # Leading numeral with punctuation
        self.assertEqual(LinguisticService.generate_sort_lx("(1) banana"), "banana")
        # Multiple leading numerals and spaces
        self.assertEqual(LinguisticService.generate_sort_lx("10 quttaúatues"), "quttauatues")
        # Different leading numerals
        self.assertEqual(LinguisticService.generate_sort_lx("6 quttáuatues"), "quttauatues")
        # Mixed punctuation and numerals
        self.assertEqual(LinguisticService.generate_sort_lx("*-1 orange"), "orange")
        # No change for non-leading numerals
        self.assertEqual(LinguisticService.generate_sort_lx("apple 1"), "apple 1")
        # Empty string
        self.assertEqual(LinguisticService.generate_sort_lx(""), "")
        # None
        self.assertEqual(LinguisticService.generate_sort_lx(None), "")
        # Just numerals and spaces
        self.assertEqual(LinguisticService.generate_sort_lx("123 "), "")

    def test_generate_sort_lx_normalization_remains(self):
        # Ensure it still handles diacritics and quotes
        self.assertEqual(LinguisticService.generate_sort_lx("quttáuatues"), "quttauatues")
        self.assertEqual(LinguisticService.generate_sort_lx("‘fancy’"), "'fancy'")

    def test_generate_sort_lx_special_symbols(self):
        # ∞ alone → oozzz
        self.assertEqual(LinguisticService.generate_sort_lx('∞'), 'oozzz')
        # -∞- → oozzz- (leading punct stripped, trailing kept)
        self.assertEqual(LinguisticService.generate_sort_lx('-∞-'), 'oozzz-')
        # o∞p → ooozzzp (mid-word substitution)
        self.assertEqual(LinguisticService.generate_sort_lx('o∞p'), 'ooozzzp')
        # ✔word → word (check mark stripped)
        self.assertEqual(LinguisticService.generate_sort_lx('✔word'), 'word')
        # Sort order: oo < ∞ < op
        self.assertLess(LinguisticService.generate_sort_lx('oo'), LinguisticService.generate_sort_lx('∞'))
        self.assertLess(LinguisticService.generate_sort_lx('∞'), LinguisticService.generate_sort_lx('op'))
        # Sort order: ooy < ∞ < op
        self.assertLess(LinguisticService.generate_sort_lx('ooy'), LinguisticService.generate_sort_lx('∞'))
        self.assertLess(LinguisticService.generate_sort_lx('∞'), LinguisticService.generate_sort_lx('op'))

if __name__ == '__main__':
    unittest.main()
