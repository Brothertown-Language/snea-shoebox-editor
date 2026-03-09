# Copyright (c) 2026 Brothertown Language
import unittest
import uuid
from src.database import get_session, init_db, Source, Language, Record, EditHistory, SearchEntry, User
from src.services.upload_service import UploadService

class TestRollbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.session = get_session()
        
        # Setup test user
        cls.user = cls.session.query(User).filter_by(github_id=999).first()
        if not cls.user:
            cls.user = User(email="tester@example.com", username="tester", github_id=999)
            cls.session.add(cls.user)
            
        # Setup test source
        cls.source = cls.session.query(Source).filter_by(name="Rollback Test Source").first()
        if not cls.source:
            cls.source = Source(name="Rollback Test Source")
            cls.session.add(cls.source)
        
        # Setup test language
        cls.lang = cls.session.query(Language).filter_by(code="rbt").first()
        if not cls.lang:
            cls.lang = Language(code="rbt", name="Rollback Test")
            cls.session.add(cls.lang)
        
        cls.session.commit()
        cls.user_email = cls.user.email
        cls.source_id = cls.source.id
        cls.lang_id = cls.lang.id

    def setUp(self):
        # Clear existing records and history to isolate tests
        self.session.query(SearchEntry).delete()
        self.session.query(EditHistory).delete()
        self.session.query(Record).delete()
        self.session.commit()

    def _add_record(self, lx, mdf_data):
        rec = Record(lx=lx, hm=1, source_id=self.source_id, mdf_data=mdf_data)
        self.session.add(rec)
        self.session.commit()
        UploadService.populate_search_entries([rec.id], session=self.session)
        return rec

    def test_rollback_updated_record(self):
        # 1. Initial state
        rec = self._add_record("dog", "\\lx dog\n\\ps n")
        initial_id = rec.id
        
        # 2. Apply update in a session
        session_id = str(uuid.uuid4())
        prev_data = rec.mdf_data
        
        # Fresh fetch to ensure we have the latest
        rec = self.session.get(Record, initial_id)
        rec.lx = "doggy"
        rec.mdf_data = "\\lx doggy\n\\ps n"
        self.session.add(EditHistory(
            record_id=initial_id,
            user_email=self.user_email,
            session_id=session_id,
            version=rec.current_version + 1,
            change_summary="Update",
            prev_data=prev_data,
            current_data=rec.mdf_data
        ))
        UploadService.populate_search_entries([initial_id], session=self.session)
        self.session.commit()
        
        # Verify updated state
        self.session.expire_all()
        r = self.session.get(Record, initial_id)
        self.assertEqual(r.lx, "doggy")
        self.assertTrue(self.session.query(SearchEntry).filter_by(record_id=initial_id, term="doggy").first())
        self.assertFalse(self.session.query(SearchEntry).filter_by(record_id=initial_id, term="dog").first())
        
        # 3. Rollback
        result = UploadService.rollback_session(session_id, user_email=self.user_email)
        self.assertEqual(result['rolled_back_count'], 1)
        self.assertEqual(result['deleted_count'], 0)
        
        # 4. Verify restored state
        self.session.expire_all()
        r_restored = self.session.get(Record, initial_id)
        self.assertEqual(r_restored.lx, "dog")
        self.assertTrue(self.session.query(SearchEntry).filter_by(record_id=initial_id, term="dog").first())
        self.assertFalse(self.session.query(SearchEntry).filter_by(record_id=initial_id, term="doggy").first())
        # History for that session should be gone
        self.assertEqual(self.session.query(EditHistory).filter_by(session_id=session_id).count(), 0)

    def test_rollback_created_record(self):
        # 1. Create a record in a session
        session_id = str(uuid.uuid4())
        rec = Record(lx="cat", hm=1, source_id=self.source_id, mdf_data="\\lx cat\n\\ps n")
        self.session.add(rec)
        self.session.flush()
        rec_id = rec.id
        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Create",
            prev_data=None,
            current_data=rec.mdf_data
        ))
        UploadService.populate_search_entries([rec_id], session=self.session)
        self.session.commit()
        
        # Verify state
        self.session.expire_all()
        self.assertIsNotNone(self.session.get(Record, rec_id))
        self.assertTrue(self.session.query(SearchEntry).filter_by(record_id=rec_id, term="cat").first())
        
        # 2. Rollback
        result = UploadService.rollback_session(session_id, user_email=self.user_email)
        self.assertEqual(result['rolled_back_count'], 0)
        self.assertEqual(result['deleted_count'], 1)
        
        # 3. Verify deleted state
        self.session.expire_all()
        self.assertIsNone(self.session.get(Record, rec_id))
        self.assertEqual(self.session.query(SearchEntry).filter_by(record_id=rec_id).count(), 0)
        self.assertEqual(self.session.query(EditHistory).filter_by(record_id=rec_id).count(), 0)

    def test_rollback_multiple_changes_to_same_record(self):
        # 1. Initial state
        rec = self._add_record("bird", "\\lx bird\n\\ps n")
        initial_id = rec.id
        
        # 2. Apply TWO updates in the same session
        session_id = str(uuid.uuid4())
        
        # First update
        prev_data_1 = rec.mdf_data
        rec.lx = "birdee"
        rec.mdf_data = "\\lx birdee\n\\ps n"
        self.session.add(EditHistory(
            record_id=initial_id,
            user_email=self.user_email,
            session_id=session_id,
            version=rec.current_version + 1,
            change_summary="Update 1",
            prev_data=prev_data_1,
            current_data=rec.mdf_data
        ))
        self.session.commit()
        
        # Second update
        prev_data_2 = rec.mdf_data
        rec.lx = "birder"
        rec.mdf_data = "\\lx birder\n\\ps n"
        self.session.add(EditHistory(
            record_id=initial_id,
            user_email=self.user_email,
            session_id=session_id,
            version=rec.current_version + 1,
            change_summary="Update 2",
            prev_data=prev_data_2,
            current_data=rec.mdf_data
        ))
        self.session.commit()
        
        # 3. Rollback
        UploadService.rollback_session(session_id, user_email=self.user_email)
        
        # 4. Verify it went back to the VERY FIRST state (bird)
        r_final = self.session.get(Record, initial_id)
        self.assertEqual(r_final.lx, "bird")

    def test_revert_batch_changes_no_post_import_edits(self):
        """Records with no post-import edits are counted as already_current."""
        session_id = str(uuid.uuid4())
        rec = Record(lx="fox", hm=1, source_id=self.source_id, mdf_data=r"\lx fox\n\ps n")
        self.session.add(rec)
        self.session.flush()
        rec_id = rec.id
        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=rec.mdf_data
        ))
        self.session.commit()

        result = UploadService.revert_batch_changes(session_id, user_email=self.user_email)
        self.assertEqual(result['reverted_count'], 0)
        self.assertEqual(result['skipped_locked'], 0)
        self.assertEqual(result['already_current'], 1)

        # Record unchanged
        self.session.expire_all()
        r = self.session.get(Record, rec_id)
        self.assertEqual(r.lx, "fox")

    def test_revert_batch_changes_reverts_post_import_edits(self):
        """Records with post-import edits are restored to post-import state."""
        session_id = str(uuid.uuid4())
        post_import_mdf = r"\lx wolf\n\ps n"
        rec = Record(lx="wolf", hm=1, source_id=self.source_id, mdf_data=post_import_mdf)
        self.session.add(rec)
        self.session.flush()
        rec_id = rec.id

        # Import history entry
        import_entry = EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=post_import_mdf
        )
        self.session.add(import_entry)
        self.session.commit()

        # Simulate a later manual edit (different session)
        later_session_id = str(uuid.uuid4())
        rec.lx = "wolfie"
        rec.mdf_data = r"\lx wolfie\n\ps n"
        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=later_session_id,
            version=2,
            change_summary="Manual edit",
            prev_data=post_import_mdf,
            current_data=rec.mdf_data
        ))
        UploadService.populate_search_entries([rec_id], session=self.session)
        self.session.commit()

        # Verify current state is the later edit
        self.session.expire_all()
        self.assertEqual(self.session.get(Record, rec_id).lx, "wolfie")

        result = UploadService.revert_batch_changes(session_id, user_email=self.user_email)
        self.assertEqual(result['reverted_count'], 1)
        self.assertEqual(result['skipped_locked'], 0)
        self.assertEqual(result['already_current'], 0)

        # Record restored to post-import state
        self.session.expire_all()
        r = self.session.get(Record, rec_id)
        self.assertEqual(r.mdf_data, post_import_mdf)
        # Later history entry deleted
        self.assertEqual(
            self.session.query(EditHistory).filter_by(session_id=later_session_id).count(), 0
        )

    def test_revert_batch_changes_skips_locked_records(self):
        """Locked records are skipped and counted in skipped_locked."""
        session_id = str(uuid.uuid4())
        post_import_mdf = r"\lx bear\n\ps n"
        rec = Record(lx="bear", hm=1, source_id=self.source_id, mdf_data=post_import_mdf,
                     is_locked=True, locked_by=self.user_email, lock_note="Protected")
        self.session.add(rec)
        self.session.flush()
        rec_id = rec.id

        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=post_import_mdf
        ))
        self.session.commit()

        # Simulate a later edit
        later_session_id = str(uuid.uuid4())
        rec.lx = "beary"
        rec.mdf_data = r"\lx beary\n\ps n"
        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=later_session_id,
            version=2,
            change_summary="Manual edit",
            prev_data=post_import_mdf,
            current_data=rec.mdf_data
        ))
        self.session.commit()

        result = UploadService.revert_batch_changes(session_id, user_email=self.user_email)
        self.assertEqual(result['reverted_count'], 0)
        self.assertEqual(result['skipped_locked'], 1)
        self.assertEqual(result['already_current'], 0)

        # Record unchanged (still has later edit)
        self.session.expire_all()
        r = self.session.get(Record, rec_id)
        self.assertEqual(r.lx, "beary")


    def test_delete_post_import_new_records_no_new_records(self):
        """No records created after import — deleted_count is 0."""
        from datetime import datetime, timezone
        session_id = str(uuid.uuid4())
        import_ts = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        rec = Record(lx="elk", hm=1, source_id=self.source_id, mdf_data=r"\lx elk\n\ps n")
        self.session.add(rec)
        self.session.flush()
        rec_id = rec.id
        self.session.add(EditHistory(
            record_id=rec_id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=rec.mdf_data,
            timestamp=import_ts,
        ))
        self.session.commit()

        result = UploadService.delete_post_import_new_records(session_id, user_email=self.user_email)
        self.assertEqual(result['deleted_count'], 0)
        self.assertEqual(result['skipped_locked'], 0)
        # Record still exists
        self.session.expire_all()
        self.assertIsNotNone(self.session.get(Record, rec_id))

    def test_delete_post_import_new_records_deletes_new_records(self):
        """Records created after import in the same source are deleted."""
        from datetime import datetime, timezone
        session_id = str(uuid.uuid4())
        import_ts = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        after_ts = datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc)

        # The import-session record
        anchor = Record(lx="moose", hm=1, source_id=self.source_id, mdf_data=r"\lx moose\n\ps n")
        self.session.add(anchor)
        self.session.flush()
        self.session.add(EditHistory(
            record_id=anchor.id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=anchor.mdf_data,
            timestamp=import_ts,
        ))

        # A new record added after the import (different session, same source)
        new_rec = Record(lx="lynx", hm=1, source_id=self.source_id, mdf_data=r"\lx lynx\n\ps n")
        self.session.add(new_rec)
        self.session.flush()
        new_rec_id = new_rec.id
        later_session_id = str(uuid.uuid4())
        self.session.add(EditHistory(
            record_id=new_rec_id,
            user_email=self.user_email,
            session_id=later_session_id,
            version=1,
            change_summary="New record",
            prev_data=None,
            current_data=new_rec.mdf_data,
            timestamp=after_ts,
        ))
        UploadService.populate_search_entries([new_rec_id], session=self.session)
        self.session.commit()

        result = UploadService.delete_post_import_new_records(session_id, user_email=self.user_email)
        self.assertEqual(result['deleted_count'], 1)
        self.assertEqual(result['skipped_locked'], 0)

        self.session.expire_all()
        self.assertIsNone(self.session.get(Record, new_rec_id))
        self.assertEqual(self.session.query(EditHistory).filter_by(record_id=new_rec_id).count(), 0)

    def test_delete_post_import_new_records_skips_locked(self):
        """Locked records created after import are skipped."""
        from datetime import datetime, timezone
        session_id = str(uuid.uuid4())
        import_ts = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        after_ts = datetime(2025, 1, 1, 13, 0, 0, tzinfo=timezone.utc)

        # The import-session anchor record
        anchor = Record(lx="bison", hm=1, source_id=self.source_id, mdf_data=r"\lx bison\n\ps n")
        self.session.add(anchor)
        self.session.flush()
        self.session.add(EditHistory(
            record_id=anchor.id,
            user_email=self.user_email,
            session_id=session_id,
            version=1,
            change_summary="Import",
            prev_data=None,
            current_data=anchor.mdf_data,
            timestamp=import_ts,
        ))

        # A locked new record added after the import
        locked_rec = Record(lx="puma", hm=1, source_id=self.source_id, mdf_data=r"\lx puma\n\ps n",
                            is_locked=True, locked_by=self.user_email, lock_note="Protected")
        self.session.add(locked_rec)
        self.session.flush()
        locked_rec_id = locked_rec.id
        later_session_id = str(uuid.uuid4())
        self.session.add(EditHistory(
            record_id=locked_rec_id,
            user_email=self.user_email,
            session_id=later_session_id,
            version=1,
            change_summary="New locked record",
            prev_data=None,
            current_data=locked_rec.mdf_data,
            timestamp=after_ts,
        ))
        self.session.commit()

        result = UploadService.delete_post_import_new_records(session_id, user_email=self.user_email)
        self.assertEqual(result['deleted_count'], 0)
        self.assertEqual(result['skipped_locked'], 1)

        self.session.expire_all()
        self.assertIsNotNone(self.session.get(Record, locked_rec_id))


if __name__ == '__main__':
    unittest.main()
