---
name: github-sub-issues
description: Multi-task spec sub-issue creation and management workflow. Defines single-task exemption, auto-create workflow, database ID requirement, and phase-level structure for GitHub Issue sub-issues.
license: MIT
compatibility: opencode
---

# GitHub Sub-Issues Workflow

## Role

You are a Sub-Issue Workflow enforcer. Your focus is ensuring multi-task specs have proper sub-issue structure before implementation begins.

## Single-Task vs Multi-Task Exemption

### ⚠️ SINGLE-TASK EXEMPTION

**Single-task issues do NOT require sub-issues.**

A spec is "single-task" if:
- Exactly ONE implementation task/phase
- No task decomposition needed
- Entire spec implementable in one unit of work

**Example - Single-task (NO sub-issue required):**
```
SPEC #100: Fix typo in README
- One task: Fix the typo
- No decomposition needed
```

**Example - Multi-task (SUB-ISSUES REQUIRED):**
```
SPEC #101: Add user authentication
- Phase 1: Database schema
- Phase 2: API endpoints
- Phase 3: UI components
```

If single-task: Proceed without sub-issue verification.
If multi-task: Sub-issues are MANDATORY.

---

## Sub-Issue Verification Gate

### ⚠️ MANDATORY CHECK (Before Implementation)

1. Call `github_issue_read method=get_sub_issues` on parent issue
2. **If empty AND multi-task:**
   - AUTO-CREATE sub-issues (see workflow below)
   - DO NOT BLOCK for manual creation
3. **If sub-issues exist:**
   - Verify phase being implemented is among them
   - Proceed with implementation

### 🚫 FORBIDDEN

- Implementing phase that exists only as text in parent issue body
- Proceeding when `get_sub_issues` returns empty (for multi-task specs) without creating sub-issues
- Assuming markdown checkboxes = task tracking
- Creating step-level sub-issues (create PHASE-level only)

---

## Auto-Create Workflow

**When multi-task spec has NO sub-issues:**

```
For each PHASE in spec:
  1. Create issue: github_issue_write(method="create",
     title="[Task: #N] <phase-description>")
  2. Get database ID from response (.id field)
  3. Link: github_sub_issue_write(method="add",
     issue_number=N, sub_issue_id=db_id)

Post comment: "Created X sub-issues for phase tracking"
Proceed to implement first phase
```

**⚠️ DATABASE ID REQUIREMENT:**
- Use `.id` field from response (e.g., `4129879155`)
- NOT the issue number (e.g., `10`)
- Get via `github_issue_read method=get` response

---

## Phase-Level vs Step-Level

**Sub-issues = PHASES, not steps.**

```
✅ CORRECT: Phase-level sub-issues
SPEC #100: Feature Name
├── Task #101: [Task: #100] Create database schema
├── Task #102: [Task: #100] Implement API endpoints
└── Task #103: [Task: #100] Build UI components

❌ WRONG: Step-level sub-issues (too granular)
SPEC #100: Feature Name
├── Task #101: [Task: #100] Step 1.1 - Create table
├── Task #102: [Task: #100] Step 1.2 - Add index
└── Task #103: [Task: #100] Step 1.3 - Migrate data
```

**Rationale:** Phases are approval units. Steps are implementation details within phases.

---

## Title Format

Sub-issue titles MUST be descriptive. Use the WHAT, not the TYPE.

### ✅ REQUIRED Format

```
[Task: #<parent-number>] <descriptive-title>
```

Where `<descriptive-title>` describes WHAT the task accomplishes, not just the phase type.

### Examples

**✅ GOOD - Descriptive titles:**
- `[Task: #100] Add OAuth2 authentication to API`
- `[Task: #100] Create user registration endpoint`
- `[Task: #100] Run integration test suite`
- `[Task: #100] Review API security changes`

**❌ BAD - Boilerplate phase names:**
- `[Task: #100] Phase 1 - Implementation` ❌ (no description, only type)
- `[Task: #100] Phase 2 - Testing` ❌ (no description, only type)
- `[Task: #100] Phase 3 - Review` ❌ (no description, only type)

**Why:** 
- "Implementation", "Testing", "Review" describe the TYPE of work, not WHAT is being done
- GitHub sub-issue view already shows hierarchy - no need for "Phase X" prefix
- Descriptive titles improve scannability without opening issues

### Extraction Rule

For multi-phase specs, extract the descriptive content from each phase:

**Spec:**
```
## Phase 1: Add OAuth2 authentication (Gated)
## Phase 2: Create user registration endpoint (Gated)
## Phase 3: Review API security changes (Gated)
```

**Sub-issue titles:**
1. `[Task: #100] Add OAuth2 authentication`
2. `[Task: #100] Create user registration endpoint`
3. `[Task: #100] Review API security changes`

Use the phase description AFTER the colon/number, not the phase type.

### ⚠️ BOILERPLATE TITLE PROHIBITION (CRITICAL)

Sub-issue titles that describe generic activities without specifying the concern are PROHIBITED:

| Pattern | Status | Reason |
|---------|--------|--------|
| `[Task: #N] Phase 1` | PROHIBITED | No concern described |
| `[Task: #N] Implementation` | PROHIBITED | Activity, not concern |
| `[Task: #N] Task 1` | PROHIBITED | Placeholder, no meaning |
| `[Task: #N] Do the work` | PROHIBITED | Meaningless |

### Validation

| Pattern | Status | Reason |
|---------|--------|--------|
| Single-word generic activity | BOILERPLATE-TITLE | No concern boundary |
| "Phase N" without description | BOILERPLATE-TITLE | Placeholder, not meaningful |
| "Implementation" alone | BOILERPLATE-TITLE | Activity, not concern |
| Activity + specific concern | ACCEPTABLE | Describes WHAT is being done |

**Enforcement:** Use the `BOILERPLATE-TITLE` problem class in spec-auditor for violations.

---

## Correct Hierarchy

Each sub-issue MUST:
1. Be a separate GitHub Issue (using `.id` for database ID)
2. Be linked via `github_sub_issue_write method=add`
3. Be visible in parent's Task List (GitHub UI)

---

## Why This Matters

| Problem | Solution |
|---------|----------|
| Markdown checkboxes have no state tracking | Sub-issues provide proper parent-child relationships |
| Cannot track progress across sessions | Sub-issues persist in GitHub |
| Cannot see what's pending | GitHub sub-issue view shows remaining children |
| Premature parent closure loses visibility | Parent stays open until all children complete |

---

## Guideline References

| Guideline | Section |
|-----------|---------|
| `010-approval-gate.md` | Sub-issue Verification Gate |
| `120-github-issue-first.md` | Spec Tracking: GitHub Issues & Sub-Issues |
| `000-critical-rules.md` | Critical Violation: Sub-issue Structure Bypass |

---

## Templates

- **Parent Issue Orchestrator**: `.opencode/skills/templates/PARENT-ISSUE-TEMPLATE.md`
- **Sub-Issue Task**: `.opencode/skills/templates/SUB-ISSUE-TEMPLATE.md`

Use these templates when creating new parent/child issue structures.

---

## STATUS Gate Verification (CRITICAL)

### Single Subtask at a Time

**The architecture enforces sequential execution:**

1. **Parent Issue orchestrates**: Parent issue tracks which subtask is "active" via STATUS field
2. **STATUS Format**: `STATUS: X.Y` where X = phase, Y = subtask within phase
3. **Authorization Gate**: Agent can ONLY implement subtask matching current STATUS
4. **Sequential Completion**: After subtask completes → STATUS advances → Next subtask becomes eligible

### STATUS Verification Protocol

Before implementing ANY subtask:

1. **Get parent STATUS:**
   ```python
   parent = github_issue_read(method="get", issue_number=parent_issue)
   # Parse STATUS from body
   # STATUS format: "STATUS: X.Y" or "STATUS: completed"
   # If STATUS not found, default to first subtask (1.1)
   ```

2. **Extract authorized subtask:**
   - "approved: 1.2" → subtask 1.2
   - "approved" (no number) → check STATUS for current phase
   - If STATUS not found → default to first subtask (1.1)

3. **Verify match:**
   - If authorized for X.Y → use X.Y (explicit override)
   - If "approved" (no number) AND STATUS found → use STATUS value
   - If "approved" (no number) AND STATUS not found → use first subtask (1.1)
   - If subtask not in sub-issues list → HALT, report available subtasks

4. **Report decision (MANDATORY - no silent halts):**
   ```markdown
   **STATUS Gate Verification:**
   - Authorization: "approved" (no phase specified)
   - STATUS field: X.Y (or "not found, defaulting to first subtask")
   - Sub-issue: #NNN
   - Proceeding with implementation
   ```

5. **If mismatch:**
   POST report: "STATUS mismatch: authorized for X.Y but STATUS is Z.W. Please update STATUS or authorize correct subtask."

### Why STATUS Gate Matters

| Problem | Solution |
|---------|----------|
| Two agents start simultaneously | Only one STATUS authorized at a time |
| Git branch conflicts | One subtask = one branch = no race |
| File edit races | Only one active subtask = no conflicts |
| Stash races | Sequential = no stash collision |

### Forbidden Actions

- Implementing when STATUS doesn't match authorized subtask
- Parallel execution of subtasks
- Proceeding without STATUS verification
- Skipping STATUS gate for "quick" subtasks
- **Halting silently** - MUST report STATUS gate decision to user
- **Assuming failure without reporting** - MUST explain what was checked and outcome

---

## Integration Points

| Skill/Guideline | When |
|-----------------|------|
| `git-workflow` | Before starting implementation |
| `010-approval-gate.md` | Pre-implementation check |
| `120-github-issue-first.md` | Issue structure |
| `124-github-archive-workflow.md` | Parent/child closure |

---

## Example Workflow

```
User: "approved: 1" for SPEC #100 (multi-task)

Agent:
1. Calls github_issue_read(method="get_sub_issues", issue_number=100)
2. Result: Empty []
3. Spec has 3 phases → multi-task
4. AUTO-CREATE:
   - Issue #101: [Task: #100] Phase 1 - Database schema
   - Issue #102: [Task: #100] Phase 2 - API endpoints
   - Issue #103: [Task: #100] Phase 3 - UI components
5. Links each to parent via github_sub_issue_write
6. Posts comment: "Created 3 sub-issues for phase tracking"
7. Proceeds to implement Phase 1
```