# Task: ground-truth

## Purpose

Adversarial verification of metadata claims against direct evidence. Do not trust markers, labels, or assertions at face value — verify every claim against actual state. This subtask embodies the "don't trust — verify" principle: a STATUS marker saying DRAFT might hide complete content; a `needs-approval` label might be stale after explicit authorization; a cross-reference might point to a deleted issue.

**Applies to all document types.** Every document has metadata claims worth verifying: status markers, labels, references, and authorization state.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| STATUS marker maturity | STRUCTURE-VIOLATION | Compare STATUS value against actual content maturity |
| Label accuracy | MISSING-ELEMENT | Verify label claims match actual issue state |
| Content maturity | STRUCTURE-VIOLATION | Classify spec as brainstorm/draft/detailed/complete based on actual content, not STATUS marker |
| Cross-reference existence | MISSING-TRACEABILITY | Verify all `#N` references point to existing, matching content |
| Cross-reference match | CONFLICTING | Verify cross-referenced issues contain content matching the reference's claimed topic |
| Code reference existence | VERIFICATION-GAP | Verify all file paths, function names, and code references in spec exist in the actual codebase |
| Authorization currency | STRUCTURE-VIOLATION | Check whether authorization claims have been superseded by spec revisions |
| Already-implemented detection | GROUND-TRUTH-MISMATCH (already-implemented) | Verify all success criteria are satisfied in the current codebase, indicating the spec describes work already done |

## Content Maturity Classification

| Maturity Level | Indicators |
|----------------|-----------|
| BRAINSTORM | Fragmented ideas, no phases, no success criteria, no approach decision |
| DRAFT | Phases outlined but steps are vague, approach chosen but not detailed, incomplete success criteria |
| DETAILED | All phases have concrete steps, approach is specific, success criteria are testable, but gaps remain |
| COMPLETE | All phases fully specified, all success criteria measurable, all edge cases addressed, no placeholders |

**Mismatch rules:**

| STATUS Says | Actual Maturity | Problem Class | Classification |
|-------------|----------------|---------------|----------------|
| BRAINSTORM | DETAILED or COMPLETE | STRUCTURE-VIOLATION | auto-fix: update STATUS marker |
| DRAFT | COMPLETE | STRUCTURE-VIOLATION | auto-fix: update STATUS marker |
| DRAFT | BRAINSTORM | — | Not a violation (conservative marking is acceptable) |
| DETAILED | COMPLETE | STRUCTURE-VIOLATION | auto-fix: update STATUS marker |
| COMPLETE | BRAINSTORM or DRAFT | CONFLICTING | flag-for-review |

## Procedure

1. **STATUS marker vs. content maturity:**
   - Read the document via GitHub MCP (`github_issue_read(method=get)`)
   - Extract the STATUS marker value
   - Analyze actual content against maturity classification table above
   - If STATUS says BRAINSTORM/DRAFT but content is DETAILED/COMPLETE → STRUCTURE-VIOLATION (auto-fix: update STATUS)
   - If STATUS says COMPLETE but content is BRAINSTORM/DRAFT → CONFLICTING (flag-for-review)
   - Evidence artifact: GitHub MCP response showing current STATUS value; content analysis in finding

2. **Label accuracy:**
   - Extract current labels via `github_issue_read(method=get_labels)`
   - Check if `needs-approval` label is present while explicit authorization exists (search issue comments for "approved" or "go" from a developer)
   - If `needs-approval` present AND explicit authorization exists → MISSING-ELEMENT (conditional: verify auth scope before removing label)
   - Evidence artifact: Label list from GitHub MCP; comment search results

3. **Cross-reference existence and match:**
   - Extract all `#N` references from document body
   - For each reference, call `github_issue_read(method=get, issue_number=N)` to verify existence
   - If referenced issue does not exist → MISSING-TRACEABILITY (flag-for-review)
   - If referenced issue exists but content mismatches the reference's claimed topic → CONFLICTING (flag-for-review)
   - Evidence artifact: GitHub MCP responses for each referenced issue

4. **Code reference verification:**
   - Extract all file paths and function names from document body
   - For file paths: use `srclight_search_symbols` or `glob` to verify existence in codebase
   - For function names: use `srclight_get_signature` to verify the symbol exists
   - If file or function does not exist → VERIFICATION-GAP (flag-for-review)
   - Evidence artifact: Search/glob results confirming existence or absence

5. **Authorization currency:**
   - If document claims authorization or has been approved, check revision history
   - Read issue comments via `github_issue_read(method=get_comments)`
   - If any spec revision occurred after the most recent authorization → STRUCTURE-VIOLATION (auto-fix: add re-approval note)
   - Evidence artifact: Comment history showing authorization date and revision date

6. **Already-implemented detection (GROUND-TRUTH-MISMATCH):**
   - Extract all success criteria from the spec
   - For each criterion, verify it is satisfied in the current codebase:
     - File/path existence: use `glob`, `srclight_search_symbols`, or `srclight_get_signature`
     - Code behavior: use `srclight_get_symbol` or `read` to confirm implementation
     - Absence of removed items: verify directories/files that should be deleted don't exist
     - Cross-reference cleanliness: `grep` for references that should no longer exist
   - Classify the finding based on verification results:
     - **ALL success criteria verified**: → GROUND-TRUTH-MISMATCH (already-implemented) — conditional auto-fix
     - **SOME criteria not met**: → flag-for-review with details of which are met and which are not
     - **NONE met**: Do not classify as already-implemented (the spec is simply not implemented yet)
   - For already-implemented findings, post a verification summary comment on the issue documenting evidence for each success criterion, then recommend closure via `approval-gate --task verify-already-implemented`
   - Evidence artifact: Per-criterion verification results with tool call evidence

## Report Format

```
Subtask: ground-truth
Finding: [STRUCTURE-VIOLATION|MISSING-ELEMENT|MISSING-TRACEABILITY|CONFLICTING|VERIFICATION-GAP|GROUND-TRUTH-MISMATCH] - [summary]
Location: [section of spec]
Context: [why this claim is unverified or mismatched]
Evidence: [tool call or command that produced the evidence]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

**For GROUND-TRUTH-MISMATCH (already-implemented) findings, use this extended format:**

```
Subtask: ground-truth
Finding: GROUND-TRUTH-MISMATCH (already-implemented) - [summary]
Location: Success Criteria section
Context: All success criteria are verified as satisfied in the current codebase
Evidence:
  - SC1: [criterion] — [tool call result confirming met]
  - SC2: [criterion] — [tool call result confirming met]
  - ...
Classification: conditional
Fix Action: Posted verification summary comment; recommended closure via verify-already-implemented
Severity: MEDIUM
```

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| STRUCTURE-VIOLATION (STATUS mismatch - conservative) | auto-fix | Update STATUS marker to reflect actual content maturity |
| STRUCTURE-VIOLATION (authorization superseded) | auto-fix | Add re-approval note to document body |
| GROUND-TRUTH-MISMATCH (already-implemented) | conditional | Post verification summary comment with evidence for each success criterion; close issue as completed |
| MISSING-ELEMENT (stale needs-approval label) | conditional | Verify auth scope, then remove label if confirmed |
| MISSING-TRACEABILITY (cross-ref to non-existent issue) | flag-for-review | Cannot create missing issues; developer must resolve |
| CONFLICTING (cross-ref to mismatched content) | flag-for-review | Intent of reference requires domain judgment |
| CONFLICTING (STATUS says COMPLETE but content is immature) | flag-for-review | May indicate intentional tracking; developer must judge |
| VERIFICATION-GAP (code reference to non-existent file/function) | flag-for-review | Code may be planned but not yet implemented; developer must confirm |

**Conditional safety check for already-implemented:** Closing an issue requires verifying ALL success criteria are met — partial implementation does NOT qualify. Each criterion must have independent evidence from a tool call or command invocation. If any criterion lacks clear evidence, the finding is downgraded to flag-for-review.

## When to Run

Always. This is a baseline subtask for all document types. Every document has metadata claims that require verification.

## Cross-Reference

- `065-verification-honesty.md` — Core verification honesty principle; this subtask extends it to metadata claims
- `010-approval-gate.md` — Authorization rules; this subtask verifies authorization claims against actual state
- `fresh-start` subtask — Self-containment checks; ground-truth complements by verifying metadata, not content references

Co-authored with AI: <AgentName> (<ModelId>)