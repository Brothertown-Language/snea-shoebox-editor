# Copyright (c) 2026 Brothertown Language
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.models.core import Language, Record, RecordLanguage, Source
from src.database.models.identity import User
from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry, SearchEntry
from src.database.models.workflow import EditHistory, MatchupQueue
from src.services.linguistic_service import LinguisticService
from src.services.statistics_service import StatisticsService


class TestLinguisticService(unittest.TestCase):
    """
    Tests for LinguisticService CRUD operations using a real pgserver DB.
    """

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver

            cls.test_db_path = Path("tmp/test_linguistic_service_db")
            if cls.test_db_path.exists():
                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)

            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            Base.metadata.create_all(cls.engine)

            # Run migrations to ensure generated columns and indexes are present
            from src.database.migrations import MigrationManager

            manager = MigrationManager(cls.engine)
            # We don't want to seed data in tests usually, but run_all() is fine for schema
            # Actually manager.run_all() seeds permissions and iso data.
            manager._ensure_extensions()
            manager._run_migrations()

            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        self.session = self.Session()
        # Seed basic data
        self.user = User(email="editor@example.com", username="editor", github_id=1)
        self.source = Source(name="Source A", short_name="SA", description="Test Source A")
        self.lang = Language(code="wqk", name="Wampanoag")
        self.session.add_all([self.user, self.source, self.lang])
        self.session.commit()

        self.source_id = self.source.id
        self.lang_id = self.lang.id

    def tearDown(self):
        self.session.close()
        with self.engine.connect() as conn:
            conn.execute(
                text(
                    "TRUNCATE matchup_queue, edit_history, "
                    "search_entries, headword_search_entries, gloss_search_entries, "
                    "records, record_languages, users, languages, sources "
                    "RESTART IDENTITY CASCADE;"
                )
            )
            conn.commit()

    def _patch_session(self):
        return patch("src.services.linguistic_service.get_session", return_value=self.Session())

    def test_get_sources_with_counts(self):
        # Create some records
        r1 = Record(lx="word1", source_id=self.source_id, mdf_data="\\lx word1")
        r2 = Record(lx="word2", source_id=self.source_id, mdf_data="\\lx word2")
        self.session.add_all([r1, r2])
        self.session.commit()

        with self._patch_session():
            sources = LinguisticService.get_sources_with_counts()

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["name"], "Source A")
        self.assertEqual(sources[0]["record_count"], 2)

    def test_get_source(self):
        with self._patch_session():
            source = LinguisticService.get_source(self.source_id)

        self.assertIsNotNone(source)
        self.assertEqual(source["name"], "Source A")
        self.assertEqual(source["short_name"], "SA")

    def test_get_record(self):
        record = Record(
            lx="nup", hm=1, ps="v", ge="die", source_id=self.source_id, mdf_data="\\lx nup\n\\ps v\n\\ge die"
        )
        self.session.add(record)
        self.session.commit()

        # Link language
        self.session.add(RecordLanguage(record_id=record.id, language_id=self.lang_id, is_primary=True))
        self.session.commit()

        with self._patch_session():
            res = LinguisticService.get_record(record.id)

        self.assertIsNotNone(res)
        self.assertEqual(res["lx"], "nup")
        self.assertEqual(res["source_name"], "Source A")
        self.assertEqual(len(res["languages"]), 1)
        self.assertEqual(res["languages"][0]["code"], "wqk")

    def test_search_records(self):
        from src.database.models.search import SearchEntry

        r1 = Record(lx="apple", ge="fruit", source_id=self.source_id, mdf_data="\\lx apple")
        r2 = Record(lx="banana", ge="fruit", source_id=self.source_id, mdf_data="\\lx banana")
        self.session.add_all([r1, r2])
        self.session.commit()

        # Add search entries for r1
        s1 = SearchEntry(record_id=r1.id, term="apple", normalized_term="apple", entry_type="lx")
        self.session.add(s1)
        self.session.commit()

        with self._patch_session():
            # Search by term (Lexeme mode default)
            result = LinguisticService.search_records(search_term="apple")
            self.assertEqual(len(result.records), 1)
            self.assertEqual(result.records[0]["lx"], "apple")
            self.assertEqual(result.total_count, 1)

            # Search by source
            result = LinguisticService.search_records(source_id=self.source_id)
            self.assertEqual(len(result.records), 2)
            self.assertEqual(result.total_count, 2)

    def test_search_records_lexeme_variants(self):
        from src.database.models.search import SearchEntry

        r1 = Record(lx="run", ge="to move fast", source_id=self.source_id, mdf_data="\\lx run\n\\va ran")
        self.session.add(r1)
        self.session.commit()

        # Add search entries
        s1 = SearchEntry(record_id=r1.id, term="run", normalized_term="run", entry_type="lx")
        s2 = SearchEntry(record_id=r1.id, term="ran", normalized_term="ran", entry_type="va")
        self.session.add_all([s1, s2])
        self.session.commit()

        with self._patch_session():
            # Search for variant
            result = LinguisticService.search_records(search_term="ran", search_mode="Lexeme")
            self.assertEqual(len(result.records), 1)
            self.assertEqual(result.records[0]["lx"], "run")
            self.assertEqual(result.total_count, 1)

    def test_search_records_fts(self):
        r1 = Record(lx="dog", ge="canine", source_id=self.source_id, mdf_data="\\lx dog\n\\nt some note")
        self.session.add(r1)
        self.session.commit()

        with self._patch_session():
            # Search in gloss
            result = LinguisticService.search_records(search_term="canine", search_mode="FTS")
            self.assertEqual(len(result.records), 1)
            self.assertEqual(result.total_count, 1)

            # Search in mdf_data
            result = LinguisticService.search_records(search_term="some note", search_mode="FTS")
            self.assertEqual(len(result.records), 1)
            self.assertEqual(result.total_count, 1)

    def test_search_records_pagination(self):
        records = [Record(lx=f"word{i}", source_id=self.source_id, mdf_data=f"\\lx word{i}") for i in range(10)]
        self.session.add_all(records)
        self.session.commit()

        with self._patch_session():
            # Test limit
            result = LinguisticService.search_records(limit=5)
            self.assertEqual(len(result.records), 5)
            self.assertEqual(result.total_count, 10)
            self.assertEqual(result.limit, 5)
            self.assertEqual(result.offset, 0)

            # Test offset
            result = LinguisticService.search_records(limit=5, offset=5)
            self.assertEqual(len(result.records), 5)
            self.assertEqual(result.total_count, 10)
            self.assertEqual(result.limit, 5)
            self.assertEqual(result.offset, 5)

    def test_get_all_records_for_export(self):
        """Test fetching all records matching criteria without pagination."""
        # Create some records first
        r1 = Record(lx="test1", source_id=self.source_id, mdf_data="\\lx test1")
        r2 = Record(lx="test2", source_id=self.source_id, mdf_data="\\lx test2")
        self.session.add_all([r1, r2])
        self.session.commit()

        with self._patch_session():
            records = LinguisticService.get_all_records_for_export(source_id=self.source_id)
            self.assertGreaterEqual(len(records), 2)
            for r in records:
                self.assertEqual(r["source_id"], self.source_id)
                # Verify column projection: 'embedding' should not be in the dictionary
                self.assertNotIn("embedding", r)
                self.assertIn("mdf_data", r)

            # Test with search term (manually add search entry since we bypass search_records)
            from src.database.models.search import SearchEntry

            self.session.add(SearchEntry(record_id=r1.id, term="test1", normalized_term="test1", entry_type="lx"))
            self.session.commit()

            records = LinguisticService.get_all_records_for_export(search_term="test1")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["lx"], "test1")

            # Test with record IDs
            rid = r1.id
            records_by_id = LinguisticService.get_all_records_for_export(record_ids=[rid])
            self.assertEqual(len(records_by_id), 1)
            self.assertEqual(records_by_id[0]["id"], rid)

    def test_stream_records_to_temp_file(self):
        """Test streaming records to a temporary file."""
        import os

        r1 = Record(lx="stream1", source_id=self.source_id, mdf_data="\\lx stream1")
        r2 = Record(lx="stream2", source_id=self.source_id, mdf_data="\\lx stream2")
        self.session.add_all([r1, r2])
        self.session.commit()

        with self._patch_session():
            temp_path = LinguisticService.stream_records_to_temp_file(source_id=self.source_id)
            try:
                self.assertTrue(os.path.exists(temp_path))
                with open(temp_path, encoding="utf-8") as f:
                    content = f.read()

                # Check that both records are present with double newline separation
                # Note: exact match depends on other records in DB if any
                self.assertIn("\\lx stream1", content)
                self.assertIn("\\lx stream2", content)
                self.assertIn("\\lx stream1\n\n\\lx stream2", content)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def test_bundle_records_to_mdf(self):
        records = [
            {"lx": "apple", "mdf_data": "\\lx apple\n\\ge fruit"},
            {"lx": "banana", "mdf_data": "\\lx banana\n\\ge fruit"},
        ]
        bundle = LinguisticService.bundle_records_to_mdf(records)
        expected = "\\lx apple\n\\ge fruit\n\n\\lx banana\n\\ge fruit"
        self.assertEqual(bundle, expected)

    def test_create_record(self):
        fields = {"lx": "test", "source_id": self.source_id, "mdf_data": "\\lx test"}
        with self._patch_session():
            record_id = LinguisticService.create_record(**fields)

        self.assertIsNotNone(record_id)
        self.session.expire_all()
        db_record = self.session.query(Record).filter_by(id=record_id).first()
        self.assertEqual(db_record.lx, "test")

    def test_update_record(self):
        record = Record(lx="old", source_id=self.source_id, mdf_data="\\lx old", status="draft")
        self.session.add(record)
        self.session.commit()

        with self._patch_session():
            success = LinguisticService.update_record(
                record.id, user_email="editor@example.com", lx="new", status="approved"
            )

        self.assertTrue(success)
        self.session.expire_all()
        db_record = self.session.query(Record).filter_by(id=record.id).first()
        self.assertEqual(db_record.lx, "new")
        self.assertEqual(db_record.status, "approved")
        self.assertIsNotNone(db_record.reviewed_at)
        self.assertEqual(db_record.reviewed_by, "editor@example.com")

        # Check history
        from src.database.models.workflow import EditHistory

        history = self.session.query(EditHistory).filter_by(record_id=record.id).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.user_email, "editor@example.com")

    def test_get_edit_history(self):
        record = Record(lx="history", source_id=self.source_id, mdf_data="\\lx history")
        self.session.add(record)
        self.session.commit()

        h1 = EditHistory(
            record_id=record.id,
            user_email="editor@example.com",
            version=1,
            change_summary="Creation",
            current_data="\\lx history",
        )
        h2 = EditHistory(
            record_id=record.id,
            user_email="editor@example.com",
            version=2,
            change_summary="Update",
            current_data="\\lx history\n\\ge updated",
        )
        self.session.add_all([h1, h2])
        self.session.commit()

        with self._patch_session():
            res = LinguisticService.get_edit_history(record.id)

        # get_edit_history excludes the max-version entry; with 2 entries, version=1 is visible
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["version"], 1)
        self.assertEqual(res[0]["user_email"], "editor@example.com")

    def test_soft_delete_record(self):
        record = Record(lx="todelete", source_id=self.source_id, mdf_data="\\lx todelete")
        self.session.add(record)
        self.session.commit()

        with self._patch_session():
            success = LinguisticService.soft_delete_record(record.id, "editor@example.com")

        self.assertTrue(success)
        self.session.expire_all()
        db_record = self.session.query(Record).filter_by(id=record.id).first()
        self.assertTrue(db_record.is_deleted)

    def test_update_source(self):
        with self._patch_session():
            success = LinguisticService.update_source(self.source_id, name="New Name")

        self.assertTrue(success)
        self.session.expire_all()
        db_source = self.session.query(Source).filter_by(id=self.source_id).first()
        self.assertEqual(db_source.name, "New Name")

    def test_reassign_records(self):
        source_b = Source(name="Source B")
        self.session.add(source_b)
        self.session.commit()
        source_b_id = source_b.id

        r1 = Record(lx="w1", source_id=self.source_id, mdf_data="\\lx w1")
        self.session.add(r1)
        self.session.commit()

        with self._patch_session():
            count = LinguisticService.reassign_records(self.source_id, source_b_id)

        self.assertEqual(count, 1)
        self.session.expire_all()
        db_record = self.session.query(Record).filter_by(id=r1.id).first()
        self.assertEqual(db_record.source_id, source_b_id)

    def test_delete_source(self):
        source_c = Source(name="Source C")
        self.session.add(source_c)
        self.session.commit()
        source_c_id = source_c.id

        # Can delete empty source
        with self._patch_session():
            success = LinguisticService.delete_source(source_c_id)
        self.assertTrue(success)
        self.session.expire_all()
        self.assertIsNone(self.session.query(Source).filter_by(id=source_c_id).first())

        # Cannot delete source with records
        r1 = Record(lx="w1", source_id=self.source_id, mdf_data="\\lx w1")
        self.session.add(r1)
        self.session.commit()

        with self._patch_session():
            success = LinguisticService.delete_source(self.source_id)
        self.assertFalse(success)
        self.session.expire_all()
        self.assertIsNotNone(self.session.query(Source).filter_by(id=self.source_id).first())

    def _patch_stats_session(self):
        return patch("src.services.statistics_service.get_session", return_value=self.Session())

    def test_statistics_service(self):
        # Setup data
        r1 = Record(lx="apple", ps="n", status="approved", source_id=self.source_id, mdf_data="\\lx apple")
        self.session.add(r1)
        self.session.commit()

        # Link language
        self.session.add(RecordLanguage(record_id=r1.id, language_id=self.lang_id, is_primary=True))

        # Add history
        history = EditHistory(
            record_id=r1.id,
            user_email="editor@example.com",
            version=1,
            change_summary="Initial import",
            current_data="\\lx apple",
        )
        self.session.add(history)
        self.session.commit()

        with self._patch_stats_session():
            stats = StatisticsService.get_summary_stats()
            self.assertEqual(stats["records"], 1)
            self.assertEqual(stats["sources"], 1)
            self.assertEqual(stats["languages"], 1)

            status_dist = StatisticsService.get_status_distribution()
            self.assertEqual(status_dist["approved"], 1)

            pos_dist = StatisticsService.get_top_parts_of_speech()
            self.assertEqual(pos_dist["n"], 1)

            source_dist = StatisticsService.get_source_distribution()
            self.assertEqual(source_dist["Source A"], 1)

            lang_dist = StatisticsService.get_language_distribution(primary_only=True)
            self.assertEqual(lang_dist["Wampanoag"], 1)

            recent = StatisticsService.get_recent_activity()
            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["lx"], "apple")

    def test_hard_delete_record_with_search_entries(self):
        record = Record(
            lx="nup", hm=1, ps="v", ge="die", source_id=self.source_id, mdf_data="\\lx nup\n\\va nut\n\\ge die"
        )
        self.session.add(record)
        self.session.commit()

        se = SearchEntry(record_id=record.id, term="nup", normalized_term="nup", entry_type="lx")
        hse_lx = HeadwordSearchEntry(record_id=record.id, term="nup", normalized_term="nup", entry_type="lx")
        hse_va = HeadwordSearchEntry(record_id=record.id, term="nut", normalized_term="nut", entry_type="va")
        gse = GlossSearchEntry(record_id=record.id, term="die", normalized_term="die")
        self.session.add_all([se, hse_lx, hse_va, gse])
        self.session.commit()

        self.assertEqual(self.session.query(SearchEntry).filter_by(record_id=record.id).count(), 1)
        self.assertEqual(self.session.query(HeadwordSearchEntry).filter_by(record_id=record.id).count(), 2)
        self.assertEqual(self.session.query(GlossSearchEntry).filter_by(record_id=record.id).count(), 1)

        with self._patch_session():
            result = LinguisticService.hard_delete_record(record.id)

        self.assertTrue(result)
        self.session.expire_all()
        self.assertIsNone(self.session.query(Record).filter_by(id=record.id).first())
        self.assertEqual(self.session.query(SearchEntry).filter_by(record_id=record.id).count(), 0)
        self.assertEqual(self.session.query(HeadwordSearchEntry).filter_by(record_id=record.id).count(), 0)
        self.assertEqual(self.session.query(GlossSearchEntry).filter_by(record_id=record.id).count(), 0)

    def test_hard_delete_record_with_edit_history(self):
        record = Record(lx="histdel", source_id=self.source_id, mdf_data="\\lx histdel")
        self.session.add(record)
        self.session.commit()

        h1 = EditHistory(
            record_id=record.id,
            user_email="editor@example.com",
            version=1,
            change_summary="Creation",
            current_data="\\lx histdel",
        )
        h2 = EditHistory(
            record_id=record.id,
            user_email="editor@example.com",
            version=2,
            change_summary="Update",
            current_data="\\lx histdel\n\\ge meaning",
        )
        self.session.add_all([h1, h2])
        self.session.commit()

        self.assertEqual(self.session.query(EditHistory).filter_by(record_id=record.id).count(), 2)

        with self._patch_session():
            result = LinguisticService.hard_delete_record(record.id)

        self.assertTrue(result)
        self.session.expire_all()
        self.assertIsNone(self.session.query(Record).filter_by(id=record.id).first())
        self.assertEqual(self.session.query(EditHistory).filter_by(record_id=record.id).count(), 0)

    def test_hard_delete_record_cleans_headword_and_gloss(self):
        record = Record(
            lx="wôpan",
            hm=1,
            ps="n",
            ge="light",
            source_id=self.source_id,
            mdf_data="\\lx wôpan\n\\va wôpanâk\n\\ge light",
        )
        self.session.add(record)
        self.session.commit()

        hse_lx = HeadwordSearchEntry(record_id=record.id, term="wôpan", normalized_term="wopan", entry_type="lx")
        hse_va = HeadwordSearchEntry(record_id=record.id, term="wôpanâk", normalized_term="wopanak", entry_type="va")
        gse = GlossSearchEntry(record_id=record.id, term="light", normalized_term="light")
        self.session.add_all([hse_lx, hse_va, gse])
        self.session.commit()

        self.assertEqual(self.session.query(HeadwordSearchEntry).filter_by(record_id=record.id).count(), 2)
        self.assertEqual(self.session.query(GlossSearchEntry).filter_by(record_id=record.id).count(), 1)

        with self._patch_session():
            result = LinguisticService.hard_delete_record(record.id)

        self.assertTrue(result)
        self.session.expire_all()
        self.assertIsNone(self.session.query(Record).filter_by(id=record.id).first())
        self.assertEqual(self.session.query(HeadwordSearchEntry).filter_by(record_id=record.id).count(), 0)
        self.assertEqual(self.session.query(GlossSearchEntry).filter_by(record_id=record.id).count(), 0)

    def test_hard_delete_record_nonexistent_returns_false(self):
        with self._patch_session():
            result = LinguisticService.hard_delete_record(99999)
        self.assertFalse(result)

    def test_hard_delete_record_nullifies_matchup_suggestion(self):
        record1 = Record(lx="suggested", source_id=self.source_id, mdf_data="\\lx suggested")
        record2 = Record(lx="to_delete", source_id=self.source_id, mdf_data="\\lx to_delete")
        self.session.add_all([record1, record2])
        self.session.commit()

        queue_entry = MatchupQueue(
            lx="word",
            mdf_data="\\lx word",
            suggested_record_id=record2.id,
            batch_id="test-batch",
            status="pending",
        )
        self.session.add(queue_entry)
        self.session.commit()

        with self._patch_session():
            result = LinguisticService.hard_delete_record(record2.id)

        self.assertTrue(result)
        self.session.expire_all()
        self.assertIsNone(self.session.query(Record).filter_by(id=record2.id).first())
        updated_queue = self.session.query(MatchupQueue).filter_by(id=queue_entry.id).first()
        self.assertIsNotNone(updated_queue)
        self.assertIsNone(updated_queue.suggested_record_id)
