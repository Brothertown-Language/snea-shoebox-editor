# Spec Flow Control - Design Discussion

## Goal
Human-approved, flexible phase-based progression for spec files. Investigation and planning phases are auto-completed before spec submission. Only implementation+ phases appear in specs with numbered phases and steps.

**Important:** This is permanent reference documentation for AI agent workflow. It is NOT a plan. Actual spec files are created in `plans/` directory.

---

## Directory Structure

| Location | Purpose |
|----------|---------|
| `docs/specs/*.md` | Permanent reference docs (this file, how-to guides) |
| `plans/` | Actual spec files created during work |
| `plans/completed/` | Approved and finished specs |
| `plans/` | Actual spec files created during work |
| `plans/completed/` | Approved and finished specs |

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
- These appear in the spec with numbered phases/steps

---

## Spec Structure (After Investigation/Planning Complete)

Specs are created AFTER investigation and planning are done. The spec only contains phases requiring approval:

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

## Status Markers (Visual Icons)

| Marker | Meaning | When to use |
|--------|---------|-------------|
| `☐` | Not started | Task not begun |
| `↻` | In progress | Currently working |
| `☑` | Complete | Task done |
| `☒` | Blocked | Issue found |

**Update `↻` during implementation**, not just after completion. Icons convey meaning at a glance.

**Example during implementation:**
```
### Steps
1. ☑ Add OAuth2 client configuration
2. ↻ Implement token refresh logic (working now)
3. ☐ Update authentication middleware
4. ☐ Add session management
```

---

## Phase Numbering

Phases are numbered sequentially starting from 1. Steps are numbered 1, 2, 3 within each phase:

| Phase Number | Type | Approval |
|--------------|------|----------|
| 1 | Implementation | Requires approval |
| 2 | Testing | Auto-progress if pass |
| 3 | Review | Requires approval |

Steps are numbered within phase:
- Phase 1: steps 1, 2, 3, 4
- Phase 2: steps 1, 2, 3
- Phase 3: steps 1, 2, 3

---

## STATUS Field Format

- `1` - Phase 1, no specific step
- `1.2` - Phase 1, step 2
- `completed` - All phases done

---

## Phase Types (For Creating Specs)

When AI creates a spec, it determines phase type by keywords:

**Implementation (requires approval):**
- build, implement, code, develop, integrate, create, write, fix, add, update, remove

**Verification (auto-progress):**
- test, verify, review, validate, check, ensure, confirm

**Completion (auto-archive):**
- complete, done, finish, ship, deploy, release

---

## Revision = Replanning

Revision re-analyzes the entire plan:

1. **Analysis**: Re-examine all phases and steps
2. **Impact assessment**: Which phases/steps are affected
3. **Restructure**: Add, remove, or modify steps as needed
4. **Cascade updates**: Adjust all downstream phases
5. **Renumber**: Ensure phases and steps are sequentially numbered
6. **No code changes during revision**: Only spec updates

**Example revision:**
```
Current STATUS: 1.2
Command: "revise: discovered OAuth2 requires PKCE"

Result:
- Add new step to Phase 1: 5. "Add PKCE challenge generation"
- Modify Phase 2 testing steps to include PKCE scenarios
- Renumber if needed
- STATUS may reset to appropriate point for revision scope
```

---

## Approval Commands

**Phase-level:**
- `approved` - Approve entire current phase
- `approved: 1` - Approve phase 1
- `approved: 1-2` - Approve phases 1 and 2

**Step-level:**
- `approved: 1.2` - Approve step 2 of phase 1
- `approved: 1.1-3` - Approve steps 1-3 of phase 1

**Revision:**
- `revise` - Re-analyze and adjust entire plan

---

## Auto-Progression

### Verification Phases Auto-Progress

When verification phase is reached:
1. Run verification steps automatically
2. If all pass → move to next phase
3. If any fail → replan if needed, stop and report

**On verification failure:**
- Stop at failing step
- Report what failed and why
- Update plan with new steps if needed
- Wait for fix or `revise` command

### Completion Auto-Archive

When spec reaches completion:
1. Verify all steps done (all `☑`)
2. Move spec to `plans/completed/<category>/`

---

## Multiple Specs with Dependencies

Larger projects may have multiple specs:

```markdown
# Spec: User Dashboard

DEPENDS ON:
- spec: user-auth (completed)

STATUS: 1.1
```

Independent specs can run in parallel. Dependent specs block until dependencies complete.

---

## What NOT to Include in Specs

**DO NOT include in specs:**
- Investigation phases (already done)
- Planning phases (already done)
- Research notes (that was investigation)
- Architecture decisions (that was planning)

**These are completed BEFORE spec creation.**

The spec starts AFTER investigation and planning are complete.

---

## Summary of Decisions

1. **Numbered phases**: Phase 1, Phase 2, Phase 3...
2. **Numbered steps**: 1, 2, 3 within each phase
3. **Visual icons**: `☐`/`↻`/`☑`/`☒` (not started/in progress/done/blocked)
4. **Investigation/planning done before spec**: NOT included in spec
5. **Spec contains only approval-required phases**: Implementation, verification, completion
6. **STATUS uses phase.step format**: `1.2` means phase 1, step 2
7. **Real-time status updates**: Mark `↻` during work, not just after
8. **Revision = replanning**: Re-analyze entire workflow, consider downstream impacts
9. **Auto-progress verification**: Tests run automatically, continue if pass
10. **Auto-archive on completion**: Done specs move to completed/