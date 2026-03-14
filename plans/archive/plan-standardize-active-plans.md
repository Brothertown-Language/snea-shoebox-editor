# Plan: Standardize Active Plans to plan_standards

**File:** `plans/plan-standardize-active-plans.md`
**Status:** ✔️ Completed

## Overview

Three active plans use `✅` instead of the required `✔️` icon per plan_standards.md. All three are marked Complete but have not been archived. This plan corrects the icons and archives each completed plan.

## Steps

1. ✔️ Fix `fix-failed-tests.md` — replace all `✅` with `✔️`; replace `**Status:** ✅ Complete` with `**Status:** ✔️ Completed`
2. ✔️ Fix `fix-preexisting-failures.md` — same icon corrections
3. ✔️ Fix `fix-e2e-test.md` — same icon corrections
4. ✔️ Archive all three plans via `uv run python ai_bin/plan archive <filename>`
5. ✔️ Update this plan to reflect completion and archive it
