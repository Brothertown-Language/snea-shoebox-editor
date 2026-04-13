# Task: address

## Purpose

Address all review comments on a PR systematically, making only requested changes without scope creep.

## Operating Protocol

1. Invoked by: `/skill receiving-code-review --task address`
2. When to use: When PR has received review feedback that needs to be addressed
3. Exit criteria: All reviewer comments addressed, replies posted, tests pass, branch pushed

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
🤖 <AgentName> (<ModelID>) addressed
```

## Anti-Patterns

### 🚫 Scope Creep During Review

Reviewer asked: "Rename this variable"
Agent also: Refactored the entire function, changed return type, added logging

### ✅ Targeted Review Response

Reviewer asked: "Rename this variable"
Agent: Renamed the variable, nothing else

## Context Required

- Related skills: `receiving-code-review` (parent skill)
- Related tasks: `respond`