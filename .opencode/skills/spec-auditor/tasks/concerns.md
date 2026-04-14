# Task: concerns

## Purpose

Analyze spec phase structure for concern separation quality — deployment independence, risk profile, and blast radius. All findings are reported for agent review, NOT auto-applied.

**Delegated from:** concern-separation-auditor (v1). Now a subtask within spec-auditor.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Phase names describe concerns | BOILERPLATE-TITLE | Generic names like "Implementation", "Testing" |
| Concern mixing | CONCERN_MIXING | Steps from different concerns in one phase |
| Dependency order | DEPENDENCY_REVERSAL | Phases in wrong dependency order |
| Risk grouping | HIGH_RISK_GROUPING | High-risk and low-risk steps mixed |

## Concern Analysis (Not Rigid Template)

This subtask analyzes ACTUAL concerns, not static templates.

**Different project structures have different concerns:**
- Stateless service: Config → API → Tests (no DB, no UI)
- CLI tool: Args → Core → Output (deployment is reinstall)
- Frontend-only: Components → State → Tests (no backend)
- Infrastructure: Setup (crosses all layers, ONE concern)
- Monolith: Schema → API → UI (may not have repository layer)

The DB→Repo→BL→UI pattern is COMMON but NOT mandatory.

## Analysis Questions

For each phase, ask:

1. **Can this step be deployed independently?**
2. **What's the risk profile?** (HIGH: schema, migrations; MEDIUM: data access; MEDIUM-LOW: API; LOW: UI)
3. **What's the blast radius?** (How many files/components affected?)
4. **What are the dependencies?** (Which steps MUST complete first?)

## Report Format

```
Subtask: concerns
Finding: [BOILERPLATE-TITLE|CONCERN_MIXING|DEPENDENCY_REVERSAL|HIGH_RISK_GROUPING] - [summary]
Location: [phase/step where issue found]
Context: [why concern separation matters for this spec]
Classification: flag-for-review
Fix Action: flagged for review — [reason]
Severity: [HIGH|MEDIUM|LOW]
```

## Why Flag-for-Review (Not Auto-Fix)

Concern-splitting and phase-renaming require context judgment that the auditor lacks:

- A BOILERPLATE-TITLE rename might be wrong for the specific spec. The spec author may have chosen a simple name intentionally for a simple change.
- A concern split might break an intentionally grouped phase. Some phases group related concerns that are deployed together.
- The agent has full context about the spec's complexity, domain, and deployment requirements. The auditor doesn't.

All findings are reported for agent review. The agent decides whether to apply changes based on their understanding of the spec's domain.

This aligns with the v2 design philosophy from `concern-separation-auditor/SKILL.md`: findings are presented, not imposed.

## When to Run

- Feature specs with multiple phases
- Specs with more than 2 phases
- Infrastructure-heavy specs

## When to Skip

- Single-task specs (no phases to analyze)
- Simple bug fixes with one phase

Co-authored with AI: <AI-Name> (<model-id>)