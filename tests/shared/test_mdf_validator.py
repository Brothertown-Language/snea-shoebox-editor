# Copyright (c) 2026 Brothertown Language
import unittest
from src.shared.mdf_validator import MDFValidator

class TestMDFValidator(unittest.TestCase):
    def test_valid_record(self):
        record = [
            "\\lx dog",
            "\\ps n",
            "\\ge dog"
        ]
        result = MDFValidator.validate_record(record)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_missing_required_tag(self):
        record = [
            "\\lx dog",
            "\\ge dog"
        ]
        result = MDFValidator.validate_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required tag: \\ps", result["errors"])

    def test_out_of_order_tags(self):
        record = [
            "\\ps n",
            "\\lx dog",
            "\\ge dog"
        ]
        result = MDFValidator.validate_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("Tag \\lx found out of order.", result["errors"])

if __name__ == "__main__":
    unittest.main()
