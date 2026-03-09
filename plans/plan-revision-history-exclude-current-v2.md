# Plan: Revision History — Exclude Current Live Version (v2)

**Status:** 🔄 Pending

## Overview

The previous fix filtered `EditHistory.version != Record.current_version`. This was based on a wrong assumption.
Actual behavior: history is written at `current_version + 1`, then SQLAlchemy's `version_id_col` increments
`current_version` to match on commit. So the latest history entry's `version` equals `current_version` after
commit — but record 3834 has `current_version=6` and latest history `version=7`, showing the two can diverge
(e.g. due to lock/unlock cycles or other non-MDF updates that increment `current_version` without writing history).

The reliable invariant is: **the most recent history entry (by max version) always represents the current live
state**. The correct filter is to exclude the entry with `max(EditHistory.version)` for that record.

## Root Cause

`EditHistory.version != Record.current_version` is unreliable because `current_version` can diverge from the
max history version. The max-version history entry is always the current snapshot regardless of `current_version`.

## Scope

- `src/services/linguistic_service.py` — `get_edit_history` only: replace the `!= Record.current_version`
  filter with a subquery that excludes the entry whose version equals the max version for that record_id.
- No UI changes. No schema changes.

## Steps

### Phase 1 — Service layer
1. 🔄 In `get_edit_history`, replace the join+filter on `Record.current_version` with a subquery:
   `max_version_subq = session.query(func.max(EditHistory.version)).filter(EditHistory.record_id == record_id).scalar_subquery()`
   then add `.filter(EditHistory.version != max_version_subq)`.

### Phase 2 — Completion
1. 🔄 Update this plan to reflect actual progress and declare completion if all steps are done.

## Out of Scope
- No UI changes.
- No new tests unless explicitly requested.
