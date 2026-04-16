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
| `completion-checkpoint` | Post-dispatch verification: detect abnormal termination, assess work, recover | ~300 |
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

## Pre-Dispatch Verification Checkpoint (MANDATORY)

**Before dispatching any sub-agent, the main agent MUST verify:**

1. **Worktree exists:** `git worktree list` shows the feature branch worktree
2. **WORKTREE_PATH is set:** `echo $WORKTREE_PATH` returns a non-empty path inside the repository (`.worktrees/`)
3. **git-workflow --task pre-work was invoked:** The worktree was created by the mandatory skill, not manually
4. **Feature branch is checked out:** The worktree shows the correct branch name

**If ANY check fails:** HALT and invoke `git-workflow --task pre-work` before proceeding.

**Evidence requirement:** Record `git worktree list` output and `WORKTREE_PATH` value before dispatching any sub-agent.

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

## Sub-Agent Completion Checkpoint

After every sub-agent dispatch, the orchestrating agent MUST perform a completion checkpoint before accepting work. This ensures abnormal terminations (context overflow, timeout, crash, incomplete execution) are detected and recovered rather than silently accepted.

**Detection:**

| Sub-agent Signal | Meaning | Action |
| -- | -- | -- |
| Returns `status: DONE` | Normal completion | Proceed to next sub-task |
| Returns `status: DONE_WITH_CONCERNS` | Completed with caveats | Review concerns, proceed if correctness/scope OK |
| Returns `status: OVERFLOW` | Context overflow | Re-dispatch with reduced scope per `overflow-signal` task |
| Returns `status: BLOCKED` | Blocked by external issue | HALT and report blocker |
| Returns **no result** (timeout, crash, empty) | **ABNORMAL TERMINATION** | Trigger assessment protocol |

**Assessment Protocol (for ABNORMAL TERMINATION):**

1. Check `git status` in the worktree:
   - If working tree is **CLEAN** (no changes) → sub-agent didn't start → Re-dispatch full scope
   - If working tree has **UNCOMMITTED changes** → sub-agent started but didn't commit → continue to step 2

2. If uncommitted changes exist:
   a. Read changed files via `git diff` and `git diff --cached`
   b. Compare against the dispatch spec (what was the sub-agent asked to do?)
   c. Assess completion level:

| Condition | Git State | Assessment | Recovery Action |
| -- | -- | -- | -- |
| No result, clean tree | No changes | Didn't start | Re-dispatch full scope |
| No result, uncommitted, complete | All deliverables in diff | Started, completed, didn't commit | UNDO + re-dispatch (default) OR Manual commit + push (narrow exception, see Recovery Mode) |
| No result, uncommitted, partial | Some deliverables in diff | Started, incomplete | `git checkout .` + re-dispatch reduced scope |
| No result, uncommitted, wrong | Changes don't match spec | Started, went wrong | `git checkout .` + re-dispatch full scope |
| OVERFLOW result | Changes up to overflow point | Context overflow | Re-dispatch remaining scope |

**The AI agent makes the recovery decision autonomously** based on the assessment protocol. This is an agent intelligence concern per the "Pushing Agent Intelligence Decisions to the User" critical violation in `000-critical-rules.md`. The user should NOT be asked to decide whether to complete manually or undo + re-dispatch.

**Reporting:** All abnormal terminations MUST be reported to chat with this format:

```
⚠️ SUB-AGENT ABNORMAL TERMINATION DETECTED

Sub-agent for #<issue> terminated abnormally.
Assessment: <Didn't start | Complete but uncommitted | Partial work | Wrong work>
Recovery action: <Re-dispatch full scope | Manual commit+push | Undo + re-dispatch reduced | Undo + re-dispatch full>
Files affected: <list>

Proceeding with recovery...
```

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

## Orchestrator Recovery Mode

When the orchestrating agent detects abnormal termination via the Sub-Agent Completion Checkpoint, it enters Recovery Mode. The orchestrator autonomously decides the recovery strategy based on the assessment protocol — this is an agent intelligence concern per the "Pushing Agent Intelligence Decisions to the User" critical violation in `000-critical-rules.md`.

**Recovery Option A: Undo and Re-dispatch (DEFAULT)**

- **When:** Changes are partial, wrong, corrupted, the sub-agent didn't start, OR no narrow exception applies
- **Action:** `git checkout .` to discard changes, then re-dispatch with appropriate scope
- **Scope determination:**
  - Clean tree (didn't start) → re-dispatch full scope
  - Partial deliverables → re-dispatch reduced scope (only remaining deliverables)
  - Wrong/corrupted changes → re-dispatch full scope
  - Complete but uncommitted (no narrow exception) → re-dispatch full scope

**Recovery Option B: Complete Manually (NARROW EXCEPTION — Strongly Discouraged)**

- **When ALL conditions are met simultaneously:**
  1. Uncommitted changes represent ≤50 lines of diff
  2. Changes touch a single file only
  3. Changes are fully correct and complete against the dispatch spec
  4. No remaining sub-agent dispatches in the batch (this is the last sub-agent)
- **Action:** Commit and push the changes, then run verification (`verification-before-completion --task verify`)
- **⚠️ Context window risk:** Manual completion consumes orchestrator context window. Even a "small" manual completion (reading diffs, composing commits) can push an already-loaded context toward overflow. This risk is WHY manual completion is strongly discouraged — the orchestrator's context window is a scarce resource that must be preserved for orchestration duties. Re-dispatching to a fresh sub-agent is context-free for the orchestrator.
- **If ANY condition is NOT met → use Option A (Undo and Re-dispatch)**

**The orchestrator MUST NOT ask the user to decide between recovery options.** The assessment protocol provides sufficient information for the AI agent to choose autonomously. Asking "Should I complete manually or re-dispatch?" would violate the "Pushing Agent Intelligence Decisions to the User" critical violation.

**Logging requirement:** All abnormal terminations MUST be reported to chat with the format specified in the Sub-Agent Completion Checkpoint section. Silent acceptance of abnormal termination state is a critical violation.

**Cross-reference:** See `000-critical-rules.md` → "Pushing Agent Intelligence Decisions to the User" for the rule that structural decisions (including recovery strategy) are agent intelligence concerns, not user decisions.

## Worktree Mode

When `WORKTREE_PATH` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `WORKTREE_PATH`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `WORKTREE_PATH/`
- `git` commands run from the worktree directory, NOT the main repo

If `WORKTREE_PATH` is NOT set, operate normally from the project root.

## Sub-Agent Tasks

### Execution Mode Table

| Task | Words | Mode |
|------|-------|------|
| `assemble-batch` | 2,782 | sub-agent |
| `orchestrate` | ~400 | inline |
| `assess` | ~300 | inline |
| `decompose` | ~300 | inline |
| `dispatch` | ~250 | inline |
| `completion-checkpoint` | ~300 | inline |
| `overflow-signal` | ~200 | inline |
| `merge` | ~150 | inline |
| `context-passing` | ~200 | inline |
| `purification-and-enforcement` | ~250 | inline |
| `completion` | ~150 | inline |

### Result Contracts (Sub-Agent Tasks)

#### assemble-batch

```yaml
status: DONE | DONE_WITH_CONCERNS | BLOCKED | OVERFLOW
task: assemble-batch
issues_dispatched: [<N>]
issues_completed: [<N>]
issues_failed: [<N>]
batch_branch: <branch_name>
batch_state_file: <path>
results: [{issue: <N>, status: <str>, summary: <str>}]
```

### Dispatch Context Schema

```yaml
batch_state_file: <path>
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```

## Sub-Agent Spawning

This skill is a **heavy skill** — its orchestration logic can run in isolation. When the main agent needs divide-and-conquer execution, spawn a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~650 words)
2. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use divide-and-conquer skill with context: issue=#N, branch=<name>, <session-context>")`
3. Sub-agent loads: this SKILL.md + relevant task files + required guidelines
4. Sub-agent executes: assess → decompose → dispatch → merge → completion
5. Sub-agent returns structured result per Sub-agent Result Contract
6. Main agent receives result — no orchestration detail in main context

**Sub-agent context parameters:** Pass `WORKTREE_PATH`, `BRANCH_NAME`, `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL` from session init.

## Live Verification: Batch State (MANDATORY)

**🚫 CRITICAL: When this skill reads batch state (prior results, authorization, branch status), it MUST verify against live GitHub/git state. Trusting batch file claims without verification is a VERIFICATION-GAP finding per `065-verification-honesty.md`.**

| Batch State Claim | Verification Action | Tool Call | Problem Class |
|------------------|-------------------|-----------|---------------|
| "Prior issue completed" in batch file | Verify prior issue PR was actually merged | `github_pull_request_read(method=get)` → check `merged` field | CONFLICTING |
| "Authorization cascades" | Verify authorization comment exists on parent issue | `github_issue_read(method=get_comments, issue_number=N)` → find auth comment | VERIFICATION-GAP |
| "Batch branch is current" | Verify branch tip matches expected state | `bash` to run `git log -1 --oneline <branch>` | VERIFICATION-GAP |
| "Sub-issue phase complete" | Verify sub-issue state is actually closed (if applicable) | `github_issue_read(method=get, issue_number=N)` → check `state` | CONFLICTING |
| "Prior results reference" | Verify referenced files/issues still exist | `glob(pattern="**/file")` or `github_issue_read(method=get, issue_number=N)` | MISSING-TRACEABILITY |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Prior PR not merged | CONFLICTING | flag-for-review | HALT — dependent branch may need to be stacked differently |
| Authorization missing | VERIFICATION-GAP | conditional | Re-verify authorization before dispatching |
| Branch out of date | VERIFICATION-GAP | auto-fix | Rebase or merge as needed |
| Sub-issue state contradicts claim | CONFLICTING | auto-fix | Update batch state to reflect actual state |
| Referenced file/issue missing | MISSING-TRACEABILITY | conditional | Search alternates before proceeding |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `subagent-driven-development` in Cross-References | File exists at `.opencode/skills/subagent-driven-development/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` in Cross-References | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `verification-before-completion` in Cross-References | File exists at `.opencode/skills/verification-before-completion/SKILL.md` | MISSING-TRACEABILITY if missing |
| `finishing-a-development-branch` in Cross-References | File exists at `.opencode/skills/finishing-a-development-branch/SKILL.md` | MISSING-TRACEABILITY if missing |
| `using-git-worktrees` in Cross-References | File exists at `.opencode/skills/using-git-worktrees/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `assemble-batch` | File exists at `.opencode/skills/divide-and-conquer/tasks/assemble-batch.md` | MISSING-TRACEABILITY if missing |
| Task table entry `assess` | File exists at `.opencode/skills/divide-and-conquer/tasks/assess.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/divide-and-conquer/tasks/completion.md` | MISSING-TRACEABILITY if missing |
| `implementation-workflow` in Adapted From | Skill directory exists or was renamed to this skill | MISSING-TRACEABILITY if missing |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced task file missing | MISSING-TRACEABILITY | flag-for-review | Task may have been renamed |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |
| Ground-truth subtask missing | MISSING-TRACEABILITY | flag-for-review | spec-auditor may not have Phase 1 changes |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including authorization currency and sub-issue state. When this skill encounters batch state claims that smell wrong (e.g., "authorization cascades" but no auth comment found, "sub-issue closed" but no merged PR), invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

- Related skills: `subagent-driven-development` (task-level isolation with two-stage review), `git-workflow` (git ops), `approval-gate` (authorization), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `using-git-worktrees` (worktree creation), `spec-auditor` (ground-truth adversarial verification)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`, `065-verification-honesty.md` (metadata verification extension)
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification
- Adapted from: `implementation-workflow` (batch-orchestrate, context-passing, purification-and-enforcement, completion)

Co-authored with AI: <AI-Name> (<model-id>)