# Copyright (c) 2026 Brothertown Language
"""
sync_prod_to_local.py — Production-to-local database sync script.

Creates an exact schema+data replica of the production PostgreSQL database (Aiven)
in the local development database (pgserver), replacing all local data.

Strategy
--------
Introspects production's actual schema via pg_catalog and replicates it faithfully —
including generated columns, all indexes — then copies production data while
skipping generated columns in INSERT statements.
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

LOG_FILE = project_root / "tmp" / "sync_prod_to_local.log"


def log_message(msg, to_console=True, pbar=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")
    if to_console:
        if pbar:
            tqdm.write(msg)
        else:
            print(msg)


def _ensure_pgserver() -> str:
    try:
        from src.database.connection import _get_local_db_path, _start_pgserver_core
        db_path = _get_local_db_path()
        log_message(f"Starting pgserver (db_path={db_path})...")
        uri = _start_pgserver_core(db_path)
        log_message(f"pgserver started: {uri.split('@')[-1]}")
        return uri
    except Exception as e:
        log_message(f"Warning: pgserver start failed: {e}")
        return "postgresql://postgres:@localhost:5432/postgres"


def load_secrets():
    prod_url = os.getenv("DATABASE_URL")
    local_url = os.getenv("LOCAL_DATABASE_URL")
    ls_path = project_root / ".streamlit" / "secrets.toml"
    ps_path = project_root / ".streamlit" / "secrets.toml.production"
    if not prod_url and ps_path.exists():
        with open(ps_path, "rb") as f:
            prod_url = tomllib.load(f).get("connections", {}).get("postgresql", {}).get("url")
    if not local_url and ls_path.exists():
        with open(ls_path, "rb") as f:
            local_url = tomllib.load(f).get("connections", {}).get("postgresql", {}).get("url")
    if not local_url:
        local_url = "postgresql://postgres:@localhost:5432/postgres"
    return prod_url, local_url


def get_table_metadata(conn, table_name: str) -> dict:
    """Return column names, generated column names, and CREATE TABLE DDL."""
    # Get non-generated column names for INSERT
    regular_cols = []
    generated_cols = []
    all_cols = []
    type_map = {}

    rows = conn.execute(text(f"""
        SELECT
            a.attname,
            t.typname,
            a.attgenerated
        FROM pg_attribute a
        JOIN pg_type t ON t.oid = a.atttypid
        WHERE a.attrelid = quote_ident('{table_name}')::regclass
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum
    """)).fetchall()

    for name, typname, generated in rows:
        all_cols.append(name)
        type_map[name] = typname
        if generated == 's':
            generated_cols.append(name)
        else:
            regular_cols.append(name)

    # Build CREATE TABLE DDL
    ddl_parts = []
    for name in all_cols:
        info = conn.execute(text(f"""
            SELECT
                CASE
                    WHEN t.typname = 'vector' THEN 'vector'
                    WHEN t.typname = 'tsvector' THEN 'tsvector'
                    WHEN t.typname = 'bool' THEN 'boolean'
                    WHEN t.typname = 'int4' THEN 'integer'
                    WHEN t.typname = 'int8' THEN 'bigint'
                    WHEN t.typname = 'float8' THEN 'double precision'
                    WHEN t.typname = 'numeric' THEN 'numeric'
                    WHEN t.typname = 'varchar' THEN 'character varying'
                    WHEN t.typname = 'text' THEN 'text'
                    WHEN t.typname = 'timestamptz' THEN 'timestamp with time zone'
                    ELSE t.typname
                END AS dtype,
                a.atttypmod,
                a.attnotnull,
                a.attgenerated
            FROM pg_attribute a
            JOIN pg_type t ON t.oid = a.atttypid
            WHERE a.attrelid = quote_ident('{table_name}')::regclass
              AND a.attname = '{name}'
              AND a.attnum > 0
        """)).first()
        if not info:
            continue
        dtype, typmod, notnull, generated = info

        if generated == 's':
            expr = conn.execute(text(f"""
                SELECT pg_get_expr(d.adbin, d.adrelid)::text
                FROM pg_attrdef d
                JOIN pg_class c ON c.oid = d.adrelid
                WHERE c.relname = '{table_name}'
                  AND d.adnum = (SELECT a.attnum FROM pg_attribute a
                                 WHERE a.attrelid = c.oid AND a.attname = '{name}')
            """)).scalar()
            ddl_parts.append(f"  {name} {dtype} GENERATED ALWAYS AS ({expr}) STORED")
        else:
            line = f"  {name} {dtype}"
            if dtype == 'character varying' and typmod and typmod > -1:
                line = f"  {name} character varying({typmod - 4})"
            if notnull:
                line += " NOT NULL"
            if info_default := conn.execute(text(f"""
                SELECT pg_get_expr(d.adbin, d.adrelid)::text
                FROM pg_attrdef d
                JOIN pg_class c ON c.oid = d.adrelid
                WHERE c.relname = '{table_name}'
                  AND d.adnum = (SELECT a.attnum FROM pg_attribute a
                                 WHERE a.attrelid = c.oid AND a.attname = '{name}')
            """)).scalar():
                if "nextval" not in info_default:
                    line += f" DEFAULT {info_default}"
            ddl_parts.append(line)

    # Add constraints (primary key, foreign keys, unique, check)
    constraints = conn.execute(text(f"""
        SELECT pg_get_constraintdef(oid) AS condef
        FROM pg_constraint
        WHERE conrelid = quote_ident('{table_name}')::regclass
          AND contype IN ('p', 'f', 'u', 'c')
        ORDER BY CASE contype
            WHEN 'p' THEN 1
            WHEN 'u' THEN 2
            WHEN 'f' THEN 3
            WHEN 'c' THEN 4
        END
    """)).fetchall()
    for (condef,) in constraints:
        ddl_parts.append(f"  {condef}")

    ddl = f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(ddl_parts) + "\n);"

    return {
        "regular_cols": regular_cols,
        "generated_cols": generated_cols,
        "all_cols": all_cols,
        "ddl": ddl,
    }


def sync_data():
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    log_message("Starting Production to Local Sync...")

    prod_url, local_url = load_secrets()
    if not prod_url:
        log_message("Error: Production DATABASE_URL not found")
        sys.exit(1)

    local_url = _ensure_pgserver()
    log_message(f"Connecting to Production: {prod_url.split('@')[-1]}")
    log_message(f"Connecting to Local: {local_url.split('@')[-1]}")

    prod_engine = create_engine(prod_url)
    local_engine = create_engine(local_url)

    with local_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # Introspect production schema
    log_message("Introspecting production schema...")
    table_meta = {}
    sorted_tables = []
    with prod_engine.connect() as pc:
        prod_tables = [
            r[0] for r in pc.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename")
            ).fetchall()
        ]
        log_message(f"  Found {len(prod_tables)} tables")

        # Cache metadata and FK dependencies for all tables
        fk_deps = {}
        for tname in prod_tables:
            table_meta[tname] = get_table_metadata(pc, tname)
            refs = pc.execute(text(f"""
                SELECT DISTINCT c.confrelid::regclass::text AS ref_table
                FROM pg_constraint c
                WHERE c.conrelid = quote_ident('{tname}')::regclass
                  AND c.contype = 'f'
            """)).fetchall()
            fk_deps[tname] = {r[0].strip('"') for r in refs}

        # Topological sort: tables that are referenced first
        remaining = set(prod_tables)
        while remaining:
            batch = {t for t in remaining if not (fk_deps.get(t, set()) & remaining)}
            if not batch:
                batch = remaining.copy()
            sorted_tables.extend(sorted(batch))
            remaining -= batch

        # Drop all local tables (reverse order)
        with local_engine.connect() as lc:
            for tname in reversed(sorted_tables):
                lc.execute(text(f"DROP TABLE IF EXISTS {tname} CASCADE"))
            lc.commit()

        # Recreate tables in dependency order
        for tname in sorted_tables:
            with local_engine.connect() as lc:
                lc.execute(text(table_meta[tname]["ddl"]))
                lc.commit()
        log_message(f"  Created {len(sorted_tables)} tables in dependency order")

        # Add indexes (exclude PKs and unique constraints already baked into CREATE TABLE)
        for tname in prod_tables:
            indexes = pc.execute(text(f"""
                SELECT i.relname AS idx_name, pg_get_indexdef(idx.indexrelid) AS idx_def
                FROM pg_index idx
                JOIN pg_class i ON i.oid = idx.indexrelid
                JOIN pg_class c ON c.oid = idx.indrelid
                WHERE c.relname = '{tname}'
                  AND i.relname NOT LIKE '%_pkey'
                  AND NOT idx.indisunique
            """)).fetchall()
            with local_engine.connect() as lc:
                for (idx_name, idx_def) in indexes:
                    lc.execute(text(idx_def))
                    lc.commit()
        log_message("  Indexes created")

    # Copy data
    log_message("Copying production data...")
    SessionLocal = sessionmaker(bind=local_engine)
    SessionProd = sessionmaker(bind=prod_engine)

    with SessionProd() as ps, SessionLocal() as ls:
        for tname in reversed(sorted_tables):
            ls.execute(text(f"DELETE FROM {tname}"))
        ls.commit()

        for tname in sorted_tables:
            meta = table_meta[tname]
            if not meta["regular_cols"]:
                log_message(f"  Skipped: {tname} (all generated)")
                continue

            cols_str = ", ".join(meta["regular_cols"])
            placeholders = ", ".join([f":{c}" for c in meta["regular_cols"]])
            rows = ps.execute(text(f"SELECT {cols_str} FROM {tname}")).fetchall()
            if rows:
                data = [dict(r._mapping) for r in rows]
                for bstart in range(0, len(data), 1000):
                    batch = data[bstart:bstart + 1000]
                    ls.execute(
                        text(f"INSERT INTO {tname} ({cols_str}) VALUES ({placeholders})"),
                        batch,
                    )
                ls.commit()
            log_message(f"  Copied: {tname} ({len(rows)} rows)")

    # Reset sequences
    log_message("Resetting sequences...")
    with local_engine.connect() as lc:
        for tname in sorted_tables:
            seq = lc.execute(text(
                "SELECT pg_get_serial_sequence(:t, 'id')"
            ), {"t": tname}).scalar()
            if seq:
                max_id = lc.execute(text(f"SELECT COALESCE(MAX(id), 1) FROM {tname}")).scalar()
                lc.execute(text(f"SELECT setval('{seq}', {max_id})"))
        lc.commit()

    # Verify
    log_message("\n=== VERIFICATION ===")
    ins = inspect(local_engine)
    for t in ['records', 'schema_version', 'fts_entries']:
        if ins.has_table(t):
            with SessionLocal() as s:
                cnt = s.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                log_message(f"  {t}: {cnt} rows")
                if t == 'records':
                    cols = [c['name'] for c in ins.get_columns(t)]
                    log_message(f"    fts_vector present: {'fts_vector' in cols}")

    from src.database.models.meta import SchemaVersion
    with SessionLocal() as s:
        v = s.query(SchemaVersion.version).order_by(SchemaVersion.version.desc()).first()
        log_message(f"  Schema version: {v[0] if v else 0}")

    log_message("\nSync completed successfully.")


if __name__ == "__main__":
    sync_data()