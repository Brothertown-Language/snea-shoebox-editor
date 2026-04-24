# Task: cleanup/verify-merge

## Purpose

Verify PR merge via GitHub API and run SC-verification and phase-completion gates before any issue closure or branch deletion.

## Entry Criteria

- Human confirms "PR merged" or similar
- PR number is known

## Exit Criteria

- PR merge verified via GitHub API (`merged_at` is not None)
- SC-verification gate passed (all success criteria verified against live code)
- Phase-completion gate passed (all phases of multi-phase specs have merged PRs)
- Rebase of pending PRs completed (if applicable)

## Procedure

### Step 1: Verify PR Merge (CRITICAL - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Closing issues without PR merge verification is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT trust `git pull` or local fast-forward. You MUST verify via GitHub API.**

```python
pr = github_pull_request_read(method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=N)

if pr.get("merged_at") is None:
    report = f"PR #{pullNumber} is not yet merged. Cannot close issues."
    return report
```

**Evidence artifacts:**
- EVIDENCE: `merged_at` = pr.get("merged_at") — Must be non-None
- EVIDENCE: `merged_by` = pr.get("merged_by") — Should be populated
- EVIDENCE: `state` = pr.get("state") — "closed" for merged PRs

### Step 2: Rebase Pending PRs

After verifying the PR merge and before switching to dev, rebase all other open PRs onto the updated `dev` branch.

Invoke: `/skill git-workflow --task rebase-pending`

Summary:
1. List all open PRs: `github_list_pull_requests(owner, repo, state="open")`
2. For each open PR (excluding the just-merged one):
   a. Create temporary worktree for the PR branch
   b. Attempt `git rebase origin/dev`
   c. If clean rebase: force-push the updated branch
   d. If conflicts: classify per `conflict-resolution` skill tiers
3. Report summary: which PRs rebased cleanly, which had conflicts

If no pending PRs: Skip this step entirely.

### Step 3: SC-Verification Gate (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL: Closing an issue without verifying its success criteria against the live codebase is a CRITICAL GUIDELINE VIOLATION.**

#### SC-Verification Procedure

Parse the issue body for success criteria patterns (`SC-\d+`, `☑`, `☐`) and verify each against the live codebase.

```python
sc_pattern = re.compile(r"(?:SC-\d+|☑|☐)\s*(.+?)(?:\n|$)", re.MULTILINE)
success_criteria = sc_pattern.findall(issue_body)
```

For each SC:
1. If SC references specific files — check those files exist in PR
2. If SC includes verification commands — run them and check output
3. If SC is descriptive only — check if PR files touch the relevant areas

#### SC-Verification Gate Actions

| Verdict | Action |
| -- | -- |
| `PASS` (all SCs verified) | Proceed to close the issue |
| `PARTIAL_FAIL` (some SCs failed) | Do NOT close. Add progress comment with per-SC table. Leave open. |
| `SKIP` (no SCs found) | Proceed — issue has no structured success criteria |

**Evidence requirement (MANDATORY):** The per-SC pass/fail table MUST be posted as a comment on the issue before closure.

```markdown
**SC Verification Evidence**

| SC ID | Success Criterion | Result |
|-------|-------------------|--------|
| SC-1 | Description... | ✅ PASS |
| SC-2 | Description... | ❌ FAIL |

**Verdict:** <PASS/PARTIAL_FAIL>
**PR Reference:** #<number>
```

### Step 4: Phase-Completion Gate (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL: Closing a multi-phase spec after a partial merge is a CRITICAL GUIDELINE VIOLATION.**

Verify ALL phases/sub-issues have merged PRs before allowing closure of a multi-phase spec or plan.

1. Parse issue body for phase headings (`### Phase N:`, `#### Task N:`)
2. Get sub-issues via `github_issue_read(method="get_sub_issues")`
3. For each sub-issue, verify it is closed with a merged PR
4. If any phase is open or lacks merged PR evidence → do NOT close the parent

| Verdict | Action |
| -- | -- |
| `SINGLE_PHASE` | Skip gate — single-phase issue |
| `ALL_COMPLETE` | Proceed to close the issue |
| `PARTIAL_COMPLETE` | Do NOT close. Add progress comment listing completed and remaining phases. |

**Safety rule: NEVER close a multi-phase spec or plan until ALL sub-issues are closed with verified merged PRs.**

### Finding Classification

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| `merged_at` is None | CONFLICTING | flag-for-review | HALT — PR not merged, cannot close issues |
| `merged_by` is None but `merged_at` set | VERIFICATION-GAP | conditional | Investigate — may be bot merge |
| Branch not in `--merged dev` list | VERIFICATION-GAP | conditional | Sync dev, recheck |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Investigate closure reason |
| Sub-issue still open after merge | VERIFICATION-GAP | conditional | Close manually via API |

## Context Required

- Related tasks: `cleanup/issue-closure`, `cleanup/branch-cleanup`
- Related skills: `conflict-resolution` (for rebase conflicts)