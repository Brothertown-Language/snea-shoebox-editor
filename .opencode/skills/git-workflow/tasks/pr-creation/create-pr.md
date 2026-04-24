# Task: pr-creation/create-pr

## Purpose

Create the pull request after squash/push, collect sub-issues, generate PR body, and extract PR URL from API response.

## Entry Criteria

- Enforcement gates passed (pr-creation/enforcement-gate)
- Branch squashed and pushed (pr-creation/squash-push)

## Exit Criteria

- PR created via GitHub API or GitBucket CLI
- PR URL extracted from API response (NEVER constructed from template)
- Executive summary reported in chat
- Agent HALTs waiting for human merge

## Procedure

### Step 5: Collect Sub-Issues (Multi-Task Specs)

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)
autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
```

**Scope-dependent PR strategy:**

| `pr_strategy` | PR Behavior |
| -- | -- |
| `stacked` | Single PR for all issues in work set |
| `individual` | Standard PR per branch |
| `none` | No PR creation — halt_at boundary |

**⚠️ CRITICAL: Sub-issues are closed by the cleanup task via API, NOT by autoclose.** GitHub autoclose is inert for `dev`-branch merges.

### Step 6: Create PR (Platform-Agnostic)

**GitHub (`github.platform=github`):**

```python
github_create_pull_request(
    owner=<github.owner>,
    repo=<github.repo>,
    title="[SPEC] <description>",
    body="""**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

Fixes #<parent>
Fixes #<child1>
""",
    head=branch_name,
    base="dev"
)
```

**GitBucket (`github.platform=gitbucket`):**

```bash
./.opencode/tools/gitbucket-api create-pr <owner> <repo> "[SPEC] <description>" <branch-name> dev --body "<PR body>"
```

### PR Body Requirements

- **Summary** section: 1-2 sentences describing stakeholder value (NOT implementation details)
- **Outcome** section: What changed for stakeholders
- `Fixes #N` annotations at bottom (informational — autoclose is inert for `dev` merges)
- Target branch is `dev` for feature work

**Use `Implements #N` instead of `Fixes #N` when the issue has sub-issues or is part of a plan-bridge hierarchy.**

### ❌ WRONG (Implementation Details)
```
Add plan-fidelity-auditor skill as the first auditor in the mandatory audit chain. It generates independent clean-room plans from problem statements and compares them against existing spec plans to identify substantive gaps.
```

### ✅ CORRECT (Executive Summary)
```
**Summary:**

Ensures specs are audited for plan fidelity before implementation, catching missing phases and scope misalignment early.

**Outcome:** Developers will catch spec quality issues before code changes begin.

Fixes #505
```

### Step 7: EXTRACT URL FROM API RESPONSE

**🚫 CRITICAL VIOLATION: Fabricating URLs from template is a CRITICAL GUIDELINE VIOLATION.**

1. Copy PR URL verbatim from the `github_create_pull_request` response `html_url` field
2. Do NOT retype, reconstruct, or assemble from known values
3. Verification checkpoint: Compare pasted URL character-by-character against `html_url`

### Step 7.5: Report PR URL and HALT

**Mandatory format:**

```
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

**PR URL:** <html_url from API response>

Wait for human to merge.
```

**Format requirements:**
- Executive summary FIRST
- PR URL LAST (before byline)
- MUST include "Wait for human to merge"
- Label MUST be "PR URL" (post-creation context)

### Agent Merge Prohibition

**🚫 ABSOLUTE PROHIBITION: AGENTS MUST NEVER MERGE PRs.**

- ALL PRs require human review before merge
- "go" does NOT authorize merging
- After PR creation: report URL and HALT

### Sub-Issue Autoclose Table

| Spec Type | PR Body Format |
| -- | -- |
| Single-task | `Fixes #<parent>` |
| Multi-task | `Fixes #<parent>` AND `Fixes #<child>` for each sub-issue |
| Work | `## Work Items\n\n#<issue1>\n#<issue2>\n\nFixes #<parent1>\nFixes #<child1>` |

### Common Issues

| Issue | Resolution |
| -- | -- |
| No commits between branches | Report: "Branch has no commits. Changes may already be merged." |
| Branch conflicts | Rebase on dev: `git rebase origin/dev` |
| Wrong base branch | Close PR, create new one with `base="dev"` |

## Context Required

- Related tasks: `pr-creation/enforcement-gate`, `pr-creation/squash-push`
- Related guidelines: `000-critical-rules.md` (URL sourcing, PR body format)