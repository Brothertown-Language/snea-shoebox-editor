# Planning: Status Tracking

## 3. Spec Flow Control (Status & Markers)

### STATUS Field Format

Every spec file MUST have a **STATUS** header at the top of the file:

```markdown
# Spec: [Feature Name]

STATUS: 1.1
CREATED: 2026-03-24

---

## Phase 1: [Concern Name] (Gated)
...
```

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**
- ✅ Good: "Database Schema Setup", "API Endpoint Integration", "Error Handling Layer"
- ❌ Bad: "Implementation", "Testing", "Development", "Build"

#### Status Values
| Format | Meaning |
|--------|---------|
| `1` | Phase 1, no specific step tracked |
| `1.2` | Phase 1, step 2 (currently active) |
| `2.1-3` | Phase 2, steps 1-3 in progress |
| `completed` | All phases done, ready for archive |
| `1.1 (REVISED - NEEDS APPROVAL)` | Spec was modified, awaiting fresh approval |

#### Revision Status Format

**When a spec or task is modified, the status MUST change:**

```
STATUS: 1.1
    ↓ (revision made)
STATUS: 1.1 (REVISED - NEEDS APPROVAL)
```

**Mandatory actions on revision:**
1. Add `(REVISED - NEEDS APPROVAL)` suffix to STATUS
2. Add `needs-approval` label to the issue
3. HALT — do NOT proceed with implementation
4. Wait for fresh explicit approval

**Exempt status updates (do NOT revoke approval):**
- STATUS marker updates only (`STATUS: 1.1` → `STATUS: 1.2`)
- Progress comments added to issue
- Bug report additions to existing spec

#### Authorization Received Status Transition

**When authorization is received after a revision, clean up approval markers BEFORE proceeding.**

**The Problem:**
- `needs-approval` label remains on issue after authorization
- `STATUS: N.M (REVISED - NEEDS APPROVAL)` suffix remains in STATUS field
- Stale todo list from interrupted workflow

**The Solution:**
When authorization is received AND workflow was interrupted:

1. **Remove `needs-approval` label** (if present)
2. **Clear STATUS suffix**: `N.M (REVISED - NEEDS APPROVAL)` → `N.M`
3. **Clear todo list** (if workflow was interrupted — see detection below)
4. **Proceed with implementation**

**⚠️ CRITICAL: Cleanup is SILENT — NO comments posted.**

- Authorization cleanup is administrative, not post-implementation review information
- GitHub comments are for implementation results, not status notifications
- The issue state (label, STATUS) IS the record — no duplicate notification needed

**Workflow Interruption Detection:**

| Interruption Type | Detection |
|------------------|-----------|
| Developer conversation | Agent asked clarification question and received answer |
| Spec revision | Agent revised spec (added/changed content) |
| Error recovery | Agent encountered error and investigated |
| Context switch | Agent switched to different task/issue |
| Investigation phase | Agent performed investigation before implementation |

**Action:** If ANY interruption occurred since last authorization, CLEAR the todo list before implementation.

| Edge Case | Action |
|-----------|--------|
| No interruption (immediate auth) | Skip todo clearing (todos still valid) |
| Todo list already empty | Skip todo clearing (no-op) |
| Label already removed | Skip label removal (no-op) |
| STATUS has no suffix | Skip STATUS edit (no-op) |

**Timeline:** Cleanup happens BEFORE implementation begins — not during, not after.

**See Also:**
- `010-approval-gate.md` → "Authorization Cleanup Workflow" section for detailed cleanup rules
- `todowrite` integration for clearing stale todos

### Status Markers (Visual Icons)

| Marker | Meaning | When to Use |
|--------|---------|-------------|
| `☐` | Not started | Task not begun |
| `↻` | In progress | Currently working — **MARK DURING WORK** |
| `☑` | Complete | Task done and verified |
| `☒` | Blocked | Issue found, cannot proceed |

### Phase Risk and Blast Radius Notation

**Each phase SHOULD include risk and blast radius information:**

```markdown
## Phase N: [Concern Name] (Risk: [LOW|MEDIUM|IGH], Blast Radius: [SMALL|MEDIUM|ARGE])

**Interdependencies**: [NONE|Phase M (must exist before this phase)]

**Why this order**: [Explanation]
```

**Risk Levels:**
- **LOW**: Read-only, additive, easily reversible
- **MEDIUM**: Modifies existing code, moderate rollback complexity
- **HIGH**: Breaking changes, hard to rollback, production-critical

**Blast Radius:**
- **SMALL**: Single file/module, unit tests sufficient
- **MEDIUM**: Multiple files, internal dependencies
- **LARGE**: Cross-module, external dependencies

**Example:**
```markdown
## Phase 1: Database Schema (Risk: LOW, Blast Radius: SMALL)

**Interdependencies**: NONE

**Why this order**: Foundation layer with no dependencies.

### Steps
1. ☐ Add user table schema
2. ☐ Create migration script
```

**CRITICAL**: Update to `↻` (in progress) **during** implementation, not just after completion.

#### Example During Implementation
```markdown
### Steps
1. ☑ Add OAuth2 client configuration
2. ↻ Implement token refresh logic (working now)
3. ☐ Update authentication middleware
4. ☐ Add session management
```

### When to Update Status
- **PENDING → `1.1`**: When spec is created (first phase, first step)
- **`N.M` → `N.M+1`**: When step M completes
- **`N.last → N+1.1`**: When last step of phase N completes, move to next phase
- **`N.M` → `completed`**: When final phase completes

### ⚠️ CRITICAL: STATUS Updates Are MINIMAL EDITS ONLY

**Status updates mean editing the STATUS line ONLY — not rewriting the entire issue body.**

When updating status:
1. **Post progress comment** documenting what was completed
2. **Edit STATUS field ONLY** (change `STATUS: 1.1` to `STATUS: 1.2` for example)
3. **Never rewrite the entire body** to change status

See `123-github-ai-identity.md` and `github-comments` skill → "Issue Body Update Rules" section for complete rules.

### Missing Status Header
If a spec file lacks a `STATUS:` header, the agent MUST:
1. Add the header with `STATUS: 1.1` (default for new specs) — MINIMAL EDIT ONLY (add one line)
2. If all tasks are marked `☑`, post completion comment then set `STATUS: completed`

---

## 4. Phases & Step Numbering

### Phase Numbering

Phases are numbered sequentially starting from 1:

```markdown
## Phase 1: [Concern Name] (Gated)
## Phase 2: [Next Concern] (Auto-progress)
## Phase 3: [Verification Concern] (Gated)
```

**⚠️ Phase names must describe specific concerns, not generic activities.**

### Step Numbering

Steps are numbered 1, 2, 3 within each phase:

```markdown
## Phase 1: OAuth2 Client Setup

### Steps
1. ☐ Add OAuth2 client configuration
2. ☐ Implement token refresh logic
3. ☐ Update authentication middleware
```

### Phase Types

| Type | Approval | Keywords |
|------|----------|----------|
| Implementation | Gated | build, implement, code, develop, integrate, create, write, fix, add, update, remove |
| Verification | Auto-progress | test, verify, review, validate, check, ensure, confirm |
| Completion | Auto-archive | complete, done, finish, ship, deploy, release |

---

## 8. Approval Commands

### Phase-Level Approval
- `approved` — Approve entire current phase
- `approved: 1` — Approve phase 1
- `approved: 1-2` — Approve phases 1 and 2

### Step-Level Approval
- `approved: 1.2` — Approve step 2 of phase 1
- `approved: 1.1-3` — Approve steps 1-3 of phase 1

### Final Approval
- `go` — Shortcut for final approval when last phase requires approval

### Revision
- `revise` — Re-analyze and adjust entire plan (no code changes during revision)

---

## 9. Auto-Progression

### Verification Phases Auto-Progress

When a verification phase is reached:
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
2. Close the GitHub Issue

---

*Source: Content migrated from `040-plan-delivery.md`*