import unittest
from pathlib import Path

from src.services.upload_service import UploadService


class TestUploadSearchEntriesRED(unittest.TestCase):
    """RED-phase tests for Phase 2: headword-block state for search entry population."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_upload_search_entries_red_db")
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

            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        from src.database.models.core import Language, Record, Source
        from src.database.models.identity import User
        from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry, SearchEntry

        self.session = self.Session()
        self.session.query(GlossSearchEntry).delete()
        self.session.query(HeadwordSearchEntry).delete()
        self.session.query(SearchEntry).delete()
        self.session.query(Record).delete()

        if not self.session.query(User).filter_by(email="test@example.com").first():
            self.session.add(User(email="test@example.com", username="tester", github_id=1))
        if not self.session.query(Source).filter_by(name="Test Source").first():
            self.session.add(Source(name="Test Source"))
        if not self.session.query(Language).filter_by(code="alg").first():
            self.session.add(Language(code="alg", name="Algonquian"))
        self.session.commit()
        self.source_id = self.session.query(Source).filter_by(name="Test Source").first().id

    def tearDown(self):
        self.session.close()

    def _add_and_populate(self, mdf_data):
        from src.database.models.core import Record

        rec = Record(lx="entry", source_id=self.source_id, mdf_data=mdf_data)
        self.session.add(rec)
        self.session.commit()
        UploadService.populate_search_entries([rec.id], session=self.session)
        return rec

    # --- Item 2.1: HeadwordSearchEntry uses primary_va (SC-3) ---
    def test_headword_va_excludes_nested_va(self):
        """SC-3: HeadwordSearchEntry va must use primary_va, excluding nested va values."""
        from src.database.models.search import HeadwordSearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw" "\n"
            r"\va wampu-" "\n"
            r"\ge round object" "\n"
            r"\se wampuw-" "\n"
            r"  \va wampum"
        )
        entries = self.session.query(HeadwordSearchEntry).filter_by(record_id=rec.id).all()
        terms = [e.term for e in entries]
        self.assertIn("wampu-", terms, "Primary headword va should be in HeadwordSearchEntry")
        self.assertNotIn("wampum", terms, "Nested subentry va must NOT be in HeadwordSearchEntry")

    # --- Item 2.2: GlossSearchEntry uses in_headword_block state (SC-5, SC-23) ---
    def test_gloss_ge_excludes_nested_ge(self):
        """SC-5, SC-23: GlossSearchEntry ge must use headword-block ge, excluding nested ge values."""
        from src.database.models.search import GlossSearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw" "\n"
            r"\ge ball" "\n"
            r"\se wampuw-" "\n"
            r"  \ge sphere"
        )
        entries = self.session.query(GlossSearchEntry).filter_by(record_id=rec.id).all()
        terms = [e.term for e in entries]
        self.assertIn("ball", terms, "Primary headword ge should be in GlossSearchEntry")
        self.assertNotIn("sphere", terms, "Nested subentry ge must NOT be in GlossSearchEntry")

    # --- Item 2.3: Skip records missing \lx for HeadwordSearchEntry (SC-26) ---
    def test_no_lx_no_headword_entry(self):
        """SC-26: Record without lx must not create HeadwordSearchEntry."""
        from src.database.models.core import Record
        from src.database.models.search import HeadwordSearchEntry

        mdf_data = r"\ge orphan gloss" "\n" r"\ps n"
        rec = Record(lx="", source_id=self.source_id, mdf_data=mdf_data)
        self.session.add(rec)
        self.session.commit()
        UploadService.populate_search_entries([rec.id], session=self.session)
        count = self.session.query(HeadwordSearchEntry).filter_by(record_id=rec.id).count()
        self.assertEqual(count, 0, "Record without lx must not create HeadwordSearchEntry")

    # --- Item 2.4: SearchEntry population is unchanged (SC-4) ---
    def test_search_entry_unchanged(self):
        """SC-4: SearchEntry must still contain ALL values including nested ones."""
        from src.database.models.search import SearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw" "\n"
            r"\va wampu-" "\n"
            r"\ge round" "\n"
            r"\se wampuw-" "\n"
            r"\cf wampuch" "\n"
            r"\ve fire"
        )
        entries = self.session.query(SearchEntry).filter_by(record_id=rec.id).all()
        types = sorted([e.entry_type for e in entries])
        self.assertEqual(
            types, ["cf", "lx", "se", "va", "ve"],
            "SearchEntry must contain ALL entry types (unchanged)"
        )


if __name__ == "__main__":
    unittest.main()
