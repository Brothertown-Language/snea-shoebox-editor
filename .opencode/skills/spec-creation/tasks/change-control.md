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
- Post chat output with prose revision summary (per `github-comments` skill → Spec Revision Chat Output)
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

## Exemptions

- Initial spec creation (version 1.0): No change control needed
- STATUS marker updates: No version increment, no approval revocation
- Non-substantive changes (typos, cross-refs): No version increment

## Context Required

- Preceded by: `write` (spec must exist to revise)
- Followed by: `approval-gate` (fresh authorization required)