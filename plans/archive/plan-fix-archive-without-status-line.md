# Plan: Fix Archive Without Status Line

**Status:** ✔️ Complete  
**Created:** 2026-03-12  
**Scope:** `ai_bin/plan` + `plans/plan_standards.md`

---

## Overview

Old-format plans (e.g., `plan-pyproject-dep-remediation.md`) have all steps marked `✔️ Completed`
in step text but no `**Status:**` header line. `is_complete()` only checks the Status line, so
`archive` errors out silently — the agent believes it archived the plan but the file stays in
`plans/`. Fix both the tool and the guidelines.

---

## Background

`cmd_archive` calls `is_complete()` which returns `False` when no `**Status:**` line exists.
The agent gets an error but may not surface it, leading to the false belief the plan was archived.

---

## Checklist

- [ ] Verify correctness with unit tests
- [ ] Verify completion with a deep code dive
- [ ] Automatically archive completed plans

---

## Steps

### 1. ✔️ Completed — Update `cmd_set_status` in `ai_bin/plan` to insert Status line if missing
When `set-status` is called and no `**Status:**` line exists, insert one after the H1 title line
(second line of the file) rather than erroring out. This makes `set-status done` + `archive`
work correctly on old-format plans without needing `--force`.

### 2. ✔️ Completed — Add rule to `plan_standards.md`
Add a rule under **Archiving**: if `archive` fails with "not marked complete", the agent MUST run
`set-status done` first (which will insert the Status line if missing), then retry `archive`.
Silently skipping archiving after an error is a CRITICAL VIOLATION.

### 3. ✔️ Completed — Archive `plan-pyproject-dep-remediation.md`
Run `uv run python ai_bin/plan set-status plan-pyproject-dep-remediation.md done` then
`uv run python ai_bin/plan archive plan-pyproject-dep-remediation.md` to clear the outstanding
unarchived plan using the new insertion behavior.

### 4. ✔️ Completed — Update memory.md
Record task outcome.

### 5. ✔️ Completed — Archive this plan
