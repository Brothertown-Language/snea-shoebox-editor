# Task: screen-issue-gate1

## Purpose

First gate of per-issue screening for pre-implementation analysis. Read issue body/comments, classify against screening categories, and execute Gate 1 (sub-issue enumeration). This gate covers Steps 1-3 and all screening classification logic.

## Entry Criteria

- Single issue number to screen (passed via dispatch context)
- Issue has been verified by `verify-authorization`
- User has explicitly authorized implementation
- `<github.owner>` and `<github.repo>` available from dispatch context

## Exit Criteria

- Issue read with body and comments
- Screening category assigned (already-implemented, superseded, moot, stale assumptions, partial implementation, revision status, meta/non-code, not-implemented-despite-closure, overlap, conflict, independent)
- Gate 1 executed if issue is a candidate for "already-implemented" classification
- Gate 1 evidence audit (GA-1) completed
- Result passed to gate2 for continuation

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
| **Superseded by work peer** | FULL-SUPERSESSION: Issue B's file_references ⊇ A's, B's scope fully encompasses A's, all A's success criteria ⊇ B's | EXCLUDE A, note "superseded by #B" | No |
| **Overlap with work peer** | PARTIAL-OVERLAP: Shared file_references or symbol_references, different core concerns | INCLUDE both, flag for merge-time coordination | No |
| **Conflict with work peer** | CONFLICT-RISK: Same files modified with conflicting intent | Serialize, flag for resolution order; ONLY HALT if success criteria are contradictory | No (auto-resolvable) / Yes (contradictory criteria) |
| **Independent** | INDEPENDENT: No meaningful file/symbol/concern overlap | Include independently | No |
| **Moot** | Referenced files/code restructured since spec creation; no remaining success criteria are achievable | Exclude, mark "moot" with reason | No |
| **Stale assumptions** | Issue A references code/functions/files that Issue B modifies or deletes | Re-stage A after B only if same intent; otherwise HALT for developer | Yes (if different intent) / No (if same intent) |
| **Conflicting (auto-resolvable)** | Issues touch same files, can be serialized (different intent, serializable) | Serialize in correct order | No |
| **Conflicting (unresolvable)** | Contradictory success criteria | Cannot auto-resolve | **Yes** — HALT |
| **Meta/Non-code** | No code changes required | Exclude, mark "no code changes" | No |
| **Revision status** | STATUS contains `REVISED - NEEDS APPROVAL` | Flag in execution plan, remove `needs-approval` label | No |

#### Screening Outcomes

- **INCLUDE**: independent (no meaningful overlap), overlap-with-work-peer (partially overlapping, coordinated via merge-time ordering)
- **EXCLUDE**: already-implemented (verified via merged PR + sub-issues closed via merged PR + success criteria verified), superseded (FULL-SUPERSESSION), moot, meta/non-code
- **REOPEN/RE-CLASSIFY**: not-implemented-despite-closure (closed but Gate 1 or Gate 2 failed — include remaining work)
- **REDUCE SCOPE**: partially-implemented (include remaining phases only)
- **RECONCILE**: status inconsistencies detected (issue state contradicts verified implementation state) — set `requires_reconciliation: true` in result contract; `pre-implementation-analysis` Step 0.7 invokes `reconcile-issue-graph` to auto-correct; developer is NOT asked
- **SERIALIZE**: same-intent stale assumptions, auto-resolvable conflicts
- **HALT**: different-intent stale assumptions, unresolvable conflicts

#### Superseded Detection (Four-Tier Classification)

Issue A is superseded by work peer B when overlap is detected. Classify the overlap:

| Classification | Criteria | Action |
|---------------|----------|--------|
| **FULL-SUPERSESSION** | B's file_references ⊇ A's, B's scope description fully encompasses A's, all A's success criteria ⊇ B's | EXCLUDE A, note "superseded by #B" — autonomous, no developer needed |
| **PARTIAL-OVERLAP** | A and B share file_references or symbol_references but have different core concerns | INCLUDE both, flag for merge-time coordination — note shared files in execution plan |
| **CONFLICT-RISK** | A and B modify same files in conflicting ways (same section, different intent) | INCLUDE both, serialize in execution plan, flag for resolution order |
| **INDEPENDENT** | No meaningful file/symbol/concern overlap | INCLUDE both independently |

**Previous behavior (superseded detection):** Previously, the only action for overlapping issues was "superseded" or "HALT for developer review." The four-tier model provides autonomous classification:
- FULL-SUPERSESSION replaces the old binary "superseded → exclude"
- PARTIAL-OVERLAP replaces the old "overlapping/conflicting → HALT for developer" — the agent now classifies and coordinates
- CONFLICT-RISK replaces the old "conflicting (unresolvable) → HALT" — only genuinely unresolvable conflicts (contradictory success criteria that cannot be serialized) escalate to the developer
- INDEPENDENT is the new explicit classification for zero overlap

**Ambiguous supersession** (partial overlap where it is unclear which spec is canonical): This remains a HALT condition for the developer. When FULL-SUPERSESSION cannot be determined because neither spec fully covers the other, the agent cannot decide which is canonical.

**Overlap analysis uses file_references, symbol_references, and concern boundaries — NOT just titles/objectives.** This is the key improvement over the previous behavior: overlap is detected at the code/scope level, not just the prose level.

#### Moot Detection

An issue is moot when:

- Its spec references files/directories that have been restructured or removed since spec creation
- None of its remaining success criteria are achievable given the current codebase state
- The problem it describes no longer exists

#### Stale Assumption Detection

An issue has stale assumptions when:

- Its spec references specific function names, class names, or file paths that another issue in the work set modifies or deletes
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
3. **CHECK CLOSURE LEGITIMACY:** For each closed sub-issue, search for merged PR evidence via `github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{<github.owner>}/{<github.repo>}")`. If closed without merged PR and `state_reason != "not_planned"` → DOWNGRADE to "partially-implemented"
4. **CHECK OPEN SUB-ISSUES:** If ANY sub-issue is open → the parent CANNOT be "already-implemented" — DOWNGRADE to "partially-implemented"
5. **PRODUCE EVIDENCE:** Each sub-issue MUST produce a tool-call artifact showing its state was verified. Blanket assertions ("all sub-issues checked") WITHOUT per-sub-issue tool-call evidence are VERIFICATION-GAP findings

**Already-Implemented Sub-Issue Verification:**

```
For each sub-issue of the candidate "already implemented" issue:
  child = github_issue_read(method="get", issue_number=sub_issue_number)

  if child.state == "closed":
    state_reason = child.get("state_reason", "")
    prs = github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{<github.owner>}/{<github.repo>}")
    merged_pr_found = False
    for pr in prs:
      pr_detail = github_pull_request_read(method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=pr["number"])
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

#### Gate 1 Evidence Audit (GA-1)

1. **Check sub-issue enumeration call:** Did you call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)` during screening? If NO → STOP. Return to Step 3 and re-run Gate 1 before proceeding.

2. **Check per-sub-issue evidence:** For EACH sub-issue returned by `get_sub_issues`, did you produce a tool-call artifact (`github_issue_read(method=get, issue_number=<sub>)`) verifying its state? If NO → STOP. Return to Step 3 and re-run Gate 1 verification.

3. **Check closure legitimacy evidence:** For each closed sub-issue, did you search for merged PR evidence? If NO → STOP. Return to Step 3 and re-run Gate 1 closure legitimacy check.

**If ANY Gate 1 check has ❌:** The classification is INVALID. DOWNGRADE to "partially-implemented" and proceed to gate2.

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`