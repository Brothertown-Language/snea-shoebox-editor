# Task: traceability

## Purpose

Map every requirement to spec section, test, and implementation step. Ensure nothing is lost between requirements and implementation.

## Entry Criteria

- Requirements extraction completed
- (Optional) Decomposition completed

## Exit Criteria

- Every requirement maps to at least one spec section
- Every spec section maps to at least one requirement
- Test scenarios identified for each requirement
- Implementation steps traceable to requirements

## Procedure

### Step 1: Build Traceability

Map each requirement to:
- Which spec section covers it
- What test scenario validates it
- Which implementation step implements it

### Step 2: Verify Bidirectional Coverage

- **Forward:** Every requirement → spec section (nothing lost)
- **Backward:** Every spec section → requirement (no scope creep)
- **Test coverage:** Every requirement → at least one test scenario
- **Implementation coverage:** Every requirement → at least one implementation step

### Step 3: Identify Gaps

- Requirements without spec sections (lost requirements)
- Spec sections without requirements (scope creep)
- Requirements without test scenarios (untestable)
- Requirements without implementation steps (orphan)

## Content Coverage

Can each requirement be traced to a spec section, test scenario, and implementation step? Does the traceability provide bidirectional coverage?

- **Forward traceability:** Every requirement → spec section and test
- **Backward traceability:** Every spec section → requirement

**Any format that provides this coverage is acceptable.** A formal traceability matrix table works well for complex specs. A prose list or inline references work well for simple specs. The agent chooses the format that best serves the spec.

## Adversarial Verification of Trace Targets (MANDATORY)

**🚫 CRITICAL: Every trace target (referenced issue, spec, code symbol) MUST be verified to actually exist. Unverified trace references are MISSING-TRACEABILITY findings per `065-verification-honesty.md`.**

### Verification Procedure

After building traceability (Step 1-3), verify every referenced target:

| Trace Target Type | Verification Action | Tool Call | Problem Class |
|-------------------|-------------------|-----------|---------------|
| Referenced GitHub Issue | Verify the issue exists and is accessible | `github_issue_read(method=get, issue_number=N)` → confirm `title` is not "404" | MISSING-TRACEABILITY |
| Referenced spec (by issue number) | Verify the spec Issue exists with proper prefix and labels | `github_issue_read(method=get, issue_number=N)` → check title starts with `[SPEC]` | MISSING-TRACEABILITY |
| Referenced code symbol | Verify the symbol exists in the current codebase | `srclight_get_symbol(name="symbol_name")` → confirm non-empty result | VERIFICATION-GAP |
| Referenced file path | Verify the file exists at the claimed path | `glob(pattern="**/filepath")` → confirm match | VERIFICATION-GAP |
| Bidirectional coverage | Verify every requirement maps to a section AND every section maps to a requirement | Cross-reference requirement list with section anchors | MISSING-TRACEABILITY |

### Evidence Format

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Classification on Failure

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced issue does not exist | MISSING-TRACEABILITY | auto-fix | Remove or replace the broken reference |
| Referenced spec lacks [SPEC] prefix | MISSING-TRACEABILITY | conditional | Verify it IS a spec; add prefix or fix reference |
| Referenced code symbol not found | VERIFICATION-GAP | conditional | May be renamed/removed; verify alternate names |
| Referenced file path not found | VERIFICATION-GAP | conditional | May be reorganized; search for file |
| Requirement with no section mapping | MISSING-TRACEABILITY | auto-fix | Add section mapping |
| Section with no requirement mapping | STRUCTURE-VIOLATION | flag-for-review | Possible scope creep; report for domain review |

**These verifications are MANDATORY. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

## Context Required

- Preceded by: `requirements`, optionally `decompose`
- Feeds into: `write`
- Note: Creation-time traceability is enforced here. `spec-auditor` verifies traceability as a second pass.