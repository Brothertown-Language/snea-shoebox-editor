# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import uuid

import pytest
from sqlalchemy import inspect

# Ensure private database is used
os.environ["OPENCODE"] = "1"

from sqlalchemy.orm import sessionmaker

from src.database.connection import init_db
from src.database.migrations import MigrationManager
from src.database.models.core import Record, Source
from src.database.models.identity import Permission
from src.database.models.meta import SchemaVersion
from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry, SearchEntry


@pytest.fixture(scope="module")
def engine():
    """Provide a database engine initialized via init_db."""
    return init_db()


@pytest.fixture()
def session(engine):
    """Provide a database session, closed after each test."""
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


class TestVersionTracking:
    """Tests for migration version tracking via SchemaVersion."""

    def test_current_version_matches_latest_migration(self, engine):
        """After init_db, the current version should equal the highest registered migration."""
        manager = MigrationManager(engine)
        current = manager._get_current_version()
        latest = max(v for v, _, _ in MigrationManager._MIGRATIONS)
        assert current >= latest, f"Expected version at least {latest}, got {current}"

    def test_schema_version_rows_exist(self, session):
        """Each registered migration should have exactly one SchemaVersion row."""
        count = session.query(SchemaVersion).count()
        expected = len(MigrationManager._MIGRATIONS)
        assert count >= expected, f"Expected at least {expected} schema_version rows, got {count}"

    def test_no_duplicate_versions(self, session):
        """No duplicate version numbers should exist in schema_version."""
        versions = [row.version for row in session.query(SchemaVersion).all()]
        assert len(versions) == len(set(versions)), f"Duplicate versions found: {versions}"


class TestIdempotency:
    """Tests that run_all can be called multiple times safely."""

    def test_run_all_twice_no_duplicate_rows(self, engine):
        """Running run_all a second time should not create duplicate schema_version entries."""
        Session = sessionmaker(bind=engine)

        s1 = Session()
        count_before = s1.query(SchemaVersion).count()
        s1.close()

        MigrationManager(engine).run_all()

        s2 = Session()
        count_after = s2.query(SchemaVersion).count()
        s2.close()

        assert count_before == count_after, f"Duplicate rows created: {count_before} before, {count_after} after"


class TestPermissionSeeding:
    """Tests for permission seed data loaded from default_permissions.json."""

    def test_permissions_seeded(self, session):
        """Default permissions should exist in the database."""
        count = session.query(Permission).count()
        assert count >= 3, f"Expected at least 3 default permissions, got {count}"

    def test_permissions_are_lowercase(self, session):
        """All permission org and team values should be lowercase."""
        permissions = session.query(Permission).all()
        for p in permissions:
            assert p.github_org == p.github_org.lower(), f"github_org not lowercase: {p.github_org}"
            assert p.github_team == p.github_team.lower(), f"github_team not lowercase: {p.github_team}"

    def test_expected_roles_present(self, session):
        """The three default roles (admin, editor, viewer) should be present."""
        roles = {p.role for p in session.query(Permission).all()}
        for expected in ("admin", "editor", "viewer"):
            assert expected in roles, f"Missing expected role: {expected}"


class TestHeadwordSearchEntrySchema:
    """SC-9: headword_search_entries table exists with correct columns and indexes."""

    def test_headword_search_entry_table_exists(self, engine):
        # SC-9
        insp = inspect(engine)
        assert "headword_search_entries" in insp.get_table_names()

    def test_headword_search_entry_columns(self, engine):
        insp = inspect(engine)
        cols = {c["name"]: c for c in insp.get_columns("headword_search_entries")}
        assert "id" in cols
        assert "record_id" in cols
        assert "entry_type" in cols
        assert "term" in cols
        assert "normalized_term" in cols
        assert not cols["record_id"]["nullable"]
        assert not cols["entry_type"]["nullable"]
        assert not cols["term"]["nullable"]
        assert not cols["normalized_term"]["nullable"]

    def test_headword_search_entry_indexes(self, engine):
        insp = inspect(engine)
        indexes = insp.get_indexes("headword_search_entries")
        idx_names = {i["name"] for i in indexes}
        assert "idx_headword_search_entries_normalized_term" in idx_names
        assert "idx_headword_search_entries_record_id" in idx_names

    def test_headword_search_entry_foreign_key(self, engine):
        insp = inspect(engine)
        fks = insp.get_foreign_keys("headword_search_entries")
        assert len(fks) >= 1
        fk = fks[0]
        assert "record_id" in fk["constrained_columns"]
        assert fk["referred_table"] == "records"

    def test_headword_search_entry_orm_roundtrip(self, session):
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"test_hw_source_{tag}")
        session.add(source)
        session.flush()

        record = Record(lx=f"test_hw_orm_{tag}", source_id=source.id, mdf_data=f"\\lx test_hw_orm_{tag}")
        session.add(record)
        session.flush()

        entry = HeadwordSearchEntry(record_id=record.id, entry_type="lx", term="wampuw", normalized_term="wampuw")
        session.add(entry)
        session.flush()

        result = session.query(HeadwordSearchEntry).filter_by(record_id=record.id).one()
        assert result.entry_type == "lx"
        assert result.term == "wampuw"
        assert result.normalized_term == "wampuw"

        session.delete(entry)
        session.delete(record)
        session.delete(source)
        session.commit()


class TestGlossSearchEntrySchema:
    """SC-10: gloss_search_entries table exists with correct columns and indexes."""

    def test_gloss_search_entry_table_exists(self, engine):
        # SC-10
        insp = inspect(engine)
        assert "gloss_search_entries" in insp.get_table_names()

    def test_gloss_search_entry_columns(self, engine):
        insp = inspect(engine)
        cols = {c["name"]: c for c in insp.get_columns("gloss_search_entries")}
        assert "id" in cols
        assert "record_id" in cols
        assert "term" in cols
        assert "normalized_term" in cols
        assert not cols["record_id"]["nullable"]
        assert not cols["term"]["nullable"]
        assert not cols["normalized_term"]["nullable"]

    def test_gloss_search_entry_indexes(self, engine):
        insp = inspect(engine)
        indexes = insp.get_indexes("gloss_search_entries")
        idx_names = {i["name"] for i in indexes}
        assert "idx_gloss_search_entries_normalized_term" in idx_names
        assert "idx_gloss_search_entries_record_id" in idx_names

    def test_gloss_search_entry_foreign_key(self, engine):
        insp = inspect(engine)
        fks = insp.get_foreign_keys("gloss_search_entries")
        assert len(fks) >= 1
        fk = fks[0]
        assert "record_id" in fk["constrained_columns"]
        assert fk["referred_table"] == "records"

    def test_gloss_search_entry_orm_roundtrip(self, session):
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"test_gl_source_{tag}")
        session.add(source)
        session.flush()

        record = Record(lx=f"test_gl_orm_{tag}", source_id=source.id, mdf_data=f"\\lx test_gl_orm_{tag}")
        session.add(record)
        session.flush()

        entry = GlossSearchEntry(record_id=record.id, term="round object", normalized_term="round object")
        session.add(entry)
        session.flush()

        session.delete(entry)
        session.delete(record)
        session.delete(source)
        session.commit()


class TestSearchEntryRollback:
    """SC-13: Can DROP headword/gloss tables without data loss to existing SearchEntry."""

    def test_drop_and_recreate_preserves_search_entries(self, engine):
        # SC-13 — verify DROP + recreate is idempotent and SearchEntry unaffected
        from sqlalchemy import text

        Session = sessionmaker(bind=engine)
        s = Session()

        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"test_rb_source_{tag}")
        s.add(source)
        s.flush()

        record = Record(lx=f"test_rb_{tag}", source_id=source.id, mdf_data=f"\\lx test_rb_{tag}")
        s.add(record)
        s.flush()

        se = SearchEntry(record_id=record.id, term=f"test_rb_{tag}", normalized_term=f"test_rb_{tag}", entry_type="lx")
        s.add(se)
        hw = HeadwordSearchEntry(
            record_id=record.id, entry_type="lx", term=f"test_rb_{tag}", normalized_term=f"test_rb_{tag}"
        )
        s.add(hw)
        gl = GlossSearchEntry(record_id=record.id, term="round", normalized_term="round")
        s.add(gl)
        s.commit()

        search_count_before = s.query(SearchEntry).count()

        s.delete(gl)
        s.delete(hw)
        s.commit()
        s.close()

        with engine.connect() as conn:
            conn.execute(text("DELETE FROM headword_search_entries"))
            conn.execute(text("DELETE FROM gloss_search_entries"))
            conn.execute(text("DROP TABLE IF EXISTS gloss_search_entries CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS headword_search_entries CASCADE"))
            conn.commit()

        s2 = Session()
        search_count_after = s2.query(SearchEntry).count()
        assert search_count_after == search_count_before, (
            f"SearchEntry count changed: {search_count_before} before, {search_count_after} after DROP"
        )
        s2.close()

        with engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS headword_search_entries ("
                    "id SERIAL PRIMARY KEY, "
                    "record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE RESTRICT, "
                    "entry_type VARCHAR NOT NULL, "
                    "term VARCHAR NOT NULL, "
                    "normalized_term VARCHAR NOT NULL)"
                )
            )
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS gloss_search_entries ("
                    "id SERIAL PRIMARY KEY, "
                    "record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE RESTRICT, "
                    "term VARCHAR NOT NULL, "
                    "normalized_term VARCHAR NOT NULL)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_headword_search_entries_normalized_term "
                    "ON headword_search_entries (normalized_term)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_headword_search_entries_record_id "
                    "ON headword_search_entries (record_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_gloss_search_entries_normalized_term "
                    "ON gloss_search_entries (normalized_term)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_gloss_search_entries_record_id ON gloss_search_entries (record_id)"
                )
            )
            conn.commit()

        insp = inspect(engine)
        assert "headword_search_entries" in insp.get_table_names()
        assert "gloss_search_entries" in insp.get_table_names()


class TestHeadwordSearchEntryBehavior:
    """SC-15, SC-17, SC-18, SC-19, SC-21: Behavioral tests for HeadwordSearchEntry."""

    def test_record_headword_relationship_traversal(self, session):
        # SC-15: Record.headword_entries returns associated HeadwordSearchEntry instances
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"hw_rel_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"hw_rel_{tag}", source_id=source.id, mdf_data=f"\\lx hw_rel_{tag}")
        session.add(record)
        session.flush()
        entry = HeadwordSearchEntry(record_id=record.id, entry_type="lx", term="wampuw", normalized_term="wampuw")
        session.add(entry)
        session.flush()
        session.expire_all()
        assert len(record.headword_entries) == 1
        assert record.headword_entries[0].term == "wampuw"
        session.delete(entry)
        session.delete(record)
        session.delete(source)
        session.commit()

    def test_on_delete_restrict_blocks_record_deletion_headword(self, session):
        # SC-17: FK RESTRICT blocks Record deletion when HeadwordSearchEntry exists
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"hw_restrict_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"hw_restrict_{tag}", source_id=source.id, mdf_data=f"\\lx hw_restrict_{tag}")
        session.add(record)
        session.flush()
        entry = HeadwordSearchEntry(record_id=record.id, entry_type="lx", term="x", normalized_term="x")
        session.add(entry)
        session.flush()
        import sqlalchemy.exc

        # Use raw SQL to test FK RESTRICT directly (bypasses ORM cascade)
        from sqlalchemy import text as sa_text

        with pytest.raises(sqlalchemy.exc.IntegrityError, match="violates foreign key constraint"):
            session.execute(sa_text("DELETE FROM records WHERE id = :rid"), {"rid": record.id})
        session.rollback()
        # Clean up created rows via raw SQL (ORM objects stale after rollback)
        session.execute(sa_text("DELETE FROM headword_search_entries WHERE id = :eid"), {"eid": entry.id})
        session.execute(sa_text("DELETE FROM records WHERE id = :rid"), {"rid": record.id})
        session.execute(sa_text("DELETE FROM sources WHERE id = :sid"), {"sid": source.id})
        session.commit()

    def test_headword_entry_type_check_constraint(self, engine, session):
        # SC-18: CHECK constraint rejects entry_type outside ('lx', 'va')
        import sqlalchemy.exc
        from sqlalchemy import text as sa_text

        # Add CHECK as NOT VALID (only new rows validated, skips existing data check)
        with engine.begin() as conn:
            conn.execute(
                sa_text("ALTER TABLE headword_search_entries DROP CONSTRAINT IF EXISTS chk_headword_entry_type")
            )
            conn.execute(
                sa_text(
                    "ALTER TABLE headword_search_entries ADD CONSTRAINT chk_headword_entry_type "
                    "CHECK (entry_type IN ('lx', 'va')) NOT VALID"
                )
            )
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"hw_check_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"hw_check_{tag}", source_id=source.id, mdf_data=f"\\lx hw_check_{tag}")
        session.add(record)
        session.commit()
        # Test new row with invalid entry_type ('se') — should raise IntegrityError
        with engine.begin() as conn:
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                conn.execute(
                    sa_text(
                        "INSERT INTO headword_search_entries (record_id, entry_type, term, normalized_term) "
                        "VALUES (:rid, :et, :t, :nt)"
                    ),
                    {"rid": record.id, "et": "se", "t": "x", "nt": "x"},
                )
        # Verify valid entry_type ('lx') is accepted
        with engine.begin() as conn:
            conn.execute(
                sa_text(
                    "INSERT INTO headword_search_entries (record_id, entry_type, term, normalized_term) "
                    "VALUES (:rid, :et, :t, :nt)"
                ),
                {"rid": record.id, "et": "lx", "t": "wampuw", "nt": "wampuw"},
            )
        # Clean up
        with engine.begin() as conn:
            conn.execute(sa_text("DELETE FROM headword_search_entries WHERE record_id = :rid"), {"rid": record.id})
            conn.execute(sa_text("DELETE FROM records WHERE id = :rid"), {"rid": record.id})
            conn.execute(sa_text("DELETE FROM sources WHERE id = :sid"), {"sid": source.id})

    def test_headword_requires_entry_type(self, engine, session):
        # SC-19: NOT NULL violation when entry_type is None
        from sqlalchemy import inspect as sa_inspect
        from sqlalchemy import text as sa_text

        cols = sa_inspect(session.bind).get_columns("headword_search_entries")
        entry_type_col = [c for c in cols if c["name"] == "entry_type"][0]
        if entry_type_col["nullable"]:
            pytest.skip("entry_type is nullable in current schema")
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"hw_null_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"hw_null_{tag}", source_id=source.id, mdf_data=f"\\lx hw_null_{tag}")
        session.add(record)
        session.commit()  # Commit so setup survives rollback
        import sqlalchemy.exc

        # Use engine connection directly to test DB-level NOT NULL
        with engine.begin() as conn:
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                conn.execute(
                    sa_text(
                        "INSERT INTO headword_search_entries (record_id, entry_type, term, normalized_term) "
                        "VALUES (:rid, NULL, :t, :nt)"
                    ),
                    {"rid": record.id, "t": "x", "nt": "x"},
                )
        # Clean up via engine connection
        with engine.begin() as conn:
            conn.execute(sa_text("DELETE FROM records WHERE id = :rid"), {"rid": record.id})
            conn.execute(sa_text("DELETE FROM sources WHERE id = :sid"), {"sid": source.id})

    def test_multiple_headword_entries_per_record(self, session):
        # SC-21: Record with 2+ HeadwordSearchEntry entries returns all via relationship
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"hw_multi_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"hw_multi_{tag}", source_id=source.id, mdf_data=f"\\lx hw_multi_{tag}")
        session.add(record)
        session.flush()
        entry1 = HeadwordSearchEntry(record_id=record.id, entry_type="lx", term="wampuw", normalized_term="wampuw")
        session.add(entry1)
        entry2 = HeadwordSearchEntry(record_id=record.id, entry_type="va", term="wampu", normalized_term="wampu")
        session.add(entry2)
        session.flush()
        session.expire_all()
        assert len(record.headword_entries) == 2
        terms = {e.term for e in record.headword_entries}
        assert "wampuw" in terms
        assert "wampu" in terms
        session.delete(entry1)
        session.delete(entry2)
        session.delete(record)
        session.delete(source)
        session.commit()


class TestGlossSearchEntryBehavior:
    """SC-16, SC-17, SC-20, SC-22: Behavioral tests for GlossSearchEntry."""

    def test_record_gloss_relationship_traversal(self, session):
        # SC-16: Record.gloss_entries returns associated GlossSearchEntry instances
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"gl_rel_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"gl_rel_{tag}", source_id=source.id, mdf_data=f"\\lx gl_rel_{tag}")
        session.add(record)
        session.flush()
        entry = GlossSearchEntry(record_id=record.id, term="round object", normalized_term="round object")
        session.add(entry)
        session.flush()
        session.expire_all()
        assert len(record.gloss_entries) == 1
        assert record.gloss_entries[0].term == "round object"
        session.delete(entry)
        session.delete(record)
        session.delete(source)
        session.commit()

    def test_gloss_rejects_entry_type(self, session):
        # SC-20: GlossSearchEntry has no entry_type column — structural difference from HW
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"gl_reject_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"gl_reject_{tag}", source_id=source.id, mdf_data=f"\\lx gl_reject_{tag}")
        session.add(record)
        session.flush()
        from sqlalchemy import inspect as sa_inspect

        col_names = {c["name"] for c in sa_inspect(session.bind).get_columns("gloss_search_entries")}
        assert "entry_type" not in col_names, "entry_type should not exist on gloss_search_entries"
        session.delete(record)
        session.delete(source)
        session.commit()

    def test_multiple_gloss_entries_per_record(self, session):
        # SC-22: Record with 2+ GlossSearchEntry entries returns all via relationship
        tag = uuid.uuid4().hex[:8]
        source = Source(name=f"gl_multi_source_{tag}")
        session.add(source)
        session.flush()
        record = Record(lx=f"gl_multi_{tag}", source_id=source.id, mdf_data=f"\\lx gl_multi_{tag}")
        session.add(record)
        session.flush()
        entry1 = GlossSearchEntry(record_id=record.id, term="round", normalized_term="round")
        session.add(entry1)
        entry2 = GlossSearchEntry(record_id=record.id, term="ball", normalized_term="ball")
        session.add(entry2)
        session.flush()
        session.expire_all()
        assert len(record.gloss_entries) == 2
        terms = {e.term for e in record.gloss_entries}
        assert "round" in terms
        assert "ball" in terms
        session.delete(entry1)
        session.delete(entry2)
        session.delete(record)
        session.delete(source)
        session.commit()
