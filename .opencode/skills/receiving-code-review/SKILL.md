---
name: receiving-code-review
description: Use when receiving code review feedback on a PR, or when addressing review comments. Triggers on: code review, PR feedback, review comment, address feedback, fix review, respond to review.
type: technique
license: MIT
compatibility: opencode
---

# Skill: receiving-code-review

## Overview

Workflow for responding to code review feedback on pull requests. This skill ensures all reviewer comments are addressed systematically, changes are minimal and targeted, and no scope creep occurs during review response. It is adapted from the NewsRx/opencode-gitbucket-superpowers workflow.

**Source Attribution:** This skill is adapted from NewsRx/opencode-gitbucket-superpowers workflow (branch: newsrx).

## Persona

You are a Review Responder. Your focus is addressing reviewer feedback precisely without expanding scope.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `address` | Address all review comments | ~700 |
| `respond` | Reply to review comments | ~400 |

## Invocation

- `/skill receiving-code-review` - Overview only
- `/skill receiving-code-review --task address` - Address review feedback
- `/skill receiving-code-review --task respond` - Reply to comments

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when:
   - PR receives review comments
   - User says "address review" or "fix review feedback"
   - Agent detects review comments on PR
   - NOT automatic — requires user instruction

2. **Scoping discipline:**
   - Address ONLY what the reviewer requested
   - No "while I'm here" changes
   - No refactoring beyond what was asked
   - No new features added during review

3. **Exit conditions:** Review response is COMPLETE when:
   - All reviewer comments addressed
   - All replies posted
   - Tests still pass
   - Branch pushed with changes

## Address Review Workflow

### Step 1: Collect All Review Comments

- Read all review comments on the PR
- Categorize by type (bug, style, design, question)
- Determine required action for each

### Step 2: Prioritize Changes

| Priority | Type | Action |
|----------|------|--------|
| 1 | Bug/defect | Must fix |
| 2 | Design concern | Must address (fix or explain why not) |
| 3 | Style/naming | Should fix |
| 4 | Suggestion | Consider, may decline with explanation |
| 5 | Question | Must answer |

### Step 3: Make Targeted Changes

For each comment:

```markdown
**Comment:** [Reviewer's feedback]
**Action:** Fix / Explain / Decline
**Change:** [What was changed, if fixing]
```

1. **Fix:** Make the minimal change addressing the feedback
2. **Explain:** If not fixing, explain why in a comment
3. **Decline:** If disagreeing, explain reasoning respectfully

### Step 4: Verify Changes

- Run tests to ensure no regression
- Run lint/typecheck
- Push changes to branch

### Step 5: Reply to Comments

Post replies to each review comment:

```markdown
**Response:** [Fixed / Explained / Declined]
**Details:** [What was changed or why not]

---
🤖 📝 Addressed by OpenCode (ollama-cloud/glm-5)
```

## Anti-Patterns

### 🚫 Scope Creep During Review

```python
# ❌ WRONG: Refactoring while addressing review
# Reviewer asked: "Rename this variable"
# Agent also: Refactored the entire function, changed return type, added logging
```

### ✅ Targeted Review Response

```python
# ✅ CORRECT: Address only what was requested
# Reviewer asked: "Rename this variable"
# Agent: Renamed the variable, nothing else
```

## Integration with Existing Workflow

### Dispatch Order

```
PR review received → receiving-code-review (address) → push changes → (reviewer re-reviews)
```

### GitBucket Platform Adaptations

- Read PR review comments via GitBucket API
- Post replies via GitBucket API
- Push changes to existing PR branch

### Git-Workflow Integration

- Address review comments on existing branch
- Push additional commits (do NOT squash review fixes)
- PR is updated automatically on push

## Cross-References

- Related skills: `requesting-code-review` (requesting review), `git-workflow` (branch management)
- Related guidelines: `050-scope-autonomy.md` (no scope creep), `060-tool-usage.md` (commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the NewsRx/opencode-gitbucket-superpowers repository (branch: newsrx). The original workflow ensures review feedback is addressed precisely without scope expansion.

**Key adaptations for OpenCode:**
- Integration with existing git-workflow skill
- GitBucket platform support via API
- Dispatch table integration for contextual invocation
- Scoping discipline enforcement