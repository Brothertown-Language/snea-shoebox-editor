# Task: dispatch

## Purpose

Spawn a sub-agent with scoped instructions and collect its structured result. The orchestrator controls all spawning — sub-agents never self-spawn.

## Entry Criteria

- Sub-tasks are defined (from `decompose` task)
- Dispatch context is prepared per Dispatch Context Contract

## Exit Criteria

- Sub-agent returns a structured result per Sub-agent Result Contract
- Result is recorded for `merge` task

## Procedure

### Step 1: Build Dispatch Context

Assemble the Dispatch Context Contract (see SKILL.md):

```yaml
issue: <number>
branch: "spec/<short-name>"
spec: "<full spec body or relevant section>"
authorization: "User approved #<N> on <date>"
depth: <current depth>
max_depth: <DIVIDE_AND_CONQUER_MAX_DEPTH or 3>
prior_context: "<AI-composed intent from prior sub-agents>"
sub_task:
  description: "<what to implement>"
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

**MANDATORY verification items before dispatch:**
- `WORKTREE_PATH` is non-empty — FATAL if missing
- `BRANCH_NAME` matches the feature branch for this sub-task
- `depth` is less than `max_depth`

### Step 2: Spawn Sub-agent

```python
task(
    subagent_type="general",
    prompt="""
Use divide-and-conquer skill with context:

WORKTREE_PATH: <value>
If WORKTREE_PATH is set, all file operations and git commands MUST use it as the base directory.

Sub-task: <description from dispatch context>
Scope: <scope>
Boundaries: <boundaries — do NOT exceed these>
Spec: <relevant spec section>

Mandatory gates before returning:
1. verification-before-completion --task verify
2. finishing-a-development-branch --task checklist
3. git-workflow --task review-prep
4. Commit and push to branch

Return result in Sub-agent Result Contract format:
  status: DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED
  files_changed: [...]
  summary: ...
  verification_passed: true | false
  compare_url: "<URL or empty if not available>"
  exec_summary: "<1-2 sentence executive summary or empty>"

If context window overflow risk: return OVERFLOW per Overflow Signal Contract.
"""
)
```

### Step 3: Collect Result

Sub-agent MUST return per Sub-agent Result Contract:

| Status | Action |
| -- | -- |
| **DONE** | Record result, proceed to next sub-task |
| **DONE_WITH_CONCERNS** | Review concerns, address if about correctness/scope |
| **OVERFLOW** | Handle per `overflow-signal` task |
| **BLOCKED** | Provide context, escalate, or decompose further |

### Step 4: Compose Prior Context

After each successful sub-agent, compose intent-and-context for the next:

- Design decisions made
- Edge cases handled
- Assumptions that later sub-tasks depend on
- Interfaces exposed that later sub-tasks should use
- NOT a change summary (that's in git)

## Sub-agent Responsibilities

Each sub-agent MUST:
1. Load spec + session context + prior context
2. Implement only what is in the sub-task scope (respect boundaries)
3. Run `verification-before-completion --task verify`
4. Run `finishing-a-development-branch --task checklist`
5. Run `git-workflow --task review-prep`
6. Commit and push to feature branch
7. Return structured result per Sub-agent Result Contract (including compare_url and exec_summary)
8. Signal OVERFLOW if work exceeds capacity (per Overflow Signal Contract)

## Edge Cases

### Sub-agent Fails

Record failure with details. For independent sub-tasks, continue to next. For dependent sub-tasks, skip dependents and report both.

### Sub-agent Discovers Bug

Sub-agent reports bug as finding (read-only), HALTs implementation for its sub-task. Orchestrator records and reports in batch summary. Bug discovery does NOT authorize fixing.