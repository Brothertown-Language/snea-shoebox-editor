# Task: review-spec

Review and revise specs for correctness, dev-architect compliance, interdependencies, and ordering requirements.

## Purpose

Automatically review specs when creating or revising, auto-revise when issues are found, and only prompt the user when serious conflicts or critical issues are detected.

## Correctness Checks

### Fresh-Start Context
- [ ] Spec is self-contained (no "see above" references)
- [ ] All context stated inline
- [ ] No reliance on conversation history or memory

### Completeness
- [ ] Problem statement present with WHY (context)
- [ ] Affected files listed with anchors (function names, section headers)
- [ ] Code snippets included for short sections
- [ ] Related issues linked with URLs and summaries
- [ ] Constraints documented (technical, time, compatibility)
- [ ] Assumptions listed
- [ ] Success criteria testable and measurable
- [ ] Edge cases identified
- [ ] Dependencies documented
- [ ] Risk assessment present

### Success Criteria
- [ ] Each criterion is testable (can verify with automated test or manual check)
- [ ] Each criterion is measurable (has specific threshold or state)
- [ ] No vague criteria ("improve performance", "better UX")

### Edge Cases
- [ ] Boundary conditions identified
- [ ] Error handling documented
- [ ] Failure scenarios considered

## Compliance Checks

### Execution Plan Format
- [ ] Execution plan has numbered steps
- [ ] Files to touch section present
- [ ] Approach documented with rationale
- [ ] Risks & unknowns section present
- [ ] Out of scope section present

### Phase Structure
- [ ] Phase names describe concerns, not activities (✅ "Database Schema", ❌ "Implementation")
- [ ] Each phase has clear steps
- [ ] Gating and auto-progress marked

## Interdependency Checks

### Prerequisites
- [ ] Spec identifies prerequisite specs (must complete before this one)
- [ ] Prerequisite specs exist and are accessible
- [ ] Prerequisite status verified (completed or in-progress)

### Dependents
- [ ] Spec identifies dependent specs (can only start after this one)
- [ ] Dependent specs documented in Dependencies section

### External Dependencies
- [ ] Libraries documented
- [ ] APIs documented
- [ ] Services documented
- [ ] Configuration requirements documented

### Circular Dependencies
- [ ] No circular dependencies between specs
- [ ] If circular dependency detected → PROMPT USER (requires design decision)

## Ordering Checks

### Documentation
- [ ] Ordering requirements clearly documented
- [ ] Prerequisites marked as complete or in-progress
- [ ] Dependent specs marked as blocked pending this spec

## Auto-Revise Conditions

**Auto-revise when:**
- Missing elements (add them)
- Incomplete context (fill in details)
- Format violations (fix format)
- Interdependency not documented (add to Dependencies section)
- Ordering not specified (add ordering requirements)

## Prompt User Conditions

**Prompt user when:**
- Serious conflict with other specs (cannot auto-resolve)
- Critical codebase inconsistency (spec doesn't match code state)
- Project goal violation (spec contradicts documented goals)
- Circular dependency detected (requires design decision)

## Output

After review:
1. **If auto-revisable issues found**: Update spec with fixes, post comment noting changes
2. **If user-prompt issues found**: Post comment explaining conflict, HALT
3. **If all checks pass**: Report spec ready for implementation

## Cross-References

- `144-planning-spec-templates.md` - Spec template requirements
- `140-planning-spec-creation.md` - Spec creation workflow
- `130-authority-source.md` - Code as authoritative source