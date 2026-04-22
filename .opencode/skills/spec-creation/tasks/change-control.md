# Task: change-control

## Purpose

Version the spec, document rationale and impact analysis for changes. Enforce change discipline for spec revisions.

## Entry Criteria

- Spec written and approved (initial version), OR
- Spec revision needed after audit or feedback

## Exit Criteria

- Spec version incremented
- Rationale documented for each change
- Impact analysis completed
- STATUS updated to `REVISED - NEEDS APPROVAL`

## Procedure

### Step 1: Identify Changes

Document each change:
- What changed (section, requirement, criterion)
- Why it changed (audit finding, user feedback, scope adjustment)
- Impact (what other sections are affected)

### Step 2: Version the Spec

- Increment version number: `STATUS: 1.0` → `STATUS: 1.1 (REVISED - NEEDS APPROVAL)`
- Add `needs-approval` label to the GitHub Issue
- Post chat output with prose revision summary (per `issue-operations` skill → `comment` task)
- Post Issue comment with prose revision summary

### Step 3: Impact Analysis

For each change, document:
- Which requirements are affected
- Which success criteria need updating
- Which traceability mappings changed
- Whether the change requires re-audit

### Step 4: HALT

After revision, the spec needs fresh authorization:
- Do NOT proceed to implementation
- Wait for explicit `approved` or `go`

## Adversarial Verification of STATUS Exemption (MANDATORY)

**🚫 CRITICAL: Every STATUS marker claiming exemption from change control MUST be verified against actual revision history. Unverified exemption claims are CONFLICTING findings per `065-verification-honesty.md`.**

### Verification Procedure

After Step 1 (Identify Changes) and Step 2 (Version the Spec), verify any STATUS exemption claims:

| Exemption Claim | Verification Action | Tool Call | Problem Class |
|----------------|-------------------|-----------|---------------|
| "Initial spec creation" (no version increment) | Verify the spec has no prior versions — check Issue body for `STATUS: 1.0` or version history | `github_issue_read(method=get, issue_number=N)` → search body for `STATUS:` markers | CONFLICTING |
| "Non-substantive change" (typos, cross-refs) | Verify the change is truly non-substantive — no scope, requirements, or success criteria changes | `github_issue_read(method=get, issue_number=N)` → compare current vs previous body content | CONFLICTING |
| "STATUS marker update" (checkbox, phase number) | Verify the change is only a STATUS marker toggle — no content change | `github_issue_read(method=get, issue_number=N)` → diff body against comment history | STRUCTURE-VIOLATION |
| "Bug report addition" (separate from spec content) | Verify the added content is a bug report section, not a spec content change | `github_issue_read(method=get, issue_number=N)` → check section added | VERIFICATION-GAP |

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
| Claims "initial creation" but `STATUS: 1.0` exists | CONFLICTING | auto-fix | Increment version, apply change control |
| Claims "non-substantive" but content changed | CONFLICTING | flag-for-review | HALT — requires domain review |
| Claims "STATUS update" but content also changed | STRUCTURE-VIOLATION | auto-fix | Apply full change control to content change |
| Claims "bug report" but adds spec requirements | VERIFICATION-GAP | conditional | Verify scope; if requirements changed, apply change control |

**These verifications are MANDATORY for any STATUS exemption claim. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

## Exemptions

- Initial spec creation (version 1.0): No change control needed
- STATUS marker updates: No version increment, no approval revocation
- Non-substantive changes (typos, cross-refs): No version increment

## Context Required

- Preceded by: `write` (spec must exist to revise)
- Followed by: `approval-gate` (fresh authorization required)