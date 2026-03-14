# Plan: TODO Review & Update 2026-03-12

**Status:** ⏳ Pending Approval  
**Created:** 2026-03-12
**Scope:** `plans/TODO.md` only

---

## Overview

Review all pending TODO items against the current codebase and update `TODO.md` to accurately reflect current state. No code changes.

---

## Background

Two items remain open in `TODO.md`. This plan audits their current status and corrects any stale metadata (e.g. line number drift).

---

## Findings

### Item: Bare `except: pass` at `connection.py:372`
- **Current state**: Still present — now at **line 377** (line numbers shifted since TODO was written).
- **Location**: `_force_stop_stuck_db()` final fallback lock-file cleanup block.
- **Action**: Update line number reference from 372 → 377 in TODO.

### Item: Implement logging to SQL table (round-robin)
- **Current state**: Still not implemented. Standard Python `logging` only via `src/logging_config.py`.
- **Action**: No change needed — item already correctly marked open with accurate note.

---

## Checklist

- [ ] Update bare-except line number reference in TODO.md (372 → 377)
- [ ] Confirm SQL logging item note is still accurate
- [ ] Archive this plan after TODO.md is updated

---

## Steps

1. Edit `plans/TODO.md`: update `connection.py:372` → `connection.py:377` in the bare-except item.
2. Archive this plan.
