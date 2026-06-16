# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import csv
import io
import json
import time
from pathlib import Path

import streamlit as st
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from src.logging_config import get_logger

from .connection import is_production

logger = get_logger("snea.migrations")


def log_migration_start(version: int, description: str) -> None:
    """Log the start of a migration execution."""
    logger.info("=" * 60)
    logger.info("MIGRATION START: v%s - %s", version, description)
    logger.info("=" * 60)


def log_migration_skip(version: int, description: str, reason: str) -> None:
    """Log when a migration is skipped (already applied or not needed)."""
    logger.info("-" * 60)
    logger.info("MIGRATION SKIP: v%s - %s", version, description)
    logger.info("  Reason: %s", reason)
    logger.info("-" * 60)


def log_migration_complete(version: int, description: str, duration_seconds: float | None = None) -> None:
    """Log the successful completion of a migration."""
    logger.info("=" * 60)
    if duration_seconds is not None:
        logger.info(
            "MIGRATION COMPLETE: v%s - %s (took %.2fs)",
            version,
            description,
            duration_seconds,
        )
    else:
        logger.info("MIGRATION COMPLETE: v%s - %s", version, description)
    logger.info("=" * 60)


def log_migration_error(version: int, description: str, error: Exception) -> None:
    """Log a migration failure with full context."""
    logger.error("=" * 60)
    logger.error("MIGRATION FAILED: v%s - %s", version, description)
    logger.error("  Error: %s: %s", type(error).__name__, str(error))
    logger.error("=" * 60)


class MigrationManager:
    """
    Centralizes schema evolution, versioned migrations, and data seeding.
    Uses the SchemaVersion model to track applied migrations and prevent
    redundant execution.
    """

    # Ordered registry of versioned migrations: (version, method_name, description)
    # AI AGENT DIRECTIVE: Future migration version numbers MUST follow the format:
    # YYYYMMDDSSSSS (Year, Month, Day, and seconds-since-midnight).
    # This number MUST reflect the actual time the migration was added to this file.
    # Incremental values (e.g. +1, +2) are FORBIDDEN.
    # This ensures the migration registry remains in sync with the database schema table.
    # DO NOT renumber existing migrations.
    _MIGRATIONS = [
        (1, "_migrate_cascade_constraints", "Add ON UPDATE CASCADE / ON DELETE RESTRICT constraints"),
        (2, "_migrate_add_embedding_column", "Add embedding vector column to records"),
        (3, "_migrate_add_matchup_queue_columns", "Add batch_id, filename, match_type to matchup_queue"),
        (4, "_migrate_create_record_languages_table", "Create record_languages join table"),
        (5, "_migrate_backfill_record_languages", "Backfill record_languages from existing records"),
        (6, "_migrate_drop_records_language_id", "Drop redundant language_id from records table"),
        (8, "_migrate_add_fts_index", "Add GIN FTS index to records for full-text search"),
        (10, "_migrate_add_sort_lx_column", "Add sort_lx column for NFD-aware sorting"),
        (11, "_migrate_upgrade_version_to_bigint", "Upgrade schema_version.version to BigInteger"),
        (
            2026021585860,
            "_migrate_add_search_entries_index",
            "Add B-tree index to search_entries(term) for prefix matching",
        ),
        (2026021585861, "_migrate_add_normalized_search_entries", "Add normalized_term to search_entries and index it"),
        (2026021585862, "_migrate_renormalize_search_entries", "Re-normalize search_entries for diacritics and quotes"),
        (2026021585863, "_migrate_renormalize_sort_lx", "Re-normalize records.sort_lx for diacritics and quotes"),
        (2026030145060, "_migrate_add_record_locking", "Add is_locked, locked_by, locked_at, and lock_note to records"),
        (
            2026030206285,
            "_migrate_ignore_leading_numerals",
            "Re-normalize records.sort_lx and search_entries.normalized_term to ignore leading numerals",
        ),
        (
            2026030207140,
            "_migrate_reprocess_all_records",
            "Reprocess all records to synchronize languages, search entries, and metadata",
        ),
        (
            20260303080520,
            "_migrate_renormalize_infinity_symbol",
            "Re-normalize sort_lx and normalized_term for \u221e and \u2714 symbol sort order",
        ),
        (
            20260405140917,
            "_migrate_create_headword_search_entries",
            "Create headword_search_entries table for PRIMARY lx and va",
        ),
        (20260405140918, "_migrate_create_gloss_search_entries", "Create gloss_search_entries table for PRIMARY ge"),
        (
            20260413120000,
            "_migrate_add_headword_entry_type_index_and_check",
            "Add entry_type index and CHECK constraint to headword_search_entries",
        ),
        (
            20260415000000,
            "_migrate_ensure_sequences",
            "Create sequences for tables missing autoincrement to match ORM expectations",
        ),
        (
            20260511000001,
            "_migrate_dedup_search_entries",
            "Deduplicate search_entries: keep one row per (record_id, term, entry_type), add unique index",
        ),
        (
            20260613120000,
            "_migrate_replace_fts_vector",
            "Replace records.fts_vector with fts_entries table using 'simple' config",
        ),
        (
            20260615125509,
            "_migrate_backfill_search_entries",
            "Backfill HeadwordSearchEntry and GlossSearchEntry for existing records",
        ),
    ]

    def __init__(self, engine):
        self._engine = engine

    def run_all(self):
        """Public entry point. Runs extensions, migrations, and seeds in order."""
        self._ensure_extensions()
        self._run_migrations()
        self._seed_default_sources()
        self.seed_default_permissions()
        self.seed_iso_639_data()

    # ── Extension Management ──────────────────────────────────────────

    def _ensure_extensions(self):
        """Ensure required PostgreSQL extensions are enabled."""
        with self._engine.connect() as conn:
            # retry logic for extensions to handle startup recovery
            import time

            max_retries = 5
            for attempt in range(max_retries):
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                    break
                except Exception as e:
                    if "shutting down" in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(
                            "DB is shutting down/recovering. Retrying extensions... (%d/%d)", attempt + 1, max_retries
                        )
                        time.sleep(2)
                        continue
                    raise

    # ── Version Tracking ──────────────────────────────────────────────

    def _get_current_version(self) -> int:
        """Return the highest applied migration version, or 0 if none."""
        from .models.meta import SchemaVersion

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            result = session.query(SchemaVersion.version).order_by(SchemaVersion.version.desc()).first()
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
        logger.info("Current schema version: %d", current)

        pending_migrations = [(v, m, d) for v, m, d in self._MIGRATIONS if v > current]
        if not pending_migrations:
            logger.info("No pending migrations to execute.")
            return

        logger.info("Found %d pending migration(s):", len(pending_migrations))
        for version, _method_name, description in pending_migrations:
            logger.info("  - v%s: %s", version, description)

        for version, method_name, description in self._MIGRATIONS:
            if version <= current:
                log_migration_skip(version, description, f"Already applied (current version: {current})")
                continue

            log_migration_start(version, description)
            start_time = time.time()

            try:
                method = getattr(self, method_name)
                method()
                elapsed = time.time() - start_time
                log_migration_complete(version, description, elapsed)
                self._record_migration(version, description)
            except Exception as e:
                log_migration_error(version, description, e)
                raise

    # ── Versioned Migrations ──────────────────────────────────────────

    def _migrate_cascade_constraints(self):
        """Migration 1: Add ON UPDATE CASCADE to user_email foreign keys
        and ON DELETE RESTRICT to entity foreign keys."""
        with self._engine.connect() as conn:
            # 1. user_activity_log
            conn.execute(
                text("ALTER TABLE user_activity_log DROP CONSTRAINT IF EXISTS user_activity_log_user_email_fkey;")
            )
            conn.execute(
                text(
                    "ALTER TABLE user_activity_log ADD CONSTRAINT user_activity_log_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )

            # 2. matchup_queue
            conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_user_email_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )

            # 3. edit_history
            conn.execute(text("ALTER TABLE edit_history DROP CONSTRAINT IF EXISTS edit_history_user_email_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE edit_history ADD CONSTRAINT edit_history_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )

            # 4. records (updated_by)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_updated_by_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE records ADD CONSTRAINT records_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )

            # 5. records (reviewed_by)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_reviewed_by_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE records ADD CONSTRAINT records_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )

            # 6. records (language_id) - DEPRECATED (dropped in migration 6)
            # conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_language_id_fkey;"))
            # conn.execute(text("ALTER TABLE records ADD CONSTRAINT records_language_id_fkey FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE RESTRICT;"))

            # 7. records (source_id)
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_source_id_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE records ADD CONSTRAINT records_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"
                )
            )

            # 8. search_entries (record_id)
            conn.execute(text("ALTER TABLE search_entries DROP CONSTRAINT IF EXISTS search_entries_record_id_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE search_entries ADD CONSTRAINT search_entries_record_id_fkey FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE RESTRICT;"
                )
            )

            # 9. matchup_queue (source_id)
            conn.execute(text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_source_id_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"
                )
            )

            # 10. matchup_queue (suggested_record_id)
            conn.execute(
                text("ALTER TABLE matchup_queue DROP CONSTRAINT IF EXISTS matchup_queue_suggested_record_id_fkey;")
            )
            conn.execute(
                text(
                    "ALTER TABLE matchup_queue ADD CONSTRAINT matchup_queue_suggested_record_id_fkey FOREIGN KEY (suggested_record_id) REFERENCES records(id) ON DELETE RESTRICT;"
                )
            )

            # 11. permissions (source_id)
            conn.execute(text("ALTER TABLE permissions DROP CONSTRAINT IF EXISTS permissions_source_id_fkey;"))
            conn.execute(
                text(
                    "ALTER TABLE permissions ADD CONSTRAINT permissions_source_id_fkey FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;"
                )
            )

            conn.commit()

    def _migrate_add_embedding_column(self):
        """Migration 2: Add embedding column to records table."""
        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS embedding vector(1536);"))
            conn.commit()

    def _migrate_add_matchup_queue_columns(self):
        """Migration 3: Add batch_id, filename, and match_type columns to matchup_queue."""
        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE matchup_queue ADD COLUMN IF NOT EXISTS batch_id VARCHAR;"))
            conn.execute(text("ALTER TABLE matchup_queue ADD COLUMN IF NOT EXISTS filename VARCHAR;"))
            conn.execute(text("ALTER TABLE matchup_queue ADD COLUMN IF NOT EXISTS match_type VARCHAR;"))
            # Backfill batch_id for any pre-existing rows so NOT NULL can be enforced
            conn.execute(text("UPDATE matchup_queue SET batch_id = 'legacy' WHERE batch_id IS NULL;"))
            conn.execute(text("ALTER TABLE matchup_queue ALTER COLUMN batch_id SET NOT NULL;"))
            conn.commit()

    def _migrate_create_record_languages_table(self):
        """Migration 4: Create record_languages join table."""
        with self._engine.connect() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS record_languages (
                    id SERIAL PRIMARY KEY,
                    record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
                    language_id INTEGER NOT NULL REFERENCES languages(id) ON DELETE RESTRICT,
                    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            )
            conn.commit()

    def _migrate_backfill_record_languages(self):
        """Migration 5: Backfill record_languages from existing records' MDF data."""
        from src.mdf.parser import parse_mdf

        from .models.core import Language, Record, RecordLanguage

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            # If tables are empty, reset autoincrement values
            if session.query(Language).count() == 0:
                logger.info("Languages table is empty, resetting autoincrement value.")
                session.execute(text("ALTER SEQUENCE languages_id_seq RESTART WITH 1"))

            if session.query(RecordLanguage).count() == 0:
                logger.info("RecordLanguages table is empty, resetting autoincrement value.")
                session.execute(text("ALTER SEQUENCE record_languages_id_seq RESTART WITH 1"))

            records = session.query(Record).all()
            for rec in records:
                # 1. Parse \lg entries from raw mdf_data
                parsed = parse_mdf(rec.mdf_data)
                if not parsed:
                    continue
                lg_entries = parsed[0].get("lg", [])

                # 2. If no \lg values found in MDF, fallback to existing language_id if it exists
                # We need to peek at language_id before dropping it in next migration.
                # Use raw SQL to avoid relying on model which no longer has this column.
                row = session.execute(text("SELECT language_id FROM records WHERE id = :id"), {"id": rec.id}).first()
                existing_lang_id = row[0] if row else None

                if not lg_entries and existing_lang_id:
                    # Create one entry from the old foreign key
                    rl = RecordLanguage(record_id=rec.id, language_id=existing_lang_id, is_primary=True)
                    session.add(rl)
                else:
                    # Create entries for each parsed \lg
                    for _i, lg in enumerate(lg_entries):
                        lg_name = lg["name"]
                        lg_code = lg["code"]

                        # Find or create Language entry
                        lang = session.query(Language).filter_by(name=lg_name).first()
                        if not lang and lg_code:
                            lang = session.query(Language).filter_by(code=lg_code).first()

                        if not lang:
                            final_code = lg_code if lg_code else lg_name[:10]
                            lang = Language(name=lg_name, code=final_code)
                            session.add(lang)
                            session.flush()
                        elif lg_code and not lang.code:
                            lang.code = lg_code
                            session.flush()

                        rl = RecordLanguage(
                            record_id=rec.id, language_id=lang.id, is_primary=lg.get("is_primary", False)
                        )
                        session.add(rl)
            session.commit()
        except Exception as e:
            logger.error(f"Backfill failed: {e}")
            session.rollback()
            raise e
        finally:
            session.close()

    def _migrate_drop_records_language_id(self):
        """Migration 6: Drop redundant language_id from records table."""
        with self._engine.connect() as conn:
            # We must drop the constraint first
            conn.execute(text("ALTER TABLE records DROP CONSTRAINT IF EXISTS records_language_id_fkey;"))
            conn.execute(text("ALTER TABLE records DROP COLUMN IF EXISTS language_id;"))
            conn.commit()

    def _migrate_add_fts_index(self):
        """Migration 8: Add GIN FTS index to records table."""
        with self._engine.connect() as conn:
            # Create a generated column for FTS
            conn.execute(
                text("""
                ALTER TABLE records ADD COLUMN IF NOT EXISTS fts_vector tsvector
                GENERATED ALWAYS AS (
                    to_tsvector('english', coalesce(lx, '') || ' ' || coalesce(ge, '') || ' ' || coalesce(mdf_data, ''))
                ) STORED;
            """)
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_fts ON records USING gin (fts_vector);"))
            conn.commit()

    def _migrate_add_search_entries_index(self):
        """Migration 2026021585860: Add index to search_entries table."""
        with self._engine.connect() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_search_entries_term ON search_entries (term);"))
            conn.commit()

    def _migrate_upgrade_version_to_bigint(self):
        """Migration 11: Upgrade version column to BigInteger."""
        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE schema_version ALTER COLUMN version TYPE BIGINT;"))
            conn.commit()

    def _migrate_add_normalized_search_entries(self):
        """Migration 2026021585861: Add normalized_term to search_entries table."""
        from src.services.linguistic_service import LinguisticService

        from .models.search import SearchEntry

        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE search_entries ADD COLUMN IF NOT EXISTS normalized_term VARCHAR;"))
            conn.commit()

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            # Backfill normalized_term for all entries
            entries = session.query(SearchEntry).filter(SearchEntry.normalized_term.is_(None)).all()
            if entries:
                logger.info(f"Backfilling normalized_term for {len(entries)} search entries...")
                for entry in entries:
                    entry.normalized_term = LinguisticService.generate_sort_lx(entry.term)
                session.commit()
                logger.info("Normalized_term backfill complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to backfill normalized_term: {e}")
            raise e
        finally:
            session.close()

        with self._engine.connect() as conn:
            # Drop old index if it exists and create new one on normalized_term
            conn.execute(text("DROP INDEX IF EXISTS idx_search_entries_term;"))
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_search_entries_normalized_term ON search_entries (normalized_term);"
                )
            )
            # Make the column NOT NULL after backfilling
            conn.execute(text("ALTER TABLE search_entries ALTER COLUMN normalized_term SET NOT NULL;"))
            conn.commit()

    def _migrate_renormalize_search_entries(self):
        """Migration 2026021585862: Re-normalize search_entries.normalized_term."""
        from src.services.linguistic_service import LinguisticService

        from .models.search import SearchEntry

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            logger.info("Re-normalizing search_entries (diacritics and quotes)...")
            # We process in batches if there are many, but here we just do all
            entries = session.query(SearchEntry).all()
            for entry in entries:
                entry.normalized_term = LinguisticService.generate_sort_lx(entry.term)
            session.commit()
            logger.info("search_entries re-normalization complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to re-normalize search_entries: {e}")
            raise e
        finally:
            session.close()

    def _migrate_renormalize_sort_lx(self):
        """Migration 2026021585863: Re-normalize records.sort_lx."""
        from src.services.linguistic_service import LinguisticService

        from .models.core import Record

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            logger.info("Re-normalizing records.sort_lx (diacritics and quotes)...")
            records = session.query(Record).all()
            for record in records:
                record.sort_lx = LinguisticService.generate_sort_lx(record.lx)
            session.commit()
            logger.info("records.sort_lx re-normalization complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to re-normalize records.sort_lx: {e}")
            raise e
        finally:
            session.close()

    def _migrate_add_sort_lx_column(self):
        """Migration 9: Add sort_lx column to records and backfill existing data."""
        from src.services.linguistic_service import LinguisticService

        from .models.core import Record

        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS sort_lx VARCHAR;"))
            conn.commit()

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            # Backfill existing records
            records = session.query(Record).filter(Record.sort_lx.is_(None)).all()
            if records:
                logger.info(f"Backfilling sort_lx for {len(records)} records...")
                for record in records:
                    record.sort_lx = LinguisticService.generate_sort_lx(record.lx)
                session.commit()
                logger.info("Sort_lx backfill complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to backfill sort_lx: {e}")
            raise e
        finally:
            session.close()

        with self._engine.connect() as conn:
            # Headword (\lx) -> Homonym (\hm) -> Part of Speech (\ps) -> Gloss (\ge)
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_sort_lx ON records (sort_lx);"))
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS idx_records_sorting_composite ON records (sort_lx, hm, ps, ge);")
            )
            conn.commit()

    def _migrate_add_record_locking(self):
        """Migration 2026030145060: Add is_locked, locked_by, locked_at, and lock_note to records."""
        with self._engine.connect() as conn:
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS is_locked BOOLEAN NOT NULL DEFAULT FALSE;"))
            conn.execute(
                text(
                    "ALTER TABLE records ADD COLUMN IF NOT EXISTS locked_by TEXT REFERENCES users(email) ON UPDATE CASCADE ON DELETE RESTRICT;"
                )
            )
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE records ADD COLUMN IF NOT EXISTS lock_note TEXT;"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_records_is_locked ON records(is_locked);"))
            conn.commit()

    def _migrate_ignore_leading_numerals(self):
        """Migration 2026030206285: Re-normalize records.sort_lx and search_entries.normalized_term to ignore leading numerals."""
        from src.services.linguistic_service import LinguisticService

        from .models.core import Record
        from .models.search import SearchEntry

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            logger.info(
                "Re-normalizing records.sort_lx and search_entries.normalized_term (ignoring leading numerals)..."
            )

            # 1. Update records.sort_lx
            records = session.query(Record).all()
            for record in records:
                record.sort_lx = LinguisticService.generate_sort_lx(record.lx)

            # 2. Update search_entries.normalized_term
            entries = session.query(SearchEntry).all()
            for entry in entries:
                entry.normalized_term = LinguisticService.generate_sort_lx(entry.term)

            session.commit()
            logger.info("Re-normalization for leading numerals complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to re-normalize for leading numerals: {e}")
            raise e
        finally:
            session.close()

    def _migrate_renormalize_infinity_symbol(self):
        """Migration 20260303080520: Re-normalize records.sort_lx and search_entries.normalized_term for ∞ and ✔ symbol sort order."""
        from src.services.linguistic_service import LinguisticService

        from .models.core import Record
        from .models.search import SearchEntry

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            logger.info(
                "Re-normalizing records.sort_lx and search_entries.normalized_term (∞ and ✔ symbol sort order)..."
            )

            # 1. Update records.sort_lx
            records = session.query(Record).all()
            for record in records:
                record.sort_lx = LinguisticService.generate_sort_lx(record.lx)

            # 2. Update search_entries.normalized_term
            entries = session.query(SearchEntry).all()
            for entry in entries:
                entry.normalized_term = LinguisticService.generate_sort_lx(entry.term)

            session.commit()
            logger.info("Re-normalization for ∞ and ✔ symbol sort order complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to re-normalize for ∞ and ✔ symbol sort order: {e}")
            raise e
        finally:
            session.close()

    def _migrate_reprocess_all_records(self):
        """Migration 2026030207140: Reprocess all records to synchronize languages, search entries, and metadata."""
        from src.services.upload_service import UploadService

        # Use the migration's own engine session, not get_session() (which connects to production)
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            logger.info("Starting global record reprocessing migration...")
            results = UploadService.reprocess_all_records(session=session)
            session.commit()
            logger.info(f"Migration reprocessed {results.get('reprocessed', 0)}/{results.get('total', 0)} records.")
        except Exception as e:
            session.rollback()
            logger.error(f"Migration 2026030207140 failed: {e}")
            raise
        finally:
            session.close()

    def _migrate_backfill_search_entries(self):
        """Migration 20260615125509: Backfill HeadwordSearchEntry and GlossSearchEntry for existing records."""
        from src.services.upload_service import UploadService

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            from .models.core import Record

            records = session.query(Record).filter(Record.is_deleted.isnot(True)).all()
            all_ids = [r.id for r in records]
            logger.info(f"Backfilling search entries for {len(all_ids)} records...")
            UploadService.populate_search_entries(record_ids=all_ids, session=session)
            session.commit()
            logger.info("Backfill complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to backfill search entries: {e}")
            raise
        finally:
            session.close()

    def _seed_default_sources(self):
        """Seed default sources if table is empty or missing specific entries."""
        from .models.core import Record, Source

        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            # If table is empty, reset autoincrement value
            source_count = session.query(Source).count()
            if source_count == 0:
                logger.info("Sources table is empty, resetting autoincrement value.")
                session.execute(text("ALTER SEQUENCE sources_id_seq RESTART WITH 1"))
                session.commit()

            # Reset records autoincrement if empty
            record_count = session.query(Record).count()
            if record_count == 0:
                logger.info("Records table is empty, resetting autoincrement value.")
                session.execute(text("ALTER SEQUENCE records_id_seq RESTART WITH 1"))
                session.commit()

            default_sources = [
                {
                    "name": "Trumbull 1903",
                    "short_name": "Trumbull (1903)",
                    "description": "Wampanoag [wam]",
                    "citation_format": "Trumbull, James Hammond. (1903). *Natick Dictionary*. Bureau of American Ethnology Bulletin 25. Washington: Government Printing Office.",
                },
                {
                    "name": "Fielding 2012",
                    "short_name": "Fielding (2012)",
                    "description": "Mohegan-Pequot [xpq]",
                    "citation_format": "Fielding, Stephanie. (2013). *A Modern Mohegan Dictionary*. (D. J. Costa, Ed.). Uncasville, CT: Mohegan Council of Elders.",
                },
                {
                    "name": "Anonymous 1647",
                    "short_name": None,
                    "description": "Wampanoag [wam]",
                    "citation_format": None,
                },
                {"name": "Winslow 1624", "short_name": None, "description": "Wampanoag [wam]", "citation_format": None},
                {"name": "Wood 1634", "short_name": None, "description": "Wampanoag [wam]", "citation_format": None},
                {
                    "name": "Prince-Speck 1904",
                    "short_name": None,
                    "description": "Mohegan-Pequot [xpq]",
                    "citation_format": None,
                },
                {
                    "name": "Williams 1643",
                    "short_name": None,
                    "description": "Narragansett [xnt]",
                    "citation_format": None,
                },
            ]

            for src_data in default_sources:
                existing = session.query(Source).filter_by(name=src_data["name"]).first()
                if not existing:
                    new_source = Source(**src_data)
                    session.add(new_source)
                    logger.info(f"Seeded source: {src_data['name']}")

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to seed default sources: {e}")
            raise e
        finally:
            session.close()

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
                logger.info("Permissions table is empty, resetting autoincrement value.")
                session.execute(text("ALTER SEQUENCE permissions_id_seq RESTART WITH 1"))
                data_file = Path(__file__).parent / "data" / "default_permissions.json"
                if not data_file.exists():
                    logger.error("Default permissions data file not found at %s", data_file)
                    return

                with open(data_file, encoding="utf-8") as f:
                    perm_data = json.load(f)

                perm_objects = [
                    Permission(github_org=entry["github_org"], github_team=entry["github_team"], role=entry["role"])
                    for entry in perm_data
                ]
                session.add_all(perm_objects)
                session.commit()
                if not is_production():
                    st.info("Seeded default permissions for Brothertown-Language.")
                else:
                    logger.info("Seeded default permissions for Brothertown-Language.")
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
                    logger.error("ISO 639-3 data file not found at %s", data_file)
                    return

                if not is_production():
                    st.info(f"Seeding ISO 639-3 data from {data_file}...")
                    st.info(f"Records before seeding: {count_before}")
                else:
                    logger.info("Seeding ISO 639-3 data from %s...", data_file)
                    logger.info("Records before seeding: %d", count_before)

                with open(data_file, encoding="utf-8") as f:
                    content = f.read()

                reader = csv.DictReader(io.StringIO(content), delimiter="\t")

                iso_entries = []
                for row in reader:
                    entry = ISO639_3(
                        id=row["Id"],
                        part2b=row.get("Part2b") or None,
                        part2t=row.get("Part2t") or None,
                        part1=row.get("Part1") or None,
                        scope=row["Scope"],
                        language_type=row["Language_Type"],
                        ref_name=row["Ref_Name"],
                        comment=row.get("Comment") or None,
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
                    logger.info("Seeded %d ISO 639-3 language records.", len(iso_entries))
                    logger.info("Records after seeding: %d", count_after)
        except Exception as e:
            logger.error("Failed to seed ISO 639-3 data: %s", e)
            session.rollback()
        finally:
            session.close()

    def _migrate_create_headword_search_entries(self):
        """Migration 20260405140917: Create headword_search_entries table for PRIMARY lx and va."""
        with self._engine.connect() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS headword_search_entries (
                    id SERIAL PRIMARY KEY,
                    record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE RESTRICT,
                    entry_type VARCHAR NOT NULL,
                    term VARCHAR NOT NULL,
                    normalized_term VARCHAR NOT NULL
                );
            """)
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_headword_search_entries_normalized_term ON headword_search_entries (normalized_term);"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_headword_search_entries_record_id ON headword_search_entries (record_id);"
                )
            )
            conn.commit()

    def _migrate_add_headword_entry_type_index_and_check(self):
        """Migration 20260413120000: Add entry_type index and CHECK constraint to headword_search_entries."""
        with self._engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_headword_search_entries_entry_type ON headword_search_entries (entry_type);"
                )
            )
            conn.execute(text("ALTER TABLE headword_search_entries DROP CONSTRAINT IF EXISTS chk_headword_entry_type;"))
            conn.execute(
                text(
                    "ALTER TABLE headword_search_entries ADD CONSTRAINT chk_headword_entry_type CHECK (entry_type IN ('lx', 'va'));"
                )
            )
            conn.commit()

    def _migrate_ensure_sequences(self):
        """Migration 20260415000000: Create sequences for tables missing autoincrement.

        Production DDL uses plain integer NOT NULL for id columns on most tables
        (no SERIAL, no IDENTITY, no DEFAULT nextval). The ORM models declare
        autoincrement=True. This migration creates sequences for all tables that
        have an integer id column but no associated sequence, and sets the column
        default to nextval().
        """
        with self._engine.connect() as conn:
            tables = [
                r[0]
                for r in conn.execute(
                    text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'")
                ).fetchall()
            ]
            for tname in tables:
                seq = conn.execute(text("SELECT pg_get_serial_sequence(:t, 'id')"), {"t": tname}).scalar()
                if seq:
                    continue
                has_int_id = conn.execute(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
                        "WHERE table_name = :t AND column_name = 'id' AND data_type = 'integer')"
                    ),
                    {"t": tname},
                ).scalar()
                if has_int_id:
                    seq_name = f"{tname}_id_seq"
                    conn.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {seq_name}"))
                    max_id = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {tname}")).scalar()
                    conn.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_id + 1}"))
                    conn.execute(text(f"ALTER TABLE {tname} ALTER COLUMN id SET DEFAULT nextval('{seq_name}')"))
            conn.commit()

    def _migrate_create_gloss_search_entries(self):
        """Migration 20260405140918: Create gloss_search_entries table for PRIMARY ge."""
        with self._engine.connect() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS gloss_search_entries (
                    id SERIAL PRIMARY KEY,
                    record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE RESTRICT,
                    term VARCHAR NOT NULL,
                    normalized_term VARCHAR NOT NULL
                );
            """)
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_gloss_search_entries_normalized_term ON gloss_search_entries (normalized_term);"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_gloss_search_entries_record_id ON gloss_search_entries (record_id);"
                )
            )
            conn.commit()

    def _migrate_dedup_search_entries(self):
        """Migration 20260511000001: Deduplicate search_entries and add unique index."""
        with self._engine.connect() as conn:
            conn.execute(
                text(
                    "DELETE FROM search_entries WHERE id NOT IN "
                    "(SELECT MIN(id) FROM search_entries GROUP BY record_id, term, entry_type);"
                )
            )
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_search_entries_record_term_type "
                    "ON search_entries (record_id, term, entry_type);"
                )
            )
            conn.commit()

    def _migrate_replace_fts_vector(self):
        """Migration 20260613120000: Replace records.fts_vector with fts_entries table."""
        from src.services.linguistic_service import LinguisticService

        from .models.core import Record

        with self._engine.connect() as conn:
            # 1. Create fts_entries table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS fts_entries (
                    id SERIAL PRIMARY KEY,
                    record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
                    fts_vector TSVECTOR NOT NULL
                );
            """)
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fts_entries_record_id ON fts_entries (record_id);"))
            conn.commit()

        # 2. Populate fts_entries from all records using generate_sort_lx() + to_tsvector('simple')
        Session = sessionmaker(bind=self._engine)
        session = Session()
        try:
            records = session.query(Record).filter(Record.is_deleted == False).all()
            logger.info(f"Populating fts_entries for {len(records)} records...")
            for record in records:
                norm_text = LinguisticService.generate_sort_lx(record.mdf_data)
                if norm_text:
                    session.execute(
                        text(
                            "INSERT INTO fts_entries (record_id, fts_vector) "
                            "VALUES (:rid, to_tsvector('simple', :norm))"
                        ),
                        {"rid": record.id, "norm": norm_text},
                    )
            session.commit()
            logger.info("fts_entries population complete.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to populate fts_entries: {e}")
            raise
        finally:
            session.close()

        with self._engine.connect() as conn:
            # 3. Create GIN index on fts_entries.fts_vector
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS idx_fts_entries_vector ON fts_entries USING gin (fts_vector);")
            )
            # 4. Drop old GIN index on records.fts_vector
            conn.execute(text("DROP INDEX IF EXISTS idx_records_fts;"))
            # 5. Drop old generated column
            conn.execute(text("ALTER TABLE records DROP COLUMN IF EXISTS fts_vector;"))
            conn.commit()
