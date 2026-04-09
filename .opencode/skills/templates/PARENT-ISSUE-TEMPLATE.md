# Parent Issue Orchestrator Template

Use this template for multi-task specifications that coordinate multiple sub-issues.

---

## Template

```markdown
# Spec: [Feature Name]

STATUS: X.Y
CREATED: YYYY-MM-DD

---

## Overview

[2-3 sentence summary of the entire feature. What it accomplishes and why it matters.]

---

## Subtasks (Sequential Execution)

| # | Subtask | Status | Issue |
|---|---------|--------|-------|
| X.1 | [Phase X - Task description] | ☐ | #NNN |
| X.2 | [Phase X - Task description] | ☐ | #NNN |
| Y.1 | [Phase Y - Task description] | ☐ | #NNN |

**⚠️ CRITICAL: Only ONE subtask executes at a time. STATUS controls which subtask is active.**

---

## Context

[Background, stakeholders, affected systems - concise context needed by fresh-start agents]

---

## Entry Criteria

- [ ] Authorization received for this specific subtask
- [ ] STATUS in parent matches this subtask number
- [ ] Previous subtask completed (if applicable)

---

## Exit Criteria

- [ ] All verification steps pass
- [ ] Subtask issue closed with summary
- [ ] Parent STATUS advances to next subtask number

---

## Cross-References

- Related: `[skill-name]` skill
- Related: `XXX-guideline-name.md`

---

## Constraints

| Constraint | Details |
|------------|---------|
| [Constraint 1] | [Description] |
| [Constraint 2] | [Description] |

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments. Issue body edits destroy history.
```

---

## STATUS Format

| Status | Meaning |
|--------|---------|
| `X.1` | Subtask 1 of Phase X is active |
| `X.2` | Subtask 2 of Phase X is active |
| `completed` | All subtasks complete |

---

## Task Table Requirements

### ✅ Required Columns

| Column | Purpose |
|--------|---------|
| `#` | Subtask number (must match STATUS) |
| `Subtask` | Descriptive title (WHAT, not phase type) |
| `Status` | Checkbox (`☐` or `☑`) |
| `Issue` | Link to sub-issue (`#NNN`) |

### Title Format for Sub-Issues

```
[Task: #<parent-number>] <descriptive-title>
```

**Examples:**
- `[Task: #469] Refactor Tier 1 Skills with Sub-Task Architecture`
- `[Task: #469] Design sub-issue orchestrator template`
- `[Task: #469] Update AGENTS.md with sub-issue invocation guidance`

**❌ WRONG:**
- `[Task: #469] Phase 1 - Implementation` (only type, no description)
- `[Task: #469] Phase 2 - Testing` (only type, no description)

---

## Single Subtask at a Time (CRITICAL)

**The architecture enforces sequential execution:**

1. **STATUS Gate**: Agent can ONLY implement subtask matching current STATUS
2. **Sequential Advancement**: STATUS advances only after subtask completion
3. **No Parallel Execution**: Previous subtask must complete before next starts

### Why This Matters

| Problem | Solution |
|---------|----------|
| Two agents start simultaneously | Only one STATUS authorized at a time |
| Git branch conflicts | One subtask = one branch = no race |
| File edit races | Only one active subtask = no conflicts |
| Stash conflicts | Sequential = no stash race |

---

## Minimal Parent Content

Parent issues should be **~100 lines max**:

- Overview: 3-5 lines
- Subtask table: 5-15 lines
- Context: 10-30 lines
- Entry/Exit criteria: 5-15 lines
- Cross-references: 5 lines
- Constraints: 5-10 lines

**Implementation details belong in sub-issues, not parent issues.**

---

## Integration Points

| Component | Purpose |
|-----------|---------|
| `approval-gate` skill | Verify STATUS matches requested subtask |
| `git-workflow` skill | Create branch named after subtask |
| `github-sub-issues` skill | Verify sub-issue structure exists |
| `124-github-archive-workflow.md` | Parent closure only after all children complete |

---

## Example

```markdown
# Spec: Skills: Sub-Task Architecture for Context Window Management

STATUS: 1.1
CREATED: 2026-03-31

---

## Overview

Refactor complex skills to use sub-task architecture, enabling selective loading of relevant portions instead of entire skills. This reduces context window pollution and improves agent efficiency.

---

## Subtasks (Sequential Execution)

| # | Subtask | Status | Issue |
|---|---------|--------|-------|
| 1.1 | Refactor Tier 1 Skills with Sub-Task Architecture | ✅ | #470 |
| 1.2 | Design GitHub Sub-Issue Sub-Task Architecture | ☐ | #473 |
| 2.1 | Test Sub-Task Invocation | ☐ | (pending) |
| 2.2 | Update Guidelines and Agent Files | ☐ | (pending) |

**⚠️ Only subtask 1.2 is currently active. STATUS must match subtask number before implementation.**

---

## Context

Skills are monolithic documents that load entirely into context. For skills with long procedural workflows (500+ lines), this pollutes context unnecessarily.

---

## Entry Criteria

- [ ] Authorization received for specific subtask
- [ ] STATUS matches subtask number
- [ ] Previous subtask completed (if applicable)

---

## Exit Criteria

- [ ] All subtasks marked ☑
- [ ] Context savings measured (50%+ target)
- [ ] AGENTS.md updated with sub-task preference

---
```