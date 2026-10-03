---
plan_schema_version: 1
issue: 1407
title: "Restore Enter-key search triggering in Records search box"
authorization_scope: for_implementation
pr_strategy: none
phase_count: 1
dispatch: [test-driven-development, verification-before-completion, finishing-a-development-branch, audit]
---

# Implementation Plan — Restore Enter-key search triggering in Records search box (Issue 1407)

- **Issue:** .issues/1407/spec.md

## Goal / Architecture / Files / Dispatch

- **Goal:** Restore Enter-key search triggering in the Records sidebar text_input: re-attach `on_change=on_search_change`, make the callback read the current dynamically suffixed widget key, commit `search_query` and reset `current_page` to 1, and reword the placeholder — leaving the magnifier-button path intact.
- **Architecture:** Single-page Streamlit state-commit fix. The callback performs a pure state commit (dynamic suffix read, backing-key writes, no rerun, no self-key write). The coupled E2E aria-label selector is updated in the same cycle as the placeholder reword (R-9 coupling).
- **Files:** `src/frontend/pages/records.py` (sole code-change surface), `test/ui/test_semantic_search_ui_flow_e2e.py` (coupled selector update).
- **Dispatch:** Phase 1 — direct steps for coherence gate, baseline check, commit-inline, and z3-check; task-card dispatches for TDD RED/GREEN cycles, verification, and post-implementation gates. See per-step indicators below.

## Blast Radius

- `src/frontend/pages/records.py` — `on_search_change` callback (currently reads the stale un-suffixed key — dead code), the `st.text_input` block (suffixed key, no `on_change` attachment, label `Enter text...`), clear-button handler that increments `_search_input_key`.
- `test/ui/test_semantic_search_ui_flow_e2e.py` — E2E locator with `aria-label="Enter text..."` that must track the placeholder change.
- No service/data-layer changes; no URL/query-param sync; no debounce/IME changes.

## Admonishments

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs must pass before this plan is complete.

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Enter-key search restoration | enter-key-search-restoration | SC-1, SC-2, SC-3, SC-4a, SC-4b | — | 1-30 | direct (1-2, 9, 14, 19, 24, 27) + task-card (3-8, 10-13, 15-18, 20-23, 25-26, 28-30) |

## Exit Criteria

- C1 — SC-1: Pressing Enter in the search text_input triggers the search — `search_query` committed from the current suffixed key and `current_page` reset to 1 (behavioral: AppTest wiring + Playwright live-browser).
- C2 — SC-2: After a clear (❌), pressing Enter commits no stale query — empty state persists (behavioral: Playwright).
- C3 — SC-3: Magnifier-button click produces exactly one search commit — identical behavior to before the change (behavioral: Playwright + AppTest regression guard).
- C4 — SC-4a: Placeholder uses neutral wording (no Enter instruction) and the coupled E2E aria-label selector is updated in the same cycle, proven by execution of the coupled E2E test (behavioral).
- C5 — SC-4b: Full pytest suite passes with zero new failures (behavioral: complete suite run).

## Phase 1 — Enter-key search restoration

- **Concern:** enter-key-search-restoration
- **Files:** `src/frontend/pages/records.py`, `test/ui/test_semantic_search_ui_flow_e2e.py`
- **SCs:** SC-1, SC-2, SC-3, SC-4a, SC-4b
- **Dependencies:** none (single-phase plan)
- **Entry condition:** approved spec at `.issues/1407/spec.md`; feature branch exists; clean working tree at trunk tip
- **Exit condition:** all five SCs verified with behavioral evidence; VbC assertions below hold

### Code Path Coverage

- `on_search_change` callback — currently reads the stale un-suffixed key `st.session_state.search_query_input`; must read `search_query_input_{st.session_state.get('_search_input_key', 0)}`.
- `st.text_input` block in the sidebar — suffixed key already in place; `on_change` attachment absent and must be restored.
- Clear-button handler — increments `_search_input_key`; callback must read the new suffix after increment (SC-2).
- Magnifier-button path — commits `search_query` + `current_page=1`; unchanged (SC-3 pin only).

### Cross-Cutting SCs

- SC-1 spans enter-wiring and post-clear state integrity (the suffixed-key read fixes both R-2 and R-7).
- SC-3 spans button-guard and enter-wiring (commit semantics must stay identical, R-3).
- SC-4b spans all items (global regression gate).

### Interface Boundaries

- Streamlit widget-state contract: callback reads the dynamic suffix key and writes ONLY `search_query` and `current_page` — never its own widget key, never via diff+rerun.
- E2E selector contract: the aria-label string in `test/ui/test_semantic_search_ui_flow_e2e.py` must equal the rendered text_input label; updated in the same delivery cycle as the placeholder change.

### State Transitions

- Typing → Enter/blur → `on_search_change` fires → reads current suffixed key → commits `search_query` → `current_page = 1` → rerun renders filtered results.
- Clear click → `_search_input_key` incremented → widget recreated empty → Enter → callback reads CURRENT suffix → commits empty string → no stale re-search.
- Unicode/IPA query strings (ə, ʃ, tʃ, diacritics, ∞) pass through verbatim — no normalization.

<!-- steps staged below -->

### Step-by-step

Pre-implementation (Tier 1 — once per plan):

- [ ] 1. Run the coherence gate — confirm the spec at `.issues/1407/spec.md` is the approved source, its SC list (SC-1, SC-2, SC-3, SC-4a, SC-4b) matches this plan, and no superseding spec exists. (**direct**)
  - SC reference: all
  - Blocker: halt with findings if the spec and plan disagree
- [ ] 2. Run the baseline check — verify the working tree is at trunk tip on the feature branch, `uv run pytest test/` is green as baseline, and record the baseline result. (**direct**)
  - SC reference: SC-4b baseline
- [ ] 3. Dispatch pre-regression — run regression test patterns before the RED phase. (**task-card** — `task(..., prompt: "execute phase-0 task from test-driven-development")`)
  - SC reference: SC-1
- [ ] 4. Dispatch pre-regression-verify — verify pre-regression results. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-1

Item 1 (SC-1 — Enter executes the search):

- [ ] 5. RED — write an AppTest in-process test asserting the text_input carries `on_change` and that triggering commits `search_query` and resets `current_page` to 1; confirm it FAILS before the change. (**task-card** — `task(..., prompt: "execute red task from test-driven-development")`)
  - SC reference: SC-1
- [ ] 6. GREEN — implement the minimum change: fix `on_search_change` to read the dynamically suffixed key, write `search_query` and reset `current_page`, and re-attach `on_change=on_search_change` to the text_input; make the RED test PASS. (**task-card** — `task(..., prompt: "execute green task from test-driven-development")`)
  - SC reference: SC-1
- [ ] 7. Post-regression — run regression test patterns after GREEN. (**task-card** — `task(..., prompt: "execute phase-4 task from test-driven-development")`)
  - SC reference: SC-1
- [ ] 8. Verify — verify implementation against SC-1: Playwright live-browser — type a query, press Enter, filtered results rendered; screenshot under `tmp/1407/artifacts/`. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-1
- [ ] 9. Commit — stage test + implementation as one atomic slice and commit. (**direct** — `git add src/frontend/pages/records.py test/... && git commit -m "restore Enter-key search triggering in Records search box"`)

Item 2 (SC-2 — no stale re-search after clear):

- [ ] 10. RED — write an AppTest clear-then-Enter sequence asserting empty state persists; confirm it FAILS with the stale-key read in place. (**task-card** — `task(..., prompt: "execute red task from test-driven-development")`)
  - SC reference: SC-2
- [ ] 11. GREEN — confirm coverage via item 1's dynamic suffix read; the test retains the interaction; make the RED test PASS. (**task-card** — `task(..., prompt: "execute green task from test-driven-development")`)
  - SC reference: SC-2
- [ ] 12. Post-regression — run regression test patterns after GREEN. (**task-card** — `task(..., prompt: "execute phase-4 task from test-driven-development")`)
  - SC reference: SC-2
- [ ] 13. Verify — verify against SC-2: Playwright — clear then Enter, confirm absence of re-search. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-2
- [ ] 14. Commit — stage test + any supporting change as one atomic slice and commit. (**direct**)

Item 3 (SC-3 — button path unchanged, no double commit):

- [ ] 15. RED — write an AppTest button-click regression guard pinning exactly one commit per click; this guard passes BEFORE and AFTER the change (guard existence is the deliverable). (**task-card** — `task(..., prompt: "execute red task from test-driven-development")`)
  - SC reference: SC-3
- [ ] 16. GREEN — assert absence of behavioral delta on the button path; make the guard PASS against the post-item-1 code. (**task-card** — `task(..., prompt: "execute green task from test-driven-development")`)
  - SC reference: SC-3
- [ ] 17. Post-regression — run regression test patterns after GREEN. (**task-card** — `task(..., prompt: "execute phase-4 task from test-driven-development")`)
  - SC reference: SC-3
- [ ] 18. Verify — verify against SC-3: Playwright — button click executes the search exactly once. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-3
- [ ] 19. Commit — stage the guard test as one atomic slice and commit. (**direct**)

Item 4a (SC-4a — neutral placeholder + coupled E2E selector, one delivery unit):

- [ ] 20. RED — write a string assertion that the placeholder is no longer the Enter-instruction wording; confirm it FAILS before the change. (**task-card** — `task(..., prompt: "execute red task from test-driven-development")`)
  - SC reference: SC-4a
- [ ] 21. GREEN — reword the placeholder to neutral wording AND update the E2E aria-label selector in the same cycle — a single delivery unit per R-9 coupling; make the RED test PASS. (**task-card** — `task(..., prompt: "execute green task from test-driven-development")`)
  - SC reference: SC-4a
- [ ] 22. Post-regression — run regression test patterns after GREEN. (**task-card** — `task(..., prompt: "execute phase-4 task from test-driven-development")`)
  - SC reference: SC-4a
- [ ] 23. Verify — verify against SC-4a: Playwright placeholder render + execution of the coupled E2E test against the updated aria-label selector (or AppTest selector check) — proof by execution, not by diff. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-4a
- [ ] 24. Commit — stage placeholder change + selector update as one atomic slice and commit. (**direct**)

Item 4b (SC-4b — zero regression, full suite):

- [ ] 25. Verify — run the complete pytest suite; assert zero new failures against the step-2 baseline. No RED/GREEN (no new behavior) and no dedicated commit (global verification criterion, ordered after item 4a). (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: SC-4b

Post-implementation (Tier 1 — once per plan):

- [ ] 26. Dispatch audit — adversarial audit of the deliverable (investigator, then validator, evaluator, arbiter in sequence). (**task-card** — `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")`)
  - SC reference: all
- [ ] 27. Run Z3 check — re-verify state against the dependency contract. (**direct** — `.opencode/tools/solve check --contract-path .issues/1407/dependency-contract.yaml --state-path .issues/1407/artifacts/state-analysis.yaml` with item variables set true)
  - SC reference: all
- [ ] 28. Dispatch structural checks — run the finishing checklist (lint, typecheck, etc.). (**task-card** — `task(..., prompt: "execute checklist task from finishing-a-development-branch")`)
  - SC reference: SC-4b
- [ ] 29. Dispatch pre-PR gate — read all SC verdicts; BLOCK if any FAIL. (**task-card** — `task(..., prompt: "execute verify task from verification-before-completion")`)
  - SC reference: all
- [ ] 30. Dispatch final regression check before pipeline halt. (**task-card** — `task(..., prompt: "execute phase-4 task from test-driven-development")`)
  - SC reference: SC-4b

Scope boundary: authorization is `for_implementation` — the pipeline HALTS after step 30 (verification complete). Review-prep and PR creation are out of scope for this authorization.

### Phase Completion Block (VbC assertions)

- Every step above reports `[item N] [PASS|FAIL]`; a FAIL halts per the Self-Remediation Protocol.
- All five exit criteria C1-C5 hold with behavioral evidence; DONE_WITH_CONCERNS coerces to FAIL; structural evidence for a behavioral SC is EVIDENCE_TYPE_MISMATCH → FAIL.

**Cost frame:** Running the AppTest + Playwright verification per item costs minutes of bounded execution — the break path that catches the defect at gate 1 with zero downstream rework. Skipping a verification step to save a tool call costs the death spiral: a silent UX regression ships, is discovered only when a user presses Enter and nothing happens, and the rework cycle compounds at 100×-1000× the skipped test's cost. Correctness is the only metric.



