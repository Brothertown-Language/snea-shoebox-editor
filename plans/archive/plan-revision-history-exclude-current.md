# Plan: Revision History — Exclude Current Live Version

**Status:** ✅ Complete (superseded by v2; v2 implemented in commit d4de0df)

## Overview

The revision history expander currently includes the entry that represents the current live state of the record. This is redundant — the live record is already displayed above the expander. The history should show only *prior* versions.

## What & Why

- `EditHistory.version` is set to `record.current_version + 1` at save time, so the most recent history entry always has `version == record.current_version` on the live record.
- Displaying this entry in the history is misleading: it shows the same data as the live record, not a prior state.
- Fix: in `get_edit_history`, join with `Record` and filter out entries where `h.version == record.current_version`.

## Scope

- `src/services/linguistic_service.py` — `get_edit_history` only: add a join + filter to exclude the current-version entry.
- No UI changes. No schema changes.

## Steps

### Phase 1 — Service layer
1. ✔️ In `get_edit_history`, join the query with `Record` on `record_id` and add `.filter(EditHistory.version != Record.current_version)` to exclude the live-version entry.

### Phase 2 — Completion
1. ✔️ Update this plan to reflect actual progress and declare completion if all steps are done.

## Out of Scope
- No UI changes.
- No new tests unless explicitly requested.
