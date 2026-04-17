# Task: batch-execution

## Purpose

Accept a batch execution plan from `approval-gate --task pre-implementation-analysis` and dispatch subagents according to the dependency order and parallelization strategy. Uses branch-per-issue with merge-based dependency resolution.

## Entry Criteria

- `pre-implementation-analysis` has completed and produced an execution plan
- All issues in the plan are verified as authorized
- Worktrees are available for execution

## Exit Criteria

- All serial phases executed in dependency order (with merge-based dependency resolution)
- All parallel-safe groups dispatched simultaneously
- All issues completed with spec and quality reviews
- All feature branches squash-merged into a single batch branch
- Non-actionable issues excluded with documented reason
- Final verification gates passed

## Procedure

### Step 1: Receive Execution Plan

The execution plan comes from `pre-implementation-analysis` and contains:

- **Serial phases**: Issues that must execute in order (must-precede chains)
- **Parallel-safe groups**: Issues that can run simultaneously (no file overlap)
- **Excluded issues**: Meta/non-code issues not requiring implementation

### Step 2: Execute Serial Phases

For each issue in a serial phase:

1. Create worktree for the issue using `using-git-worktrees --task create-worktree`
   - First issue: `BASE_BRANCH=dev` (default)
   - Dependent issues: `BASE_BRANCH=<prior-issue-branch>` — then merge the prior branch
1. **Dependency merge** (for dependent issues only):
   ```bash
   # In the dependent issue's worktree:
   git merge <prior-issue-branch> -m "Merge <prior-issue-branch> into <current-branch> — dependency chain (#<prior>, #<current>)"
   ```
   - Tiers 1-2 conflicts: Auto-resolve per `conflict-resolution` skill
   - Tier 3 (intent) conflicts: HALT and flag for developer review
1. Mark prior issue's branch as **frozen** — no rebasing, amending, or force-pushing
1. Dispatch implementer subagent per `implementer-prompt.md` with `prior_context` (AI-composed intent-and-context)
1. Run spec compliance review per `spec-reviewer-prompt.md`
1. Run code quality review per `code-quality-reviewer-prompt.md`
1. Mark issue complete
1. Compose `prior_context` for next issue based on what was implemented
1. Proceed to next serial issue

### Step 3: Execute Parallel-Safe Groups

For each parallel-safe group:

1. Create a separate worktree for each issue in the group (all from `dev`)
1. Dispatch all implementer subagents simultaneously using `task` tool
1. Wait for all subagents to complete
1. Run spec review → code quality review for each
1. Mark all group issues complete

### Step 4: Batch Assembly

After ALL issues complete:

1. Create a batch branch (name chosen by agent, e.g., `batch/<short-name>`):
   ```bash
   git checkout dev
   git checkout -b <batch-branch-name>
   ```
1. Squash-merge each feature branch into the batch branch in dependency order:
   ```bash
   git merge --squash spec/issue-a
   git commit -m "Implement #A: <description>"

   git merge --squash spec/issue-b
   git commit -m "Implement #B: <description> (#A dependency)"
   ```
1. Commit messages MUST reference issue numbers for GitHub auto-linking

### Step 5: Handle Excluded Issues

For meta/non-code issues identified in the analysis:

1. Skip implementation entirely
1. Document the exclusion reason in chat
1. Include in final report with "Excluded: no code changes required"

### Step 6: Report Completion

After ALL phases and groups complete:

1. Invoke `verification-before-completion --task verify` (MANDATORY)
1. Invoke `finishing-a-development-branch --task checklist` (MANDATORY)
1. Invoke `git-workflow --task review-prep` (MANDATORY)
1. Report completion for ALL issues ONCE
1. HALT — do NOT create PR without explicit instruction

## Execution Plan Output Format

When presenting the execution plan to the developer in chat:

```markdown
## Batch Execution Plan

**Approved Issues:** #660, #662, #621, #614, #630

### Classification

| Issue | Category | Files | Dependencies |
|-------|----------|-------|-------------|
| #660 | Meta/Non-code | N/A | None |
| #662 | Independent | `.opencode/skills/` | None |
| #621 | Conflict-risk | `.opencode/guidelines/` | After #630 |
| #614 | Independent | `src/` | None |
| #630 | Must-precede | `.opencode/guidelines/` | None |

### Execution Order

**Phase 1 (Serial — must-precede):**
1. #630 — must complete before #621
   - Branch: `spec/630-...`, worktree: `.worktrees/spec-630-...`
   - BASE_BRANCH: dev

**Phase 2 (Parallel-safe group):**
- #662 (branch: `spec/662-...`, worktree: `.worktrees/spec-662-...`, BASE_BRANCH: dev)
- #614 (branch: `spec/614-...`, worktree: `.worktrees/spec-614-...`, BASE_BRANCH: dev)

**Phase 3 (After #630 completes — merge #630 branch):**
- #621 (branch: `spec/621-...`, worktree: `.worktrees/spec-621-...`, BASE_BRANCH: dev)
  - Dependency merge: `git merge spec/630-...` before starting work

**Batch Assembly:**
- Branch: `batch/skill-consolidation`
- Squash-merge: #630, #662, #614, #621 in order

**Excluded:**
- #660 — meta/behavioral issue (no code changes)

Proceeding with execution.
```

## Dependency Merge Protocol

When a later issue depends on a prior issue:

1. The prior issue's branch is merged into the dependent issue's branch
1. Merge commit message format: `Merge <prior-branch> into <current-branch> — <description> (#<prior>, #<current>)`
1. Conflict resolution:
   - Tier 1 (trivial: whitespace, formatting): Auto-resolve, silent
   - Tier 2 (textual but safe: same intent, different text): Auto-resolve, note in chat
   - Tier 3 (intent conflict: different goals): HALT, flag for developer review
1. After merge, the prior branch is **frozen**:
   - No rebasing, amending, or force-pushing
   - If backtrack needed: assess scope (minor fix vs. major change)
   - Minor fix: fix on frozen branch, dependents re-merge
   - Major change: full review, potential discard-and-restart
   - Always requires explicit developer authorization

## Intent-and-Context Metadata

`prior_context` replaces the old `prior_results` field in the dispatch context:

- **AI-composed**: The orchestrating agent composes metadata based on the relationship between issues
- **No fixed template**: Flexible prose format
- **Focus on intent**: Design decisions, edge cases, assumptions, interfaces
- **NOT a change summary**: What changed is in git; why it changed is in prior_context

**What to include:**

- Key design decisions made during implementation
- Non-obvious constraints discovered
- Interfaces exposed that dependents should use
- Edge cases handled and how
- Assumptions downstream code relies on

**What NOT to include:**

- File change lists (use `git diff`)
- Diff contents (use `git log -p`)
- Verbatim spec text (sub-agent reads directly)

## Dispatch Context

Each sub-agent MUST receive complete worktree context:

```yaml
issue: <number>
branch: "spec/<short-name>"
worktree_path: ".worktrees/spec-<short-name>"
dev_base_hash: "<7-char-sha>"
prior_context: "<AI-composed intent and context>"
dependency_branches: ["spec/<prior-branch>"]
env_vars:
  WORKTREE_PATH: ".worktrees/spec-<short-name>"
  BRANCH_NAME: "spec/<short-name>"
  GitOwner: "<from-session>"
  GitRepo: "<from-session>"
  DevName: "<from-session>"
  DevEmail: "<from-session>"
```

**Invariants:** `WORKTREE_PATH` is MANDATORY — no exceptions. If empty: FATAL ERROR → FLAG DEV → HALT.

## Parallel Dispatch Constraints

| Constraint | Reason |
|------------|--------|
| Separate worktree per issue | Isolation prevents file conflicts |
| No shared working directories | Prevents merge conflicts in worktrees |
| Conflict-risk issues NEVER parallelized | Even with worktrees, same-file edits cause conflicts |
| Wait for serial phase completion | Must-precede dependency must complete before dependents start |
| Report ONCE after all issues | Reduce noise, give developer complete picture |
| Dependency merge before work | Later issues merge prior branches, not branch-from-prior |
| Frozen branches after merge | No rebasing or amending once merged into a dependent |

## Red Flags

**Never:**

- Dispatch conflict-risk issues in parallel
- Create multiple issues in the same worktree
- Skip serial dependencies (must-precede)
- Skip dependency merge for dependent issues
- Include meta/non-code issues in implementation dispatch
- Report completion per issue (report ONCE after ALL)
- Create PRs for individual batch issues without explicit instruction
- Skip verification gates after all issues complete
- Rebase, amend, or force-push a frozen branch

**Always:**

- Use `using-git-worktrees` for each issue's workspace
- Present the complete execution plan to the developer before starting
- Execute must-precede issues first
- Merge prior issue branches into dependent branches before work
- Group independent issues for parallel dispatch
- Wait for all subagents in a parallel group before proceeding
- Compose AI-driven prior_context for each dependent issue
- Run all mandatory post-implementation gates after ALL issues
- Squash-merge feature branches into a single batch branch for the PR
- Exclude non-actionable issues with documented reason
