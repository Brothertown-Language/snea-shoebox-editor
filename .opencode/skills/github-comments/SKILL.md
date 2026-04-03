______________________________________________________________________

## name: github-comments description: GitHub comment format and protocol for AI agents. Defines AI identity attribution, lifecycle status indicators, comment types, progress comments, closure summaries, and when to comment vs edit issue bodies. license: MIT compatibility: opencode

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

### ⚠️ MANDATORY: Dynamic Runtime Identity Detection

**Agents MUST use their ACTUAL runtime identity — NEVER copy placeholder values from examples.**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/glm-5" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**Example Values in Guidelines are ILLUSTRATIVE:**

- `OpenCode (ollama-cloud/glm-5)` → Example only
- `AI Assistant (model-id)` → Placeholder only
- **DETECT YOUR OWN IDENTITY** at runtime

**When Identity Unknown:**

- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

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

https://github.com/<owner>/<repo>/compare/main...<branch>
```

### ⚠️ URL Placement Rule (MANDATORY)

**URLs MUST appear LAST in executive summaries.**

| Element | Position |
|---------|----------|
| Summary text | First |
| Outcome | Middle |
| Agent byline | Last line before URL |
| URL | FINAL LINE (always last) |

**Why URL last:**

- URLs are typically long and may wrap across lines
- Placing URLs last allows developers to quickly scan summary content first
- Easy visual anchor: "look for the URL at the end"
- Consistent pattern across all AI-generated summaries

**Multiple URLs:** Place the primary URL (most actionable) last. Secondary URLs can appear in body with context.

**No URLs:** If no URLs are relevant, executive summary ends with the summary text. No URL placeholder needed.

**FORBIDDEN in Progress Comments:**

- File lists (redundant with git)
- "Next" field (dialog prompt)
- "Awaiting authorization" (use HALT)
- Technical changelogs (focus on impact)
- URLs anywhere except at the end

## When to Comment vs Edit Body

| Action | Method | Use When |
|--------|--------|----------|
| Create issue | Body | Initial spec content |
| Update STATUS | Body | Phase/step markers |
| Task completion | Comment | Progress report |
| Closure | Comment with summary | Final status |

## Quick Start

Use `/skill github-comments --task overview` for complete protocol with examples.
