# Task: batch-execution

## Purpose

Accept a batch execution plan from `approval-gate --task batch-approval-analysis` and dispatch subagents according to the dependency order and parallelization strategy.

## Entry Criteria

- `batch-approval-analysis` has completed and produced an execution plan
- All issues in the plan are verified as authorized
- Worktrees are available for parallel execution

## Exit Criteria

- All serial phases executed in dependency order
- All parallel-safe groups dispatched simultaneously
- All issues completed with spec and quality reviews
- Non-actionable issues excluded with documented reason
- Final verification gates passed

## Procedure

### Step 1: Receive Execution Plan

The execution plan comes from `batch-approval-analysis` and contains:

- **Serial phases**: Issues that must execute in order (must-precede chains)
- **Parallel-safe groups**: Issues that can run simultaneously (no file overlap)
- **Excluded issues**: Meta/non-code issues not requiring implementation

### Step 2: Execute Serial Phases

For each issue in a serial phase:

1. Create worktree for the issue using `using-git-worktrees`
2. Dispatch implementer subagent per `implementer-prompt.md`
3. Run spec compliance review per `spec-reviewer-prompt.md`
4. Run code quality review per `code-quality-reviewer-prompt.md`
5. Mark issue complete
6. Proceed to next serial issue

### Step 3: Execute Parallel-Safe Groups

For each parallel-safe group:

1. Create a separate worktree for each issue in the group
2. Dispatch all implementer subagents simultaneously using `task` tool
3. Wait for all subagents to complete
4. Run spec review → code quality review for each
5. Mark all group issues complete

### Step 4: Handle Excluded Issues

For meta/non-code issues identified in the analysis:

1. Skip implementation entirely
2. Document the exclusion reason in chat
3. Include in final report with "Excluded: no code changes required"

### Step 5: Report Completion

After ALL phases and groups complete:

1. Invoke `verification-before-completion --task verify` (MANDATORY)
2. Invoke `finishing-a-development-branch --task checklist` (MANDATORY)
3. Invoke `git-workflow --task review-prep` (MANDATORY)
4. Report completion for ALL issues ONCE
5. HALT — do NOT create PR without explicit instruction

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

**Phase 2 (Parallel-safe group):**
- #662 (worktree: `.worktrees/spec/662-...`)
- #614 (worktree: `.worktrees/spec/614-...`)

**Phase 3 (After #630 completes):**
- #621 (worktree: `.worktrees/spec/621-...`)

**Excluded:**
- #660 — meta/behavioral issue (no code changes)

Proceeding with execution.
```

## Parallel Dispatch Constraints

| Constraint | Reason |
|------------|--------|
| Separate worktree per issue | Isolation prevents file conflicts |
| No shared working directories | Prevents merge conflicts in worktrees |
| Conflict-risk issues NEVER parallelized | Even with worktrees, same-file edits cause merge conflicts |
| Wait for serial phase completion | Must-precede dependency must complete before dependents start |
| Report ONCE after all issues | Reduce noise, give developer complete picture |

## Red Flags

**Never:**
- Dispatch conflict-risk issues in parallel
- Create multiple issues in the same worktree
- Skip serial dependencies (must-precede)
- Include meta/non-code issues in implementation dispatch
- Report completion per issue (report ONCE after ALL)
- Create PRs for individual batch issues without explicit instruction
- Skip verification gates after all issues complete

**Always:**
- Use `using-git-worktrees` for each issue's workspace
- Present the complete execution plan to the developer before starting
- Execute must-precede issues first
- Group independent issues for parallel dispatch
- Wait for all subagents in a parallel group before proceeding
- Run all mandatory post-implementation gates after ALL issues
- Exclude non-actionable issues with documented reason