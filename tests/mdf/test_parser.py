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
        mdf_text = "\\ge testing\n\\lx test\n\\ps n"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 1)
        self.assertEqual(record['ps'], "n")
        self.assertEqual(record['ge'], "testing")

    def test_parse_mdf_hm(self):
        mdf_text = "\\lx test\n\\hm 3"
        records = parse_mdf(mdf_text)
        record = records[0]
        self.assertEqual(record['lx'], "test")
        self.assertEqual(record['hm'], 3)

if __name__ == '__main__':
    unittest.main()
