---
remote_issue: 1392
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1392
promoted_at: 2026-09-30T17:10:00Z
labels:
  - needs-approval
---

# SPEC-FIX: Unrendered `<MAINTAINER_CONTACT>` Placeholder Leaks Into UI

## 1. Intent and Executive Summary

| # | Field | Description |
|---|-------|-------------|
| 1 | **Problem Statement** | The "Access Restricted" dialog on the login page renders a raw, unrendered `<MAINTAINER_CONTACT>` template placeholder to end users instead of the intended maintainer contact text. |
| 2 | **Root Cause / Motivation** | The placeholder is never resolved because no substitution mechanism exists in the codebase: the literal string is hardcoded at 3 call sites — `show_unauthorized_dialog()` in `src/frontend/pages/login.py` and two dialogs in `_initialize_database()` in `streamlit_app.py` — and a grep over Python source files only finds those 3 hits (stale `__pycache__` compiled artifacts may also match, but they contain no authored source); no environment variable, secret key, or build step defines or replaces it. Introduced in commit 36c7153 ("Batch implementation: 17 issues"), likely copied from a template whose placeholder-substitution step never landed. The Mastodon URL itself renders correctly via `st.secrets["contact"]["mastodon_url"]` (`.streamlit/secrets.toml`), which proves the secrets mechanism already works for these dialogs. |
| 3 | **Approach Chosen** | Resolve the placeholder through the existing `st.secrets` mechanism: a new `contact.maintainer_label` key in the `[contact]` section supplies the contact text, all 3 call sites read it through one shared resolution path, and startup validation fails fast with an actionable error naming the key when it is absent. |
| 4 | **Alternatives Considered & Why Discarded** | **Alternative: rewrite the dialog text to avoid the `<...>` template form entirely.** Discarded because a rewritten inline literal reintroduces duplicated hardcoded contact text at 3 call sites — violating the single-source-of-truth requirement — and makes the contact text unconfigurable per environment. **Alternative: build the missing generic template-substitution step.** Discarded because a build-time substitution mechanism is disproportionate for a single placeholder; the secrets mechanism already resolves `contact.mastodon_url` at runtime and carries the same rendering guarantee. |
| 5 | **Key Design Decisions** | (1) Secrets-based resolution via the existing `[contact]` section — tradeoff: every deployed environment supplies one more key, but contact text stays environment-configurable and reuses the proven `st.secrets` path instead of a new mechanism. (2) Fail-fast at startup when the key is absent — tradeoff: the app refuses to start rather than rendering a default, trading deploy-time availability for the guarantee that an unrendered placeholder or silent default never reaches an end user. (3) One shared resolution helper feeding all 3 call sites — tradeoff: a small refactor surface, in exchange for eliminating future call-site drift. |
| 6 | **User Intent / Original Prompt** | The developer reported that the "Access Restricted" dialog displays a raw `<MAINTAINER_CONTACT>` placeholder instead of the intended maintainer contact, and asked for the placeholder to resolve so end users see real contact text. |

## 2. Not Included

- **[Dialog layout redesign]** — Only the contact text resolution changes; dialog structure and copy around the contact line stay as they are.
- **[Contact destination value]** — The Mastodon URL value (`contact.mastodon_url`) is unchanged; only the contact label resolves differently.
- **[Secrets file restructuring]** — Beyond adding the `contact.maintainer_label` key to the existing `[contact]` section, the secrets layout is unchanged.
- **[Generic template-substitution framework]** — A single secrets-sourced key covers this defect; a build-time substitution pipeline is disproportionate to the problem.

## 3. Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|----------------------|
| SC-1 | The "Access Restricted" dialog on the login page SHALL render the resolved maintainer contact text (the `contact.maintainer_label` value) to end users; the raw `<MAINTAINER_CONTACT>` token SHALL NOT be displayed | `behavioral` | Playwright real-browser test against the live app on :8501 (`test/ui/`, `playwright_e2e` marker, `SNEA_E2E=1`, per `docs/development/ui_testing_standard.md`) asserting the dialog shows the `contact.maintainer_label` value and contains no `<MAINTAINER_CONTACT>` token | `docs/development/ui_testing_standard.md`; `src/frontend/pages/login.py` `show_unauthorized_dialog()` |
| SC-2 | The literal `<MAINTAINER_CONTACT>` token SHALL NOT appear in any user-facing source string | `string` | `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` returns 0 matches (the `--include='*.py'` scope keeps stale `__pycache__/*.pyc` compiled artifacts, which retain the pre-fix literal, out of the check) | `src/frontend/pages/login.py` `show_unauthorized_dialog()`; `streamlit_app.py` `_initialize_database()` |
| SC-3 | The maintainer contact text SHALL have a single source of truth — each of the 3 former call sites SHALL derive it through one shared resolution path, with no duplicated hardcoded contact text remaining | `semantic` | Clean-room sub-agent reads the 3 former call sites and confirms each references the shared resolution path rather than an inline literal | `src/frontend/pages/login.py` `show_unauthorized_dialog()`; `streamlit_app.py` `_initialize_database()` |
| SC-4 | When `contact.maintainer_label` is absent from the environment's secrets, the app SHALL fail fast during startup with an actionable error naming `contact.maintainer_label` | `behavioral` | Test invokes the app startup path with `contact.maintainer_label` absent and asserts the error is raised from startup initialization — not deferred to a dialog-render call — with a message naming `contact.maintainer_label` (`uv run pytest test/`) | `streamlit_app.py` startup path; `test/` pytest suite |
| SC-5 | No user-facing string SHALL contain an unrendered `<ALL_CAPS_TEMPLATE_TOKEN>` placeholder | `string` | Run a repo test (added with this SC) that uses Python's `ast` module to scan string literals passed to user-facing Streamlit render calls (`st.write`, `st.info`, `st.error`, `st.warning`, `st.success`, `st.markdown`, `st.caption`) in `src/` and `streamlit_app.py` and asserts zero matches of the `<[A-Z][A-Z0-9_]{2,}>` pattern; AST parsing excludes docstrings and comments by construction, so non-user-facing tokens such as the `<SSSSS>` filename-format docstring in `src/services/upload_service.py` are out of scope (`uv run pytest test/`) | `src/services/upload_service.py` filename-format docstring (scope-boundary counter-example) |
| SC-6 | The `contact.maintainer_label` key SHALL be present in the secrets templates (`.streamlit/secrets.toml` and `.streamlit/secrets.toml.production`) so every deployed environment can supply it | `string` | `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` returns at least one hit in each file | `.streamlit/secrets.toml`; `.streamlit/secrets.toml.production` (synchronization directive) |
| SC-7 | The `contact.maintainer_label` key SHALL be documented in the local-development secrets-configuration guidance (`docs/development/local-development.md`) so deployed environments can supply it | `string` | `grep -n "maintainer_label" docs/development/local-development.md` returns at least one hit | `docs/development/local-development.md` "Configure local secrets" |
| SC-8 | A local-run test simulation mechanism SHALL exist as ONE deliverable — a simulation hook implemented as the environment variable `SNEA_SIMULATE_AUTH` with an enumerated parameter domain of exactly three values (`authorized` \| `unauthorized` \| `anonymous`) — that the app's identity path honors ONLY when the secrets `[runtime]` mode equals "local"; production mode SHALL ignore the variable entirely (the inertness guard is the mode check, not the env var's presence). The three simulated auth states are that one mechanism's specified parameter domain: `authorized` (identity sync succeeds), `unauthorized` (authenticated token whose identity sync fails → `is_unauthorized` → Access Restricted dialog), `anonymous` (no auth). No browser auth cookies SHALL be fabricated | `behavioral` | Playwright e2e runs with `SNEA_E2E=1` (`uv run pytest test/ui/ -m playwright_e2e`, live app on :8501) asserting all three states: `authorized` syncs identity successfully; `unauthorized` renders the Access Restricted dialog with the resolved `contact.maintainer_label` contact text and no raw `<MAINTAINER_CONTACT>` token; `anonymous` redirects to `/login` without the dialog. The mechanism either honors the variable in local mode and is inert in production mode, or it does not | `docs/development/ui_testing_standard.md` (agents never fabricate cookie state; the simulation replaces the headed developer-login fixture requirement for the unauthorized-state test ONLY) |

## 4. Requirements

- R-1. The system SHALL render maintainer contact text resolved from the `[contact]` secrets section in every dialog that references it, and the raw `<MAINTAINER_CONTACT>` token SHALL NOT be displayed to end users.
- R-2. All 3 former call sites SHALL derive the contact text through one shared resolution path; duplicated hardcoded contact text SHALL NOT remain.
- R-3. The system SHALL validate `contact.maintainer_label` during app startup, before any dialog renders, and SHALL fail fast with an actionable error naming the missing key when it is absent; silent defaults SHALL NOT substitute for the missing key.
- R-4. No user-facing string SHALL contain an unrendered `<ALL_CAPS_TEMPLATE_TOKEN>` placeholder.
- R-5. The `contact.maintainer_label` key SHALL be present in both `.streamlit/secrets.toml` and `.streamlit/secrets.toml.production`.
- R-6. The `contact.maintainer_label` key SHALL be documented in the local-development secrets-configuration guidance.
- R-7. The local-run test simulation mechanism for Playwright e2e auth states SHALL be ONE mechanism — the `SNEA_SIMULATE_AUTH` environment variable hook (values: `authorized` \| `unauthorized` \| `anonymous`) — whose activation is guarded by the secrets `[runtime]` mode check: the app SHALL honor the variable ONLY when `[runtime]` mode equals "local", and production mode SHALL ignore it entirely. No browser auth cookies SHALL be fabricated.

## 5. Items

Items map 1:1 to success criteria; item numbers track SC numbers, not execution order. Phase grouping is declared in §7 Traceability: Items 6–7 (configuration and documentation) form the enablement phase, which precedes the code phase containing Items 1–5 and 8. Within the code phase the plan sequences execution: the shared resolution path (Item 3) precedes the call-site migrations that consume it (Items 1, 2, 4), the entire Item 5 (SC-5) cycle co-locates with the Item 2 (SC-2) removal — Item 5's RED runs while the original `<MAINTAINER_CONTACT>` literals are still present, before Item 2's GREEN removes them, and Item 5's GREEN, verify, and commit run after Item 2's GREEN, all within the same phase — and the auth-state simulation (Item 8) executes between Item 1's GREEN and Item 1's verify, because SC-1's live Playwright verification of the unauthorized state requires the SC-8 simulation to reach the Access Restricted dialog.

### Item 1 (SC-1): Render resolved contact text in the "Access Restricted" dialog

- RED: Playwright real-browser test asserts the dialog shows the `contact.maintainer_label` value and no `<MAINTAINER_CONTACT>` token; it fails because the raw token currently renders.
- GREEN: Route `show_unauthorized_dialog()` in `src/frontend/pages/login.py` through the shared resolution path so it renders the `contact.maintainer_label` value.
- verify: `SNEA_E2E=1 uv run pytest test/ui/ -m playwright_e2e` against the live app on :8501, per `docs/development/ui_testing_standard.md`.
- commit: `src/frontend/pages/login.py` and the Playwright test.

### Item 2 (SC-2): Remove the literal token from user-facing source strings

- RED: `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` currently returns 3 matches; the enforcement test asserts 0.
- GREEN: Replace the literal at all 3 call sites with the shared resolution path.
- verify: Re-run the grep (with `--include='*.py'`); 0 matches.
- commit: `src/frontend/pages/login.py`, `streamlit_app.py`, and the grep enforcement test.

### Item 3 (SC-3): Add the shared resolution path for the maintainer contact text

- RED: Clean-room read of the 3 call sites confirms inline hardcoded contact text rather than a shared reference; the test asserts a shared path exists and is referenced by all 3.
- GREEN: Add one shared resolution helper that reads `contact.maintainer_label` from `st.secrets` and route all 3 call sites through it.
- verify: Clean-room sub-agent reads the 3 former call sites and confirms each references the shared resolution path.
- commit: the shared helper plus its reference from all 3 call sites.

### Item 4 (SC-4): Fail fast at startup when the contact label key is absent

- RED: Test invokes the app startup path with `contact.maintainer_label` absent and asserts an actionable error naming the key is raised from startup initialization; it fails because no validation exists.
- GREEN: Add a startup validation step that reads `contact.maintainer_label` and raises an actionable error naming the key when it is absent.
- verify: `uv run pytest test/` — assert the error is raised from startup, not from a dialog-render call, and that its message names `contact.maintainer_label`.
- commit: the startup validation and its test.

### Item 5 (SC-5): Sweep user-facing strings for unrendered placeholders

- RED: The AST-based sweep test asserts zero `<[A-Z][A-Z0-9_]{2,}>` matches across user-facing render-call string literals; it fails while the `<MAINTAINER_CONTACT>` literals (SC-2) are still present.
- GREEN: Add the AST sweep test scanning user-facing Streamlit render-call string literals; remediate any placeholder it finds.
- verify: `uv run pytest test/` — zero pattern matches across the scanned user-facing strings; docstring tokens such as `<SSSSS>` in `src/services/upload_service.py` remain out of scope by construction.
- commit: the sweep test plus any remediation it drives.

### Item 6 (SC-6): Add the contact label key to both secrets templates

- RED: `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` currently returns 0 hits; the test asserts at least one hit per file.
- GREEN: Add `contact.maintainer_label` with its value to `.streamlit/secrets.toml` and `.streamlit/secrets.toml.production`, preserving the section-order synchronization directive.
- verify: Re-run the grep; one hit in each file.
- commit: `.streamlit/secrets.toml`, `.streamlit/secrets.toml.production`, and the grep enforcement test.

### Item 7 (SC-7): Document the contact label key in local-development guidance

- RED: `grep -n "maintainer_label" docs/development/local-development.md` currently returns 0 hits; the test asserts at least one hit.
- GREEN: Document `contact.maintainer_label` in the "Configure local secrets" guidance so operators know to supply it.
- verify: Re-run the grep; at least one hit.
- commit: `docs/development/local-development.md` and the grep enforcement test.

### Item 8 (SC-8): Local-run auth-state simulation for Playwright e2e tests

- RED: A Playwright e2e test asserting that the `unauthorized` simulation state reaches the Access Restricted dialog and that the `anonymous` state reaches `/login` fails because no simulation mechanism exists — the only saved storage state belongs to an authorized user (identity sync succeeds, so the dialog never fires), and anonymous visitors redirect to `/login` without rendering the dialog; agents must not authenticate on the developer's behalf per `docs/development/ui_testing_standard.md`.
- GREEN: Add ONE local-run simulation mechanism — a hook implemented as the `SNEA_SIMULATE_AUTH` environment variable (`authorized` \| `unauthorized` \| `anonymous`) that the app's identity path honors ONLY when the secrets `[runtime]` mode equals "local"; production mode ignores it entirely — letting Playwright e2e tests drive the live app in the three simulated auth states without fabricating browser auth cookies.
- verify: `SNEA_E2E=1 uv run pytest test/ui/ -m playwright_e2e` against the live app on :8501 — the `unauthorized` state reaches the Access Restricted dialog (the SC-1 unblocking proof), the `authorized` state syncs identity successfully, and the `anonymous` state reaches `/login` without the dialog.
- commit: the simulation mechanism and its Playwright tests.

## 6. Dependencies

- **Reference:** `.streamlit/secrets.toml` `[contact]` section
- **Relationship:** Existing source of `contact.mastodon_url`; the new `contact.maintainer_label` key joins this section and feeds the shared resolution path.
- **Status:** Satisfied (existing; new key added by SC-6).
- **Reference:** `docs/development/ui_testing_standard.md`
- **Relationship:** Mandatory procedure for the SC-1 Playwright verification. The SC-8 local-run auth-state simulation replaces the headed developer-login fixture requirement for the unauthorized-state test ONLY; agents still never fabricate cookie state.
- **Status:** Satisfied (existing).
- **Reference:** `test/ui/` Playwright infrastructure (`playwright_e2e` marker, `SNEA_E2E=1` gating)
- **Relationship:** Required execution environment for SC-1 and SC-8.
- **Status:** Satisfied (existing; SC-8 adds the simulation mechanism the SC-1 unauthorized-state test consumes).

## 7. Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1, SC-2 | Phase 2 |
| R-2 | SC-3 | Phase 2 |
| R-3 | SC-4 | Phase 2 |
| R-4 | SC-5 | Phase 2 |
| R-5 | SC-6 | Phase 1 |
| R-6 | SC-7 | Phase 1 |
| R-7 | SC-8 | Phase 2 |

## 8. Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| Login dialog call site | code | `src/frontend/pages/login.py` `show_unauthorized_dialog()` | read (primary defect site) |
| Database-error dialog call sites | code | `streamlit_app.py` `_initialize_database()` | read (two additional defect sites) |
| Secrets templates | config | `.streamlit/secrets.toml`, `.streamlit/secrets.toml.production` | read (existing `[contact]` section; section-order synchronization directive) |
| Secrets `[runtime]` mode | config | `.streamlit/secrets.toml` `[runtime]` section | read (SC-8 inertness guard source — the mode check gates `SNEA_SIMULATE_AUTH`) |
| Local-development secrets guidance | doc | `docs/development/local-development.md` "Configure local secrets" | read (SC-7 documentation target) |
| UI testing standard | doc | `docs/development/ui_testing_standard.md` | read (SC-1 verification procedure; `playwright_e2e` / `SNEA_E2E=1` gating) |
| Non-user-facing token counter-example | code | `src/services/upload_service.py` filename-format docstring | read (scope boundary for SC-5: `<SSSSS>` is documentation, not a user-facing string) |
| Root-cause commit | code | commit 36c7153 ("Batch implementation: 17 issues") | recorded in the GitHub issue #1392 body |

## 9. Enforcement Gate

> **Enforcement gate:** All success criteria (SC-1 through SC-8) MUST pass before this spec is considered complete. Partial implementation is not permitted.

## 10. Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Running the Playwright dialog test costs minutes of live-browser execution — the end-user rendering defect is caught before merge. Skipping costs a shipped dialog that shows a raw placeholder to every restricted user — a visible defect surfacing at 1000× the fix cost.
- **SC-2:** Running the token grep costs seconds — source-level removal is confirmed in one pass. Skipping costs a leftover literal that reintroduces the leak on the next render — surfacing at 1000× the fix cost.
- **SC-3:** Reading the 3 call sites against the shared resolution path costs minutes of clean-room review — call-site drift is caught at review time. Skipping costs divergent contact text reappearing across dialogs — a maintenance defect surfacing at 1000× the fix cost.
- **SC-4:** Running the fail-fast test costs minutes — the missing-key path is proven to abort at startup. Skipping costs a deployed environment that renders without contact text or fails silently at runtime — an integrity defect surfacing at 1000× the fix cost.
- **SC-5:** Running the AST sweep costs seconds — every user-facing string is scanned with docstrings excluded by construction. Skipping costs an undiscovered sibling placeholder reaching an end user — surfacing at 1000× the fix cost.
- **SC-6:** Grepping the secrets templates costs seconds — key presence is confirmed in both files. Skipping costs a deployed environment that cannot supply the key — a deploy-time failure surfacing at 1000× the fix cost.
- **SC-7:** Grepping the local-development guidance costs seconds — the documentation gap is confirmed. Skipping costs the next operator rediscovering the key by reading source — defect-discovery latency at 1000× the fix cost.
- **SC-8:** Running the Playwright auth-state simulation tests costs minutes of live-browser execution — all three `SNEA_SIMULATE_AUTH` states are proven against the live app and the mode-gated production inertness is confirmed before merge, and the SC-1 unauthorized-state verification becomes executable at all. Skipping costs a permanently blocked SC-1 behavioral verification (the only saved storage state belongs to an authorized user, so the Access Restricted dialog can never be driven) — an untestable acceptance criterion surfacing at 1000× the fix cost.

## 11. Edge Cases

- **Input boundaries:** `contact.maintainer_label` present with a non-empty value → the dialogs render it. `contact.maintainer_label` absent from `[contact]` → startup validation raises an error naming `contact.maintainer_label` (R-3). `contact.mastodon_url` absent → the existing `if mastodon_url` guard skips the contact link, unchanged by this spec.
- **State transitions:** App startup → key validation passes → dialogs render resolved text. App startup → key validation fails → startup aborts with an actionable error before any dialog renders.
- **Failure modes:** A deployed environment whose secrets lack the key → fail-fast error at startup naming the key, never a raw placeholder and never a silent default. The shared resolution path raising → surfaces as a startup failure, never as a partial render.
- **Concurrency:** Not applicable — resolution reads `st.secrets` at startup and render time with no shared mutable state and no race surface.
- **Recovery:** The operator adds `contact.maintainer_label` to the environment's secrets following SC-6/SC-7 guidance and restarts the app; startup then validates the key and renders proceed.

## 12. Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-10-01 | Initial spec (promoted from issue body) | Spec promotion from GitHub issue #1392 | AI agent (spec-creation create task) |
| 2026-10-01 | Added Success Criteria section: 6 SCs with per-SC evidence types (`behavioral`, `string`, `semantic`) and verification methods, derived from Problem/Root Cause/Approach/Impact and the published exec-summary Scope; added Enforcement Gate statement | writing-plans analyze returned BLOCKED with `NO_SUCCESS_CRITERIA` — spec had no Success Criteria table, preventing per-SC plan decomposition. Implementation intent, scope, and requirements unchanged | AI agent (spec-creation revise task) under `for_pr` authorization scope |
| 2026-10-01 | Structural completion revision: restructured the preamble into the 6-field Intent and Executive Summary (Problem Statement, Root Cause / Motivation, Approach Chosen, Alternatives Considered & Why Discarded, Key Design Decisions, User Intent / Original Prompt); added Not Included, Requirements (R-1–R-6, SHALL language), Items (1:1 with SCs), Dependencies, Traceability, Documentation Sources (§8 plus a Documentation Sources column on the SC table), Cost Frame (per-SC), and Edge Cases. Resolved the Approach either/or to a single secrets-based strategy (`contact.maintainer_label` via `st.secrets`) consistent with SC-4/SC-6. Split compound original SC-6 into SC-6 (secrets templates) and SC-7 (docs). Rewrote SC-5 verification as an AST scan scoped to user-facing Streamlit render-call string literals, excluding the non-user-facing `<SSSSS>` docstring in `src/services/upload_service.py`. Strengthened SC-4 verification to assert startup-timing. Replaced line-number call-site references with stable function anchors. Removed the unreproduced "Visible at localhost:8501" claim. | Validation findings: aggregate FAIL (20 checks: 11 PASS, 9 FAIL) — 11 missing required structure sections, unresolved either/or escape hatch, SC-5 determinism/evidence-scope defect, SC-6 compound SC, shall-language conformance; warnings: SC-4 startup-timing verification and unreproduced visibility claim. Intent, scope, and implementation approach unchanged | AI agent (spec-creation revise task) under `for_pr` authorization scope |
| 2026-10-01 | Phase regrouping for triplet co-location: §7 Traceability now assigns R-5/R-6 (SC-6, SC-7) to Phase 1 (configuration/documentation enablement) and R-1–R-4 (SC-1–SC-5) to Phase 2 (code), replacing the previous Phase 1 [SC-1–SC-4] / Phase 2 [SC-5] / Phase 3 [SC-6, SC-7] split. §5 Items preamble now declares the grouping source, that item numbers track SC numbers rather than execution order, and that the entire Item 5 (SC-5) cycle co-locates with the Item 2 (SC-2) removal — RED before Item 2's GREEN while the `<MAINTAINER_CONTACT>` literals are still present, GREEN/verify/commit after Item 2's GREEN, all within the same phase. No SC wording, evidence types, verification methods, requirements, or scope changes. | writing-plans research BLOCKED with `TRIPLET_SPLIT`: SC-5's RED must execute while the 3 `<MAINTAINER_CONTACT>` literals are still present (pre-SC-2-removal window), but SC-5's GREEN requires the post-SC-2-removal state, and the previous grouping placed SC-5 in a later phase than SC-2 — no atomic phase ordering co-located SC-5's RED/GREEN/verify/commit triplet (corroborated by concern-map CG-3 sequencing note). Config/docs regrouped ahead of the code phase because SC-1's behavioral verify and SC-4's post-validation startup both require the `contact.maintainer_label` key that SC-6 adds to test secrets — the cross-phase dependency recorded in research-blocked.yaml's corroborating finding, which would otherwise fail Phase 1 verification under sequential phase execution. | AI agent (spec-creation revise task) under `for_pr` authorization scope |
| 2026-10-01 | Verification-scope fix for SC-2: added `--include='*.py'` to SC-2's verification command and to Item 2's RED and verify commands (previously bare `grep -rn "<MAINTAINER_CONTACT>" src/ streamlit_app.py`); clarified Root Cause / Motivation to state the 3-hit grep scope is Python source files only, noting stale `__pycache__` compiled artifacts may also match but contain no authored source. | Validation findings: aggregate FAIL (20 checks, 19 PASS, 1 FAIL) — sole failure structural check 3.5 `VERIFICATION_METHOD_SCOPE_MISMATCH` on SC-2: the bare grep also matches the stale compiled artifact `src/frontend/pages/__pycache__/login.cpython-312.pyc` (live-verified: 4 hits = 3 source + 1 binary), so after GREEN the method cannot report the criterion as satisfied. Intent, scope, requirements, and success-criteria semantics unchanged | AI agent (spec-creation revise task) under `for_pr` authorization scope |
| 2026-10-01 | Added SC-8 (new success criterion): a local-run test simulation mechanism that lets Playwright e2e tests drive the live app in three simulated auth states — fully logged in (identity sync succeeds), restricted login (authenticated token whose identity sync fails → `is_unauthorized` → Access Restricted dialog), and no auth — without fabricating browser auth cookies, inert in production (guarded via `[runtime]` mode = "local" or a test-only entry-point wrapper; never triggered by an env var alone in production mode). Evidence type `behavioral`; verification `SNEA_E2E=1 uv run pytest test/ui/ -m playwright_e2e`. Added matching R-7, Item 8 (1:1, code phase, sequenced between Item 1's GREEN and Item 1's verify because SC-1's unauthorized-state verification requires the simulation), Traceability row (R-7 → SC-8, Phase 2), Cost Frame entry, and Enforcement Gate update to SC-1..SC-8. Updated the UI-testing-standard cross-reference: the simulation replaces the headed developer-login fixture requirement for the unauthorized-state test ONLY; agents still never fabricate cookie state. All existing SCs unchanged — no SC weakened. Linked plan synced in the same revision (Item 8 added to Phase 2; dependency contract gains sc8_done and the SC-1←SC-8 ordering edge). | Developer direction mid-pipeline (chat 2026-10-01): "I think we need some way to monkey patch the local test run so you can properly simulate fully logged in vs restricted login vs no auth login." Blocker context: SC-1's live Playwright verification requires an authenticated-but-unauthorized session; the only saved storage state belongs to an authorized user (identity sync succeeds, dialog never fires); anonymous visitors redirect to /login without rendering the Access Restricted dialog; agents must not authenticate on the developer's behalf per the UI testing standard | Developer (Michael Conrad), executed by AI agent (spec-creation revise task) under `for_pr` authorization scope |
| 2026-10-01 | SC-8 wording revision: resolved the implementor-choice either/or guard mechanism to ONE mechanism — the `SNEA_SIMULATE_AUTH` environment variable hook (values: `authorized` \| `unauthorized` \| `anonymous`) that the app's identity path honors ONLY when the secrets `[runtime]` mode equals "local"; production mode ignores it entirely (the inertness guard is the mode check, not the env var's presence). Removed the "e.g." and "or" escape-hatch language. Made atomicity explicit: the three simulated auth states are the enumerated parameter values of the ONE simulation hook (one deliverable), not three deliverables. SC-8 verification now covers all three states: `authorized` syncs identity successfully, `unauthorized` renders the Access Restricted dialog with the resolved contact text and no raw token, `anonymous` redirects to `/login` without the dialog. Synced R-7 (single mechanism, mode-gated, inert outside local test runs), Item 8, Cost Frame SC-8 entry, and dependency contract. No SC weakened; no scope, requirement, or success-criteria semantics beyond SC-8's own wording changed | Validation findings: 4 FAILs all in SC-8 wording — (1) either/or guard mechanism unresolved, (2) "e.g."/"or" escape-hatch language, (3) atomicity ambiguity (three states read as three deliverables), (4) verification method did not cover the authorized state | AI agent (spec-creation revise task) under `for_pr` authorization scope |

---
🤖 OpenCode (ollama-cloud/glm-5.3-flash) created
🤖 Co-authored with AI: OpenCode (opencode/mimo-v2.6-flash-free)
Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
