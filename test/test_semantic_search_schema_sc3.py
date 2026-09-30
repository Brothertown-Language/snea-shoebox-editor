# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-3 (structural) RED test: semantic search schema and ORM declarations must exist.

Asserts against the synced local DB (`src.database.connection.get_db_url()`):

1. ``gloss_search_entries`` gains exactly 3 new columns:
   ``embedding`` (pgvector vector, 384 dims), ``entry_type``, ``embedding_model``.
2. A new table ``semantic_search_entries`` exists with columns:
   ``record_id`` (FK to records.id, ON DELETE CASCADE), ``entry_type``, ``term``,
   ``embedding`` (vector 384), ``embedding_model``.
3. ORM declarations exist: ``src/database/models/search.py`` defines
   ``SemanticSearchEntry`` and gloss_search_entries ORM carries the 3 new columns.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import unittest

from sqlalchemy import create_engine, inspect

from src.database.connection import get_db_url


class TestSemanticSearchSchemaSc3(unittest.TestCase):
    """Phase 3 Item 3 (SC-3, structural): semantic search schema introspection."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        # Register the pgvector SQLAlchemy type so the inspector resolves the
        # `embedding` column type instead of reporting NULL.
        import src.database.models.search  # noqa: F401

        cls.engine = create_engine(get_db_url())
        cls.inspector = inspect(cls.engine)
        cls.tables = set(cls.inspector.get_table_names())

    def test_gloss_search_entries_has_three_new_columns(self):
        cols = {c["name"]: c for c in self.inspector.get_columns("gloss_search_entries")}
        for col in ("embedding", "entry_type", "embedding_model"):
            self.assertIn(col, cols, f"gloss_search_entries missing '{col}' column")

    def test_gloss_search_entries_embedding_is_vector384(self):
        cols = {c["name"]: c for c in self.inspector.get_columns("gloss_search_entries")}
        self.assertIn("embedding", cols)
        col_type = str(cols["embedding"]["type"]).lower()
        self.assertIn("vector", col_type)
        self.assertIn("384", col_type.replace(" ", ""), f"embedding type not vector(384): {col_type}")

    def test_semantic_search_entries_table_exists(self):
        self.assertIn("semantic_search_entries", self.tables)

    def test_semantic_search_entries_columns(self):
        self.assertIn("semantic_search_entries", self.tables)
        cols = {c["name"]: c for c in self.inspector.get_columns("semantic_search_entries")}
        for col in ("record_id", "entry_type", "term", "embedding", "embedding_model"):
            self.assertIn(col, cols, f"semantic_search_entries missing '{col}' column")

    def test_semantic_search_entries_embedding_is_vector384(self):
        self.assertIn("semantic_search_entries", self.tables)
        cols = {c["name"]: c for c in self.inspector.get_columns("semantic_search_entries")}
        self.assertIn("embedding", cols)
        col_type = str(cols["embedding"]["type"]).lower()
        self.assertIn("vector", col_type)
        self.assertIn("384", col_type.replace(" ", ""), f"embedding type not vector(384): {col_type}")

    def test_semantic_search_entries_record_id_cascades_on_delete(self):
        self.assertIn("semantic_search_entries", self.tables)
        fks = self.inspector.get_foreign_keys("semantic_search_entries")
        record_fk = [
            fk for fk in fks
            if fk.get("referred_table") == "records"
            and "record_id" in (fk.get("constrained_columns") or [])
        ]
        self.assertTrue(record_fk, "semantic_search_entries.record_id FK to records missing")
        self.assertEqual(((record_fk[0].get("options") or {}).get("ondelete") or record_fk[0].get("ondelete") or "").upper(), "CASCADE")

    def test_orm_semantic_search_entry_declared(self):
        from src.database.models import search as search_models  # noqa: PLC0415

        self.assertTrue(hasattr(search_models, "SemanticSearchEntry"))
        cls_ = search_models.SemanticSearchEntry
        self.assertEqual(cls_.__tablename__, "semantic_search_entries")

    def test_orm_gloss_search_entry_has_new_columns(self):
        from src.database.models import search as search_models  # noqa: PLC0415

        gloss = search_models.GlossSearchEntry
        for col in ("embedding", "entry_type", "embedding_model"):
            self.assertTrue(hasattr(gloss, col), f"GlossSearchEntry ORM missing '{col}'")


if __name__ == "__main__":
    unittest.main()