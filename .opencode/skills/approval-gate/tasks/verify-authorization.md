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

### Step 2.5: Verify Sub-Issues for Multi-Task Specs (CRITICAL)

**This check is MANDATORY before proceeding with implementation.**

```python
# CRITICAL: Check sub-issues to verify task completion
sub_issues = github_issue_read(method="get_sub_issues", issue_number=parent_issue)

# NEVER assume parent status reflects sub-issue status
for sub in sub_issues:
    if sub.state == "open":
        # Sub-issue is open - DO NOT ASSUME IT IS COMPLETE
        # Check if this is the sub-issue we're implementing
        if sub.number == current_sub_issue:
            # This is the one we're implementing - proceed
            continue
        else:
            # Other sub-issue is open and not being implemented
            # HALT - parent cannot be considered complete
            report("Sub-issue #{} is still open. Cannot proceed.", sub.number)
```

**Key Point:** A parent issue marked "closed" does NOT mean all sub-issues are complete. ALWAYS verify sub-issues explicitly.

### Step 2.6: Audit Closed Issues (CRITICAL)

**When targeting a closed issue for implementation, MUST audit before proceeding.**

**WHY THIS MATTERS:**
- Incorrectly-closed parents with open children propagate violations
- Closed issues may have been closed prematurely
- Work may be incomplete despite closure

**Pre-Authorization Audit Workflow:**

```python
# When issue is CLOSED, audit before proceeding
if issue.state == "closed":
    # Step 1: Query sub-issues
    sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)
    
    # Step 2: Detect violations (open sub-issues on closed parent)
    open_children = [s for s in sub_issues if s.state == "open"]
    
    # Step 3: If violations found, inspect project DIRECTLY
    if open_children:
        for child in open_children:
            # DIRECT INSPECTION - NEVER rely on comments/memory
            result = inspect_project_directly(child)
            
            if result == "work_done":
                # Close child with evidence
                github_issue_write(method="update", issue_number=child.number, 
                                   state="closed", state_reason="completed")
                post_comment(child.number, "Auto-remediated: work complete per direct inspection")
            
            elif result == "not_done":
                # Reopen parent - premature closure
                github_issue_write(method="update", issue_number=N,
                                   state="open", state_reason="reopened")
                post_comment(N, "Reopened: sub-issue incomplete")
                HALT("Parent reopened. Awaiting re-authorization.")
            
            elif result == "superseded":
                # Verify superseding issue, close child as not_planned
                github_issue_write(method="update", issue_number=child.number,
                                   state="closed", state_reason="not_planned")
    
    # Step 4: If NO sub-issues or ALL closed, proceed
    else:
        proceed_implementation()
```

**Direct Inspection Methods (MANDATORY):**

| Evidence Type | Method | What It Proves |
|---------------|--------|----------------|
| Code in files | Read files mentioned in spec | Implementation exists |
| PR merged | `github_pull_request_read(method="get")` | PR was merged |
| Commits in history | `git log --oneline --grep="#N"` | Work was committed |
| Database state | Query DB directly | Schema/data changes applied |
| Config changes | Read config files | Configuration changed |

**FORBIDDEN Evidence Sources:**

- Issue comments (indirect, unverified)
- Memory from previous sessions
- Changelogs/README notes
- "I remember doing this"
- Project conventions/assumptions

**When to HALT:**
- Cannot access codebase (permission error)
- Cannot call GitHub API (network/auth failure)
- Spec is ambiguous about deliverables

**HALT message must explain what couldn't be inspected.**

**See `124-github-archive-workflow.md` → "Closed-Issue Remediation" for complete workflow.**

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
