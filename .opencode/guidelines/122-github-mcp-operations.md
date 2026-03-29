# GitHub Workflow: MCP Operations

## Tool Preference Summary

| Operation | GitHub MCP Available | GitHub MCP Unavailable |
|-----------|----------------------|--------------------------|
| Spec tracking | GitHub Issues | GitHub Issues via `gh` CLI |
| Create spec | `github_issue_write` | `gh issue create` |
| Track progress | Issue body STATUS + labels | Issue body STATUS + labels |
| Archive | Close issue (no file needed) | Close issue via `gh` CLI |
| Create PR | `github_create_pull_request` | `gh pr create` |
| Merge PR | 🚫 **NEVER — human only** | 🚫 **NEVER — human only** |
| Review | `github_request_copilot_review` | `gh pr review` |

---

## GitHub MCP Coverage

The GitHub MCP tools cover ALL repository operations:

| Category | Operations |
|----------|------------|
| **Issues** | read, write, create, update, label, comment, sub-issues |
| **Pull requests** | read, create, merge (human approval required), review, comment |
| **Repositories** | branches, commits, files, releases, tags, forking |
| **Search** | code, issues, PRs, repos, users |
| **Teams** | members, teams |

**Use GitHub MCP tools INSTEAD OF:**
- Opening browser to GitHub UI
- Using `gh` CLI for operations covered by MCP
- Manual API calls via curl
- Direct file operations on repository files

---

## Permissions Reference

| Tool | Required Permission |
|------|---------------------|
| `github_issue_read` | `issues: read` |
| `github_issue_write` | `issues: write` |
| `github_create_pull_request` | `pull_requests: write` |
| `github_pull_request_read` | `pull_requests: read` |
| `github_merge_pull_request` | `pull_requests: write` (PROHIBITED by guidelines) |
| `github_get_file_contents` | `contents: read` |
| `github_push_files` | `contents: write` |

---

*Source: `020-github-workflow.md` (will be deprecated)*