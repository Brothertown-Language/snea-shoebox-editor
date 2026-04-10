---
name: github-comments
description: Use when posting comments to GitHub Issues or PRs. Triggers on: comment, progress update, issue comment, PR comment, post to GitHub, byline, status indicator.
type: technique
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

#### Examples

**Investigation Results Posted for User:**
```
## Analysis: Still an Issue (2026-04-01)

**Root Cause:** The `identifier` constraint in `Validations.scala` uses an overly restrictive regex pattern that rejects valid usernames containing hyphens.

**Location:** `Validations.scala#L16-L25`

**Recommendation:** Update regex to allow hyphens in username patterns.

---
🤖 ✎ on behalf of <DEV_NAME>
```

**Issue Comment Posted for User:**
```
## Status Update

Based on the investigation, the feature is ready for implementation. The API endpoints are designed and the database schema is finalized.

---
🤖 ✎ on behalf of <DEV_NAME>
```

### Issue/PR Body Attribution (Lifecycle Status)

**🚨 CRITICAL: ALWAYS APPEND. NEVER REPLACE.**

| Action | Operation | Byline |
|--------|-----------|--------|
| Create issue | Append | `🤖 ✨ Created by <AgentName> (<ModelID>)` |
| Update content | Append | `🤖 📝 Updated by <AgentName> (<ModelID>)` |
| Complete issue | Append | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| Reject issue | Append | `🤖 ❌ Rejected by <AgentName> (<ModelID>)` |
| Supersede issue | Append | `🤖 🔄 Superseded by <AgentName> (<ModelID>)` |

**Rule:** Byline = WHO did WHAT. Details belong in comment body, not byline. No extra context.

**Example lifecycle (append-only):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by <AgentName> (<ModelID>)
🤖 📝 Updated by <AgentName> (<ModelID>)
🤖 ✅ Completed by <AgentName> (<ModelID>)
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
- **Audit findings reports** — spec-auditor findings are internal agent guidance, not stakeholder communication. Act on findings by revising the spec; don't post the audit report as a comment.

### ✅ REQUIRED Comments

- Closing an issue (with reason)
- Updating substantive textual content (requirements, objectives, phases)
- Completing implementation task
- Creating PR
- Altering spec structure
- Blocking/unblocking decision

### Audit Findings Are NOT Comments

Audit findings from `spec-auditor` are internal agent guidance — equivalent to linter output. They inform the agent what to fix, not what to announce.

**Workflow:**
1. Audit → collect findings
2. Act → revise the spec to address findings
3. Comment → ONLY if the revision is substantive (changes to requirements, phases, success criteria, scope)

| Action | Post Comment? |
|--------|---------------|
| Audit finds issues, agent revises spec substantively | ✅ YES — one revision comment |
| Audit finds issues, agent makes only non-substantive changes (STATUS, typos, cross-refs) | ❌ NO |
| Audit finds zero issues | ❌ NO |
| Agent posts audit findings report as a comment | 🚫 FORBIDDEN |
| Stakeholder explicitly asks for audit results | ✅ YES — direct request override |

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
| `spec-auditor` | Findings are internal guidance — act on them, don't post; comment only for substantive revisions |

## Example Workflows

### Task Completion Comment (Intermediate Task)

```
**Summary:**

Created skill file defining comment format rules, decision tables for when to comment vs edit issue bodies, and example workflows. This establishes clear protocols for AI agents posting to GitHub.

**Outcome:** Agents now have explicit guidance on comment types, timing, and format—reducing inconsistent or missing issue updates.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Task Completion Comment (Final Task)

```
**Summary:**

Updated cross-references in all affected guideline files to point to the new skill. Ensures consistent agent behavior across the codebase.

**Outcome:** All guideline references now correctly point to github-comments skill for comment protocol.

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Single-Task Completion

```
**Summary:**

Replaced technical punch-list progress comments with executive summaries focused on stakeholder value. Removed redundant file lists and dialog prompts that violated HALT protocol.

**Outcome:** Progress comments now communicate impact and outcomes rather than changelog details—improving readability for stakeholders reviewing issue history.

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Issue Body Update Comment

```
🤖 📝 Updated for guideline updates per discussion in comment #5

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

### Spec Alteration Comment

```
🤖 📝 Spec altered: Added Phase 3 for verification

- Added: Phase 3: Verification (auto-progress)
- Added: Success criteria verification steps

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

### Issue Creation (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by <AgentName> (<ModelID>)
```

### Issue Updates as Combined Bylines List (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 ✨ Created by <AgentName> (<ModelID>)
🤖 📝 Updated by <AgentName> (<ModelID>)
🤖 📝 Updated by <AgentName> (<ModelID>)
🤖 ✅ Completed by <AgentName> (<ModelID>)
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
🤖 ✅ Completed by <AgentName> (<ModelID>)
```# Issue Comment Protocol

## NEVER Use Issue Comments as Dialog Prompts

GitHub issue comments are **general comments**, NOT interactive dialogs.

### Problem Statement

Agents are adding "awaiting authorization" prompts like:

> The 5 fields can be added when you're ready to proceed.
> 
> Awaiting authorization to implement.

This is incorrect because:
- Developers cannot read agent internal reasoning
- Issue comments are public records, not chat interfaces
- Dialog prompts create noise and confusion
- The HALT protocol already handles authorization flow

### 🚫 PROHIBITED Patterns

- "Awaiting authorization to implement."
- "Let me know when you're ready to proceed."
- "Please confirm before I start."
- "Ready when you are."
- Any text that expects an inline response

### ✅ CORRECT Behavior

1. **SILENTLY HALT** after completing a task or reaching a decision point
2. **Wait for explicit user instruction** via new comment
3. **Respond to user comments** by addressing the actual question/request

### Rationale

- Developers cannot read agent internal reasoning
- Issue comments are public records, not chat interfaces
- Dialog prompts create noise and confusion
- The HALT protocol already handles authorization flow

## Relationship to Other Guidelines

| Guideline | Relationship |
|-----------|--------------|
| `000-critical-rules.md` → "Ignoring Issue Comments" | Respond to user questions via comment |
| `000-critical-rules.md` → "Progress Comments" | Document actual progress, not dialogs |
| `03-ai-identity.md` → "Status Review Comments" | Don't post status without action |
| This guideline | Don't prompt for authorization via comments |

The HALT protocol (see `010-approval-gate.md`) is the correct mechanism for authorization flow:
- Complete task → report completion → **STOP and wait**
- Do NOT post "awaiting authorization" comments

## When to Comment vs. HALT

| Situation | Action |
|-----------|--------|
| Completed a task | Post progress comment, then HALT |
| User asked a question | Respond via comment addressing the question |
| Reached decision point | HALT silently, wait for user |
| Changed files | Comment documenting the change |
| Need clarification | Post question in comment, then HALT |

## Anti-Patterns to Avoid

### ❌ WRONG: Dialog Prompt After Completion

```
AI: OpenCode ollama-cloud/glm-5 🤖 Task complete: Updated the validation logic.
Ready to proceed with the next task? Awaiting authorization.
```

**Problem**: Implicit prompt expecting response. Developers can't see your reasoning.

### ✅ RIGHT: Clean Completion

```
AI: OpenCode ollama-cloud/glm-5 ✅ Task complete: Updated the validation logic.

**Summary:**

Refactored the input validation module to handle edge cases in MeSH term lookups and added error context propagation. This prevents validation failures when terms contain special characters.

**Outcome:** MeSH term validation now handles edge cases gracefully with clear error messages.
```

**Correct**: Documents progress with executive summary focusing on stakeholder value. No file lists. No dialog prompt.

### ❌ WRONG: Prompting for Confirmation

```
AI: OpenCode ollama-cloud/glm-5 🤖 Analysis complete. Should I proceed with implementation?
```

**Problem**: Asking permission via comment instead of waiting for explicit instruction.

### ✅ RIGHT: Present Findings and HALT

```
AI: OpenCode ollama-cloud/glm-5 🔍 Analysis complete: Found 3 issues in validation module.
- Issue 1: Missing null check in `validate_input()`
- Issue 2: Duplicate validation in `process_data()`
- Issue 3: Unreachable code in `handle_error()`
```

**Correct**: Presents findings, HALTs. Developer will authorize when ready.

## After Spec Creation/Update Comments

When posting spec updates:

### ✅ CORRECT

```markdown
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added .env and local file support
```

### 🚫 FORBIDDEN

```markdown
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Added .env and local file support

**Awaiting authorization to begin Phase 1.** Say "approved" or "go" when ready.
```

The second example is FORBIDDEN because:
- It prompts for authorization
- "Awaiting authorization" is an offensive phrase
- "Say 'approved' or 'go' when ready" is dialog prompting

**After spec creation/update: SILENTLY HALT. Do NOT add any "awaiting" or "ready when you are" text.**

## Summary

**Issue comments are for:**
- Documenting progress
- Answering questions
- Explaining decisions
- Providing evidence

**Issue comments are NOT for:**
- Prompting for authorization
- Starting dialogs
- Asking "ready to proceed?"
- Cross-reference updates (origin links, back-references)

**Use HALT for authorization flow.**

## Non-Substantive Updates (No Comment Required)

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

### Examples

**Non-Substantive (No Comment Needed):**
```markdown
> **Origin:** Investigated in https://github.com/<owner>/<repo>/issues/100
> **Investigation Result:** api-agent cannot be used
```

This is just a reference link at the top of the issue body. No comment explaining "added cross-reference" is needed.

**Substantive (Comment Required):**
- Adding a new phase to the spec
- Changing the requirements section
- Modifying success criteria
- Altering the implementation approach

These require a comment explaining what changed and why.
---
