# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
from src.mdf.parser import parse_mdf

class TestMDFParser(unittest.TestCase):
    def test_parse_mdf_basic(self):
        mdf_text = "\\lx test\n\\ps n\n\\ge testing"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 1)
        self.assertEqual(record['ps'], "n")
        self.assertEqual(record['ge'], "testing")

    def test_parse_mdf_extra_space(self):
        mdf_text = "\\lx   test  \n\\ps   n  \n\\ge   testing  "
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 1)
        self.assertEqual(record['ps'], "n")
        self.assertEqual(record['ge'], "testing")

    def test_parse_mdf_missing_fields(self):
        mdf_text = "\\lx test"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 1)
        self.assertEqual(record['ps'], "")
        self.assertEqual(record['ge'], "")

    def test_parse_mdf_order_independence(self):
        # Order independence within the record is fine, but \lx must be first
        mdf_text = "\\lx test\n\\ge testing\n\\ps n"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 1)
        self.assertEqual(record['ps'], "n")
        self.assertEqual(record['ge'], "testing")

    def test_parse_mdf_fatal_before_lx(self):
        mdf_text = "\\sh v3.0\n\\lx test"
        with self.assertRaisesRegex(ValueError, "Content detected before the first \\\\lx marker"):
            parse_mdf(mdf_text)

    def test_parse_mdf_watermark_fatal(self):
        # 3 valid tags (lx, ps, ge), 2 invalid (foo, bar) -> 2/5 = 40% (exceeds 20%)
        mdf_text = "\\lx test\n\\ps n\n\\ge testing\n\\foo bar\n\\bar baz"
        with self.assertRaisesRegex(ValueError, "High volume of unrecognized tags"):
            parse_mdf(mdf_text)

    def test_parse_mdf_indented_lx(self):
        mdf_text = "  \\lx test\n\\ps n"
        records = parse_mdf(mdf_text)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['lx'], "test")

    def test_parse_mdf_multiple_records(self):
        # Records separated by \lx even without blank lines
        mdf_text = "\\lx one\n\\ps n\n\\lx two\n\\ps v"
        records = parse_mdf(mdf_text)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['lx'], "one")
        self.assertEqual(records[1]['lx'], "two")

    def test_parse_mdf_hm(self):
        mdf_text = "\\lx test\n\\hm 3"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 3)

if __name__ == '__main__':
    unittest.main()
