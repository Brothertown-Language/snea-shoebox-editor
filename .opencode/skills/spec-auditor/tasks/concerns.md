# Task: concerns

## Purpose

Analyze spec phase structure for concern separation quality — deployment independence, risk profile, and blast radius. All findings are reported, NOT auto-applied.

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
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| BOILERPLATE-TITLE | auto-fix | Rename phase to describe specific concern |
| CONCERN_MIXING | auto-fix | Split mixed-concern phase into separate phases per concern |
| DEPENDENCY_REVERSAL | auto-fix | Reorder phases to match dependency order |
| HIGH_RISK_GROUPING | auto-fix | Separate high-risk steps into their own phase or flag at top of phase |

## Why Auto-Fix Is Safe for These Findings

- BOILERPLATE-TITLE: Generic names are always suboptimal; specific concern names are always better
- CONCERN_MIXING: Mixed-concern phases create deployment risk; splitting is always correct
- DEPENDENCY_REVERSAL: Wrong order is objectively wrong; reordering is always correct
- HIGH_RISK_GROUPING: Separating risk profiles is always safer

## When to Run

- Feature specs with multiple phases
- Specs with more than 2 phases
- Infrastructure-heavy specs

## When to Skip

- Single-task specs (no phases to analyze)
- Simple bug fixes with one phase

Co-authored with AI: OpenCode (ollama-cloud/glm-5)