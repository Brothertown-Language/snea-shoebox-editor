# Task: orchestrate

Migrated from `implementation-workflow` task orchestrate.

## Purpose

Full implementation workflow sequence — from receiving authorization context to yielding review-prep results. Coordinates git-workflow tasks (git ops only) and implementation subagents with mandatory verification gates. Includes pre-flight assessment to determine direct implementation vs decomposition.

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
  title: '[SPEC] Integrate skill enforcement plugin'
  phases: [Core Skills, Dispatch Table, Quality Gates, '...']
  current_phase: 1
  authorization_comment: approved
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
branch: spec/workflow-skills-integration
worktree_path: .worktrees/spec-workflow-skills-integration
dev_base_hash: abc1234
working_tree_clean: true
ready_for: implementation
```

**Intelligence note:** Format matches what implementation needs (branch name, clean state).

### Step 3: Pre-Flight Assessment

**⚠️ PRE-IMPLEMENTATION CHECK (CRITICAL):**

Before proceeding, verify:

1. **Bug-discovery guardrail**: Is this implementation for a bug discovered during other work? If yes, HALT — bug discovery does NOT authorize implementation. Create an issue and wait for explicit authorization.
2. **Spec exists**: Verify the issue has a spec that was explicitly approved.
3. **Authorization confirmed**: Verify the user said "approved" or "go" for this specific issue.

If ANY check fails → HALT and report. Do NOT proceed.

**Invoke assessment task:**

```
/skill divide-and-conquer --task assess
```

**Assessment yields one of:**

- `IMPLEMENT_DIRECTLY` → Proceed to Step 4a
- `DECOMPOSE` → Proceed to Step 4b

### Step 4a: Implement Directly (Trivial Tasks)

For tasks assessed as `IMPLEMENT_DIRECTLY`:

- The orchestrator implements directly without sub-agent dispatch
- Scope is small enough that context overflow is not a risk
- Still MUST run verification gate (Step 5) and review-prep (Step 6)
- After implementation, proceed to Step 5

### Step 4b: Decompose and Dispatch (Non-Trivial Tasks)

For tasks assessed as `DECOMPOSE`:

1. **Invoke decompose task:**

   ```
   /skill divide-and-conquer --task decompose
   ```

   Yields: ordered sub-tasks with descriptions, scope, boundaries, and dependencies.

2. **Invoke dispatch task** for each sub-task in order:

   ```
   /skill divide-and-conquer --task dispatch
   ```

   Each sub-agent returns a structured result per Sub-agent Result Contract.

3. **Invoke merge task** to aggregate results:

   ```
   /skill divide-and-conquer --task merge
   ```

   Yields: final summary, conflict identification, readiness for completion.

### Step 4c: Batch Assembly (When Batch Needed)

For multi-issue batches or when `assemble-batch` is needed:

1. **Invoke assemble-batch task:**

   ```
   /skill divide-and-conquer --task assemble-batch
   ```

   This handles:
   - Branch-per-issue creation and worktrees
   - Dependency merge protocol (Tier 1-2 auto-resolve, Tier 3 HALT)
   - Sub-agent dispatch per issue with intent-and-context metadata
   - Squash-merge each feature branch into batch branch
   - Frozen branch enforcement

2. **After assemble-batch completes**, proceed to Step 5

### Step 5: Verification Gate (MANDATORY, NO DECISION POINT)

**⚠️ CRITICAL: This step is MANDATORY and has NO decision point. Skipping it is a CRITICAL GUIDELINE VIOLATION.**

After implementation completes, BEFORE proceeding to review-prep, invoke verification skills in strict sequence:

**Step 5a: Invoke verification-before-completion**

```
/skill verification-before-completion --task verify
```

**Context:**

```yaml
issue: 77
phase: Phase 1 implementation
success_criteria: [from spec issue]
files_changed: ['...']
```

**Expected yield:**

```yaml
status: pass | fail
verified_criteria:
  - criterion: '...'
    evidence: '...'
    verified: true
unverified_criteria: []  # Must be empty to pass
missing_evidence: []      # Must be empty to pass
```

**If verification FAILS → HALT and report.** Do NOT proceed to Step 6.

**Step 5b: Invoke finishing-a-development-branch**

```
/skill finishing-a-development-branch --task checklist
```

**Context:**

```yaml
branch: spec/workflow-skills-integration
implementation_complete: true
verification_passed: true
```

**Expected yield:**

```yaml
status: pass | fail
checklist_results:
  - item: All changes committed
    passed: true
  - item: Lint checks pass
    passed: true
  - item: Tests pass
    passed: true
  - item: Branch pushed
    passed: true
failed_items: []  # Must be empty to pass
```

**If checklist FAILS → HALT and report.** Do NOT proceed to Step 6.

**Why This Gate Exists:**

| Without Gate | With Gate |
| -- | -- |
| Agent skips verification | Success criteria checked with evidence |
| Agent skips branch checklist | Uncommitted changes, failing tests caught |
| Agent manually executes steps | Full skill context loaded with enforcement |
| "Changes look correct" justification | Required evidence for each criterion |

### Step 6: Call Review-Prep (Git Ops Only)

**Context passed to review-prep:**

```yaml
branch: spec/workflow-skills-integration
commits_pushed: true
implementation_complete: true
```

**Expected yield from review-prep:**

```yaml
status: success
compare_url: https://github.com/owner/repo/compare/dev...branch
exec_summary: |
  **Summary:**

  Integrated workflow skills into the enforcement plugin.

  **Outcome:**

  Created 4 core skills for brainstorming, planning, execution, and verification.
ready_for: pr_creation
```

**Intelligence note:** Format matches what CHAT needs (markdown + actionable URL).

### Step 7: HALT with Results

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
divide-and-conquer/orchestrate:
    → Calls pre-work: "Branch: spec/X, ready"
    → Invokes implementation subagent
        → Subagent encounters error
        → Subagent yields: {status: "failure", error: "..."}
    → HALT with error report
    → Wait for user instruction
```

### Verification Fails

```
divide-and-conquer/orchestrate:
    → Invokes verification-before-completion --task verify
        → Success criterion missing evidence
        → Verification FAILS
    → HALT: "Verification failed. Missing evidence for: [criterion]"
    → Wait for user to provide evidence or fix
```

### Branch Checklist Fails

```
divide-and-conquer/orchestrate:
    → Invokes finishing-a-development-branch --task checklist
        → Lint errors found, uncommitted changes
        → Checklist FAILS
    → HALT: "Branch not ready. Fix: [lint errors, commit changes]"
    → Wait for user to fix issues
```

### Working Tree Dirty

```
divide-and-conquer/orchestrate:
    → Calls pre-work
        → pre-work detects dirty working tree
        → pre-work creates worktree
        → pre-work yields: {worktree_path: ".worktrees/spec-X", branch: "spec/X"}
    → Continues with implementation...
```

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)