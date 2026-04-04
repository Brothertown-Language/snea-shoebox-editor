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

## Auto-Revise Categories (DEFAULT)

**⚠️ CRITICAL: Auto-revise is the DEFAULT. Prompt ONLY for catastrophic failures.**

The following table maps ALL violation types to auto-revise actions. If a violation type is not listed below, treat it as format violation (auto-revise).

| Violation Category | Example Violations | Auto-Revise Action |
|-------------------|---------------------|-------------------|
| **Format** | Boilerplate phase names ("Implementation", "Testing"), missing `STATUS:`, missing `CREATED:`, wrong structure, phase names describe activities instead of concerns | Fix format immediately (rename phases, add missing headers) |
| **Missing Elements** | No `CREATED` date, no success criteria, no problem statement | Add placeholders or infer from context |
| **Incomplete Context** | File references lack function/line info, code snippets missing, related issues not summarized | Fill in from codebase exploration |
| **Content Quality** | Vague success criteria, untestable criteria, "improve X" without threshold | Clarify criteria or add `[TODO: define threshold]` |
| **Interdependency** | Missing `Dependencies` section, prerequisites not linked | Add from codebase analysis |
| **Codebase Drift** | Spec references wrong file/function (code has `funcB`, spec says `funcA`) | Update spec to match code reality |
| **Related Spec Conflict** | Conflicting with other specs | Document conflict in spec, note which spec takes precedence |

### Auto-Revise Process

When auto-revise conditions are found:
1. **Fix immediately** - do NOT prompt for permission
2. **Post comment** explaining what was changed
3. **Continue to next check** - do NOT halt unless catastrophic

## Catastrophic Failures (REQUIRE USER PERMISSION)

**⚠️ Prompt user ONLY for catastrophic failures that cannot be auto-resolved.**

| Catastrophic Failure | Why It Requires Permission | Action |
|----------------------|----------------------------|--------|
| **Circular dependency between specs** | Requires design decision - which spec should be restructured? | POST comment explaining circular dependency, HALT |
| **Spec contradicts fundamental project architecture** | Requires architectural review - is the spec wrong or should architecture change? | POST comment explaining architecture violation (cite guideline), HALT |

### Catastrophic Failure Process

When catastrophic failure is found:
1. **POST comment** explaining the issue clearly
2. **HALT** - do NOT attempt to auto-revise
3. **Wait for user decision** - user must resolve architectural/design conflict

## Output

After review:
1. **If auto-revisable issues found**: Update spec with fixes, post comment noting changes
2. **If user-prompt issues found**: Post comment explaining conflict, HALT
3. **If all checks pass**: Report spec ready for implementation

## Cross-References

- `144-planning-spec-templates.md` - Spec template requirements
- `140-planning-spec-creation.md` - Spec creation workflow
- `130-authority-source.md` - Code as authoritative source