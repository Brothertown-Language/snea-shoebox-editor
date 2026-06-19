"""Test for Phase 1: system_event_log table creation migration.

SC-1: system_event_log table exists with correct schema after migration.
RED phase: this test must FAIL because _migrate_create_system_event_log() does not exist yet.
"""

import unittest
from pathlib import Path

import pgserver
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.migrations import MigrationManager


class TestMigrationSystemEventLog(unittest.TestCase):
    """RED-phase test: system_event_log table does not exist before migration."""

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = Path("tmp/test_system_event_log_db")
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

        # Import models to ensure base metadata is populated
        from src.database.models.core import Language, Record, Source  # noqa: F401
        from src.database.models.identity import User, UserActivityLog  # noqa: F401
        from src.database.models.search import (  # noqa: F401
            FTSEntry,
            GlossSearchEntry,
            HeadwordSearchEntry,
            SearchEntry,
        )
        from src.database.models.workflow import EditHistory, MatchupQueue  # noqa: F401
        from src.database.models.meta import SchemaVersion  # noqa: F401

        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_migration_creates_system_event_log(self):
        """SC-1: _migrate_create_system_event_log() creates the system_event_log table.

        RED phase: this FAILS because the migration method does not exist yet.
        GREEN phase: this PASSES after the method is implemented.
        """
        # Given: the table does not exist yet
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        self.assertNotIn("system_event_log", table_names, "system_event_log should not exist before migration")

        # When: the migration runs (this will AttributeError — method doesn't exist yet)
        mgr = MigrationManager(self.engine)
        mgr._migrate_create_system_event_log()

        # Then: the table should exist with correct schema
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        self.assertIn("system_event_log", table_names, "system_event_log should exist after migration")

        columns = {col["name"]: col for col in inspector.get_columns("system_event_log")}

        expected_columns = {
            "id": {"type": "INTEGER", "nullable": False},
            "event_type": {"type": "VARCHAR", "nullable": False},
            "severity": {"type": "VARCHAR", "nullable": False},
            "message": {"type": "VARCHAR" if "TEXT" else "VARCHAR", "nullable": False},
            "source": {"type": "VARCHAR", "nullable": False},
            "details": {"type": "JSONB" if "JSONB" else "JSON", "nullable": True},
            "created_at": {"type": "TIMESTAMP", "nullable": False},
        }

        for col_name, expected in expected_columns.items():
            self.assertIn(
                col_name, columns, f"Column '{col_name}' should exist in system_event_log"
            )
            self.assertFalse(
                columns[col_name]["nullable"],
                f"Column '{col_name}' should be NOT NULL",
            )