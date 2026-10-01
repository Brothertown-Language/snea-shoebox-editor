---
plan_schema_version: "1.0"
issue: 1392
title: "Unrendered <MAINTAINER_CONTACT> placeholder resolves through st.secrets contact.maintainer_label"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 2
dispatch:
  - "pre-implementation: (orchestrator) [coherence gate, baseline check]"
  - "phase 1 (configuration & documentation enablement): test-driven-development [pre-regression, red, green, post-regression], verification-before-completion [pre-regression-verify, verify], (orchestrator) [commit-inline]"
  - "phase 2 (secrets-based resolution, fail-fast validation & placeholder sweep): test-driven-development [pre-regression, red, green, post-regression], verification-before-completion [pre-regression-verify, verify], (orchestrator) [commit-inline]"
  - "post-implementation: audit [verification-audit], (orchestrator) [z3-check], finishing-a-development-branch [checklist], verification-before-completion [verify], test-driven-development [regression-check], git-workflow-pr [review-prep, create], completion-core [completion]"
---

<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->
<!-- Provenance: AI-generated -->

# Implementation Plan — #1392 — Unrendered `<MAINTAINER_CONTACT>` Placeholder Leaks Into UI

- **Issue:** .issues/1392/spec.md — https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1392
- **Authorization:** approved-for-for_pr — full pipeline through PR creation; human-only merge
- **PR strategy:** stacked — one feature branch, N commits, one PR

## Goal

Resolve the `<MAINTAINER_CONTACT>` placeholder through the existing `st.secrets` mechanism: a new `contact.maintainer_label` key supplies the contact text, all 3 dialog call sites derive it through one shared resolution path, startup validation fails fast with an actionable error naming the key when it is absent, and an AST sweep keeps unrendered placeholders out of every user-facing Streamlit string — so no end user ever sees a raw token.

## Architecture

Secrets-based resolution reusing the proven `[contact]` section (`contact.mastodon_url` already renders correctly there). One shared helper — `get_maintainer_label()` in `src/frontend/ui_utils.py`, no arguments, returns `str` — feeds all 3 call sites (`show_unauthorized_dialog()` in `src/frontend/pages/login.py`, two dialogs in `_initialize_database()` in `streamlit_app.py`); `streamlit_app.py` already imports from that module, so no new module is introduced. Startup validation in `main()` reads the key after `st.set_page_config` (which stays the first Streamlit command) and raises an error naming `contact.maintainer_label` when absent — no silent default. Two phases: configuration/documentation enablement (SC-6, SC-7) precedes the code phase (SC-3 → SC-1 → SC-2/SC-5 interleaved → SC-4), because SC-1's behavioral verify and SC-4's success path both require the key that SC-6 adds. Item numbers track SC numbers; execution order follows the structure artifact's intra-phase sequence.

## Files

- `src/frontend/pages/login.py` — MODIFIED (SC-1, SC-2, SC-3 — dialog contact line)
- `streamlit_app.py` — MODIFIED (SC-2, SC-3, SC-4 — two dialogs + startup validation in `main()`)
- `src/frontend/ui_utils.py` — MODIFIED (SC-3 — shared `get_maintainer_label()` helper)
- `.streamlit/secrets.toml` — MODIFIED (SC-6 — `[contact]` key, additive)
- `.streamlit/secrets.toml.production` — MODIFIED (SC-6 — `[contact]` key, additive, synchronized)
- `docs/development/local-development.md` — MODIFIED (SC-7 — "Configure local secrets" guidance)
- `test/test_shared_contact_resolution_sc3.py` — NEW (SC-3 enforcement)
- `test/ui/test_login_unauthorized_dialog.py` — NEW (SC-1 Playwright e2e)
- `test/test_no_maintainer_contact_token_sc2.py` — NEW (SC-2 grep enforcement)
- `test/test_startup_maintainer_label_sc4.py` — NEW (SC-4 startup fail-fast)
- `test/test_user_facing_placeholder_sweep_sc5.py` — NEW (SC-5 AST sweep)
- `test/test_maintainer_label_secrets_sc6.py` — NEW (SC-6 grep enforcement)
- `test/test_maintainer_label_docs_sc7.py` — NEW (SC-7 grep enforcement)

**Out of scope (unchanged):** dialog layout and surrounding copy; the `contact.mastodon_url` value and its `if mastodon_url` guard; secrets layout beyond the one new key; `src/services/upload_service.py` (the `<SSSSS>` filename-format docstring is a non-user-facing scope boundary for SC-5); generic template-substitution tooling.

## Dispatch

- Pre-implementation: direct (1-2)
- Phase 1: task-card (3-8, 10-13) + direct (9, 14)
- Phase 2: task-card (15-20, 22-25, 27-31, 33-35, 37-40) + direct (21, 26, 32, 36, 41)
- Post-implementation: task-card (42, 44-49) + direct (43)

## Blast Radius

Three `<MAINTAINER_CONTACT>` literals across 2 source files are the defect (one in `src/frontend/pages/login.py`, two in `streamlit_app.py` — live-verified: exactly 3 `*.py` hits). Blast extends to 2 secrets templates, 1 operator doc target, 1 existing UI-test surface, and 1 shared helper in an existing module both consumers already import. One UI-testing standard doc and one scope-boundary counter-example (`<SSSSS>` docstring) are read-only. Impact zones: the `st.write` contact line in the login dialog, the two `st.info` contact lines in `_initialize_database()`, the `[contact]` section of both secrets templates, and startup initialization in `main()` — no dependency, model, or schema changes.

---

## Admonishment — Compliance

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

## One-Step-at-a-Time

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

## Step Status

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

## Enforcement Gate

> **Enforcement gate:** All SCs must pass before this plan is complete.

---

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

---

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Configuration & documentation enablement | CG-1 — `contact.maintainer_label` key added to both secrets templates and documented in local-development guidance; pure config/docs enablement, no code changes | SC-6, SC-7 | — | 3-14 | task-card (3-8, 10-13) + direct (9, 14) |
| 2 | Secrets-based resolution, fail-fast validation & placeholder sweep | CG-2 + CG-3 — one shared resolution helper feeding the 3 call-site migrations, paired with startup fail-fast validation, plus the AST placeholder sweep whose RED straddles SC-2's removal | SC-3, SC-1, SC-2, SC-5, SC-4 | 1 | 15-41 | task-card (15-20, 22-25, 27-31, 33-35, 37-40) + direct (21, 26, 32, 36, 41) |

---

## Self-Remediation Protocol

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

---

## Pre-Implementation (steps 1-2)

- [ ] 1. **Coherence gate (**direct**).** Re-read `.issues/1392/spec.md` and `.issues/1392/artifacts/structure.yaml`; confirm all 7 SCs map to the 2 phases with no structural drift, that every item references exactly one SC-ID, that the phase DAG has no circular dependencies, and that Phase 2's intra-phase execution order matches spec §5 (Item 3 → Item 1 → Item 2 RED → Item 5 RED → Item 2 GREEN → Item 5 GREEN → Item 4) before any implementation begins. **→ all SCs**
  - Sources: spec §3 Success Criteria, spec §5 Items, spec §7 Traceability; `artifacts/structure.yaml` phases, dependency_dag, intra_phase_execution_order.
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-coherence-*`
- [ ] 2. **Baseline check (**direct**).** Verify the working tree is on the issue feature branch at trunk tip with zero pending changes, reproduce the RED baselines (`grep -n "maintainer_label"` → 0 hits in both secrets templates and in the local-development doc; `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` → 3 hits), and record baseline evidence under `tmp/issue-1392/artifacts/`. **→ all SCs**
  - Regression Test Protocol: re-sync the local database first with `bash scripts/sync_prod_to_local.sh` (the sync script from the feature branch under test).
  - Evidence artifact: `tmp/issue-1392/artifacts/baseline-check.yaml`

---

## Phase 1 — Configuration & documentation enablement

**Concern:** CG-1 — add the `contact.maintainer_label` key to both secrets templates (SC-6) and document it in the local-development secrets guidance (SC-7); pure configuration/docs enablement with no code changes.

**Files:** `.streamlit/secrets.toml`, `.streamlit/secrets.toml.production`, `docs/development/local-development.md`; NEW `test/test_maintainer_label_secrets_sc6.py`, `test/test_maintainer_label_docs_sc7.py`.

**SCs:** SC-6 (string), SC-7 (string)

**Dependencies:** none.

**Entry conditions:** after steps 1-2 (coherence gate, baseline check).

**Exit conditions:** key present in both templates and documented in the operator guidance, both enforcement tests green, no `src/` or `streamlit_app.py` changes.

**Code Path Coverage:** CP-6 (SC-6) — insert `contact.maintainer_label` into the `[contact]` section of both secrets templates, preserving the section-order synchronization directive; grep returns 0 hits today (live). CP-7 (SC-7) — insert the key into the "Configure local secrets" guidance of `docs/development/local-development.md`; grep returns 0 hits today (live).

**Cross-Cutting SCs:** none — SC-6 and SC-7 are single-concern per the cross-cutting matrix; this phase carries no cross-phase spans of its own (downstream crossing into SC-1/SC-4 verification is recorded on those SCs).

**Interface Boundaries:** IF-6 secrets-template synchronization contract — both templates stay key-set synchronized; the change is an additive TOML key with no existing key removed or renamed. IF-1's `st.secrets [contact]` mapping gains one key; consumers of `contact.mastodon_url` are untouched.

**State Transitions:** ST-6 — key absent from both templates → key present in both with section-order synchronization preserved (trigger: Item 6 GREEN; invariant: additive only). ST-7 — key undocumented → documented under "Configure local secrets" (trigger: Item 7 GREEN; invariant: grep returns at least 1 hit).

**Steps:**

- [ ] 3. **Pre-regression (**task-card**).** Establish the green baseline before any change per the test-driven-development phase-0 task. **→ SC-6, SC-7**
  - Dispatch: `task(..., prompt: "execute phase-0 task from test-driven-development")`
  - Regression Test Protocol: `bash scripts/sync_prod_to_local.sh` first (feature-branch script).
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-pre-regression-*`
- [ ] 4. **Pre-regression verify (**task-card**).** Confirm the baseline evidence is real — tests actually executed (`tests_run > 0`, all passed, `tests-run.yaml` artifact) — before any RED begins. **→ SC-6, SC-7**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-pre-regression-verify-*`
- [ ] 5. **Item 6 RED (**task-card**).** The SC-6 enforcement test fails on the current state: it asserts at least one `maintainer_label` hit per secrets template while both templates carry zero hits. **→ SC-6**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` returns 0 hits in both files today (live baseline).
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 6. **Item 6 GREEN (**task-card**).** The key is present: `contact.maintainer_label` exists under `[contact]` in both templates with the maintainer's real contact label as its value (a real label — never a synthetic or placeholder string), additive only — no existing key removed or renamed — and the enforcement test passes. **→ SC-6**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 7. **Item 6 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-6**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 8. **Item 6 Verify (**task-card**).** Verify per verification-before-completion: re-run the grep — one hit in each file — and review the diff for additive-only conformance (existing `[contact]` keys intact). **→ SC-6**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 9. **Item 6 Commit (**direct**).** Stage and commit the two secrets templates plus the grep enforcement test as one atomic slice — no sub-agent dispatch. **→ SC-6**
  - Command: `git add .streamlit/secrets.toml .streamlit/secrets.toml.production test/test_maintainer_label_secrets_sc6.py && git commit -m "feat(1392): add contact.maintainer_label key to both secrets templates (SC-6)"`
- [ ] 10. **Item 7 RED (**task-card**).** The SC-7 enforcement test fails on the current state: it asserts at least one `maintainer_label` hit in the local-development secrets guidance while the document carries zero hits. **→ SC-7**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: `grep -n "maintainer_label" docs/development/local-development.md` returns 0 hits today (live baseline).
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 11. **Item 7 GREEN (**task-card**).** The key is documented: the "Configure local secrets" guidance of `docs/development/local-development.md` names `contact.maintainer_label` so operators know to supply it, and the enforcement test passes. **→ SC-7**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 12. **Item 7 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-7**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 13. **Item 7 Verify (**task-card**).** Verify per verification-before-completion: re-run the grep — at least 1 hit in the guidance document. **→ SC-7**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 14. **Item 7 Commit (**direct**).** Stage and commit the documentation plus its grep enforcement test as one atomic slice — no sub-agent dispatch. **→ SC-7**
  - Command: `git add docs/development/local-development.md test/test_maintainer_label_docs_sc7.py && git commit -m "docs(1392): document contact.maintainer_label in local-development secrets guidance (SC-7)"`

**Cost frame:** Grepping the two secrets templates and the local-development guidance costs seconds — key presence and operator documentation are confirmed before any code depends on them. Skipping costs a Phase 2 behavioral verify that fails on a missing key, surfacing the enablement gap downstream at 100× the seconds-cheap grep. Correctness is the only metric.

**Phase 1 completion (VbC assertions):**

- [ ] SC-6: `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` returns at least 1 hit per file; diff review shows additive-only change (no existing key removed or renamed).
- [ ] SC-7: `grep -n "maintainer_label" docs/development/local-development.md` returns at least 1 hit.
- [ ] Both enforcement tests green under `uv run pytest test/`; `git status` clean; no `src/` or `streamlit_app.py` changes in this phase.

**Concern transition:** Leaving configuration/docs enablement → entering the secrets-resolution code phase. Phase 2's SC-1 behavioral verify and SC-4 startup success path both consume the key this phase commits (dependency DAG edge 1→2).

---

## Phase 2 — Secrets-based resolution, fail-fast validation & placeholder sweep

**Concern:** CG-2 + CG-3 — one shared resolution helper (SC-3) feeding the 3 call-site migrations (SC-1 login dialog, SC-2 token removal) paired with startup fail-fast validation (SC-4), plus the AST placeholder sweep (SC-5) whose RED/GREEN straddles SC-2's removal inside this same phase.

**Files:** `src/frontend/pages/login.py`, `streamlit_app.py`, `src/frontend/ui_utils.py` (shared helper home — both consumers already import from it); NEW `test/test_shared_contact_resolution_sc3.py`, `test/ui/test_login_unauthorized_dialog.py`, `test/test_no_maintainer_contact_token_sc2.py`, `test/test_user_facing_placeholder_sweep_sc5.py`, `test/test_startup_maintainer_label_sc4.py`.

**SCs:** SC-3 (semantic), SC-1 (behavioral), SC-2 (string), SC-5 (string), SC-4 (behavioral)

**Dependencies:** 1 (Phase 1).

**Entry conditions:** Phase 1's committed `contact.maintainer_label` key in both secrets templates (SC-1's behavioral verify and SC-4's success path consume it).

**Exit conditions:** all code SCs (SC-1..SC-5) verified.

**Code Path Coverage:** CP-3 (SC-3) — new helper reads `st.secrets["contact"]["maintainer_label"]`, consumed by CP-1, CP-2a, CP-2b, CP-4. CP-1 (SC-1) — `login()` → `show_unauthorized_dialog()` → contact `st.write` line. CP-2a/CP-2b (SC-2) — the two `st.info` contact lines in `_initialize_database()`. CP-2c (SC-2) — grep over Python source must return 0 after GREEN (3 hits today, live). CP-5 (SC-5) — AST sweep over user-facing Streamlit render-call string literals in `src/` and `streamlit_app.py`. CP-4 (SC-4) — `main()` → `st.set_page_config` (stays first Streamlit command) → validation → `_initialize_database()`; error must originate in startup initialization. Adjacent path not modified: the `mastodon_url` read feeding `handle_ui_error`'s contact text in `streamlit_app.py` (no token, unchanged).

**Cross-Cutting SCs:** SC-1 (CG-2 × CG-1 — verification needs the Phase 1 key plus UI-test infrastructure: `test/ui/`, `playwright_e2e`, `SNEA_E2E=1`, live app on :8501). SC-2 (CG-2 × CG-3 — shares the atomic RED/GREEN window with SC-5). SC-4 (CG-2 × CG-1 — success path needs the Phase 1 key; startup-timing assertion). SC-5 (CG-3 × CG-2 — RED pre-removal, GREEN post-removal; scope boundary vs non-user-facing `<SSSSS>` docstring). SC-3 is single-concern.

**Interface Boundaries:** IF-2 shared resolution helper — single function, no arguments, returns `str`; consumers are the 3 call sites, absence path governed by IF-3. IF-3 startup validation — raises an error whose message names `contact.maintainer_label`; `st.set_page_config` must remain the first Streamlit command in `main()`. IF-4 `show_unauthorized_dialog()` signature and behavior unchanged — only the contact line's value source changes. IF-5 `_initialize_database()` signature unchanged — 2 internal `st.info` contact lines change value source. IF-1 `[contact]` mapping gains the key (Phase 1) — `mastodon_url` access pattern and `if mastodon_url` guards unchanged. IF-7 Playwright e2e contract consumed as-is (`SNEA_E2E=1`, `playwright_e2e` marker, live app on :8501, `docs/development/ui_testing_standard.md`).

**State Transitions:** ST-3 — 3 independent inline contact-text expressions → 1 shared resolution path consumed by all 3 call sites (trigger: Item 3 GREEN; invariant: no duplicated hardcoded contact text). ST-1 — dialog renders raw token → renders resolved `contact.maintainer_label` text (trigger: Item 1 GREEN; guard: key present). ST-2 — 3 `<MAINTAINER_CONTACT>` literals in Python source → 0 (trigger: Item 2 GREEN; invariant: grep returns 0 with `--include='*.py'`). ST-5 — no automated sweep → AST sweep exists with zero user-facing placeholder matches (trigger: Item 5 GREEN after Item 2's removal). ST-4 — no startup validation → validation runs during startup initialization, pass branch renders resolved text, fail branch aborts naming `contact.maintainer_label` before any dialog renders (trigger: Item 4 GREEN; invariant: no silent default).

**Steps:**

- [ ] 15. **Pre-regression (**task-card**).** Establish the green baseline for the code phase before any change per the test-driven-development phase-0 task. **→ SC-1..SC-5**
  - Dispatch: `task(..., prompt: "execute phase-0 task from test-driven-development")`
  - Regression Test Protocol: `bash scripts/sync_prod_to_local.sh` first (feature-branch script).
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-pre-regression-*`
- [ ] 16. **Pre-regression verify (**task-card**).** Confirm the baseline evidence is real — tests actually executed (`tests_run > 0`, all passed, `tests-run.yaml` artifact) — before any RED begins. **→ SC-1..SC-5**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-pre-regression-verify-*`
- [ ] 17. **Item 3 RED (**task-card**).** The SC-3 semantic test fails on the current state: a clean-room read of the 3 call sites confirms inline hardcoded contact text rather than a shared reference, while the test asserts a shared path exists and is referenced by all 3. **→ SC-3**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: live read — no shared helper exists; each site independently renders the literal (`login.py` dialog contact line; 2 `_initialize_database()` contact lines).
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 18. **Item 3 GREEN (**task-card**).** The shared path exists: `get_maintainer_label()` added in `src/frontend/ui_utils.py` — reads `contact.maintainer_label` from `st.secrets`, no arguments, returns `str` — and all 3 call sites are routed through it; the semantic test passes. **→ SC-3**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 19. **Item 3 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-3**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 20. **Item 3 Verify (**task-card**).** Verify per verification-before-completion: a clean-room sub-agent reads the 3 former call sites and confirms each references the shared resolution path with no duplicated inline contact text. **→ SC-3**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 21. **Item 3 Commit (**direct**).** Stage and commit the shared helper, its references from all 3 call sites, and the SC-3 enforcement test as one atomic slice — no sub-agent dispatch. **→ SC-3**
  - Command: `git add src/frontend/ui_utils.py src/frontend/pages/login.py streamlit_app.py test/test_shared_contact_resolution_sc3.py && git commit -m "feat(1392): add shared get_maintainer_label() resolution path and route 3 call sites (SC-3)"`
- [ ] 22. **Item 1 RED (**task-card**).** The Playwright dialog test fails on the current state: it asserts the "Access Restricted" dialog shows the `contact.maintainer_label` value and no `<MAINTAINER_CONTACT>` token, and the raw token currently renders. **→ SC-1**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: real-browser test against the live app on :8501 — `test/ui/`, `playwright_e2e` marker, `SNEA_E2E=1`, per `docs/development/ui_testing_standard.md`.
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 23. **Item 1 GREEN (**task-card**).** The dialog renders the resolved label: `show_unauthorized_dialog()` in `src/frontend/pages/login.py` derives the contact text through the shared resolution path, so the dialog shows the `contact.maintainer_label` value and never the raw token. **→ SC-1**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 24. **Item 1 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-1**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 25. **Item 1 Verify (**task-card**).** Verify per verification-before-completion: `SNEA_E2E=1 uv run pytest test/ui/ -m playwright_e2e` against the live app on :8501, per `docs/development/ui_testing_standard.md` — skip-by-design is never PASS, a skipped run reports FAIL for this SC. **→ SC-1**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 26. **Item 1 Commit (**direct**).** Stage and commit the login dialog change plus the Playwright test as one atomic slice — no sub-agent dispatch. **→ SC-1**
  - Command: `git add src/frontend/pages/login.py test/ui/test_login_unauthorized_dialog.py && git commit -m "feat(1392): render maintainer_label in Access Restricted dialog via shared path (SC-1)"`
- [ ] 27. **Item 2 RED (**task-card**).** The SC-2 grep enforcement test fails on the current state: it asserts 0 `<MAINTAINER_CONTACT>` matches in Python source while token literals remain — 2 in `streamlit_app.py` after Item 1's GREEN, per the intra-phase execution order. **→ SC-2**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` returned 3 matches at baseline (live); 2 remain after step 26.
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 28. **Item 5 RED (**task-card**).** The AST sweep test fails on the current state: it asserts zero `<[A-Z][A-Z0-9_]{2,}>` matches across user-facing Streamlit render-call string literals while the `<MAINTAINER_CONTACT>` literals are still present — the pre-Item-2-GREEN window required by spec §5. **→ SC-5**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: sweep scans `st.write`, `st.info`, `st.error`, `st.warning`, `st.success`, `st.markdown`, `st.caption` string literals in `src/` and `streamlit_app.py`; docstring tokens such as `<SSSSS>` in `src/services/upload_service.py` are out of scope by AST construction.
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 29. **Item 2 GREEN (**task-card**).** No token literals remain in Python source: the `<MAINTAINER_CONTACT>` literals at the call sites still outstanding after Item 1 are replaced with the shared resolution path, so `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` returns 0 matches and the enforcement test passes. **→ SC-2**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 30. **Item 2 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-2**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 31. **Item 2 Verify (**task-card**).** Verify per verification-before-completion: re-run the grep with `--include='*.py'` — 0 matches (compiled `__pycache__` artifacts out of scope). **→ SC-2**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 32. **Item 2 Commit (**direct**).** Stage and commit the remaining source call sites plus the grep enforcement test as one atomic slice — no sub-agent dispatch. **→ SC-2**
  - Command: `git add src/frontend/pages/login.py streamlit_app.py test/test_no_maintainer_contact_token_sc2.py && git commit -m "feat(1392): remove MAINTAINER_CONTACT token literals from all call sites (SC-2)"`
- [ ] 33. **Item 5 GREEN (**task-card**).** The AST sweep test passes: it scans the user-facing Streamlit render-call string literals in `src/` and `streamlit_app.py` and reports zero `<[A-Z][A-Z0-9_]{2,}>` matches — no placeholder remediation remains after Item 2's removal, and docstring tokens stay out of scope by AST construction. **→ SC-5**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 34. **Item 5 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-5**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 35. **Item 5 Verify (**task-card**).** Verify per verification-before-completion: `uv run pytest test/` — zero pattern matches across the scanned user-facing strings. **→ SC-5**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 36. **Item 5 Commit (**direct**).** Stage and commit the sweep test plus any remediation it drives (none remains after step 32) as one atomic slice — no sub-agent dispatch. **→ SC-5**
  - Command: `git add test/test_user_facing_placeholder_sweep_sc5.py && git commit -m "test(1392): add AST placeholder sweep for user-facing Streamlit strings (SC-5)"`
- [ ] 37. **Item 4 RED (**task-card**).** The startup fail-fast test fails on the current state: it invokes the app startup path with `contact.maintainer_label` absent and asserts an actionable error naming the key is raised from startup initialization, but no validation exists. **→ SC-4**
  - Dispatch: `task(..., prompt: "execute red task from test-driven-development")`
  - Evidence: live read — no startup validation exists today (spec SC-4 RED premise); `main()` goes `st.set_page_config` → `_initialize_database()`.
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-red-*`
- [ ] 38. **Item 4 GREEN (**task-card**).** Startup validation exists: `main()` in `streamlit_app.py` reads `contact.maintainer_label` and raises an actionable error naming the key when it is absent — no silent default — with `st.set_page_config` still the first Streamlit command. **→ SC-4**
  - Dispatch: `task(..., prompt: "execute green task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-green-*`
- [ ] 39. **Item 4 Post-regression (**task-card**).** Run regression test patterns after GREEN per the test-driven-development phase-4 task. **→ SC-4**
  - Dispatch: `task(..., prompt: "execute phase-4 task from test-driven-development")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-post-regression-*`
- [ ] 40. **Item 4 Verify (**task-card**).** Verify per verification-before-completion: `uv run pytest test/` — the error is raised from startup initialization, not from a dialog-render call, and its message names `contact.maintainer_label`. **→ SC-4**
  - Dispatch: `task(..., prompt: "execute verify task from verification-before-completion")`
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-verify-*`
- [ ] 41. **Item 4 Commit (**direct**).** Stage and commit the startup validation plus its test as one atomic slice — no sub-agent dispatch. **→ SC-4**
  - Command: `git add streamlit_app.py test/test_startup_maintainer_label_sc4.py && git commit -m "feat(1392): fail fast at startup when contact.maintainer_label is absent (SC-4)"`

**Cost frame:** Running the Playwright dialog test, the startup fail-fast test, the clean-room call-site read, and the AST sweep costs minutes of execution time — the end-user placeholder leak and every sibling placeholder are caught before merge. Skipping costs a shipped dialog that renders a raw token to every restricted user, surfacing at 1000× the fix cost. Correctness is the only metric.

**Phase 2 completion (VbC assertions):**

- [ ] SC-3: clean-room read confirms all 3 former call sites reference the shared resolution path with no duplicated inline contact text.
- [ ] SC-1: `SNEA_E2E=1 uv run pytest test/ui/ -m playwright_e2e` PASS against the live app on :8501 — dialog shows the `contact.maintainer_label` value, no `<MAINTAINER_CONTACT>` token; skip-by-design never PASS.
- [ ] SC-2: `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` returns 0 matches.
- [ ] SC-5: `uv run pytest test/` — AST sweep reports zero user-facing placeholder matches; `<SSSSS>` docstring out of scope by AST construction.
- [ ] SC-4: startup test passes — error raised from startup initialization naming `contact.maintainer_label`; `st.set_page_config` still the first Streamlit command.
- [ ] `git status` clean; each of the 7 items committed as its own atomic slice (steps 9, 14, 21, 26, 32, 36, 41).

**Concern transition:** Leaving the secrets-resolution code phase → entering the post-implementation pipeline. Phase 1 + Phase 2 deliver all 7 SCs' code and tests; the post-implementation gates (audit → z3-check → structural → pre-pr-gate → regression → review-prep → PR → completion) prove them end to end. Plan execution ends at step 49; human-only merge applies.

---

## Post-Implementation (steps 42-49)

- [ ] 42. **Audit (**task-card**).** Adversarial audit of the deliverable: `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — followed by validator, evaluator, arbiter in sequence. **→ all SCs**
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-audit-*`
- [ ] 43. **Z3 check (**direct**).** Run `.opencode/tools/solve check --state-path .issues/1392/artifacts/state-analysis.yaml --contract-path .issues/1392/dependency-contract.yaml` directly — no sub-agent dispatch. **→ all SCs**
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-z3-check-*`
- [ ] 44. **Structural checks (**task-card**).** Run the finishing checklist (lint, typecheck, branch readiness): `task(..., prompt: "execute checklist task from finishing-a-development-branch")`. **→ all SCs**
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-structural-checks-*`
- [ ] 45. **Pre-PR gate (**task-card**).** Verify every SC verdict — BLOCK if any FAIL: `task(..., prompt: "execute verify task from verification-before-completion")`. A DONE_WITH_CONCERNS or EVIDENCE_TYPE_MISMATCH verdict is coerced to FAIL. **→ all SCs**
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-pre-pr-gate-*`
- [ ] 46. **Regression check (**task-card**).** Final regression check before the PR: `task(..., prompt: "execute phase-4 task from test-driven-development")`. **→ all SCs**
  - Pre-clean: `rm -f ./tmp/issue-1392/artifacts/pipeline-regression-check-*`
  - Regression Test Protocol: `bash scripts/sync_prod_to_local.sh` first.
- [ ] 47. **Review-prep (**task-card**).** Prepare PR review context: `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")`. **→ all SCs**
- [ ] 48. **Create PR (**task-card**).** Create the pull request (stacked — one feature branch, N commits, one PR): `task(..., prompt: "execute create task from git-workflow-pr")`. Human-only merge — the agent does not merge; no auto-closing keywords for the stakeholder issue. **→ all SCs**
- [ ] 49. **Completion summary (**task-card**).** Generate the completion executive summary: `task(..., prompt: "execute completion task from completion-core")`. **→ all SCs**

---

## Exit Criteria

- [ ] C1. SC-6 passes: `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` returns at least one hit in each file (string evidence; additive only — no existing key removed or renamed).
- [ ] C2. SC-7 passes: `grep -n "maintainer_label" docs/development/local-development.md` returns at least one hit (string evidence).
- [ ] C3. SC-3 passes: a clean-room read of the 3 former call sites confirms each derives the contact text through the shared resolution path with no duplicated inline contact text (semantic evidence).
- [ ] C4. SC-1 passes: the Playwright real-browser test against the live app on :8501 asserts the dialog shows the `contact.maintainer_label` value and contains no `<MAINTAINER_CONTACT>` token (behavioral evidence; a skip-by-design run is never PASS).
- [ ] C5. SC-2 passes: `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` returns 0 matches (string evidence; compiled `__pycache__` artifacts out of scope).
- [ ] C6. SC-5 passes: the AST sweep test reports zero `<[A-Z][A-Z0-9_]{2,}>` matches across user-facing Streamlit render-call string literals; docstring tokens such as `<SSSSS>` in `src/services/upload_service.py` remain out of scope by construction (string evidence).
- [ ] C7. SC-4 passes: the startup test with `contact.maintainer_label` absent asserts the error is raised from startup initialization — not a dialog-render call — and its message names `contact.maintainer_label` (behavioral evidence).
- [ ] C8. Each of the 7 items ran its own RED → GREEN → post-regression → verify → commit cycle, RED failing before GREEN, with test and implementation committed as one atomic slice; the phase DAG executed 1 → 2 with no cycles.
- [ ] C9. Post-implementation gates all pass (audit, z3-check, structural checks, pre-pr-gate, regression check) and the stacked PR is created — human-only merge.

---

## lifecycle_events

- event: plan_created
  timestamp: 2026-10-01T16:35:44Z
  plan_file: .issues/1392/plan.md
  phase_count: 2

---

*Co-authored with AI: OpenCode (opencode/mimo-v2.6-flash-free)*
