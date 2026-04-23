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
model_context: "<ollama-cloud-model-tag>"
env_vars:
  worktree.path: "<worktree path>"
  branch: "<branch name>"
  github.owner: "<from-session>"
  github.repo: "<from-session>"
  dev.name: "<from-session>"
  dev.email: "<from-session>"
```

**MANDATORY verification items before dispatch:**
- `worktree.path` is non-empty — FATAL if missing
- `branch` matches the feature branch for this sub-task
- `depth` is less than `max_depth`

**Model context:** The `model_context` field specifies the Ollama Cloud model for UI sub-agents (e.g., `kimi-k2.6:cloud` for `ui-design`, `glm-5.1:cloud` for `ui-engineer`). Use an empty string for non-UI tasks (default model).

### Step 2: Spawn Sub-agent

```python
task(
    subagent_type="general",
    prompt="""
Use divide-and-conquer skill with context:

worktree.path: <value>
If worktree.path is set, all file operations and git commands MUST use it as the base directory.

Model context: <value from model_context field, or "default" if empty>

Sub-task: <description from dispatch context>
Scope: <scope>
Boundaries: <boundaries — do NOT exceed these>
Spec: <relevant spec section>

 Mandatory gates before returning:
 1. verification-before-completion --task verify
 2. finishing-a-development-branch --task checklist
 3. git-workflow --task review-prep
 4. Commit and push to branch (**MANDATORY — do NOT return without committing and pushing**)
 
 If you cannot commit (e.g., conflicts): return status: BLOCKED with explanation.

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

### Step 4: Sub-Agent Completion Checkpoint

After collecting the sub-agent result, the orchestrator MUST perform a completion checkpoint before proceeding:

1. **If sub-agent returned a structured result** — check `status` field:
   - `DONE` → normal, proceed to Step 5
   - `DONE_WITH_CONCERNS` → review concerns, proceed if OK
   - `OVERFLOW` → handle per `overflow-signal` task
   - `BLOCKED` → HALT and report blocker

2. **If sub-agent returned NO result** (timeout, crash, empty response) — this is **ABNORMAL TERMINATION**:
   a. Run `git status` in the worktree (`workdir=worktree.path`)
   b. If working tree is clean → sub-agent didn't start → re-dispatch (return to Step 2)
   c. If working tree has uncommitted changes → assess the changes:
      - `git diff` and `git diff --cached` to see what was modified
      - Compare changed files against the dispatch spec deliverables
      - Determine completion level: complete / partial / wrong
      - Apply recovery action per the decision matrix in SKILL.md "Sub-Agent Completion Checkpoint" section
    d. Report abnormal termination to chat (see reporting format in SKILL.md)
    e. Do NOT proceed to next task until recovery is complete

**The orchestrator decides the recovery action autonomously.** Per the "Pushing Agent Intelligence Decisions to the User" critical violation (`000-critical-rules.md`), the recovery decision is an agent intelligence concern. The user is NOT asked to decide. UNDO + re-dispatch is the default; manual completion is a narrow exception (see SKILL.md Recovery Mode for conditions).

### Step 5: Compose Prior Context

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
6. **Commit and push to feature branch (MANDATORY self-commit protocol)** — sub-agents MUST commit their own work before returning. Steps:
   a. `git add -A` (stage all changes)
   b. `git commit -m "<descriptive message>"` with co-authored-by trailer
   c. `git push -u origin <branch>`
   d. THEN return structured result
   If a sub-agent cannot commit (e.g., conflicts), it MUST return `status: BLOCKED` with an explanation.
7. Return structured result per Sub-agent Result Contract (including compare_url and exec_summary)
8. Signal OVERFLOW if work exceeds capacity (per Overflow Signal Contract)

## Edge Cases

### Sub-agent Fails

Record failure with details. For independent sub-tasks, continue to next. For dependent sub-tasks, skip dependents and report both.

### Sub-agent Discovers Bug

Sub-agent reports bug as finding (read-only), HALTs implementation for its sub-task. Orchestrator records and reports in work summary. Bug discovery does NOT authorize fixing.
## Live Verification: Dispatch Claims (MANDATORY)

**Verify dispatch state claims against actual sub-agent results per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Sub-agent completed" | Verify result contract returned | Check for result contract in context | VERIFICATION-GAP |
| "worktree.path passed" | Verify worktree path in dispatch context | Check dispatch prompt for worktree.path | STRUCTURE-VIOLATION |
| "Sub-agent stayed in worktree" | Verify sub-agent didn't modify main repo | `git -C <main-repo> status --porcelain` | CONFLICTING |

**Evidence artifact:** Result contract presence and main repo cleanliness check.
## Enforcement References
-  Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
-  Result validation: see `enforcement/result-validation.md`
-  Overflow signal: see `enforcement/overflow-signal.md`
