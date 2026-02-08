# Copyright (c) 2026 Brothertown Language
import unittest
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database import (
    Base, Source, Language, Record, SearchEntry, 
    User, UserActivityLog, Permission, MatchupQueue, 
    EditHistory, SchemaVersion
)

class TestDatabaseCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start a temporary pgserver instance and initialize the schema."""
        try:
            import pgserver
            from pathlib import Path
            # Use a unique path in tmp/ for this test session
            cls.test_db_path = Path("tmp/test_crud_db")
            if cls.test_db_path.exists():
                import shutil
                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)
            
            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            
            # Enable extensions
            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
            
            # Create all tables
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not installed, skipping CRUD tests.")

    @classmethod
    def tearDownClass(cls):
        """Shut down the pgserver instance."""
        if hasattr(cls, 'pg_server'):
            cls.pg_server.cleanup()
        if hasattr(cls, 'test_db_path') and cls.test_db_path.exists():
            import shutil
            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        """Create a new session for each test."""
        self.session = self.Session()

    def tearDown(self):
        """Close the session and clean up tables."""
        self.session.close()
        # Clean up tables in order of dependency to avoid foreign key issues
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE schema_version, edit_history, matchup_queue, user_activity_log, permissions, search_entries, records, users, languages, sources RESTART IDENTITY CASCADE;"))
            conn.commit()

    def test_lookup_tables_crud(self):
        """Test CRUD for Language and Source tables."""
        # Create
        lang = Language(code="wam", name="Wampanoag", description="A Southern New England Algonquian language")
        source = Source(name="Natick/Trumbull", short_name="Trumbull", description="Trumbull's Natick Dictionary", citation_format="{page}")
        self.session.add_all([lang, source])
        self.session.commit()

        # Read
        lang_db = self.session.query(Language).filter_by(code="wam").first()
        source_db = self.session.query(Source).filter_by(name="Natick/Trumbull").first()
        self.assertIsNotNone(lang_db)
        self.assertEqual(lang_db.name, "Wampanoag")
        self.assertIsNotNone(source_db)
        self.assertEqual(source_db.short_name, "Trumbull")

        # Update
        lang_db.name = "Wôpanâak"
        self.session.commit()
        lang_updated = self.session.query(Language).filter_by(code="wam").first()
        self.assertEqual(lang_updated.name, "Wôpanâak")

        # Delete
        self.session.delete(lang_updated)
        self.session.commit()
        self.assertIsNone(self.session.query(Language).filter_by(code="wam").first())

    def test_record_and_search_crud(self):
        """Test CRUD for Record and SearchEntry tables."""
        # Setup prerequisites
        lang = Language(code="wam", name="Wampanoag")
        source = Source(name="Natick/Trumbull")
        self.session.add_all([lang, source])
        self.session.flush()

        # Create Record
        record = Record(
            lx="nup", 
            hm=1, 
            ps="v", 
            ge="die", 
            language_id=lang.id, 
            source_id=source.id,
            mdf_data="\\lx nup\n\\ps v\n\\ge die"
        )
        self.session.add(record)
        self.session.flush()

        # Create Search Entry
        search = SearchEntry(record_id=record.id, term="nup", entry_type="lx")
        self.session.add(search)
        self.session.commit()

        # Read
        record_db = self.session.query(Record).filter_by(lx="nup").first()
        self.assertIsNotNone(record_db)
        self.assertEqual(record_db.ge, "die")
        self.assertEqual(len(record_db.search_entries), 1)
        self.assertEqual(record_db.search_entries[0].term, "nup")

        # Update
        record_db.ge = "to die"
        self.session.commit()
        record_updated = self.session.query(Record).filter_by(lx="nup").first()
        self.assertEqual(record_updated.ge, "to die")

        # Delete (should FAIL because of RESTRICT)
        self.session.delete(record_db)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

        # Clean up SearchEntry first
        search_db = self.session.query(SearchEntry).filter_by(term="nup").first()
        self.session.delete(search_db)
        self.session.commit()

        # Now delete Record should succeed
        record_db = self.session.query(Record).filter_by(lx="nup").first()
        self.session.delete(record_db)
        self.session.commit()
        self.assertIsNone(self.session.query(Record).filter_by(lx="nup").first())
        self.assertIsNone(self.session.query(SearchEntry).filter_by(term="nup").first())

    def test_user_and_identity_crud(self):
        """Test CRUD for User, UserActivityLog, and Permission tables."""
        # Create User
        user = User(
            email="tester@example.com", 
            username="tester", 
            github_id=12345, 
            extra_metadata={"theme": "dark"}
        )
        self.session.add(user)
        self.session.flush()

        # Create Activity Log
        log = UserActivityLog(
            user_email=user.email,
            action="login",
            details="User logged in from test suite",
            ip_address="127.0.0.1"
        )
        
        # Create Permission (must include github_team because it is NOT NULL)
        perm = Permission(
            github_org="brothertown",
            github_team="testers",
            role="editor"
        )
        
        self.session.add_all([log, perm])
        self.session.commit()

        # Read
        user_db = self.session.query(User).filter_by(email="tester@example.com").first()
        self.assertIsNotNone(user_db)
        self.assertEqual(user_db.extra_metadata["theme"], "dark")
        self.assertEqual(len(user_db.activity_logs), 1)

        perm_db = self.session.query(Permission).filter_by(github_org="brothertown").first()
        self.assertIsNotNone(perm_db)
        self.assertEqual(perm_db.role, "editor")

    def test_user_active_flag(self):
        """Test the is_active flag on the User model."""
        user = User(
            email="disabled@example.com",
            username="disabled",
            github_id=555,
            is_active=False
        )
        self.session.add(user)
        self.session.commit()

        user_db = self.session.query(User).filter_by(username="disabled").first()
        self.assertFalse(user_db.is_active)

        user_db.is_active = True
        self.session.commit()
        self.assertTrue(self.session.query(User).filter_by(username="disabled").first().is_active)

    def test_prevention_of_accidental_user_deletion(self):
        """Test that deleting a user is restricted if they have activity logs."""
        user = User(email="active@example.com", username="active", github_id=999)
        self.session.add(user)
        self.session.flush()

        log = UserActivityLog(user_email=user.email, action="login")
        self.session.add(log)
        self.session.commit()

        # Attempt to delete user should fail due to foreign key constraint (RESTRICT)
        self.session.delete(user)
        with self.assertRaises(Exception):
            self.session.commit()
        
        self.session.rollback()

    def test_prevention_of_accidental_record_deletion(self):
        """Test that deleting a record is restricted if it has edit history or search entries."""
        lang = Language(code="test", name="Test")
        source = Source(name="Test Source")
        self.session.add_all([lang, source])
        self.session.flush()

        record = Record(lx="test", language_id=lang.id, source_id=source.id, mdf_data="\\lx test")
        self.session.add(record)
        self.session.flush()

        # 1. Test restriction by SearchEntry
        search = SearchEntry(record_id=record.id, term="test", entry_type="lx")
        self.session.add(search)
        self.session.commit()

        self.session.delete(record)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

        # Clean up search entry to test history
        search = self.session.query(SearchEntry).first()
        self.session.delete(search)
        self.session.commit()

        # 2. Test restriction by EditHistory
        history = EditHistory(record_id=record.id, user_email="admin@example.com", version=1, current_data="\\lx test")
        # Ensure user exists for history
        user = User(email="admin@example.com", username="admin", github_id=1)
        self.session.add_all([user, history])
        self.session.commit()

        # Attempt to delete record should fail (RESTRICT)
        self.session.delete(record)
        with self.assertRaises(Exception):
            self.session.commit()
        
        self.session.rollback()

    def test_user_deletion_restriction(self):
        """Test that deleting a user is restricted if they have logs, history or matchup entries."""
        user = User(email="editor2@example.com", username="editor2", github_id=11223)
        self.session.add(user)
        self.session.commit()

        # 1. Restriction by Activity Log
        log = UserActivityLog(user_email=user.email, action="login")
        self.session.add(log)
        self.session.commit()

        self.session.delete(user)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

        # 2. Restriction by Matchup Queue
        # Need source for matchup queue
        source = Source(name="Matchup Source")
        self.session.add(source)
        self.session.flush()

        # Remove log to isolate matchup queue restriction
        log = self.session.query(UserActivityLog).filter_by(user_email=user.email).first()
        self.session.delete(log)
        
        mq = MatchupQueue(user_email=user.email, source_id=source.id, mdf_data="\\lx test")
        self.session.add(mq)
        self.session.commit()

        self.session.delete(user)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

    def test_language_and_source_deletion_restriction(self):
        """Test that deleting a language or source is restricted if referenced by records."""
        lang = Language(code="restricted", name="Restricted")
        source = Source(name="Restricted Source")
        self.session.add_all([lang, source])
        self.session.flush()

        record = Record(lx="test", language_id=lang.id, source_id=source.id, mdf_data="\\lx test")
        self.session.add(record)
        self.session.commit()

        # Test Language restriction
        self.session.delete(lang)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

        # Test Source restriction
        self.session.delete(source)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

    def test_user_deletion_does_not_affect_records(self):
        """Test that deleting a user (if they have no logs/history) is blocked if they are in updated_by."""
        # Setup
        lang = Language(code="wam", name="Wampanoag")
        source = Source(name="Natick/Trumbull")
        user = User(email="temporary@example.com", username="temp", github_id=999)
        self.session.add_all([lang, source, user])
        self.session.flush()

        record = Record(
            lx="nup", 
            language_id=lang.id, 
            source_id=source.id,
            mdf_data="\\lx nup",
            updated_by=user.email
        )
        self.session.add(record)
        self.session.commit()

        # Delete user should now FAIL because updated_by has ON DELETE RESTRICT
        self.session.delete(user)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

        # Verify record still exists
        record_db = self.session.query(Record).filter_by(lx="nup").first()
        self.assertIsNotNone(record_db)
        self.assertEqual(record_db.updated_by, "temporary@example.com")

if __name__ == "__main__":
    unittest.main()
