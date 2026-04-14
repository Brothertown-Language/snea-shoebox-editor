# Task: audit-phases

## Purpose

Analyze spec phase structure for concern separation quality. Reports findings to the agent — does NOT auto-fix.

## Procedure

1. Read the spec issue via GitHub MCP
2. Extract all phases and their steps
3. For each phase, analyze:
    - **Phase name**: Is it a specific concern or a generic activity (BOILERPLATE-TITLE)? Generic names like "Implementation", "Development", "Coding" are dual signals: BOILERPLATE-TITLE AND potential PLAN-BLEED (phase may describe HOW instead of WHAT).
    - **Concern boundaries**: Do all steps in this phase share the same concern?
   - **Risk profile**: What's the risk level (HIGH/MEDIUM/LOW) for each step?
   - **Blast radius**: How many files/components are affected?
   - **Deployment independence**: Can this phase be deployed independently?
4. Report findings in the standard format

## Keyword Hints (Starting Points)

| Keyword Pattern | Often Indicates | Risk Level |
|-----------------|-----------------|------------|
| migration, schema, table | Schema changes | HIGH |
| repository, query, ORM | Data access | MEDIUM |
| API endpoint, service, handler | Business logic | MEDIUM-LOW |
| UI, component, template | Presentation | LOW |

**These are HINTS. Always verify with actual concern analysis.**

## Finding Types

| Type | Problem Class | When to Report |
|------|---------------|----------------|
| Generic phase name | BOILERPLATE-TITLE | Phase uses "Implementation", "Testing", "Build" |
| Generic phase name (plan-bleed signal) | BOILERPLATE-TITLE + potential PLAN-BLEED | "Implementation", "Development", "Coding" — these names often indicate the phase describes HOW instead of WHAT |
| Mixed concerns | CONCERN_MIXING | Steps from different concern boundaries in one phase |
| Wrong dependency order | DEPENDENCY_REVERSAL | Phase depends on a later phase |
| High/low risk mixing | HIGH_RISK_GROUPING | HIGH and LOW risk steps in same phase |

## Report Format

```
Finding: [BOILERPLATE-TITLE|CONCERN_MIXING|DEPENDENCY_REVERSAL|HIGH_RISK_GROUPING] - [summary]
Location: [phase name and step]
Context: [why concern separation matters here]
Recommendation: [suggested phase name or split]
Severity: [HIGH|MEDIUM|LOW]
```

## Edge Cases

| Scenario | Analysis | Action |
|----------|----------|--------|
| Infrastructure phase | Crosses all layers by design | Report as intentional, no split needed |
| Testing phase | Validates all layers | Report as intentional, single concern |
| Single-step phase | Already atomic | No split needed |
| Phase with <3 steps | Too small to split cleanly | No split needed |
| Already separated | Analysis shows single concern | No change needed |

Co-authored with AI: <AI-Name> (<model-id>)