# Task: overview

Audits spec phase structure for concern separation, deployment independence, and risk isolation.

## Role

Concern Separation Auditor ensuring spec phases represent actual separation of concerns, not just generic activity names.

## When to Invoke

- When creating new specs (before approval)
- When reviewing existing specs for quality
- When "audit" or "review" keywords used
- Before approving spec implementation

## Phase Naming Quality (MANDATORY)

### Boilerplate Phase Names (PROHIBITED)

Phase names describing generic activities:
- "Implementation" — activity, not concern boundary
- "Testing" — activity, not concern boundary
- "Build" / "Create" / "Develop" — activities, not concerns
- "Verify" / "Validate" / "Check" — activities, not concerns
- "Deploy" / "Ship" / "Release" — activities, not concerns

### Meaningful Phase Names (REQUIRED)

Phase names describing specific concern boundaries:
- "Database Schema Setup" — specific concern boundary
- "API Endpoint Integration" — specific concern boundary
- "Error Handling Layer" — specific concern boundary
- "Configuration Migration" — specific concern boundary

## Validation Rules

| Pattern | Status | Reason |
|---------|--------|--------|
| Single-word activity name | BOILERPLATE-TITLE | No concern boundary specified |
| "Testing" alone | BOILERPLATE-TITLE | Generic activity |
| "Testing Infrastructure" | ACCEPTABLE | Specific concern (infrastructure) |
| "Unit Testing" | ACCEPTABLE | Specific testing type |
| "Implementation" with specific steps | REVIEW | May be acceptable if steps define concern |

## Blast Radius Analysis

Each phase should answer:

1. **What breaks if this phase fails?**
   - Clear, limited scope
   - Independent rollback possible

2. **What other phases depend on this?**
   - Explicit dependencies
   - No circular dependencies

3. **Can this be deployed independently?**
   - Phase-level deployment
   - Feature flags or configuration

## Risk Isolation

Each phase should isolate:

- **Data risks** — Database changes in separate phases
- **API risks** — Endpoint changes in separate phases
- **UI risks** — Frontend changes in separate phases
- **Configuration risks** — Config changes in separate phases

## Deployment Independence

Phase should be independently deployable:

1. **Database migrations** — Can run without code changes
2. **API endpoints** — Can be added/removed independently
3. **UI components** — Can be deployed separately from backend
4. **Configuration** — Can be toggled without redeployment

## Examples

**❌ BOILERPLATE:**
```markdown
## Phase 1: Implementation (Gated)
### Steps
1. ☐ Write the code
2. ☐ Make it work
3. ☐ Fix bugs
```

**✅ MEANINGFUL:**
```markdown
## Phase 1: Database Schema Setup (Gated)
### Steps
1. ☐ Create user table with authentication fields
2. ☐ Add indexes for login queries
3. ☐ Write migration script
```

## Cross-References

- Related: `spec-auditor` skill (spec quality audit)
- Related: `approval-gate` skill (spec+authorization requirements)
- Guidelines: `142-planning-archive-workflow.md` (phase naming rules)
