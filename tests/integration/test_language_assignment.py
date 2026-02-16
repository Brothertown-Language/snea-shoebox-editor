import unittest
import uuid
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database import Base, Record, Language, RecordLanguage, MatchupQueue, Source, User
from src.services.upload_service import UploadService

class TestLanguageAssignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            cls.test_db_path = Path("tmp/test_lang_assignment_db")
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
        self.session.commit()

        # Create a source
        self.source = Source(name="Test Source")
        self.session.add(self.source)
        self.session.flush()
        self.source_id = self.source.id

    def tearDown(self):
        self.session.close()

    def _commit_mdf(self, lx, mdf_data):
        batch_id = str(uuid.uuid4())
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx=lx,
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        from unittest.mock import patch
        with patch("src.services.upload_service.get_session", return_value=self.session), \
             patch("src.services.audit_service.get_session", return_value=self.session):
            UploadService.commit_new(batch_id, "test@example.com", str(uuid.uuid4()))
        
        return self.session.query(Record).filter_by(lx=lx).first()

    def test_scenario_1_headword_ln_only(self):
        r"""1) headword has \ln, sub entries do not = record has a primary language"""
        mdf_data = "\\lx test1\n\\ln Mohegan [moh]\n\\ge test gloss\n\\se subentry\n\\ge subgloss"
        record = self._commit_mdf("test1", mdf_data)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        self.assertTrue(record_langs[0].is_primary)
        
        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "moh")

    def test_scenario_2_headword_and_subentry_ln(self):
        r"""2) headword has \ln, subentries have \ln = record has both a primary language and secondary languages"""
        mdf_data = "\\lx test2\n\\ln Mohegan [moh]\n\\ge test gloss\n\\se subentry\n\\ln English [eng]\n\\ge subgloss"
        record = self._commit_mdf("test2", mdf_data)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).order_by(RecordLanguage.id).all()
        self.assertEqual(len(record_langs), 2)
        
        # Primary
        self.assertTrue(record_langs[0].is_primary)
        lang1 = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang1.code, "moh")
        
        # Secondary
        self.assertFalse(record_langs[1].is_primary)
        lang2 = self.session.get(Language, record_langs[1].language_id)
        self.assertEqual(lang2.code, "eng")

    def test_scenario_3_subentry_ln_only(self):
        r"""3) headwords does not have \ln, subentries have \ln = record does not have a primary language and has secondary languages"""
        mdf_data = "\\lx test3\n\\ge test gloss\n\\se subentry\n\\ln Mohegan [moh]\n\\ge subgloss"
        record = self._commit_mdf("test3", mdf_data)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        self.assertFalse(record_langs[0].is_primary)
        
        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "moh")

    def test_scenario_4_no_ln(self):
        r"""4) headwords does not have \ln, subentreis do not have \n = records does not have any languages"""
        mdf_data = "\\lx test4\n\\ge test gloss\n\\se subentry\n\\ge subgloss"
        record = self._commit_mdf("test4", mdf_data)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 0)

if __name__ == "__main__":
    unittest.main()
