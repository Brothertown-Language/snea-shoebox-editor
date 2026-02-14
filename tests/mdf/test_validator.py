# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
from src.mdf.validator import MDFValidator

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
        self.assertTrue(result["valid"])
        
        diagnostics = MDFValidator.diagnose_record(record)
        self.assertEqual(diagnostics[0]["status"], "suggestion")
        self.assertIn("missing suggested tags", diagnostics[0]["message"])

    def test_out_of_order_tags(self):
        record = [
            "\\ps n",
            "\\lx dog",
            "\\ge dog"
        ]
        result = MDFValidator.validate_record(record)
        self.assertTrue(result["valid"])
        
        diagnostics = MDFValidator.diagnose_record(record)
        # Find the out of order tag diagnostic
        out_of_order = next(d for d in diagnostics if d.get("tag") == "lx")
        self.assertEqual(out_of_order["status"], "suggestion")
        self.assertIn("is out of order", out_of_order["message"])

    def test_se_hierarchy_reset(self):
        r"""Tests that \se resets the hierarchy tracking for \ps and \ge."""
        record = [
            "\\lx dog",
            "\\ps n",
            "\\ge dog",
            "\\se puppy",
            "\\ps n",
            "\\ge young dog"
        ]
        diagnostics = MDFValidator.diagnose_record(record)
        # Check that the second \ps and \ge are NOT flagged as out of order
        ps_indices = [i for i, d in enumerate(diagnostics) if d.get("tag") == "ps"]
        ge_indices = [i for i, d in enumerate(diagnostics) if d.get("tag") == "ge"]
        
        self.assertEqual(diagnostics[ps_indices[1]]["status"], "ok")
        self.assertEqual(diagnostics[ge_indices[1]]["status"], "ok")

    def test_sn_hierarchy_reset(self):
        r"""Tests that \sn resets the hierarchy tracking."""
        record = [
            "\\lx record",
            "\\ps n",
            "\\sn 1",
            "\\ge disc",
            "\\sn 2",
            "\\ps v",
            "\\ge to write down"
        ]
        diagnostics = MDFValidator.diagnose_record(record)
        # Find index of the line starting with \ps v
        v_idx = -1
        for i, line in enumerate(record):
            if line.startswith("\\ps v"):
                v_idx = i
                break
        
        self.assertNotEqual(v_idx, -1)
        self.assertEqual(diagnostics[v_idx]["status"], "ok")

if __name__ == "__main__":
    unittest.main()
