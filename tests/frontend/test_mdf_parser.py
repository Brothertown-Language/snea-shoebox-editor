# Copyright (c) 2026 Brothertown Language
import unittest
from src.frontend.app import parse_mdf

class TestMDFParser(unittest.TestCase):
    def test_parse_mdf_basic(self):
        mdf_text = "\\lx test\n\\ps n\n\\ge testing"
        lx, hm, ps, ge = parse_mdf(mdf_text)
        self.assertEqual(lx, "test")
        self.assertEqual(hm, 1)
        self.assertEqual(ps, "n")
        self.assertEqual(ge, "testing")

    def test_parse_mdf_extra_space(self):
        mdf_text = "\\lx   test  \n\\ps   n  \n\\ge   testing  "
        lx, hm, ps, ge = parse_mdf(mdf_text)
        self.assertEqual(lx, "test")
        self.assertEqual(hm, 1)
        self.assertEqual(ps, "n")
        self.assertEqual(ge, "testing")

    def test_parse_mdf_missing_fields(self):
        mdf_text = "\\lx test"
        lx, hm, ps, ge = parse_mdf(mdf_text)
        self.assertEqual(lx, "test")
        self.assertEqual(hm, 1)
        self.assertEqual(ps, "")
        self.assertEqual(ge, "")

    def test_parse_mdf_order_independence(self):
        mdf_text = "\\ge testing\n\\lx test\n\\ps n"
        lx, hm, ps, ge = parse_mdf(mdf_text)
        self.assertEqual(lx, "test")
        self.assertEqual(hm, 1)
        self.assertEqual(ps, "n")
        self.assertEqual(ge, "testing")

    def test_parse_mdf_hm(self):
        mdf_text = "\\lx test\n\\hm 3"
        lx, hm, ps, ge = parse_mdf(mdf_text)
        self.assertEqual(lx, "test")
        self.assertEqual(hm, 3)

if __name__ == '__main__':
    unittest.main()
