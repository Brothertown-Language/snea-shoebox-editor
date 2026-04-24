---
name: divide-and-conquer
description: Use when implementing an approved spec, orchestrating sub-agents, or when a task risks context window overflow. Triggers on: implement, build, orchestrate, context overflow, decompose, dispatch subagent, work execution.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Divide and Conquer

## Overview

Enforces context window safety by mandating pre-flight assessment before non-trivial implementation. When a task risks overflow, it MUST be decomposed into sub-tasks and dispatched to sub-agents. The orchestrator is a pure coordinator — it never edits implementation files directly. Only trivial single-file fixes skip assessment.

**Source Attribution:** This skill addresses the context window overflow patterns identified in issue #734. Decomposition and dispatch patterns adapted from `implementation-workflow` (work-orchestrate, context-passing, purification-and-enforcement).

**Persona:** You are a Divide and Conquer Orchestrator. Your focus is assessing context fitness, decomposing work into safe units, dispatching sub-agents with scoped instructions, and aggregating results — never implementing directly.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `assess` | Pre-flight context-fit assessment — determine workload sizing for sub-agent dispatch | ≈300 |
| `decompose` | Split a task into sub-tasks with dispatch context, preserve spec boundaries | ≈300 |
| `dispatch` | Spawn sub-agent with scoped instructions and collect structured result | ≈250 |
| `completion-checkpoint` | Post-dispatch verification: detect abnormal termination, assess work, recover | ≈300 |
| `result-validation` | Post-dispatch result validation: empty/malformed result detection and fallback | ≈200 |
| `overflow-signal` | Structured OVERFLOW response protocol for sub-agents that can't fit the work | ≈200 |
| `merge` | Combine sub-agent results into final output, pure aggregation | ≈150 |
| `context-passing` | Reference for dispatch context shapes between orchestrator and sub-agents | ≈200 |
| `purification-and-enforcement` | Scope boundaries and enforcement rules for the orchestration layer | ≈250 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ≈150 |
| `orchestrate` | Full workflow: assess → decompose → dispatch → merge → completion | ≈400 |
| `assemble-work` | Work set assembly: squash-merge feature branches into work branch | ≈200 |
| `implementer-prompt` | Sub-agent prompt template: implementation context and instructions | ≈250 |
| `spec-reviewer-prompt` | Spec review stage prompt: two-stage review for spec compliance | ≈200 |
| `code-quality-reviewer-prompt` | Code quality review stage prompt: two-stage review for code quality | ≈200 |

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
- `/skill divide-and-conquer --task result-validation` - Post-dispatch result validation and fallback
- `/skill divide-and-conquer --task orchestrate` - Full workflow
- `/skill divide-and-conquer --task assemble-work` - Work set branch assembly
- `/skill divide-and-conquer --task two-stage-review` - Optional two-stage review pipeline (spec + code quality)

**COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Pre-flight assessment is MANDATORY** before any non-trivial task. Run `--task assess` first. Skipping assessment for non-trivial work is a CRITICAL violation.
2. **No direct implementation** — the orchestrator NEVER implements directly. All implementation goes through `assemble-work` as sub-agent dispatch. Single issue = work set of one sub-agent. No IMPLEMENT_DIRECTLY path.
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

## Pre-Dispatch Verification Checkpoint (MANDATORY)

**Before dispatching any sub-agent, the main agent MUST verify:**

1. **Worktree exists:** `git worktree list` shows the feature branch worktree
2. **worktree.path is set:** `echo $WORKTREE_PATH` returns a non-empty path inside the repository (`.worktrees/`)
3. **git-workflow --task pre-work was invoked:** The worktree was created by the mandatory skill, not manually
4. **Feature branch is checked out:** The worktree shows the correct branch name

**If ANY check fails:** HALT and invoke `git-workflow --task pre-work` before proceeding.

**Evidence requirement:** Record `git worktree list` output and `worktree.path` value before dispatching any sub-agent.

## Overflow Signal Contract

When a sub-agent cannot fit the assigned work, it MUST return `status: OVERFLOW` with `completed_work`, `remaining_work`, and `suggested_splits`. See `overflow-signal` task for the full schema.

## Dispatch Context Contract

When the orchestrator dispatches a sub-agent, it MUST pass: `issue`, `branch`, `spec`, `plan_issue`, `authorization`, `authorization_scope`, `halt_at`, `pr_strategy`, `depth`, `max_depth`, `prior_context`, `decision_log_reference`, `phase_progress` (prose-driven: completed phases by concern, boundaries crossed, verification evidence), `sub_task` (description, scope, boundaries), `model_context`, `env_vars` (worktree.path, branch, github.owner, github.repo), `tdd_phase`, `current_item`, `top_down_items`, `dev.name`, `dev.email`. See `context-passing` task for the full schema.

**Invariants:** `worktree.path` is MANDATORY — no exceptions. If empty: FATAL ERROR → HALT. `plan_issue` is set when dispatched from plan approval flow. `phase_progress` accumulates across the work set from prior sub-agent results.

## Sub-Agent Completion Checkpoint

After every sub-agent dispatch, perform a completion checkpoint before accepting work. See `completion-checkpoint` task for the full protocol.

**Detection summary:**

| Signal | Action |
| -- | -- |
| `status: DONE` | Proceed |
| `status: DONE_WITH_CONCERNS` | Review concerns, proceed if OK |
| `status: OVERFLOW` | Re-dispatch reduced scope |
| `status: BLOCKED` | HALT and report |
| **No result** (timeout/crash/empty) | **ABNORMAL TERMINATION** → assessment protocol |

## Sub-agent Result Contract

Every sub-agent MUST return: `status` (DONE | DONE_WITH_CONCERNS | OVERFLOW | BLOCKED), `files_changed`, `summary`, `concerns` (if DONE_WITH_CONCERNS), `decision_log_entry` (prose, no prescribed format), `plan_issue`, `phase_progress` (completed_phases, concern_boundaries_crossed, verification_evidence, verification_passed), `compare_url`, `exec_summary`.

**Decision Log persistence:** After each sub-agent returns, the orchestrator appends `decision_log_entry` as a GitHub Issue comment on the Plan issue (append-only, persists across sessions).

## Orchestrator Recovery Mode

**Option A: Undo and Re-dispatch (DEFAULT)** — `git checkout .` and re-dispatch with appropriate scope. Use for all cases except the narrow exception.

**Option B: Complete Manually (NARROW EXCEPTION)** — Only when ALL conditions are met: ≤50 lines diff, single file, fully correct against spec, last sub-agent in work set. Action: commit+push, run verification. Context window risk makes this strongly discouraged.

**The orchestrator MUST NOT ask the user to choose recovery options.** This is an agent intelligence concern per `000-critical-rules.md`. All abnormal terminations MUST be reported to chat.

## Result Validation (MANDATORY)

After every sub-agent dispatch, validate the result before acting on it. See `result-validation` task for the full procedure.

| Condition | Action |
|-----------|--------|
| Empty/whitespace result | FALLBACK: perform inline; report warning |
| Non-YAML but parseable | TRY parse; FALLBACK if unparseable |
| Valid `status: DONE` | PROCEED |
| Valid `status: DONE_WITH_CONCERNS` | Review, proceed if scope OK |
| Valid `status: BLOCKED` | HALT |
| Valid `status: OVERFLOW` | Re-dispatch reduced scope |
| Error/exception trace | FALLBACK: perform inline; report error |

**FALLBACK:** Report warning, perform task inline. **Double-failure:** Report both failures, invoke `--task completion`, HALT with status + byline. This gate runs BEFORE the Completion Checkpoint.

## UI Sub-Agent Routing

The divide-and-conquer orchestrator delegates UI-related tasks to specialized sub-agent skills based on task characteristics and trigger criteria.

### Trigger Criteria Mapping

| Task Characteristic | Target Skill | Model Context |
|---|---|---|
| Wireframe, mockup, visual layout, interaction design | `ui-design` | `kimi-k2.6:cloud` |
| UI implementation, frontend code, framework component | `ui-engineer` | `glm-5.1:cloud` |
| Screenshot capture, design review | `ui-design` | `kimi-k2.6:cloud` |
| Design artifact validation | `ui-design` (review task) | `kimi-k2.6:cloud` |
| Implementation validation against interaction-spec | `ui-engineer` (validate-impl task) | `glm-5.1:cloud` |

### Three-Tier Trigger Model

1. **Intelligence**: Main agent infers UI delegation from context analysis (spec mentions UI terms, layout descriptions, visual elements, interaction design)
2. **Keyword-enhanced**: `[UI]` label on issues, `requires-ui: true` in spec frontmatter, `ui-design`/`ui-engineer` in task tags
3. **Direct instruction**: User explicitly says "use ui-design" or "use ui-engineer" or invokes `/skill ui-design --task wireframe`

### Model Context Assignment

When dispatching to UI sub-agents, the orchestrator sets `model_context` in the Dispatch Context Contract:

- `ui-design` tasks → `model_context: "kimi-k2.6:cloud"`
- `ui-engineer` tasks → `model_context: "glm-5.1:cloud"`
- Non-UI tasks → `model_context: ""` (default)

### Parallel Dispatch

UI and non-UI work CAN run concurrently when:
- No shared file dependencies between UI and non-UI tasks
- No data flow dependency (UI artifacts needed by non-UI tasks are already produced)

UI sub-agents MUST NOT run concurrently when:
- Non-UI tasks depend on UI artifacts not yet produced
- The ui-design and ui-engineer sub-agents have a sequential dependency (ui-engineer consumes ui-design output)

## Worktree Mode

When `worktree.path` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- `git` commands run from the worktree directory, NOT the main repo

If `worktree.path` is NOT set, operate normally from the project root.

## Sub-Agent Tasks

### Sub-Agent Tasks

| Task | Words |
|------|-------|
| `assemble-work` | 2,782 |
| `orchestrate` | ≈400 |
| `assess` | ≈300 |
| `decompose` | ≈300 |
| `dispatch` | ≈250 |
| `completion-checkpoint` | ≈300 |
| `result-validation` | ≈200 |
| `overflow-signal` | ≈200 |
| `merge` | ≈150 |
| `context-passing` | ≈200 |
| `purification-and-enforcement` | ≈250 |
| `completion` | ≈150 |
| `implementer-prompt` | ≈250 |
| `spec-reviewer-prompt` | ≈200 |
| `code-quality-reviewer-prompt` | ≈200 |

### Result Contracts (Sub-Agent Tasks)

See individual task files for full schemas. Key result contract:

**assemble-work**: Returns `status`, `issues_dispatched`, `issues_completed`, `issues_failed`, `work_branch`, `work_state_file`, `results` array.

**Dispatch Context Schema**: `work_state_file`, `authorization_scope`, `halt_at`, `pr_strategy`, `session_vars` (github.owner, github.repo, dev.name, dev.email, worktree.path). See `assemble-work` task for full schema.

## Sub-Agent Spawning

1. Main agent loads this dispatch document (≈650 words)
2. Spawns sub-agent: `task(subagent_type="general", prompt="Use divide-and-conquer skill with context: issue=#N, branch=<name>, <session-context>")`
3. Sub-agent loads: this SKILL.md + task files + required guidelines
4. Sub-agent executes: assess → decompose → dispatch → merge → completion
5. Returns structured result per Result Contract
6. Main agent receives result — no orchestration detail in main context

Pass `<worktree.path>`, `branch`, `<github.owner>`, `<github.repo>`, `<dev.name>`, `<dev.email>` from session init.

## Live Verification: Work State (MANDATORY)

**CRITICAL: When reading work state, verify against live GitHub/git state. Trusting claims without verification is a VERIFICATION-GAP per `065-verification-honesty.md`.**

| Work State Claim | Verification Action | Tool Call | Problem Class |
|------------------|-------------------|-----------|---------------|
| "Prior issue completed" | Verify PR was merged | `github_pull_request_read(method=get)` → `merged` | CONFLICTING |
| "Authorization cascades" | Verify auth comment on parent | `github_issue_read(method=get_comments)` | VERIFICATION-GAP |
| "Work branch is current" | Verify branch tip | `git log -1 --oneline <branch>` | VERIFICATION-GAP |
| "Sub-issue phase complete" | Verify sub-issue is closed | `github_issue_read(method=get)` → `state` | CONFLICTING |
| "Prior results reference" | Verify files/issues exist | `glob` or `github_issue_read` | MISSING-TRACEABILITY |

**On failure:** CONFLICTING → flag-for-review; VERIFICATION-GAP → conditional; auto-fix where safe (rebase, update state). See full classification table in task files.

## Cross-Reference Verification (MANDATORY)

**CRITICAL: Each cross-reference must be verified against actual skill content.** Before invoking any cross-referenced skill: `ls .opencode/skills/<name>/SKILL.md` for existence, `grep` for task references, compare behavior with content. Missing references → MISSING-TRACEABILITY; mismatched behavior → CONFLICTING.

**Adversarial cross-reference:** When work state claims seem wrong, invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension".

## Two-Stage Review Pipeline

Optional quality gate for sub-agent output: (1) **Spec reviewer** (`spec-reviewer-prompt`): validates implementation against spec success criteria. (2) **Code quality reviewer** (`code-quality-reviewer-prompt`): validates code quality, testing, conventions. (3) **Implementer prompt** (`implementer-prompt`): provides dispatch context template for review workflows.

Use when spec has complex success criteria benefiting from independent verification. Single-issue work sets with straightforward criteria may skip. Invoke: `--task two-stage-review`.

## Cross-References

- `git-workflow` (git ops), `approval-gate` (authorization), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `using-git-worktrees` (worktree creation), `spec-auditor` (ground-truth adversarial verification)
- `010-approval-gate.md`, `000-critical-rules.md`, `065-verification-honesty.md` (metadata verification extension)
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification
- Adapted from: `implementation-workflow`

Co-authored with AI: <AgentName> (<ModelId>)