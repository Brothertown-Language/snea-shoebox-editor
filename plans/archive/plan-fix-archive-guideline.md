# Plan: Add Pre-Submit Archive Enforcement to Guidelines
## Status: ✅ Complete

## Overview
**WHAT**: Add a mandatory pre-submit checklist step to `plan_standards.md` (and a reinforcing note in `01-approval-gate.md`) that requires the agent to verify and execute plan archiving before calling `submit`.

**WHY**: The previous session completed `plan-sync-prod-verify-docs.md` (all 4 steps ✅, status set to Complete) but failed to run `uv run python ai_bin/plan archive`. The archiving rule exists but is buried in prose — there is no explicit "before you call submit, check this list" hook. A pre-submit checklist makes the omission impossible to miss.

## Scope
- `plans/plan_standards.md` — add pre-submit checklist section
- `.junie/guidelines/01-approval-gate.md` — add reinforcing inline reminder in the Archiving Mandate paragraph
- No code changes, no logic changes

## Steps

1. ✅ Add a **Pre-Submit Checklist** section to `plans/plan_standards.md` with a mandatory bullet: "If any plan in `plans/` is ✅ Complete, archive it via `uv run python ai_bin/plan archive <filename>` before calling `submit`."
2. ✅ Add a one-line reinforcing note to the **Archiving Mandate** paragraph in `.junie/guidelines/01-approval-gate.md`: "Before calling `submit`, scan `plans/` for any completed plan not yet archived and archive it."
3. ✅ Archive `plan-sync-prod-verify-docs.md` (the missed archive from the previous session).
4. ✅ Update this plan to reflect actual progress and declare completion if all steps are done.

## Non-Scope
- No changes to `ai_bin/` tools
- No changes to any source code
