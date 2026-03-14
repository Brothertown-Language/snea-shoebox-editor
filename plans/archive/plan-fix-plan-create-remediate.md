# Plan: Fix `ai_bin/plan create` Template + Add `remediate` Command

**Status:** ✔️ Complete  
**Created:** 2026-03-12  
**Scope:** `ai_bin/plan` only — no `src/` changes

---

## Overview

The `ai_bin/plan create` command generates a plan template missing required sections per
`plan_standards.md`: `## Overview` and `## Checklist` (with 3 mandatory items). This causes
`set-status` failures (missing `**Status:**` line is already present, but missing sections
cause non-compliance). Additionally, there is no way to bring an existing non-compliant plan
file into compliance.

**Why**: Plans missing `## Overview` or `## Checklist` cannot be properly managed by `ai_bin/plan`
and violate `plan_standards.md`. The `remediate` command provides a repair path for legacy plans.

---

## Checklist

- [ ] Verify correctness with unit tests
- [ ] Verify completion with a deep code dive
- [ ] Automatically archive completed plans

---

## Steps

### Phase 1 — Fix `cmd_create` Template

1. 🔄 Pending — Add `## Overview` section (with placeholder comment) to the `cmd_create` template in `ai_bin/plan`, positioned after the `---` separator and before `## Background`.
2. 🔄 Pending — Add `## Checklist` section with the 3 mandatory items (`Verify correctness with unit tests`, `Verify completion with a deep code dive`, `Automatically archive completed plans`) to the `cmd_create` template, positioned after `## Steps` heading.

### Phase 2 — Add `remediate` Subcommand

3. 🔄 Pending — Implement `cmd_remediate(args)` function: reads plan file, detects missing sections (`## Overview`, `## Checklist` with mandatory items, `**Status:**` line), inserts them at appropriate positions without disturbing existing content.
4. 🔄 Pending — Wire `remediate` into the argparse subcommands with usage: `remediate <filename>` — prints a summary of what was added/already present.
5. 🔄 Pending — Update the DESCRIPTION docstring at the top of `ai_bin/plan` to include the new `remediate` command.

### Phase 3 — Verification

6. 🔄 Pending — Smoke test `plan create`: create a test plan, verify all required sections present (`**Status:**`, `## Overview`, `## Checklist` with 3 items, `## Steps`).
7. 🔄 Pending — Smoke test `plan remediate`: run against a minimal non-compliant plan file, verify missing sections are inserted correctly and existing content is preserved.
8. 🔄 Pending — Verify `plan set-status` works on a newly created plan (regression: previously failed due to missing `**Status:**` — confirm still works and new sections don't break it).
9. 🔄 Pending — Delete test plan files created during verification.

### Phase 4 — Housekeeping

10. 🔄 Pending — Update `memory.md` with `last_task`.
11. 🔄 Pending — Archive this plan via `uv run python ai_bin/plan archive plan-fix-plan-create-remediate.md`.
