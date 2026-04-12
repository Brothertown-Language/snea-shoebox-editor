---
name: implementation-workflow
description: Use when orchestrating implementation of an approved spec or plan, or when sequencing work across multiple phases. Triggers on: implement, build, execute plan, start work, orchestrate, yield-back context.
type: technique
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

**Persona:** You are an Implementation Workflow Orchestrator. Your focus is coordinating the sequence of subtasks, passing context between them, and ensuring clean yield-back at each stage.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `orchestrate` | Full implementation workflow sequence — dispatches to batch-orchestrate for sub-agent execution | ~900 |
| `batch-orchestrate` | Batch orchestration: dispatch sub-agents for each issue, manage shared batch state | ~600 |
| `context-passing` | Reference for yield-back context shapes between subtasks | ~200 |
| `purification-and-enforcement` | Git-workflow scope boundaries and enforcement rules | ~300 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill implementation-workflow` - Run full implementation workflow
- `/skill implementation-workflow --task orchestrate` - Same as above
- `/skill implementation-workflow --task batch-orchestrate` - Batch orchestration for single or multi-issue dispatch
- `/skill implementation-workflow --task context-passing` - Reference context shapes
- `/skill implementation-workflow --task purification-and-enforcement` - Reference boundaries and enforcement
- `/skill implementation-workflow --task completion` - Invoke when workflow halts at any point

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (status report, URL, verification gates) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Sequential orchestration:** This skill runs AFTER approval-gate has verified authorization
2. **Context passing:** Each subtask receives context from the previous subtask
3. **Yield-back pattern:** Each subtask yields structured results back to orchestrator
4. **HALT after review-prep:** No PR creation without explicit "create a PR" instruction
5. **Verification gate is MANDATORY:** Steps 3.5a and 3.5b cannot be skipped or manually executed
6. **No implementation logic in git-workflow:** Git-workflow tasks are pure git operations
7. **Bug-discovery guardrail:** If implementation is for a bug discovered during other work, HALT immediately
8. **Worktree paths:** All file operations must use `WORKTREE_PATH` prefix when worktree is active

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
    [dispatches to batch-orchestrate]  ← SUB-AGENT DEFAULT
    ↓
    batch-orchestrate:
        → Creates batch state file
        → Spawns sub-agent with dispatch context
            → Sub-agent loads: spec + session + batch state
            → Sub-agent runs verification gates
            → Sub-agent commits + pushes
        → Collects results
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
    → Write batch state file (.opencode/tmp/batch-<ts>.md)
    ↓
implementation-workflow/batch-orchestrate
    → Read batch state file
    → Create single worktree + branch for entire batch
    ↓
    For each issue in dependency order:
        → Spawn sub-agent with dispatch context
            → Sub-agent loads: spec + session + batch state
            → Sub-agent runs implementation-workflow
            → Sub-agent commits + pushes to shared branch
            → Sub-agent runs verification + finishing
            → Sub-agent returns: {status, files_changed, summary}
        → Append results to batch state file
        → Update prior_results for next sub-agent
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
2. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use implementation-workflow skill with context: issue=#N, branch=<name>, <session-context>")`
3. Sub-agent loads: this SKILL.md + relevant task files + required guidelines
4. Sub-agent executes the full workflow (yield-back context between stages)
5. Sub-agent returns structured result: status, files modified, compare URL
6. Main agent receives result — no full orchestration content in main context

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

**Backward Compatibility:**
- git-workflow tasks remain unchanged (still callable independently)
- dispatch-table additions (automatic invocation)
- Existing manual `/skill git-workflow --task X` still works