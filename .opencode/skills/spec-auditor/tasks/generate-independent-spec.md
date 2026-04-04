# Task: generate-independent-spec

Generate a **complete, implementable spec draft** from scratch BEFORE viewing the live spec.

## Purpose

Prevent the existing live spec from influencing/biasing the auditor's independent analysis. Create a REAL spec (not a checklist) that could be implemented from scratch.

## ⚠️ CRITICAL: Draft Must Be a REAL Spec

**If you're writing "A good spec should include...", you're doing it WRONG.**

The draft is an IMPLEMENTABLE SPEC, not advice about specs.

### WRONG (What It Did Before)

```markdown
## What a Good Spec Should Include

A good spec for a search feature should include:
1. Problem Statement
2. Proposed Solution
3. Affected Files
```

This is **meta-commentary** — it tells you ABOUT specs, doesn't CREATE a spec.

### CORRECT (What It Should Be)

```markdown
# Independent Draft: Add Headword and Gloss Search Modes

## Problem

Users need focused search modes for dictionary workflow. Current Lexeme mode searches too many fields, returning noise. Linguists need precise targeting of headword/variants and primary gloss only.

## Proposed Solution

Add two search modes:
- **Headword**: Search `\lx` and primary `\va` only
- **Gloss**: Search primary `\ge` only (exclude subentry/cross-ref glosses)

## Affected Files

| File | Anchor | Change |
|------|--------|--------|
| `src/services/linguistic_service.py` | `search_records()` | Add Headword/Gloss cases |
| `src/services/upload_service.py` | `SearchEntry` creation | Add primary `\ge` extraction |

## Success Criteria

- Search "wampuw" in Headword mode → finds record via `\lx`
- Search "round" in Gloss mode → finds record via primary `\ge`

## Edge Cases

- Records with no `\ge` field → no `entry_type='ge'` SearchEntry created
- Records with no `\va` field → Headword search queries only `\lx`

## Dependencies

- SearchEntry model (internal)
- MDF parser (internal)

## Risk Assessment

- Migration corrupts existing data → mitigate with rollback migration
- UI radio button behavior unexpected → match existing toggle behavior
```

**This is an IMPLEMENTABLE spec that developers could work from.**

---

## Workflow

**Step 1: Generate Independent Draft**

Write a complete spec draft to `./tmp/tmp-spec-{issue}-draft.md` based ONLY on:
- The issue number (for context)
- The issue title
- General knowledge of the project structure
- Common patterns for this issue type

**Step 2: DO NOT Load Live Spec**

At this stage, you MUST NOT:
- Read the GitHub Issue body
- Read any spec content
- View any related documentation
- Check previous audit results

**Step 3: Real Spec Content**

The draft must include:

| Section | Purpose | Content |
|---------|---------|---------|
| **Problem Statement** | What's broken and why | Specific to this issue, with context |
| **Proposed Solution** | Technical approach | Architecture, components, flow |
| **Affected Files** | Where changes happen | With function/section anchors |
| **Success Criteria** | How to verify | Testable conditions |
| **Edge Cases** | What could go wrong | Specific to this implementation |
| **Dependencies** | What it depends on | Internal/external dependencies |
| **Risk Assessment** | What could fail | Mitigation strategies |

---

## Output Template

Create `./tmp/tmp-spec-{issue}-draft.md` with:

```markdown
# Independent Draft: {Issue Title}

Issue: #{issue_number}
Generated: {timestamp}

## Problem

{Specific problem this issue addresses. Include context: who is affected, why it matters now.}

## Proposed Solution

{Technical approach with architecture decisions. Include WHY this approach.}

## Affected Files

| File | Anchor | Change |
|------|--------|--------|
| {path} | {function/section} | {what changes} |

## Success Criteria

- {testable condition 1}
- {testable condition 2}
- {testable condition 3}

## Edge Cases

- {edge case 1}: {how to handle}
- {edge case 2}: {how to handle}

## Dependencies

- {dependency 1}: {why needed}
- {dependency 2}: {why needed}

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {what could go wrong} | {Low/Medium/High} | {Low/Medium/High} | {how to handle} |

## Decision Rationale

**Why this approach:** {explanation}

**Alternatives considered:**
1. {alternative 1} — Rejected because {reason}
2. {alternative 2} — Rejected because {reason}
```

---

## Constraints

- Use `./tmp/` directory for temporary draft (per `070-environment.md`)
- Draft MUST be a real spec (implementable), NOT meta-commentary
- Draft MUST include specific files, functions, anchors
- Draft MUST include decision rationale
- DO NOT view the live spec at this stage
- Cleanup required after audit completes

## Return Value

- Path to the generated draft file
- Confirmation that draft was created without viewing live spec
- Readiness to proceed to `audit` task

## Example: Wrong vs Correct

### WRONG (Meta-Commentary — What to AVOID)

```markdown
## What a Good Spec Should Include

A good spec for this type of issue should include:
1. A clear problem statement
2. A proposed solution
3. Affected files

## Expected Structure

The spec should have:
- STATUS header
- CREATED date
- Phases and steps

## Common Pitfalls

For this spec type, watch out for:
- Missing edge cases
- Unclear success criteria
```

### CORRECT (Real Spec — What to CREATE)

```markdown
# Independent Draft: Fix spec-auditor generate-independent-spec Task

## Problem

The `generate-independent-spec` task was generating meta-commentary instead of implementable spec drafts. LLM agents received useless checklists instead of real specs they could implement from.

## Proposed Solution

Complete rewrite:
1. Rename task from `create-draft` to `generate-independent-spec`
2. Replace template with real spec structure
3. Enforce implementable draft requirement with WRONG vs CORRECT examples

## Affected Files

| File | Anchor | Change |
|------|--------|--------|
| `.opencode/skills/spec-auditor/tasks/generate-independent-spec.md` | Entire file | Replace content with real spec template |
| `.opencode/skills/spec-auditor/SKILL.md` | Task table | Update task name and description |

## Success Criteria

- Running `generate-independent-spec` produces real spec draft
- Draft contains problem, solution, files, criteria
- Draft is implementable without viewing live spec

## Edge Cases

- No edge cases for this task rewrite

## Dependencies

- None (internal skill refactoring)

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Template misunderstood | Low | Medium | Add explicit WRONG vs CORRECT examples |

## Decision Rationale

**Why complete rewrite:** The original design was fundamentally flawed from conception — it generated checklists instead of specs. Minor fixes would perpetuate the wrong approach.
```