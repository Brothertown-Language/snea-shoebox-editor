# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Shared fixtures for the tests/ tree.

Issue #1426: several test modules historically set ``os.environ["OPENCODE"] = "1"``
at module import. pytest imports every test module during collection, so that
process-global leaked into the whole session and redirected *all* DB-backed
tests — including fixtures that must read the freshly synced production replica
at ``tmp/local_db`` — to the stale private scratch DB at ``tmp/opencode_db``.
That order-coupling produced the recorded suite-context failures (synced-record
assertions seeing an empty DB, FK violations against the wrong schema/data).

The fix keeps the isolation those modules need (they write test rows and drop
indexes — they must not touch the synced replica) but scopes it: the
``private_db`` fixture below switches the process to the private scratch DB
only for the module that requests it, starts it from a wiped pgdata so results
never depend on leftover state from prior runs, and restores the process-global
connection state afterwards so later modules resolve the synced local DB again.
"""

# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT

import os
import shutil
from pathlib import Path

import pytest

SCRATCH_DB_PATH = Path("tmp/opencode_db")


def _stop_and_remove_scratch_db():
    """Stop any server on the private scratch pgdata and delete it.

    Reuses the connection layer's own force-stop helper so the cleanup path is
    identical to the one src/ uses for stuck local databases.
    """
    from src.database import connection as conn_mod

    if SCRATCH_DB_PATH.exists() and (SCRATCH_DB_PATH / "postmaster.pid").exists():
        try:
            conn_mod._force_stop_stuck_db(SCRATCH_DB_PATH)
        except Exception:  # pragma: no cover - best-effort cleanup
            pass
    if SCRATCH_DB_PATH.exists():
        shutil.rmtree(SCRATCH_DB_PATH, ignore_errors=True)


@pytest.fixture(scope="module")
def private_db():
    """Give the requesting module an isolated, freshly created scratch database.

    Within the module's lifetime:

    * ``OPENCODE=1`` selects the private scratch DB path in
      ``src/database/connection.py`` (the documented OpenCode isolation path);
    * the scratch pgdata is wiped first, so test outcomes never depend on
      leftover state from previous runs;
    * the connection module's process-global caches (URL cache, pgserver
      handle, Streamlit engine cache) are reset so the scratch DB is actually
      the one used.

    On exit everything is restored, so modules that run afterwards resolve the
    synced local replica exactly as they would in a fresh process.
    """
    import streamlit as st

    from src.database import connection as conn_mod

    saved = (
        os.environ.get("OPENCODE"),
        conn_mod._db_url_cache,
        conn_mod._pg_server,
        conn_mod._pg_server_was_preexisting,
    )

    _stop_and_remove_scratch_db()
    os.environ["OPENCODE"] = "1"
    conn_mod._db_url_cache = None
    conn_mod._pg_server = None
    conn_mod._pg_server_was_preexisting = False
    try:
        conn_mod.get_engine.clear()
    except Exception:  # pragma: no cover - cache clear is best-effort
        pass

    try:
        yield
    finally:
        # Stop the scratch server so it does not linger after the module.
        scratch_server = conn_mod._pg_server
        if scratch_server is not None:
            try:
                scratch_server.cleanup()
            except Exception:  # pragma: no cover - best-effort cleanup
                pass
        (
            env_saved,
            conn_mod._db_url_cache,
            conn_mod._pg_server,
            conn_mod._pg_server_was_preexisting,
        ) = saved
        if env_saved is None:
            os.environ.pop("OPENCODE", None)
        else:
            os.environ["OPENCODE"] = env_saved
        try:
            conn_mod.get_engine.clear()
        except Exception:  # pragma: no cover - cache clear is best-effort
            pass


@pytest.fixture(scope="module")
def private_db_engine(private_db):
    """An initialized engine against the module's private scratch database."""
    from src.database.connection import init_db

    return init_db()
