# Issue Comment Protocol

## Three-Tier Principle (MANDATORY)

**GitHub Issue comments are for substantive content, NOT for state tracking or progress notifications.**

**State tracking uses LABELS. Progress notifications go to CHAT.**

### Tier 1: NEVER Acceptable for GitHub Comments

These are CRITICAL VIOLATIONS:

- State tracking (STATUS updates, progress blocks)
- Progress notifications (implementation progress, review-prep, PR creation)
- Routine updates (file changes, test results, lint)

**Use labels for state tracking:** `needs-approval`, `in-progress`, `blocked`, or custom labels.

### Tier 2: ALWAYS Acceptable for GitHub Comments

- Answering questions asked via GitHub comments
- Executive summary when issue closes (historical record for future maintainers)

### Tier 3: AI Agent Intelligence Determines

AI agent MAY post to GitHub when substantive content warrants recording:

- Bug identification that needs recording
- Design decisions needing context for future maintainers
- Architectural warnings about long-term implications
- Edge case documentation for future reference
- Security observations requiring permanent record
- Data integrity concerns
- Any substantive information for future readers

**When in doubt:** Ask "Would a future maintainer need this context?" If yes → post to GitHub. If no → chat only.

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
| Completed a task | Provide executive summary in CHAT ONLY, then HALT |
| User asked a question | Respond via comment addressing the question |
| Reached decision point | HALT silently, wait for user |
| Changed files | Provide executive summary in CHAT ONLY, then HALT |
| Need clarification | Post question in comment, then HALT |
| Issue closed AFTER MERGE | Post closure summary to GitHub (historical record) |

## Anti-Patterns to Avoid

### ❌ WRONG: Dialog Prompt After Completion

```
AI: <AgentName> (<ModelID>) 🤖 Task complete: Updated the validation logic.
Ready to proceed with the next task? Awaiting authorization.
```

**Problem**: Implicit prompt expecting response. Developers can't see your reasoning.

### ✅ RIGHT: Clean Completion

```
AI: <AgentName> (<ModelID>) ✅ Task complete: Updated the validation logic.

**Summary:**

Refactored the input validation module to handle edge cases in MeSH term lookups and added error context propagation. This prevents validation failures when terms contain special characters.

**Outcome:** MeSH term validation now handles edge cases gracefully with clear error messages.
```

**Correct**: Documents progress with executive summary focusing on stakeholder value. No file lists. No dialog prompt.

### ❌ WRONG: Prompting for Confirmation

```
AI: <AgentName> (<ModelID>) 🤖 Analysis complete. Should I proceed with implementation?
```

**Problem**: Asking permission via comment instead of waiting for explicit instruction.

### ✅ RIGHT: Present Findings and HALT

```
AI: <AgentName> (<ModelID>) 🔍 Analysis complete: Found 3 issues in validation module.
- Issue 1: Missing null check in `validate_input()`
- Issue 2: Duplicate validation in `process_data()`
- Issue 3: Unreachable code in `handle_error()`
```

**Correct**: Presents findings, HALTs. Developer will authorize when ready.

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

### Decision Table

| Update Type | Comment? | Example |
|------------|----------|---------|
| Adding phase to spec | YES | "Added Phase 2 with API endpoints" |
| Changing requirements | YES | "Modified success criteria for performance" |
| STATUS marker update | NO | `STATUS: 1.1` → `STATUS: 1.2` |
| Adding origin link | NO | `> **Origin:** Issue #123` |
| Typo fix in spec | NO | Fixed misspelling in title |
| Label change | NO | Added `needs-approval` label |

## Context-Based Summaries for Issue Comments

**GitHub Issue comments are for FUTURE MAINTAINERS, not immediate developers.**

**Purpose:** Provide historical context for future readers

**Content:** WHAT changed and WHY (technical context)

**NO URLs in GitHub Issue comments.**

### Context-Based Summary Example (Substantive Update)

```markdown
Added Phase 2 to spec. Phase 2 implements the API layer for the approval workflow.

**Changes:**
- Added Phase 2 implementation steps
- Defined API endpoints: approve(), reject(), getStatus()
- Specified error handling for invalid states

---
🤖 📝 Updated by <AgentName> (<ModelID>)
```

**Key Characteristics:**
- Explains WHAT changed (content details)
- Explains WHY (purpose/rationale)
- Provides technical context for future maintainers
- NO URL (URLs belong in Chat, not GitHub Issues)

### When to Use Context-Based Summaries

| Context | Location | Summary Type | Contains URL? |
|---------|----------|--------------|---------------|
| Issue update (substantive) | GitHub Issue | Context-based | NO |
| Issue creation | GitHub Issue | Minimal attribution only | NO |
| Issue closure | GitHub Issue | Closure summary | NO |
| Implementation complete | Chat | Executive summary | YES |

## URL Placement in Executive Summaries (MANDATORY)

**URLs MUST appear LAST in all executive summaries and progress comments.**

### Rule

When a comment includes a URL (issue link, PR link, code compare link, etc.), the URL MUST be the final line of the comment.

### Format

```markdown
**Summary:**

<Summary content>

**Outcome:** <What changed>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/dev...<branch>
```

### Why URL Last

- URLs are typically long and may wrap across lines
- Placing URLs last allows developers to quickly scan summary content first
- Easy visual anchor: "look for the URL at the end"
- Consistent pattern across all AI-generated summaries

### Multiple URLs

If multiple URLs are relevant (e.g., both issue and PR):

- Place the primary URL (most actionable) last
- Secondary URLs can appear in body with context

**Example:**

```markdown
**Summary:**

Skills imported from external repository. Parent issue #149 tracks overall progress.

**Outcome:** 5 new skills added to repository.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/dev...<branch>
```

### No URLs

If no URLs are relevant (pure summary, no links):

- Executive summary ends with the agent byline
- No URL placeholder needed

**Applicable to:**

- Executive summaries in progress comments
- Completion comments on issues
- Review-prep completion comments
- PR creation confirmation comments
- **New issue creation comments** (URL after summary, not before)

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
