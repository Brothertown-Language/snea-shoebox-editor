import unittest
import uuid
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database import Base, Record, Language, RecordLanguage, MatchupQueue, Source, EditHistory, SearchEntry, User
from src.services.upload_service import UploadService

class TestSoParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            cls.test_db_path = Path("tmp/test_ln_parsing_db")
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

            # Seed ISO 639-3 data required for language validation
            import csv, io
            from pathlib import Path as _Path
            from src.database.models.iso639 import ISO639_3
            _data_file = _Path("src/database/data/iso-639-3.tab")
            _Session = sessionmaker(bind=cls.engine)
            _sess = _Session()
            if _sess.query(ISO639_3).count() == 0:
                with open(_data_file, encoding='utf-8') as _f:
                    _reader = csv.DictReader(_f, delimiter='\t')
                    _sess.add_all([ISO639_3(id=r['Id'], part2b=r.get('Part2b') or None, part2t=r.get('Part2t') or None, part1=r.get('Part1') or None, scope=r['Scope'], language_type=r['Language_Type'], ref_name=r['Ref_Name'], comment=r.get('Comment') or None) for r in _reader])
                    _sess.commit()
            _sess.close()
        except ImportError:
            raise unittest.SkipTest("pgserver not installed")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'pg_server'):
            cls.pg_server.cleanup()
        if hasattr(cls, 'test_db_path') and cls.test_db_path.exists():
            import shutil
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        self.session = self.Session()
        # Clean up tables
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE user_activity_log, record_languages, edit_history, search_entries, records, languages, matchup_queue, users, sources RESTART IDENTITY CASCADE;"))
            conn.commit()

        # Create a user
        self.user = User(email="test@example.com", username="testuser", github_id=123)
        self.session.add(self.user)
        self.session.commit() # Commit so AuditService can find it

        # Create a source
        self.source = Source(name="Test Source")
        self.session.add(self.source)
        self.session.flush()
        self.source_id = self.source.id

        # Create a default language
        self.default_lang = Language(name="Default", code="def")
        self.session.add(self.default_lang)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def _patch_session(self):
        from unittest.mock import patch
        return patch("src.services.upload_service.get_session", return_value=self.session)

    def test_so_parsing_bulk_new(self):
        r"""Test that \so tag is parsed correctly in bulk approve new."""
        mdf_data = "\\lx test\n\\so Mohegan-Pequot [xpq]\n\\ge test gloss"
        batch_id = str(uuid.uuid4())
        
        # Stage entry
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx="test",
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        # Commit bulk new
        from unittest.mock import patch
        with patch("src.services.upload_service.get_session", return_value=self.session), \
             patch("src.services.audit_service.get_session", return_value=self.session):
            UploadService.commit_new(batch_id, "test@example.com", str(uuid.uuid4()))

        # Verify record and language
        record = self.session.query(Record).filter_by(lx="test").first()
        self.assertIsNotNone(record)
        
        # Check associated languages
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        
        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.name, "Mohegan-Pequot")
        self.assertEqual(lang.code, "xpq")

    def test_legacy_lg_not_parsed(self):
        r"""Test that \lg tag is NO LONGER parsed and no RecordLanguage is created."""
        mdf_data = "\\lx test2\n\\ps n\n\\ge test gloss\n\\nt test note\n\\lg OldTag [old]"
        batch_id = str(uuid.uuid4())
        
        # Stage entry
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx="test2",
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        # Commit bulk new
        from unittest.mock import patch
        with patch("src.services.upload_service.get_session", return_value=self.session), \
             patch("src.services.audit_service.get_session", return_value=self.session):
            UploadService.commit_new(batch_id, "test@example.com", str(uuid.uuid4()))

        # Verify record and fallback language
        record = self.session.query(Record).filter_by(lx="test2").first()
        self.assertIsNotNone(record)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        # Should be 0 because \lg is ignored and \so is missing
        self.assertEqual(len(record_langs), 0)

    def test_no_so_tag_no_exception_no_default(self):
        r"""Verify that record without \so tag causes no exception and gets no default language."""
        mdf_data = "\\lx test_noln\n\\ps n\n\\ge gloss without ln"
        batch_id = str(uuid.uuid4())
        
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx="test_noln",
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        # Execute commit_new - should not raise exception
        from unittest.mock import patch
        with patch("src.services.upload_service.get_session", return_value=self.session), \
             patch("src.services.audit_service.get_session", return_value=self.session):
            UploadService.commit_new(batch_id, "test@example.com", str(uuid.uuid4()))

        # Verify record exists
        record = self.session.query(Record).filter_by(lx="test_noln").first()
        self.assertIsNotNone(record)
        
        # Verify NO RecordLanguage entries exist for this record
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 0, rf"Record should not have any associated languages when \so is missing. Found: {record_langs}")

if __name__ == "__main__":
    unittest.main()
