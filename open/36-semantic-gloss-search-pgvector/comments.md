# Issue #36 Comments

*Auto-synced from GitHub. Last sync: 2026-06-13*

---

## Comment 1 — Concern Separation Audit (2026-04-01)

## Summary
- Issues Found: 1
- Issues Fixed: 1
- Issues Skipped: 0

## Changes Applied

**Phase Structure Refactor:**
- Split numbered implementation sections (1-6) into concern-separated phases
- Phase 1: Database Schema Setup (HIGH risk) - migration, extension, indexes
- Phase 2: Core Services Implementation (MEDIUM risk) - embedding service, search functions
- Phase 3: UI Integration (LOW risk) - radio buttons, search modes

## Separation Improvement

**Blast Radius:** Each phase now has bounded blast radius:
- Phase 1 (Schema): HIGH risk, rollback requires migration revert
- Phase 2 (Services): MEDIUM risk, service changes can be reverted independently
- Phase 3 (UI): LOW risk, frontend changes easily rolled back

**Deployment Independence:**
- Schema changes isolated from UI changes
- Services can be deployed after schema is ready
- UI can be deployed after services are ready

**Risk Isolation:**
- HIGH risk (schema) separated from LOW risk (UI)
- Clear dependency chain: DB → Services → UI

## Phase Structure Assessment
- Concern separation: PASS - HIGH risk schema isolated from LOW risk UI
- Dependency flow: PASS - clear dependency chain (DB → Services → UI)
- Grouping quality: PASS - single group with logical ordering
- Risk distribution: PASS - risks isolated by phase (HIGH, MEDIUM, LOW)

---
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Concern Separation Audit

---

## Comment 2 — Audit Complete (2026-04-01)

## Summary
- Issues Found: 1 (Missing Edge Cases)
- Issues Fixed: 1
- Issues Skipped: 0

## Fresh-Start Context Compliance
- **Inline context**: PASS - All context stated inline without "see above" references
- **File references**: PASS - Exact file paths with code snippets included
- **Cross-reference quality**: PASS - Issue #23 and #14 referenced with summaries

## Six-Area Coverage
- **Commands**: PASS - `uv sync`, migration commands, test commands specified
- **Testing**: PASS - Unit tests for embedding service and semantic search
- **Project Structure**: PASS - Files affected table with exact locations
- **Code Style**: PASS - Code examples use project conventions
- **Git Workflow**: PASS - Git LFS consideration documented
- **Boundaries**: PASS - Clear scope boundaries defined

## Content Quality
- **STATUS**: PASS - `STATUS: 1.1` present
- **CREATED**: PASS - `CREATED: 2026-03-29` present
- **Phases**: PASS - 3 phases with concern separation
- **Success criteria**: PASS - 8 testable criteria with expected results
- **Edge cases**: PASS (after fix) - 8 scenarios documented
- **Dependencies**: PASS - Packages with versions and purposes

## Verification Signal
changed — Added Edge Cases section and concern-separated phases

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)

---

## Comment 3 — TDD Revision v1.2 (2026-04-24)

## TDD Compliance Revision (v1.1 → v1.2)

**STATUS** updated to `1.2 (REVISED - NEEDS APPROVAL)` — spec revision revokes prior approval.

### Changes

1. **Per-phase TDD RED/GREEN cycle tables** added to all 3 phases with explicit RED→GREEN→REFACTOR→COMMIT step markers
2. **Success Criteria numbered** as SC-1 through SC-10, each mapped to a specific test function with `# SC-N:` comment markers
3. **Phase step order reversed** — RED test writing (steps 1.x) now precedes GREEN implementation (steps 2.x) per `091-incremental-build.md` per-item TDD discipline
4. **SC mapping table** replaces the unnumbered Success Criteria table for traceability
5. **Enforcement test references** — each RED step specifies the exact test file and function name
6. **Integration with #400** noted (updated reference from #23 to #400)

### TDD Compliance Summary

| Phase | RED Tests (before impl) | GREEN Tests (after impl) | RED→GREEN Order |
|-------|------------------------|------------------------|-----------------|
| Phase 1: Schema | 4 tests (SC-9, SC-10, ivfflat, entry_type) | Migration + model changes | ✅ RED first |
| Phase 2: Services | 9 tests (SC-1–SC-8, embed_batch) | Service + search functions | ✅ RED first |
| Phase 3: UI | 2 tests (radio buttons) | UI integration | ✅ RED first |

🤖 OpenCode (ollama-cloud/glm-5) 📝 TDD Revision
