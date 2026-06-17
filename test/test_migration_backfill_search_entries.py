import unittest
from pathlib import Path

from src.database.migrations import MigrationManager


class TestMigrationBackfillSearchEntries(unittest.TestCase):
    """Tests for Phase 3: backfill HeadwordSearchEntry and GlossSearchEntry for existing records."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_migration_backfill_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)

            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            # Import core models first (records table needed by FK in search models)
            from src.database.models.core import Language, Record, Source  # noqa: F401
            from src.database.models.identity import User  # noqa: F401

            # Import search models (FTSEntry has FK to records.id, must come after core)
            from src.database.models.search import (  # noqa: F401
                FTSEntry,
                GlossSearchEntry,
                HeadwordSearchEntry,
                SearchEntry,
            )
            from src.database.models.workflow import EditHistory, MatchupQueue  # noqa: F401

            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        # Import MatchupQueue first to satisfy Source's relationship string reference
        from src.database.models.core import Record, Source
        from src.database.models.identity import User
        from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry, SearchEntry
        from src.database.models.workflow import MatchupQueue  # noqa: F401

        self.session = self.Session()
        self.session.query(GlossSearchEntry).delete()
        self.session.query(HeadwordSearchEntry).delete()
        self.session.query(SearchEntry).delete()
        self.session.query(Record).delete()

        if not self.session.query(User).filter_by(email="test@example.com").first():
            self.session.add(User(email="test@example.com", username="tester", github_id=1))

        if not self.session.query(Source).filter_by(name="Test Source").first():
            self.session.add(Source(name="Test Source"))

        self.session.commit()

    def tearDown(self):
        self.session.close()

    def _create_sample_record(self) -> int:
        """Create a sample record and return its id."""
        from src.database.models.core import Record, Source

        source = self.session.query(Source).filter_by(name="Test Source").first()
        record = Record(
            lx="testword",
            ge="a test word",
            mdf_data="\\lx testword\n\\ge a test word\n",
            source_id=source.id,
            updated_by="test@example.com",
        )
        self.session.add(record)
        self.session.commit()
        return record.id

    def test_initial_tables_empty(self):
        """SC-13: Before migration, HeadwordSearchEntry and GlossSearchEntry tables are empty."""
        from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry

        rid = self._create_sample_record()

        hw_count = self.session.query(HeadwordSearchEntry).filter_by(record_id=rid).count()
        gl_count = self.session.query(GlossSearchEntry).filter_by(record_id=rid).count()

        self.assertEqual(hw_count, 0, "HeadwordSearchEntry should be empty before migration")
        self.assertEqual(gl_count, 0, "GlossSearchEntry should be empty before migration")

    def test_migration_populates_tables(self):
        """SC-13: After migration, HeadwordSearchEntry and GlossSearchEntry have entries."""
        from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry

        rid = self._create_sample_record()
        self.session.close()

        mgr = MigrationManager(self.engine)
        mgr._migrate_backfill_search_entries()

        session = self.Session()
        try:
            hw_count = session.query(HeadwordSearchEntry).filter_by(record_id=rid).count()
            gl_count = session.query(GlossSearchEntry).filter_by(record_id=rid).count()

            self.assertGreater(hw_count, 0, "HeadwordSearchEntry should have entries after migration")
            self.assertGreater(gl_count, 0, "GlossSearchEntry should have entries after migration")
        finally:
            session.close()

    def test_rollback_safety(self):
        """SC-13: Dropping new tables does not affect SearchEntry or records data."""
        from sqlalchemy import text

        from src.database.models.core import Record
        from src.database.models.search import SearchEntry

        rid = self._create_sample_record()
        self.session.close()

        mgr = MigrationManager(self.engine)
        mgr._migrate_backfill_search_entries()

        session = self.Session()
        try:
            search_entry_count = session.query(SearchEntry).filter_by(record_id=rid).count()
            self.assertGreater(search_entry_count, 0, "SearchEntry should have entries after migration")

            with self.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS headword_search_entries CASCADE;"))
                conn.execute(text("DROP TABLE IF EXISTS gloss_search_entries CASCADE;"))
                conn.commit()

            record = session.query(Record).filter_by(id=rid).first()
            self.assertIsNotNone(record, "Record should still exist after dropping new tables")
            self.assertEqual(record.lx, "testword", "Record data should be intact after rollback")

            remaining_search = session.query(SearchEntry).filter_by(record_id=rid).count()
            self.assertEqual(
                remaining_search,
                search_entry_count,
                "SearchEntry data should be intact after dropping new tables",
            )
        finally:
            session.close()

    def test_migration_registered(self):
        """Migration version 20260615125509 is registered in _MIGRATIONS."""
        registered = any(v == 20260615125509 for v, _, _ in MigrationManager._MIGRATIONS)
        self.assertTrue(registered, "Migration version 20260615125509 must be registered in _MIGRATIONS")
