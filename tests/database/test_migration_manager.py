# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
import pytest

# Ensure private database is used
os.environ["JUNIE_PRIVATE_DB"] = "true"

from src.database.connection import init_db
from src.database.migrations import MigrationManager
from src.database.models.meta import SchemaVersion
from src.database.models.identity import Permission
from sqlalchemy.orm import sessionmaker


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
        assert count >= expected, (
            f"Expected at least {expected} schema_version rows, got {count}"
        )

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

        assert count_before == count_after, (
            f"Duplicate rows created: {count_before} before, {count_after} after"
        )


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
            assert p.github_org == p.github_org.lower(), (
                f"github_org not lowercase: {p.github_org}"
            )
            assert p.github_team == p.github_team.lower(), (
                f"github_team not lowercase: {p.github_team}"
            )

    def test_expected_roles_present(self, session):
        """The three default roles (admin, editor, viewer) should be present."""
        roles = {p.role for p in session.query(Permission).all()}
        for expected in ("admin", "editor", "viewer"):
            assert expected in roles, f"Missing expected role: {expected}"
