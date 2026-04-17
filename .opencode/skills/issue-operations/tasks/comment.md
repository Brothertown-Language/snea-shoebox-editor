# Task: comment

## Purpose

Post comments to issues/PRs following the substantive comment gate and byline format. Routes posting via platform sub-skill. Absorbs `github-comments` skill functionality.

## Entry Criteria

- Comment content is substantive (conveys information stakeholders need to understand what changed or why)
- Comment type specified (completion, update, rejection)
- Issue/PR number identified

## Exit Criteria

- If substantive: comment posted with correct byline format
- If not substantive: comment skipped (no posting)

## Procedure

### Step 1: Substantiveness Gate

Before posting, evaluate: Does this comment convey information a stakeholder needs to understand what changed or why?

| If | Action |
|----|--------|
| Comment explains substantive change stakeholders need to know | **Post with byline** |
| Comment is merely "Task complete" or status update | **SKIP — do not post** |
| Comment explains what changed during closure (beyond status) | **Post with byline** |

### Step 2: Determine Comment Type

| Type | Purpose | Status Text | Icon |
|------|---------|-------------|------|
| Completion | Task finished | completed | ✅ |
| Update | Modified existing content | updated | 📝 |
| Rejection | Cannot proceed | rejected | ❌ |
| Copy Editor | Posting on behalf of user | `🤖 ✎📝 on behalf of <AgentName>` | ✎ |

### Step 3: Apply Format Template

**Invariant byline format (all types):**
```
🤖 <AgentName> (<ModelId>) <status-icon> <status>
```

**Completion Template:**
```markdown
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 <AgentName> (<ModelId>) ✅ completed
```

**Update Template:**
```markdown
**Summary:**

<1-2 sentences describing what changed and why stakeholders need to know>

**Outcome:** <What changed for stakeholders>

---
🤖 <AgentName> (<ModelId>) 📝 updated
```

### Prose-Driven Comment Bodies (CRITICAL)

**Comment bodies MUST be prose-driven — natural paragraphs that explain what changed and why.**

Stakeholders need understanding, not commit logs. GitHub diffs already show what changed; comments explain WHY.

### Step 4: Validate Format

**CRITICAL: Emoji must be PLAIN TEXT (not inside italic/bold formatting)**

- Emoji is outside markdown formatting
- Byline follows invariant format
- Summary is 1-2 sentences max
- Outcome states what changed
- Horizontal rule separates summary from byline
- Body is prose-driven, not rigid bullet lists

### Step 5: Post Comment (Platform Routing)

**GitHub platform:**
```python
github_add_issue_comment(
    owner=<GitOwner>,
    repo=<GitRepo>,
    issue_number=N,
    body=formatted_comment
)
```

**GitBucket platform:**
```python
from skills.gitbucket_api.tools import GitBucketAPI
api = GitBucketAPI()
api.add_issue_comment(
    owner=<GitOwner>,
    repo=<GitRepo>,
    issue_number=N,
    body=formatted_comment
)
```

## Live Verification: Comment Claims (MANDATORY)

**When this task prepares a comment, any claims about issue/PR state MUST be verified against live state.**

| Comment Claim | Verification Action | Tool Call |
|--------------|-------------------|-----------|
| "Spec revised" in revision comment | Verify spec body actually changed | `github_issue_read(method=get, issue_number=N)` → compare body |
| "Implementation complete" in closure comment | Verify PR merged via platform API | `github_pull_request_read(method=get)` → check `merged` field |
| "Fixes #N" in PR comment | Verify issue #N exists | `github_issue_read(method=get, issue_number=N)` |

## Common Issues

| Issue | Resolution |
|-------|------------|
| Non-substantive content | Skip posting entirely — progress goes to chat only |
| Emoji inside bold/italic | Move emoji outside formatting |
| Missing outcome | Add what changed for stakeholders |
| Summary too long | Reduce to 1-2 sentences |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, GIT_PLATFORM
- Related tasks: `close` (uses comment for closure), `link-sub-issue` (uses comment for fallback)
- Platform routing: `../platforms/github-mcp/` or `../platforms/gitbucket-api/`