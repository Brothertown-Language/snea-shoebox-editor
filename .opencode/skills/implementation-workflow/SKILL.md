______________________________________________________________________

## name: implementation-workflow description: Use when orchestrating implementation of an approved spec or plan, or when sequencing work across multiple phases. Triggers on: implement, build, execute plan, start work, orchestrate, yield-back context. type: technique license: MIT compatibility: opencode

# Skill: implementation-workflow

## Overview

Orchestration layer that coordinates the implementation workflow by dispatching sub-agents per issue with branch-per-issue and merge-based dependency resolution. Each issue gets its own feature branch and worktree; dependent issues merge prior branches before starting work; all branches are squash-merged into a single batch branch for the final PR.

**Architecture:**

- `implementation-workflow` (orchestration) → calls → `git-workflow` tasks (git ops only)
- `implementation-workflow` → dispatches → sub-agent per issue (actual work)
- `git-workflow` tasks → yield → context back to orchestrator
- Each issue: separate branch → separate worktree → merge dependencies → implement → verify → push
- Batch assembly: squash-merge each feature branch into batch branch → single PR

**Source Attribution:** This skill addresses the yield-back coordination gaps identified in issue #77 and #68.

**Persona:** You are an Implementation Workflow Orchestrator. Your focus is coordinating the sequence of subtasks, passing context between them, and ensuring clean yield-back at each stage.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `orchestrate` | Full implementation workflow sequence — dispatches to batch-orchestrate for sub-agent execution | ~900 |
| `batch-orchestrate` | Batch orchestration: branch-per-issue, merge dependencies, squash-merge into batch branch | ~600 |
| `context-passing` | Reference for yield-back context shapes between subtasks | ~200 |
| `purification-and-enforcement` | Git-workflow scope boundaries and enforcement rules | ~300 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill implementation-workflow` - Run full implementation workflow
- `/skill implementation-workflow --task orchestrate` - Same as above
- `/skill implementation-workflow --task batch-orchestrate` - Batch orchestration: branch-per-issue, merge dependencies, single batch PR
- `/skill implementation-workflow --task context-passing` - Reference context shapes
- `/skill implementation-workflow --task purification-and-enforcement` - Reference boundaries and enforcement
- `/skill implementation-workflow --task completion` - Invoke when workflow halts at any point

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (status report, URL, verification gates) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Sequential orchestration:** This skill runs AFTER approval-gate has verified authorization
1. **Context passing:** Each subtask receives context from the previous subtask
1. **Yield-back pattern:** Each subtask yields structured results back to orchestrator
1. **HALT after review-prep:** No PR creation without explicit "create a PR" instruction
1. **Verification gate is MANDATORY:** Steps 3.5a and 3.5b cannot be skipped or manually executed
1. **No implementation logic in git-workflow:** Git-workflow tasks are pure git operations
1. **Bug-discovery guardrail:** If implementation is for a bug discovered during other work, HALT immediately
1. **Worktree paths:** All file operations must use `WORKTREE_PATH` prefix when worktree is active
1. **Always batch mode:** Single issue = batch of one, no special-case path
1. **Branch per issue:** Each issue gets its own feature branch and worktree; dependent issues merge prior branches
1. **Frozen branches:** Once a prior branch is merged into a dependent, it is frozen (no rebase/amend/force-push)

## Interdependency Chain

```
User: "#77 approved" (single issue)
    ↓
approval-gate (dispatch table invoked)
    YIELDS: {issue: N, authorized: true, context: {...}}
    ↓
implementation-workflow/orchestrate (receives auth context)
    ↓
    [calls git-workflow --task pre-work]
    YIELDS: {branch: "spec/X", status: "ready"}
    ↓
    [dispatches to batch-orchestrate]
    ↓
    batch-orchestrate:
        → Create feature branch + worktree for issue (BASE_BRANCH=dev)
        → Spawn sub-agent with dispatch context (prior_context + dependency_branches)
            → Sub-agent loads: spec + session + prior context
            → Sub-agent runs verification gates
            → Sub-agent commits + pushes to feature branch
        → Collect results, compose prior_context for next issue
    ↓
    [batch assembly: squash-merge feature branch into batch branch]
    ↓
    [calls git-workflow --task review-prep]
    YIELDS: {compare_url: "...", exec_summary: "..."}
    ↓
    HALT (chat shows URL + summary)
```

```
User: "#690 #591 approved" (multi-issue batch)
    ↓
approval-gate/batch-approval-analysis
    → Classify, plan
    → Determine execution order (must-precede chains, parallel-safe groups)
    ↓
implementation-workflow/batch-orchestrate
    → Create feature branches + worktrees per issue
    → For each issue in dependency order:
        → If dependent: merge prior issue branch into current branch
        → Spawn sub-agent with dispatch context (prior_context + dependency_branches)
            → Sub-agent loads: spec + session + prior context
            → Sub-agent runs implementation-workflow in own branch
            → Sub-agent commits + pushes to own feature branch
            → Sub-agent runs verification + finishing
            → Sub-agent returns: {status, files_changed, summary}
        → Compose prior_context for next sub-agent (intent-and-context, not change summary)
        → Mark prior branch as frozen
    ↓
    [batch assembly: squash-merge each feature branch into batch branch]
    ↓
    [calls git-workflow --task review-prep]
    YIELDS: {compare_url: "...", exec_summary: "..."}
    ↓
    HALT (chat shows URL + summary)
```

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

## Platform Compatibility

- **GitHub:** Uses GitHub MCP tools for git operations
- **GitBucket:** Uses GitBucket Python API client for git operations
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Sub-Agent Spawning

This skill is a **heavy skill** — its orchestration logic can run in isolation. When the main agent needs full workflow execution, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~656 words)
1. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use implementation-workflow skill with context: issue=#N, branch=<name>, <session-context>")`
1. Sub-agent loads: this SKILL.md + relevant task files + required guidelines
1. Sub-agent executes the full workflow (yield-back context between stages)
1. Sub-agent returns structured result: status, files modified, compare URL
1. Main agent receives result — no full orchestration content in main context

**Sub-agent context parameters:** Pass issue number, `WORKTREE_PATH`, `BRANCH_NAME`, `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL` from session init.

## Cross-References

- Related skills: `git-workflow` (git ops), `approval-gate` (authorization), `subagent-driven-development` (alternative orchestration for independent tasks)
- Related guidelines: `010-approval-gate.md`, `110-git-branch-first.md`
- Related dispatch: `dispatch-table.yaml` (approval-gate → implementation-workflow sequence)

## Migration from Old Architecture

| Old (git-workflow) | New (implementation-workflow) |
|--------------------|-------------------------------|
| git-workflow contains implementation logic | Implementation logic moved to subagent |
| No orchestration layer | implementation-workflow orchestrates |
| No context passing | Yield-back pattern between subtasks |
| Redundant auth checks | Auth check only in approval-gate |

**Migration from Previous Batch Architecture:**

| Old (batch-orchestrate) | New (batch-orchestrate) |
|-------------------------|-------------------------|
| Single shared branch for entire batch | Branch per issue |
| `prior_results` = change summary template | `prior_context` = AI-composed intent-and-context |
| Batch state file (`.opencode/tmp/batch-*.md`) | Git history + issue metadata |
| Single-issue dispatch edge case | Always batch mode (batch of one) |
| No dependency merge | Merge prior branches into dependent branches |
| All commits on one branch | Squash-merge each feature branch into batch branch |

**Backward Compatibility:**

- git-workflow tasks remain unchanged (still callable independently)
- dispatch-table additions (automatic invocation)
- Existing manual `/skill git-workflow --task X` still works
