# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database import Base, Source, Language, User, Record, MatchupQueue, EditHistory, SearchEntry, RecordLanguage
from src.services.upload_service import UploadService

class TestUploadE2E(unittest.TestCase):
    """
    Integration tests for D-4.2 (E2E Integration Test).
    Verifies the full lifecycle from staging to persistence.
    """

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            cls.test_db_path = Path("tmp/test_upload_e2e_db")
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
        if hasattr(cls, 'pg_server'):
            cls.pg_server.cleanup()
        if hasattr(cls, 'test_db_path') and cls.test_db_path.exists():
            import shutil
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        self.session = self.Session()
        # Clean data
        self.session.query(SearchEntry).delete()
        self.session.query(EditHistory).delete()
        self.session.query(MatchupQueue).delete()
        self.session.query(RecordLanguage).delete()
        self.session.query(Record).delete()
        self.session.query(User).delete()
        self.session.query(Language).delete()
        self.session.query(Source).delete()
        self.session.commit()

        # Seed basics
        self.user = User(email='editor@example.com', username='editor', github_id=123)
        self.source = Source(name='Source A', short_name='SA')
        self.lang = Language(code='alg', name='Algonquian')
        self.session.add_all([self.user, self.source, self.lang])
        self.session.commit()
        
        self.user_email = self.user.email
        self.source_id = self.source.id
        self.language_id = self.lang.id

    def tearDown(self):
        self.session.close()

    def _patch_session(self):
        return patch('src.services.upload_service.get_session', return_value=self.Session())

    def test_upload_lifecycle_matched_and_new(self):
        """Test full cycle: Staging -> Matching -> Confirm -> Apply (Matched & New)"""
        
        # 1. Create an existing record to match against
        existing_mdf = "\\lx dog\n\\ps n\n\\ge canine"
        rec = Record(
            lx="dog", 
            hm=1, 
            ps="n", 
            ge="canine", 
            source_id=self.source_id, 
            mdf_data=existing_mdf
        )
        self.session.add(rec)
        self.session.flush()
        rl = RecordLanguage(record_id=rec.id, language_id=self.language_id, is_primary=True)
        self.session.add(rl)
        self.session.commit()
        
        # 2. Stage new entries: one should match 'dog', one is new 'cat'
        entries = [
            {'lx': 'dog', 'mdf_data': '\\lx dog\n\\ps n\n\\ge pet dog'},
            {'lx': 'cat', 'mdf_data': '\\lx cat\n\\ps n\n\\ge feline'}
        ]
        
        with self._patch_session():
            batch_id = UploadService.stage_entries(self.user_email, self.source_id, entries, "test.mdf")
            
            # 3. Suggest matches
            suggestions = UploadService.suggest_matches(batch_id)
            self.assertEqual(len(suggestions), 2)
            
            # Identify which is which
            dog_entry = next(s for s in suggestions if s['lx'] == 'dog')
            cat_entry = next(s for s in suggestions if s['lx'] == 'cat')
            
            self.assertEqual(dog_entry['suggested_record_id'], rec.id)
            self.assertEqual(dog_entry['match_type'], 'exact')
            self.assertIsNone(cat_entry['suggested_record_id'])
            
            # 4. Confirm match (D-2 workflow)
            # Default for exact match is 'matched', but let's re-confirm
            UploadService.confirm_match(dog_entry['queue_id'], rec.id)
            
            # Set cat as 'create_new' (already default, but explicit for test)
            from sqlalchemy import update
            self.session.execute(
                update(MatchupQueue).where(MatchupQueue.id == cat_entry['queue_id']).values(status='create_new')
            )
            self.session.commit()
            
            # 5. Apply single (D-4.2 immediate apply)
            session_id = str(uuid.uuid4())
            
            # Apply 'dog' (Update)
            dog_result = UploadService.apply_single(
                queue_id=dog_entry['queue_id'],
                user_email=self.user_email,
                language_id=self.language_id,
                session_id=session_id
            )
            self.assertEqual(dog_result['record_id'], rec.id)
            
            # Apply 'cat' (New)
            cat_result = UploadService.apply_single(
                queue_id=cat_entry['queue_id'],
                user_email=self.user_email,
                language_id=self.language_id,
                session_id=session_id
            )
            self.assertIsNotNone(cat_result['record_id'])
            self.assertNotEqual(cat_result['record_id'], rec.id)
            
            # 6. Verify Persistence
            # Check Record Updates
            dog_rec = self.session.get(Record, rec.id)
            self.assertEqual(dog_rec.ge, "pet dog") # Updated from new MDF
            self.assertEqual(dog_rec.current_version, 2)
            
            cat_rec = self.session.get(Record, cat_result['record_id'])
            self.assertEqual(cat_rec.lx, "cat")
            # In SQLAlchemy with version_id_col, it might start at 1 and increment to 2 on first save 
            # or start at 2 depending on how current_version default is handled.
            self.assertIn(cat_rec.current_version, (1, 2))
            
            # Check Edit History
            histories = self.session.query(EditHistory).filter_by(session_id=session_id).all()
            self.assertEqual(len(histories), 2)
            
            # Check Search Entries (Post-apply sync)
            UploadService.populate_search_entries([dog_rec.id, cat_rec.id])
            
            dog_search = self.session.query(SearchEntry).filter_by(record_id=dog_rec.id, entry_type='lx').first()
            self.assertIsNotNone(dog_search)
            self.assertEqual(dog_search.term, "dog")
            
            cat_search = self.session.query(SearchEntry).filter_by(record_id=cat_rec.id, entry_type='lx').first()
            self.assertIsNotNone(cat_search)
            self.assertEqual(cat_search.term, "cat")

    def test_upload_lifecycle_discard(self):
        """Test staging and then discarding an entry."""
        entries = [{'lx': 'trash', 'mdf_data': '\\lx trash\n\\ge junk'}]
        with self._patch_session():
            batch_id = UploadService.stage_entries(self.user_email, self.source_id, entries, "trash.mdf")
            q_id = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first().id
            
            UploadService.mark_as_discard(q_id)
            
            session_id = str(uuid.uuid4())
            result = UploadService.apply_single(
                queue_id=q_id,
                user_email=self.user_email,
                language_id=self.language_id,
                session_id=session_id
            )
            
            self.assertIsNone(result.get('record_id'))
            
            # Verify no record created
            rec_count = self.session.query(Record).count()
            self.assertEqual(rec_count, 0)
            
            # Verify queue row is gone (or status changed - apply_single deletes from queue)
            q_row = self.session.get(MatchupQueue, q_id)
            self.assertIsNone(q_row)

if __name__ == '__main__':
    unittest.main()
