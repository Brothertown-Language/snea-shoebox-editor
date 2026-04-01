# Spec Flow Control

## Goal
Human-approved, phase-based progression for spec files. Investigation and planning phases are auto-completed before spec submission. Only implementation+ phases appear in specs with numbered phases and steps.

**Important:** This document (`docs/specs/spec-flow-control*.md`) is permanent reference documentation that governs how AI agents create and manage plans. It is NOT a plan itself. Actual plans/specs are created in `plans/` directory.

---

## Directory Structure & Tooling

| Context | Spec Location | Status Tracking | Archive |
|---------|---------------|-----------------|---------|
| **GitHub MCP Available** | GitHub Issues & Projects | Project Columns + Sub-issues | `plans/completed/` (MD) |
| **MCP Unavailable** | `plans/*.md` | Local file STATUS markers | `plans/completed/` (Move) |

**Important:** When GitHub MCP tools are available, the **GitHub Project Board** and **Issues** are the authoritative spec. Local `plans/` files are used only when MCP tools are unavailable.

---

## Two Workflow Stages

**Stage 1: Auto-Completed (Before Spec Submission)**
- Investigation phases - research, analysis, exploration
- Planning phases - design, architecture, breakdown
- These are DONE before the spec is created
- NOT included in the final spec

**Stage 2: Requires Human Approval (In Spec)**
- Implementation phases - build, code, integrate
- Verification phases - test, review, validate
- Completion phases - ship, deploy, release
- These appear in the spec with numbered phases/steps

---

## Spec Structure

Specs are created AFTER investigation and planning. Only phases requiring approval:

```markdown
# Spec: Fix User Authentication

STATUS: 1.1
CREATED: 2026-03-23

---

## Phase 1: Implementation (requires approval)

### Steps
1. ☐ Add OAuth2 client configuration
2. ☐ Implement token refresh logic
3. ☐ Update authentication middleware
4. ☐ Add session management

### Content
OAuth2 flow will use client credentials grant. Tokens cached in Redis with 1-hour TTL.

---

## Phase 2: Integration Testing (auto-progress)

### Steps
1. ☐ Run unit tests for auth module
2. ☐ Run integration tests for OAuth flow
3. ☐ Validate token refresh scenarios

---

## Phase 3: Final Review (requires approval)

### Steps
1. ☐ Security review
2. ☐ Performance validation
3. ☐ Documentation update

---

## Approval Log
| Date | Phase | Command | Notes |
|------|-------|---------|-------|
```

---

## Status Mapping (Project-First Strategy)

When GitHub MCP tools are available, Spec phases map to Project columns:
- `Specify` — Initial vision (Issue #... [SPEC])
- `Plan` — Technical architecture (Issue #... [SPEC])
- `Tasks` — Breakdown into sub-issues (Issue #... [Task])
- `Implement` — Active coding (Status header `N.M`)
- `Verify` — Integration/Verification phase
- `Done` — Merged and archived

---

## Phase Numbering

Phases: 1, 2, 3...
Steps: 1, 2, 3 within each phase

| Phase | Type | Approval |
|-------|------|----------|
| 1 | Implementation | Requires approval |
| 2 | Verification | Auto-progress |
| 3 | Review | Requires approval |

---

## STATUS Field

- `1` - Phase 1
- `1.2` - Phase 1, step 2
- `completed` - Done

---

## Phase Types

**Implementation (requires approval):**
- build, implement, code, develop, integrate, create, write, fix, add, update, remove

**Verification (auto-progress):**
- test, verify, review, validate, check, ensure, confirm

**Completion (auto-archive):**
- complete, done, finish, ship, deploy, release

---

## Approval Commands

- `approved` - Approve current phase
- `approved: 1` - Approve phase 1
- `approved: 1.2` - Approve step 2 of phase 1
- `go` - Shortcut for final approval (when last phase requires approval)

---

## Completion Flow (on "go" or final approval)

**When final phase is approved:**
1. Update STATUS to `completed`
2. Mark ALL steps as `☑`
3. Add COMPLETED date field
4. Add implementation notes (key changes, results)
5. Move spec to `plans/completed/<category>/`
6. Delete original from `plans/`

**Example completed spec header:**
```markdown
# Spec: Fix User Authentication

STATUS: completed
CREATED: 2026-03-23
REVISED: 2026-03-24
COMPLETED: 2026-03-24
```

**Category subdirectories:**
- `plans/completed/interlinear/` - interlinear alignment specs
- `plans/completed/planning/` - planning tool specs
- `plans/completed/reports/` - report generation specs
- etc.

---

## Revision = Replanning

1. Re-examine all phases/steps
2. Add/remove/modify steps
3. Cascade to downstream phases
4. Renumber if needed
5. No code changes - spec only

---

## What NOT in Specs

- Investigation phases (already done)
- Planning phases (already done)

Spec starts AFTER investigation/planning complete.

---

## Auto-Progression

**Verification phases:**
1. Run steps automatically
2. If pass → next phase
3. If fail → replan, stop, report

**Completion:**
1. Verify all done (all `☑`)
2. Move to `plans/completed/`

---

## Summary

1. **Numbered phases/steps**: Phase 1, steps numbered 1, 2, 3...
2. **Visual icons**: `☐`/`↻`/`☑`/`☒` (not started/in progress/done/blocked)
3. **Investigation/planning done before spec**: NOT in spec
4. **Spec has only approval-needed phases**
5. **STATUS: phase.step format**: `1.2` = phase 1, step 2
6. **Real-time `↻` updates** during implementation
7. **Revision = replan entire workflow**