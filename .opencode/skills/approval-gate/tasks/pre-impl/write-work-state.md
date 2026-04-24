# Task: write-work-state

## Purpose

Determine execution strategy, capture the dev base hash, build dispatch context for parallel issues, and write the work state file that persists the execution plan for sub-agent dispatch.

## Entry Criteria

- Dependency graph built (from `build-dependency-graph`)
- Cross-spec overlap check complete (from `check-cross-spec-overlap`)
- All issues classified with execution order determined

## Exit Criteria

- Execution strategy determined (sequential, parallel, hybrid, exclude, or reduce-scope)
- Dev base hash captured via `git rev-parse origin/dev`
- Dispatch context built for each issue (including worktree paths, partially-implemented context, revised status)
- Work state file written to `.opencode/tmp/work-<timestamp>.md`
- File contains: authorization context, scope fields, pre-analysis results, gate evidence audit table, execution order, merge-time ordering, completed tracking, and results placeholder

## Procedure

### Step 5: Determine Execution Strategy

| Strategy | When | How |
|----------|------|-----|
| **Sequential** | Must-precede chain exists | Execute in dependency order |
| **Parallel** | Independent issues | Dispatch via `divide-and-conquer` |
| **Hybrid** | Mix of both | Serial for must-precede, parallel for independent groups |
| **Exclude** | Meta/non-code, already-implemented, superseded, moot | Report exclusion with reason |
| **Reduce scope** | Partially-implemented | Include remaining phases only |

### Step 7: Capture Dev Base Hash (Before Dispatch)

Before dispatching any parallel worktrees, the orchestrating agent MUST capture the current dev branch hash:

```bash
git rev-parse origin/dev
```

This `dev_base_hash` MUST be included in the dispatch context for each parallel issue. See Step 8 for the complete dispatch context schema.

### Step 8: Dispatch Context for Parallel Issues

For each issue in a parallel-safe group, the dispatch context MUST include worktree information:

```yaml
issue: <number>
branch: "spec/<short-name>"
worktree_path: ".worktrees/spec-<short-name>"
dev_base_hash: "<7-char-sha>"
env_vars:
  worktree.path: ".worktrees/spec-<short-name>"
  branch: "spec/<short-name>"
  github.owner: "<from-session>"
  github.repo: "<from-session>"
  dev.name: "<from-session>"
  dev.email: "<from-session>"
```

The `worktree_path` is derived from the branch name by replacing `/` with `-`:

- Branch `spec/foo` → Worktree path `.worktrees/spec-foo`
- Branch `feature/bar` → Worktree path `.worktrees/feature-bar`

The `dev_base_hash` ensures all parallel worktrees start from the same base commit on `dev`.

**For partially-implemented issues**, include additional context:

```yaml
  partially_implemented: true
  completed_phases: [1]
  completed_by_pr: "#M"
  remaining_phases: [2, 3]
```

**For issues with REVISED status**, include:

```yaml
  revised_status: true
  spec_version: "current revised body"
```

### Step 9: Write Work State File

After the execution plan is presented, write a work state file that persists the plan for sub-agent dispatch:

```bash
mkdir -p .opencode/tmp
```

**File:** `.opencode/tmp/work-<timestamp>.md`

**Contents:**

```markdown
# Work Execution Plan

**Session:** <timestamp>
**Authorized Issues:** #A, #B, #C
**Authorization Context:** User said "approved" on <date>
**Authorization Scope:** <scope_value> (parsed from authorization text)
**HALT At:** <pipeline_stage> (derived from scope horizon)
**PR Strategy:** stacked | individual | none (derived from scope)

## Scope Fields

- **authorization_scope:** <scope_value>
- **halt_at:** <pipeline_stage>
- **pr_strategy:** <stacked|individual|none>
- **gap_fill:** <list of gap-fill actions executed or pending>

## Pre-Analysis Results

| Issue | Screening | Details |
|-------|-----------|---------|
| #A | Included | — |
| #D | Excluded | already-implemented (PR #M) |
| #E | Scope-reduced | phase 1 done by PR #M; phases 2, 3 remaining |

## Gate Evidence Audit Table

| Issue # | Sub-issues Enumerated? (Gate 1) | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? (Gate 2) | All Criteria Verified vs Codebase? | Final Classification |
|---------|----------------------------------|--------------------------|-------------------------------|--------------------------------------|-----------------------------------|---------------------|
| #D | ✅ | ✅ | ✅ | ✅ | ✅ | already-implemented |

## Execution Order

1. #A — <title> (touches <files>)
2. #B — <title> (depends on #A, touches <files>)
3. #C — <title> (independent, touches <files>)

## Merge-Time Ordering

- #C will rebase onto `dev` after #A merges before creating its PR.

## Completed

- [ ] #A — branch: <name>, status: pending
- [ ] #B — branch: <name>, status: pending
- [ ] #C — branch: <name>, status: pending

## Results

(Agent appends completion summaries here as issues finish)
```

**Key properties:**

- Session-scoped via timestamp — stale files are detectable
- Survives context turnover — agent can re-read after HALT
- Hybrid: in-line context passed to each sub-agent + file backup for recovery
- Cleaned up after work set completes (or on new session start)

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`

## Work State I/O

- **Reads from:** `## build-dependency-graph`, `## check-cross-spec-overlap`
- **Writes to:** `## write-work-state`

After completing this task, write results to the work state file under section `## write-work-state` using the YAML format defined in `enforcement/work-state-schema.md`.