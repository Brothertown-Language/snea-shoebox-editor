# Task: verify-authorization

## Purpose

Check for explicit authorization and needs-approval label status before implementation.

## Entry Criteria

- User says "approved", "go", or similar authorization
- Spec exists as GitHub Issue

## Exit Criteria

- Authorization verified as explicit and for correct issue
- needs-approval label status checked
- Authorization recorded for scope tracking

## Procedure

### Step 1: Verify Authorization Is Explicit

Check that authorization is:

- From user (not agent)
- Explicit ("approved", "go", "approved: N.M")
- For the CURRENT issue (not old session)

### Step 2: Check needs-approval Label

```python
# Get issue labels
issue = github_issue_read(method="get", issue_number=N)
has_label = "needs-approval" in [l["name"] for l in issue["labels"]]

if has_label and explicit_authorization:
    # Label is informational, NOT blocking
    # Proceed with implementation
    # Optionally note: "needs-approval label can be removed"
```

### Step 3: Record Authorization Scope

Authorization applies to:

- Specific issue only
- Current phase/task only
- This session only (no carryover)

## Critical: Approval Pattern Matching Rules

### Approval Patterns (EXPLICIT Authorization)

**These patterns constitute valid authorization:**

| Pattern | Example | Authorization Scope |
|---------|---------|---------------------|
| `approved` (standalone) | `"approved"` | All phases |
| `go` (standalone) | `"go"` | All phases |
| `approved: N` | `"approved: 2"` | Phase N only |
| `approved: N.M` | `"approved: 2.3"` | Phase N, step M only |
| `#N approved` | `"#198 approved"` | Issue #N, all phases |
| `approved #N` | `"approved #198"` | Issue #N, all phases |

**Standalone definition:** The approval word is separated by whitespace or is the only content. It is NOT part of a larger compound word or command.

### Non-Approval Patterns (Informational/Verification)

**These patterns are NOT authorization:**

| Pattern | Example | Why Not Authorization |
|---------|---------|----------------------|
| Compound commands | `"check pr"` | Verification command, not approval |
| Embedded in text | `"approvedcheck pr"` | Part of compound text, not standalone |
| Issue reference + verification | `"#196 approvedcheck pr"` | Verification instruction, not approval |
| Questions | `"should I do X?"` | Seeking permission, not granting |

### Compound Command Handling

**Compound command:** A message containing multiple instructions without proper separation.

| Message | Parsed As | Authorization? |
|---------|-----------|----------------|
| `"check pr"` | Verify PR status | NO - verification |
| `"#196 approvedcheck pr"` | Issue reference + compound text | NO - not explicit approval |
| `"#196 approved"` | Issue #196 approved | YES - standalone |
| `"approved check pr"` | Approval + verification | YES - proper separation |

**Separation Requirements:**
- Space between commands: `"approved check pr"` → approval is standalone
- No space (compound): `"approvedcheck pr"` → NOT standalone approval
- Hyphen/dash separator: `"approved - check pr"` → approval is standalone

### Pattern Matching Algorithm

```
1. Tokenize message by whitespace
2. Check for approval tokens:
   - Exact match: "approved" or "go"
   - Qualified match: "approved:N", "approved:N.M"
   - Issue reference: "#N approved" or "approved #N"
3. Verify token is standalone (separated by whitespace or end-of-message)
4. If standalone approval found → Authorization granted
5. If no standalone approval → Check for compound commands → HALT
```

### Examples

**✅ VALID Authorization:**
- `"approved"` → Standalone, all phases
- `"go"` → Standalone, all phases
- `"approved: 1"` → Phase 1 only
- `"#198 approved"` → Issue 198, all phases
- `"approved #198"` → Issue 198, all phases
- `"approved - check pr"` → Approval + verification (separate)

**❌ NOT Authorization:**
- `"check pr"` → Verification only
- `"#196 approvedcheck pr"` → Compound text, approval not standalone
- `"approvedcheck pr"` → Compound word, not separate commands
- `"should I check pr?"` → Question, seeking permission

## Critical: Explicit Authorization Priority

When user provides explicit authorization, it **OVERRIDES** the needs-approval label.

| Scenario | Action |
|----------|--------|
| `"approved"` (standalone) AND label present | PROCEED - explicit auth wins |
| `"approved"` (standalone) AND no label | PROCEED |
| Compound text (no standalone approval) AND label present | HALT - wait for authorization |
| NO approval AND no label | Check other blockers |

## Context Required

- Guidelines: `010-approval-gate.md`
- Related tasks: `verify-sub-issues`, `verify-codebase`
