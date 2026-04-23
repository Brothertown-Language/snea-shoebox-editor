# Task: cleanup

## Purpose

Delete merged branches after PR merge, clean stale references, and verify repository state is ready for next work session.

## Operating Protocol

1. **After PR merge:** Run when human confirms "PR merged" or similar
2. **Automatic detection:** Can also run when invoked to check for merged branches
3. **Mandatory cleanup:** ALL merged branches must be deleted (local and remote)

## Entry Criteria

- Human confirms "PR merged" or similar
- OR skill invoked with cleanup detection enabled

## Exit Criteria

- Local merged branch deleted
- Remote merged branch deleted (if applicable)
- Stale remote references pruned
- Other merged branches cleaned up
- Working tree clean

## Procedure

### Step 1: Succinct Confirmation Template (CRITICAL)

**The `cleanup` task is THE END of the PR workflow. It MUST produce a one-line succinct confirmation and then HALT.**

**Succinct Confirmation Template:**

```
PR #<number> merged. Branch `<branch-name>` deleted. Cleanup complete.
```

**⚠️ CRITICAL: Do NOT re-report PR details or issue lists. The PR was already reported at creation time.**

### Step 2: Verify PR Merge (CRITICAL - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Closing issues without PR merge verification is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT trust `git pull` or local fast-forward. You MUST verify via GitHub API.**

```python
# MUST use GitHub API to verify merge
pr = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)

# Verify merged_at timestamp exists
if pr.get("merged_at") is None:
    # PR is not merged, STOP
    report = f"PR #{pullNumber} is not yet merged. Cannot close issues."
    return report

# ONLY after verified merge:
proceed_to_close_issues()
```

**Why API verification is mandatory:**

### Step 2.5: Rebase Pending PRs

After verifying the PR merge and before switching to dev, rebase all other open PRs onto the updated `dev` branch.

**Full procedure:** See `rebase-pending` task for complete details.

**Summary:**

1. List all open PRs: `github_list_pull_requests(owner, repo, state="open")`
2. For each open PR (excluding the just-merged one):
   a. Create temporary worktree for the PR branch
   b. Attempt `git rebase origin/dev`
   c. If clean rebase: force-push the updated branch (`git push --force-with-lease origin <branch>`)
   d. If conflicts: classify per `conflict-resolution` skill tiers
      - Tier 1 (Trivial): auto-resolve, silent
      - Tier 2 (Textual but safe): auto-resolve, note in chat
      - Tier 3 (Intent conflict): read both PR specs, determine intent
        - Same intent: auto-resolve with note
        - Different intent: HALT, report to developer with conflict details
3. Report summary: which PRs rebased cleanly, which had conflicts, which were auto-resolved, which are blocked for developer review

**If Tier 3 conflicts block any rebase:** Report full conflict details to developer (see `rebase-pending` task for template). Developer must resolve manually before force-pushing.

**If no pending PRs:** Skip this step entirely.

**Invoke as:** `/skill git-workflow --task rebase-pending`

### Step 2.6: SC-Verification Gate (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL: Closing an issue without verifying its success criteria against the live codebase is a CRITICAL GUIDELINE VIOLATION.**

Before closing ANY issue referenced in the PR body, the cleanup task MUST verify that each success criterion (SC) in the issue body has been met by the merged code.

#### SC-Verification Procedure

```python
def sc_verification_gate(issue_num, issue_body, pr_files):
    """
    Verify each success criterion in an issue body against live codebase state.
    Returns a per-SC pass/fail table as evidence.
    """
    sc_pattern = re.compile(
        r"(?:SC-\d+|☑|☐)\s*(.+?)(?:\n|$)",
        re.MULTILINE
    )
    success_criteria = sc_pattern.findall(issue_body)

    if not success_criteria:
        return {"verdict": "SKIP", "reason": "No success criteria found in issue body"}

    results = []
    all_pass = True
    for sc_text in success_criteria:
        sc_id_match = re.search(r"SC-(\d+)", sc_text)
        sc_id = sc_id_match.group(1) if sc_id_match else "unknown"

        verified = verify_sc_against_codebase(sc_text, pr_files)
        results.append({
            "sc_id": sc_id,
            "text": sc_text.strip(),
            "result": "PASS" if verified else "FAIL",
        })
        if not verified:
            all_pass = False

    if all_pass:
        return {"verdict": "PASS", "evidence": results}
    else:
        return {"verdict": "PARTIAL_FAIL", "evidence": results}


def verify_sc_against_codebase(sc_text, pr_files):
    """
    Verify a single success criterion by checking:
    1. SC references specific files — check those files exist in PR
    2. SC includes verification commands — run them and check output
    3. SC is descriptive only — check if PR files touch the relevant areas
    """
    file_refs = re.findall(r"`([^`]+)`", sc_text)
    if file_refs:
        for ref in file_refs:
            if any(ref in f for f in pr_files):
                return True
        return False

    verification_cmd = re.search(r"Verification:\s*`(.+?)`", sc_text)
    if verification_cmd:
        return True

    return True
```

#### SC-Verification Gate Actions

| Verdict | Action |
| -- | -- |
| `PASS` (all SCs verified) | Proceed to close the issue |
| `PARTIAL_FAIL` (some SCs failed) | Do NOT close. Add progress comment with per-SC table. Update STATUS marker. Leave open. |
| `SKIP` (no SCs found) | Proceed — issue has no structured success criteria |

**Evidence requirement (MANDATORY):** The per-SC pass/fail table MUST be posted as a comment on the issue before closure. This is a tool-call artifact — not posting the table is a VERIFICATION-GAP finding.

```markdown
**SC Verification Evidence**

| SC ID | Success Criterion | Result |
|-------|-------------------|--------|
| SC-1 | Description... | ✅ PASS |
| SC-2 | Description... | ❌ FAIL |

**Verdict:** <PASS/PARTIAL_FAIL>
**PR Reference:** #<number>
```

**For PARTIAL_FAIL verdicts:** Add a progress comment documenting which SCs passed and which remain open. Update the issue STATUS marker to reflect partial completion. Do NOT close the issue.

### Step 2.6.5: Phase-Completion Gate (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL: Closing a multi-phase spec after a partial merge (only some phases complete) is a CRITICAL GUIDELINE VIOLATION.**

Before closing a spec or plan issue, verify that ALL phases/sub-issues have merged PRs. A multi-phase spec MUST NOT be closed until every phase is verified complete.

#### Phase-Completion Verification Procedure

```python
def phase_completion_gate(issue_num, issue_body, merged_pr_number):
    """
    Verify that all phases of a multi-phase spec have merged PRs
    before allowing closure.
    """
    phase_pattern = re.compile(
        r"(?:###?\s*Phase\s+(\d+)|####\s*Task\s+(\d+))",
        re.MULTILINE
    )
    phases = phase_pattern.findall(issue_body)

    if not phases:
        return {"verdict": "SINGLE_PHASE", "reason": "No multi-phase structure detected"}

    sub_issues = github_issue_read(
        method="get_sub_issues", issue_number=issue_num
    )

    open_phases = []
    completed_phases = []

    for sub in sub_issues:
        sub_detail = github_issue_read(method="get", issue_number=sub["number"])
        if sub_detail.get("state") == "open":
            open_phases.append({
                "number": sub["number"],
                "title": sub_detail.get("title", ""),
            })
        elif sub_detail.get("state") == "closed":
            merged_pr_found = False
            prs = github_search_pull_requests(
                query=f"Fixes #{sub['number']} repo:{<github.owner>}/{<github.repo>}"
            )
            for pr in prs:
                pr_detail = github_pull_request_read(
                    method="get", owner=<github.owner>, repo=<github.repo>,
                    pullNumber=pr["number"]
                )
                if pr_detail.get("merged_at") is not None:
                    merged_pr_found = True
                    break

            completed_phases.append({
                "number": sub["number"],
                "title": sub_detail.get("title", ""),
                "merged_pr": merged_pr_found,
            })

    if open_phases:
        return {
            "verdict": "PARTIAL_COMPLETE",
            "open_phases": open_phases,
            "completed_phases": completed_phases,
        }
    else:
        return {"verdict": "ALL_COMPLETE", "completed_phases": completed_phases}
```

#### Phase-Completion Gate Actions

| Verdict | Action |
| -- | -- |
| `SINGLE_PHASE` (no multi-phase structure) | Skip gate — single-phase issue |
| `ALL_COMPLETE` (all phases have merged PRs) | Proceed to close the issue |
| `PARTIAL_COMPLETE` (some phases still open or without merged PR) | Do NOT close. Add progress comment listing completed and remaining phases. Leave open. |

**For PARTIAL_COMPLETE verdicts:** Add a progress comment documenting which phases are complete and which remain:

```markdown
**Phase Completion Status**

**Completed phases:**
- Phase 1: #<n> — ✅ Merged PR #<pr>
- Phase 2: #<n> — ✅ Merged PR #<pr>

**Remaining phases:**
- Phase 3: #<n> — 🔲 Open

**Verdict:** PARTIAL_COMPLETE — issue remains open until all phases are merged.
```

**Safety rule: NEVER close a multi-phase spec or plan until ALL sub-issues are closed with verified merged PRs.**

### Step 2.7: Hierarchical Issue Closure (MANDATORY)

**GitHub autoclose (`Fixes #N`/`Closes #N`) is inert for this repo — all PRs merge to `dev`, not `main`. The cleanup task is the SOLE closure mechanism. Every issue that should be closed must be explicitly closed via GitHub API.**

#### Step 2.7.1: Collect All Referenced Issues from PR Body

Parse the PR body for all issue reference patterns. Build the initial closure list.

| Pattern | Matches | Purpose |
| -- | -- | -- |
| `Spec:\s*#(\d+)` | `Spec: #959` | Plan→Spec upward |
| `Plan:\s*#(\d+)` | `Plan: #960` | Spec→Plan downward |
| `Fixes\s*#(\d+)` | `Fixes #968` | Cross-reference |
| `Implements\s*#(\d+)` | `Implements #866` | Informational reference |
| `Related\s*#(\d+)` | `Related #100` | Weak reference (evaluate only) |

```python
import re

patterns = {
    "spec_ref": r"Spec:\s*#(\d+)",
    "plan_ref": r"Plan:\s*#(\d+)",
    "fixes": r"Fixes\s*#(\d+)",
    "implements": r"Implements\s*#(\d+)",
    "related": r"Related\s*#(\d+)",
}

closure_candidates = set()
for pattern_name, pattern in patterns.items():
    for match in re.finditer(pattern, pr_body):
        issue_num = int(match.group(1))
        closure_candidates.add(issue_num)
```

#### Step 2.7.2: Classify Each Issue

For each issue in the closure candidates, determine its type from labels or title prefix:

| Classification | Detection | Closure Path |
| -- | -- | -- |
| Plan | Has `[PLAN]` label or `[PLAN]` title prefix | Plan closure path (Step 2.7.3) |
| Spec / Spec-Fix | Has `[SPEC]` or `[SPEC-FIX]` label or title prefix | Spec closure path (Step 2.7.4) |
| Other | No plan/spec labels | Direct close |

```python
for issue_num in closure_candidates:
    issue = github_issue_read(method="get", issue_number=issue_num)
    labels = [l["name"] for l in issue.get("labels", [])]
    title = issue.get("title", "")

    if "PLAN" in labels or title.startswith("[PLAN]"):
        plan_closure_path(issue_num, issue)
    elif "SPEC" in labels or "SPEC-FIX" in labels or title.startswith("[SPEC"):
        spec_closure_path(issue_num, issue)
    else:
        direct_close(issue_num)
```

#### Step 2.7.3: Plan Closure Path

1. Parse plan body for spec reference using regex `Spec:\s*#(\d+)` or `For spec:\s*#(\d+)`
2. If found, add spec to closure candidates
3. Check `get_sub_issues` API for task sub-issues under the plan
4. Close task sub-issues first (plan work is merged → tasks complete)
5. Close the plan issue

```python
def check_deliverables_in_pr(sub_detail, pr_files):
    """
    Check whether a sub-issue's deliverables are covered by
    the merged PR's file list.
    """
    body = sub_detail.get("body", "") or ""
    title = sub_detail.get("title", "") or ""
    deliverable_patterns = re.findall(
        r"(?:deliverable|file|path|modif(?:y|ied|ication)):\s*`?([^\s`*#]+)`?",
        body,
        re.IGNORECASE,
    )
    title_paths = re.findall(r"`([^`]+)`", title)

    candidates = deliverable_patterns + title_paths

    if not candidates:
        # No explicit deliverables — check if sub-issue number
        # appears in PR body (Fixes #N, Implements #N, etc.)
        sub_num = sub_detail.get("number")
        if sub_num and any(
            f"#{sub_num}" in (ref or "")
            for ref in [pr_body]
        ):
            return True
        # No deliverables and not referenced in PR — cannot verify
        return False

    for candidate in candidates:
        if any(candidate in f for f in pr_files):
            return True

    return False

def plan_closure_path(plan_num, plan_issue, pr_files=None, merged_pr_number=None):
    plan_body = plan_issue.get("body", "")

    spec_match = re.search(r"(?:Spec|For spec):\s*#(\d+)", plan_body)
    if spec_match:
        spec_num = int(spec_match.group(1))
        closure_candidates.add(spec_num)

    sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_num)

    for sub in sub_issues:
        sub_detail = github_issue_read(method="get", issue_number=sub["number"])
        if sub_detail.get("state") == "open":
            deliverables_covered = (
                pr_files is not None
                and check_deliverables_in_pr(sub_detail, pr_files)
            )

            if deliverables_covered:
                github_issue_write(
                    method="update", issue_number=sub["number"],
                    state="closed", state_reason="completed"
                )
                github_add_issue_comment(
                    issue_number=sub["number"],
                    body=f"Closing: deliverables verified in merged PR #{merged_pr_number}. "
                         f"Parent #{plan_num} was closed by the same PR."
                )
            else:
                # Flag for review — do NOT auto-close
                github_add_issue_comment(
                    issue_number=sub["number"],
                    body=f"⚠️ Deliverables for this sub-issue were NOT found in "
                         f"merged PR #{merged_pr_number}. Parent #{plan_num} was closed, "
                         f"but this sub-issue remains open pending developer review."
                )

    plan_detail = github_issue_read(method="get", issue_number=plan_num)
    if plan_detail.get("state") == "open":
        github_issue_write(method="update", issue_number=plan_num,
                          state="closed", state_reason="completed")
```

#### Step 2.7.4: Spec Closure Path

1. Search `github_search_issues(query="Spec: #{spec_number} repo:{<github.owner>}/{<github.repo>}")` for plans referencing this spec
2. For each plan found, verify it is closed
3. If ALL plans for the spec are closed → close the spec
4. If ANY plan is still open → do NOT close the spec

```python
def spec_closure_path(spec_num, spec_issue):
    plans = github_search_issues(
        query=f"Spec: #{spec_num} repo:{<github.owner>}/{<github.repo>}"
    )

    open_plans = []
    for plan in plans:
        plan_detail = github_issue_read(method="get", issue_number=plan["number"])
        if plan_detail.get("state") == "open":
            open_plans.append(plan)

    if not open_plans:
        spec_detail = github_issue_read(method="get", issue_number=spec_num)
        if spec_detail.get("state") == "open":
            github_issue_write(method="update", issue_number=spec_num,
                              state="closed", state_reason="completed")
    else:
        pass
```

#### Step 2.7.5: Cross-Reference Closure

For bug reports with `[SPEC-FIX]`, parse body for `Fixes #N`, `Related #N`. Evaluate linked issues.

```python
def cross_reference_closure(issue_num, issue):
    body = issue.get("body", "")
    related = re.findall(r"(?:Fixes|Related)\s*#(\d+)", body)

    for related_num in related:
        related_detail = github_issue_read(method="get", issue_number=int(related_num))
        if related_detail.get("state") == "open":
            pass
```

#### Step 2.7.6: Work PR Handling

Apply above for every issue in PR body. After processing all, re-check specs with multiple plans.

```python
for issue_num in closure_candidates:
    classify_and_close(issue_num)

for spec_num in [i for i in closure_candidates if is_spec(i)]:
    spec_closure_path(spec_num, None)
```

**Safety rule: NEVER close an issue that still has open children or open linked plans.**

#### Step 2.7.7: Transitive Graph Reconciliation

**After processing all closure candidates, traverse the issue graph for consistency.** This step catches orphaned sub-issues, dangling cross-references, and other graph inconsistencies that the per-issue closure paths miss.

```python
def reconcile_issue_graph(merged_pr_number, pr_files):
    """
    After closing issues referenced in PR body, traverse the entire
    reachable graph to find and reconcile orphaned nodes.
    """
    root_issues = closure_candidates  # Already collected in Step 2.7.1
    visited = set()
    queue = [(issue_num, 0) for issue_num in root_issues]
    orphaned = []
    reconciled = []

    while queue:
        issue_num, depth = queue.pop(0)
        if issue_num in visited or depth > 5:
            continue
        visited.add(issue_num)

        issue = github_issue_read(method="get", issue_number=issue_num)

        # Check sub-issues of this node
        sub_issues = github_issue_read(method="get_sub_issues", issue_number=issue_num)
        for sub in sub_issues:
            sub_detail = github_issue_read(method="get", issue_number=sub["number"])

            if sub_detail["state"] == "open" and issue["state"] == "closed":
                # Open sub-issue on closed parent — potential orphan
                # Check if deliverables are in PR file list
                deliverables_covered = check_deliverables_in_pr(
                    sub_detail, pr_files
                )
                if deliverables_covered:
                    # Close sub-issue with evidence
                    github_issue_write(
                        method="update", issue_number=sub["number"],
                        state="closed", state_reason="completed"
                    )
                    github_add_issue_comment(
                        issue_number=sub["number"],
                        body=f"Closing: deliverables verified in merged PR #{merged_pr_number}. " +
                             f"Parent #{issue_num} was closed by the same PR."
                    )
                    reconciled.append(sub["number"])
                else:
                    orphaned.append(sub["number"])

            # Recurse into sub-issue's own graph
            queue.append((sub["number"], depth + 1))

        # Parse cross-references
        body = issue.get("body", "")
        for pattern in [r"Spec:\s*#(\d+)", r"Plan:\s*#(\d+)",
                        r"Fixes\s*#(\d+)", r"Implements\s*#(\d+)"]:
            for match in re.finditer(pattern, body):
                ref = int(match.group(1))
                if ref not in visited:
                    queue.append((ref, depth + 1))

    return {"orphaned": orphaned, "reconciled": reconciled, "visited": visited}
```

**Reporting:** After reconciliation, report to chat:

```
Issue Graph Reconciliation:
Reconciled (closed with PR evidence): #<n1>, #<n2>, ...
Orphaned (still open — deliverables not in PR): #<m1>, #<m2>, ...
Total nodes visited: <N>
```

**If orphaned sub-issues remain:** Do NOT close them. Report them as verification gaps requiring developer attention.

### Step 2.7.8: Orphaned Task Issues (Unlinked Sub-issues)

For issues with `[Task: #N]` or `Phase N:` patterns in their title that reference the parent plan but are not formal sub-issues (i.e., not returned by `get_sub_issues`), include them in closure candidates by searching the issue body and PR body for these references.

```python
def find_orphaned_task_issues(parent_issue_number, pr_body, pr_files):
    """
    Find issues that reference a parent plan in their title but
    are not linked via formal sub-issue relationships.
    """
    sub_issues = github_issue_read(
        method="get_sub_issues", issue_number=parent_issue_number
    )
    linked_numbers = {sub["number"] for sub in sub_issues}

    title_patterns = [
        r"\[Task:\s*#(\d+)\]",
        r"Phase\s+\d+",
    ]

    orphaned_candidates = []

    search_sources = [pr_body]
    parent_issue = github_issue_read(method="get", issue_number=parent_issue_number)
    if parent_issue.get("body"):
        search_sources.append(parent_issue["body"])

    for source in search_sources:
        for match in re.finditer(r"#(\d+)", source):
            ref_num = int(match.group(1))
            if ref_num == parent_issue_number:
                continue
            if ref_num in linked_numbers:
                continue

            ref_issue = github_issue_read(method="get", issue_number=ref_num)
            ref_title = ref_issue.get("title", "")

            for pattern in title_patterns:
                if re.search(pattern, ref_title):
                    orphaned_candidates.append({
                        "number": ref_num,
                        "title": ref_title,
                        "state": ref_issue.get("state"),
                    })
                    break

    return orphaned_candidates
```

For each orphaned task issue found, apply the same closure verification logic as formal sub-issues (check deliverables against PR file list, verify merged PR evidence). Orphaned issues with verified deliverables should be closed; those without should be flagged for developer review.

### Step 3: Switch to Dev and Sync (Fast-Forward Only)

**Three-Branch Workflow:** After feature PR merge, switch to `dev` (not `main`) and sync with remote.

```bash
git checkout dev
git pull origin dev --ff-only
```

**🚫 CRITICAL: The `--ff-only` flag is MANDATORY.** A plain `git pull origin dev` can silently succeed with a merge commit, hiding divergence issues. The `--ff-only` flag ensures dev fast-forwards to the remote tip without creating merge commits.

**If `--ff-only` pull fails (diverged history):**

```bash
# HALT and report. Suggest manual resolution:
echo "ERROR: local dev has diverged from origin/dev"
echo "Suggest: git pull --rebase origin dev"
echo "Or manual resolution required"
# HALT — do NOT proceed with stale codebase
```

**⚠️ DO NOT create merge commits on dev.** If ff-only fails, HALT and report to the developer. Suggest `git pull --rebase origin dev` or manual resolution.

**Verify local dev matches the merge commit:**

```bash
git log --oneline -1 origin/dev
git log --oneline -1 dev
```

The two commit hashes MUST match. If they differ, the pull did not succeed — re-run `git pull origin dev --ff-only` and verify again.

**Why this verification matters:** Without confirming local `dev` is synced, the next session starts with a stale local branch, causing `git pull` failures from untracked files and merge conflicts when creating new feature branches. The `--ff-only` flag prevents silent merge commits that obscure divergence.

**Worktree context:** If running from a worktree, `git checkout dev` and `git pull` must operate on the main working tree, not the worktree. Use `git -C /path/to/main/repo checkout dev && git -C /path/to/main/repo pull origin dev --ff-only` to ensure operations target the main tree.

### Step 3.5: Dev Sync Verification Gate (MANDATORY — ZERO TOLERANCE)

**After Step 3 (merge verification) and BEFORE any branch deletion, worktree removal, or issue closure:**

This gate is a HARD BLOCK, not a checklist item. No downstream operation may proceed until local dev HEAD matches origin/dev HEAD.

**Procedure:**

1. Run: `git checkout dev && git pull origin dev --ff-only`
2. Capture local hash: `git log --oneline -1 dev`
3. Capture remote hash: `git log --oneline -1 origin/dev`
4. Compare hashes — they MUST match exactly
5. If hashes differ → re-pull and verify again (maximum 3 attempts)
6. If still different after 3 attempts → HALT and report to developer

**Evidence artifact (MANDATORY):** The tool-call output showing matching hashes MUST be present in chat before proceeding. This is a verification gate, not a checklist item.

**Why this is a hard gate:** Without confirming local dev is synced, the next session starts with a stale local branch. This causes `git pull` failures from untracked files and merge conflicts when creating new feature branches. The `--ff-only` flag prevents silent merge commits that obscure divergence.

**🚫 FORBIDDEN:** Proceeding past this gate without matching hash evidence. Branch deletion, worktree removal, and issue closure ALL require this gate to pass first.

**Worktree context:** If running from a worktree, the dev sync MUST operate on the main working tree. Use absolute paths: `git -C /path/to/main/repo checkout dev && git -C /path/to/main/repo pull origin dev --ff-only`. The worktree has already been removed in some flows — the main tree must be synced before proceeding.

### Step 4: Remove Feature Worktree

Feature worktrees must be cleaned up after PR merge.

```bash
# Determine worktree name from branch name:
# spec/<name> → .worktrees/spec-<name>
# feature/<name> → .worktrees/feature-<name>
# Rule: Replace / with - in the worktree directory name

SANITIZED=$(echo "<merged-branch-name>" | tr '/')
WT_PATH=".worktrees/${SANITIZED}"

# Check if worktree exists for this branch
if [ -d ".worktrees" ] && git worktree list | grep -q "$WT_PATH"; then
    git worktree remove "$WT_PATH"
    echo "Removed worktree: $WT_PATH"
fi
```

### Step 4.5: Check for Active Parallel Worktrees

After removing the specific worktree, check if other agents may still be active:

```bash
# Check for remaining feature worktrees
REMAINING=$(git worktree list | grep -c ".worktrees/spec-\|.worktrees/feature-")
if [ "$REMAINING" -gt 0 ]; then
    echo "Other feature worktrees still active: $REMAINING remaining"
    echo "Skipping git worktree prune — other agents may still be working"
    # Do NOT run git worktree prune
    # Do NOT run git checkout dev in main tree during parallel work
else
    echo "No other feature worktrees remaining"
    git worktree prune
fi
```

**Why this check matters:**

- In parallel sub-agent mode, other agents may still be working in their worktrees
- Premature `git worktree prune` could corrupt active worktrees
- Only prune when ALL parallel work is confirmed complete
- The orchestrator (per `divide-and-conquer` skill) runs `git worktree prune` after ALL sub-agents complete

**Individual agent (during parallel work):**

1. Remove only YOUR specific worktree: `git worktree remove .worktrees/<your-branch-name>`
2. Do NOT run `git worktree prune` — other agents may still be active
3. Do NOT run `git checkout dev` in main working tree during parallel work

**Orchestrator (after ALL parallel work completes):**

1. Verify no feature worktrees remain: `git worktree list`
2. If only `.worktrees/main` remains: safe to prune
3. Run: `git worktree prune`
4. Run: `git checkout dev && git pull origin dev` (sync main working tree)

### Step 5: Delete Current Merged Branch

```bash
# Delete local branch
git branch -d <merged-branch-name>

# Delete remote branch (if not auto-deleted by GitHub)
git push origin --delete <merged-branch-name> 2>/dev/null || echo "Remote already deleted"

# Prune stale remote references
git fetch --prune

# Prune stale remote-tracking branches (MANDATORY)
git remote prune origin
```

**Why `git remote prune origin` is mandatory:** After a remote branch is deleted (either by GitHub auto-deletion or explicit `git push origin --delete`), the local remote-tracking reference (`refs/remotes/origin/<branch>`) becomes stale. `git fetch --prune` only prunes refs for remote branches that no longer exist AND have no upstream tracking, while `git remote prune origin` explicitly removes all stale remote-tracking branches. Skipping this leaves ghost references that cause confusion in `git branch -a` output and can interfere with new branch creation.

### Step 5.5: Work Branch Cleanup

**When the merged branch was a work branch (created by `assemble-work`), additional cleanup is required.**

#### Detecting a Work Branch

A work branch has these characteristics:
- Branch name typically starts with `work/` or was identified in the work state file
- Work state file exists at `.opencode/tmp/work-*.md`
- Multiple implementation commits in the branch (one per issue in the work execution)

#### Work Cleanup Procedure

After a work PR is confirmed merged:

1. **Delete individual feature branches that were squash-merged into the work branch:**

   ```bash
   # Extract feature branch names from work state file
   # Each line like "- [ ] #A — branch: spec/<name>, status: done"
   # gives us the branch names to delete

   # For each feature branch listed in work state:
   git branch -d spec/<feature-branch-name>
   git push origin --delete spec/<feature-branch-name> 2>/dev/null || echo "Remote already deleted"
   ```

2. **Delete the work branch itself:**

   ```bash
   git branch -d <work-branch-name>
   git push origin --delete <work-branch-name> 2>/dev/null || echo "Remote already deleted"
   ```

3. **Remove individual feature worktrees:**

   ```bash
   # For each feature worktree listed in work state:
   git worktree remove .worktrees/spec-<feature-name>

   # Remove work worktree if it exists:
   git worktree remove .worktrees/<work-worktree-name>
   ```

4. **Remove work state file:**

   ```bash
   rm .opencode/tmp/work-*.md
   ```

5. **Prune remote references:**

   ```bash
   git fetch --prune
   git remote prune origin
   ```

6. **Close all referenced issues via API:**

   ```python
   for issue_number in work_issues:
       issue = github_issue_read(method="get", issue_number=issue_number)
       if issue.get("state") != "closed":
           # Close all referenced issues via API — platform autoclose is inert for dev-branch merges
           github_issue_write(method="update", issue_number=issue_number,
                             state="closed", state_reason="completed")
   ```

#### Work Cleanup Safety Checks

| Check | Purpose |
| -- | -- |
| Work PR is merged (verified via API) | Prevents deleting unmerged work |
| Each feature branch is an ancestor of the work branch | Ensures no work was lost |
| Working tree clean on main repo | No uncommitted changes before cleanup |
| Feature worktrees removed before branch deletion | Prevents dangling worktree references |

**⚠️ CRITICAL: Never delete a work branch or its feature branches until the work PR is confirmed merged via GitHub API (`merged_at` is not None).**

### Step 6: Clean Other Merged Branches

**Find merged branches:**

```bash
git branch --merged dev
```

**For each merged branch (except main/master/dev):**

```bash
git branch -d <branch>
```

### Step 7: Verify Clean State

```bash
git status --porcelain  # Must be empty
git branch -vv          # Should show minimal branches
```

## Branch Cleanup After Merge — MANDATORY

**⚠️ CRITICAL: Cleanup is NOT Optional**

After EVERY merged PR, cleanup is MANDATORY — no exceptions, no "I'll do it later".

### ✅ ALWAYS DO — IMMEDIATELY After Merge Confirmation

1. **Switch to dev and sync** — `git checkout dev && git pull origin dev`
2. **Verify dev sync** — `git log --oneline -5` must show the merge commit
3. **Delete local feature branch** — `git branch -d <branch-name>`
4. **Delete remote branch** — `git push origin --delete <branch-name>` (if not auto-deleted by GitHub)
5. **Verify cleanup** — `git branch -vv` to confirm deletion
6. **Prune remote references** — `git fetch --prune && git remote prune origin`

**This is NOT optional.** Cleanup happens in the same session as merge confirmation.

### ✅ ALWAYS DO — When User Asks "cleanup branches"

1. **List merged local branches** — `git branch --merged dev`
2. **Delete merged local branches** — `git branch -d <branch-name>` for each
3. **List merged remote branches** — `git branch -r --merged dev`
4. **Delete merged remote branches** — `git push origin --delete <branch-name>` for each
5. **Prune stale remote refs** — `git fetch --prune`
6. **Verify cleanup** — `git branch -a` to confirm clean state

**⚠️ CRITICAL: Clean BOTH local AND upstream.** Leaving stale remote branches defeats the purpose.

## Branch Status Categories

| Status | Condition | Action |
| -- | -- | -- |
| **Fully merged** | `ahead=0, behind=0` or PR merged | **DELETE IMMEDIATELY** |
| **Superseded** | PR closed/merged, changes incorporated via other branch | **DELETE IMMEDIATELY** |
| **Stale** | Behind main by many commits, no PR, no recent work | Safe to delete |
| **Active** | Has unmerged commits, open PR, or active work | **Do NOT delete** |

## Automatic Cleanup Detection

**Entry triggers:** Explicit "PR merged" confirmation, "cleanup branches" request, or "check pr" / "check prs" / "check pull request" / "check pull requests" phrases.

### "Check PR" Workflow

When the user says "check pr", "check prs", "check pull request", or "check pull requests":

1. **List all PRs** (open and merged) using `github_list_pull_requests`
2. **For each merged PR:**
   - Check if local branch still exists
   - If local branch exists → proceed with cleanup (Steps 2–7 of this task)
   - If no local branch → report "already cleaned up"
3. **For each open PR:**
   - Report PR number, title, and status
   - Do NOT take any cleanup action
4. **If only open PRs exist** → report PRs and HALT
5. **If merged PRs detected** → activate full cleanup workflow

When invoked without "check pr" trigger, can check for merged branches:

```python
# Query GitHub for merged PRs
github_list_pull_requests(state="merged", perPage=50)

# For each merged PR:
#   - Check if local branch exists
#   - Check if merged into main
#   - Report cleanup candidate
```

### Safety Checks Before Deletion

| Check | Purpose | Method |
| -- | -- | -- |
| Branch merged | Prevent deleting unmerged work | `git branch --merged dev` |
| PR status | Confirm merge (not just closed) | GitHub API |
| Not current | Prevent deleting active branch | `git branch --show-current` |
| Not protected | Block main/master deletion | Hardcoded exclusion |
| Clean working tree | Ensure no uncommitted changes | `git status --porcelain` |

**If ANY check fails → SKIP that branch with warning.**

## Archive Workflow (Completion)

### When to Archive

Archive a spec **immediately** after the final phase is approved and the PR is merged:

1. All steps marked `☑`
2. PR merged (not just created)
3. Add closing summary comment to issue
4. Close the GitHub Issue (state change only)

### Archive Process

**All specs use GitHub Issues as the authoritative source** (no local files needed).

**Archive process:** Add closing summary comment, then close the GitHub Issue.

⚠️ **CRITICAL:** NEVER edit the issue body when closing. Adding `STATUS: completed` or `COMPLETED: YYYY-MM-DD` to the body destroys history. Use comments instead.

## Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

### 🚫 PROHIBITED

1. **NEVER close an issue immediately after implementation**
2. **NEVER close an issue when PR is created but not merged**
3. **NEVER close an issue when PR is submitted for review**
4. **NEVER close an issue based on `git pull` alone** — MUST verify via GitHub API

### ✅ REQUIRED SEQUENCE

| Step | Action | Agent Role |
| -- | -- | -- |
| Implementation complete | Create PR with `Fixes #123` | ✅ Agent creates PR |
| PR created | Report URL, HALT | ✅ Agent waits |
| Human merges PR | Merge happens | 🚫 Human ONLY |
| User confirms merge | Call `github_pull_request_read method=get` | ✅ Agent verifies |
| PR state = merged | Close issue | ✅ Agent closes |

## Parent/Child Issue Closure

**Parent issues MUST NOT be closed while ANY child issues remain open.**

### 🚫 PROHIBITED

1. **NEVER close a parent `[SPEC]` issue when ANY child `[Task]` issues are still open**
2. **NEVER close a parent after PR merge if other child tasks are incomplete**
3. **NEVER assume "the PR covers everything" when sub-issues exist**

### Example Workflow

```
SPEC #100 (parent)
├── Task #101: Phase 1 - Database schema
├── Task #102: Phase 2 - API endpoints
└── Task #103: Phase 3 - UI components

PR merges for Phase 1 → Close #101 ONLY
#100 remains open (children #102, #103 pending)

Later, PR merges for Phase 2 → Close #102 ONLY
#100 remains open (child #103 pending)

Later, PR merges for Phase 3 → Close #103 AND #100 (all children done)
```

### Exception: All Children Completed

When ALL child issues are completed by a single PR merge:

1. Close the child issue corresponding to the PR
2. **ALSO close the parent issue** (all children are now complete)
3. Add summary comment to the parent explaining all work is complete

## Closing Summary (Conditional)

Before closing any issue (SPEC or Task), the AI agent MAY provide a final summary comment ONLY if it conveys substantive information stakeholders need to understand what changed or why.

### When to Post Closing Comment

| Scenario | Action |
| -- | -- |
| Closing summary explains substantive changes stakeholders need to know | **POST comment** |
| Closing summary is merely "Task complete" or status update | **SKIP — do not post** |
| Multiple related changes that stakeholders need context on | **POST comment** |
| Routine closure with no stakeholder-meaningful information | **SKIP — do not post** |

### Summary Requirements

- **Summary of Changes**: High-level overview of what was implemented
- **Test Results**: Summary of verification steps (tests run, coverage, manual checks)
- **Impacts**: Any impacts on other issues or project components
- **Superseded/Not Implemented**: Explicitly state if any planned items were superseded, deferred, or intentionally skipped

### Example Closing Comment

```
**Issue Closing Summary**
- **Changes**: Implemented the new rate limiting middleware in `pubmed_client.py` and updated workflow docs.
- **Test Results**: All 12 unit tests passed. Manual verification confirmed retry logic works.
- **Impacts**: None on existing issues.
- **Superseded/Not Implemented**: The "Phase 3: Circuit breaker" was deferred to a follow-up issue #165.

---
🤖 <AgentName> (<ModelId>) ✅ completed
```

### When to Close

**Only close after PR merge:**

1. PR has been reviewed
2. PR has been merged by human
3. CI/CD passed (if applicable)
4. THEN close the issue with summary comment

## Branch Status Decision Tree

```
Merged PR (current branch just merged)
    │
    ├─► Switch to main: git checkout dev
    │
    ├─► Pull latest: git pull origin main
    │
    ├─► Delete local: git branch -d <branch>
    │
    ├─► Delete remote: git push origin --delete <branch>
    │
    └─► Prune: git fetch --prune

Merged PR (other branches from previous sessions)
    │
    ├─► List merged: git branch --merged dev
    │
    └─► For each (except main/master):
            git branch -d <branch>
```

## Safety Checks Before Deletion

Before ANY branch deletion:

1. **Merged status:** `git branch --merged dev` includes the branch ✓
2. **GitHub PR status:** PR is "merged" (not "closed") ✓
3. **Not current branch:** `git branch --show-current` ≠ branch to delete ✓
4. **Not protected:** Branch name ≠ `main`, `master` ✓
5. **Clean working tree:** `git status --porcelain` returns empty ✓

**If ANY check fails → SKIP that branch with warning.**

## Sub-Issue Closure Enforcement (CRITICAL)

**⚠️ CRITICAL: Sub-issues are closed by the platform via "Fixes #N" annotations, NOT manually by the agent.**

### 🚫 FORBIDDEN

- **Closing sub-issues after implementation but BEFORE PR merge**
- **Closing sub-issues when PR is created but not merged**
- **Manually closing sub-issues that have "Fixes #N" in PR description**
- **Closing sub-issues without verifying PR merge via GitHub API**

### ✅ REQUIRED WORKFLOW

**GitHub autoclose is inert for this repo (PRs merge to `dev`, not `main`). The cleanup task is the SOLE closure mechanism. All issues must be closed via API after PR merge verification.**

1. **Implement sub-issue** → Create PR with `Fixes #N` in description (informational label for human readers)
2. **PR created** → Report URL, HALT
3. **Human merges PR** → Issues are NOT automatically closed
4. **User confirms "pr merged"** → Agent verifies merge via GitHub API → Agent closes ALL referenced issues via API
5. **Agent verifies sub-issues are closed** → API check (`state: "closed"`)
6. **If sub-issue still open** → Agent closes it manually (standard procedure, not edge case)
7. **All sub-issues closed?** → Close parent issue

### Verification Sequence

```python
# Step 1: Verify PR merge via GitHub API
pr = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)
if pr.get("merged_at") is None:
    halt("PR not merged yet")

# Step 2: Close all sub-issues via API — platform autoclose is inert for dev-branch merges
children = github_issue_read(method="get_sub_issues", issue_number=parent)
open_children = [c for c in children if c["state"] == "open"]

if open_children:
    for child in open_children:
        github_issue_write(method="update", issue_number=child["number"], 
                          state="closed", state_reason="completed")

# Step 3: Close parent only after all children closed
if not open_children:
    github_issue_write(method="update", issue_number=parent,
                       state="closed", state_reason="completed")
```

### "Fixes #N" Annotation (MANDATORY)

**PR descriptions MUST include sub-issue numbers:**

```markdown
Fixes #86, #87, #88

[PR body...]
```

This enables automatic closure by GitBucket/GitHub.

### Edge Case Handling

| Scenario | Action |
| -- | -- |
| Sub-issue still open after merge | Agent closes manually via API (standard procedure — autoclose is inert for dev merges) |
| PR closed without merge | Sub-issues remain open (correct behavior) |
| Draft PR | Sub-issues remain open until PR is merged (correct behavior) |
| Multiple sub-issues in one PR | Close all via API after merge verification |

## Pre-Closure Sub-Issue Verification Gate (CRITICAL)

**🚫 CRITICAL: Before closing ANY issue, verify that closed sub-issues were legitimately closed via merged PR. A closed state alone does NOT mean work is done.**

This verification gate runs BEFORE the sub-issue double-check (which verifies open sub-issues remain). This gate verifies that already-closed sub-issues were legitimately closed.

### Verification Procedure

```
For each sub-issue of the parent issue:
  child = github_issue_read(method="get", issue_number=sub_issue_number)

  if child.state == "closed":
    state_reason = child.get("state_reason", "")

    # Verify closure is legitimate (not premature)
    prs = github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{<github.owner>}/{<github.repo>}")
    merged_pr_found = False
    for pr in prs:
      pr_detail = github_pull_request_read(method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=pr["number"])
      if pr_detail.get("merged_at") is not None:
        merged_pr_found = True
        break

    if state_reason == "completed" and merged_pr_found:
      # Legitimate closure — sub-issue was implemented and merged
      PROCEED — sub-issue verified

    elif state_reason == "completed" and not merged_pr_found:
      # Closed as "completed" but NO merged PR — likely premature closure
      VERIFICATION-GAP — flag-for-review
      # Do NOT close parent — investigate this sub-issue first

    elif state_reason == "not_planned":
      # Intentionally not implemented — acceptable if documented
      # Parent CAN be closed if remaining sub-issues are legitimate
      NOTE — sub-issue was intentionally skipped

    elif state_reason == "duplicate":
      # Closed as duplicate — verify target issue exists and covers scope
      # Check if the duplicate target is also legitimately closed
      VERIFICATION-GAP — conditional (verify duplicate covers scope)

    else:
      # No clear closure reason
      VERIFICATION-GAP — flag-for-review

  elif child.state == "open":
    # Open sub-issue — handled by Sub-Issue Double-Check below
    PASS — handled by next section
```

### Finding Classification

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| Closed + merged PR | VERIFIED | auto-proceed | Sub-issue verified as legitimately closed |
| Closed "completed" + no merged PR | VERIFICATION-GAP | flag-for-review | Investigate — may be premature closure |
| Closed "not_planned" | VERIFIED | auto-proceed | Intentionally skipped — parent can close remaining scope |
| Closed "duplicate" | VERIFICATION-GAP | conditional | Verify duplicate target covers scope |
| Open sub-issue | MISSING-ELEMENT | conditional | Handled by Sub-Issue Double-Check below |

**Only proceed to parent closure after ALL closed sub-issues are verified as legitimately closed or intentionally skipped.**

## Sub-Issue Double-Check (CRITICAL)

After closing child issues addressed by PR, ALWAYS verify remaining sub-issues before closing parent.

**This requires agent intelligence, not just script logic.**

### Step 1: Query Sub-Issues

```python
children = github_issue_read(method="get_sub_issues", issue_number=parent_issue)
```

### Step 2: Classify Each Sub-Issue

**Already Closed:**

- `state: "closed"` + `state_reason: "completed"` → Done
- `state: "closed"` + `state_reason: "not_planned"` → Intentionally not done
- Closed with "Superseded by #N" comment → Check replacement exists

**Open but May Be Complete:**

- Check comments for "Superseded by #N" → Verify new issue covers work
- Check body for PR link ("Fixes #N") → If merged, work is done

**Open and Incomplete:**

- No PR, no superseded link, no completion comment → BLOCK parent closure

### Step 3: Take Action

```python
open_children = [c for c in children if c.state == "open"]

if open_children:
    # Classify each open child
    truly_incomplete = []
    
    for child in open_children:
        # Agent intelligence required here:
        # - Check state_reason
        # - Check comments for superseded links
        # - Check for merged PR links
        # - Determine if work is actually done
        
        if child_is_truly_incomplete(child):
            truly_incomplete.append(child)
    
    if truly_incomplete:
        # POST WARNING - do NOT close parent
        post_warning_comment(parent, truly_incomplete)
        # DO NOT close parent
    else:
        # All open children have justification
        close_parent_with_summary(parent)
else:
    # All children closed
    close_parent_with_summary(parent)
```

### Step 4: Warning Comment Template

If parent cannot be closed:

```markdown
**Cannot Close Parent — Open Sub-Issues Detected**

This parent issue cannot be closed because the following sub-issue(s) remain incomplete:

- #N: [Title] — [status analysis]

**Status Analysis:**
- [Explain why each open child cannot be closed]

**To close this parent:**
1. Complete the remaining sub-issue(s)
2. Close each sub-issue when work is complete
3. Or close as "not planned" with explanation if intentionally skipped

---
🤖 <AgentName> (<ModelId>) 🚫 blocking
```

## Live Verification (MANDATORY)

**🚫 CRITICAL: Each verification point requires a tool call for evidence. Assertions without tool-call artifacts are VERIFICATION-GAP findings. Closing issues without verified merge evidence is a CRITICAL GUIDELINE VIOLATION.**

### PR Merge Verification

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| PR merge status | `github_pull_request_read(method=get, ...)` | `merged_at` is not None | CONFLICTING → HALT, do not close issues |
| Merged by | `github_pull_request_read(method=get, ...)` | `merged_by` populated | VERIFICATION-GAP → investigate |
| Branch merged into dev | `git branch --merged dev` | Feature branch listed | VERIFICATION-GAP → may need manual merge |
| Local dev synced | `git log --oneline -1 dev` equals `git log --oneline -1 origin/dev` | Hashes match exactly | VERIFICATION-GAP → re-pull and re-verify |
| Dev has merge commit | `git log --oneline -5 dev` | Merge commit visible | MISSING-ELEMENT → sync dev first |
| Sub-issues closed | `github_issue_read(method=get_sub_issues, ...)` | All sub-issues state=closed | VERIFICATION-GAP → close remaining or investigate |

### Verification Procedure

**In Step 2 (Verify PR Merge), mandatory evidence collection:**

```python
# PR merge verification — MANDATORY, NOT OPTIONAL
pr = github_pull_request_read(method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=N)

# Evidence artifacts:
# EVIDENCE: merged_at = pr.get("merged_at")  # Must be non-None
# EVIDENCE: merged_by = pr.get("merged_by")   # Should be populated
# EVIDENCE: state = pr.get("state")            # "closed" for merged PRs

if pr.get("merged_at") is None:
    # CONFLICTING finding — HALT
    # Do NOT close issues, do NOT delete branches
    pass
```

**In Step 5.5/6 (Issue Closure), verify sub-issues:**

```python
# Sub-issue closure verification
sub_issues = github_issue_read(method="get_sub_issues", issue_number=parent)

# Evidence artifacts:
# EVIDENCE: sub_issue_count = len(sub_issues)
# EVIDENCE: open_issues = [s for s in sub_issues if s["state"] == "open"]

if open_issues:
    # VERIFICATION-GAP finding — investigate each open sub-issue
    # Do NOT close parent until all children resolved
    pass
```

### Finding Classification

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| `merged_at` is None | CONFLICTING | flag-for-review | HALT — PR not merged, cannot close issues |
| `merged_by` is None but `merged_at` set | VERIFICATION-GAP | conditional | Investigate — may be bot merge, proceed with caution |
| Branch not in `--merged dev` list | VERIFICATION-GAP | conditional | Sync dev with `git pull origin dev`, recheck |
| Merge commit not in dev log | MISSING-ELEMENT | conditional | `git pull origin dev` then recheck |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Investigate closure reason, may need reopen |
| Sub-issue still open after merge | VERIFICATION-GAP | conditional | Close manually via API — autoclose is inert for dev merges |

**PR merge verification via API is MANDATORY. Trusting local git state alone is a CRITICAL GUIDELINE VIOLATION. Local `git pull` or fast-forward checks are NOT sufficient — they cannot distinguish between "merged via PR" and "locally merged without review."**

## Common Issues

| Issue | Resolution |
| -- | -- |
| Remote branch already deleted | Skip remote deletion, clean local |
| Local has extra commits | Warn user, ask before deleting |
| Multiple PRs from same branch | Wait until ALL PRs merged |
| Stash exists from pre-work | N/A — worktrees eliminate need for stash |

## Automatic Cleanup Detection (Secondary Reference)

**Entry triggers:** Explicit "PR merged" confirmation, "cleanup branches" request, or "check pr" / "check prs" / "check pull request" / "check pull requests" phrases. See the primary "Automatic Cleanup Detection" section above for full "check PR" workflow details.

When invoked, can check for merged branches:

```python
# Query GitHub for merged PRs
github_list_pull_requests(state="merged", perPage=50)

# For each merged PR:
#   - Check if local branch exists
#   - Check if merged into main
#   - Report cleanup candidate
```

## Why This Task Is Critical

- Feature branches accumulate over time
- Previous sessions may leave merged branches uncleaned
- Stale remote references clutter `git branch -a`
- Clean repository state required for next work session
- Prevents confusion from stale branch references
- **Issues ONLY closed after VERIFIED PR merge**

## Correct vs Incorrect Workflow

### ✅ CORRECT Workflow (Issue Closure)

```
PR created
    ↓
Developer reviews and merges PR
    ↓
Developer confirms "PR merged"
    ↓
cleanup task invoked
    ↓
Verify merge via GitHub API (merged_at field)
    ↓
API confirms merge → Proceed
    ↓
Close child issues addressed by PR
    ↓
Check parent for remaining sub-issues
    ↓
If all children closed → Close parent with summary
```

### 🚫 INCORRECT Workflow (CRITICAL VIOLATION)

```
PR created (or just branch pushed)
    ↓
Immediately close issues (NO MERGE)
    ↓
NO GitHub API verification
NO PR merge status check
NO parent/child structure check
```

**This incorrect workflow VIOLATES critical rules and causes:**

- Issues closed without PR tracking
- No merge verification
- Potential reopen of closed issues if PR rejected
- Lost audit trail

## Final HALT (CRITICAL)

**After closing issues and posting final summary, the agent MUST HALT.**

**HALT = Stop all further action. No prompting, no questions, no next steps.**

### What HALT Means After Cleanup

| Action | Status |
| -- | -- |
| Close issues | ✅ Done |
| Delete branches | ✅ Done |
| Post final summary | ✅ Done |
| Ask "What's next?" | 🚫 NEVER |
| Prompt for next task | 🚫 NEVER |
| Suggest new work | 🚫 NEVER |

**The workflow is complete. The agent stops. The human decides what happens next.**

### Correct Final Output

```
PR #81 merged. Branch `spec/github-issue-creation-skill` deleted. Cleanup complete.
```

**That's it. ONE LINE. Succinct confirmation. Then stop.**

### 🚫 CRITICAL VIOLATIONS After Cleanup

| Violation | Example |
| -- | -- |
| Continue without new instruction | "Ready for next task?" |
| Suggest next work | "Should I start on #75?" |
| Prompt for anything | "What would you like me to do?" |
| Not posting final summary | Missing executive summary |

**The cleanup task is the END. HALT means STOP.**

## Label State Machine

When changing issue labels during cleanup (e.g., removing `in-progress`), consult `141-planning-status-tracking.md §10` for the complete label transition matrix and the GitHub `labels` parameter warning (replaces all labels, not additive).# Git Protocol: Merge Protocol

## 5. Spec Implementation Branches

### ✅ ALWAYS DO

When implementing an approved spec:

1. **Branch Naming**: Derive from spec filename or issue — `spec/<short-name>` (e.g., `plans/SPEC-mesh-descriptor-lookup.md` → `spec/mesh-descriptor-lookup` or Issue #15 → `spec/project-first-strategy`)

2. **Branch Creation**: Before any implementation, create a worktree:

   ```bash
   git checkout dev && git pull origin dev
   git worktree add .worktrees/spec-<short-name> -b spec/<short-name> dev
   ```

3. **Work in Isolation**: All implementation commits go in the worktree, never in the main working directory

4. **Easy Rollback**: If implementation fails, simply `git checkout dev && git branch -D spec/<short-name>`

### 📋 Merging Spec Branches

**When GitHub MCP Tools Available:**

Use PR workflow instead of local merge:

**Before creating PR:**

1. **Rebase on main**: `git fetch origin && git rebase origin/dev`
2. **Squash commits**: Interactive rebase to consolidate multiple commits
3. **Force push**: `git push --force-with-lease origin <branch>`
4. **Then create PR**: Only after branch is clean and rebased

**PR Workflow Steps:**

1. Create feature worktree: `git worktree add .worktrees/feature-issue-123 -b feature/issue-123-description dev`
2. Commit changes to feature branch
3. Push to remote: `git push origin feature/issue-123-description`
4. Create PR: `github_create_pull_request` with `Fixes #123` in description
5. Request review: `github_request_copilot_review`
6. Address feedback with new commits
7. **WAIT for human to merge** — NEVER call `github_merge_pull_request` yourself
8. Delete branch after human merges

### ⚠️ MANDATORY: SQUASH MERGE ONLY

**All PRs MUST be squash-merged to `main`.**

- Never use regular merge — always squash
- Never use rebase-merge — always squash
- This maintains a clean commit history on `main`
- One commit per PR, with PR number in commit message

**For humans merging PRs:**

- GitHub "Squash and merge" button is required
- Never click "Merge" or "Rebase and merge" buttons

**When Local Merge is Acceptable (even with MCP tools):**

- Trivial fixes (typos, whitespace, single-line changes)
- Urgent hotfixes requiring immediate deployment
- Docs-only changes that don't affect production code

______________________________________________________________________

## When GitHub MCP Tools Unavailable

**Use local squash-merge:**

### ✅ ALWAYS DO

**When merging a feature branch into main:**

- Use **squash-merge** to create a single clean commit
- Delete the feature branch after merge
- Include spec reference in commit message

**When keeping a feature branch up-to-date:**

- Use **rebase** (not merge) to pull latest changes from dev
- `git fetch origin && git rebase origin/dev`

### 🚫 NEVER DO

- **NEVER use regular merge** (`git merge`) to merge feature branches into main — creates messy history
- **NEVER use merge** to sync feature branch with main — use rebase instead
- **NEVER force-push to main**

### Rebase Workflow

```bash
# On feature branch
git fetch origin
git rebase origin/dev

# If conflicts occur, resolve them and continue
git status  # see which files conflict
# edit conflicting files
git add <resolved-files>
git rebase --continue
```

______________________________________________________________________

## *Source: Content migrated from `110-git-protocol.md`*

*Source: Migrated from .opencode/guidelines/112-git-merge-protocol.md*
