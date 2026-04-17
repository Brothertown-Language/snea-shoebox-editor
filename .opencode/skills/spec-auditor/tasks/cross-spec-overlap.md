# Task: cross-spec-overlap

## Purpose

Detect overlap between the audited spec and other open specs/plans by comparing file references, symbol references, and concern boundaries. Produces findings classified as CROSS-SPEC-OVERLAP or FULL-SUPERSESSION.

## Entry Criteria

- Invoked as a conditional subtask during spec/plan audit
- The audited document has file_references, symbol_references, or affected-files sections
- GitHub API access available for issue searches

## Exit Criteria

- All open `[SPEC]`, `[PLAN]`, and `[SPEC-FIX]` issues searched for overlap
- Each overlap classified (FULL-SUPERSESSION, PARTIAL-OVERLAP, CONFLICT-RISK, INDEPENDENT)
- Findings produced in spec-auditor report format
- No developer escalation required — autonomous classification

## Procedure

### Step 1: Extract References from Audited Document

Extract overlap-significant references from the audited spec/plan:

1. **File references:** All file paths mentioned in affected-files, file_references, or similar sections
2. **Symbol references:** All function, class, and module names referenced in the spec body
3. **Concern boundaries:** Phase descriptions and their concern areas (what each phase addresses)

If the document has no extractable references, exit with no findings.

### Step 2: Search Open Specs/Plans for Overlap

Query GitHub for all open `[SPEC]`, `[PLAN]`, and `[SPEC-FIX]` issues (excluding the currently audited issue):

```
github_list_issues(owner, repo, state="open")
```

Filter results for issues with `[SPEC]`, `[PLAN]`, or `[SPEC-FIX]` title prefix.

For each open spec/plan issue:

1. Read the issue body via `github_issue_read(method=get, issue_number=N)`
2. Extract file paths, symbol names, and concern areas from the body
3. Compare with the audited document's references

### Step 3: Classify Overlap

For each pair of overlapping references, classify using the four-tier model:

| Classification | Criteria | Auto-fix Action |
|---------------|----------|----------------|
| **FULL-SUPERSESSION** | Spec B's scope entirely covered by Spec A (A's file_references ⊇ B's, A's concern boundaries ⊇ B's, all B's success criteria ⊇ B's) | Propose superseding: flag B as superseded by A, suggest closing B with cross-reference |
| **PARTIAL-OVERLAP** | Specs share file_references or symbol_references but have different core concerns | Flag for review: note shared files/symbols, describe each spec's distinct concern |
| **CONFLICT-RISK** | Same files modified in conflicting ways (different intent for same code) | Flag for review: note conflicting files, describe opposing intents |
| **INDEPENDENT** | No meaningful overlap in files, symbols, or concern boundaries | No action |

**Classification heuristics:**

- **File overlap:** Two specs reference the same file path → check if modifications are to different sections (PARTIAL-OVERLAP) or same section with conflicting intent (CONFLICT-RISK)
- **Symbol overlap:** Two specs reference the same function/class → check if modifications are compatible (PARTIAL-OVERLAP) or contradictory (CONFLICT-RISK)
- **Concern overlap:** Two specs address the same concern → check if one subsumes the other (FULL-SUPERSESSION) or if they have distinct sub-concerns (PARTIAL-OVERLAP)
- **No overlap:** Files, symbols, and concerns are all distinct → INDEPENDENT (no finding produced)

### Step 4: Produce Findings

For each overlap detected (excluding INDEPENDENT), produce a finding:

```
Subtask: cross-spec-overlap
Finding: [CROSS-SPEC-OVERLAP|FULL-SUPERSESSION] - [summary]
Location: [section of spec where overlap was found]
Context: [overlapping issue #N, shared references, classification]
Classification: auto-fix | flag-for-review
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

**Classification mapping:**

| Overlap Classification | Finding Classification | Auto-fix |
|----------------------|----------------------|----------|
| FULL-SUPERSESSION | auto-fix (CROSS-SPEC-OVERLAP) | Propose superseding: add cross-reference note to audited spec |
| PARTIAL-OVERLAP | flag-for-review (CROSS-SPEC-OVERLAP) | Flag: note shared files/symbols and distinct concerns |
| CONFLICT-RISK | flag-for-review (CROSS-SPEC-OVERLAP) | Flag: note conflicting files and opposing intents |
| INDEPENDENT | (no finding) | No action |

**AUTO-FIX for FULL-SUPERSESSION:** Add a `Superseded-by` or `Overlap` note to the audited spec's issue body in the relevant section. The note includes the overlapping issue number, shared references, and the classification.

**FLAG-FOR-REVIEW for PARTIAL-OVERLAP and CONFLICT-RISK:** Report in executive summary only. Do NOT modify the spec body for these — they require developer judgment about how to resolve the overlap.

### Step 5: No-Overlap Case

If no overlapping specs are found after Step 2, exit with no findings. Do not produce a "no overlap found" finding — absence of overlap is expected and not noteworthy.

## Context Required

- The audited document's content (from previous subtask reads)
- GitHub API access for issue searches
- Session variables: `github.owner`, `github.repo`

## Problem Classes Produced

| Class | Description | Auto-fix Eligible |
|-------|-------------|-------------------|
| CROSS-SPEC-OVERLAP | Overlap detected between specs (PARTIAL-OVERLAP or CONFLICT-RISK) | No — flag for review |
| FULL-SUPERSESSION | One spec's scope entirely covers another's | Yes — propose superseding |

## Red Flags

**Never:**

- Skip searching for open specs/plans before classifying overlap
- Auto-fix PARTIAL-OVERLAP or CONFLICT-RISK — these require developer judgment
- Classify overlap without extracting and comparing actual file/symbol references
- Produce findings for INDEPENDENT (non-overlapping) specs

**Always:**

- Search `[SPEC]`, `[PLAN]`, and `[SPEC-FIX]` labels for overlap candidates
- Compare file_references, symbol_references, AND concern boundaries (not just titles)
- Use the four-tier classification model (FULL-SUPERSESSION, PARTIAL-OVERLAP, CONFLICT-RISK, INDEPENDENT)
- Classify autonomously — no developer escalation for classifiable overlap