# Task: orchestrate

## Purpose

Full implementation workflow sequence — from receiving authorization context to yielding review-prep results. Coordinates git-workflow tasks (git ops only) and implementation subagents with mandatory verification gates.

## Entry Criteria

- Approval-gate has verified authorization and yielded context
- Issue number and spec are available
- Authorization context includes: `{issue, authorized: true, context: {...}}`

## Exit Criteria

- Compare URL and executive summary are in chat
- HALT after review-prep (no PR creation without explicit instruction)
- All verification gates passed

## Procedure

### Step 1: Receive Authorization Context

**Input (from approval-gate):**
```yaml
issue: 77
authorized: true
context:
  title: "[SPEC] Integrate skill enforcement plugin"
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
worktree_path: ".worktrees/spec-workflow-skills-integration"
dev_base_hash: "abc1234"
working_tree_clean: true
ready_for: "implementation"
```

**Intelligence note:** Format matches what implementation needs (branch name, clean state).

### Step 3: Invoke Implementation Subagent

**⚠️ PRE-IMPLEMENTATION CHECK (CRITICAL):**

Before invoking the implementation subagent, verify:

1. **Bug-discovery guardrail**: Is this implementation for a bug discovered during other work? If yes, HALT — bug discovery does NOT authorize implementation. Create an issue and wait for explicit authorization.
2. **Spec exists**: Verify the issue has a spec that was explicitly approved.
3. **Authorization confirmed**: Verify the user said "approved" or "go" for this specific issue.

If ANY check fails → HALT and report. Do NOT invoke the implementation subagent.

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
compare_url: "https://github.com/owner/repo/compare/dev...branch"
exec_summary: |
  **Summary:**
  
  Integrated workflow skills into the enforcement plugin.
  
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

Compare URL: https://github.com/owner/repo/compare/dev...branch
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

## Edge Cases

### Implementation Fails

```
implementation-workflow/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready"
    → Invokes implementation subagent
        → Subagent encounters error
        → Subagent yields: {status: "failure", error: "..."}
    → HALT with error report
    → Wait for user instruction
```

### Verification Fails

```
implementation-workflow/orchestrate:
    → Invokes verification-before-completion --task verify
        → Success criterion missing evidence
        → Verification FAILS
    → HALT: "Verification failed. Missing evidence for: [criterion]"
    → Wait for user to provide evidence or fix
```

### Branch Checklist Fails

```
implementation-workflow/orchestrate:
    → Invokes finishing-a-development-branch --task checklist
        → Lint errors found, uncommitted changes
        → Checklist FAILS
    → HALT: "Branch not ready. Fix: [lint errors, commit changes]"
    → Wait for user to fix issues
```

### Working Tree Dirty

```
implementation-workflow/orchestrate:
    → Calls pre-work
        → pre-work detects dirty working tree
        → pre-work creates worktree
        → pre-work yields: {worktree_path: ".worktrees/spec-X", branch: "spec/X"}
    → Continues with implementation...
```