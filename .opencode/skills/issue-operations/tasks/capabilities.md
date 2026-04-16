# Task: capabilities

## Purpose

Probe platform capabilities at runtime. Determines what operations the current platform supports, enabling the dispatcher to choose between direct API calls and fallback patterns.

## Entry Criteria

- `GIT_PLATFORM` detected from session init
- Platform sub-skill available

## Exit Criteria

- Capability manifest returned for current platform
- Dispatcher knows which operations can use direct API vs fallback

## Procedure

### Step 1: Detect Platform

```
GIT_PLATFORM environment variable:
  "github"    → platforms/github-mcp/
  "gitbucket"  → platforms/gitbucket-api/
  (unset)      → platforms/github-mcp/ (default)
```

### Step 2: Query Capabilities

**Dynamic query (when MCP plugin present):**

If `gitbucket_*` MCP tools are detected at runtime, query for dynamic capabilities:

```
Probe for gitbucket_* MCP tools
If present → dynamic capability query overrides static manifest
If absent → fall back to static manifest in platform SKILL.md
```

**Static manifest (default):**

Read the platform sub-skill SKILL.md for the static capability table.

### Step 3: Return Capability Set

```yaml
capabilities:
  create_issue: true|false
  list_issues: true|false
  get_issue: true|false
  update_issue: true|false      # PATCH
  close_issue: true|false        # PATCH with state=closed
  add_comment: true|false
  update_comment: true|false
  delete_comment: true|false
  sub_issues: true|false         # formal sub-issue API
  search_issues: true|false
  search_pull_requests: true|false
  labels: true|false             # post-creation label operations
  create_pr: true|false
  merge_pr: true|false
  pr_reviews: true|false
  file_contents: true|false
  commits: true|false
```

### Step 4: Fallback Mapping

For each capability that is `false`, the dispatcher uses the fallback pattern defined in SKILL.md:

| Capability | Fallback |
|-----------|----------|
| `update_issue` | Comment with change content |
| `close_issue` | Comment "Closing: reason" |
| `sub_issues` | Comment-based linking on parent |
| `search_issues` | Iterative listing + client-side filter |
| `labels` | Labels only during `create_issue()` |

## Future MCP Plugin Path

When the GitBucket MCP plugin implements missing endpoints, the capability landscape changes dynamically. The dispatcher automatically uses full capabilities without code changes.

## Context Required

- Session values: GIT_PLATFORM
- Platform sub-skill: `../platforms/github-mcp/SKILL.md` or `../platforms/gitbucket-api/SKILL.md`

## Live Verification: Capabilities Evidence (MANDATORY)

**Each capability claim MUST be verified via tool call, not assumed from memory. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "GIT_PLATFORM is X" | Verify session init value | Check session init output | MISSING-ELEMENT |
| "Platform supports operation Y" | Probe platform SKILL.md or MCP | `read(path=".opencode/skills/issue-operations/platforms/<platform>/SKILL.md")` | CONFLICTING |
| "MCP plugin present" | Check for platform MCP tools | `grep(pattern="gitbucket_", path=".opencode/skills/issue-operations/platforms/")` | VERIFICATION-GAP |

**Evidence artifact:** Capability manifest returned from Step 3 with per-operation verification.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Platform not detected | MISSING-ELEMENT | flag-for-review | HALT — default to github-mcp |
| Capability claim wrong | CONFLICTING | auto-fix | Update capability set from live probe |
| MCP not present | VERIFICATION-GAP | auto-fix | Fall back to static manifest |