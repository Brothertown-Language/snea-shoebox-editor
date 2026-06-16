"""Session-scoped conftest: run pending migrations before any integration test."""

import pytest
from sqlalchemy import create_engine

from src.database.connection import _get_local_db_path, _start_pgserver_core
from src.database.migrations import MigrationManager


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    """Run all pending migrations before any integration test connects."""
    db_path = _get_local_db_path()
    uri = _start_pgserver_core(db_path)
    engine = create_engine(uri)
    MigrationManager(engine).run_all()
