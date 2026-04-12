# Task: batch-orchestrate

## Purpose

Orchestrate batch implementation by dispatching sub-agents for each approved issue, managing shared batch state, and ensuring no HALTs between issues. This task makes the main agent a pure orchestrator that never edits implementation files directly.

## Entry Criteria

- Approval-gate has verified authorization for one or more issues
- Batch state file exists (for multi-issue) or single-issue dispatch context is available
- Worktree is created and ready

## Exit Criteria

- All issues in batch have been implemented via sub-agents
- Each sub-agent ran verification + finishing before returning
- Batch state file updated with results for all completed issues
- Compare URL generated, executive summary in chat
- HALT after review-prep (no PR creation without explicit instruction)

## Procedure

### Step 1: Initialize Batch State

**For single-issue dispatch:**
- Read the issue spec from GitHub
- Create a minimal batch state file: `.opencode/tmp/batch-<timestamp>.md`
- Determine complexity level (simple/moderate/complex)

**For multi-issue dispatch:**
- Read batch state file from batch-approval-analysis output
- Verify all authorized issues are listed
- Determine execution order from dependency analysis

**Batch state file format:**
```markdown
# Batch Execution Plan

**Session:** <timestamp>
**Authorized Issues:** #A, #B, #C
**Authorization Context:** User said "approved" on <date>

## Execution Order

1. #A — <title> (touches <files>)
2. #B — <title> (depends on #A, touches <files>)
3. #C — <title> (independent, touches <files>)

## Completed

- [ ] #A — branch: <name>, status: pending
- [ ] #B — branch: <name>, status: pending
- [ ] #C — branch: <name>, status: pending

## Results

(Agent appends completion summaries here as issues finish)
```

### Step 2: Determine Dispatch Context

For each issue in the batch, determine the dispatch context:

```yaml
batch:
  plan_file: ".opencode/tmp/batch-<timestamp>.md"
  authorized_issues: [#A, #B, #C]
  completed_issues: [<completed>]  # populated as batch progresses
  prior_results: "<summary of prior issues' changes>"
issue: #<current>
spec: "<full spec body from GitHub Issue>"
authorization: "User approved #A, #B, #C on <date>"
env_vars:
  WORKTREE_PATH: ".worktrees/spec-<name>"
  BRANCH_NAME: "spec/<name>"
  GIT_OWNER: "<from-session>"
  GIT_REPO: "<from-session>"
  DEV_NAME: "<from-session>"
  DEV_EMAIL: "<from-session>"
```

**Complexity determines context richness:**

| Complexity | Context Level | Rationale |
|------------|---------------|-----------|
| Simple (≤3 files, obvious fix) | Minimal: issue + spec + env | Fast, isolated |
| Moderate (multi-file, some interfaces) | Standard: + batch state file path | Needs full spec context |
| Complex (multi-phase, architectural) | Full: + prior_results summary | Must adapt to prior changes |

### Step 3: Dispatch Sub-Agent for Each Issue

**For each issue in execution order:**

1. **Build dispatch context** with accumulated `prior_results` from previously completed issues
2. **Spawn sub-agent** via `task(subagent_type="general", prompt=...)`
3. **Sub-agent responsibilities:**
   - Load spec + session context + batch state
   - Run `implementation-workflow` skill for the specific issue
   - Make WIP commits as needed
   - Run `verification-before-completion --task verify`
   - Run `finishing-a-development-branch --task checklist`
   - Return structured result: `{status, files_changed, summary}`
4. **Collect result** from sub-agent
5. **Update batch state file:**
   - Mark issue as completed
   - Append summary to Results section
   - Update `prior_results` for next sub-agent
6. **Handle failures:**
   - If sub-agent fails: record failure in batch state
   - For independent issues: continue to next issue
   - For must-precede chains: skip dependent issues, report both
7. **Continue** to next issue

**Sub-agent prompt template:**
```
You are an implementation sub-agent for issue #<N>.

Context:
- Batch plan file: <plan_file_path>
- Prior results: <prior_results_summary>
- Spec: <full_spec_body>
- Authorization: User approved <issues> on <date>

Environment:
- WORKTREE_PATH: <worktree_path>
- BRANCH_NAME: <branch_name>
- GIT_OWNER: <owner>
- GIT_REPO: <repo>

Your task:
1. Read the spec from the batch plan and issue
2. Use the implementation-workflow skill to implement the spec
3. Run verification-before-completion --task verify
4. Run finishing-a-development-branch --task checklist
5. Commit and push changes to the shared branch
6. Return: {status, files_changed, summary}
```

### Step 4: Post-Batch Review-Prep

After ALL issues in the batch complete:

1. **Verify all results** — check batch state for any failures
2. **Run git-workflow --task review-prep** for the single shared branch
3. **Collect compare URL**
4. **Clean up batch state file** if all issues succeeded

### Step 5: Report and HALT

**Chat output:**
```markdown
**Summary:**

Implemented <N> issues via sub-agent batch orchestration.

**Outcome:**

- #A: <summary> ✅
- #B: <summary> ✅
- #C: <summary> ⚠️ (partial — see details)

Compare URL: https://github.com/<owner>/<repo>/compare/dev...spec/<branch>
```

**Issue comments:**
Post completion comment on each issue ONLY if substantive (per `github-comments` skill Substantive Comment Gate). Skip comment for non-substantive completions.

**HALT condition:**
- Do NOT create PR
- Do NOT close issues
- Wait for explicit "create a PR" instruction

## Edge Cases

### Sub-Agent Failure

```
batch-orchestrate:
    → Dispatch sub-agent for #B
        → Sub-agent fails (error/timeout)
        → Record failure in batch state
    → If #B has dependents (#C requires #B): skip #C, report both
    → If #C is independent: continue with #C
    → After all possible issues complete:
        → Report failures clearly
        → HALT with partial results if any issues succeeded
```

### Sub-Agent Discovers Bug

```
batch-orchestrate:
    → Dispatch sub-agent for #B
        → Sub-agent discovers bug per bug-discovery protocol
        → Sub-agent reports bug as finding (read-only)
        → Sub-agent HALTs implementation for #B
        → Records: "#B halted — bug discovered at <location>"
    → Continue to next independent issue
    → Report bug in batch summary
```

### Session Restart Mid-Batch

```
batch-orchestrate:
    → Read batch state file
        → Find: #A completed, #B pending, #C pending
    → Authorization check: file contains auth context
    → Resume from #B (skip #A, already done)
    → Continue batch as normal
```

### Single-Issue Dispatch

```
batch-orchestrate:
    → Read issue spec
    → Create minimal batch state (single-item batch)
    → Create worktree
    → Spawn sub-agent with dispatch context
    → Sub-agent implements + verifies + pushes
    → Update batch state
    → review-prep → HALT
```

**Why?** Consistency. No special-casing. The agent always orchestrates, never implements. Context window stays clean for orchestration decisions.

## Mandatory Rules

1. **Main agent NEVER edits implementation files** — only orchestrates
2. **Every sub-agent runs verification + finishing** — no skipping
3. **One branch per batch** — all issues share one branch
4. **No HALTs between issues** — all issues complete before single HALT
5. **Batch state file is source of truth** — always read from file, not from memory
6. **Prior results accumulate** — each sub-agent receives summary of all prior changes
7. **Clean up batch state after completion** — remove file after PR is created