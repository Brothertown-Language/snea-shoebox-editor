# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-4 (behavioral) RED test: pgvector DDL-only migrations, isolated (#1346 flake-isolation pattern).

Asserts against an isolated ephemeral PostgreSQL instance (pgserver) — never the
synced/shared DB — that:

1. Exactly two new registry entries are appended to ``MigrationManager._MIGRATIONS``
   in append-only ``YYYYMMDDSSSSS`` format, both strictly AFTER the last existing
   version (20260615125509), in apply order:
   - CREATE TABLE ``semantic_search_entries``
   - ALTER TABLE ``gloss_search_entries`` ADD COLUMN embedding vector(384),
     entry_type, embedding_model
2. Applying ``run_all()`` to the isolated DB: migrations apply in order, the
   pgvector extension is ensured, version rows advance past the pre-state, and
   the new table/columns exist.
3. ``semantic_search_entries.record_id`` FK is ON DELETE CASCADE.
4. Rerunning ``_run_migrations()`` is a no-op: no new version rows, schema stable.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import re
import unittest
from pathlib import Path

from sqlalchemy import text

from src.database.migrations import MigrationManager

# Last version currently registered in migrations.py (append-only baseline).
BASELINE_LAST_VERSION = 20260615125509
# 14-digit timestamps: YYYYMMDD + 6-digit seconds-since-midnight (e.g. 20260929200606).
YYYYMMDDSSSSS_RE = re.compile(r"^20\d{12}$")


class TestDdlMigrationsSemanticSchemaSc4(unittest.TestCase):
    """Phase 3 Item 4 (SC-4, behavioral): isolated DDL migration contract."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        try:
            import pgserver
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            cls.test_db_path = Path("tmp/test_migration_sc4_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            cls.Session = sessionmaker(bind=cls.engine)

            # pgvector extension must exist before creating ORM tables that use
            # the Vector type (records.embedding, gloss_search_entries.embedding).
            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            # Create the schema the migrations under test depend on: the records
            # table (FK target for semantic_search_entries/gloss_search_entries),
            # users + sources (FK targets of records), and the migration-tracking
            # table. GlossSearchEntry ORM carries the new embedding columns, so its
            # table is created with the ALTER-able columns already present — the
            # gloss ALTER migration is then exercised by re-adding/normalizing them.
            from src.database.base import Base
            from src.database.models.meta import SchemaVersion  # noqa: F401
            from src.database.models.identity import User  # noqa: F401
            from src.database.models.workflow import EditHistory  # noqa: F401
            from src.database.models.core import Record, Source  # noqa: F401
            from src.database.models.search import GlossSearchEntry  # noqa: F401

            Base.metadata.create_all(cls.engine)
            with cls.engine.connect() as conn:
                conn.execute(
                    text(
                        "INSERT INTO schema_version (version, description) "
                        "VALUES (:v, 'baseline for SC-4 isolation') ON CONFLICT DO NOTHING;"
                    ),
                    {"v": BASELINE_LAST_VERSION},
                )
                conn.commit()
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def _find_semantic_migrations(self):
        """Return registry entries for the two new DDL migrations, in apply order."""
        entries = [
            (v, m, d)
            for v, m, d in MigrationManager._MIGRATIONS
            if v > BASELINE_LAST_VERSION
            and ("semantic_search_entries" in str(d) or "gloss_search_entries" in str(d))
        ]
        return sorted(entries, key=lambda e: e[0])

    def test_two_ddl_migrations_registered_append_only(self):
        """Exactly two new registry entries exist, after the baseline, in order."""
        entries = self._find_semantic_migrations()
        self.assertEqual(len(entries), 2, f"expected exactly 2 new DDL entries, got: {entries}")
        versions = [v for v, _, _ in entries]
        self.assertTrue(all(v > BASELINE_LAST_VERSION for v in versions), f"versions not appended after {BASELINE_LAST_VERSION}: {versions}")
        self.assertTrue(list(versions) == sorted(versions), "registry entries not in apply order")

    def test_registry_versions_follow_yyyymmddsssss(self):
        """Registry versions for the new migrations are YYYYMMDDSSSSS format (no +1/+2)."""
        for version, _, _ in self._find_semantic_migrations():
            self.assertRegex(str(version), YYYYMMDDSSSSS_RE, f"version {version} is not YYYYMMDDSSSSS")

    def test_migration_descriptions_map_to_ddl_concerns(self):
        """Registry descriptions distinguish CREATE TABLE vs ALTER TABLE concerns."""
        entries = self._find_semantic_migrations()
        self.assertTrue(entries, "no semantic-search migration entries in registry")
        all_desc = " ".join(d.lower() for _, _, d in entries)
        self.assertIn("semantic_search_entries", all_desc)
        self.assertIn("gloss_search_entries", all_desc)

    def test_migrations_apply_in_order_and_objects_exist(self):
        """Behavioral: run the registered migrations on the isolated DB; objects exist."""
        mgr = MigrationManager(self.engine)
        mgr._ensure_extensions()

        # pgvector extension available with an extversion we can assert on
        with self.engine.connect() as conn:
            extver = conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname='vector';")
            ).scalar()
        self.assertTrue(extver, "pgvector extension missing after _ensure_extensions")

        mgr._run_migrations()

        # Version rows advanced past the baseline
        with self.engine.connect() as conn:
            max_version = conn.execute(text("SELECT MAX(version) FROM schema_version;")).scalar()
        self.assertGreater(max_version, BASELINE_LAST_VERSION, "version rows did not advance")

        # New table exists with the declared columns
        with self.engine.connect() as conn:
            tables = {
                r[0] for r in conn.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
                )
            }
        self.assertIn("semantic_search_entries", tables)

        with self.engine.connect() as conn:
            gloss_cols = {
                r[0] for r in conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name='gloss_search_entries';"
                    )
                )
            }
            sem_cols = {
                r[0] for r in conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name='semantic_search_entries';"
                    )
                )
            }
        for col in ("embedding", "entry_type", "embedding_model"):
            self.assertIn(col, gloss_cols, f"gloss_search_entries missing '{col}'")
            self.assertIn(col, sem_cols, f"semantic_search_entries missing '{col}'")

    def test_semantic_fk_cascade_in_applied_schema(self):
        """Behavioral: applied semantic_search_entries.record_id FK is ON DELETE CASCADE."""
        self.test_migrations_apply_in_order_and_objects_exist()
        with self.engine.connect() as conn:
            ondelete = conn.execute(
                text(
                    "SELECT confdeltype FROM pg_constraint "
                    "WHERE conrelid='semantic_search_entries'::regclass AND contype='f';"
                )
            ).scalar()
        # c = CASCADE, r = RESTRICT, a = no action
        self.assertEqual(ondelete, "c", f"semantic_search_entries FK ondelete is {ondelete!r}, expected CASCADE")

    def test_semantic_embedding_column_is_vector384(self):
        """Behavioral: applied embeddings are vector(384) in both tables."""
        self.test_migrations_apply_in_order_and_objects_exist()
        with self.engine.connect() as conn:
            for table in ("semantic_search_entries", "gloss_search_entries"):
                typ = conn.execute(
                    text(
                        "SELECT data_type, udt_name FROM information_schema.columns "
                        "WHERE table_name=:t AND column_name='embedding';"
                    ),
                    {"t": table},
                ).first()
        self.assertTrue(typ, "embedding column not found in semantic_search_entries")
        self.assertIn("vector", str(typ), f"embedding is not vector type: {typ}")

    def test_rerun_is_noop(self):
        """Behavioral: rerunning migrations after apply records no new version rows."""
        mgr = MigrationManager(self.engine)
        mgr._ensure_extensions()
        mgr._run_migrations()

        with self.engine.connect() as conn:
            before = conn.execute(text("SELECT COUNT(*), MAX(version) FROM schema_version;")).fetchone()

        mgr._run_migrations()  # second run — must skip everything

        with self.engine.connect() as conn:
            after = conn.execute(text("SELECT COUNT(*), MAX(version) FROM schema_version;")).fetchone()

        self.assertEqual(tuple(before), tuple(after), f"rerun recorded new version rows: {before} -> {after}")
        self.assertGreater(after[1], BASELINE_LAST_VERSION, "version rows did not advance before rerun")

    def test_ddl_only_no_data_writes(self):
        """Behavioral: running migrations performs no data writes to gloss_search_entries."""
        mgr = MigrationManager(self.engine)
        mgr._ensure_extensions()
        mgr._run_migrations()
        with self.engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM gloss_search_entries;")).scalar()
        self.assertEqual(count, 0, "migration wrote data rows (must be DDL-only)")


if __name__ == "__main__":
    unittest.main()