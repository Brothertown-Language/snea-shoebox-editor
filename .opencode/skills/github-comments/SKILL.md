---
name: github-comments
description: GitHub comment format and protocol for AI agents. Defines AI identity attribution, lifecycle status indicators, comment types, progress comments, closure summaries, and when to comment vs edit issue bodies.
license: MIT
compatibility: opencode
---

# GitHub Comment Protocol

Ensures all comments on issues and PRs follow correct format, are posted at the right time, and preserve history.

## When to Use

- Before posting ANY GitHub comment (MANDATORY - auto-loaded)
- Before editing issue bodies (verify attribution)
- After task completion (verify progress format)
- Before closing issues (verify closure format)

## Available Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete comment protocol with examples |

## AI Identity Attribution Format (CRITICAL)

**ALL comments MUST end with ONE byline combining status, agent, and model:**

```
<response content>

---
🤖 <status-emoji> <status-text> by <AgentName> (<ModelID>)[: optional-context]
```

### Status Emoji Guide

| Status | Emoji | Byline Format |
|--------|-------|---------------|
| Task Complete | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| In Progress | ↻ | `🤖 ↻ Working by <AgentName> (<ModelID>)` |
| Created | ✨ | `🤖 ✨ Created by <AgentName> (<ModelID>)[: Issue #N]` |
| Updated | 📝 | `🤖 📝 Updated by <AgentName> (<ModelID>)[: description]` |
| Rejected | ❌ | `🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>` |
| Superseded | 🔄 | `🤖 🔄 Superseded by <AgentName> (<ModelID>): <replacement-issue>` |

## Progress Comment Format (MANDATORY)

```
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**FORBIDDEN in Progress Comments:**

- File lists (redundant with git)
- "Next" field (dialog prompt)
- "Awaiting authorization" (use HALT)
- Technical changelogs (focus on impact)

## When to Comment vs Edit Body

| Action | Method | Use When |
|--------|--------|----------|
| Create issue | Body | Initial spec content |
| Update STATUS | Body | Phase/step markers |
| Task completion | Comment | Progress report |
| Closure | Comment with summary | Final status |

## Quick Start

Use `/skill github-comments --task overview` for complete protocol with examples.