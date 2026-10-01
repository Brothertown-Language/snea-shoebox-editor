"""SC2 (issue 1394) — rebuilt DDL emits vector(384) for gloss_search_entries.embedding.

Enforcement test for the DDL builder in scripts/sync_prod_to_local.py.
Drives get_table_metadata() against a stubbed connection whose catalog
fixture mirrors production introspection of gloss_search_entries
(typname='vector', atttypmod=384, i.e.
format_type(atttypid, atttypmod) == 'vector(384)') and asserts the
emitted CREATE TABLE DDL for gloss_search_entries carries the
typmod-qualified type vector(384) on the embedding column — never a
bare vector.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_prod_to_local.py"
_spec = importlib.util.spec_from_file_location("sync_prod_to_local", _SCRIPT)
sync_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync_mod)


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None

    def scalar(self):
        row = self.first()
        return row[0] if row else None


class _FakeConn:
    """Stub for the exact catalog queries get_table_metadata() issues."""

    def __init__(self):
        self.column_info = {
            "dtype": "vector",
            "typmod": 384,
            "notnull": False,
            "generated": None,
        }

    def execute(self, stmt, *args, **kwargs):
        sql = str(stmt)
        if "pg_get_constraintdef" in sql:
            return _FakeResult([])
        if "pg_get_expr" in sql:
            return _FakeResult([])
        if "attname" in sql and "atttypmod" in sql:
            info = self.column_info
            return _FakeResult([(info["dtype"], info["typmod"], info["notnull"], info["generated"])])
        # initial column metadata query
        return _FakeResult([("embedding", "vector", None)])

    def commit(self):
        pass


def test_ddl_emits_vector_384_for_gloss_search_entries_embedding():
    conn = _FakeConn()
    meta = sync_mod.get_table_metadata(conn, "gloss_search_entries")
    ddl = meta["ddl"]
    assert "CREATE TABLE IF NOT EXISTS gloss_search_entries" in ddl, (
        f"DDL must target gloss_search_entries; got:\n{ddl}"
    )
    assert "embedding vector(384)" in ddl, (
        "DDL must emit typmod-qualified vector(384) for "
        f"gloss_search_entries.embedding; got:\n{ddl}"
    )
    # A bare vector column type is the regression this SC forbids.
    bare = "embedding vector\n" in ddl or "embedding vector," in ddl
    assert not bare, f"DDL emitted bare vector without typmod:\n{ddl}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
