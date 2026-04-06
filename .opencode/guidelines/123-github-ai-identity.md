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
- `[: optional-context]`: Context ONLY when useful (replacement reference, rejection reason)
  - **Progress comments**: Omit (content already describes the work)
  - **Issue creation**: NO context (issue number is redundant on same issue)
  - **Rejection/Superseded**: Include reason or replacement reference
  - **AI Agent Judgment**: Use minimal byline suffix text by default; add extra context only when it provides clear value

### ⚠️ MANDATORY: Dynamic Runtime Identity Detection

**Agents MUST use their ACTUAL runtime identity — NEVER copy placeholder values from examples.**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/*" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**Example Values in Guidelines are ILLUSTRATIVE:**
- `<AgentName> (<ModelID>)` → Example only
- `AI Assistant (model-id)` → Placeholder only
- **DETECT YOUR OWN IDENTITY** at runtime

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

**Minimal Byline Principle:** Default to minimal byline format (e.g., `🤖 📝 Updated by <AgentName> (<ModelID>)`). Add suffix context only when it clarifies ambiguity or provides essential reference.

**Emoji Formatting:** Emoji must be PLAIN TEXT (NOT inside italic/bold formatting) to prevent render failures.

### Examples

**Task completion (no context needed):**
```
<summary content>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**Created issue (optional context):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by <AgentName> (<ModelID>): Issue #N
```

**Updated issue (brief context):**
```
🤖 ✨ Created by <AgentName> (<ModelID>): Issue #N
🤖 📝 Updated by <AgentName> (<ModelID>): Added Phase 2
```

**Rejected proposal (reason required):**
```
---
🤖 ❌ Rejected by <AgentName> (<ModelID>): Duplicate of #400
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

🤖 ✨ Created by <AgentName> (<ModelID>): Issue #N
🤖 📝 Updated by <AgentName> (<ModelID>): Added Phase 2
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

---

## Copy Editing Attribution (Human Provides Substance)

**When an AI agent copy edits a human's message without generating substantive content:**

1. **Human is the primary author** — they provided the ideas, substance, and key content
2. **AI role is copy editing** — formatting, grammar correction, tone adjustment
3. **Attribution reflects supporting role:**

```markdown
<Human's message content>

---
🤖 [AI: AgentName (Model)] — Copy editing on behalf of <HumanName>
```

### Key Distinction

| Role | Attribution Format | Primary Author |
|------|-------------------|----------------|
| **Content generation** | `Co-authored with AI: AgentName (Model)` | AI generated substantive content |
| **Copy editing** | `[AI: AgentName (Model)] — Copy editing on behalf of <HumanName>` | Human provided substance, AI improved presentation |

### Examples

**Content Generation (AI as Co-Author):**
```markdown
# Feature Proposal: Add Rate Limiting

[Idea and substance generated by AI agent]

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

**Copy Editing (Human as Primary Author):**
```markdown
# Feature Proposal: Add Rate Limiting

[Idea and substance from human developer]

AI agent improved formatting, grammar, and tone.

---
🤖 [AI: OpenCode (ollama-cloud/glm-5)] — Copy editing on behalf of Michael Conrad
```

### When to Use Copy Editing Attribution

| Scenario | Attribution |
|----------|-------------|
| AI formats human's rough notes | Copy editing |
| AI fixes grammar in human's message | Copy editing |
| AI adjusts tone of human's feedback | Copy editing |
| AI structures human's ideas into spec | Copy editing |
| AI generates new ideas from scratch | Content generation (co-authorship) |
| AI expands human's brief into full spec | Content generation (co-authorship) |
| AI rewrites human's spec entirely | Content generation (co-authorship) |

### Critical Distinction

**Copy editing = Human provided ideas and substance, AI improved presentation**
**Content generation = AI created substantive ideas or content**

If unsure, ask: "Did the human provide the core ideas, or did the AI generate them?"

- Human provided core ideas → Copy editing
- AI generated core ideas → Content generation

---

## 🚫 CRITICAL VIOLATIONS (Zero Tolerance)

| Violation | Consequence |
|-----------|--------------|
| Ignoring user comments without posting response | CRITICAL — user cannot see your reasoning |
| Closing issue without explanation comment | CRITICAL — no audit trail |
| Editing issue body to add "CLOSED" text | CRITICAL — destroys history |
| Using PREFIX for comment attribution | CRITICAL — wrong position |
| Replacing existing attribution (not appending) | CRITICAL — destroys history |
| Wrapping emoji in italic/bold | CRITICAL — render failure |

**See `github-comments` skill for:**
- Complete comment format rules
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