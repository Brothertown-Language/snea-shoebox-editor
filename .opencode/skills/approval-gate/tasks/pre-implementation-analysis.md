# Task: pre-implementation-analysis

## Purpose

Analyze interdependencies and determine execution order for all approved issues — whether one or many — producing a flat item list for `assemble-batch` dispatch. Every approval follows this unified path: sub-issue expansion → flat item list → assemble-batch → batch branch → pr-creation → one PR.

**Per-issue screening is performed by the `screen-issue` task**, dispatched as parallel sub-agents (one per issue). This task receives N screening result contracts and performs cross-issue merge + dependency graph building.

## Entry Criteria

- One or more issues approved (e.g., `Approved: #660`, `Approved: #660, #662, #621`)
- Each issue has been verified by `verify-authorization`
- User has explicitly authorized implementation
- **Per-issue screening results available** (from `screen-issue` sub-agents or inline execution)

## Exit Criteria

- Each approved issue screened and classified by dependency category
- Already-implemented, superseded, moot, and meta/non-code issues excluded with reason
- Partially-implemented issues reduced to remaining phases
- Sub-issues expanded into flat item list (even for single issues)
- Dependency graph produced with execution order
- Parallel-safe groups identified
- Execution plan presented in chat (informative only — no confirmation)
- Agent proceeds immediately to `assemble-batch`

## Procedure

### Step -1: Batch Size Check and Dispatch Decision (MANDATORY FIRST)

Before reading ANY issue body:

1. COUNT the number of approved issues
2. If count ≤ 3: inline screening is PERMITTED (proceed to Step 0)
3. If count > 3: sub-agent dispatch is MANDATORY — do NOT read any issue body into orchestrator context

**⚠️ CRITICAL VIOLATION:** Reading issue bodies for >3 issues into orchestrator context before sub-agent dispatch is a CRITICAL GUIDELINE VIOLATION per `000-critical-rules.md` §Inline Screening of Batch Approvals. The orchestrator's context window must stay clean for cross-issue merge and dependency graph building — not consumed by raw issue bodies.

### Step 0: Collect Screening Results

Collect per-issue screening results from `screen-issue` sub-agents (parallel) or inline execution.

If screening results are NOT already available from sub-agent dispatch, dispatch `screen-issue` sub-agents:

```
For each approved issue:
  Dispatch sub-agent: task(subagent_type="general", prompt="Use screen-issue task for issue #N with dispatch context: ...")
  Collect result contract
```

**Dispatch context per sub-agent:**

```yaml
issue_number: <N>
batch_peers: [<list of all approved issue numbers except this one>]
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```

**After all sub-agents return**, assemble screening results.

### Step 0.5: Assemble Gate Evidence Audit Table

From the collected screening results, assemble the full Gate Evidence Audit Table:

```markdown
## Gate Evidence Audit Table

| Issue # | Sub-issues Enumerated? (Gate 1) | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? (Gate 2) | All Criteria Verified vs Codebase? | Final Classification |
|---------|----------------------------------|--------------------------|-------------------------------|--------------------------------------|-----------------------------------|---------------------|
| #N | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | <classification> |
```

Each row comes from the `gate_evidence` field of the corresponding `screen-issue` result contract.

**If ANY row has ❌ in columns 2-5:** That issue's classification is INVALID. It MUST be DOWNGRADED:
- ❌ in Gate 1 columns → DOWNGRADE to "partially-implemented" (sub-issues not verified)
- ❌ in Gate 2 columns → DOWNGRADE to "partially-implemented" or "not-implemented-despite-closure" (success criteria not verified)

**After downgrades:** Remove downgraded issues from "already-implemented" list. Add them to the "partially-implemented" list in the execution plan. Re-classify per screening results.

**If the table is incomplete:** HALT and complete it before proceeding.

### Step 0.7: Reconcile Issue Status Inconsistencies (MANDATORY)

After the Gate Evidence Audit Table is assembled (Step 0.5), identify all issues with status inconsistencies and invoke `reconcile-issue-graph` to auto-correct them before assembling the flat item list. This step prevents the pipeline from escalating deterministic status corrections to the developer.

**Status inconsistency indicators from screening results:**

| Indicator | Example | Reconciliation Action |
|-----------|---------|----------------------|
| Issue reopened after PR merge | `state: open` + merged PR exists with `Fixes #N` | Auto-close (merged PR path) |
| Issue open but all success criteria verified in codebase | `state: open` + Gate 1 + Gate 2 pass | Auto-close (code verified path) |
| Sub-issue closed without merged PR | Sub-issue `state: closed` + `state_reason` not `not_planned`/`duplicate` + no merged PR | Reopen |
| Issue closed as completed but success criteria fail Gate 2 | `state: closed` + Gate 2 FAIL | Reopen (not-implemented-despite-closure) |
| Sub-issue open but parent PR merged with `Fixes` on parent | Sub-issue `state: open` + parent has merged PR | Evaluate: auto-close if criteria met, or include remaining work |

**Procedure:**

1. **Collect inconsistencies:** From the screening results, collect all issues where the current GitHub state contradicts the verified implementation state:
   - `category: already-implemented` + `gate_evidence.gate1_closure_legitimacy: false` → status inconsistency
   - `category: partially-implemented` + issue/sub-issues closed prematurely → status inconsistency
   - `requires_developer: true` due to status confusion (not genuine conflict) → route to reconciliation

2. **Build findings list:** For each inconsistent issue, create a finding with:
   - `issue_number`: the issue with wrong state
   - `state`: current state from GitHub API
   - `classification`: one of `auto-close (merged PR)`, `auto-close (code verified)`, `reopen`, `no-action (not_planned)`, `no-action (duplicate)`, `uncertain`
   - `evidence_summary`: brief description of why the state is wrong

3. **Invoke `reconcile-issue-graph`:** Pass the findings list to the reconciliation task. Follow the `reconcile-issue-graph` procedure exactly:
   - Step 1: Categorize findings (reuse classifications from above)
   - Step 2: Verify auto-close candidates (merged PR or code verification)
   - Step 3: Verify reopen candidates (no merged PR, code not in repo)
   - Step 4: Process no-action findings
   - Step 5: Collect uncertain findings (only these escalate to developer)
   - Step 6: Execute auto-close actions (update issue state + comment with evidence)
   - Step 7: Execute reopen actions (update issue state + comment with evidence)
   - Step 8: Output reconciliation report to chat

4. **Re-screen after reconciliation:** After `reconcile-issue-graph` completes, re-read the affected issues' state from GitHub API. Update screening result classifications if state changed. Proceed to Step 1.

**Key principle:** The developer is NEVER asked to determine whether an issue's state is correct. `reconcile-issue-graph` resolves all deterministic cases (merged PR = auto-close, no merged PR = reopen). Only `uncertain` findings (conflicting signals) are escalated.

**This step MUST complete before Step 1.** Assembling the flat item list requires accurate issue state — if issues are in the wrong state, the flat item list will be wrong.

### Step 1: Assemble Flat Item List

From the collected screening results, assemble the flat item list:

- For each `included` issue: add its `flat_items` to the execution list
- For each `excluded` issue: add to "Excluded" section with reason
- For each `scope-reduced` issue: add its remaining phases to the execution list
- For issues with `requires_reconciliation: true`: these were handled by Step 0.7 — use their post-reconciliation classification
- For issues with `requires_developer: true` AFTER reconciliation (only `uncertain` findings): HALT for developer review

### Step 2: Cross-Issue Analysis

Analyze cross-issue relationships using file/symbol references from screening results. **No additional API calls needed** — screening results already contain verified file and symbol references.

#### Cross-Issue Checks

1. **Stale assumptions across issues:** If issue A's `file_references` overlap with issue B's `file_references`, check intent alignment:
   - Same intent → serialize (B before A if B provides the canonical change)
   - Different intent → HALT for developer review

1. **Supersession across issues:** If issue B's `file_references` are a superset of issue A's, and B's scope description fully encompasses A's:
   - Unambiguous → exclude A (superseded by B)
   - Ambiguous → HALT for developer review

1. **Cross-issue sub-issue pairs:** If a parent and its sub-issues are both included:
   - Default: omit sub-issues — parent's cascade covers them
   - Exception: isolated sub-issues with no file overlap → dispatch to own sub-agent
   - Edge case: parent excluded but sub-issues included → include independently

1. **Merge-time conflict risk:** Issues touching the same file in different sections. Noted in execution plan for `assemble-batch` handling. Do NOT block execution.

### Step 3: Classify Each Issue

Determine each issue's category based on cross-issue analysis:

| Category | Criteria | Action |
|----------|----------|--------|
| **Must-precede** | Issue A modifies files that Issue B also needs to edit | Execute A before B |
| **Independent** | Issue A and B touch completely different files | Can run in parallel |
| **Conflict-risk** | Issue A and B both modify overlapping files | Serialize or coordinate |
| **Meta/Non-code** | Issue describes behavior/rule with NO code changes | Exclude from implementation |

**Classification heuristics:**

1. **File overlap analysis:** Use `file_references` from screening results. No API calls needed.
1. **Skill overlap:** Issues using the same skills that mutate shared state (e.g., both update `000-critical-rules.md`) are conflict-risk.
1. **Logical ordering:** When Issue A's output becomes Issue B's input (e.g., A creates a skill that B references), A must precede B.
1. **Scope analysis:** `.opencode/`-only changes vs `src/` changes vs doc-only changes.

**Add edges from screening results:**

- Same-intent stale assumption pairs → must-precede edge
- Cross-issue sub-issue pairs → dependency edge (parent covers sub-issues unless isolated)

### Step 4: Build Dependency Graph

Create a directed graph where:

- Nodes = remaining (non-excluded) approved issues
- Edges = "must-precede" relationships (including stale-assumption and cross-sub-issue edges from cross-issue analysis)
- Groups = sets of issues with no inter-dependencies (parallel-safe)

```markdown
## Dependency Analysis

### Execution Order

**Serial (must be done in order):**
1. #A — must precede #B (shared file: `path/to/file.md`)
2. #B — depends on #A output

**Parallel-safe Group 1:**
- #C (touches `.opencode/skills/X/`)
- #D (touches `src/module_y.py`)

**Parallel-safe Group 2:**
- #E (touches `docs/`)

### Excluded (Pre-Analysis Screening)
- #F — meta/behavioral issue, no code changes required
- #G — already-implemented (PR #M merged)
- #H — superseded by #B

### Scope-Reduced
- #I — partially-implemented (phase 1 done by PR #M; phases 2, 3 remaining)
```

### Step 5: Determine Execution Strategy

| Strategy | When | How |
|----------|------|-----|
| **Sequential** | Must-precede chain exists | Execute in dependency order |
| **Parallel** | Independent issues | Dispatch via `subagent-driven-development` |
| **Hybrid** | Mix of both | Serial for must-precede, parallel for independent groups |
| **Exclude** | Meta/non-code, already-implemented, superseded, moot | Report exclusion with reason |
| **Reduce scope** | Partially-implemented | Include remaining phases only |

### Step 6: Present Execution Plan (Informative Only)

**MANDATORY: The dependency analysis MUST be visible in chat (not hidden in agent reasoning).**

**The plan is presented for informational purposes. Agent proceeds immediately to execution. No confirmation is requested or awaited.**

Format:

```markdown
## Batch Approval — Dependency Analysis

**Approved Issues:** #660, #662, #621, #614, #630

### Pre-Analysis Screening

| Issue | Screening Result | Reason |
|-------|-----------------|--------|
| #660 | Excluded — meta/non-code | No code changes required |
| #670 | Excluded — already-implemented | PR #719 merged, all criteria met |
| #671 | Scope-reduced — partially-implemented | Phase 1 done by PR #719; phases 2, 3 remaining |

### Classification

| Issue | Category | Files | Dependencies |
|-------|----------|-------|-------------|
| #662 | Independent | `.opencode/skills/` | None |
| #621 | Conflict-risk | `.opencode/guidelines/000-*.md` | Conflicts with #630 |
| #614 | Independent | `src/` | None |
| #630 | Must-precede #621 | `.opencode/guidelines/` | Must complete before #621 |
| #671 | Independent | `.opencode/skills/` | None (scope: phases 2, 3 only) |

### Execution Plan

**Phase 1 (Serial):**
1. #630 — must precede #621

**Phase 2 (Parallel-safe):**

Each parallel issue includes dispatch context:
- #662 (`.opencode/skills/`) → `worktree_path: .worktrees/spec-662`
- #614 (`src/`) → `worktree_path: .worktrees/spec-614`
- #671 (`.opencode/skills/` — phases 2, 3 only) → `worktree_path: .worktrees/spec-671`

**Phase 3 (After #630):**
- #621 (`.opencode/guidelines/`)

**Merge-time ordering:**
- #662 and #621 may conflict at merge — #621 will rebase onto `dev` after #662 merges before creating its PR.

**Excluded:**
- #660 — meta/behavioral issue, no code changes required
- #670 — already-implemented (PR #719)

**Scope-reduced:**
- #671 — partially-implemented (phase 1 done by PR #719; phases 2, 3 remaining)

Proceeding with execution plan.
```

**Checkpoint (MANDATORY):** Before proceeding to `assemble-batch`, verify NO `question` tool calls have been made since the execution plan was presented. If any were made, remove them and proceed autonomously. The execution plan is presented for informational purposes — no confirmation is requested or awaited.

#### Prohibited Actions

- **No `question` tool invocation** after plan presentation
- **No HALT** between plan presentation and `assemble-batch`
- **No "Proceed?" / "Shall I?" / any confirmation solicitation**
- **No "awaiting approval" / "waiting for GO" / any pending-state marker**

#### Developer Involvement Triggers

The ONLY conditions requiring developer input during batch approval analysis:

- **Unresolvable conflicts**: Contradictory success criteria between issues in batch
- **Stale spec assumptions (different intent)**: Issue A references code that Issue B deletes, and A's intent differs from B's
- **Ambiguous supersession**: Two issues partially overlap, unclear which supersedes which
- **Uncertain reconciliation findings**: `reconcile-issue-graph` (Step 0.7) produced `requires_dev_action` entries with conflicting signals that prevent confident classification
- **screen-issue returned `requires_developer: true` AFTER reconciliation**: Any screening sub-agent flagged for developer review for reasons OTHER than status inconsistencies (which Step 0.7 handles)

**Status inconsistencies are NOT a developer involvement trigger.** `reconcile-issue-graph` resolves them deterministically (auto-close for verified-complete, reopen for verified-incomplete). Only `uncertain` findings with conflicting evidence that prevent classification are escalated.

When any of these triggers fire, HALT and present the conflict to the developer with a clear question. Do NOT attempt to auto-resolve.

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
  WORKTREE_PATH: ".worktrees/spec-<short-name>"
  BRANCH_NAME: "spec/<short-name>"
  GIT_OWNER: "<from-session>"
  GIT_REPO: "<from-session>"
  DEV_NAME: "<from-session>"
  DEV_EMAIL: "<from-session>"
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

### Step 9: Write Batch State File

After the execution plan is presented, write a batch state file that persists the plan for sub-agent dispatch:

```bash
mkdir -p .opencode/tmp
```

**File:** `.opencode/tmp/batch-<timestamp>.md`

**Contents:**

```markdown
# Batch Execution Plan

**Session:** <timestamp>
**Authorized Issues:** #A, #B, #C
**Authorization Context:** User said "approved" on <date>

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
- Cleaned up after batch completes (or on new session start)

### Step 10: Execute Immediately

After presenting the plan, proceed immediately to `assemble-batch`. Do not HALT. Do not ask for confirmation. Do not wait.

Yield control to `divide-and-conquer --task assemble-batch`:

```text
/skill divide-and-conquer --task assemble-batch
```

**assemble-batch** reads the batch state file and handles:

- Creating worktrees for the batch
- Dispatching sub-agents for each issue
- Collecting results and updating batch state
- Running review-prep after all issues complete

This handoff ensures:

- No HALTs between issues in the batch
- Each sub-agent gets isolated context
- The orchestrator stays clean — no implementation pollution
- Batch state survives context turnover

## Classification Detail

### Must-Precede Detection

An issue A must precede issue B when:

- A creates or modifies a file that B references or imports
- A defines a function/class/variable that B uses
- A restructures a directory that B assumes the old layout for
- A adds a dependency that B requires to build

### Conflict-Risk Detection

Two issues are conflict-risk when:

- Both modify the same file (detected via file path mentions)
- Both add content to the same section of a shared document
- Both rename/move the same files
- Both use skills that modify the same state file (e.g., `000-critical-rules.md`)

### Independent Detection

Two issues are independent when:

- They touch completely different file trees
- They use different skills with no overlapping state
- They add new files rather than modifying existing ones
- They can be merged in any order without conflicts

### Meta/Non-Code Detection

An issue is meta/non-code when:

- The body describes behavioral rules without file modifications
- The issue tracks observability or enforcement without requiring code changes
- The "implementation" is just acknowledging a pattern, not writing code
- All success criteria are satisfied by existence of documentation or rules already in place

### Superseded Detection

Issue A is superseded by batch peer B when:

- B's file list is a superset of A's file list
- B's scope description fully encompasses A's scope
- All of A's success criteria would be met by implementing B

**Ambiguous supersession** (partial overlap, unclear which is canonical): HALT for developer review.

### Moot Detection

An issue is moot when:

- Its spec references files/directories that have been restructured or removed since spec creation
- None of its remaining success criteria are achievable given the current codebase state
- The problem it describes no longer exists

### Partial Implementation Detection Heuristic

An issue is partially implemented when:

- A merged PR references the issue number in its body or commits
- Some (but not all) success criteria are already met in the current codebase
- The issue's phases can be mapped to the PR's changes to identify which are done

### Stale Assumption Detection

An issue has stale assumptions when:

- Its spec references specific function names, class names, or file paths that another issue in the batch modifies or deletes
- The reference is integral to the issue's implementation instructions (not just background context)

**Same intent (auto-resolvable):** Both issues want the same outcome for the referenced code.
**Different intent (HALT):** The issues have conflicting goals for the referenced code.

### Cross-Issue Sub-Issue Detection

A cross-issue sub-issue pair exists when:

- Issue A is a parent issue with sub-issues
- One or more of A's sub-issues are also in the approved batch
- Detected via `flat_items` from screening results

### Merge-Time Conflict Detection

Issues have a merge-time conflict risk when:

- They touch the same file but in different sections or with non-contradictory changes
- They are independent during implementation but may produce overlapping diffs
- This is distinct from conflict-risk (which affects implementation order)

## Adversarial Interdependency Verification

**Before trusting spec-claimed dependencies, verify them against actual codebase state.** Use `file_references` and `symbol_references` from screening results to avoid redundant API calls.

### Verify File Overlap Claims Against Actual Code

For each pair of issues with overlapping `file_references`, use srclight to verify actual dependency:
- `srclight_get_dependents` or `srclight_get_callers` to verify import/call chains
- If spec claims "A modifies X which B needs" but srclight shows no dependency → VERIFICATION-GAP
- If srclight shows dependency not mentioned in either spec → MISSING-ELEMENT

### Verify Must-Precede Claims

For each must-precede relationship claimed in specs:
- Check if A actually creates/modifies symbols that B uses
- `srclight_get_callers(symbol_name="<symbol_from_A>", project="<project>")`
- If callers include code from B's scope → dependency verified
- If callers do NOT include code from B's scope → VERIFICATION-GAP

### Verify Independence Claims

For each pair of issues claimed as "independent":
- `srclight_get_dependents(symbol_name="<key_symbol>", project="<project>", transitive=True)`
- If transitive dependents include code from the other issue's scope → NOT independent
- Downgrade from "parallel-safe" to "conflict-risk" or "must-precede"

### Verify Code References Exist

For each file path or symbol from screening `file_references`/`symbol_references`:
- File paths: verify with glob or read that the file exists
- Symbol names: verify with srclight_get_signature that the symbol exists
- If file/symbol does not exist → VERIFICATION-GAP

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| File overlap claimed but no actual dependency | VERIFICATION-GAP | flag-for-review | Re-classify as independent unless other evidence |
| Dependency exists but not mentioned in specs | MISSING-ELEMENT | conditional | Add to dependency graph, adjust execution order |
| Independence claimed but transitive dependency exists | CONFLICTING | conditional | Downgrade to conflict-risk or must-precede |
| Code reference to non-existent file/symbol | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or typo |

## Red Flags

**Never:**

- Skip dependency analysis when multiple issues are approved together
- Dispatch parallel subagents for conflict-risk issues without serialization
- Include meta/non-code, already-implemented, superseded, or moot issues in the implementation plan
- Present dependency analysis only in agent reasoning (MUST be in chat)
- Assume all issues are independent without analysis
- Execute must-precede issues out of order
- Use `question` tool after presenting the execution plan
- HALT between plan presentation and `assemble-batch`
- Ask "Proceed?", "Shall I?", or any confirmation solicitation after plan presentation
- Auto-re-stage issues with different-intent stale assumptions
- Skip gate evidence audit table assembly from screening results
- Proceed without verifying all screening result contracts are collected
- Classify an issue as "already-implemented" while it has open sub-issues or unverified success criteria
- Escalate status inconsistencies (reopened after merge, premature closure) to the developer instead of invoking `reconcile-issue-graph`

**Always:**

- Collect per-issue screening results before cross-issue analysis
- Assemble the Gate Evidence Audit Table from screening results
- Present the full dependency graph to the developer in chat
- Classify every issue before execution
- Execute must-precede issues first
- Group independent issues for parallel dispatch
- Exclude non-actionable issues with explicit reason
- Report each issue's classification in the execution plan
- Proceed immediately to `assemble-batch` after presenting the plan
- Auto-detect partially-implemented issues (no developer input needed)
- HALT for developer review only for unresolvable conflicts, different-intent stale assumptions, ambiguous supersession, and uncertain reconciliation findings
- Verify screening result `requires_developer` field and HALT if true (after reconciliation runs)
- Invoke `reconcile-issue-graph` (Step 0.7) for all issues with status inconsistencies before assembling the flat item list