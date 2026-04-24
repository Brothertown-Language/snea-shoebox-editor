# Task: explore/pre-spec-inspection

## Purpose

Mandatory pre-spec code inspection and evidence artifact collection before any spec creation begins. Verifies code structure, imports, call paths, and architectural assumptions.

## Entry Criteria

- Spec or bug report proposes changes to existing code
- User has requested a feature, bug fix, or enhancement

## Exit Criteria

- All six inspection items addressed (or N/A with justification)
- Tool-call artifacts collected as evidence for each claim
- Verification classification table generated
- Agent may proceed to Step 1 of exploration

## Evidence Artifact Requirement (MANDATORY)

**🚫 CRITICAL: Each item MUST produce a tool-call artifact. Assertions without tool-call evidence are VERIFICATION-GAP findings.**

| Checklist Item | Verification Action | Tool Call | Problem Class |
| -- | -- | -- | -- |
| Trace call paths | Verify actual import/call relationships | `srclight_get_callers(symbol_name="target")`, `srclight_get_callees(symbol_name="target")` | VERIFICATION-GAP |
| Verify imports | Confirm actual import path | `srclight_get_symbol(name="module.symbol")` → check file location | VERIFICATION-GAP |
| Detect dead code | Verify referenced symbols are used | `srclight_get_dependents(symbol_name="symbol")` | MISSING-ELEMENT |
| Verify format/protocol | Confirm data format matches assumption | `srclight_get_signature(name="function_name")` | CONFLICTING |
| Confirm architectural layer | Verify code is in correct layer | `srclight_search_symbols(query="target", kind="function")` → check file path | STRUCTURE-VIOLATION |
| Check for existing alternatives | Search for existing solutions | `srclight_search_symbols(query="feature description")` | MISSING-ELEMENT |

## Evidence Format

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

## Classification on Failure

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Call path assumption wrong | CONFLICTING | conditional | Re-map actual call path |
| Import path assumed but not found | VERIFICATION-GAP | conditional | Search alternates |
| Dead code claimed as alive | MISSING-ELEMENT | auto-fix | Remove from affected-files |
| Data format assumption wrong | CONFLICTING | flag-for-review | HALT — redesign may be needed |
| Architectural layer violation | STRUCTURE-VIOLATION | flag-for-review | HALT — redesign may be needed |
| Alternative solution exists | MISSING-ELEMENT | conditional | Evaluate existing solution |

## Step 0.5: Cross-Spec Scope Search (MANDATORY)

**Before exploring project context, search for open specs/plans that may overlap:**

1. Query open issues: `github_list_issues(owner, repo, state="open")`
2. Filter for specs/plans with `[SPEC]`, `[PLAN]`, `[SPEC-FIX]` prefixes
3. Extract scope signals from user's request and compare

**Overlap Classification:**

| Classification | Criteria | Action |
| -- | -- | -- |
| FULL-SUPERSESSION | Existing spec entirely covers request | Report: "Spec #N covers this scope." |
| PARTIAL-OVERLAP | Existing spec shares files/symbols | Report overlaps and adjust scope |
| CONFLICT-RISK | Existing spec modifies same files | Report conflict and coordinate |
| INDEPENDENT | No meaningful overlap | Proceed silently |

## Acceptance Criteria

- [ ] All six checklist items addressed with tool-call evidence
- [ ] Cross-spec scope search complete (if applicable)
- [ ] Classification table generated for any findings
- [ ] HALT flag raised for STRUCTURE-VIOLATION or unresolvable CONFLICTING

## Context Required

- Related guidelines: `015-pre-spec-inspection.md`, `065-verification-honesty.md`
- Related tasks: `explore/exploration-workflow`