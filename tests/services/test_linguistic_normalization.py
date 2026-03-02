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

if __name__ == '__main__':
    unittest.main()
