# Issue #400 Comments

*Auto-synced from GitHub. Last sync: 2026-06-13*

---

## Comment 1 — TDD Compliance Revision v1.1→v1.2 (2026-04-24)

## TDD Compliance Revision (v1.1 → v1.2)

**STATUS** updated to `1.2 (REVISED - NEEDS APPROVAL)` — spec revision revokes prior approval.

### Changes

1. **Per-phase TDD RED/GREEN cycle tables** added to all 6 phases with explicit RED→GREEN→REFACTOR→COMMIT step markers
2. **Success Criteria numbered** as SC-1 through SC-14, each mapped to a specific test function with `# SC-N:` comment markers
3. **Phase 1 TDD Gap acknowledged** — Phase 1 was already completed without prior RED tests (GREEN-without-RED violation). RED tests marked as "Retrospective" (☑ Retrospective). Future phases MUST follow RED→GREEN order.
4. **Phase step order reversed for Phases 2–6** — RED test writing now precedes GREEN implementation per `091-incremental-build.md`
5. **New integration test file** specified: `tests/integration/test_search_modes_e2e.py` for Phase 6
6. **Test files identified** per phase: `tests/database/test_migration_manager.py` (Phase 1, 3), `tests/services/test_upload_service.py` (Phase 2), `tests/services/test_linguistic_service.py` (Phase 4), `tests/frontend/test_records_ui.py` (Phase 5), `tests/integration/test_search_modes_e2e.py` (Phase 6)

---

## Comment 2 — Adversarial Spec Audit (2026-05-09)

## Adversarial Spec Audit — Pre-Implementation Check

**Audit Type:** spec-audit  
**Audit Phase:** spec_creation (pre-implementation)  
**Orchestrator Model:** ollama-cloud/glm-5.1 (family: glm — excluded)  
**Auditor 1:** auditor-deepseek-flash (family: deepseek)  
**Auditor 2:** auditor-mistral-large (family: mistral)  

### Overall Consensus: **FAIL** (7/10 criteria passed, 3 failed)

| Criterion | Description | Auditor 1 (deepseek) | Auditor 2 (mistral) | Consensus | Agreement? |
|---|---|---|---|---|---|
| SC-1 | Problem statement present | PASS | PASS | **PASS** | Yes |
| SC-2 | Success criteria measurable | PASS | FAIL | **FAIL** | No |
| SC-3 | Phases well-structured | PASS | PASS | **PASS** | Yes |
| SC-4 | Steps actionable | PASS | PASS | **PASS** | Yes |
| SC-5 | Dependencies identified | PASS | PASS | **PASS** | Yes |
| SC-6 | Concerns separated | PASS | PASS | **PASS** | Yes |
| SC-7 | Edge cases covered | PASS | PASS | **PASS** | Yes |
| SC-8 | Risk assessment present | PASS | PASS | **PASS** | Yes |
| SC-9 | TDD compliance | PASS | FAIL | **FAIL** | No |
| SC-10 | Prose structure valid | PASS | FAIL | **FAIL** | No |

### Key Findings

1. **SPEC_AMBIGUOUS — SC-2**: Success criteria list measurable test function names that don't yet exist (pre-implementation spec — tests are intended to be written during RED phases)
2. **SPEC_OVERSPECIFIED — SC-9**: Phase 1 "☑ Retrospective" markers claim tests exist that are absent from the codebase
3. **SPEC_AMBIGUOUS — SC-10**: Prose asserts test function existence that's not yet true — future tense recommended

### Executive Summary

**Spec #400 pre-implementation audit: 7/10 criteria passed. Consensus: FAIL.** Three failures all stem from a single root cause: the spec presents planned (not-yet-implemented) test functions as though they exist. Recommended: clarify that SC-2/SC-9/SC-10 are *prospective* — use future tense and "Status: Planned" column.
