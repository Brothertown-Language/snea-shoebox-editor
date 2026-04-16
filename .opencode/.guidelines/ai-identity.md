# Fragment: AI Identity Attribution

**AI Identity Attribution Format**

### Single Combined Byline (CRITICAL)

**ALL substantive comments and issue body footers MUST end with ONE byline that combines agent, model, and status.** Non-substantive comments should not be posted (per `github-comments` skill).

**Authoritative format (from `000-critical-rules.md`):**
```
<response content>

---
🤖 <AgentName> (<ModelID>) <status-icon> <status>
```

**For completion comments:**
```
**Summary:**

<1-2 sentences describing stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 <AgentName> (<ModelID>) ✅ completed
```

**Components (supplied dynamically at runtime):**
- `<AgentName>`: AI's actual name (e.g., `OpenCode Desktop`, `OpenCode`)
- `<ModelID>`: Model identifier with provider (e.g., `<ModelID>`)
- `<status-icon>`: Status icon from the iconography map (preferred where feasible)
- `<status>`: Status in plain text (completed, created, updated, rejected, etc.). Use `other` as fallback when no canonical status fits.

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity.**

**Rule:** Byline = WHO (model) + STATUS (icon + text). Status icons are preferred where feasible. Details belong in comment body, not byline.

### Status Text Guide

| Status | Icon | Byline |
|--------|------|--------|
| Task Complete | ✅ | `🤖 <AgentName> (<ModelID>) ✅ completed` |
| In Progress | 🔄 | `🤖 <AgentName> (<ModelID>) 🔄 working` |
| Created | ➕ | `🤖 <AgentName> (<ModelID>) ➕ created` |
| Updated | 📝 | `🤖 <AgentName> (<ModelID>) 📝 updated` |
| Rejected | ❌ | `🤖 <AgentName> (<ModelID>) ❌ rejected` |
| Superseded | ⏭️ | `🤖 <AgentName> (<ModelID>) ⏭️ superseded` |
| Blocking | 🚫 | `🤖 <AgentName> (<ModelID>) 🚫 blocking` |
| Analysis | 🔍 | `🤖 <AgentName> (<ModelID>) 🔍 analysis` |
| Decision | ✋ | `🤖 <AgentName> (<ModelID>) ✋ decision` |
| Other | 🎯 | `🤖 <AgentName> (<ModelID>) 🎯 other` |
| Copy Editor | ✎ | `🤖 ✎📝 on behalf of <AI-Name>` |

When no canonical status matches the agent's current state, use `other` as the status text with the 🎯 icon rather than inventing a new status word. This ensures bylines remain parseable and consistent.

Status icons are preferred where the AI agent can determine the appropriate icon. When in doubt, use the plain-text status alone without an icon. Do not invent new icons.

**Rule:** Byline = WHO (model). Status icons replace plain-text status words to improve visual scanning. Details belong in comment body, not byline.

### Copy Editor Byline (User-Authored Content)

#### When to Use

Use the **Copy Editor** byline when posting content on behalf of users:
- User asks agent to investigate a codebase and post findings to GitHub
- User asks agent to analyze an issue and comment with results
- User requests agent to update an issue with investigation results
- Agent posts analysis, findings, or summaries on behalf of user

#### When NOT to Use

Use standard bylines (Created, Completed, Updated) for:
- Agent creates its own spec/issue for implementation work
- Agent posts substantive comments for its own implementation tasks
- Agent creates issues for user-approved specs (those already have user attribution)
- Agent performs independent implementation work

#### Copy Editor Byline Format

**Format:**
```
<content posted on behalf of user>

---
🤖 ✎📝 on behalf of <AI-Name>
```

**Components:**
- `✎`: Pencil emoji indicates editing/posting role (not authorship)
- `📝`: Updated icon for copy editor context
- `on behalf of <AI-Name>`: The AI agent posting on behalf of the user

**Rule:** Byline = WHO did WHAT. Details belong in comment body, not byline.

<!--
Fragment ID: ai-identity
Estimated tokens: 470
Type: text-block
Sync status: synchronized
-->