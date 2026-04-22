import unittest

from sqlalchemy import text

from src.database.connection import get_session
from src.database.models.core import Record, Source
from src.database.models.identity import User
from src.services.linguistic_service import LinguisticService


class TestRecordLocking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure we have a clean state for testing
        with get_session() as session:
            session.execute(
                text(
                    "TRUNCATE user_activity_log, record_languages, edit_history, search_entries, records, sources, users CASCADE"
                )
            )

            # Seed a test user
            cls.user_email = "test@example.com"
            user = User(email=cls.user_email, username="testuser", github_id=12345)
            session.add(user)

            # Seed a source
            source = Source(name="Test Source")
            session.add(source)
            session.commit()
            cls.source_id = source.id

    def setUp(self):
        with get_session() as session:
            # Create a record for each test
            record = Record(lx="test_lexeme", source_id=self.source_id, mdf_data="\\lx test_lexeme\n\\ge test gloss")
            session.add(record)
            session.commit()
            self.record_id = record.id

    def tearDown(self):
        with get_session() as session:
            session.execute(text("TRUNCATE edit_history, records CASCADE"))
            session.commit()

    def test_lock_record(self):
        success = LinguisticService.lock_record(self.record_id, self.user_email, "Locking for test")
        self.assertTrue(success)

        record = LinguisticService.get_record(self.record_id)
        self.assertTrue(record["is_locked"])
        self.assertEqual(record["locked_by"], self.user_email)
        self.assertEqual(record["lock_note"], "Locking for test")

        # Check history
        history = LinguisticService.get_edit_history(self.record_id)
        self.assertEqual(len(history), 0)  # get_edit_history excludes the max-version entry

    def test_update_locked_record_rejected(self):
        # Lock first
        LinguisticService.lock_record(self.record_id, self.user_email)

        # Try to update
        success = LinguisticService.update_record(
            self.record_id, self.user_email, mdf_data="\\lx test_lexeme\n\\ge updated gloss"
        )
        self.assertFalse(success)

        # Verify no change
        record = LinguisticService.get_record(self.record_id)
        self.assertIn("test gloss", record["mdf_data"])

    def test_unlock_record(self):
        # Lock first
        LinguisticService.lock_record(self.record_id, self.user_email)

        # Unlock
        success = LinguisticService.unlock_record(self.record_id, self.user_email)
        self.assertTrue(success)

        record = LinguisticService.get_record(self.record_id)
        self.assertFalse(record["is_locked"])
        self.assertIsNone(record["locked_by"])

        # Check history
        history = LinguisticService.get_edit_history(self.record_id)
        self.assertEqual(len(history), 1)  # get_edit_history excludes max-version; lock entry is visible
        self.assertEqual(history[0]["change_summary"], "Record locked")

    def test_update_after_unlock_success(self):
        # Lock then unlock
        LinguisticService.lock_record(self.record_id, self.user_email)
        LinguisticService.unlock_record(self.record_id, self.user_email)

        # Update should now succeed
        success = LinguisticService.update_record(
            self.record_id, self.user_email, mdf_data="\\lx test_lexeme\n\\ge updated gloss"
        )
        self.assertTrue(success)

        record = LinguisticService.get_record(self.record_id)
        self.assertIn("updated gloss", record["mdf_data"])


if __name__ == "__main__":
    unittest.main()
