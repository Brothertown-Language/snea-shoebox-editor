# Task: check-independence

## Purpose

Validate deployment independence between phases. Reports findings — does NOT auto-fix.

## Procedure

1. Read the spec issue via GitHub MCP
2. For each pair of phases, check:
   - **Can Phase A be deployed without Phase B?**
   - **Can Phase B be deployed without Phase A?**
   - **If Phase A fails, does Phase B still function?**
3. Build a dependency matrix
4. Identify coupled phases that should potentially be merged or uncoupled
5. Report findings in the standard format

## Dependency Matrix

| | Phase 1 | Phase 2 | Phase 3 |
|---|---------|---------|---------|
| Phase 1 | — | depends on | — |
| Phase 2 | — | — | depends on |
| Phase 3 | — | — | — |

## Finding Types

| Type | Problem Class | When to Report |
|------|---------------|----------------|
| Coupled deployment | CONCERN_MIXING | Two phases must deploy together |
| Circular dependency | DEPENDENCY_REVERSAL | Phases depend on each other |
| Implicit dependency | CONCERN_MIXING | Dependency not stated in spec |

## Standalone Deployment Test

For each phase, ask:
1. Can this phase be deployed to production on its own?
2. After deployment, does the system still function (possibly with reduced features)?
3. Can this phase be rolled back independently?

If the answer to any question is "no" and the phase isn't explicitly marked as requiring another, flag it.

## Report Format

```
Finding: [CONCERN_MIXING|DEPENDENCY_REVERSAL] - [summary]
Location: [phases involved]
Context: [why independence matters here]
Recommendation: [merge phases OR make dependency explicit OR uncouple]
Severity: [HIGH|MEDIUM|LOW]
```

Co-authored with AI: <AI-Name> (<model-id>)

## Live Verification: Dependency Claims (MANDATORY)

**Each phase dependency/independence claim MUST be verified against actual code. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Phases are independent" | Verify no import/call dependency exists | `srclight_get_callers(symbol_name="target")` → check cross-phase calls | CONFLICTING |
| "Phase A depends on Phase B" | Verify actual code dependency exists | `srclight_get_callees(symbol_name="target")` → check outputs | VERIFICATION-GAP |
| "No circular dependency" | Verify no bidirectional imports | `srclight_get_dependents(symbol_name="target")` → check for cycles | CONFLICTING |
| "Implicit dependency" | Verify unstated dependency in code | `srclight_get_callers` + compare to spec-declared dependencies | MISSING-ELEMENT |

**Evidence artifact:** Tool call results confirming or refuting dependency claims.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Independence claimed but code dependency exists | CONFLICTING | flag-for-review | Report — phases may need merging or re-ordering |
| Dependency claimed but no code evidence | VERIFICATION-GAP | auto-fix | Remove unverified dependency from findings |
| Circular dependency found | CONFLICTING | flag-for-review | Report — requires architectural decision |
| Unstated code dependency found | MISSING-ELEMENT | conditional | Add to dependency matrix |