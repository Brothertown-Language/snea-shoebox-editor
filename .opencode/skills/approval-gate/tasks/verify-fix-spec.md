# Task: verify-fix-spec

## Purpose

Verify that a bug report has a fix spec sub-issue before it can be considered complete. This enforces the critical rule that bugs must have fix specs before closure.

## Entry Criteria

- Issue has been identified as a bug report (via triage or `bug` label)
- Issue data gathered (body, comments, sub-issues)

## Exit Criteria

- Fix spec sub-issue existence verified OR missing fix spec reported
- If missing, `analyze-and-spec` task recommended

## Procedure

### Step 1: Determine if Issue Is a Bug Report

Check for bug indicators:

| Indicator | Present? |
|-----------|----------|
| `bug` label on issue | Check labels |
| Bug language in body ("crash", "error", "broken", "steps to reproduce") | Analyze content |
| Title contains bug keywords | Analyze title |

If NOT a bug report, this check does not apply. Report "N/A — not a bug report" and EXIT.

### Step 2: Check for Fix Spec Sub-Issues

```
github_issue_read(method="get_sub_issues", issue_number=N)
```

Examine sub-issues for:

| Signal | Indicates Fix Spec? |
|--------|---------------------|
| Sub-issue title starts with `[SPEC] Fix:` | Yes — fix spec exists |
| Sub-issue has `spec` label | Likely — verify content |
| Sub-issue has `needs-approval` label | Likely — pending fix spec |
| No sub-issues match above | No — fix spec missing |

### Step 3: Report Findings

**If fix spec exists:**
- Report the fix spec issue number
- Note its authorization status (has `needs-approval` or has been approved)
- Continue with normal workflow

**If fix spec is missing:**
- Report "fix spec sub-issue NOT found for bug report"
- Recommend invoking `issue-review --issue N --task analyze-and-spec`
- This is a **blocking condition** for bug report closure per `000-critical-rules.md`

## Edge Cases

| Case | Handling |
|------|----------|
| Bug report is already closed | **Do NOT skip — verify closure is legitimate via merged PR.** See "Closed Bug Report Verification" below |
| Bug report has multiple fix spec sub-issues | Report all; this is valid for multiple root causes |
| Sub-issue exists but is not a fix spec | Ignore for this check; still need a proper fix spec |
| Issue was misclassified as bug | Skip this check; not applicable |

### Closed Bug Report Verification

**🚫 CRITICAL: A closed bug report does NOT mean the fix is already resolved.** Before skipping verification for a closed bug report, verify that the closure is legitimate per the closed-issue verification module.

- See `enforcement/closed-issue-verification.md` for the complete closed-state verification procedure, state_reason classification, and merged PR evidence requirements

## Cross-References

- `issue-review --task analyze-and-spec`: Creates fix spec for bug reports
- `000-critical-rules.md`: Bug reports must have fix spec before closure
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `spec-auditor --task ground-truth`: Adversarial verification model for metadata claims

## Ground-Truth Verification

**Before trusting any fix spec claim, verify it against actual GitHub state.** Do NOT rely on cached sub-issue lists, assumed labels, or claimed STATUS values.

### Verification Checklist

- **Fix spec existence:** Verify each sub-issue exists via `github_issue_read(method=get)` — not just claimed to exist. 404 → MISSING-TRACEABILITY (flag-for-review).
- **Label and STATUS maturity:** Verify labels and STATUS markers match content maturity. Stale labels → STRUCTURE-VIOLATION (auto-fix). Overstated STATUS → CONFLICTING (flag-for-review).
- **Premature closure:** Verify closed sub-issues have merged PR evidence. No merged PR → VERIFICATION-GAP (flag-for-review).

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Closed-issue verification procedure: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`
