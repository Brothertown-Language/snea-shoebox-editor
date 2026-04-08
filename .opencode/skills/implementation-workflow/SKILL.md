---
name: implementation-workflow
description: Orchestration layer that sequences subtasks with yield-back context passing. Calls git-workflow tasks for git ops, runs implementation agents for actual work, and yields structured results between stages.
license: MIT
compatibility: opencode
---

# Skill: implementation-workflow

## Overview

Orchestration layer that coordinates the implementation workflow by sequencing subtasks with yield-back context passing. This skill handles WHEN to call tasks, WHAT context to pass, and HOW to yield results to the next stage.

**Architecture:**
- `implementation-workflow` (orchestration) → calls → `git-workflow` tasks (git ops only)
- `implementation-workflow` → invokes → implementation subagent (actual work)
- `git-workflow` tasks → yield → context back to orchestrator

**Source Attribution:** This skill addresses the yield-back coordination gaps identified in issue #77 and #68.

## Persona

You are an Implementation Workflow Orchestrator. Your focus is coordinating the sequence of subtasks, passing context between them, and ensuring clean yield-back at each stage.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `orchestrate` | Full implementation workflow sequence | ~800 |

## Invocation

- `/skill implementation-workflow` - Run full implementation workflow
- `/skill implementation-workflow --task orchestrate` - Same as above

## Operating Protocol

1. **Sequential orchestration:** This skill runs AFTER approval-gate has verified authorization
2. **Context passing:** Each subtask receives context from the previous subtask
3. **Yield-back pattern:** Each subtask yields structured results back to orchestrator
4. **HALT after review-prep:** No PR creation without explicit "create a PR" instruction

## Interdependency Chain

```
User: "#77 approved"
    ↓
approval-gate (dispatch table invoked)
    YIELDS: {issue: N, authorized: true, context: {...}}
    ↓
implementation-workflow/orchestrate (receives auth context)
    ↓
    [calls git-workflow --task pre-work]
    YIELDS: {branch: "spec/X", status: "ready"}
    ↓
    [invokes implementation subagent]
    YIELDS: {files_changed: [...], commit_status: {...}}
    ↓
    [invokes verification-before-completion --task verify]  ← MANDATORY GATE
    YIELDS: {verification: "pass" | "fail"}
    ↓ (if FAIL → HALT and report)
    ↓ (if PASS → continue)
    [invokes finishing-a-development-branch --task checklist]  ← MANDATORY GATE
    YIELDS: {checklist: "pass" | "fail"}
    ↓ (if FAIL → HALT and report)
    ↓ (if PASS → continue)
    [calls git-workflow --task review-prep]
    YIELDS: {compare_url: "...", exec_summary: "..."}
    ↓
    HALT (chat shows URL + summary)
```

## Orchestration Task

### Step 1: Receive Authorization Context

**Input (from approval-gate):**
```yaml
issue: 77
authorized: true
context:
  title: "[SPEC] Integrate Superpowers workflow"
  phases: [Core Skills, Dispatch Table, Quality Gates, ...]
  current_phase: 1
  authorization_comment: "approved"
```

**Action:**
- Verify authorization context is valid
- Extract issue details for implementation
- Pass to pre-work

### Step 2: Call Pre-Work (Git Ops Only)

**Context passed to pre-work:**
```yaml
authorization: confirmed
issue: 77
working_tree_status: checked
```

**Expected yield from pre-work:**
```yaml
status: success
branch: "spec/workflow-skills-integration"
stash_created: false
working_tree_clean: true
ready_for: "implementation"
```

**Intelligence note:** Format matches what implementation needs (branch name, clean state).

### Step 3: Invoke Implementation Subagent

**Context passed to subagent:**
```yaml
branch: "spec/workflow-skills-integration"
issue: 77
task: "Implement Phase 1 of spec"
working_tree_clean: true
```

**Implementation subagent responsibilities:**
- Read spec details
- Edit/create files
- Make WIP commits as needed (calls `git-workflow --task commit-prep` directly)
- Report progress

**Expected yield from implementation:**
```yaml
status: success | failure
files_changed:
  - path: ".opencode/skills/new-skill/SKILL.md"
    action: "created"
  - path: ".opencode/dispatch-table.yaml"
    action: "modified"
commits:
  - hash: "abc123"
    message: "WIP: Phase 1 core skills"
summary: "Created 4 new skills, updated dispatch table"
ready_for: "review"
```

**Intelligence note:** Format provides what review-prep needs (files changed, commit summary).

### Step 3.5: Verification Gate (MANDATORY, NO DECISION POINT)

**⚠️ CRITICAL: This step is MANDATORY and has NO decision point. Skipping it is a CRITICAL GUIDELINE VIOLATION.**

After implementation completes, BEFORE proceeding to review-prep, invoke verification skills in strict sequence:

**Step 3.5a: Invoke verification-before-completion**
```
/skill verification-before-completion --task verify
```

**Context:**
```yaml
issue: 77
phase: "Phase 1 implementation"
success_criteria: [from spec issue]
files_changed: [...]
```

**Expected yield:**
```yaml
status: pass | fail
verified_criteria:
  - criterion: "..."
    evidence: "..."
    verified: true
unverified_criteria: []  # Must be empty to pass
missing_evidence: []      # Must be empty to pass
```

**If verification FAILS → HALT and report.** Do NOT proceed to Step 4.

**Step 3.5b: Invoke finishing-a-development-branch**
```
/skill finishing-a-development-branch --task checklist
```

**Context:**
```yaml
branch: "spec/workflow-skills-integration"
implementation_complete: true
verification_passed: true
```

**Expected yield:**
```yaml
status: pass | fail
checklist_results:
  - item: "All changes committed"
    passed: true
  - item: "Lint checks pass"
    passed: true
  - item: "Tests pass"
    passed: true
  - item: "Branch pushed"
    passed: true
failed_items: []  # Must be empty to pass
```

**If checklist FAILS → HALT and report.** Do NOT proceed to Step 4.

**Why This Gate Exists:**

| Without Gate | With Gate |
|-------------|-----------|
| Agent skips verification | Success criteria checked with evidence |
| Agent skips branch checklist | Uncommitted changes, failing tests caught |
| Agent manually executes steps | Full skill context loaded with enforcement |
| "Changes look correct" justification | Required evidence for each criterion |

### Step 4: Call Review-Prep (Git Ops Only)

**Context passed to review-prep:**
```yaml
branch: "spec/workflow-skills-integration"
commits_pushed: true
implementation_complete: true
```

**Expected yield from review-prep:**
```yaml
status: success
compare_url: "https://github.com/owner/repo/compare/main...branch"
exec_summary: |
  **Summary:**
  
  Integrated workflow skills from Superpowers repository.
  
  **Outcome:**
  
  Created 4 core skills for brainstorming, planning, execution, and verification.
ready_for: "pr_creation"
```

**Intelligence note:** Format matches what CHAT needs (markdown + actionable URL).

### Step 5: HALT with Results

**Chat output:**
```markdown
**Summary:**

Integrated workflow skills from Superpowers repository.

**Outcome:**

Created 4 core skills for brainstorming, planning, execution, and verification.

Compare URL: https://github.com/owner/repo/compare/main...branch
```

**Issue comment:**
```markdown
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)

**Summary:**

Integrated workflow skills from Superpowers repository.

**Outcome:**

Created 4 core skills for brainstorming, planning, execution, and verification.
```

**HALT condition:**
- Do NOT create PR
- Do NOT close issue
- Wait for explicit "create a PR" instruction

## Context Passing Between Subtasks

### What Pre-Work Needs FROM Authorization

```yaml
authorization: confirmed (bool)
issue_number: int
```

### What Implementation Needs FROM Pre-Work

```yaml
branch: string
working_tree_clean: bool
```

### What Review-Prep Needs FROM Implementation

```yaml
files_changed: list
commit_summary: string
implementation_status: success | failure
```

### What Verification Gate Needs FROM Implementation

```yaml
issue_number: int
phase: string
success_criteria: list
files_changed: list
```

### What Finishing Checklist Needs FROM Verification

```yaml
branch: string
verification_passed: true
implementation_complete: true
```

### What Chat Needs FROM Review-Prep

```yaml
compare_url: string (actionable link)
exec_summary: string (markdown, human-readable)
```

## Git Workflow Task Purification

**This skill CALLS git-workflow tasks. Git-workflow does NOT contain implementation logic.**

### What Git-Workflow Tasks DO (Pure Git Ops)

| Task | Purpose | Implements? |
|------|---------|-------------|
| `pre-work` | Stash changes, create branch | NO - git ops only |
| `commit-prep` | Stage and commit changes | NO - git ops only |
| `review-prep` | Push branch, gen URL | NO - git ops only |
| `pr-creation` | Squash, create PR | NO - git ops only |
| `cleanup` | Delete merged branches | NO - git ops only |

### What Git-Workflow Tasks DO NOT Do

| ❌ NOT in git-workflow | Moved Where? |
|------------------------|---------------|
| Implementation logic | `implementation-workflow` orchestrator |
| File editing | Implementation subagent |
| Spec reading | Implementation subagent |
| Progress tracking | Implementation subagent |

## Dispatch Table Integration

```yaml
# POST-AUTHORIZATION GATE - Workflow orchestration
- trigger: "After approval-gate confirms authorization"
  skill: "implementation-workflow"
  task: "orchestrate"
  purpose: "Sequence implementation workflow with yield-back context"
  automatic: true
  note: "Called after approval-gate, orchestrates git-workflow + implementation"
```

## Enforcement Mechanisms

### ⚠️ CRITICAL: Verification Gate (Step 3.5)

**This gate is MANDATORY and has NO decision point.** It cannot be skipped, bypassed, or manually executed.

| Step | Skill | Required? | Decision Point? |
|------|-------|-----------|-----------------|
| 3.5a | verification-before-completion --task verify | YES | NO |
| 3.5b | finishing-a-development-branch --task checklist | YES | NO |
| 4 | git-workflow --task review-prep | YES | NO |

**Skipping any step in this sequence is a CRITICAL GUIDELINE VIOLATION.**

See `000-critical-rules.md` → "Skipping Post-Implementation Verification Skills" for the enforcement rule.

### ⚠️ CRITICAL: No Implementation Logic in Git-Workflow

Git-workflow skills MUST remain pure git operations:
- ✅ Git commands (stash, branch, commit, push)
- ✅ Git status checks
- ✅ Git cleanup
- ❌ File editing
- ❌ Spec reading
- ❌ Implementation decisions

### ⚠️ CRITICAL: Yield-Back Before HALT

Each subtask MUST yield structured context before HALT:
- pre-work must yield branch info
- implementation must yield files changed
- review-prep must yield URL + summary

### ⚠️ CRITICAL: HALT After Review-Prep

NEVER proceed to PR creation without explicit "create a PR":
- review-prep yields URL for CHAT
- HALT and wait
- Only "create a PR" triggers pr-creation

## Integration with Approval-Gate

Approval-gate runs FIRST (dispatch table), then yields to implementation-workflow:

```
User: "#77 approved"
    ↓
approval-gate (dispatch table triggers)
    → Verifies authorization
    → Checks sub-issues
    → Context: {issue, authorized, ...}
    ↓
implementation-workflow (receives context)
    → Orchestrates rest of workflow
```

## Platform Compatibility

- **GitHub:** Uses GitHub MCP tools for git operations
- **GitBucket:** Uses GitBucket Python API client for git operations
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Cross-References

- Related skills: `git-workflow` (git ops), `approval-gate` (authorization)
- Related guidelines: `010-approval-gate.md`, `110-git-branch-first.md`
- Related dispatch: `dispatch-table.yaml` (approval-gate → implementation-workflow sequence)

## Common Issues

| Issue | Resolution |
|-------|------------|
| Authorization context lost | approval-gate passes context to implementation-workflow |
| Pre-work asks for auth again | Pre-work receives context from orchestrator, no re-check |
| Implementation doesn't commit | Implementation calls git-workflow commit-prep directly |
| Verification fails | HALT and report missing evidence; do NOT proceed to review-prep |
| Finishing checklist fails | HALT and report issues (lint, tests, uncommitted); do NOT proceed to review-prep |
| Review-prep HALTs prematurely | Correct behavior - wait for "create a PR" |

## Migration from Old Architecture

### What Changes

| Old (git-workflow) | New (implementation-workflow) |
|--------------------|-------------------------------|
| git-workflow contains implementation logic | Implementation logic moved to subagent |
| No orchestration layer | implementation-workflow orchestrates |
| No context passing | Yield-back pattern between subtasks |
| Redundant auth checks | Auth check only in approval-gate |

### Backward Compatibility

- git-workflow tasks remain unchanged (still callable independently)
- dispatch-table additions (automatic invocation)
- Existing manual `/skill git-workflow --task X` still works

## Examples

### Example 1: Typical Implementation Flow

```
User: "#77 approved"
    ↓
approval-gate: "Authorized for issue #77"
    ↓
implementation-workflow/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready for implementation"
    → Invokes implementation subagent
        → Subagent edits files
        → Subagent calls commit-prep directly
        → Subagent yields: "4 files changed, 2 commits"
    → Invokes verification-before-completion --task verify
        → All success criteria verified with evidence
        → Verification PASSES
    → Invokes finishing-a-development-branch --task checklist
        → All changes committed, tests pass, branch pushed
        → Checklist PASSES
    → Calls review-prep: "URL: https://..., summary: ..."
    → HALT with URL in chat
```

### Example 2: Implementation Fails

```
implementation-workflow/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready"
    → Invokes implementation subagent
        → Subagent encounters error
        → Subagent yields: {status: "failure", error: "..."}
    → HALT with error report
    → Wait for user instruction
```

### Example 3: Verification Fails

```
implementation-workflow/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready"
    → Invokes implementation subagent
        → Subagent yields: {status: "success", files_changed: [...]}
    → Invokes verification-before-completion --task verify
        → Success criterion missing evidence
        → Verification FAILS
    → HALT: "Verification failed. Missing evidence for: [criterion]"
    → Wait for user to provide evidence or fix
```

### Example 4: Branch Checklist Fails

```
implementation-workflow/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready"
    → Invokes implementation subagent
        → Subagent yields: {status: "success"}
    → Invokes verification-before-completion --task verify
        → Verification PASSES
    → Invokes finishing-a-development-branch --task checklist
        → Lint errors found, uncommitted changes
        → Checklist FAILS
    → HALT: "Branch not ready. Fix: [lint errors, commit changes]"
    → Wait for user to fix issues
```

### Example 5: Working Tree Dirty

```
implementation-workflow/orchestrate:
    → Calls pre-work
        → pre-work detects dirty working tree
        → pre-work stashes changes
        → pre-work yields: {stash_created: true, branch: "spec/X"}
    → Continues with implementation...
```