---
name: github-comments
description: GitHub comment format and protocol for AI agents. Defines AI identity prefixes, comment types, progress comments, closure summaries, and when to comment vs edit issue bodies.
license: MIT
compatibility: opencode
---

# GitHub Comment Protocol

## Role

You are a GitHub Comment Protocol enforcer. Your focus is ensuring all comments on issues and PRs follow the correct format, are posted at the right time, and preserve history by preferring comments over issue body edits.

## Comment Format: Branded AI Identity

### ✅ ALWAYS DO (MANDATORY)

ALL comments on issues and PRs MUST end with AI byline.

**ALL bylines AND issue body signatures MUST include "on behalf of <HumanName>".**

**Bylines are ALWAYS at the END of content, wrapped in italics.**

**Format:**
```
*[<AgentIcon> AI: <AgentBrand>] on behalf of <HumanName> <ContextEmoji> <TypeText>*
```

**For PROGRESS COMMENTS (task completion, implementation updates):**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

*[🤖 AI: OpenCode/glm-5] on behalf of <HumanName> ✅ Task Complete: <task-name>*
```

**For GENERAL COMMENTS (responses, clarifications):**
```
<response content>

*[🤖 AI: OpenCode/glm-5] on behalf of <HumanName> 🤖*
```

**Components (supplied dynamically at runtime):**
- `<AgentIcon>`: Agent iconography (🤖 for OpenCode, 🟣 for Claude, 💙 for Copilot)
- `<AgentBrand>`: Agent brand identifier (e.g., `OpenCode/glm-5`, `Claude/sonnet-4`)
- `<HumanName>`: From `git config user.name` (fallback to `$USER`)

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity.**

### Agent Icon Registry

| Agent | Icon | Brand |
|-------|------|-------|
| OpenCode | 🤖 | `OpenCode/<model>` |
| Claude | 🟣 | `Claude/<model>` |
| Copilot | 💙 | `Copilot/<model>` |
| Generic | 🤖 | `AI/<model>` |

### Context Emoji Reference

| Emoji | Type Text | Use Case |
|-------|-----------|----------|
| ✅ | `Task Complete: <task>` | Progress comments |
| 🤖 | *(none)* | General responses |
| 📝 | `Updated: <reason>` | Body updates |
| 📝 | `Spec altered: <summary>` | Spec alterations |
| ❌ | `Closed - <reason>` | Issue closures |
| 🔍 | `Analysis` | Investigation findings |
| ⚠️ | `Warning` | Cautions |
| ✨ | `Created` | Issue/PR creation |
| 🚀 | `Launched` | PR creation |

### Signature for Issue/PR Bodies (NOT comments)

```markdown
<issue content>

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> ✨ Created*
```

Place at END of issue bodies and PR descriptions, preceded by blank line.

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

### ✅ REQUIRED Format: Executive Summary (POST TO GITHUB, NOT CHAT)

**For intermediate task (multi-task spec):**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> ✅ Task Complete: <task-name>*
```

**For final task or single-task spec:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>

All tasks complete from this specification.

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> ✅ Task Complete: <task-name>*
```

### Executive Summary Requirements

The summary MUST answer:
1. **What changed?** — The actual implementation/fix/enhancement
2. **Why it matters** — Impact on stakeholders (users, developers, system)
3. **Result** — Improved behavior, new capability, fixed issue

### 🚫 FORBIDDEN in Progress Comments

- **File lists** — Redundant (visible in git commits)
- **"Next" field** — Dialog prompt (violates `125-github-issue-comments.md`)
- **Punch-list format** — Use executive summary paragraphs
- **"Awaiting authorization"** — Use HALT protocol, not comments
- **"Waiting for..."** — Use HALT protocol, not comments
- **"Ready for review"** — Use HALT protocol, not comments
- **"Ready for approval"** — Use HALT protocol, not comments
- **"Please confirm..."** — Use HALT protocol, not comments
- **"Let me know when..."** — Use HALT protocol, not comments
- **Technical changelog** — Focus on impact, not file-by-file changes
- **Just "I did X"** — Explain WHY it matters
- **Any procedural status** — "HALT", "Waiting", "Ready" — Use HALT protocol silently

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

### Two-Step Operation (MANDATORY)

When updating textual content in an issue body:

1. **First**: `github_issue_write method=update` (update body)
2. **IMMEDIATELY after**: `github_add_issue_comment` (explain change)

**⚠️ CRITICAL**: Both calls in same function_calls block. Never update without commenting.

### Comment Format for Body Updates

```
<summary of changes>

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> 📝 Updated: <reason>*
```

### Spec Alteration Format

```
- Changed: <what changed>
- Added: <what added>
- Removed: <what removed>

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> 📝 Spec altered: <summary>*
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

---

## Issue Closure Rules

### Mandatory Two-Step Operation

1. **First**: `github_add_issue_comment` with detailed closure reason
2. **Then**: `github_issue_write method=update state=closed` (state change ONLY)

**🚫 NEVER**: Edit issue body to add "CLOSED" — use comments
**🚫 NEVER**: Close without explanation comment

### Closure Comment Format

```
## Summary
Completed all tasks from this specification:
- ✅ <task 1>
- ✅ <task 2>

## Evidence
Commit `<sha>`: <commit message>

All success criteria met.

*[🤖 AI: <AgentBrand>] on behalf of <HumanName> ❌ Closed - Implemented*
```

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

### ✅ REQUIRED Comments

- Closing an issue (with reason)
- Updating textual content
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

- Post bylines at END of ALL comments with branded AI marker
- Use signature footer for issue/PR bodies at END
- Comment when updating textual content
- Comment when altering spec structure
- Comment when closing issues
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

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad ✅ Task Complete: Create github-comments SKILL.md*
```

### Task Completion Comment (Final Task)

```
**Summary:**

Updated cross-references in all affected guideline files to point to the new skill. Ensures consistent agent behavior across the codebase.

**Outcome:** All guideline references now correctly point to github-comments skill for comment protocol.

All tasks complete from this specification.

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad ✅ Task Complete: Update cross-references*
```

### Single-Task Completion

```
**Summary:**

Replaced technical punch-list progress comments with executive summaries focused on stakeholder value. Removed redundant file lists and dialog prompts that violated HALT protocol.

**Outcome:** Progress comments now communicate impact and outcomes rather than changelog details—improving readability for stakeholders reviewing issue history.

All tasks complete from this specification.

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad ✅ Task Complete: Implement executive summary format*
```

### Issue Body Update Comment

```
Added Phase 2 for guideline updates per discussion in comment #5

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad 📝 Updated: Added Phase 2 for guideline updates*
```

### Spec Alteration Comment

```
- Added: Phase 3: Verification (auto-progress)
- Added: Success criteria verification steps

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad 📝 Spec altered: Added Phase 3 for verification*
```

### Issue Closure Comment

```
## Summary
Completed all tasks from this specification:
- ✅ Created github-comments skill
- ✅ Updated three guideline files
- ✅ Removed duplicate content

## Evidence
Commit `abc123`: Add github-comments skill directory

All success criteria met.

*[🤖 AI: OpenCode/glm-5] on behalf of Michael Conrad ❌ Closed - Implemented*
```