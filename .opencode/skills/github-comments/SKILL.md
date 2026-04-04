---
name: github-comments
description: GitHub comment format and protocol for AI agents. Defines AI identity attribution, lifecycle status indicators, comment types, progress comments, closure summaries, and when to comment vs edit issue bodies.
license: MIT
compatibility: opencode
---

# Skill: github-comments

Comment format enforcement for different contexts, audiences, and locations. Defines WHEN to post comments and WHAT those comments should contain.

## ⚠️ CRITICAL: Audience-First Design

**Comments must match their AUDIENCE and LOCATION:**

| Audience | Location | Needs | Timeframe |
|----------|----------|-------|-----------|
| Future maintainers | GitHub Issue | Context: WHAT/WHY changed | Historical record |
| Developer (immediate) | Chat | Impact: stakeholder value | Immediate action |

**CRITICAL VIOLATION: URLs in GitHub Issue Comments**

- **URLs are for CHAT ONLY**
- **GitHub Issue comments MUST NOT contain URLs**
- **Chat output MUST include URL when relevant**

## When to Use

- Before posting ANY GitHub comment (MANDATORY - auto-loaded)
- Before editing issue bodies (verify attribution)
- After task completion (verify progress format)
- Before closing issues (verify closure format)

## Available Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete comment protocol with examples |

## GitHub Issue Comments (Future Maintainers)

**Audience:** Future maintainers reading issue history

**Purpose:** Historical context for future readers

**Location:** GitHub Issue comments

### When to Comment on Issues

| Context | Comment? | Byline Format |
|---------|----------|---------------|
| Issue Creation | YES | `🤖 ✨ Created by <AgentName> (<ModelID>)` |
| Issue Update (Substantive) | YES | `🤖 📝 Updated by <AgentName> (<ModelID>)` |
| Issue Update (Non-Substantive) | NO | (No comment needed) |
| Issue Closure | YES | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |

### Issue Creation Comment

```markdown
🤖 ✨ Created by <AgentName> (<ModelID>)
```

**NO summary needed** - the issue body already contains the spec.

### Substantive Update Comment (Context-Based Summary)

```markdown
Added Phase 2 to spec. Phase 2 implements the API layer for the approval workflow.

**Changes:**
- Added Phase 2 implementation steps
- Defined API endpoints: approve(), reject(), getStatus()
- Specified error handling for invalid states

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

**Context-based summary explains WHAT changed and WHY** (technical context for future maintainers).

### Non-Substantive Update (NO Comment)

| Non-Substantive Updates | Substantive Updates |
|------------------------|-------------------|
| STATUS field updates | Adding/removing phases |
| Label changes | Modifying requirements |
| Checklist marker updates | Changing success criteria |
| Typo/formatting fixes | Altering implementation approach |
| Origin links at top of body | Significant content changes |

**Rule:** If it doesn't change meaning, don't comment.

### Issue Closure Comment

```markdown
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

Implemented comment format enforcement with clear audience/location distinction.

**Outcome:** All four guideline/skill files updated with correct examples.

All tasks complete from this specification.
```

**NO URL** - URLs belong in Chat, not GitHub Issue comments.

## Chat Output (Immediate Developer)

**Audience:** Developer who needs to make decisions

**Purpose:** Immediate visibility and action support

**Location:** Chat output (terminal, IDE, web chat)

### When to Output to Chat

| Context | Output? | Byline Format |
|---------|----------|---------------|
| Implementation Complete | YES | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |

### Executive Summary (Chat Output)

```markdown
**Summary:**

Implemented comment format enforcement with audience-first structure.

**Outcome:** Developers can now distinguish when to use GitHub Issue comments (context-based summaries) vs Chat output (executive summaries with URLs).

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/dev...<branch>
```

**Executive summary explains IMPACT and VALUE** (stakeholder benefit, immediate action).

**URL Placement:** URL MUST be the FINAL LINE of chat output.

## 🚫 CRITICAL VIOLATIONS (Zero Tolerance)

| Violation | Consequence |
|-----------|-------------|
| URLs in GitHub Issue comments | CRITICAL - wrong location |
| Executive summaries in issues | CRITICAL - wrong audience |
| Comments for non-substantive updates | CRITICAL - noise |
| Wrong content for wrong audience | CRITICAL - confusion |

## Context-Based vs Executive Summaries

### Context-Based Summary (GitHub Issue)

**WHAT changed and WHY:**

```markdown
Added Phase 2 to spec. Phase 2 implements the API layer for the approval workflow.

**Changes:**
- Added Phase 2 implementation steps
- Defined API endpoints: approve(), reject(), getStatus()
- Specified error handling for invalid states

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

**Audience:** Future maintainers reading history

**Location:** GitHub Issue comment

**Content:** Technical context, WHAT/WHY

**URLs:** FORBIDDEN

### Executive Summary (Chat)

**Impact and stakeholder value:**

```markdown
**Summary:**

Implemented API layer for approval workflow. Developers can now use approve()/reject()/getStatus() endpoints.

**Outcome:** Approval workflow is now accessible via REST API.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/dev...<branch>
```

**Audience:** Developer making decisions

**Location:** Chat output

**Content:** Impact/value, stakeholder benefit

**URLs:** REQUIRED (when relevant)

## AI Identity Attribution Format

**ALL comments MUST end with ONE byline:**

```
<response content>

---
🤖 <status-emoji> <status-text> by <AgentName> (<ModelID>)[: optional-context]
```

### ⚠️ MANDATORY: Dynamic Runtime Identity Detection

**Agents MUST use their ACTUAL runtime identity — NEVER copy placeholder values from examples.**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
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

### When to Include Context in Byline

| Context | Include Context? |
|---------|-------------------|
| Progress/Task completion | NO (content already describes work) |
| Issue creation | OPTIONAL (issue number is redundant on same issue) |
| Content updates | BRIEF description of change |
| Rejection/Superseded | YES (reason or replacement reference required) |

**Minimal Byline Principle:** Default to minimal byline format. Add context only when it clarifies ambiguity or provides essential reference.

## Quick Start

Use `/skill github-comments --task overview` for complete protocol with examples.