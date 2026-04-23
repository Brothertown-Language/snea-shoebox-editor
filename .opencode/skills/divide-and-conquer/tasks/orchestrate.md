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
  authorization_scope: standard
  halt_at: review_prep
  pr_strategy: individual
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
authorization_scope: standard
halt_at: review_prep
pr_strategy: individual
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

**Assessment yields workload sizing context only** — it informs the dispatch but does NOT change the workflow path. All implementation goes through `assemble-work`:

- **Small workload** → `assemble-work` dispatches one sub-agent (work-of-1)
- **Large workload** → `assemble-work` dispatches multiple sub-agents

**The unified path is: `orchestrate` → `assemble-work` → sub-agent(s) → verification → review-prep.** There is no IMPLEMENT_DIRECTLY shortcut.

### Step 4: Dispatch to Assemble-Work (Unified Path)

**Every implementation — single issue or work set — follows this path.**

1. **Invoke assemble-work task:**

   ```
   /skill divide-and-conquer --task assemble-work
   ```

   This handles:
   - Branch-per-issue creation and worktrees
   - Sub-agent dispatch per issue (single issue = one sub-agent)
   - Squash-merge each feature branch into work branch
   - Dependency merge protocol (Tier 1-2 auto-resolve, Tier 3 HALT)
   - Frozen branch enforcement

2. **After assemble-work completes**, proceed to Step 5

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
  compare_url: <<Compare URL from review-prep — character-match verified per URL Sourcing Rules>>
  exec_summary: |
  **Summary:**

  Integrated workflow skills into the enforcement plugin.

  **Outcome:**

  Created 4 core skills for brainstorming, planning, execution, and verification.
ready_for: pr_creation
```

**Intelligence note:** Format matches what CHAT needs (markdown + actionable URL).

### Step 7: HALT with Results

**Chat output (MANDATORY format — executive summary FIRST, URL LAST, AI byline LAST after URL):**

```markdown
**Summary:**

Integrated workflow skills from Superpowers repository.

**Outcome:**

Created 4 core skills for brainstorming, planning, execution, and verification.

Compare URL: <<Character-match verified URL from session-init values>>

🤖 <AgentName> (<ModelId>) completed
```

**Format verification (MANDATORY — check before posting):**

- [ ] Executive summary present as first element
- [ ] Compare URL present as last element before byline
- [ ] AI byline present after URL in format `🤖 <AgentName> (<ModelId>) <status>`
- [ ] No URL before executive summary
- [ ] No byline before URL

**Issue comment:**

```markdown
🤖 <AgentName> (<ModelId>) completed

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

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Orchestration Claims (MANDATORY)

**Verify orchestration state claims against actual git/GitHub state per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Workflow step completed" | Verify step was actually executed | Check for step output in context | VERIFICATION-GAP |
| "Sub-agent dispatch correct" | Verify dispatch context includes worktree.path | Review dispatch prompt | STRUCTURE-VIOLATION |
| "Work state current" | Verify work state file reflects latest state | `glob(pattern="./tmp/work-*.md")` | VERIFICATION-GAP |
| "No skipped steps" | Verify all mandatory steps were invoked | Check for tool-call artifacts per step | MISSING-ELEMENT |

**Evidence artifact:** Tool call results and context inspection confirming orchestration accuracy.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Step claimed but no artifact | VERIFICATION-GAP | conditional | Re-execute step |
| worktree.path missing from dispatch | STRUCTURE-VIOLATION | auto-fix | Re-dispatch with correct context |
| Work state stale | VERIFICATION-GAP | auto-fix | Re-read and verify |
| Mandatory step skipped | MISSING-ELEMENT | conditional | Execute skipped step now |## Enforcement References
-  Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
-  Work state verification: see `enforcement/work-state-verification.md`
