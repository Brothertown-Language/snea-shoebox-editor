# Task: fresh-start

## Purpose

Check that a document is self-contained and understandable by an agent with no memory context. No "see above", no vague references, no assumptions about prior conversations.

**Note for non-spec document types:** Self-containment checks focus on the document type's specific requirements:
- **Spec:** Full self-containment — all context inline, no external references without summaries
- **Plan:** Milestones and deliverables must be self-contained; cross-references to specs must include summaries
- **Process Flow:** Each step's inputs and outputs must be explicitly stated; no assumed knowledge of tool locations or credentials
- **Runbook/SOP:** Prerequisites, tools, and credentials must be listed; no assumed environment knowledge
- **Checklist:** Items must be self-explanatory; no ambiguous shorthand
- **Reference Doc:** Definitions and context must be included; cross-references must have summaries

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Inline context | FRESH-START-VIOLATION | Does the spec rely on "see above", "as discussed", or external references? |
| Stable anchors | FRESH-START-VIOLATION | Do file references use function names and section headers, not line numbers? |
| Cross-reference quality | FRESH-START-VIOLATION | Do cross-references include summaries and relevance, not just issue numbers? |
| Decision rationale | FRESH-START-VIOLATION | Are decisions explained with why, alternatives, and constraints? |
| Context overflow | CONTEXT-OVERFLOW | Are sections overly long or complex, risking truncation in LLM context? |

## Procedure

1. Read the spec issue via GitHub MCP
2. Scan for: "see above", "as discussed", "as mentioned", "previously", bare issue numbers without summaries
3. Check that file references use anchors (function names, section headers), not line numbers
4. Verify cross-references include URLs, summaries, and relevance
5. Verify decision rationale is documented
6. Flag sections that exceed reasonable length for LLM processing

## Report Format

```
Subtask: fresh-start
Finding: [FRESH-START-VIOLATION|CONTEXT-OVERFLOW] - [summary]
Location: [section of spec]
Context: [why this matters]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| FRESH-START-VIOLATION | auto-fix | Inline context, replace "see above"/"as discussed" with actual content, add summaries to cross-references |
| CONTEXT-OVERFLOW | conditional | Reduce section length after verifying all requirements are preserved |

## Standards Reference

Per guidelines `045-open-questions.md` and `140-planning-spec-creation.md`:
- All context must be stated inline
- File references must use stable anchors
- Cross-references must include summaries

Co-authored with AI: <AI-Name> (<model-id>)