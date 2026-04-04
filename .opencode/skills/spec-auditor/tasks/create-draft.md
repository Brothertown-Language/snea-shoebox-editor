# Task: create-draft

Generate an independent temporary draft spec BEFORE viewing the live spec.

## Purpose

Prevent the existing live spec from influencing/biasing the auditor's independent analysis. This subtask separation ensures the auditor writes their draft fresh, without seeing the spec they're auditing.

## Workflow

**Step 1: Generate Independent Draft**

Write a prose-driven analysis to `./tmp/tmp-spec-{issue}-draft.md` based ONLY on:
- The issue number (for context)
- Common spec template knowledge
- General best practices

**Step 2: DO NOT Load Live Spec**

At this stage, you MUST NOT:
- Read the GitHub Issue body
- Read any spec content
- View any related documentation
- Check previous audit results

**Step 3: Prose-Driven Analysis**

The draft must use prose, not static format checks:
- Explain what SHOULD be in a good spec for this issue type
- Describe the expected structure for fresh-start context
- List typical requirements for the six core areas
- Identify common pitfalls for this spec type

## Output

Create `./tmp/tmp-spec-{issue}-draft.md` with:

```markdown
# Independent Draft: Spec Content Analysis

Issue: #{issue_number}
Generated: {timestamp}

## Expected Structure (Prose Analysis)

### What a Good Spec Should Include

<prose description of expected content>

### Fresh-Start Context Requirements

<prose description of inline context requirements>

### Six Core Areas Coverage

<prose description of commands, testing, structure, style, git, boundaries>

### Common Pitfalls for This Spec Type

<prose description of typical issues>

## Draft Checklist

- [ ] Problem statement with context
- [ ] Affected files with anchors
- [ ] Related issues with summaries
- [ ] Constraints documented
- [ ] Assumptions stated
- [ ] Success criteria testable
- [ ] Edge cases identified
- [ ] Dependencies specified
- [ ] Risk assessment included
- [ ] Decision rationale present

## Architectural Reasoning Checklist

- [ ] WHY explained: Does the spec explain why this approach was chosen?
- [ ] Alternatives considered: Does the spec describe alternatives and why they were rejected?
- [ ] Constraints documented: Are technical/resource/time constraints specified?
- [ ] Risky dependencies identified: Are external/system dependencies called out with their risks?
- [ ] Implementation details: Are affected functions, modules, and patterns specified?

## Fresh-Start Context Checklist

- [ ] No memory references: No "see above", "as discussed", "previous comment"
- [ ] Stable anchors: File paths use function names or section headers (NOT line numbers)
- [ ] Inline context: All necessary context restated in spec body
- [ ] Cross-references complete: Issue links include summaries and relevance
- [ ] Line numbers flagged: Any line number references flagged as FRESH-START-VIOLATION
```

## Constraints

- Use `./tmp/` directory for temporary draft (per `070-environment.md`)
- Prose-driven analysis, NOT static format enforcement
- DO NOT view the live spec at this stage
- Cleanup required after audit completes

## Return Value

- Path to the generated draft file
- Confirmation that draft was created without viewing live spec
- Readiness to proceed to `audit` task