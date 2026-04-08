# Fragment: AI Identity Attribution

**AI Identity Attribution Format**

### Single Combined Byline (CRITICAL)

**ALL comments MUST end with ONE byline that combines status, agent, and model.**

**Format:**
```
<response content>

---
🤖 <status-emoji> <status-text> by <AgentName> (<ModelID>)
```

**For progress comments:**
```
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

<1-2 sentences describing stakeholder value.>

**Outcome:** <What changed for stakeholders>
```

**Components (supplied dynamically at runtime):**
- `<status-emoji>`: Status indicator (✅ ✨ 📝 ❌ 🔄 ↻ ⚠️ 🔍 📋 ✎)
- `<status-text>`: Status description (Completed, Created, Updated, Rejected, Superseded, Working)
- `<AgentName>`: AI's actual name (e.g., `OpenCode Desktop`, `OpenCode`)
- `<ModelID>`: Model identifier with provider (e.g., `<ModelID>`)

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity.**

**Rule:** Byline = WHO did WHAT. Details belong in comment body, not byline. No extra context.

### Status Emoji Guide

| Status | Emoji | Byline Format |
|--------|-------|---------------|
| Task Complete | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| In Progress | ↻ | `🤖 ↻ Working by <AgentName> (<ModelID>)` |
| Created | ✨ | `🤖 ✨ Created by <AgentName> (<ModelID>)` |
| Updated | 📝 | `🤖 📝 Updated by <AgentName> (<ModelID>)` |
| Copy Editor | ✎ | `🤖 ✎ on behalf of <UserName>` |
| Completed | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| Rejected | ❌ | `🤖 ❌ Rejected by <AgentName> (<ModelID>)` |
| Superseded | 🔄 | `🤖 🔄 Superseded by <AgentName> (<ModelID>)` |
| Blocking | ⚠️ | `🤖 ⚠️ Blocking by <AgentName> (<ModelID>)` |
| Analysis | 🔍 | `🤖 🔍 Analysis by <AgentName> (<ModelID>)` |
| Decision | 📋 | `🤖 📋 Decision by <AgentName> (<ModelID>)` |

**Rule:** Byline = WHO did WHAT. Details belong in comment body, not byline. No extra context.

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
- Agent posts progress comments for its own implementation tasks
- Agent creates issues for user-approved specs (those already have user attribution)
- Agent performs independent implementation work

#### Copy Editor Byline Format

**Format:**
```
<content posted on behalf of user>

---
🤖 ✎ on behalf of <UserName>
```

**Components:**
- `✎`: Pencil emoji indicates editing/posting role (not authorship)
- `on behalf of <UserName>`: The user who requested/owns the content

**Rule:** Byline = WHO did WHAT. Details belong in comment body, not byline.

<!--
Fragment ID: ai-identity
Estimated tokens: 470
Type: text-block
Sync status: synchronized
-->