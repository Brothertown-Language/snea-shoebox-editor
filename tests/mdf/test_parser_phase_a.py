# Copyright (c) 2026 Brothertown Language
"""Tests for Phase A parser enhancements: record_id, sub-entry fields, normalize_nt_record."""
import os
import unittest

from src.mdf.parser import normalize_nt_record, parse_mdf

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'seed_data', 'natick_sample_100.txt')


class TestRecordIdExtraction(unittest.TestCase):
    """A-1: Extract \\nt Record: <id> tag."""

    def test_record_id_present(self):
        mdf = "\\lx test\n\\ps n\n\\ge thing\n\\nt Record: 42"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['record_id'], 42)

    def test_record_id_absent(self):
        mdf = "\\lx test\n\\ps n\n\\ge thing"
        records = parse_mdf(mdf)
        self.assertIsNone(records[0]['record_id'])

    def test_record_id_with_other_nt(self):
        """\\nt lines that are not Record: should not set record_id."""
        mdf = "\\lx test\n\\nt some remark\n\\nt Record: 99"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['record_id'], 99)

    def test_record_id_only_remark_nt(self):
        mdf = "\\lx test\n\\nt just a remark"
        records = parse_mdf(mdf)
        self.assertIsNone(records[0]['record_id'])

    def test_record_id_with_extra_spaces(self):
        mdf = "\\lx test\n\\nt Record:   7  "
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['record_id'], 7)

    def test_sample_file_no_record_ids(self):
        """The natick sample has no \\nt Record: tags; all should be None."""
        with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        records = parse_mdf(content)
        self.assertTrue(len(records) > 0)
        for rec in records:
            self.assertIsNone(rec['record_id'], f"Unexpected record_id in lx={rec['lx']}")


class TestSubEntryFields(unittest.TestCase):
    """A-2: Extract \\va, \\se, \\cf, \\ve fields as lists."""

    def test_va_extraction(self):
        mdf = "\\lx test\n    \\va variant1\n    \\va variant2"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['va'], ['variant1', 'variant2'])

    def test_se_extraction(self):
        mdf = "\\lx test\n\\se subentry1\n\\se subentry2"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['se'], ['subentry1', 'subentry2'])

    def test_cf_extraction(self):
        mdf = "\\lx test\n\\cf cross1\n\\cf cross2\n\\cf cross3"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['cf'], ['cross1', 'cross2', 'cross3'])

    def test_ve_extraction(self):
        mdf = "\\lx test\n\\se sub\n    \\ve English meaning"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['ve'], ['English meaning'])

    def test_empty_lists_when_absent(self):
        mdf = "\\lx test\n\\ps n"
        records = parse_mdf(mdf)
        self.assertEqual(records[0]['va'], [])
        self.assertEqual(records[0]['se'], [])
        self.assertEqual(records[0]['cf'], [])
        self.assertEqual(records[0]['ve'], [])

    def test_sample_file_has_cf(self):
        """The natick sample contains \\cf fields in some entries."""
        with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        records = parse_mdf(content)
        has_cf = any(rec['cf'] for rec in records)
        self.assertTrue(has_cf, "Expected at least one entry with \\cf")

    def test_sample_file_has_va(self):
        with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        records = parse_mdf(content)
        has_va = any(rec['va'] for rec in records)
        self.assertTrue(has_va, "Expected at least one entry with \\va")


class TestNormalizeNtRecord(unittest.TestCase):
    """A-3: normalize_nt_record function."""

    def test_add_to_entry_without_nt_record(self):
        mdf = "\\lx test\n\\ps n\n\\ge thing"
        result = normalize_nt_record(mdf, 42)
        self.assertIn('\\nt Record: 42', result)
        self.assertEqual(result.count('\\nt Record:'), 1)

    def test_replace_existing_nt_record(self):
        mdf = "\\lx test\n\\nt Record: 10\n\\ps n"
        result = normalize_nt_record(mdf, 99)
        self.assertIn('\\nt Record: 99', result)
        self.assertNotIn('\\nt Record: 10', result)
        self.assertEqual(result.count('\\nt Record:'), 1)

    def test_deduplicate_multiple_nt_records(self):
        mdf = "\\lx test\n\\nt Record: 10\n\\nt Record: 20\n\\ps n"
        result = normalize_nt_record(mdf, 55)
        self.assertIn('\\nt Record: 55', result)
        self.assertEqual(result.count('\\nt Record:'), 1)

    def test_preserves_other_nt_lines(self):
        mdf = "\\lx test\n\\nt some remark\n\\nt Record: 10"
        result = normalize_nt_record(mdf, 42)
        self.assertIn('\\nt some remark', result)
        self.assertIn('\\nt Record: 42', result)
        self.assertNotIn('\\nt Record: 10', result)

    def test_appended_at_end(self):
        mdf = "\\lx test\n\\ps n"
        result = normalize_nt_record(mdf, 1)
        lines = result.split('\n')
        self.assertEqual(lines[-1], '\\nt Record: 1')

    def test_preserves_content(self):
        mdf = "\\lx test\n\\ps n\n\\ge thing"
        result = normalize_nt_record(mdf, 5)
        self.assertIn('\\lx test', result)
        self.assertIn('\\ps n', result)
        self.assertIn('\\ge thing', result)


if __name__ == '__main__':
    unittest.main()
