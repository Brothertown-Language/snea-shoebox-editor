# Task: check-cross-spec-overlap

## Purpose

Check for overlap between approved issues and open specs/plans OUTSIDE the current authorization batch. This prevents the pipeline from implementing work that conflicts with or duplicates open specs outside the authorization set.

## Entry Criteria

- Dependency graph built (from `build-dependency-graph`)
- Flat item list assembled with file_references and symbol_references for each included issue
- Access to GitHub API for querying open issues

## Exit Criteria

- All open `[SPEC]`, `[PLAN]`, and `[SPEC-FIX]` issues outside the batch queried
- Each approved issue compared against each external spec's scope signals
- Overlap classified using the four-tier model
- Overlap flags added to execution plan (advisory, not blocking)
- Approved issues proceed with implementation regardless of external overlap

## Procedure

### Cross-Spec Overlap Check Against Open Specs/Plans Outside the Batch

**In addition to cross-issue analysis within the approved batch, check for overlap with open specs/plans NOT in the batch.** This prevents the pipeline from implementing work that conflicts with or duplicates open specs outside the authorization set.

**Procedure:**

1. **Query open issues:** Use `github_list_issues(owner, repo, state="open")` to retrieve all open issues.

2. **Filter for specs/plans outside the batch:** Select issues with `[SPEC]`, `[PLAN]`, or `[SPEC-FIX]` title prefix that are NOT in the current approved batch.

3. **Extract scope signals from each external spec:** For each external spec/plan, extract:
   - File references (from affected-files, file_references sections)
   - Symbol references (function/class/module names)
   - Concern boundaries (phase descriptions and problem areas)

4. **Compare with each issue in the batch:** For each approved issue, compare its file_references, symbol_references, and concerns against each external spec's extracted references.

5. **Classify overlap using the four-tier model:**

   | Classification | Criteria | Action |
   |---------------|----------|--------|
   | **FULL-SUPERSESSION** | External spec entirely covers an approved issue's scope | Flag in execution plan: "Issue #N may be superseded by open spec #M" — do NOT exclude (external spec is not approved), but surface the overlap for awareness |
   | **PARTIAL-OVERLAP** | External spec shares files/symbols with an approved issue | Flag in execution plan: "Issue #N overlaps with open spec #M on files [list]" — aware for merge-time coordination |
   | **CONFLICT-RISK** | External spec modifies same files as an approved issue with conflicting intent | Flag in execution plan: "Issue #N conflicts with open spec #M on [files/symbols]" — serialize accordingly |
   | **INDEPENDENT** | No meaningful overlap | No action |

6. **Key difference from batch-internal overlap:** For external specs, FULL-SUPERSESSION does NOT exclude the approved issue (the external spec is not in the authorization set). It only produces a warning flag in the execution plan for awareness. The approved issue proceeds with implementation.

**Overlap with external specs is advisory, not blocking.** The approved batch has authorization; external specs do not. The check surfaces awareness for merge-time coordination but does not halt implementation.

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`