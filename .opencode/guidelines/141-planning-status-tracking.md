# Planning: Status Tracking

## 3. Spec Flow Control (Status & Markers)

### STATUS Field Format

Every spec file SHOULD have a **STATUS** indicator at the top. The format varies by spec complexity:

**For multi-phase specs (prose-driven format — recommended):**

```markdown
# Spec: [Feature Name]

STATUS: in progress — Authorization Gate, Step 1
CREATED: 2026-03-24

---

## Phase 1: Authorization Gate (Gated)
...
```

**For simple single-task specs (acceptable format):**

```markdown
# Spec: [Bug Description]

STATUS: in progress

---

## Fix Approach
...
```

**STATUS values:**

| Format | Meaning |
| -- | -- |
| `in progress — {concern}, Step {N}` | Working on a specific step within a concern (prose-driven, recommended) |
| `completed — {concern}` | Phase/concern done (prose-driven, recommended) |
| `{concern} — {task description}` | Active task within a concern (prose-driven, recommended) |
| `1` | Phase 1, no specific step tracked (numeric, backward-compatible) |
| `1.2` | Phase 1, step 2 (numeric, backward-compatible) |
| `2.1-3` | Phase 2, steps 1-3 in progress (numeric, backward-compatible) |
| `in progress` | Simple spec — currently being worked on |
| `complete` | Simple spec — all work done |
| `completed` | All phases done, ready for archive |
| `1.1 (REVISED - NEEDS APPROVAL)` | Spec was modified, awaiting fresh approval |
| `in progress — {concern} (REVISED - NEEDS APPROVAL)` | Prose-driven revision marker |

**Backward compatibility:** The numeric `X.Y` format (e.g., `1.2`, `2.1-3`) is still recognized by all tools and skills, but is no longer recommended. New specs should use prose-driven STATUS formats that reference concern names rather than numeric phase indices. This makes STATUS markers self-explanatory and resilient to phase renumbering.

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**

- ✅ Good: "Database Schema Setup", "API Endpoint Integration", "Error Handling Layer"
- ❌ Bad: "Implementation", "Testing", "Development", "Build"

#### Revision Status Format

**When a spec or task is modified, the status MUST change:**

```
STATUS: in progress — Authorization Gate, Step 1
    ↓ (revision made)
STATUS: in progress — Authorization Gate, Step 1 (REVISED - NEEDS APPROVAL)
```

**Numeric revision format (backward-compatible):**

```
STATUS: 1.1
    ↓ (revision made)
STATUS: 1.1 (REVISED - NEEDS APPROVAL)
```

**Mandatory actions on revision:**

1. Add `(REVISED - NEEDS APPROVAL)` suffix to STATUS
2. Add `needs-approval` label to the issue
3. Post chat output with exec summary + spec URL + byline (per `github-comments` skill → Spec Revision Chat Output)
4. HALT — do NOT proceed with implementation
5. Wait for fresh explicit approval

**Exempt status updates (do NOT revoke approval):**

- STATUS marker updates only (`STATUS: in progress — Auth, Step 1` → `STATUS: in progress — Auth, Step 2`, or `STATUS: 1.1` → `STATUS: 1.2`)
- Bug report additions to existing spec

### Status Markers (Visual Icons)

| Marker | Meaning | When to Use |
| -- | -- | -- |
| `☐` | Not started | Task not begun |
| `↻` | In progress | Currently working — **MARK DURING WORK** |
| `☑` | Complete | Task done and verified |
| `☒` | Blocked | Issue found, cannot proceed |

Status markers (`☐`/`↻`/`☑`/`☒`) are recommended for tracking step completion. Any clear progress indicator works — the intent is visibility, not a specific format.

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

- **PENDING → `in progress — {concern}, Step 1`**: When spec is created (or `1.1` for backward compatibility)
- **Step completion**: `in progress — {concern}, Step N` → `in progress — {concern}, Step N+1`
- **Concern completion**: `in progress — {concern}, Step N` → `completed — {concern}` → `in progress — {next concern}, Step 1`
- **Final completion**: Last concern → `completed`

**Numeric transitions (backward-compatible):**

- **PENDING → `1.1`**: When spec is created (first phase, first step)
- **`N.M` → `N.M+1`**: When step M completes
- **`N.last → N+1.1`**: When last step of phase N completes, move to next phase
- **`N.M` → `completed`**: When final phase completes

### ⚠️ CRITICAL: STATUS Updates Are MINIMAL EDITS ONLY

**Status updates mean editing the STATUS line ONLY — not rewriting the entire issue body.**

When updating status:

1. **Report progress to chat** documenting what was completed
2. **Edit STATUS field ONLY** (change `STATUS: in progress — {concern}, Step N` or `STATUS: 1.1` for backward compatibility)
3. **Never rewrite the entire body** to change status

See `123-github-ai-identity.md` and `github-comments` skill → "Issue Body Update Rules" section for complete rules.

### Missing Status Header

If a spec file lacks a `STATUS:` header, the agent MUST:

1. Add the header with prose-driven STATUS (e.g., `STATUS: in progress — {concern}, Step 1`) — MINIMAL EDIT ONLY (add one line). For backward compatibility, `STATUS: 1.1` is also acceptable.
2. If all tasks are marked `☑`, set `STATUS: completed`

______________________________________________________________________

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
| -- | -- | -- |
| Implementation | Gated | build, implement, code, develop, integrate, create, write, fix, add, update, remove |
| Verification | Auto-progress | test, verify, review, validate, check, ensure, confirm |
| Completion | Auto-archive | complete, done, finish, ship, deploy, release |

______________________________________________________________________

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

______________________________________________________________________

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

______________________________________________________________________

## 10. Label State Transitions

### Label Categories

| Category | Labels | Purpose |
| -- | -- | -- |
| **Core Workflow** | `needs-approval`, `needs-revision`, `in-progress` | Track issue lifecycle position |
| **Categorization** | `bug`, `enhancement`, `architecture`, `spec`, `plan` | Classify issue type |
| **Resolution** | `wontfix`, `duplicate`, `question` | Mark final disposition |

### Core Workflow Labels

| Label | Meaning | When Applied | When Removed |
| -- | -- | -- | -- |
| `needs-approval` | Awaiting explicit authorization to implement | Issue/spec created or spec revised | Explicit approval received (`approved`/`go`) |
| `needs-revision` | Spec requires changes before approval | Spec audit findings, reviewer feedback | Revised spec re-submitted and awaiting approval (replace with `needs-approval`) |
| `in-progress` | Currently being implemented | Authorization verified and implementation started | Implementation complete (PR created) or blocked |

### Full Transition Matrix

| From State | Trigger | To State | Label Actions |
| -- | -- | -- | -- |
| (new) | Issue created | `needs-approval` | **ADD** `needs-approval` |
| `needs-approval` | User says `approved`/`go` | (implementation) | **REMOVE** `needs-approval`, **ADD** `in-progress` if starting work |
| `needs-approval` | Spec audit requires changes | `needs-revision` | **REMOVE** `needs-approval`, **ADD** `needs-revision` |
| `needs-approval` | Already implemented (autoclose) | (closed) | **REMOVE** `needs-approval` |
| `needs-revision` | Revised spec re-submitted | `needs-approval` | **REMOVE** `needs-revision`, **ADD** `needs-approval` |
| `needs-revision` | Spec withdrawn/duplicate | (closed) | **REMOVE** `needs-revision`, **ADD** resolution label (`wontfix`/`duplicate`) |
| `in-progress` | PR created | (review) | **REMOVE** `in-progress` |
| `in-progress` | Implementation blocked | `needs-revision` | **REMOVE** `in-progress`, **ADD** `needs-revision` |
| (review) | PR merged | (closed) | No label change (labels no longer relevant on closed issue) |
| (review) | PR changes requested | `needs-revision` | **ADD** `needs-revision` |
| Any state | Bug/issue type identified | (categorized) | **ADD** categorization label (`bug`, `enhancement`, etc.) — categorization labels are additive, they do NOT replace workflow labels |

### GitHub `labels` Parameter Warning

**The GitHub `labels` parameter replaces ALL labels on an issue — it is NOT additive.**

When updating labels via `github_issue_write` or similar tools, you MUST:

1. **Read current labels first**: `github_issue_read(method="get_labels", ...)`
2. **Construct the complete label set**: Include existing labels PLUS any new labels
3. **Write the full set**: Pass ALL labels, not just the ones being added

```python
# WRONG — removes all other labels
github_issue_write(method="update", labels=["in-progress"])

# CORRECT — preserves existing labels
current_labels = [l["name"] for l in github_issue_read(method="get_labels", ...)]
new_labels = set(current_labels) - {"needs-approval"} | {"in-progress"}
github_issue_write(method="update", labels=list(new_labels))
```

**Adding a label without reading first will ERASE all other labels.** Always read before writing.

### Label Transition Cross-References

Skills that change issue state MUST consult this section (`§10`) before adding or removing labels:

| Skill | Task(s) | Label Actions |
| -- | -- | -- |
| `approval-gate` | `verify-authorization`, `verify-blockers`, `verify-already-implemented`, `completion` | Remove `needs-approval` on approval; add `needs-revision` on revision; remove `needs-approval` on autoclose |
| `github-issue-creation` | `creation`, `completion` | Add `needs-approval` on creation |
| `spec-auditor` | `structure` | Add `needs-revision` when audit requires changes |
| `git-workflow` | `cleanup` | No label changes (issues closed, labels no longer relevant) |
| `writing-plans` | `create` | No label changes (plan is a sub-issue) |
| `executing-plans` | `start` | Add `in-progress` when implementation begins |

______________________________________________________________________

*Source: Content migrated from `040-plan-delivery.md`, updated per spec #821*