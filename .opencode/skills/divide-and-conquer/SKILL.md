---
name: divide-and-conquer
description: Use when implementing an approved spec, orchestrating sub-agents, or when a task risks context window overflow. Triggers on: implement, build, orchestrate, context overflow, decompose, dispatch subagent, batch execution.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Divide and Conquer

## Overview

Enforces context window safety by mandating pre-flight assessment before non-trivial implementation. When a task risks overflow, it MUST be decomposed into sub-tasks and dispatched to sub-agents. The orchestrator is a pure coordinator — it never edits implementation files directly. Only trivial single-file fixes skip assessment.

**Source Attribution:** This skill addresses the context window overflow patterns identified in issue #734. Decomposition and dispatch patterns adapted from `implementation-workflow` (batch-orchestrate, context-passing, purification-and-enforcement).

**Persona:** You are a Divide and Conquer Orchestrator. Your focus is assessing context fitness, decomposing work into safe units, dispatching sub-agents with scoped instructions, and aggregating results — never implementing directly.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `assess` | Pre-flight context-fit assessment — determine workload sizing for sub-agent dispatch | ~300 |
| `decompose` | Split a task into sub-tasks with dispatch context, preserve spec boundaries | ~300 |
| `dispatch` | Spawn sub-agent with scoped instructions and collect structured result | ~250 |
| `overflow-signal` | Structured OVERFLOW response protocol for sub-agents that can't fit the work | ~200 |
| `merge` | Combine sub-agent results into final output, pure aggregation | ~150 |
| `context-passing` | Reference for dispatch context shapes between orchestrator and sub-agents | ~200 |
| `purification-and-enforcement` | Scope boundaries and enforcement rules for the orchestration layer | ~250 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~150 |
| `orchestrate` | Full workflow: assess → decompose → dispatch → merge → completion | ~400 |
| `assemble-batch` | Batch assembly: squash-merge feature branches into batch branch | ~200 |

## Invocation

- `/skill divide-and-conquer` - Overview only
- `/skill divide-and-conquer --task assess` - Pre-flight context-fit assessment
- `/skill divide-and-conquer --task decompose` - Split task into sub-tasks
- `/skill divide-and-conquer --task dispatch` - Spawn sub-agent with scoped instructions
- `/skill divide-and-conquer --task overflow-signal` - Handle OVERFLOW from sub-agent
- `/skill divide-and-conquer --task merge` - Combine sub-agent results
- `/skill divide-and-conquer --task context-passing` - Reference dispatch context shapes
- `/skill divide-and-conquer --task purification-and-enforcement` - Reference boundaries
- `/skill divide-and-conquer --task completion` - Invoke when workflow halts
- `/skill divide-and-conquer --task orchestrate` - Full workflow
- `/skill divide-and-conquer --task assemble-batch` - Batch branch assembly

**COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Pre-flight assessment is MANDATORY** before any non-trivial task. Run `--task assess` first. Skipping assessment for non-trivial work is a CRITICAL violation.
2. **No direct implementation** — the orchestrator NEVER implements directly. All implementation goes through `assemble-batch` as sub-agent dispatch. Single issue = batch of one sub-agent. No IMPLEMENT_DIRECTLY path.
3. **AI-driven sizing** — assessment informs workload sizing (single sub-agent vs multiple), not whether to dispatch. All work goes through sub-agents.
4. **Recursive sub-delegation** — sub-agents receiving decomposed work CAN signal OVERFLOW if their portion still exceeds capacity. The orchestrator receives the signal and decomposes further.
5. **Depth limit** — maximum decomposition depth configurable via `DIVIDE_AND_CONQUER_MAX_DEPTH` (default: 3). At max depth, HALT and report to user. Depth is tracked in the Dispatch Context Contract.
6. **Orchestrator controls all spawning** — sub-agents never self-spawn. Only the orchestrator dispatches via `--task dispatch`. Sub-agents that need further decomposition return OVERFLOW; the orchestrator handles it.
7. **Main agent is pure orchestrator** — never edits implementation files directly. Implementation happens only inside sub-agents. Violating this is a CRITICAL violation.
8. **Branch per issue** — each issue gets its own feature branch and worktree. No shared branches across issues.
9. **Frozen branches** — once a prior branch is merged into a dependent, it is frozen (no rebase, amend, or force-push).
10. **Verification gate remains mandatory** — sub-agents MUST run `verification-before-completion --task verify` and `finishing-a-development-branch --task checklist` before returning results. Orchestrator enforces this in dispatch context.
11. **Stacking is a prerequisite, not a preference** — feature branches MUST be stacked sequentially (merge-based dependency resolution) as the prerequisite approach. Parallel sub-agent dispatch is OPPORTUNISTIC — it depends on circumstances genuinely allowing it (truly independent codepaths, no shared files, no hidden dependencies). When in doubt, stack.
12. **Completion guarantee** — idempotent completion on any halt. Invoke `--task completion` before halting regardless of outcome.

## Overflow Signal Contract

When a sub-agent determines it cannot fit the assigned work within its context window, it MUST return:

```yaml
status: OVERFLOW
completed_work:
  description: "<what was accomplished before overflow>"
  files_changed: ["<path>"]
  summary: "<result of completed portion>"
remaining_work:
  description: "<what still needs doing>"
  scope: "<files, functions, modules affected>"
  spec_references: ["<spec section IDs>"]
suggested_splits:
  - description: "<sub-task 1>"
    scope: "<files/modules>"
  - description: "<sub-task 2>"
    scope: "<files/modules>"
depth: <current depth>
```

## Dispatch Context Contract

When the orchestrator dispatches a sub-agent, it MUST pass:

```yaml
issue: <number>
branch: "spec/<short-name>"
spec: "<full spec body or relevant section>"
plan_issue: <number or empty>
authorization: "User approved #<N> on <date>"
depth: <current decomposition depth, starting at 0>
max_depth: <DIVIDE_AND_CONQUER_MAX_DEPTH or 3>
prior_context: "<AI-composed intent and context from prior sub-agents>"
decision_log_reference: "<URL or reference to the Decision Log on the Plan issue, or 'see Decision Log on Plan #N' — the sub-agent can retrieve full decision history from this reference>"
phase_progress:
  completed_phases: "<prose listing of completed phases by concern name, not just number>"
  concern_boundaries_crossed: "<prose description of architectural concern transitions encountered>"
  verification_evidence: "<prose summary of what was verified and the outcomes>"
sub_task:
  description: "<what this sub-agent must implement>"
  scope: "<files, modules, functions>"
  boundaries: "<what is OUT of scope>"
env_vars:
  WORKTREE_PATH: "<worktree path>"
  BRANCH_NAME: "<branch name>"
  GIT_OWNER: "<from-session>"
  GIT_REPO: "<from-session>"
  DEV_NAME: "<from-session>"
  DEV_EMAIL: "<from-session>"
```

**Phase progress is prose-driven.** The `phase_progress` section communicates what information must travel between phases — completed phases should be named by the concern they address, concern boundaries should describe the architectural transition point, and verification evidence should summarize what was confirmed and the outcome. The agent composing the context decides how to encode this; the requirement is the information, not the format.

**Invariants:** `WORKTREE_PATH` is MANDATORY — no exceptions. If empty: FATAL ERROR → HALT. `plan_issue` is set when dispatched from plan approval flow. `phase_progress` is composed by the orchestrator from prior sub-agent results and the Plan STATUS marker — it accumulates across the batch as each issue completes.

## Sub-agent Result Contract

Every sub-agent MUST return a structured result:

```yaml
status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
files_changed: ["<path>"]
summary: "<what was implemented and key decisions>"
concerns: "<only if DONE_WITH_CONCERNS>"
decision_log_entry: "<prose summary of design decisions made during this phase — no prescribed format, the agent decides structure>"
plan_issue: <number or empty>
phase_progress:
  completed_phases: "<prose listing of phases completed, named by concern>"
  concern_boundaries_crossed: "<prose description of architectural concern transitions>"
  verification_evidence: "<prose summary of what was verified and outcomes>"
verification_passed: true | false
compare_url: "<compare URL from review-prep, or empty string>"
exec_summary: "<1-2 sentence executive summary for chat output, or empty string>"
```

**Phase progress in results** enables the orchestrator to compose `phase_progress` for subsequent sub-agents. The completed phases, concern boundaries crossed, and verification evidence from prior sub-agent results feed directly into the next dispatch context's `phase_progress` field.

**Decision Log persistence.** The `decision_log_entry` field captures design decisions made during a phase. After each sub-agent returns, the orchestrator appends this entry as a dedicated GitHub Issue comment on the Plan issue — this is the Decision Log. It persists across session restarts because it lives on the GitHub Issue, not in transient agent context. The Decision Log uses comments (not Plan body edits) for lightweight, append-only durability. The `decision_log_entry` is prose-driven — no prescribed format, the agent decides the structure that best communicates what was decided and why.

## Worktree Mode

When `WORKTREE_PATH` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `WORKTREE_PATH`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `WORKTREE_PATH/`
- `git` commands run from the worktree directory, NOT the main repo

If `WORKTREE_PATH` is NOT set, operate normally from the project root.

## Sub-Agent Spawning

This skill is a **heavy skill** — its orchestration logic can run in isolation. When the main agent needs divide-and-conquer execution, spawn a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~650 words)
2. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use divide-and-conquer skill with context: issue=#N, branch=<name>, <session-context>")`
3. Sub-agent loads: this SKILL.md + relevant task files + required guidelines
4. Sub-agent executes: assess → decompose → dispatch → merge → completion
5. Sub-agent returns structured result per Sub-agent Result Contract
6. Main agent receives result — no orchestration detail in main context

**Sub-agent context parameters:** Pass `WORKTREE_PATH`, `BRANCH_NAME`, `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL` from session init.

## Cross-References

- Related skills: `subagent-driven-development` (task-level isolation with two-stage review), `git-workflow` (git ops), `approval-gate` (authorization), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `using-git-worktrees` (worktree creation)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`
- Adapted from: `implementation-workflow` (batch-orchestrate, context-passing, purification-and-enforcement, completion)

Co-authored with AI: <AI-Name> (<model-id>)