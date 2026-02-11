# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
from src.mdf.parser import format_mdf_record


class TestFormatMdfRecord(unittest.TestCase):

    def test_removes_indentation(self):
        text = "\\lx test\n    \\ps n\n    \\ge thing"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ps n\n\\ge thing")

    def test_blank_line_before_se(self):
        text = "\\lx test\n\\ps n\n\\se subentry\n\\ps v"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ps n\n\n\\se subentry\n\\ps v")

    def test_blank_line_before_nt_record(self):
        text = "\\lx test\n\\ps n\n\\nt Record: 42"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ps n\n\n\\nt Record: 42")

    def test_no_blank_before_se_if_first_line(self):
        text = "\\se subentry\n\\ps v"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\se subentry\n\\ps v")

    def test_removes_extra_blank_lines(self):
        text = "\\lx test\n\n\n\\ps n\n\n\\ge thing"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ps n\n\\ge thing")

    def test_multiple_subentries_get_blank_lines(self):
        text = "\\lx test\n\\ge main\n\\se sub1\n\\ps n\n\\se sub2\n\\ps v"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ge main\n\n\\se sub1\n\\ps n\n\n\\se sub2\n\\ps v")

    def test_indented_se_gets_blank_line(self):
        text = "\\lx test\n\\ge main\n    \\se sub1\n    \\ps n"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ge main\n\n\\se sub1\n\\ps n")

    def test_nt_record_and_se_together(self):
        text = "\\lx test\n\\se sub1\n\\ps n\n\\nt Record: 5"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\n\\se sub1\n\\ps n\n\n\\nt Record: 5")

    def test_regular_nt_no_blank_line(self):
        text = "\\lx test\n\\nt some note\n\\ps n"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\nt some note\n\\ps n")

    def test_already_has_blank_before_se_no_double(self):
        text = "\\lx test\n\\ge main\n\n\\se sub1"
        result = format_mdf_record(text)
        self.assertEqual(result, "\\lx test\n\\ge main\n\n\\se sub1")

    def test_complex_record_with_indents(self):
        text = (
            "\\lx adchau\n"
            "\\ps v.i. / AI\n"
            "\\ge he hunts\n"
            "    \\se adchaonk\n"
            "    \\ps Vbl. n.\n"
            "    \\ge hunting\n"
            "    \\se adchaen\n"
            "    \\ps N.agent\n"
            "\\nt Record: 99"
        )
        expected = (
            "\\lx adchau\n"
            "\\ps v.i. / AI\n"
            "\\ge he hunts\n"
            "\n"
            "\\se adchaonk\n"
            "\\ps Vbl. n.\n"
            "\\ge hunting\n"
            "\n"
            "\\se adchaen\n"
            "\\ps N.agent\n"
            "\n"
            "\\nt Record: 99"
        )
        result = format_mdf_record(text)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
