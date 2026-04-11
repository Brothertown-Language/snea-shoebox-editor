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

**ALL comments MUST end with ONE byline that combines identity and status.**

**Format:**
```
<response content>

---
🤖 <AgentName> (<ModelID>) <status>
```

**Components (supplied dynamically at runtime):**
- `<AgentName>`: AI's actual name (e.g., `OpenCode Desktop`, `OpenCode`)
- `<ModelID>`: Model identifier with provider (e.g., `<ModelID>`)
- `<status>`: Single emoji for the outcome

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity.**

**Rule:** Byline = WHO + outcome. Identity first, status last. No extra context.

### Status Icon Guide

| Status | Icon | Example |
|--------|------|---------|
| Task Complete | ✅ | `🤖 OpenCode (ollama-cloud/glm-5.1) ✅` |
| In Progress | ↻ | `🤖 OpenCode (ollama-cloud/glm-5.1) ↻` |
| Created | ✨ | `🤖 OpenCode (ollama-cloud/glm-5.1) ✨` |
| Updated | 📝 | `🤖 OpenCode (ollama-cloud/glm-5.1) 📝` |
| Copy Editor | ✎ | `🤖 OpenCode (ollama-cloud/glm-5.1) ✎ on behalf of <UserName>` |
| Rejected | ❌ | `🤖 OpenCode (ollama-cloud/glm-5.1) ❌` |
| Superseded | 🔄 | `🤖 OpenCode (ollama-cloud/glm-5.1) 🔄` |
| Blocking | ⚠️ | `🤖 OpenCode (ollama-cloud/glm-5.1) ⚠️` |
| Analysis | 🔍 | `🤖 OpenCode (ollama-cloud/glm-5.1) 🔍` |
| Decision | 📋 | `🤖 OpenCode (ollama-cloud/glm-5.1) 📋` |

**Rule:** Byline = WHO + outcome. Identity first, status last. No extra context.

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
🤖 <AgentName> (<ModelID>) ✎ on behalf of <UserName>
```

**Components:**
- `✎`: Pencil emoji indicates editing/posting role (not authorship)
- `on behalf of <UserName>`: The user who requested/owns the content

**Rule:** Byline = WHO + outcome. Identity first, status last.

#### Examples

**Investigation Results Posted for User:**
```
## Analysis: Still an Issue (2026-04-01)

**Root Cause:** The `identifier` constraint in `Validations.scala` uses an overly restrictive regex pattern that rejects valid usernames containing hyphens.

**Location:** `Validations.scala#L16-L25`

**Recommendation:** Update regex to allow hyphens in username patterns.

---
🤖 OpenCode (ollama-cloud/glm-5.1) ✎ on behalf of <DEV_NAME>
```

**Issue Comment Posted for User:**
```
## Status Update

Based on the investigation, the feature is ready for implementation. The API endpoints are designed and the database schema is finalized.

---
🤖 OpenCode (ollama-cloud/glm-5.1) ✎ on behalf of <DEV_NAME>
```

### Issue/PR Body Attribution (Lifecycle Status)

**🚨 CRITICAL: ALWAYS APPEND. NEVER REPLACE.**

| Action | Operation | Byline |
|--------|-----------|--------|
| Create issue | Append | `🤖 <AgentName> (<ModelID>) ✨` |
| Update content | Append | `🤖 <AgentName> (<ModelID>) 📝` |
| Complete issue | Append | `🤖 <AgentName> (<ModelID>) ✅` |
| Reject issue | Append | `🤖 <AgentName> (<ModelID>) ❌` |
| Supersede issue | Append | `🤖 <AgentName> (<ModelID>) 🔄` |

**Rule:** Byline = WHO + outcome. Identity first, status last. No extra context.

**Example lifecycle (append-only):**
```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 OpenCode (ollama-cloud/glm-5.1) ✨
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
🤖 OpenCode (ollama-cloud/glm-5.1) ✅
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
| Complete implementation task | ❌ NO | Progress goes to chat only |
| Create PR | ✅ YES | Link to issue for traceability |
| Close issue | ✅ YES | Provide closing summary |
| Alter spec (add/remove phases, steps) | ✅ YES | Document spec changes |
| Report blocker | ✅ YES | Others need to know work is stuck |
| Report bug discovered during implementation | ✅ YES | Affects scope or approach |
| Respond to user question | ✅ YES | Must respond where asked |
| Review status without action | ❌ NO | No value added |
| Label changes | ❌ NO | GitHub auto-tracks |
| Checklist completion (`☐` → `☑`) | ❌ NO | Status tracking |

---

## Progress Reports (MANDATORY)

**Every implementation step MUST be documented with a progress executive summary in chat.**

### When to Report

- After completing EACH task in multi-task implementation
- After ANY file modification
- When creating PR
- NEVER wait until all tasks complete — report after EACH task

### Channel Decision (CRITICAL)

**Progress executive summaries go to chat ONLY, not GitHub Issue comments.**

| Channel | Purpose | Content |
|---------|---------|---------|
| **Chat** | Operational progress (immediate) | Full executive summary (summary, outcome) |
| **GitHub Issue** | State changes (permanent record) | Only: spec revision, PR created, blocked, bug, user response, closure |

**Why:** Chat serves the active developer. GitHub preserves long-term history. Implementation progress is ephemeral (session-scoped); state changes are permanent.

**✅ DO:** Post executive summary to chat
**🚫 NEVER:** Post implementation progress to GitHub Issue comments
**🚫 NEVER:** Skip chat report

### Chat Output Rule (CRITICAL)

**Chat output order (mandatory):**
1. Executive summary (what happened, outcome)
2. URL (if one exists)
3. AI byline LAST — `🤖 <AgentName> (<ModelID>) <status>`

Nothing after the byline. The byline signals output is complete.

**Byline format:** `🤖 <AgentName> (<ModelID>) <status>`

Identity first, status last. Reads naturally: "AI agent X completed ✅"

| Status | Icon | Example |
|--------|------|---------|
| Completed | ✅ | `🤖 OpenCode (ollama-cloud/glm-5.1) ✅` |
| Created | ✨ | `🤖 OpenCode (ollama-cloud/glm-5.1) ✨` |
| Updated | 📝 | `🤖 OpenCode (ollama-cloud/glm-5.1) 📝` |
| Blocked | ⚠️ | `🤖 OpenCode (ollama-cloud/glm-5.1) ⚠️` |
| Rejected | ❌ | `🤖 OpenCode (ollama-cloud/glm-5.1) ❌` |
| Superseded | 🔄 | `🤖 OpenCode (ollama-cloud/glm-5.1) 🔄` |
| Analysis | 🔍 | `🤖 OpenCode (ollama-cloud/glm-5.1) 🔍` |

### ✅ REQUIRED Format: Executive Summary

**For intermediate task (multi-task spec):**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>
```

**For final task or single-task spec:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value of the change.>

**Outcome:** <What changed for stakeholders / users / system behavior>

All tasks complete from this specification.
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
2. ✅ Report progress in chat IMMEDIATELY
3. ✅ ONLY THEN: Move to next task or report completion

**🚫 WRONG:** Complete task → Move to next → Report later
**✅ RIGHT:** Complete task → Report in chat → Then move to next

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
📝 Updated: <reason>

---
🤖 <AgentName> (<ModelID>) 📝
```

### Spec Alteration Format

```
📝 Spec altered: <summary>

- Changed: <what changed>
- Added: <what added>
- Removed: <what removed>

---
🤖 <AgentName> (<ModelID>) 📝
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
❌ **Closed**

## Rejection Reason (if rejected)
<reason with evidence>

## Summary (if completed)
<what was implemented>

## Alternative (if applicable)
<suggestion for rejected proposals>

---
🤖 <AgentName> (<ModelID>) ❌
```

### After Closure: Append Completion Attribution

When closing as completed:
```markdown
🤖 <AgentName> (<ModelID>) ✅
```

When closing as rejected:
```markdown
🤖 <AgentName> (<ModelID>) ❌
```

When closing as superseded:
```markdown
🤖 <AgentName> (<ModelID>) 🔄
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
- **Implementation progress comments** — progress reports go to chat only
- **Audit findings reports** — spec-auditor findings are internal agent guidance, not stakeholder communication. Act on findings by revising the spec; don't post the audit report as a comment.

### ✅ REQUIRED Comments

- Closing an issue (with reason)
- Updating substantive textual content (requirements, objectives, phases)
- Creating PR
- Altering spec structure
- Blocking/unblocking decision
- Responding to user questions

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
- Post implementation progress to GitHub Issue comments (chat only)
- Proceed to next task without reporting progress in chat

### ✅ ALWAYS DO

- Post ALL comments with attribution at END (not prefix)
- Use 🤖 emoji FIRST, then agent identity, then status icon
- Use attribution footer for issue/PR bodies (appended, never replaced)
- Ensure emoji is PLAIN TEXT (NOT inside italic/bold)
- Comment when updating textual content
- Comment when altering spec structure
- Comment when closing issues
- Append attribution for all issue body changes (created, updated, completed, rejected)
- Report progress in chat after completing each task
- Report progress IMMEDIATELY (not later)
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
```

### Task Completion Comment (Final Task)

```
**Summary:**

Updated cross-references in all affected guideline files to point to the new skill. Ensures consistent agent behavior across the codebase.

**Outcome:** All guideline references now correctly point to github-comments skill for comment protocol.

All tasks complete from this specification.
```

### Single-Task Completion

```
**Summary:**

Replaced technical punch-list progress comments with executive summaries focused on stakeholder value. Removed redundant file lists and dialog prompts that violated HALT protocol.

**Outcome:** Progress comments now communicate impact and outcomes rather than changelog details—improving readability for stakeholders reviewing issue history.

All tasks complete from this specification.
```

### Issue Body Update Comment

```
📝 Updated for guideline updates per discussion in comment #5

---
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
```

### Spec Alteration Comment

```
📝 Spec altered: Added Phase 3 for verification

- Added: Phase 3: Verification (auto-progress)
- Added: Success criteria verification steps

---
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
```

### Issue Creation (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 OpenCode (ollama-cloud/glm-5.1) ✨
```

### Issue Updates as Combined Bylines List (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 OpenCode (ollama-cloud/glm-5.1) ✨
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
🤖 OpenCode (ollama-cloud/glm-5.1) ✅
```

## Issue Comment Protocol

### Spec Alteration Comment

```
📝 Spec altered: Added Phase 3 for verification

- Added: Phase 3: Verification (auto-progress)
- Added: Success criteria verification steps

---
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
```

### Issue Creation (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 OpenCode (ollama-cloud/glm-5.1) ✨
```

### Issue Updates as Combined Bylines List (Body)

```markdown
[Issue body content]

---

> **Approval Tracking**: Approvals tracked via comments.

🤖 OpenCode (ollama-cloud/glm-5.1) ✨
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
🤖 OpenCode (ollama-cloud/glm-5.1) ✅
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
🤖 OpenCode (ollama-cloud/glm-5.1) ✅
```

# Issue Comment Protocol

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
Updated the validation logic to handle edge cases in MeSH term lookups and added error context propagation. This prevents validation failures when terms contain special characters.

🤖 OpenCode (ollama-cloud/glm-5.1) ✅
```

**Correct**: Documents progress with executive summary focusing on stakeholder value. No file lists. No dialog prompt.

### ❌ WRONG: Prompting for Confirmation

```
AI: OpenCode ollama-cloud/glm-5 🤖 Analysis complete. Should I proceed with implementation?
```

**Problem**: Asking permission via comment instead of waiting for explicit instruction.

### ✅ RIGHT: Present Findings and HALT

```
Found 3 issues in validation module:
- Issue 1: Missing null check in `validate_input()`
- Issue 2: Duplicate validation in `process_data()`
- Issue 3: Unreachable code in `handle_error()`

🤖 OpenCode (ollama-cloud/glm-5.1) 🔍
```

## After Spec Creation/Update Comments

When posting spec updates:

### ✅ CORRECT

```markdown
📝 Updated: Added .env and local file support

---
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
```

### 🚫 FORBIDDEN

```markdown
📝 Updated: Added .env and local file support

**Awaiting authorization to begin Phase 1.** Say "approved" or "go" when ready.

---
🤖 OpenCode (ollama-cloud/glm-5.1) 📝
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
