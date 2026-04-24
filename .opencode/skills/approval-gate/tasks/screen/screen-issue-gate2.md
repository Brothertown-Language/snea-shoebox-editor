# Task: screen-issue-gate2

## Purpose

Second gate of per-issue screening for pre-implementation analysis. Execute Gate 2 (success criteria verification), cross-reference traversal, gate evidence audit, sub-issue expansion, cross-issue handling, file/symbol extraction, and produce the final result contract. This gate covers Steps 4-10.

## Entry Criteria

- Gate 1 (screen-issue-gate1) has completed for the issue
- Issue is a candidate for "already-implemented" classification OR screening category has been assigned
- Gate 1 evidence audit (GA-1) completed (or issue is not an "already-implemented" candidate)
- `<github.owner>` and `<github.repo>` available from dispatch context

## Exit Criteria

- Gate 2 executed if issue is an "already-implemented" candidate
- Cross-reference traversal completed
- Gate evidence audit (GA-2 through GA-4) completed
- Sub-issues expanded into flat item list
- Cross-issue sub-issue handling resolved
- File and symbol references extracted
- Compact result contract produced (≈100-500 words, YAML-structured)

## Procedure

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
3. **If no sub-issues (work-of-1):** The issue IS the flat item — no expansion needed.
4. **Build the flat item list:** Each sub-issue (or single issue) becomes one flat item. This is the input to the merge phase.

**Expansion rules:**

| Parent Type | Expansion Action |
|-----------|-------------------|
| Single-task spec (no sub-issues) | Item = the issue itself |
| Multi-task spec (has sub-issues) | Items = each sub-issue (parent provides context) |
| Multi-task spec with some sub-issues NOT in work set | Items = sub-issues in work set only |

### Step 8: Cross-Issue Sub-Issue Handling

When both a parent and its sub-issues are in the approved work set:

1. **Detect:** If any sub-issue number is also in `work_peers`, flag the pair.

2. **Default behavior:** Omit sub-issues from execution plan — parent's cascade covers them. Sub-agent for parent receives the full spec including all phases.

3. **Exception — isolated sub-issues:** If a sub-issue has a well-isolated scope (clear boundaries, no file overlap with parent's other phases), dispatch it to its own sub-agent for parallelism. Isolation criteria:

   - Touches completely different files from parent's other phases
   - No dependency on parent's other phases
   - Can be merged independently

4. **Edge case:** Parent is excluded (already implemented) but sub-issues aren't. Include sub-issues independently since parent's cascade doesn't apply.

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

The result contract MUST be YAML-structured, compact (≈100-500 words):

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
work_peers: [<list of other issue numbers in work set>]
authorization_scope:   # From verify-authorization Step 2.0
gap_fill_actions: []  # Derived from authorization_scope
session_vars:
  github.owner: <from-session>
  github.repo: <from-session>
  dev.name: <from-session>
  dev.email: <from-session>
  worktree.path: <from-session>
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
  1. Unresolvable conflicts: contradictory success criteria between issues in authorization set
  2. Different-intent stale assumptions: Issue A references code Issue B deletes, with different goals
  3. Ambiguous supersession: partial scope overlap, unclear which is canonical
  4. `Uncertain` reconciliation findings after `reconcile-issue-graph` runs
  5. Authorization scope gap: user approves an issue but the implementable target is unclear AND output lineage cascade (Step 2.1) does NOT apply

**DEFAULT FAILSAFE:** If a screening sub-agent encounters a scenario not covered by conditions 1-5, it must RESOLVE autonomously (classify with best judgment) rather than defaulting to `requires_developer: true`. Escalating undefined scenarios to the developer is the "Pushing Agent Intelligence Decisions" anti-pattern. Set `requires_developer: true` ONLY when the developer's intent is genuinely ambiguous and cannot be inferred from context.

### Autonomous Resolution

**Reference: `000-critical-rules.md` §"Pushing Agent Intelligence Decisions to the User"**

Screening classification decisions are agent intelligence concerns, not developer judgment calls. The `requires_developer: true` field in the result contract MUST be set to `true` ONLY for the exhaustive conditions listed in the Red Flags section (conditions 1-5). All other scenarios are resolved autonomously.

**PROHIBITED questions (agent MUST decide, never ask):**

- "Should this be single-task or multi-task?" → agent decides based on scope
- "Is this a small change or a big one?" → agent assesses from screening
- "Do you want this as one spec or multiple?" → agent classifies
- "How should we handle this partially-implemented issue?" → scope-reduce and continue
- "Should we re-plan?" → yes, if authorization says "re-plan as needed"
- "How should we close this already-implemented issue?" → via verify-already-implemented or via referenced spec-fix

**When `requires_developer: true` is genuinely needed (exhaustive list):**

1. **Unresolvable conflicts:** Contradictory success criteria between issues in the authorization set
2. **Different-intent stale assumptions:** Issue A references code Issue B deletes, with different goals
3. **Ambiguous supersession:** Partial scope overlap where it is unclear which spec is canonical
4. **Uncertain reconciliation findings:** `reconcile-issue-graph` produced `requires_dev_action` with conflicting signals
5. **Authorization scope gap:** User approves an issue but the implementable target is unclear AND output lineage cascade does NOT apply

**DEFAULT FAILSAFE:** If a scenario is NOT covered by conditions 1-5, RESOLVE autonomously (classify with best judgment) rather than defaulting to `requires_developer: true`. Per `000-critical-rules.md` §"Pushing Agent Intelligence Decisions to the User," structural decisions are agent intelligence concerns.

### Screening Results Are Not Decision Points

Screening sub-agents produce result contracts that feed into `pre-implementation-analysis`. The orchestrator assembles results and proceeds to the dispatch chain automatically. Key rules:

1. **Screening results are data, not decisions.** The result contract is consumed by `pre-implementation-analysis` which auto-dispatches to `assemble-work`. No human review of screening results is required unless `requires_developer: true`.
2. **Individual screen-issue sub-agents MUST NOT halt the orchestrator.** They return result contracts and terminate. The orchestrator processes all contracts before any action.
3. **The orchestrator assembles results and proceeds.** Presentation of assembled results is informational — not a gate, not a decision point, not a halt point. See `pre-implementation-analysis.md` §"Post-Analysis Dispatch (MANDATORY)" for enforcement.

### Gap-Fill Override for Screening Sub-Agents

**When `authorization_scope` is passed via dispatch context and its gap-fill actions include `auto_create_spec`, screening sub-agents MUST NOT block on missing spec artifacts (including the fix-spec requirement for bug reports).** The missing spec is a gap-fill trigger handled by `verify-authorization` Step 5c, not a screening blocking condition.

Screening sub-agents classify issues (include/exclude/reduce-scope). They do NOT enforce artifact requirements that are covered by the authorization scope's gap-fill cascade. A bug report without a fix-spec is classified normally (e.g., "included") — the fix-spec creation is deferred to the gap-fill cascade.

**Procedure:**

```python
# When evaluating a bug report during screening:
if is_bug_report and not has_fix_spec:
    if "auto_create_spec" in dispatch_context.get("gap_fill_actions", []):
        # Do NOT flag as blocking — gap-fill handles this
        # Classify normally (include/reduce-scope/etc.)
        pass
    else:
        # No gap-fill coverage — flag in result contract
        result_contract["concerns"].append(
            "Bug report lacks fix-spec; scope has no auto_create_spec gap-fill"
        )
```

**The `gap_fill_actions` field MUST be passed in the dispatch context** when `authorization_scope >= for_implementation`. See `verify-authorization.md` Step 2.0 for the `GAP_FILL` mapping.

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`