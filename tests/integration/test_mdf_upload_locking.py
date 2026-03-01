import unittest
import uuid
from src.database import get_session, Record, User, Source, MatchupQueue
from src.services.upload_service import UploadService
from sqlalchemy import text

class TestMDFUploadLocking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with get_session() as session:
            session.execute(text("TRUNCATE user_activity_log, record_languages, edit_history, search_entries, matchup_queue, records, sources, users CASCADE"))
            
            cls.user_email = "upload_test@example.com"
            user = User(email=cls.user_email, username="upload_user", github_id=67890)
            session.add(user)
            
            source = Source(name="Upload Test Source")
            session.add(source)
            session.commit()
            cls.source_id = source.id

    def setUp(self):
        with get_session() as session:
            # Create one locked record and one unlocked record
            self.locked_lx = "locked_lex"
            self.unlocked_lx = "unlocked_lex"
            
            rec1 = Record(lx=self.locked_lx, source_id=self.source_id, mdf_data=f"\\lx {self.locked_lx}\n\\ge locked", is_locked=True)
            rec2 = Record(lx=self.unlocked_lx, source_id=self.source_id, mdf_data=f"\\lx {self.unlocked_lx}\n\\ge unlocked", is_locked=False)
            
            session.add_all([rec1, rec2])
            session.commit()
            self.locked_id = rec1.id
            self.unlocked_id = rec2.id
            self.batch_id = str(uuid.uuid4())

    def tearDown(self):
        with get_session() as session:
            session.execute(text("TRUNCATE matchup_queue, edit_history, records CASCADE"))
            session.commit()

    def test_suggest_matches_detects_lock(self):
        # Stage entries that conflict with locked and unlocked records
        entries = [
            {"lx": self.locked_lx, "mdf_data": f"\\lx {self.locked_lx}\n\\ge new locked content"},
            {"lx": self.unlocked_lx, "mdf_data": f"\\lx {self.unlocked_lx}\n\\ge new unlocked content"},
            {"lx": "brand_new", "mdf_data": "\\lx brand_new\n\\ge something new"}
        ]
        
        UploadService.stage_entries(self.user_email, self.source_id, entries, filename="test.mdf")
        
        # Verify batch_id was created
        with get_session() as session:
            batch_id = session.query(MatchupQueue.batch_id).first()[0]
            
        results = UploadService.suggest_matches(batch_id)
        
        # Check results
        locked_res = next(r for r in results if r['lx'] == self.locked_lx)
        unlocked_res = next(r for r in results if r['lx'] == self.unlocked_lx)
        new_res = next(r for r in results if r['lx'] == "brand_new")
        
        self.assertTrue(locked_res['suggested_is_locked'])
        self.assertFalse(unlocked_res['suggested_is_locked'])
        self.assertFalse(new_res['suggested_is_locked'])
        
        # Verify queue status
        with get_session() as session:
            locked_q = session.query(MatchupQueue).filter_by(lx=self.locked_lx).first()
            self.assertEqual(locked_q.status, 'locked_conflict')
            
            unlocked_q = session.query(MatchupQueue).filter_by(lx=self.unlocked_lx).first()
            self.assertEqual(unlocked_q.status, 'pending')

    def test_discard_locked_conflicts(self):
        entries = [
            {"lx": self.locked_lx, "mdf_data": f"\\lx {self.locked_lx}\n\\ge content"},
            {"lx": "clean", "mdf_data": "\\lx clean\n\\ge content"}
        ]
        UploadService.stage_entries(self.user_email, self.source_id, entries)
        
        with get_session() as session:
            batch_id = session.query(MatchupQueue.batch_id).first()[0]
            
        UploadService.suggest_matches(batch_id)
        
        # Discard
        count = UploadService.discard_locked_conflicts(batch_id)
        self.assertEqual(count, 1)
        
        with get_session() as session:
            remaining = session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0].lx, "clean")

    def test_download_locked_conflicts(self):
        entries = [
            {"lx": self.locked_lx, "mdf_data": f"\\lx {self.locked_lx}\n\\ge content"}
        ]
        UploadService.stage_entries(self.user_email, self.source_id, entries)
        
        with get_session() as session:
            batch_id = session.query(MatchupQueue.batch_id).first()[0]
            
        UploadService.suggest_matches(batch_id)
        
        fragment = UploadService.download_locked_conflicts(batch_id)
        self.assertIn(f"\\lx {self.locked_lx}", fragment)

if __name__ == '__main__':
    unittest.main()
