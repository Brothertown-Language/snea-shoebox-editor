# Copyright (c) 2026 Brothertown Language
import csv
import io
import json
from pathlib import Path

import streamlit as st
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from .connection import is_production


class MigrationManager:
    """
    Centralizes schema evolution, versioned migrations, and data seeding.
    Uses the SchemaVersion model to track applied migrations and prevent
    redundant execution.
    """

    # Ordered registry of versioned migrations: (version, method_name, description)
    _MIGRATIONS = [
        (1, "_migrate_cascade_constraints", "Add ON UPDATE CASCADE / ON DELETE RESTRICT constraints"),
        (2, "_migrate_add_embedding_column", "Add embedding vector column to records"),
    ]

    def __init__(self, engine):
        self._engine = engine

    def run_all(self):
        """Public entry point. Runs extensions, migrations, and seeds in order."""
        self._ensure_extensions()
        self._run_migrations()
        self.seed_default_permissions()
        self.seed_iso_639_data()

    # ── Extension Management ──────────────────────────────────────────

    def _ensure_extensions(self):
        """Ensure required PostgreSQL extensions are enabled."""
        with self._engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

    # ── Version Tracking ──────────────────────────────────────────────

    def _get_current_version(self) -> int:
        """Return the highest applied migration version, or 0 if none."""
        from .models.meta import SchemaVersion
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            result = session.query(SchemaVersion.version).order_by(
                SchemaVersion.version.desc()
            ).first()
            return result[0] if result else 0
        finally:
            session.close()

    def _record_migration(self, version: int, description: str):
        """Record a successfully applied migration."""
        from .models.meta import SchemaVersion
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            entry = SchemaVersion(version=version, description=description)
            session.add(entry)
            session.commit()
        finally:
            session.close()

    def _run_migrations(self):
        """Execute all pending versioned migrations in order."""
        current = self._get_current_version()
        for version, method_name, description in self._MIGRATIONS:
            if version <= current:
                continue
            method = getattr(self, method_name)
            method()
            self._record_migration(version, description)

    # ── Versioned Migrations ──────────────────────────────────────────

    def _migrate_cascade_constraints(self):
        """Migration 1: Add ON UPDATE CASCADE to user_email foreign keys
        and ON DELETE RESTRICT to entity foreign keys."""
        with self._engine.connect() as conn:
            # 1. user_activity_log
            conn.execute(text("ALTER TABLE user_activity_log DROP CONSTRAINT IF EXISTS user_activity_log_user_email_fkey;"))
            conn.execute(text("ALTER TABLE user_activity_log ADD CONSTRAINT user_activity_log_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

            # 2. matchup_queue
            conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_user_email_fkey;"))
            conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

            # 3. edit_history
            conn.execute(text("ALTER TABLE edit_history DROP CONSTRAINT IF EXISTS edit_history_user_email_fkey;"))
            conn.execute(text("ALTER TABLE edit_history ADD CONSTRAINT edit_history_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

            # 4. records (updated_by)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_updated_by_fkey;"))
            conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

            # 5. records (reviewed_by)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_reviewed_by_fkey;"))
            conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"))

            # 6. records (language_id)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_language_id_fkey;"))
            conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_language_id_fkey FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE RESTRICT;"))

            # 7. records (source_id)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_source_id_fkey;"))
            conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

            # 8. search_entries (record_id)
            conn.execute(text("ALTER TABLE search_entries DROP CONSTRAINT IF EXISTS search_entries_record_id_fkey;"))
            conn.execute(text("ALTER TABLE search_entries ADD CONSTRAINT search_entries_record_id_fkey FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE RESTRICT;"))

            # 9. matchup_queue (source_id)
            conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_source_id_fkey;"))
            conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

            # 10. matchup_queue (suggested_record_id)
            conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_suggested_record_id_fkey;"))
            conn.execute(text("ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_suggested_record_id_fkey FOREIGN KEY (suggested_record_id) REFERENCES records(id) ON DELETE RESTRICT;"))

            # 11. permissions (source_id)
            conn.execute(text("ALTER TABLE permissions DROP CONSTRAINT IF EXISTS permissions_source_id_fkey;"))
            conn.execute(text("ALTER TABLE permissions ADD CONSTRAINT permissions_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"))

            conn.commit()

    def _migrate_add_embedding_column(self):
        """Migration 2: Add embedding column to records table."""
        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS embedding vector(1536);"))
            conn.commit()

    # ── Data Seeding ──────────────────────────────────────────────────

    def seed_default_permissions(self):
        """Seed default permissions from JSON data file and ensure lowercase normalization."""
        from .models.identity import Permission
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            # 1. Update existing permissions to be lowercase for matching robustness
            permissions = session.query(Permission).all()
            for p in permissions:
                if p.github_team != p.github_team.lower() or p.github_org != p.github_org.lower():
                    p.github_team = p.github_team.lower()
                    p.github_org = p.github_org.lower()
            session.commit()

            # 2. Seed defaults if table is empty
            if session.query(Permission).count() == 0:
                data_file = Path(__file__).parent / "data" / "default_permissions.json"
                if not data_file.exists():
                    print(f"ERROR: Default permissions data file not found at {data_file}")
                    return

                with open(data_file, encoding='utf-8') as f:
                    perm_data = json.load(f)

                perm_objects = [
                    Permission(
                        github_org=entry["github_org"],
                        github_team=entry["github_team"],
                        role=entry["role"]
                    )
                    for entry in perm_data
                ]
                session.add_all(perm_objects)
                session.commit()
                if not is_production():
                    st.info("Seeded default permissions for Brothertown-Language.")
                else:
                    print("INFO: Seeded default permissions for Brothertown-Language.")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def seed_iso_639_data(self):
        """Seed ISO 639-3 data from local project file if the table is empty."""
        from .models.iso639 import ISO639_3
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            count_before = session.query(ISO639_3).count()

            if count_before == 0:
                data_file = Path(__file__).parent / "data" / "iso-639-3.tab"
                if not data_file.exists():
                    print(f"ERROR: ISO 639-3 data file not found at {data_file}")
                    return

                if not is_production():
                    st.info(f"Seeding ISO 639-3 data from {data_file}...")
                    st.info(f"Records before seeding: {count_before}")
                else:
                    print(f"INFO: Seeding ISO 639-3 data from {data_file}...")
                    print(f"INFO: Records before seeding: {count_before}")

                with open(data_file, encoding='utf-8') as f:
                    content = f.read()

                reader = csv.DictReader(io.StringIO(content), delimiter='\t')

                iso_entries = []
                for row in reader:
                    entry = ISO639_3(
                        id=row['Id'],
                        part2b=row.get('Part2b') or None,
                        part2t=row.get('Part2t') or None,
                        part1=row.get('Part1') or None,
                        scope=row['Scope'],
                        language_type=row['Language_Type'],
                        ref_name=row['Ref_Name'],
                        comment=row.get('Comment') or None
                    )
                    iso_entries.append(entry)

                # Use bulk insert for performance
                session.add_all(iso_entries)
                session.commit()

                count_after = session.query(ISO639_3).count()
                if not is_production():
                    st.info(f"Seeded {len(iso_entries)} ISO 639-3 language records.")
                    st.info(f"Records after seeding: {count_after}")
                else:
                    print(f"INFO: Seeded {len(iso_entries)} ISO 639-3 language records.")
                    print(f"INFO: Records after seeding: {count_after}")
        except Exception as e:
            print(f"ERROR: Failed to seed ISO 639-3 data: {e}")
            session.rollback()
        finally:
            session.close()
