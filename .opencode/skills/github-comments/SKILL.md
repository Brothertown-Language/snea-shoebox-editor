---
name: github-comments
description: GitHub comment format and protocol for AI agents. Defines AI identity attribution, lifecycle status indicators, comment types, progress comments, closure summaries, and when to comment vs edit issue bodies.
license: MIT
compatibility: opencode
---

# GitHub Comment Protocol

## Role

You are a GitHub Comment Protocol enforcer. Your focus is ensuring all comments on issues and PRs follow the correct format, are posted at the right time, and preserve history by preferring comments over issue body edits.

## AI Identity Attribution Format

### Single Combined Byline (CRITICAL)

**ALL comments MUST end with ONE byline that combines status, agent, and model.**

**Format:**
```
<response content>

---
🤖 <status-emoji> <status-text> by <AgentName> (<ModelID>)[: optional-context]
```

**For progress comments:**
```
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

<1-2 sentences describing stakeholder value.>

**Outcome:** <What changed for stakeholders>
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

### Status Emoji Guide

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

### Issue/PR Body Attribution (Lifecycle Status)

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

**Example lifecycle (append-only):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added Phase 2
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

**Why append-only:**
- Same rule everywhere (no confusion)
- Matches comment history behavior (comments append)
- Preserves full lifecycle visibility
- No special cases to remember

---

## Comment Type Decision Table

| Action | Post Comment? | Reason |
|--------|---------------|--------|
| Create new issue | ❌ NO | Issue body is the communication |
| Update issue body (textual content) | ✅ YES | Explain the change |
| Update issue body (STATUS field only) | ❌ NO | Status tracking, not narrative |
| Complete implementation task | ✅ YES | Document progress |
| Create PR | ✅ YES | Link to issue |
| Close issue | ✅ YES | Provide closing summary |
| Alter spec (add/remove phases, steps) | ✅ YES | Document spec changes |
| Review status without action | ❌ NO | No value added |
| Label changes | ❌ NO | GitHub auto-tracks |
| Checklist completion (`☐` → `☑`) | ❌ NO | Status tracking |

---

## Progress Comments (MANDATORY)

**Every implementation step MUST be documented with a comment on the associated issue.**

### When to Post

- After completing EACH task in multi-task implementation
- After ANY file modification
- When creating PR
- NEVER wait until all tasks complete — post after EACH task

### Chat Output Rule

**Progress executive summaries go to BOTH GitHub comments AND chat.**

| Location | Content |
|----------|---------|
| **GitHub Issue Comment** | Full executive summary (summary, outcome) |
| **Chat Output** | Same executive summary (summary, outcome) |

**Why:** Both GitHub history AND chat transcript should show progress. GitHub preserves long-term history; chat maintains session context.

**✅ DO:** Post executive summary to GitHub, then provide SAME summary in chat
**🚫 NEVER:** Skip either location
**🚫 NEVER:** Put full summary in chat but skip GitHub comment

### ✅ REQUIRED Format: Executive Summary

**For intermediate task (multi-task spec):**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**For final task or single-task spec:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Executive Summary Requirements

The summary MUST answer:
1. **What changed?** — The actual implementation/fix/enhancement
2. **Why it matters** — Impact on stakeholders (users, developers, system)
3. **Result** — Improved behavior, new capability, fixed issue

### 🚫 FORBIDDEN in Progress Comments

- **File lists** — Redundant (visible in git commits)
- **"Next" field** — Dialog prompt (violates the "Never Prompt in Comments" rule in `AGENTS.md`)
- **Punch-list format** — Use executive summary paragraphs
- **"Awaiting authorization"** — Use HALT protocol, not comments
- **Technical changelog** — Focus on impact, not file-by-file changes
- **Just "I did X"** — Explain WHY it matters

### Why Executive Summaries?

1. **Stakeholder value** — Focus on impact, not technical details
2. **No redundancy** — Git shows file changes; comments explain significance
3. **No dialog prompts** — "Next:" violates the HALT protocol
4. **Clear completion** — Explicit "All tasks complete" when done
5. **Chat visibility** — Format renders well in both GitHub and AI chat

### Sequence Enforcement

1. ✅ Complete the implementation
2. ✅ Post progress comment IMMEDIATELY
3. ✅ ONLY THEN: Move to next task or report completion

**🚫 WRONG:** Complete task → Move to next → Comment later
**✅ RIGHT:** Complete task → Comment → Then move to next

---

## Issue Body Update Rules

### Issue Body Attribution (MANDATORY)

After creating or updating an issue body:

1. **Append attribution footer** (NEVER replace existing footer)
2. **Format:** `🤖 <status-emoji> *<status-text> by AI: <AgentName> (<ModelID>)*`
3. **Emoji OUTSIDE italic formatting** (plain text for proper rendering)
4. **Preceded by blank line and `---` separator**

### Two-Step Operation for Content Updates

When updating textual content in an issue body:

1. **First**: `github_issue_write method=update` (update body)
2. **IMMEDIATELY after**: Append attribution footer AND `github_add_issue_comment` (explain change)

**⚠️ CRITICAL**: Append attribution, never replace. Comment to explain change.

### Comment Format for Body Updates

```
🤖 📝 Updated: <reason>

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

### Spec Alteration Format

```
🤖 📝 Spec altered: <summary>

- Changed: <what changed>
- Added: <what added>
- Removed: <what removed>

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

### What Counts as "Textual Content"

| Content Type | Requires Comment? |
|--------------|-------------------|
| Objective, requirements, spec sections | ✅ YES |
| Roadmap/task list additions/removals | ✅ YES |
| Prose content changes | ✅ YES |
| STATUS field updates | ❌ NO |
| Label changes | ❌ NO |
| Checklist markers (`☐` → `☑`) | ❌ NO |
| Typo fixes (no meaning change) | ❌ NO |
| Back-references/origin links at top | ❌ NO |
| Cross-reference additions | ❌ NO |

### What is "Substantive" vs "Non-Substantive"

**Substantive** (Comment Required):
- Changes to requirements, objectives, success criteria
- Adding/removing phases or tasks
- Altering spec scope or approach
- Significant content changes that affect understanding

**Non-Substantive** (No Comment):
- Adding links/references at the top of issue body (origin links, cross-references)
- STATUS field updates
- Label changes
- Checklist marker updates
- Typo/formatting fixes
- Housekeeping edits that don't change meaning

---

## Issue Closure Rules

### Mandatory Two-Step Operation

1. **First**: `github_add_issue_comment` with detailed closure reason
2. **Then**: Append completion attribution to issue body + `github_issue_write method=update state=closed`

**🚫 NEVER**: Edit issue body to add "CLOSED" — use comments
**🚫 NEVER**: Close without explanation comment

### Closure Comment Format

```
🤖 ❌ **Closed**

## Rejection Reason (if rejected)
<reason with evidence>

## Summary (if completed)
<what was implemented>

## Alternative (if applicable)
<suggestion for rejected proposals>

---
🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>
```

### After Closure: Append Completion Attribution

When closing as completed:
```markdown
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

When closing as rejected:
```markdown
🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>
```

When closing as superseded:
```markdown
🤖 🔄 Superseded by <AgentName> (<ModelID>): <replacement-issue>
```

**⚠️ CRITICAL: ALWAYS APPEND attribution. NEVER replace existing creation attribution.**

### Closure Reasons Requiring Comments

| Closure Reason | Comment Required? |
|----------------|-------------------|
| Completed (PR merged) | ✅ YES |
| Rejected | ✅ YES |
| Superseded | ✅ YES |
| Not planned | ✅ YES |
| Duplicate | ✅ YES |
| Cannot reproduce | ✅ YES |

---

## When NOT to Comment

### 🚫 FORBIDDEN Comments

- "Status Review" comments on correctly tracked issues
- Restating the current STATUS field value
- Confirming issue is waiting correctly
- "Awaiting authorization to implement"
- "Please confirm before I proceed"
- "Ready for approval?"
- Cross-reference link additions (origin/back-reference links)
- Housekeeping edits (typo fixes, formatting)

### ✅ REQUIRED Comments

- Closing an issue (with reason)
- Updating substantive textual content (requirements, objectives, phases)
- Completing implementation task
- Creating PR
- Altering spec structure
- Blocking/unblocking decision

---

## Responding to User Comments (MANDATORY)

**When a user comments on an issue, ALWAYS respond via GitHub comment — NOT just internal analysis.**

Users communicating via GitHub Issues:
- Cannot see your internal analysis
- Are not mind readers
- Expect responses where they asked the question

### Protocol

1. **Read**: `github_issue_read method=get_comments`
2. **Respond**: `github_add_issue_comment` with answer
3. **Be conversational**: Answer directly, ask simply

### Example

```
User: "how do these keys seem?"

BAD: "Awaiting authorization to implement."

GOOD: "The keys look correct. Ready when you are."
```

---

## Prohibitions

### 🚫 NEVER DO

- Edit issue body to add "CLOSED" or "COMPLETED" text
- Rewrite entire issue body to change STATUS
- Close issue without explanation comment
- Post "status review" comments without action
- Use "Awaiting authorization" in comments
- Analyze user comments without posting response
- Create issue AND post separate comment (body is sufficient)
- Proceed to next task without posting progress comment

### ✅ ALWAYS DO

- Post ALL comments with attribution at END (not prefix)
- Use 🤖 emoji FIRST, then status emoji
- Use attribution footer for issue/PR bodies (appended, never replaced)
- Ensure emoji is PLAIN TEXT (NOT inside italic/bold)
- Comment when updating textual content
- Comment when altering spec structure
- Comment when closing issues
- Append attribution for all issue body changes (created, updated, completed, rejected)
- Comment after completing each task
- Post progress comment IMMEDIATELY (not later)
- Respond to user questions via GitHub comment

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `git-workflow` | Post comment when PR created |
| `spec-auditor` | Comment audit findings on issue |

## Guideline References

| Guideline | Content |
|-----------|---------|
| `123-github-ai-identity.md` | Full AI identity requirements |
| `120-github-issue-first.md` | Issue workflow, sub-issues |
| `000-critical-rules.md` | Critical violation enforcement |

## Example Workflows

### Task Completion Comment (Intermediate Task)

```
**Summary:**

Created skill file defining comment format rules, decision tables for when to comment vs edit issue bodies, and example workflows. This establishes clear protocols for AI agents posting to GitHub.

**Outcome:** Agents now have explicit guidance on comment types, timing, and format—reducing inconsistent or missing issue updates.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Task Completion Comment (Final Task)

```
**Summary:**

Updated cross-references in all affected guideline files to point to the new skill. Ensures consistent agent behavior across the codebase.

**Outcome:** All guideline references now correctly point to github-comments skill for comment protocol.

All tasks complete from this specification.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Single-Task Completion

```
**Summary:**

Replaced technical punch-list progress comments with executive summaries focused on stakeholder value. Removed redundant file lists and dialog prompts that violated HALT protocol.

**Outcome:** Progress comments now communicate impact and outcomes rather than changelog details—improving readability for stakeholders reviewing issue history.

All tasks complete from this specification.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Issue Body Update Comment

```
🤖 📝 Updated: Added Phase 2 for guideline updates per discussion in comment #5

---
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5)
```

### Spec Alteration Comment

```
🤖 📝 Spec altered: Added Phase 3 for verification

- Added: Phase 3: Verification (auto-progress)
- Added: Success criteria verification steps

---
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5)
```

### Issue Creation (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
```

### Issue Updates as Combined Bylines List (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by OpenCode (ollama-cloud/glm-5): Issue #462
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added Phase 2
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Fixed typo in success criteria
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Issue Closure Comment

```
**Summary:**
Completed all tasks from this specification:
- ✅ Created github-comments skill
- ✅ Updated three guideline files
- ✅ Removed duplicate content

**Evidence:**
Commit `abc123`: Add github-comments skill directory

All success criteria met.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```