# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Tests for SearchEntry deduplication migration (issue #1285).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)
"""

import os

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

os.environ["OPENCODE"] = "1"

from src.database.connection import init_db
from src.database.migrations import MigrationManager
from src.database.models.core import Record, Source
from src.database.models.search import SearchEntry

DEDUP_MIGRATION_METHOD = "_migrate_dedup_search_entries"
UNIQUE_INDEX_NAME = "uq_search_entries_record_term_type"


@pytest.fixture(scope="module")
def engine():
    """Provide a database engine initialized via init_db."""
    return init_db()


@pytest.fixture()
def session(engine):
    """Provide a database session with test data cleanup after each test."""
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()


def _drop_unique_index_if_exists(engine):
    """Drop the unique index so test data insertion of duplicates can succeed."""
    with engine.connect() as conn:
        conn.execute(text(f"DROP INDEX IF EXISTS {UNIQUE_INDEX_NAME}"))
        conn.commit()


def _insert_test_record(engine):
    """Insert a minimal test record via raw SQL and return its id.

    Uses raw SQL on the engine connection to ensure the record is committed
    and visible to subsequent raw-SQL search_entries inserts on a different
    connection.
    """
    with engine.connect() as conn:
        source_id = conn.execute(text("SELECT id FROM sources LIMIT 1")).scalar()
        if source_id is None:
            conn.execute(
                text("INSERT INTO sources (name) VALUES ('test_dedup_source')")
            )
            conn.commit()
            source_id = conn.execute(text("SELECT id FROM sources LIMIT 1")).scalar()

        record_id = conn.execute(
            text(
                "INSERT INTO records "
                "(lx, ge, mdf_data, source_id, status, current_version, is_deleted, is_locked) "
                "VALUES ('testlx', 'testge', '\\\\lx testlx\\\\nge testge', :sid, 'draft', 1, false, false) "
                "RETURNING id"
            ),
            {"sid": source_id},
        ).scalar()
        conn.commit()
        return record_id


class TestDedupRemovesDuplicatesKeepsLowestId:
    """SC-1: Migration SQL deletes duplicate SearchEntry rows keeping one per (record_id, term, entry_type)."""

    def test_dedup_removes_duplicates_keeps_lowest_id(self, engine, session):
        """Insert duplicate SearchEntry rows, run migration, verify only one row per
        (record_id, term, entry_type) remains with the lowest id."""
        _drop_unique_index_if_exists(engine)

        record_id = _insert_test_record(engine)

        # Insert 3 duplicate rows + 1 distinct via raw SQL
        with engine.connect() as conn:
            for entry_type in ["lx", "lx", "lx", "va"]:
                conn.execute(
                    text(
                        "INSERT INTO search_entries (record_id, term, normalized_term, entry_type) "
                        "VALUES (:rid, :term, :norm, :etype)"
                    ),
                    {"rid": record_id, "term": "wampanoag", "norm": "wampanoag", "etype": entry_type},
                )
            conn.commit()

        # Capture IDs before migration
        Session0 = sessionmaker(bind=engine)
        s0 = Session0()
        lx_ids = [
            row[0]
            for row in s0.execute(
                text(
                    "SELECT id FROM search_entries "
                    "WHERE record_id = :rid AND term = :term AND entry_type = 'lx' ORDER BY id"
                ),
                {"rid": record_id, "term": "wampanoag"},
            ).fetchall()
        ]
        va_ids = [
            row[0]
            for row in s0.execute(
                text(
                    "SELECT id FROM search_entries "
                    "WHERE record_id = :rid AND term = :term AND entry_type = 'va'"
                ),
                {"rid": record_id, "term": "wampanoag"},
            ).fetchall()
        ]
        s0.close()

        assert len(lx_ids) == 3, f"Setup: expected 3 lx entries, got {len(lx_ids)}"
        assert len(va_ids) == 1, f"Setup: expected 1 va entry, got {len(va_ids)}"
        lowest_lx_id = min(lx_ids)
        va_id = va_ids[0]

        # Run migration
        mgr = MigrationManager(engine)
        mgr._migrate_dedup_search_entries()

        # Verify: only one lx row remains with lowest id; va row untouched
        Session2 = sessionmaker(bind=engine)
        s2 = Session2()
        remaining = (
            s2.query(SearchEntry)
            .filter(SearchEntry.record_id == record_id, SearchEntry.term == "wampanoag")
            .all()
        )

        lx_entries = [e for e in remaining if e.entry_type == "lx"]
        va_entries = [e for e in remaining if e.entry_type == "va"]

        assert len(lx_entries) == 1, f"Expected 1 lx entry, got {len(lx_entries)}"
        assert lx_entries[0].id == lowest_lx_id, (
            f"Expected kept id {lowest_lx_id}, got {lx_entries[0].id}"
        )
        assert len(va_entries) == 1, f"Expected 1 va entry, got {len(va_entries)}"
        assert va_entries[0].id == va_id
        s2.close()


class TestDedupIsIdempotent:
    """SC-4: Migration is idempotent (safe to run multiple times)."""

    def test_dedup_is_idempotent(self, engine, session):
        """Run migration twice, verify same result, zero error."""
        _drop_unique_index_if_exists(engine)

        record_id = _insert_test_record(engine)

        # Insert 3 duplicate rows via raw SQL
        with engine.connect() as conn:
            for _ in range(3):
                conn.execute(
                    text(
                        "INSERT INTO search_entries (record_id, term, normalized_term, entry_type) "
                        "VALUES (:rid, :term, :norm, :etype)"
                    ),
                    {"rid": record_id, "term": "idemtest", "norm": "idemtest", "etype": "lx"},
                )
            conn.commit()

        mgr = MigrationManager(engine)
        mgr._migrate_dedup_search_entries()

        Session2 = sessionmaker(bind=engine)
        s2 = Session2()
        count_after_first = (
            s2.query(SearchEntry)
            .filter(SearchEntry.record_id == record_id, SearchEntry.term == "idemtest")
            .count()
        )

        # Run again — must not fail or change row count
        mgr._migrate_dedup_search_entries()

        count_after_second = (
            s2.query(SearchEntry)
            .filter(SearchEntry.record_id == record_id, SearchEntry.term == "idemtest")
            .count()
        )

        assert count_after_first == count_after_second, (
            f"Idempotency violated: {count_after_first} rows after first run, "
            f"{count_after_second} after second"
        )
        s2.close()


class TestUniqueIndexExists:
    """SC-5: Unique index uq_search_entries_record_term_type on (record_id, term, entry_type)."""

    def test_unique_index_exists(self, engine, session):
        """After migration, verify the unique index was created."""
        mgr = MigrationManager(engine)
        mgr._migrate_dedup_search_entries()

        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename = 'search_entries' "
                    "AND indexname = :idx_name"
                ),
                {"idx_name": UNIQUE_INDEX_NAME},
            )
            rows = result.fetchall()

        assert len(rows) == 1, (
            f"Expected unique index '{UNIQUE_INDEX_NAME}', found: {rows}"
        )


class TestUniqueIndexPreventsDuplicateInsert:
    """SC-5: Unique index prevents new duplicates."""

    def test_unique_index_prevents_duplicate_insert(self, engine, session):
        """After migration, attempt to insert a duplicate (same record_id, term, entry_type)
        and verify it raises an error."""
        record_id = _insert_test_record(engine)

        # Insert one valid entry via raw SQL
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO search_entries (record_id, term, normalized_term, entry_type) "
                    "VALUES (:rid, :term, :norm, :etype)"
                ),
                {"rid": record_id, "term": "uniqtest", "norm": "uniqtest", "etype": "lx"},
            )
            conn.commit()

        mgr = MigrationManager(engine)
        mgr._migrate_dedup_search_entries()

        # Attempt duplicate via raw SQL
        with pytest.raises(IntegrityError):
            with engine.connect() as conn:
                conn.execute(
                    text(
                        "INSERT INTO search_entries (record_id, term, normalized_term, entry_type) "
                        "VALUES (:rid, :term, :norm, :etype)"
                    ),
                    {"rid": record_id, "term": "uniqtest", "norm": "uniqtest", "etype": "lx"},
                )
                conn.commit()


class TestDedupPreservesLegitimateDistinctEntries:
    """SC-3: No data loss — only exact duplicates are removed."""

    def test_dedup_preserves_legitimate_distinct_entries(self, engine, session):
        """Insert entries with same record_id and term but different entry_type values,
        run migration, verify all are kept (no data loss)."""
        _drop_unique_index_if_exists(engine)

        record_id = _insert_test_record(engine)

        entry_types = ["lx", "va", "se", "cf"]
        with engine.connect() as conn:
            for et in entry_types:
                conn.execute(
                    text(
                        "INSERT INTO search_entries (record_id, term, normalized_term, entry_type) "
                        "VALUES (:rid, :term, :norm, :etype)"
                    ),
                    {"rid": record_id, "term": "polyptest", "norm": "polyptest", "etype": et},
                )
            conn.commit()

        # Capture IDs
        Session0 = sessionmaker(bind=engine)
        s0 = Session0()
        inserted_ids = [
            row[0]
            for row in s0.execute(
                text(
                    "SELECT id FROM search_entries "
                    "WHERE record_id = :rid AND term = :term ORDER BY id"
                ),
                {"rid": record_id, "term": "polyptest"},
            ).fetchall()
        ]
        s0.close()

        mgr = MigrationManager(engine)
        mgr._migrate_dedup_search_entries()

        Session2 = sessionmaker(bind=engine)
        s2 = Session2()
        remaining = (
            s2.query(SearchEntry)
            .filter(SearchEntry.record_id == record_id, SearchEntry.term == "polyptest")
            .all()
        )

        remaining_types = sorted([e.entry_type for e in remaining])
        assert remaining_types == sorted(entry_types), (
            f"Expected entry_types {sorted(entry_types)}, got {remaining_types}"
        )
        assert len(remaining) == len(entry_types), (
            f"Expected {len(entry_types)} entries, got {len(remaining)}"
        )

        remaining_ids = [e.id for e in remaining]
        for orig_id in inserted_ids:
            assert orig_id in remaining_ids, (
                f"Original id {orig_id} was lost — data loss detected"
            )
        s2.close()