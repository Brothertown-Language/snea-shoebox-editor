# Work State Verification Module

## Live State Verification Table

When `assemble-work` records claims about work state (e.g., "sub-agent completed", "issue linked"), each claim MUST be verified against live state before the orchestration proceeds.

### Verification Table

| Claim | Verification Action | Tool Call | Problem Class |
|-------|---------------------|-----------|---------------|
| Sub-agent completed | Result contract exists with status DONE or DONE_WITH_CONCERNS | Read work state file | STRUCTURE-VIOLATION |
| Issue created | Issue exists on GitHub with correct title and labels | `github_issue_read(method=get, issue_number=N)` | MISSING-ELEMENT |
| Sub-issues linked | `github_issue_read(method=get_sub_issues)` returns expected sub-issues | `github_issue_read(method=get_sub_issues, issue_number=N)` | MISSING-ELEMENT |
| Branch created | Branch exists in local worktree | `git rev-parse --verify <branch>` | MISSING-ELEMENT |
| Worktree path set | Worktree directory exists and is git repository | `git rev-parse --show-toplevel` in worktree | STRUCTURE-VIOLATION |
| All phases complete | Every phase in work state has status DONE | Read work state file | VERIFICATION-GAP |
| PR URL valid | PR URL extracted from API response, not constructed | Extract from `github_create_pull_request` response `html_url` | CONFLICTING |

### Work State File Format

Work state files are stored at `.opencode/tmp/work-<timestamp>.md` and contain:

```markdown
# Work State: <branch-name>

Authorization: "<authorization-text>"
Authorization scope: <scope>
PR strategy: <strategy>
Branch: <branch-name>
Worktree: <worktree-path>

## Issues

- [x|#] <issue-number> — <issue-title>

## Progress

### <issue-number> — <title>
- Status: PENDING | IN_PROGRESS | DONE | BLOCKED
- Sub-branch: <sub-branch-name>
- Result: <result-contract-summary>
```

### Evidence Artifacts

Every claim about work state MUST have a corresponding tool-call artifact:
- Work state file read → verify branch/status entries
- Git commands → verify branch/worktree state
- GitHub API calls → verify issue/PR state

Claims without artifacts are verification honesty violations.