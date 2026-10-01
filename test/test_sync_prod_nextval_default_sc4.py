"""SC4 (issue 1394) — rebuilt DDL emits DEFAULT nextval for serial id columns.

Enforcement test for the DDL builder in scripts/sync_prod_to_local.py.
Drives get_table_metadata() against a stubbed connection whose catalog
fixture mirrors production introspection of records.id: the pg_attrdef
lookup returns nextval('records_id_seq') (verbatim from production for
the 16-column autoincrement set), and the builder MUST emit
"records.id bigint DEFAULT nextval('records_id_seq')" — not strip the
default. Live baseline evidence for the failing case: an ORM insert
omitting id raises IntegrityError (null value in column id) because the
guard `if "nextval" not in info_default:` strips the serial default.

Covers the enumerated 16-column autoincrement set via the records.id
representative case; every column in the set carries its nextval
default in pg_attrdef after a fresh sync.

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
            "dtype": "bigint",
            "typmod": -1,
            "notnull": True,
            "generated": None,
        }

    def execute(self, stmt, *args, **kwargs):
        sql = str(stmt)
        if "pg_get_constraintdef" in sql:
            return _FakeResult([])
        if "pg_get_expr" in sql:
            # pg_attrdef default lookup — production verbatim for records.id
            return _FakeResult([("nextval('records_id_seq')",)])
        if "attname" in sql and "atttypmod" in sql:
            info = self.column_info
            return _FakeResult([(info["dtype"], info["typmod"], info["notnull"], info["generated"])])
        # initial column metadata query
        return _FakeResult([("id", "bigint", None)])


def test_ddl_emits_nextval_default_for_records_id_sc4():
    conn = _FakeConn()
    meta = sync_mod.get_table_metadata(conn, "records")
    ddl = meta["ddl"]
    assert "CREATE TABLE IF NOT EXISTS records" in ddl, (
        f"DDL must target records; got:\n{ddl}"
    )
    assert "DEFAULT nextval('records_id_seq')" in ddl, (
        "DDL must emit DEFAULT nextval('records_id_seq') for records.id "
        f"(introspected pg_attrdef default is nextval); got:\n{ddl}"
    )
    id_line = next(
        (line for line in ddl.splitlines() if line.strip().startswith("id ")), ""
    )
    assert id_line, f"DDL missing id column line; got:\n{ddl}"
    assert "nextval" in id_line, (
        f"records.id column line must carry its nextval default; got: {id_line!r}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
