# Task: respond

## Purpose

Reply to review comments after changes have been made, providing clear documentation of what was changed and why.

## Operating Protocol

1. Invoked by: `/skill receiving-code-review --task respond`
2. When to use: After `--task address` has been completed — replying to reviewer comments
3. Exit criteria: All comments replied to, HALT and wait for next review round

## Reply Formats

### For Fixed Comments

```markdown
**Response:** Fixed
**Details:** [What was changed and where]

🤖 <AgentName> (<ModelID>) ✅ completed
```

### For Explained Comments (Not Fixed)

```markdown
**Response:** Explained
**Details:** [Why this was not changed — rationale for keeping current approach]

🤖 <AgentName> (<ModelID>) ✅ completed
```

### For Declined Comments

```markdown
**Response:** Declined
**Details:** [Respectful reasoning for disagreeing with the suggestion]

🤖 <AgentName> (<ModelID>) ✅ completed
```

## Important Notes

- Always be respectful and constructive
- Provide specific details about what was changed
- Link to specific commits when possible
- If declining, offer clear reasoning
- HALT after responding — wait for next review round

## Context Required

- Related skills: `receiving-code-review` (parent skill)
- Related tasks: `address`