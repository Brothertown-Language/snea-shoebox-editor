# GitHub Workflow: AI Identity in Comments

**See `github-comments` skill for complete comment protocol.**

## 🤖 MANDATORY: Single Combined Byline Format

ALL comments on issues and PRs MUST have a SINGLE byline at the END combining status, agent, and model.

### Unified Byline Format

**Format:**
```
<response content>

---
🤖 <status-emoji> <status-text> by <AgentName> (<ModelID>)[: optional-context]
```

**Components (supplied dynamically at runtime):**
- `<status-emoji>`: Status indicator (✅ ✨ 📝 ❌ 🔄 ↻ ⚠️ 🔍 📋)
- `<status-text>`: Status description (Completed, Created, Updated, Rejected, Superseded, Working)
- `<AgentName>`: AI's actual name (e.g., `OpenCode Desktop`, `OpenCode`)
- `<ModelID>`: Model identifier with provider (e.g., `ollama-cloud/glm-5`)
- `[: optional-context]`: Context ONLY when useful (issue number, replacement reference, reason)
  - **Progress comments**: Omit (content already describes the work)
  - **Issue creation/completion**: Include issue number if useful
  - **Rejection/Superseded**: Include reason or replacement reference

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity.**

**Emoji Formatting:** Emoji must be PLAIN TEXT (NOT inside italic/bold formatting) to prevent render failures.

### Examples

**Task completion (no context needed):**
```
<summary content>

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

**Created issue (optional context):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
```

**Updated issue (brief context):**
```
🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added Phase 2
```

**Rejected proposal (reason required):**
```
---
🤖 ❌ Rejected by OpenCode (ollama-cloud/glm-5): Duplicate of #400
```

---

## Status Emoji Reference

| Status | Emoji | Byline Format |
|--------|-------|---------------|
| Task Complete | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| In Progress | ↻ | `🤖 ↻ Working by <AgentName> (<ModelID>)` |
| Created | ✨ | `🤖 ✨ Created by <AgentName> (<ModelID>)[: Issue #N]` |
| Updated | 📝 | `🤖 📝 Updated by <AgentName> (<ModelID>)[: description]` |
| Completed | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| Rejected | ❌ | `🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>` |
| Superseded | 🔄 | `🤖 🔄 Superseded by <AgentName> (<ModelID>): <replacement-issue>` |
| Blocking | ⚠️ | `🤖 ⚠️ Blocking by <AgentName> (<ModelID>): <reason>` |
| Analysis | 🔍 | `🤖 🔍 Analysis by <AgentName> (<ModelID>): <topic>` |
| Decision | 📋 | `🤖 📋 Decision by <AgentName> (<ModelID>): <result>` |

---

## Issue/PR Body Attribution (Append Always)

**🚨 CRITICAL: ALWAYS APPEND. NEVER REPLACE.**

| Action | Operation | Byline |
|--------|-----------|--------|
| Create issue | Append | `🤖 ✨ Created by <AgentName> (<ModelID>)[: Issue #N]` |
| Update content | Append | `🤖 📝 Updated by <AgentName> (<ModelID>)[: description]` |
| Complete issue | Append | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| Reject issue | Append | `🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>` |
| Supersede issue | Append | `🤖 🔄 Superseded by <AgentName> (<ModelID>): <replacement-issue>` |

**When to Include Context:**
- **Progress/Task completion**: No context needed (content already describes the work)
- **Issue creation**: Optional — use if issue number provides useful reference
- **Content updates**: Brief description of what changed
- **Rejection/Superseded**: Always include reason or replacement reference

**Why append-only:**
- Same rule everywhere (no confusion)
- Matches comment history behavior
- Preserves full lifecycle visibility
- No special cases to remember

**Example lifecycle (append-only):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added Phase 2
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

---

## 🚫 CRITICAL VIOLATIONS (Zero Tolerance)

| Violation | Consequence |
|-----------|--------------|
| Missing progress comments after task completion | CRITICAL — implementation incomplete |
| Ignoring user comments without posting response | CRITICAL — user cannot see your reasoning |
| Closing issue without explanation comment | CRITICAL — no audit trail |
| Editing issue body to add "CLOSED" text | CRITICAL — destroys history |
| Proceeding to next task without posting comment | CRITICAL — breaks workflow |
| Using PREFIX for comment attribution | CRITICAL — wrong position |
| Replacing existing attribution (not appending) | CRITICAL — destroys history |
| Wrapping emoji in italic/bold | CRITICAL — render failure |

**See `github-comments` skill for:**
- Complete comment format rules
- Progress comment format and timing
- Issue body update rules
- Closure comment format
- When NOT to comment

---

## Integration with Guidelines

| Guideline | Section |
|-----------|---------|
| `120-github-issue-first.md` | Issue workflow, sub-issues |
| `000-critical-rules.md` | Critical violation enforcement |
| `github-comments` skill | Complete comment protocol |

---