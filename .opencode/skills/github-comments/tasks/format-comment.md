# Task: format-comment

## Purpose

Format comments with AI identity attribution, lifecycle status indicators, and proper structure. Only used for substantive comments that convey stakeholder-meaningful information.

## Entry Criteria

- Comment content is substantive (conveys information stakeholders need to understand what changed or why)
- Comment type specified (completion, update, rejection)

## Exit Criteria

- Comment formatted with proper byline
- Lifecycle status indicator added
- Structure follows GitHub comment format
- Emoji in plain text (not inside formatting)

## Procedure

### Step 1: Determine Comment Type

| Type | Purpose | Emoji |
|------|---------|-------|
| Completion | Task finished | ✅ |
| Update | Modified existing content | 📝 |
| Rejection | Cannot proceed | ❌ |

### Step 2: Apply Format Template

**Completion Template:**
```markdown
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**Update Template:**
```markdown
**Summary:**

<1-2 sentences describing what changed and why stakeholders need to know>

**Outcome:** <What changed for stakeholders>

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

### Step 3: Validate Format

**CRITICAL: Emoji must be PLAIN TEXT (not inside italic/bold formatting)**

❌ WRONG: `**Summary** 🤖 ✅ Completed...`
✅ CORRECT: `**Summary:**\n...\n---\n🤖 ✅ Completed by...`

**Checklist:**
- [ ] Emoji is outside markdown formatting
- [ ] Byline includes agent name and model ID
- [ ] Summary is 1-2 sentences max
- [ ] Outcome states what changed
- [ ] Horizontal rule separates summary from byline

### Step 4: Return Formatted Comment

Return formatted comment for posting via `github_add_issue_comment`.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Emoji inside bold/italic | Move emoji outside formatting |
| Missing outcome | Add what changed for stakeholders |
| Summary too long | Reduce to 1-2 sentences |
| Wrong emoji for type | Use correct lifecycle indicator |

## Context Required

- Session values: GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL
- Related tasks: `post-completion`