# Task: screen-issue

## Purpose

Per-issue screening for pre-implementation analysis. Screen a single approved issue against screening categories (already-implemented, superseded, moot, stale assumptions, partial implementation, revision status, meta/non-code, cross-issue sub-issue handling). Produce a compact result contract for cross-issue merge.

## Entry Criteria

- Single issue number to screen (passed via dispatch context)
- Issue has been verified by `verify-authorization`
- User has explicitly authorized implementation
- `GIT_OWNER` and `GIT_REPO` available from dispatch context

## Exit Criteria

- Issue classified into one screening category
- Gate 1 (sub-issue enumeration) executed if applicable
- Gate 2 (success criteria verification) executed if applicable
- Compact result contract produced (~100-500 words, YAML-structured)

## Procedure

### Step 1: Read Issue Body and Comments

Read the full issue body and all comments for the target issue.

```
issue = github_issue_read(method="get", issue_number=<target>)
comments = github_issue_read(method="get_comments", issue_number=<target>)
```

### Step 2: Screening Categories Check

Check each category in order:

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
| **Revision status** | STATUS contains `REVISED - NEEDS APPROVAL` | Flag in execution plan, remove `needs-approval` label | No |

#### Screening Outcomes

- **EXCLUDE**: already-implemented (verified via merged PR + sub-issues closed via merged PR + success criteria verified), superseded, moot, meta/non-code
- **REOPEN/RE-CLASSIFY**: not-implemented-despite-closure (closed but Gate 1 or Gate 2 failed — include remaining work)
- **REDUCE SCOPE**: partially-implemented (include remaining phases only)
- **RECONCILE**: status inconsistencies detected (issue state contradicts verified implementation state) — set `requires_reconciliation: true` in result contract; `pre-implementation-analysis` Step 0.7 invokes `reconcile-issue-graph` to auto-correct; developer is NOT asked
- **SERIALIZE**: same-intent stale assumptions, auto-resolvable conflicts
- **HALT**: different-intent stale assumptions, unresolvable conflicts

#### Superseded Detection

Issue A is superseded by batch peer B when:

- B's file list is a superset of A's file list
- B's scope description fully encompasses A's scope
- All of A's success criteria would be met by implementing B

**Ambiguous supersession** (partial overlap, unclear which is canonical): HALT for developer review.

#### Moot Detection

An issue is moot when:

- Its spec references files/directories that have been restructured or removed since spec creation
- None of its remaining success criteria are achievable given the current codebase state
- The problem it describes no longer exists

#### Stale Assumption Detection

An issue has stale assumptions when:

- Its spec references specific function names, class names, or file paths that another issue in the batch modifies or deletes
- The reference is integral to the issue's implementation instructions (not just background context)

**Same intent (auto-resolvable):** Both issues want the same outcome for the referenced code.
**Different intent (HALT):** The issues have conflicting goals for the referenced code.

When issue A's spec references code/functions/files that issue B modifies or deletes:

1. **Same intent (auto-resolvable):** Issue A says "delete `parseEnvFromOutput()`" and Issue B also deletes it → same intent, serialize, no conflict. B before A is sufficient; A's implementation will find the function already gone.

1. **Different intent (HALT for developer):** Issue A says "modify `parseEnvFromOutput()`" and Issue B deletes it → agent cannot determine if A's intent is still valid or if A should be adjusted. HALT and present to developer: "Issue #A references `parseEnvFromOutput()` but Issue #B deletes it. Should #A's spec be revised, or is the modification still needed?"

1. **Do NOT auto-re-stage when intent differs.** The agent must not assume it knows whether the developer wants the function modified or deleted.

#### Meta/Non-Code Detection

An issue is meta/non-code when:

- The body describes behavioral rules without file modifications
- The issue tracks observability or enforcement without requiring code changes
- The "implementation" is just acknowledging a pattern, not writing code
- All success criteria are satisfied by existence of documentation or rules already in place

#### Revision Status Handling

When an issue has STATUS marked as `REVISED - NEEDS APPROVAL`:

1. **"approved #N" covers the revised spec.** The developer explicitly authorized the issue number. The spec body (including revisions) is authoritative.

1. **Flag in execution plan:** "#N has REVISED status — using revised spec as implementation scope."

1. **Remove `needs-approval` label** from the issue post-approval (per existing approval-gate rule: explicit auth overrides label).

#### Partial Implementation Detection

When a merged PR references the issue but not all success criteria are met:

1. Identify which phases/criteria are already satisfied by reading the merged PR's diff
1. Extract remaining phases/criteria as the implementation scope
1. Include in execution plan with reduced scope: `#N (phases 2, 3 remaining — phase 1 done by PR #M)`
1. Sub-agent receives context: which phases are already done, what remains
1. Do NOT ask the developer to specify — auto-detect

### Step 3: Gate 1 — Sub-Issue Enumeration (MANDATORY for already-implemented candidates)

**🚫 CRITICAL — ZERO TOLERANCE: Before classifying ANY issue as "already-implemented," the agent MUST call `github_issue_read(method=get_sub_issues)` for that issue. Skipping this gate is a CRITICAL GUIDELINE VIOLATION. If `get_sub_issues` is not called, the classification is INVALID.**

This gate ensures the agent cannot skip the sub-issue traversal. The section below describes what to check; this gate enforces that the check ACTUALLY HAPPENS.

**Mandatory gate procedure — every candidate "already-implemented" issue MUST pass through ALL steps:**

1. **ENUMERATE:** Call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)` — no exceptions, no shortcuts
2. **VERIFY EACH CHILD:** For EVERY sub-issue returned, call `github_issue_read(method=get, issue_number=<sub_issue_number>)` — do NOT trust cached state; verify against live GitHub API
3. **CHECK CLOSURE LEGITIMACY:** For each closed sub-issue, search for merged PR evidence via `github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{GIT_OWNER}/{GIT_REPO}")`. If closed without merged PR and `state_reason != "not_planned"` → DOWNGRADE to "partially-implemented"
4. **CHECK OPEN SUB-ISSUES:** If ANY sub-issue is open → the parent CANNOT be "already-implemented" — DOWNGRADE to "partially-implemented"
5. **PRODUCE EVIDENCE:** Each sub-issue MUST produce a tool-call artifact showing its state was verified. Blanket assertions ("all sub-issues checked") WITHOUT per-sub-issue tool-call evidence are VERIFICATION-GAP findings

**Already-Implemented Sub-Issue Verification:**

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
      DOWNGRADE to "partially-implemented" or "scope-reduced"

    if state_reason == "not_planned":
      MARK as "scope-reduced — sub-issue #{sub_issue_number} intentionally not planned"

  elif child.state == "open":
    DOWNGRADE to "partially-implemented"
```

**Gate 1 failure triggers:**

| Failure Condition | Classification | Action |
|-----------------|----------------|--------|
| `get_sub_issues` not called | CRITICAL VIOLATION | Classification is INVALID — retry with gate |
| Open sub-issue found | DOWNGRADE | "partially-implemented" — open sub-issue remains |
| Sub-issue closed without merged PR | DOWNGRADE | "partially-implemented" — premature closure suspected |
| Sub-issue closed as "not_planned" | SCOPE-REDUCE | "scope-reduced" — exclude intentionally skipped sub-issue |
| No evidence artifacts produced | VERIFICATION-GAP | Re-run gate with evidence collection |

### Step 4: Gate 2 — Success Criteria Verification (MANDATORY after Gate 1 passes)

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

### Step 5: Cross-Reference Traversal

After both Gate 1 and Gate 2 pass, check the issue body for cross-references and verify those referenced issues have consistent state. This prevents scenarios where a spec references a plan that has been closed, or a plan references a spec that is still open, indicating inconsistent closure.

**Mandatory cross-reference check:**

```
For each candidate "already-implemented" issue:
  body = github_issue_read(method="get", issue_number=candidate)
  
  for pattern in [r"Spec:\s*#(\d+)", r"Plan:\s*#(\d+)", r"Implements\s*#(\d+)"]:
    for match in re.finditer(pattern, body):
      ref_num = int(match.group(1))
      ref_issue = github_issue_read(method="get", issue_number=ref_num)
      
      if ref_issue["state"] == "open" and candidate is classified as "already-implemented":
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

### Step 6: Gate Evidence Audit

After screening, produce the Gate Evidence Audit for this single issue.

#### GA-1: Verify Gate 1 Evidence Exists

1. **Check sub-issue enumeration call:** Did you call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)` during screening? If NO → STOP. Return to Step 3 and re-run Gate 1 before proceeding.

2. **Check per-sub-issue evidence:** For EACH sub-issue returned by `get_sub_issues`, did you produce a tool-call artifact (`github_issue_read(method=get, issue_number=<sub>)`) verifying its state? If NO → STOP. Return to Step 3 and re-run Gate 1 verification.

3. **Check closure legitimacy evidence:** For each closed sub-issue, did you search for merged PR evidence? If NO → STOP. Return to Step 3 and re-run Gate 1 closure legitimacy check.

#### GA-2: Verify Gate 2 Evidence Exists

1. **Extract success criteria:** Did you read the issue body and extract every success criterion? If NO → STOP. Return to Step 4 and re-run Gate 2 for this issue.

2. **Verify each criterion:** For each success criterion, did you perform a direct verification action (read, grep, lint, test) against the current `dev` branch? If NO → STOP. Return to Step 4 and re-run Gate 2 verification.

3. **Evidence artifacts:** For each criterion, is there a tool-call artifact documenting the verification? If NO → STOP. Return to Step 4 and re-run with evidence collection.

#### GA-3: Produce the Gate Evidence Audit Row

For this issue, produce the audit row:

```markdown
| Issue # | Sub-issues Enumerated? (Gate 1) | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? (Gate 2) | All Criteria Verified vs Codebase? | Final Classification |
|---------|----------------------------------|--------------------------|-------------------------------|--------------------------------------|-----------------------------------|---------------------|
| #N | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | already-implemented / partially-implemented / not-implemented-despite-closure |
```

**If ANY column has ❌ in columns 2-5:** The classification is INVALID. It MUST be DOWNGRADED:
- ❌ in Gate 1 columns → DOWNGRADE to "partially-implemented" (sub-issues not verified)
- ❌ in Gate 2 columns → DOWNGRADE to "partially-implemented" or "not-implemented-despite-closure" (success criteria not verified)

#### GA-4: Verify Audit Row Completeness

1. The audit row exists for this issue
2. Every column has ✅ or ❌ (no blank entries)
3. All ❌ entries have been actioned (downgrade applied, classification corrected)
4. The row is included in the result contract

**If the row is incomplete:** HALT and complete it before producing the result contract.

### Step 7: Sub-Issue Expansion

Expand the issue into its sub-issues (flat item list):

1. **Query sub-issues:** `github_issue_read(method="get_sub_issues", issue_number=N)`
2. **If sub-issues exist:** Expand the parent into its sub-issues as individual implementation items. The parent's spec body provides context; each sub-issue defines a phase.
3. **If no sub-issues (single-task):** The issue IS the flat item — no expansion needed.
4. **Build the flat item list:** Each sub-issue (or single issue) becomes one flat item. This is the input to the merge phase.

**Expansion rules:**

| Parent Type | Expansion Action |
|-----------|-------------------|
| Single-task spec (no sub-issues) | Item = the issue itself |
| Multi-task spec (has sub-issues) | Items = each sub-issue (parent provides context) |
| Multi-task spec with some sub-issues NOT in batch | Items = sub-issues in batch only |

### Step 8: Cross-Issue Sub-Issue Handling

When both a parent and its sub-issues are in the approved batch:

1. **Detect:** If any sub-issue number is also in `batch_peers`, flag the pair.

1. **Default behavior:** Omit sub-issues from execution plan — parent's cascade covers them. Sub-agent for parent receives the full spec including all phases.

1. **Exception — isolated sub-issues:** If a sub-issue has a well-isolated scope (clear boundaries, no file overlap with parent's other phases), dispatch it to its own sub-agent for parallelism. Isolation criteria:

   - Touches completely different files from parent's other phases
   - No dependency on parent's other phases
   - Can be merged independently

1. **Edge case:** Parent is excluded (already implemented) but sub-issues aren't. Include sub-issues independently since parent's cascade doesn't apply.

### Step 9: Extract File and Symbol References

For cross-issue dependency analysis (done by the merge phase), extract:

- File paths mentioned in the issue body
- Symbol names (functions, classes) referenced
- Skill/directory references

Use `srclight_get_dependents` or `srclight_get_callers` where possible to verify actual dependencies:

```
For each file path or symbol mentioned in the issue:
  - File paths: verify with glob or read that the file exists
  - Symbol names: verify with srclight_get_signature that the symbol exists
  - For key symbols: srclight_get_dependents(symbol_name="<symbol>", project="<project>", transitive=True)
  - For claimed dependencies: srclight_get_callers(symbol_name="<symbol>", project="<project>")
```

**Evidence artifact:** Search/glob/srclight results confirming existence or absence of referenced code.

### Step 10: Produce Result Contract

The result contract MUST be YAML-structured, compact (~100-500 words):

```yaml
status: DONE | DONE_WITH_CONCERNS | BLOCKED | OVERFLOW
task: screen-issue
issue_number: <N>
classification: included | excluded | scope-reduced
category: <screening category, e.g. already-implemented, superseded, moot, partially-implemented, meta-non-code, null>
exclude_reason: <reason if excluded, null if included>
reduce_reason: <reason if scope-reduced, null otherwise>
reduced_scope:
  completed_phases: []
  remaining_phases: []
flat_items:
  - issue: <N or sub-issue number>
    title: <title>
    phase: <phase description>
gate_evidence:
  gate1_called: true | false
  gate1_sub_issues_verified: true | false
  gate1_closure_legitimacy: true | false
  gate2_criteria_extracted: true | false
  gate2_criteria_verified: true | false
  final_classification: already-implemented | partially-implemented | included | not-implemented-despite-closure
requires_developer: true | false
developer_reason: <reason if true, null if false>
requires_reconciliation: true | false
reconciliation_reason: <reason if true, null if false>
file_references:
  - <file path>
symbol_references:
  - <symbol name>
concerns:
  - <concern text, if any>
```

## Dispatch Context Schema

```yaml
issue_number: <N>
batch_peers: [<list of other issue numbers in batch>]
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```

## Red Flags

**Never:**

- Skip Gate 1 (sub-issue enumeration) for any candidate "already-implemented" issue
- Classify an issue as "already-implemented" while it has open sub-issues or unverified success criteria
- Proceed past Gate Evidence Audit without completing the audit row for all "already-implemented" classifications
- Classify an issue as "already-implemented" without a corresponding `get_sub_issues` tool-call artifact in the current session
- Auto-re-stage issues with different-intent stale assumptions
- Claim "all criteria met" without per-criterion tool-call evidence
- Skip cross-reference traversal after Gate 1 and Gate 2 pass
- Trust cached sub-issue state or closure status without live API verification
- Set `requires_developer: true` for status inconsistencies (reopened after merge, premature closure) — these are deterministic and should use `requires_reconciliation: true` instead

**Always:**

- Call `github_issue_read(method=get_sub_issues)` for every candidate "already-implemented" issue (Gate 1)
- Verify each success criterion against the live codebase before classifying as "already-implemented" (Gate 2)
- Complete the Gate Evidence Audit row (Step 6) before producing the result contract
- Produce a per-issue `get_sub_issues` tool-call artifact in the current session for every "already-implemented" classification
- HALT for developer review only for unresolvable conflicts and different-intent stale assumptions
- Auto-detect partially-implemented issues (no developer input needed)
- Set `requires_reconciliation: true` (NOT `requires_developer: true`) when issue state contradicts verified implementation state — `reconcile-issue-graph` handles this deterministically
- Set `requires_developer: true` ONLY for the following conditions (exhaustive list):
  1. Unresolvable conflicts: contradictory success criteria between batch issues
  2. Different-intent stale assumptions: Issue A references code Issue B deletes, with different goals
  3. Ambiguous supersession: partial scope overlap, unclear which is canonical
  4. `Uncertain` reconciliation findings after `reconcile-issue-graph` runs
  5. Authorization scope gap: user approves an issue but the implementable target is unclear AND output lineage cascade (Step 2.1) does NOT apply

**DEFAULT FAILSAFE:** If a screening sub-agent encounters a scenario not covered by conditions 1-5, it must RESOLVE autonomously (classify with best judgment) rather than defaulting to `requires_developer: true`. Escalating undefined scenarios to the developer is the "Pushing Agent Intelligence Decisions" anti-pattern. Set `requires_developer: true` ONLY when the developer's intent is genuinely ambiguous and cannot be inferred from context.
- Produce the result contract as the final output of this task