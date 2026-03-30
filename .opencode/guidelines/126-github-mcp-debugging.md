# GitHub MCP Debugging: Owner Mismatch Protocol

## Overview

When GitHub MCP operations fail due to owner/repo mismatch, the agent MUST document the error on the associated issue with complete debugging information.

---

## Mandatory Documentation Protocol

### When to Document

**ALWAYS document GitHub MCP errors when ANY of these occur:**

| Error Type | Example |
|------------|---------|
| 404 Not Found | `GET https://api.github.com/repos/muksihs/snea-shoebox-editor/issues/47` → 404 |
| Permission Denied | `403 Forbidden` when accessing repo |
| Resource Not Found | Issue, PR, or file not found in expected location |
| Unexpected Empty Results | `github_issue_read` returns empty when issue should exist |

### What to Document

**Post a comment on the associated issue containing:**

1. **Error Details**
   - The exact GitHub API error message (if any)
   - The `owner` and `repo` values used in the failing call
   - The tool name and parameters that caused the error

2. **Session Context**
   - The `GIT_OWNER` and `GIT_REPO` values from session init
   - The `git remote -v` output
   - The `git config --get remote.origin.url` output

3. **Evidence of Correct Values**
   - Full `uv run python ai_bin/session_init.py` output
   - Any environment variables that might override

4. **Agent Context (if applicable)**
   - Whether this is a fresh session or continuation
   - Any previous session context that might have stale values

---

## Example Debug Comment

```markdown
## GitHub MCP Owner Mismatch Debug

### Error Details
- **Tool:** `github_issue_read`
- **Parameters:** `owner=muksihs, repo=snea-shoebox-editor, issue_number=47`
- **Error:** `404 Not Found - resource not found`

### Session Context
```
$ uv run python ai_bin/session_init.py
# Session Init - Git Context
GIT_USER_NAME=Michael Conrad
GIT_USER_EMAIL=m.conrad.202@gmail.com
GIT_OWNER=Brothertown-Language
GIT_REPO=snea-shoebox-editor
GIT_HOOKS_PATH=
GIT_REMOTE_URL=git@github.com:Brothertown-Language/snea-shoebox-editor.git

$ git remote -v
origin  git@mconrad-github:Brothertown-Language/snea-shoebox-editor.git (fetch)
origin  git@mconrad-github:Brothertown-Language/snea-shoebox-editor.git (push)

$ git config --get remote.origin.url
git@github.com:Brothertown-Language/snea-shoebox-editor.git
```

### Analysis
- Session init correctly returns `Brothertown-Language` as owner
- Agent tool call used `muksihs` as owner
- Root cause: [to be investigated]

### Session Info
- Fresh session: Yes/No
- Previous context: [describe if this is a continuation]

🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* 🔍 Debug Report
```

---

## Root Cause Checklist

When documenting owner mismatch errors, check for:

| Potential Cause | How to Verify |
|-----------------|---------------|
| Session not run | Verify `session_init.py` was executed first |
| Cached/stale values | Check if this is a continuation from a previous session |
| Agent context injection | Check agent prompts for hardcoded owner values |
| Environment variables | Run `env | grep -iE "(owner|git|github)"` |
| Git config overrides | Run `git config --list | grep -E "(user|remote)"` |
| SSH alias confusion | Run `git remote -v` and `git config --get remote.origin.url` |

---

## Never Assume Owner Values (Zero Tolerance)

**🚫 FORBIDDEN (Zero Tolerance — See `000-critical-rules.md`):**
- Assuming owner from git username (e.g., `muksihs` from `$USER`)
- Guessing owner from file paths (`/home/muksihs/...`)
- Using hardcoded owner values from previous sessions
- Proceeding with GitHub MCP calls without running session init first

**✅ REQUIRED:**
- Run `uv run python ai_bin/session_init.py` at session start
- Use `GIT_OWNER` and `GIT_REPO` from session init output for ALL GitHub MCP calls
- Document any discrepancies between expected and actual values
- When in doubt, run session init again and verify output

---

## Session Init is Authoritative

The `ai_bin/session_init.py` script is the SINGLE SOURCE OF TRUTH for:

| Value | Usage |
|-------|-------|
| `GIT_OWNER` | `owner` parameter in all GitHub MCP tools |
| `GIT_REPO` | `repo` parameter in all GitHub MCP tools |
| `GIT_USER_NAME` | Commit trailer `on behalf of <name>` |
| `GIT_USER_EMAIL` | Commit author email |
| `GIT_REMOTE_URL` | Verification of remote configuration |

**If session init produces unexpected values:**
1. STOP immediately
2. Do NOT proceed with GitHub operations
3. Document the discrepancy on the issue
4. Wait for human intervention

---

## Related

- `000-session-init.md` — Session initialization protocol
- `122-github-mcp-operations.md` — GitHub MCP tool usage
- `120-github-issue-first.md` — Issue-first workflow