---
remote_issue: 1359
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1359
promoted_at: 2026-07-16T00:00:00Z
labels:
  - spec
  - needs-approval
---

# [SPEC] Document Local PostgreSQL Setup

## Problem Statement

The local PostgreSQL database setup lacks comprehensive documentation. While `docs/lessons-learned/2026-06-14-pg-catalog-schema-replication.md` covers the sync mechanism and `AGENTS.md` mentions the sync command, there is no central reference explaining:

1. What the local PostgreSQL instance is and how it works
2. How to start, stop, and query it
3. What it's used for in development workflows
4. Common patterns for interacting with the data

This gap forces developers to rediscover setup details each session.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | New lesson-learned file exists at `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` | `structural` | `ls docs/lessons-learned/2026-07-16-local-postgresql-setup.md` |
| SC-2 | Lesson-learned file covers: pgserver location, sync mechanism, start/stop, query patterns | `string` | `grep` for key sections in the file |
| SC-3 | `docs/lessons-learned/index.md` updated with new entry | `string` | `grep` for new entry in index |
| SC-4 | `AGENTS.md` updated with reference to new lesson-learned file | `string` | `grep` for reference in AGENTS.md |

## Scope

**In Scope:**
- Create `docs/lessons-learned/2026-07-16-local-postgresql-setup.md`
- Update `docs/lessons-learned/index.md`
- Update `AGENTS.md` Research Catalog section

**Out of Scope:**
- Modifying the sync script itself
- Changing the database schema
- Adding new database features

## Implementation Notes

The lesson-learned file should document:
- Local PostgreSQL runs via pgserver in `tmp/local_db/`
- Synced from production via `scripts/sync_prod_to_local.py`
- Used for development and regression testing
- Connection: `postgresql://postgres:@localhost:5432/postgres`
- Query patterns using SQLAlchemy and `get_session()`
- Example: searching for `\ph` in `mdf_data` column (430 entries found)

## Risk Assessment

**Low Risk** — Documentation-only change, no code modifications.

## Files Referenced

| File | Purpose |
|------|---------|
| `scripts/sync_prod_to_local.py` | Sync script to document |
| `src/database/connection.py` | Connection setup to document |
| `docs/lessons-learned/2026-06-14-pg-catalog-schema-replication.md` | Related existing documentation |
| `AGENTS.md` | Needs update to reference new lesson |
