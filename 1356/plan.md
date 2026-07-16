# Implementation Plan — [#1356](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1356) — Retire dev branch: purge all references from docs and guidelines

- **Goal:** Remove all `dev` branch workflow references from documentation after PR #1354 merged `dev` into `main`
- **Architecture:** Three sequential phases — (1) delete retired workflow docs, (2) update remaining references, (3) verification sweep
- **Files:** `docs/git-workflow-migration-guide.md`, `docs/streamlit-dev-workflow.md`, `AGENTS.md`, `docs/security/credential-leakage-remediation.md`
- **Dispatch:** `writing-plans-creation --task create` via `writing-plans` dispatcher

## Blast Radius

| Phase | Affected Components | Impact | Risk |
|-------|-------------------|--------|------|
| 1 | `docs/git-workflow-migration-guide.md`, `docs/streamlit-dev-workflow.md` | Direct deletion | Low |
| 2 | `AGENTS.md` (line 52), `docs/security/credential-leakage-remediation.md` (line 84) | Direct edit | Low |
| 3 | `docs/` directory | Indirect (grep sweep) | Low |

## Concern Map Reference

| Phase | Concern |
|-------|---------|
| 1 — Delete retired workflow docs | Remove documentation describing a workflow that no longer exists |
| 2 — Update doc references | Update remaining doc references from `dev` to `main` |
| 3 — Verification sweep | Verify zero `dev` branch workflow references remain |

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

> **One step at a time:** Execute steps in exact order. When a step completes, pause — do not proceed to the next step until the current step's verification has passed. Each step's RED/GREEN cycle must complete before the next step begins.

> **Step status notation:** `- [ ]` = pending, `- [x]` = completed, `- [~]` = in progress. At every checkpoint, update all step markers to reflect current state.

> **Self-remediation protocol:** When a step fails, do not escalate immediately. Attempt remediation autonomously. Only after verified remediation failure should the agent escalate.

## Phase Table

| # | Name | Concern | SCs | Dependencies | Steps | Dispatch |
|---|------|---------|-----|-------------|-------|----------|
| 1 | Delete retired workflow docs | Remove files describing retired `feature→dev→main` workflow | SC-1, SC-2 | None | 1-8 | `implementation-pipeline` |
| 2 | Update dev→main references | Edit remaining references from `dev` to `main` | SC-3, SC-4 | Phase 1 complete | 9-16 | `implementation-pipeline` |
| 3 | Verification sweep | Verify zero `dev` branch workflow references remain | SC-5 | Phases 1-2 complete | 17-22 | `implementation-pipeline` |
| Common | SC integrity | SC-6 | All phases | 23-26 | `implementation-pipeline` |

## SC-to-Step Traceability

| SC ID | Criterion | Phase | Step(s) |
|-------|-----------|-------|---------|
| SC-1 | `docs/git-workflow-migration-guide.md` deleted | 1 | 2 |
| SC-2 | `docs/streamlit-dev-workflow.md` deleted | 1 | 3 |
| SC-3 | `AGENTS.md` line 52 dev exception removed | 2 | 10 |
| SC-4 | Credential doc line 84 references `origin main` | 2 | 11 |
| SC-5 | No remaining `\`dev\`` branch references in `docs/` | 3 | 18 |
| SC-6 | SC integrity — no weakening/reclassification | Common | 23-26 |

## Feasibility Verification

| Step | Reference | Verified? | Evidence |
|------|-----------|-----------|----------|
| 1.1 | `docs/git-workflow-migration-guide.md` | ✅ | `ls` |
| 1.2 | `docs/streamlit-dev-workflow.md` | ✅ | `ls` |
| 2.1 | `AGENTS.md` line 52 | ✅ | `grep -n 'dev' AGENTS.md` |
| 2.2 | `docs/security/credential-leakage-remediation.md` line 84 | ✅ | `grep -n 'origin dev'` |

## Exit Criteria

- [ ] C1: Plan index stored at `.issues/1356/plan.md`
- [ ] C2: Phase files stored at `.issues/1356/plan-01.md`, `.issues/1356/plan-02.md`, `.issues/1356/plan-03.md`
- [ ] C3: All plan file paths verified via `ls`
- [ ] C4: All referenced skills exist under `.opencode/skills/`
- [ ] C5: Approval cascade applied (`for_pr` scope → auto-approved)
- [ ] C6: Plan reported in chat with `.issues/1356/plan.md` path
- [ ] C7: All SCs trace to at least one plan step
- [ ] C8: No scope creep — all steps trace to at least one SC

## Self-Review Evidence

All file references verified via `ls` and `grep` in the current session. Plan structure derived from spec's Affected Files table and SC-to-Phase mapping.

---

Co-authored with AI: OpenCode (deepseek-v4-flash-free)
