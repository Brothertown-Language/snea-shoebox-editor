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
> **Origin:** Investigated in https://github.com/NewsRx/newsrx-genai-python/issues/100
> **Investigation Result:** api-agent cannot be used
```

This is just a reference link at the top of the issue body. No comment explaining "added cross-reference" is needed.

**Substantive (Comment Required):**
- Adding a new phase to the spec
- Changing the requirements section
- Modifying success criteria
- Altering the implementation approach

These require a comment explaining what changed and why.