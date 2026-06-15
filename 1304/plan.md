# Plan: Phase 2 — Backend Indexing Logic

**Issue:** [#1304](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1304)
**Parent:** [#400](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400) — Add Headword and Gloss Search Modes
**Goal:** Populate `HeadwordSearchEntry` and `GlossSearchEntry` tables during record processing, using `in_headword_block` state tracking to identify PRIMARY entries and exclude nested/subentry fields.
**Architecture:** MDF parser → parsed record → `populate_search_entries()` in `UploadService` → 3 search entry tables (SearchEntry, HeadwordSearchEntry, GlossSearchEntry)
**Tech Stack:** Python 3.12+, SQLAlchemy ORM, PostgreSQL, pytest

---

## Phase 1: Parser — Expose Headword-Block State for `\va` Values

**Concern (entering):** MDF parser output — the parsed record must distinguish PRIMARY `\va` values (in headword block) from nested `\va` values (in subentries). Currently `_process_block_into_record()` collects ALL `\va` values into a flat list with no headword-block distinction.

**Concern (leaving):** Parser internals — `in_headword` tracking exists for language `is_primary` but is not exposed for `\va` values.

**Handoff to Phase 2:** Parsed record gains a `primary_va: list[str]` field containing only `\va` values that appear before the first structural branching tag (`\se`, `\sn`, `\va`, `\xv`). Phase 2 reads `primary_va` instead of `va` for HeadwordSearchEntry population.

**Files affected:** `src/mdf/parser.py`
**SCs covered:** SC-P1-1, SC-P1-2 (Phase 1-specific SCs; Phase 2 SCs SC-3/SC-5/SC-23/SC-26 verified in Phase 2)

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "execute sc-coherence-gate from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "execute pre-red-baseline from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "execute red-phase from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "execute red-doublecheck from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-red-enforcement from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "execute green-phase from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-green-enforcement from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-P1-1, SC-P1-2 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "execute structural-checks from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "execute green-doublecheck from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "execute green-vbc from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "execute adversarial-audit from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "execute cross-validate from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "execute regression-check from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "execute review-prep from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "execute exec-summary from implementation-pipeline", "issue_number": 1304, "phase": 1}` | SC-P1-1, SC-P1-2 |

### Per-Unit Pipeline Gate Table

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec/plan coherence verified — parser change scope matches spec intent |
| 2 | pre-red-baseline | Source currency documented; SC-ID cross-ref traceability established |
| 3 | red-phase | Test verifies `_process_block_into_record()` returns `primary_va` with only headword-block `\va` values; test FAILS because field does not exist yet |
| 4 | red-doublecheck | RED-side SC evidence collected — test output shows expected failure |
| 5 | post-red-enforcement | `git diff --name-only -- src/` shows zero src/ changes |
| 6 | green-phase | `_process_block_into_record()` populates `primary_va` with headword-block `\va` values only; existing `va` list unchanged; all existing tests pass |
| 7 | post-green-enforcement | `git diff --name-only -- test/` shows test file changes exist |
| 8 | checkpoint-commit | Phase 1 changes committed with descriptive message |
| 9 | structural-checks | `ruff check --fix`, `ruff format`, `pyright` all pass on `src/mdf/parser.py` and test files |
| 10 | green-doublecheck | Semantic-intent verification: parser correctly distinguishes headword `\va` from nested `\va` |
| 11 | green-vbc | All Phase 1 SCs (SC-P1-1, SC-P1-2) verified before completion |
| 12 | adversarial-audit | Dual-auditor PASS on parser changes |
| 13 | cross-validate | Consensus PASS between auditors |
| 14 | regression-check | All existing tests pass; no regression in parser behavior |
| 15 | review-prep | PR diff reviewed; compare URL generated |
| 16 | exec-summary | Push complete; issue comment posted |

### TDD Steps

#### Item 1.1: Add `primary_va` field to parsed record

**RED condition:** `_process_block_into_record()` returns a record dict without a `primary_va` key when called with MDF containing both headword and nested `\va` values. A test asserting `"primary_va" in record` FAILS.

**GREEN condition:** `_process_block_into_record()` returns a record dict with `primary_va: list[str]` containing only `\va` values that appear before the first structural branching tag (`\se`, `\sn`, `\va`, `\xv`). The test asserting `"primary_va" in record` PASSES.

**Implementation:**
- In `_process_block_into_record()` in `src/mdf/parser.py`, add `"primary_va": []` to the initial record dict (line ~57)
- In the first pass (lines 60-69), before `in_headword = False` is set, append `\va` values to `primary_va` when `in_headword` is still `True`
- The existing `va` list (lines 98-101) remains unchanged — it collects ALL `\va` values

**Test file:** `test/test_parser_headword_block.py`

#### Item 1.2: Verify existing parser behavior is unchanged

**RED condition:** A test asserting that `va` list still contains ALL `\va` values (both headword and nested) FAILS because the test doesn't exist yet.

**GREEN condition:** The test PASSES — `va` list is unchanged, `primary_va` is a subset.

---

## Phase 2: Upload Service — Use Headword-Block State for Search Entry Population

**Concern (entering):** `populate_search_entries()` in `UploadService` — must use `primary_va` from parser for HeadwordSearchEntry, and must use `in_headword_block` state for GlossSearchEntry (first PRIMARY `\ge` only).

**Concern (leaving):** Parser output consumed — Phase 1's `primary_va` field is the data source.

**Handoff from Phase 1:** Parsed record now has `primary_va: list[str]` for headword-block `\va` values.

**Files affected:** `src/services/upload_service.py`
**SCs covered:** SC-3, SC-5, SC-23, SC-26

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "execute sc-coherence-gate from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "execute pre-red-baseline from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "execute red-phase from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "execute red-doublecheck from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-red-enforcement from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "execute green-phase from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-green-enforcement from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-3, SC-5, SC-23, SC-26 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "execute structural-checks from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "execute green-doublecheck from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "execute green-vbc from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "execute adversarial-audit from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "execute cross-validate from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "execute regression-check from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "execute review-prep from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "execute exec-summary from implementation-pipeline", "issue_number": 1304, "phase": 2}` | SC-3, SC-5, SC-23, SC-26 |

### Per-Unit Pipeline Gate Table

| Gate | Name | Exit Criterion |
|------|------|----------------|
| 1 | sc-coherence-gate | Spec/plan coherence verified — upload service changes match spec intent |
| 2 | pre-red-baseline | Source currency documented; SC-ID cross-ref traceability established |
| 3 | red-phase | Behavioral tests for SC-3, SC-5, SC-23, SC-26 FAIL because code change does not exist yet |
| 4 | red-doublecheck | RED-side SC evidence collected — test output shows expected failures |
| 5 | post-red-enforcement | `git diff --name-only -- src/` shows zero src/ changes |
| 6 | green-phase | `populate_search_entries()` uses `primary_va` for HeadwordSearchEntry, uses `in_headword_block` state for GlossSearchEntry (first PRIMARY `\ge` only); all behavioral tests PASS |
| 7 | post-green-enforcement | `git diff --name-only -- test/` shows test file changes exist |
| 8 | checkpoint-commit | Phase 2 changes committed with descriptive message |
| 9 | structural-checks | `ruff check --fix`, `ruff format`, `pyright` all pass on `src/services/upload_service.py` and test files |
| 10 | green-doublecheck | Semantic-intent verification: HeadwordSearchEntry excludes nested `\va`; GlossSearchEntry indexes only first `\ge` at headword level; records missing `\lx` excluded |
| 11 | green-vbc | All SCs (SC-3, SC-5, SC-23, SC-26) verified before completion |
| 12 | adversarial-audit | Dual-auditor PASS on upload service changes |
| 13 | cross-validate | Consensus PASS between auditors |
| 14 | regression-check | All existing tests pass; `SearchEntry` population unchanged |
| 15 | review-prep | PR diff reviewed; compare URL generated |
| 16 | exec-summary | Push complete; issue comment posted |

### TDD Steps

#### Item 2.1: Use `primary_va` for HeadwordSearchEntry `\va` population

**RED condition:** A record with both headword `\va` ("wampu-") and nested `\va` ("wampum") has both values in `HeadwordSearchEntry`. Searching headword for "wampu-" returns the record (SC-3 violation). The behavioral test FAILS.

**GREEN condition:** `populate_search_entries()` iterates `entry.get("primary_va", [])` instead of `entry.get("va", [])` for HeadwordSearchEntry `\va` entries (line ~1804). Searching headword for "wampu-" returns 0 records. The behavioral test PASSES.

**Implementation:**
- In `populate_search_entries()` at line 1804, change `for val in entry.get("va", []):` to `for val in entry.get("primary_va", []):`

#### Item 2.2: Use `in_headword_block` state for GlossSearchEntry (first PRIMARY `\ge` only)

**RED condition:** A record with both headword `\ge` ("ball") and nested `\ge` ("sphere") has both values in `GlossSearchEntry`. Searching gloss for "ball" returns the record but also returns it for "sphere" (SC-5, SC-23 violations). The behavioral test FAILS.

**GREEN condition:** `populate_search_entries()` tracks `in_headword_block` state during MDF line scanning and only populates `GlossSearchEntry` with the first `\ge` value that appears while `in_headword_block` is `True`. Searching gloss for "ball" returns the record; searching for "sphere" returns 0 records. The behavioral test PASSES.

**Implementation:**
- In `populate_search_entries()`, after parsing MDF, scan the raw MDF lines to determine `in_headword_block` state
- Only populate `GlossSearchEntry` with the first `\ge` value found while `in_headword_block` is `True`
- The existing `entry.get("ge")` logic (line 1811) already captures only the first `\ge` — the change is to gate it behind `in_headword_block` state

#### Item 2.3: Skip records missing `\lx` for HeadwordSearchEntry

**RED condition:** A record without `\lx` still gets a `HeadwordSearchEntry` created (SC-26 violation). The behavioral test FAILS.

**GREEN condition:** `populate_search_entries()` skips `HeadwordSearchEntry` creation when `entry.get("lx")` is falsy. The behavioral test PASSES.

**Implementation:**
- The existing code at line 1799 already guards `if entry.get("lx"):` — verify this is correct and add a test for it

#### Item 2.4: Verify `SearchEntry` population is unchanged

**RED condition:** A test asserting that `SearchEntry` still contains ALL `\lx`, `\va`, `\se`, `\cf`, `\ve` values (including nested ones) FAILS because the test doesn't exist yet.

**GREEN condition:** The test PASSES — `SearchEntry` population is identical to pre-change behavior.

---

## Post-All-Phases Sweep

- [ ] FINISHING CHECKLIST — orchestrator routes to finishing sub-agent: `git status` clean, lint/typecheck from scratch, coverage sweep
- [ ] PR CREATION — orchestrator routes to `git-workflow` pr-creation: via `github_create_pull_request`, extract `html_url` from response
- [ ] POST-MERGE CLEANUP — orchestrator routes to `git-workflow` cleanup: delete merged branches, close issues, sync dev
