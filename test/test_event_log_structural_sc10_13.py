# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Structural tests for issue #1332 — SC-10, SC-11, SC-12, SC-13.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import ast
import unittest
from pathlib import Path

MODELS_INIT = Path("src/database/models/__init__.py")
CONNECTION = Path("src/database/connection.py")
MIGRATIONS = Path("src/database/migrations.py")
EVENT_LOG_MODEL = Path("src/database/models/event_log.py")
# Last version registered before the #1332 migration was appended (baseline).
PREVIOUS_LAST_VERSION = 20260929200607


class TestStructuralSc10ToSc13(unittest.TestCase):
    def test_sc10_models_init_has_no_imports_or_reexports(self):
        """SC-10: src/database/models/__init__.py remains CONVENTION-comment only."""
        tree = ast.parse(MODELS_INIT.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, (ast.Import, ast.ImportFrom), f"import found: {ast.dump(node)[:80]}")
            self.assertNotIsInstance(node, ast.Assign, f"re-export assignment found: {ast.dump(node)[:80]}")

    def test_sc11_system_event_log_registered_in_init_db(self):
        """SC-11: SystemEventLog imported inside init_db() in connection.py."""
        source = CONNECTION.read_text(encoding="utf-8")
        init_body = source.split("def init_db():", 1)[1]
        self.assertIn("from .models.event_log import SystemEventLog", init_body)

    def test_sc12_new_migration_entry_complies_with_directive(self):
        """SC-12: YYYYMMDDSSSSS actual-time value > 20260929200607; no renumbering."""
        tree = ast.parse(MIGRATIONS.read_text(encoding="utf-8"))
        registry = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "_MIGRATIONS":
                registry = node.value
        self.assertIsNotNone(registry)
        versions = [elt.elts[0].value for elt in registry.elts if isinstance(elt, ast.Tuple)]
        self.assertEqual(len(versions), len(set(versions)), "duplicate versions in registry")
        new_entries = [v for v in versions if v > PREVIOUS_LAST_VERSION]
        self.assertEqual(len(new_entries), 1, f"expected exactly one new entry: {new_entries}")
        new_version = new_entries[0]
        self.assertTrue(str(new_version).startswith("20261005"), f"not an actual-time 2026-10-05 value: {new_version}")
        self.assertEqual(len(str(new_version)), 14)
        # No existing entries renumbered: all pre-change versions still present.
        self.assertIn(PREVIOUS_LAST_VERSION, versions)

    def test_sc13_no_backfill_distinct_table(self):
        """SC-13: no backfill logic; system_event_log distinct from user_activity_log."""
        model_source = EVENT_LOG_MODEL.read_text(encoding="utf-8")
        self.assertIn('__tablename__ = "system_event_log"', model_source)
        self.assertNotIn('__tablename__ = "user_activity_log"', model_source)
        tree = ast.parse(model_source)
        fk_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and getattr(node.func, "id", None) == "Column"
            and any(isinstance(arg, ast.Call) and getattr(arg.func, "id", None) == "ForeignKey" for arg in node.args)
        )
        self.assertEqual(fk_count, 0, "SystemEventLog must carry no FK (REQ-10)")
        # No backfill: migrations.py must not read pre-existing migration history
        # into system_event_log (the only writes come from live lifecycle calls).
        migrations_source = MIGRATIONS.read_text(encoding="utf-8")
        self.assertNotIn("system_event_log", migrations_source.split("_log_migration_event")[0])


if __name__ == "__main__":
    unittest.main()
