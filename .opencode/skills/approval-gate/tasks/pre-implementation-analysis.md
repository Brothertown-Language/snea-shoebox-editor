# Task: pre-implementation-analysis

## Purpose

Analyze interdependencies and determine execution order for all approved issues — whether one or many — producing a flat item list for `assemble-batch` dispatch. Every approval follows this unified path: sub-issue expansion → flat item list → assemble-batch → batch branch → pr-creation → one PR.

## Entry Criteria

- One or more issues approved (e.g., `Approved: #660`, `Approved: #660, #662, #621`)
- Each issue has been verified by `verify-authorization`
- User has explicitly authorized implementation

## Exit Criteria

- Each approved issue screened (pre-analysis) and classified by dependency category
- Already-implemented, superseded, moot, and meta/non-code issues excluded with reason
- Partially-implemented issues reduced to remaining phases
- Sub-issues expanded into flat item list (even for single issues)
- Dependency graph produced with execution order
- Parallel-safe groups identified
- Execution plan presented in chat (informative only — no confirmation)
- Agent proceeds immediately to `assemble-batch`

## Procedure

### Step 0: Pre-Analysis Screening

Before classification, screen each approved issue against the following categories. Issues that fail screening are excluded or scope-reduced BEFORE building the dependency graph.

For each approved issue:

1. Check partial/full implementation (merged PR references + success criteria)
1. Check sub-issue closure verification for already-implemented classification (each sub-issue must be closed via merged PR, not prematurely closed)
1. Check superseded by batch peer (scope overlap analysis)
1. Check moot (spec references code that no longer exists/changed; no achievable criteria)
1. Check stale assumptions (cross-reference with other issues in batch)
1. Check revision status (flag in plan, remove `needs-approval` label)
1. Check for cross-issue sub-issue pairs (default: parent covers; exception: isolated sub-agent)
1. Classify conflicting pairs: auto-resolvable vs unresolvable

#### Screening Categories

| Category | Detection | Auto-resolve | Developer needed? |
|----------|-----------|-------------|-------------------|
| **Already implemented** | Merged PR references issue + Gate 1 passed (sub-issue enumeration gate) + Gate 2 passed (success criteria verification gate) + cross-references consistent | Exclude, mark "already-implemented" | No |
| **Not implemented despite closure** | `state: closed` + merged PR exists + Gate 1 OR Gate 2 FAILED (sub-issues open/unverified, or success criteria not met) | Reopen or include remaining work, mark "not-implemented-despite-closure — premature closure" | No |
| **Partially implemented** | Merged PR references issue + some success criteria met, some remaining | Include remaining phases only, mark "partially-implemented (phases X,Y done by PR #M)" | No |
| **Superseded by batch peer** | Issue B's scope fully covers issue A's scope | Exclude A, note "superseded by #B" | No (if unambiguous) / Yes (if ambiguous) |
| **Moot** | Referenced files/code restructured since spec creation; no remaining success criteria are achievable | Exclude, mark "moot" with reason | No |
| **Stale assumptions** | Issue A references code/functions/files that Issue B modifies or deletes | Re-stage A after B only if same intent; otherwise HALT for developer | Yes (if different intent) / No (if same intent) |
| **Conflicting (auto-resolvable)** | Issues touch same files, can be serialized | Serialize in correct order | No |
| **Conflicting (unresolvable)** | Contradictory success criteria | Cannot auto-resolve | **Yes** — HALT |
| **Meta/Non-code** | No code changes required | Exclude, mark "no code changes" | No |

#### Screening Outcomes

- **EXCLUDE**: already-implemented (verified via merged PR + sub-issues closed via merged PR + success criteria verified), superseded, moot, meta/non-code
- **REOPEN/RE-CLASSIFY**: not-implemented-despite-closure (closed but Gate 1 or Gate 2 failed — include remaining work)
- **REDUCE SCOPE**: partially-implemented (include remaining phases only)
- **SERIALIZE**: same-intent stale assumptions, auto-resolvable conflicts
- **HALT**: different-intent stale assumptions, unresolvable conflicts

#### Partial Implementation Detection

When a merged PR references the issue but not all success criteria are met:

#### Already-Implemented Sub-Issue Verification

**🚫 CRITICAL: An issue cannot be classified as "already implemented" if any of its sub-issues were closed without a merged PR.** Before excluding an issue as "already implemented," verify each sub-issue's closure:

```
For each sub-issue of the candidate "already implemented" issue:
  child = github_issue_read(method="get", issue_number=sub_issue_number)

  if child.state == "closed":
    state_reason = child.get("state_reason", "")
    prs = github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{GIT_OWNER}/{GIT_REPO}")
    merged_pr_found = False
    for pr in prs:
      pr_detail = github_pull_request_read(method="get", owner=GIT_OWNER, repo=GIT_REPO, pullNumber=pr["number"])
      if pr_detail.get("merged_at") is not None:
        merged_pr_found = True
        break

    if not merged_pr_found and state_reason != "not_planned":
      # Sub-issue closed without merged PR — NOT legitimate closure
      # Do NOT classify parent as "already implemented"
      DOWNGRADE to "partially-implemented" or "scope-reduced"

    if state_reason == "not_planned":
      # Sub-issue intentionally not implemented
      # Parent may be "already implemented" for remaining scope only
      # Reduce scope to exclude intentionally skipped sub-issue
      MARK as "scope-reduced — sub-issue #{sub_issue_number} intentionally not planned"

  elif child.state == "open":
    # Open sub-issue means parent is NOT fully implemented
    DOWNGRADE to "partially-implemented"
```

#### Mandatory Sub-Issue Enumeration Gate (Gate 1)

**🚫 CRITICAL — ZERO TOLERANCE: Before classifying ANY issue as "already-implemented," the agent MUST call `github_issue_read(method=get_sub_issues)` for that issue. Skipping this gate is a CRITICAL GUIDELINE VIOLATION. If `get_sub_issues` is not called, the classification is INVALID.**

This gate ensures the agent cannot skip the sub-issue traversal prescribed in the "Already-Implemented Sub-Issue Verification" section above. The existing section describes what to check; this gate enforces that the check ACTUALLY HAPPENS.

**Mandatory gate procedure — every candidate "already-implemented" issue MUST pass through ALL steps:**

1. **ENUMERATE:** Call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)` — no exceptions, no shortcuts
2. **VERIFY EACH CHILD:** For EVERY sub-issue returned, call `github_issue_read(method=get, issue_number=<sub_issue_number>)` — do NOT trust cached state; verify against live GitHub API
3. **CHECK CLOSURE LEGITIMACY:** For each closed sub-issue, search for merged PR evidence via `github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{GIT_OWNER}/{GIT_REPO}")`. If closed without merged PR and `state_reason != "not_planned"` → DOWNGRADE to "partially-implemented"
4. **CHECK OPEN SUB-ISSUES:** If ANY sub-issue is open → the parent CANNOT be "already-implemented" — DOWNGRADE to "partially-implemented"
5. **PRODUCE EVIDENCE:** Each sub-issue MUST produce a tool-call artifact showing its state was verified. Blanket assertions ("all sub-issues checked") WITHOUT per-sub-issue tool-call evidence are VERIFICATION-GAP findings

**Gate 1 failure triggers:**

| Failure Condition | Classification | Action |
|-----------------|----------------|--------|
| `get_sub_issues` not called | CRITICAL VIOLATION | Classification is INVALID — retry with gate |
| Open sub-issue found | DOWNGRADE | "partially-implemented" — open sub-issue remains |
| Sub-issue closed without merged PR | DOWNGRADE | "partially-implemented" — premature closure suspected |
| Sub-issue closed as "not_planned" | SCOPE-REDUCE | "scope-reduced" — exclude intentionally skipped sub-issue |
| No evidence artifacts produced | VERIFICATION-GAP | Re-run gate with evidence collection |

#### Success Criteria Verification Gate (Gate 2)

**🚫 CRITICAL — ZERO TOLERANCE: After Gate 1 passes (all sub-issues legitimately closed), the agent MUST verify every success criterion from the issue body against the live codebase. `state:closed` + merged PR does NOT shortcut this gate — closed issues require the SAME evidence as open issues, plus the additional merged PR evidence.**

A merged PR proves code was merged. It does NOT prove that success criteria are met, that changes are complete, or that no files were accidentally omitted. The merged PR is a **prerequisite gate** (needed to begin verification), NOT proof of implementation. Verification against the live codebase IS the evidence.

**Mandatory gate procedure — every candidate "already-implemented" issue MUST pass through ALL steps:**

1. **EXTRACT CRITERIA:** Read the issue body and extract every success criterion (checkboxes, bullet points with "must"/"shall"/"should", testable assertions)
2. **VERIFY EACH CRITERION:** For each success criterion, perform a direct verification action against the current state of `dev`:
   - Criterion says "file X contains Y" → `read` file X, verify Y exists
   - Criterion says "command Z returns expected output" → run command Z, verify output
   - Criterion says "no lint failures" → run lint command, verify zero failures
   - Criterion says "test T passes" → run test T, verify it passes
   - Criterion references a skill task → `read` the task file, verify the claimed content exists
3. **EVIDENCE REQUIRED:** Each criterion MUST produce a tool-call artifact. Assertions without tool-call evidence are VERIFICATION-GAP findings. "I checked earlier" or "the PR merged" are NOT evidence.
4. **FAILURE HANDLING:** If ANY criterion fails or is unverified → DOWNGRADE to "partially-implemented" or "not-implemented-despite-closure"

**Gate 2 failure triggers:**

| Failure Condition | Classification | Action |
|-----------------|----------------|--------|
| No success criteria extracted | VERIFICATION-GAP | Re-read issue body; if criteria cannot be found, flag for review |
| Criterion fails verification | DOWNGRADE | "partially-implemented" — criterion not met despite closure |
| Criterion unverified (no tool call) | VERIFICATION-GAP | Re-run verification; if unverifiable, flag for review |
| Success criteria not in issue body | MISSING-ELEMENT | Search comments; if absent, flag for developer to confirm |
| Agent claims "all criteria met" without evidence | CRITICAL VIOLATION | Re-run gate with evidence collection |

#### Cross-Reference Traversal

After both Gate 1 and Gate 2 pass, check the issue body for cross-references and verify those referenced issues have consistent state. This prevents scenarios where a spec references a plan that has been closed, or a plan references a spec that is still open, indicating inconsistent closure.

**Mandatory cross-reference check:**

```
For each candidate "already-implemented" issue:
  body = github_issue_read(method="get", issue_number=candidate)
  
  # Parse body for cross-reference patterns
  for pattern in [r"Spec:\s*#(\d+)", r"Plan:\s*#(\d+)", r"Implements\s*#(\d+)"]:
    for match in re.finditer(pattern, body):
      ref_num = int(match.group(1))
      ref_issue = github_issue_read(method="get", issue_number=ref_num)
      
      # Verify referenced issue has consistent state
      if ref_issue["state"] == "open" and candidate is classified as "already-implemented":
        # Referenced issue is open but candidate claims done — INCONSISTENT
        DOWNGRADE to "partially-implemented" or flag-for-review
      
      if ref_issue["state"] == "closed":
        # Verify referenced issue was legitimately closed (merged PR exists)
        # Reuse closed-issue verification logic from verify-authorization Step 5.4
```

**Cross-reference failure triggers:**

| Failure Condition | Classification | Action |
|-----------------|----------------|--------|
| Referenced issue is open | CONFLICTING | DOWNGRADE or flag-for-review — state mismatch |
| Referenced issue closed without merged PR | VERIFICATION-GAP | Flag for review — may be premature closure |
| Cross-reference 404 | MISSING-TRACEABILITY | Flag for developer — referenced issue doesn't exist |

**Key principle:** Even if Gate 1 and Gate 2 pass, cross-reference inconsistencies invalidate the "already-implemented" classification. The full issue graph must be consistent.

1. Identify which phases/criteria are already satisfied by reading the merged PR's diff
1. Extract remaining phases/criteria as the implementation scope
1. Include in execution plan with reduced scope: `#N (phases 2, 3 remaining — phase 1 done by PR #M)`
1. Sub-agent receives context: which phases are already done, what remains
1. Do NOT ask the developer to specify — auto-detect

#### Cross-Issue Sub-Issue Handling

When both a parent issue and its sub-issues are in the approved batch:

1. **Detect:** For each issue, check `github_issue_read(method=get_sub_issues)`. If any sub-issue number is also in the approved set, flag the pair.

1. **Default behavior:** Omit sub-issues from execution plan — parent's cascade covers them. Sub-agent for parent receives the full spec including all phases.

1. **Exception — isolated sub-issues:** If a sub-issue has a well-isolated scope (clear boundaries, no file overlap with parent's other phases), dispatch it to its own sub-agent for parallelism. Isolation criteria:

   - Touches completely different files from parent's other phases
   - No dependency on parent's other phases
   - Can be merged independently

1. **Edge case:** Parent is excluded (already implemented) but sub-issues aren't. Include sub-issues independently since parent's cascade doesn't apply.

#### Stale Spec Assumption Detection

When issue A's spec references code/functions/files that issue B modifies or deletes:

1. **Same intent (auto-resolvable):** Issue A says "delete `parseEnvFromOutput()`" and Issue B also deletes it → same intent, serialize, no conflict. B before A is sufficient; A's implementation will find the function already gone.

1. **Different intent (HALT for developer):** Issue A says "modify `parseEnvFromOutput()`" and Issue B deletes it → agent cannot determine if A's intent is still valid or if A should be adjusted. HALT and present to developer: "Issue #A references `parseEnvFromOutput()` but Issue #B deletes it. Should #A's spec be revised, or is the modification still needed?"

1. **Do NOT auto-re-stage when intent differs.** The agent must not assume it knows whether the developer wants the function modified or deleted.

#### Merge-Time Conflict Handling (Batch Assembly)

When two issues are independent during implementation but may conflict when squash-merged into the batch branch:

1. **Detect:** Issues that touch the same file in different sections or in overlapping but non-contradictory ways.

1. **Action — Batch assembly ordering:**

   - The `assemble-batch` task handles squash-merge ordering automatically
   - Issues are squash-merged into the batch branch in dependency/serial order
   - Later issues may need to resolve conflicts from earlier squash-merges during the batch assembly step
   - Tier 1-2 conflicts (formatting/whitespace): auto-resolve per `conflict-resolution` skill
   - Tier 3 conflicts (intent): HALT and flag for developer review

1. **Do NOT block execution.** All issues proceed with implementation immediately. Conflict resolution happens at batch assembly time, not during implementation.

1. **Note in execution plan:** "#A and #B may conflict at batch assembly — `assemble-batch` will handle merge ordering."

#### Revision Status Handling

When an issue in the batch has STATUS marked as `REVISED - NEEDS APPROVAL`:

1. **"approved #N" covers the revised spec.** The developer explicitly authorized the issue number. The spec body (including revisions) is authoritative.

1. **Flag in execution plan:** "#N has REVISED status — using revised spec as implementation scope."

1. **Remove `needs-approval` label** from the issue post-approval (per existing approval-gate rule: explicit auth overrides label).

### Step 0.5: Gate Evidence Audit (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL — STRUCTURAL CHECKPOINT: After Step 0 screening and BEFORE sub-issue expansion, the agent MUST verify that Gate 1 and Gate 2 were actually EXECUTED (not just read) for every issue classified as "already-implemented." This step is a mechanical audit — it checks whether evidence artifacts exist. It is NOT advisory text the agent can skip.**

**Why this step exists:** Previous fixes (#979, #980, PR #981) added Gate 1 and Gate 2 as text instructions to `pre-implementation-analysis.md`. Subsequent agent sessions read these instructions and skipped them anyway — no `get_sub_issues` calls, no per-sub-issue evidence, no success criteria verification. Text-based guardrails are insufficient; this step adds a structural checkpoint that halts advancement unless evidence exists.

**If NO issues were classified as "already-implemented":** This step passes trivially. Skip to Step 1.

**If ANY issues were classified as "already-implemented":** Perform the following audit:

#### GA-1: Verify Gate 1 Evidence Exists

For EACH issue classified as "already-implemented":

1. **Check sub-issue enumeration call:** Did you call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)` during Step 0 screening? If NO → STOP. Return to Step 0 and re-run Gate 1 for this issue before proceeding.

2. **Check per-sub-issue evidence:** For EACH sub-issue returned by `get_sub_issues`, did you produce a tool-call artifact (`github_issue_read(method=get, issue_number=<sub>)`) verifying its state? If NO → STOP. Return to Step 0 and re-run Gate 1 verification.

3. **Check closure legitimacy evidence:** For each closed sub-issue, did you search for merged PR evidence? If NO → STOP. Return to Step 0 and re-run Gate 1 closure legitimacy check.

#### GA-2: Verify Gate 2 Evidence Exists

For EACH issue classified as "already-implemented":

1. **Extract success criteria:** Did you read the issue body and extract every success criterion? If NO → STOP. Return to Step 0 and re-run Gate 2 for this issue.

2. **Verify each criterion:** For each success criterion, did you perform a direct verification action (read, grep, lint, test) against the current `dev` branch? If NO → STOP. Return to Step 0 and re-run Gate 2 verification.

3. **Evidence artifacts:** For each criterion, is there a tool-call artifact documenting the verification? If NO → STOP. Return to Step 0 and re-run with evidence collection.

#### GA-3: Produce the Gate Evidence Audit Table

**This table is a MANDATORY structural artifact.** `assemble-batch` (Step 1 of assemble-batch.md) checks for this table before proceeding. If the table is missing, `assemble-batch` returns here.

For all "already-implemented" classifications, produce:

```markdown
## Gate Evidence Audit Table

| Issue # | Sub-issues Enumerated? (Gate 1) | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? (Gate 2) | All Criteria Verified vs Codebase? | Final Classification |
|---------|----------------------------------|--------------------------|-------------------------------|--------------------------------------|-----------------------------------|---------------------|
| #N | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | already-implemented / partially-implemented / not-implemented-despite-closure |
```

**If ANY row has ❌ in columns 2-5:** That issue's classification is INVALID. It MUST be DOWNGRADED:
- ❌ in Gate 1 columns → DOWNGRADE to "partially-implemented" (sub-issues not verified)
- ❌ in Gate 2 columns → DOWNGRADE to "partially-implemented" or "not-implemented-despite-closure" (success criteria not verified)

**After downgrades:** Remove downgraded issues from "already-implemented" list. Add them to the "partially-implemented" list in the execution plan. Re-classify per Screening Categories table.

#### GA-4: Verify Audit Table Completeness

Before proceeding to Step 1:
1. The Gate Evidence Audit Table includes ALL issues classified as "already-implemented"
2. Every column has ✅ or ❌ (no blank entries)
3. All ❌ entries have been actioned (downgrade applied, issue moved to correct list)
4. The table is present in the chat output (not hidden in agent reasoning)

**If the table is incomplete:** HALT and complete it before proceeding.

### Step 1: Sub-Issue Expansion (MANDATORY)

**Every approved issue — whether single or batch — MUST undergo sub-issue expansion before classification.**

For each approved issue:

1. **Query sub-issues:** `github_issue_read(method="get_sub_issues", issue_number=N)`
2. **If sub-issues exist:** Expand the parent into its sub-issues as individual implementation items. The parent's spec body provides context; each sub-issue defines a phase.
3. **If no sub-issues (single-task):** The issue IS the flat item — no expansion needed.
4. **Build the flat item list:** Each sub-issue (or single issue) becomes one row in the execution plan. This is the input to `assemble-batch`.

**Why expansion is mandatory even for single issues:**

- Single issue = batch of one = one sub-agent in `assemble-batch`
- Eliminates forked code paths between "single issue" and "batch" workflows
- Sub-issue expansion produces a uniform data structure regardless of count

**Expansion rules:**

| Parent Type | Expansion Action |
|-----------|-------------------|
| Single-task spec (no sub-issues) | Item = the issue itself |
| Multi-task spec (has sub-issues) | Items = each sub-issue (parent provides context) |
| Multi-task spec with some sub-issues NOT in batch | Items = sub-issues in batch only |

### Step 2: Read All Remaining (Non-Excluded) Issues

For each issue that survived screening, read the full issue body and comments:

```python
for issue_number in remaining_issues:
    issue = github_issue_read(method="get", issue_number=issue_number)
    comments = github_issue_read(method="get_comments", issue_number=issue_number)
```

### Step 3: Classify Each Issue

Determine each issue's category:

| Category | Criteria | Action |
|----------|----------|--------|
| **Must-precede** | Issue A modifies files that Issue B also needs to edit | Execute A before B |
| **Independent** | Issue A and B touch completely different files | Can run in parallel |
| **Conflict-risk** | Issue A and B both modify overlapping files | Serialize or coordinate |
| **Meta/Non-code** | Issue describes behavior/rule with NO code changes | Exclude from implementation |

**Classification heuristics:**

1. **File overlap analysis**: Scan each issue's body for file path references, directory references, or component names that map to files in the repo.
1. **Skill overlap**: Issues using the same skills that mutate shared state (e.g., both update `000-critical-rules.md`) are conflict-risk.
1. **Logical ordering**: When Issue A's output becomes Issue B's input (e.g., A creates a skill that B references), A must precede B.
1. **Scope analysis**: `.opencode/`-only changes vs `src/` changes vs doc-only changes.

**Add edges from pre-analysis screening:**

- Same-intent stale assumption pairs → must-precede edge (the issue providing the canonical change precedes)
- Cross-issue sub-issue pairs → dependency edge (parent covers sub-issues unless isolated)

### Step 4: Build Dependency Graph

Create a directed graph where:

- Nodes = remaining (non-excluded) approved issues
- Edges = "must-precede" relationships (including stale-assumption and cross-sub-issue edges from Step 0)
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

When any of these triggers fire, HALT and present the conflict to the developer with a clear question. Do NOT attempt to auto-resolve.

### Step 7: Capture Dev Base Hash (Before Dispatch)

Before dispatching any parallel worktrees, the orchestrating agent MUST capture the current dev branch hash:

```bash
git rev-parse origin/dev
```

This `dev_base_hash` MUST be included in the dispatch context for each parallel issue. See Step 7 for the complete dispatch context schema.

### Step 8: Dispatch Context for Parallel Issues

For each issue in a parallel-safe group, the dispatch context MUST include worktree information:

```yaml
# Dispatch Context Per Issue
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
- Detected via `github_issue_read(method=get_sub_issues)` for each issue

### Merge-Time Conflict Detection

Issues have a merge-time conflict risk when:

- They touch the same file but in different sections or with non-contradictory changes
- They are independent during implementation but may produce overlapping diffs
- This is distinct from conflict-risk (which affects implementation order)

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
- Skip Gate 1 (sub-issue enumeration) for any candidate "already-implemented" issue
- Classify an issue as "already-implemented" while it has open sub-issues or unverified success criteria
- Proceed to Step 1 (sub-issue expansion) without completing the Gate Evidence Audit Table for all "already-implemented" classifications
- Classify an issue as "already-implemented" without a corresponding `get_sub_issues` tool-call artifact in the current session

**Always:**

- Run pre-analysis screening (Step 0) before classification
- Present the full dependency graph to the developer in chat
- Classify every issue before execution
- Execute must-precede issues first
- Group independent issues for parallel dispatch
- Exclude non-actionable issues with explicit reason
- Report each issue's classification in the execution plan
- Proceed immediately to `assemble-batch` after presenting the plan
- Auto-detect partially-implemented issues (no developer input needed)
- Call `github_issue_read(method=get_sub_issues)` for every candidate "already-implemented" issue (Gate 1)
- Verify each success criterion against the live codebase before classifying as "already-implemented" (Gate 2)
- Complete the Gate Evidence Audit Table (Step 0.5) before proceeding to Step 1
- Produce a per-issue `get_sub_issues` tool-call artifact in the current session for every "already-implemented" classification
- HALT for developer review only for unresolvable conflicts and different-intent stale assumptions

## Adversarial Interdependency Verification

**Before trusting spec-claimed dependencies, verify them against actual codebase state.** Specs may claim "Issue A must precede Issue B" based on assumed file overlap that doesn't exist, or miss dependencies that do exist.

### Verify File Overlap Claims Against Actual Code

```
For each spec claiming file overlap with another spec:
  - Extract file paths mentioned in each spec body
  - Use srclight_get_dependents or srclight_get_callers to verify actual import/call chains
  - If spec claims "A modifies X which B needs" but srclight shows no dependency → VERIFICATION-GAP
  - If srclight shows dependency not mentioned in either spec → MISSING-ELEMENT
```

**Evidence artifact:** `srclight_get_dependents` and `srclight_get_callers` results for symbols mentioned in specs.

### Verify Must-Precede Claims

```
For each must-precede relationship claimed in specs:
  - Check if A actually creates/modifies symbols that B uses
  - srclight_get_callers(symbol_name="<symbol_from_A>", project="<project>")
  - If callers include code from B's scope → dependency verified
  - If callers do NOT include code from B's scope → VERIFICATION-GAP (may not actually need serialization)
```

**Evidence artifact:** Caller graph results showing whether the claimed dependency exists in actual code.

### Verify Independence Claims

```
For each pair of issues claimed as "independent":
  - Use srclight_get_dependents(symbol_name="<key_symbol>", project="<project>", transitive=True)
  - If transitive dependents include code from the other issue's scope → NOT independent
  - Downgrade from "parallel-safe" to "conflict-risk" or "must-precede"
```

**Evidence artifact:** Transitive dependency graph showing whether claimed independence holds.

### Verify Code References Exist

```
For each file path or symbol mentioned in any spec:
  - File paths: verify with glob or read that the file exists
  - Symbol names: verify with srclight_get_signature that the symbol exists
  - If file/symbol does not exist → VERIFICATION-GAP (flag-for-review: planned but not yet implemented, or typo)
```

**Evidence artifact:** Search/glob results confirming existence or absence of referenced code.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| File overlap claimed but no actual dependency | VERIFICATION-GAP | flag-for-review | Re-classify as independent unless other evidence |
| Dependency exists but not mentioned in specs | MISSING-ELEMENT | conditional | Add to dependency graph, adjust execution order |
| Independence claimed but transitive dependency exists | CONFLICTING | conditional | Downgrade to conflict-risk or must-precede |
| Code reference to non-existent file/symbol | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or typo |
