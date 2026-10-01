"""SC1 (issue 1394) — rebuilt DDL emits vector(1536) for records.embedding.

Enforcement test for the DDL builder in scripts/sync_prod_to_local.py.
Drives get_table_metadata() against a stubbed connection whose catalog
fixture mirrors production introspection for the records table
(typname='vector', atttypmod=1536). pgvector stores precision directly
in atttypmod with no -4 offset, so format_type(atttypid, atttypmod)
== 'vector(1536)' and the rebuilt DDL must carry the typmod-qualified
type vector(1536) — never a bare vector.

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
            "dtype": "vector",  # baseline builder output for typname='vector'
            "typmod": 1536,
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
            return _FakeResult(
                [(info["dtype"], info["typmod"], info["notnull"], info["generated"])]
            )
        # initial column metadata query
        return _FakeResult([("embedding", "vector", None)])

    def commit(self):
        pass


def test_ddl_emits_vector_1536_for_records_embedding_column():
    conn = _FakeConn()
    meta = sync_mod.get_table_metadata(conn, "records")
    ddl = meta["ddl"]
    assert "embedding vector(1536)" in ddl, (
        f"DDL must emit typmod-qualified vector(1536) for records.embedding "
        f"(pgvector stores precision directly in atttypmod, no -4 offset); "
        f"got:\n{ddl}"
    )
    # A bare vector column type is the regression this SC forbids.
    bare = "embedding vector\n" in ddl or "embedding vector," in ddl
    assert not bare, f"DDL emitted bare vector without typmod:\n{ddl}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
