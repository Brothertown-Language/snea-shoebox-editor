# Implementation Plan: Phase 5 — Search Mode UI: Vertical Radio with Grouping

**Spec:** [Issue #1126](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1126)
**Parent:** #400 (Phase 5)
**Authorization Scope:** `for_pr`
**Halt At:** `pr_created`
**PR Strategy:** `stacked`

## Goal

Change the search mode selector from a 2-option horizontal radio to a 4-option vertical radio with Focused/Broad grouping, Headword as the new default, and active mode name in the search results header. Lexeme and FTS modes remain UNCHANGED in behavior — only their UI representation changes.

## Architecture

Single-file change to `src/frontend/pages/records.py`. The backend (`src/services/linguistic_service.py`) already handles all 4 search modes per #1305. No backend changes.

## Tech Stack

- Streamlit (`st.radio`, `st.markdown`, `st.columns`, `st.button`)
- Session state for mode persistence
- `on_change` callback for mode switching

## Affected Files

| File | Responsibility |
|------|---------------|
| `src/frontend/pages/records.py` | Search mode UI: vertical radio, grouping, default change, header update, help text, button reflow |

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

---

## Phase 1: Search Mode UI — Vertical Radio with Grouping

**Concern:** Frontend UI — search mode selector, header, and button layout in `src/frontend/pages/records.py`
**Files:** `src/frontend/pages/records.py`
**SCs covered:** SC-1, SC-2, SC-3, SC-4, SC-5, SC-6, SC-7, SC-8, SC-9, SC-10, SC-11

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "sc-coherence-gate", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "pre-red-baseline", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "red-phase", "issue_number": 1126, "phase": 1}` | SC-1, SC-2, SC-6, SC-8, SC-9 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "red-doublecheck", "issue_number": 1126, "phase": 1}` | SC-1, SC-2, SC-6, SC-8, SC-9 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "post-red-enforcement", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "green-phase", "issue_number": 1126, "phase": 1}` | SC-1, SC-2, SC-6, SC-8, SC-9 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "post-green-enforcement", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-1 through SC-11 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "structural-checks", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "green-doublecheck", "issue_number": 1126, "phase": 1}` | SC-3, SC-4, SC-5, SC-10 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "green-vbc", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "adversarial-audit", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "cross-validate", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "regression-check", "issue_number": 1126, "phase": 1}` | SC-11 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "review-prep", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "exec-summary", "issue_number": 1126, "phase": 1}` | SC-1 through SC-11 |

### Concern Boundary Annotations

- **Leaving:** Current 2-option horizontal radio with inline search/clear buttons at 0.15 column width
- **Entering:** 4-option vertical radio with Focused/Broad grouping, full-width buttons below, mode name in header, help text
- **Handoff:** Session state key `search_mode_radio` and `search_mode` continue to work; `on_mode_change` callback signature unchanged

### Item Decomposition

#### Item 1: Default mode change + session state initialization

**RED condition:** New session initializes `st.session_state.search_mode` to `"Lexeme"` (current default). A test that creates a fresh session state and checks the value finds `"Lexeme"`.

**GREEN condition:** New session initializes `st.session_state.search_mode` to `"Headword"`. A test that creates a fresh session state and checks the value finds `"Headword"`.

**Files:** `src/frontend/pages/records.py` line 58-59

#### Item 2: Vertical radio with 4 options + Focused/Broad grouping

**RED condition:** The radio widget shows 2 horizontal options `["Lexeme", "FTS"]` with no grouping separators. A test rendering the sidebar finds exactly 2 radio options and no markdown separator text.

**GREEN condition:** The radio widget shows 4 vertical options `["Headword", "Gloss", "Lexeme", "FTS"]` with `"── Focused ──"` and `"── Broad ──"` markdown separators. A test rendering the sidebar finds 4 radio options and both separator texts.

**Files:** `src/frontend/pages/records.py` lines 198-218

#### Item 3: Search header shows mode name + count

**RED condition:** Search header shows `"Search (N records)"` with no mode name. A test with a truthy search term finds the header pattern without a mode prefix.

**GREEN condition:** Search header shows `"Search: Headword (N records)"` when Headword mode is active. A test with a truthy search term finds the header pattern with the mode name.

**Files:** `src/frontend/pages/records.py` lines 184-188

#### Item 4: Help text below radio

**RED condition:** No help text exists below the radio widget. A grep for mode-description text finds no match.

**GREEN condition:** Help text `"HW: \\lx+\\va (primary) | Gloss: \\ge (primary) | LX: all markers | FTS: all fields"` renders below the radio group. A grep finds the help text pattern.

**Files:** `src/frontend/pages/records.py` (new section after radio)

#### Item 5: Search/clear buttons reflow to full width below radio

**RED condition:** Search/clear buttons are in `st.columns([0.7, 0.15, 0.15])` alongside the radio. A test finds the column layout with 0.15-width button columns.

**GREEN condition:** Search/clear buttons are full-width below the radio group, not in 0.15-width columns. A test finds buttons rendered outside the narrow column layout.

**Files:** `src/frontend/pages/records.py` lines 199, 210-218

### Per-Unit Pipeline Gate Table

#### Unit 1: Default mode change + session state initialization

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec and plan agree: Headword is new default |
| 2 | pre-red-baseline | Current default is "Lexeme" at line 59 |
| 3 | red-phase | Test written that asserts default is "Headword" — test FAILS |
| 4 | red-doublecheck | RED test confirmed failing against current code |
| 5 | post-red-enforcement | Only test files modified, no src/ changes |
| 6 | green-phase | Change line 59 default to "Headword" — test PASSES |
| 7 | post-green-enforcement | src/ change confirmed (line 59) |
| 8 | checkpoint-commit | Commit made with message including "default: Headword" |
| 9 | structural-checks | `ruff`, `pyright` pass on modified file |
| 10 | green-doublecheck | Semantic intent: default changed to Headword |
| 11 | green-vbc | SC-1 verified PASS |
| 12 | adversarial-audit | Dual auditor confirms SC-1 |
| 13 | cross-validate | Auditors agree on SC-1 |
| 14 | regression-check | All existing tests still pass |
| 15 | review-prep | Diff reviewed, no stale references |
| 16 | exec-summary | Summary reported |

#### Unit 2: Vertical radio with 4 options + Focused/Broad grouping

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec and plan agree: single st.radio with markdown separators |
| 2 | pre-red-baseline | Current radio is horizontal with 2 options at lines 201-209 |
| 3 | red-phase | Test written that asserts 4 options + separators — test FAILS |
| 4 | red-doublecheck | RED test confirmed failing against current code |
| 5 | post-red-enforcement | Only test files modified, no src/ changes |
| 6 | green-phase | Replace lines 198-218 with vertical radio + separators — test PASSES |
| 7 | post-green-enforcement | src/ change confirmed |
| 8 | checkpoint-commit | Commit made with message including "vertical radio" |
| 9 | structural-checks | `ruff`, `pyright` pass on modified file |
| 10 | green-doublecheck | Semantic intent: 4 options visible, separators render |
| 11 | green-vbc | SC-2, SC-8 verified PASS |
| 12 | adversarial-audit | Dual auditor confirms SC-2, SC-8 |
| 13 | cross-validate | Auditors agree on SC-2, SC-8 |
| 14 | regression-check | All existing tests still pass |
| 15 | review-prep | Diff reviewed, no stale references |
| 16 | exec-summary | Summary reported |

#### Unit 3: Search header shows mode name + count

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec and plan agree: header format is `"Search: {mode} (N records)"` |
| 2 | pre-red-baseline | Current header is `"Search (N records)"` at line 184 |
| 3 | red-phase | Test written that asserts mode name in header — test FAILS |
| 4 | red-doublecheck | RED test confirmed failing against current code |
| 5 | post-red-enforcement | Only test files modified, no src/ changes |
| 6 | green-phase | Update line 184 to include mode name — test PASSES |
| 7 | post-green-enforcement | src/ change confirmed |
| 8 | checkpoint-commit | Commit made with message including "header mode name" |
| 9 | structural-checks | `ruff`, `pyright` pass on modified file |
| 10 | green-doublecheck | Semantic intent: header shows mode name when search_term is truthy |
| 11 | green-vbc | SC-6 verified PASS |
| 12 | adversarial-audit | Dual auditor confirms SC-6 |
| 13 | cross-validate | Auditors agree on SC-6 |
| 14 | regression-check | All existing tests still pass |
| 15 | review-prep | Diff reviewed, no stale references |
| 16 | exec-summary | Summary reported |

#### Unit 4: Help text below radio

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec and plan agree: help text describes all 4 modes |
| 2 | pre-red-baseline | No help text exists in the sidebar search section |
| 3 | red-phase | Test written that asserts help text pattern — test FAILS |
| 4 | red-doublecheck | RED test confirmed failing against current code |
| 5 | post-red-enforcement | Only test files modified, no src/ changes |
| 6 | green-phase | Add `st.markdown` with help text below radio — test PASSES |
| 7 | post-green-enforcement | src/ change confirmed |
| 8 | checkpoint-commit | Commit made with message including "help text" |
| 9 | structural-checks | `ruff`, `pyright` pass on modified file |
| 10 | green-doublecheck | Semantic intent: help text visible below radio |
| 11 | green-vbc | SC-7 verified PASS |
| 12 | adversarial-audit | Dual auditor confirms SC-7 |
| 13 | cross-validate | Auditors agree on SC-7 |
| 14 | regression-check | All existing tests still pass |
| 15 | review-prep | Diff reviewed, no stale references |
| 16 | exec-summary | Summary reported |

#### Unit 5: Search/clear buttons reflow to full width below radio

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec and plan agree: buttons below radio, not in 0.15 columns |
| 2 | pre-red-baseline | Current buttons in `st.columns([0.7, 0.15, 0.15])` at lines 199-218 |
| 3 | red-phase | Test written that asserts buttons are full-width — test FAILS |
| 4 | red-doublecheck | RED test confirmed failing against current code |
| 5 | post-red-enforcement | Only test files modified, no src/ changes |
| 6 | green-phase | Remove column layout, render buttons full-width below radio — test PASSES |
| 7 | post-green-enforcement | src/ change confirmed |
| 8 | checkpoint-commit | Commit made with message including "button reflow" |
| 9 | structural-checks | `ruff`, `pyright` pass on modified file |
| 10 | green-doublecheck | Semantic intent: buttons full width, not in 0.15 columns |
| 11 | green-vbc | SC-9 verified PASS |
| 12 | adversarial-audit | Dual auditor confirms SC-9 |
| 13 | cross-validate | Auditors agree on SC-9 |
| 14 | regression-check | All existing tests still pass |
| 15 | review-prep | Diff reviewed, no stale references |
| 16 | exec-summary | Summary reported |

### Inter-Phase Handoff

N/A — single phase.

### Post-All-Phases Sweep

- [ ] FINISHING CHECKLIST — orchestrator routes to finishing sub-agent: git status clean, lint/typecheck from scratch, coverage sweep
- [ ] PR CREATION — orchestrator routes to `git-workflow pr-creation`: via `github_create_pull_request`, extract `html_url` from response
- [ ] POST-MERGE CLEANUP — orchestrator routes to `git-workflow cleanup`: delete merged branches, close issues, sync dev

---

## Implementation Checklist

### Pre-Flight

- [ ] Verify spec-to-plan handoff: spec #1126 is approved (`approved-for-pr` label present)
- [ ] Verify pipeline-readiness: no `sc-pipeline-readiness.yaml` exists — spec is single-file, single-concern, proceed
- [ ] Create feature branch from `dev`
- [ ] Verify `authorization_scope: for_pr` — plan auto-approved per approval cascade matrix

### Phase 1 Execution

- [ ] G1: Run sc-coherence-gate — verify spec/plan coherence
- [ ] G2: Run pre-red-baseline — verify current source state
- [ ] G3: Run red-phase — write failing tests for Items 1-5
- [ ] G4: Run red-doublecheck — confirm RED tests fail
- [ ] G5: Run post-red-enforcement — verify only test/ modified
- [ ] G6: Run green-phase — implement Items 1-5
- [ ] G7: Run post-green-enforcement — verify src/ modified
- [ ] G8: Checkpoint commit
- [ ] G9: Run structural-checks — lint, typecheck, format
- [ ] G10: Run green-doublecheck — semantic verification
- [ ] G11: Run green-vbc — verification before completion
- [ ] G12: Run adversarial-audit — dual auditor
- [ ] G13: Run cross-validate — auditor consensus
- [ ] G14: Run regression-check — all existing tests pass
- [ ] G15: Run review-prep — prepare for PR
- [ ] G16: Run exec-summary — push, comment, report

### Post-Phase

- [ ] Finishing checklist: git status clean, lint/typecheck from scratch, coverage sweep
- [ ] PR creation: via `github_create_pull_request`, extract `html_url`
- [ ] Report in chat with plan path and PR URL

---

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

## Exit Criteria

- [ ] Plan stored at `.issues/1126/plan.md`
- [ ] All 11 SCs from spec #1126 covered
- [ ] 5 items decomposed with dependency ordering
- [ ] Each item has RED/GREEN conditions
- [ ] Dispatch table uses 16-gate format from implementation-pipeline
- [ ] No TBD/TODO placeholders
- [ ] Approval cascade: `for_pr` scope → auto-approved
