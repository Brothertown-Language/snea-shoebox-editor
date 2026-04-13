# Task: format-comment

## Purpose

Format comments with AI identity attribution and proper structure. Only used for substantive comments that convey stakeholder-meaningful information. Comment bodies are prose-driven — use natural paragraphs, not rigid Changed/Added/Removed lists.

## Entry Criteria

- Comment content is substantive (conveys information stakeholders need to understand what changed or why)
- Comment type specified (completion, update, rejection)

## Exit Criteria

- Comment formatted with invariant byline
- Structure uses prose paragraphs, not rigid sections
- Emoji in plain text (not inside formatting)

## Procedure

### Step 1: Determine Comment Type

| Type | Purpose | Status Text |
|------|---------|-------------|
| Completion | Task finished | completed |
| Update | Modified existing content | updated |
| Rejection | Cannot proceed | rejected |

### Step 2: Apply Format Template

**Invariant byline format (all types):**
```
🤖 <AgentName> (<ModelID>) <status>
```

The byline is identical for all comment types — only the status text changes.

**Completion Template:**
```markdown
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 <AgentName> (<ModelID>) completed
```

**Update Template:**
```markdown
**Summary:**

<1-2 sentences describing what changed and why stakeholders need to know>

**Outcome:** <What changed for stakeholders>

---
🤖 <AgentName> (<ModelID>) updated
```

### Prose-Driven Comment Bodies (CRITICAL)

**Comment bodies MUST be prose-driven — natural paragraphs that explain what changed and why.**

**✅ CORRECT (prose-driven):**
```markdown
**Summary:**

Refactored the authentication module to use token-based sessions instead of cookie-based auth, resolving the session expiry issues reported in #42.

**Outcome:** Session management now uses JWT tokens with configurable expiry, eliminating 401 errors for long-lived sessions.

---
🤖 OpenCode (ollama-cloud/glm-5) completed
```

**❌ WRONG (rigid Changed/Added/Removed lists):**
```markdown
**Summary:**
- Changed: auth module to use tokens
- Added: JWT session support
- Removed: cookie-based sessions

---
🤖 OpenCode (ollama-cloud/glm-5) completed
```

**Why prose-driven:**
- Stakeholders need understanding, not commit logs
- Natural language communicates impact better than bullet inventories
- Rigid lists tend to become stale and miss context
- GitHub diffs already show what changed; comments explain WHY

### Step 3: Validate Format

**CRITICAL: Emoji must be PLAIN TEXT (not inside italic/bold formatting)**

❌ WRONG: `**Summary** 🤖 completed...`
✅ CORRECT: `**Summary:**\n...\n---\n🤖 <AgentName> (<ModelID>) completed`

**Checklist:**
- [ ] Emoji is outside markdown formatting
- [ ] Byline follows invariant format: `🤖 <AgentName> (<ModelID>) <status>`
- [ ] No "by" between model ID and status text
- [ ] No status emoji before status text (status is plain lowercase word)
- [ ] Summary is 1-2 sentences max
- [ ] Outcome states what changed
- [ ] Horizontal rule separates summary from byline
- [ ] Body is prose-driven, not rigid bullet lists

### Step 4: Return Formatted Comment

Return formatted comment for posting via `github_add_issue_comment`.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Emoji inside bold/italic | Move emoji outside formatting |
| Missing outcome | Add what changed for stakeholders |
| Summary too long | Reduce to 1-2 sentences |
| Wrong status text | Use lowercase plain text (completed, updated, rejected) |
| Rigid Changed/Added/Removed list | Rewrite as prose paragraphs |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL
- Related tasks: `post-completion`