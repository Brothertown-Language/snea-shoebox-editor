# GitHub Workflow: Archive & Issue Closure

> **See `git-workflow` skill → `cleanup` task for issue closure procedure.**

## Archive Workflow (Completion)

**Archive a spec immediately after PR merge:**
1. All steps marked `☑`
2. PR merged (not just created)
3. Add closing summary comment to issue
4. Close the GitHub Issue (state change only)

⚠️ **CRITICAL**: NEVER edit the issue body when closing. Use comments instead.

---

## ⚠️ ENFORCED: Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

### 🚫 PROHIBITED

1. **NEVER close an issue immediately after implementation**
2. **NEVER close an issue when PR is created but not merged**
3. **NEVER close an issue when PR is submitted for review**
4. **NEVER close an issue based on `git pull` alone** — MUST verify via GitHub API

### ✅ REQUIRED SEQUENCE

| Step | Action | Agent Role |
|------|--------|------------|
| Implementation complete | Create PR with `Fixes #123` | ✅ Agent creates PR |
| PR created | Report URL, HALT | ✅ Agent waits |
| Human merges PR | Merge happens | 🚫 Human ONLY |
| User confirms merge | Call `github_pull_request_read method=get` | ✅ Agent verifies |
| PR state = merged | Close issue | ✅ Agent closes |

### ⚠️ MANDATORY: API-Based Merge Verification

**Before closing ANY issue, the agent MUST call `github_pull_request_read method=get` to verify the PR is merged.**

**MANDATORY Pre-Close Checklist (NO EXCEPTIONS):**

| Step | Action | MUST Result |
|------|--------|-------------|
| **1** | Query sub-issues: `github_issue_read(method="get_sub_issues", issue_number=N)` | `[]` empty or verified all closed |
| **2** | Verify PR merge state: `github_pull_request_read(method="get", pullNumber=PR)` | `merged_at` field exists |
| **3** | Close child issues | Only children addressed by merged PR |
| **4** | Re-query parent sub-issues | Verify all children now closed |
| **5** | Close parent | Only if ALL children closed |

**⚠️ CRITICAL: Step 1 is MANDATORY before closing ANY issue - parent or child.**

```python
# MANDATORY: Before closing ANY issue
def before_close_issue(issue_number: int, pr_number: int):
    # Step 1: Query sub-issues (MANDATORY for ALL issues)
    children = github_issue_read(method="get_sub_issues", issue_number=issue_number)
    
    if children:
        # Parent with sub-issues - must verify all children closed
        open_children = [c for c in children if c.state == "open"]
        if open_children:
            # BLOCK: Cannot close parent with open children
            post_warning_comment(issue_number, open_children)
            return  # DO NOT CLOSE
    
    # Step 2: Verify PR merge
    pr = github_pull_request_read(method="get", pullNumber=pr_number)
    if not pr.get("merged_at"):
        report = f"PR #{pr_number} is not yet merged. Cannot close issue."
        return  # DO NOT CLOSE
    
    # Step 3-5: Proceed with closure
    close_issue_with_summary(issue_number)
```

**Why `git pull` is insufficient:**
- Local fast-forward shows `git pull` succeeded
- Does NOT verify the PR merge state in GitHub
- Agent could close issue before human actually merged

**Correct verification sequence:**

```python
# Step 1: User says "pr merged" or similar confirmation
# Step 2: Agent calls GitHub API to verify
github_pull_request_read(method="get", owner="...", repo="...", pullNumber=123)

# Step 3: Check response for merged state
# Look for: "merged_at" field (timestamp) or "state": "closed" with merge

# Step 4: Only AFTER API confirms merge, close the issue
github_issue_write(method="update", issue_number=456, state="closed", state_reason="completed")
```

**Verification fields:**
- `merged_at` (timestamp) — PR was merged
- `state: "closed"` with `merged` attribute — PR closed via merge

**If API shows PR not merged:**
- Do NOT close the issue
- Report: "PR #123 is not yet merged. Please confirm merge before I close the issue."

**Sequence:**
1. Implement → Create PR → Report PR URL → HALT
2. Human reviews and merges PR
3. User confirms "pr merged"
4. **Call GitHub API to verify PR state** ← MANDATORY STEP
5. Only after PR merge verified → Close the issue

### Why This Matters

- Issues closed before PR merge may need to be reopened if PR is rejected
- Open issues accurately reflect work-in-progress state
- Waiting ensures accurate state tracking

---

## ⚠️ ENFORCED: Parent/Child Issue Closure

**Parent issues MUST NOT be closed while ANY child issues remain open.**

**CRITICAL: When checking if a task is complete, ALWAYS verify sub-issues — NEVER assume parent status reflects sub-issue completion.**

### 🚫 PROHIBITED

1. **NEVER close a parent `[SPEC]` issue when ANY child `[Task]` issues are still open**
2. **NEVER close a parent after PR merge if other child tasks are incomplete**
3. **NEVER assume "the PR covers everything" when sub-issues exist**
4. **NEVER assume parent status reflects sub-issue status — ALWAYS query sub-issues**

### ✅ REQUIRED WORKFLOW

**When working with parent/child issue hierarchies:**

| Step | Action | Issues Affected |
|------|--------|-----------------|
| PR merged for child task | Close corresponding child issue ONLY | Child issue only |
| Check remaining children | Verify all children closed | No action yet |
| All children closed? | Close parent with summary | Parent issue |

### Example Workflow

```
SPEC #100 (parent)
├── Task #101: Phase 1 - Database schema
├── Task #102: Phase 2 - API endpoints
└── Task #103: Phase 3 - UI components

PR merges for Phase 1 → Close #101 ONLY
#100 remains open (children #102, #103 pending)

Later, PR merges for Phase 2 → Close #102 ONLY
#100 remains open (child #103 pending)

Later, PR merges for Phase 3 → Close #103 AND #100 (all children done)
```

### Exception: All Children Completed

**When ALL child issues are completed by a single PR merge:**

1. Close the child issue corresponding to the PR
2. **ALSO close the parent issue** (all children are now complete)
3. Add summary comment to the parent explaining all work is complete

**Example:** If PR #150 fixes both #102 and #103 (the last remaining children), close BOTH child issues AND the parent #100 after merge.

### Why This Matters

- **Parent issues track overall progress** across all phases
- **Premature parent closure loses visibility** into remaining work
- **Stakeholders need to see open issues** for incomplete work
- **GitHub sub-issue view shows** which children remain

### Sub-Issue Double-Check (MANDATORY)

**After closing child issues addressed by PR, ALWAYS verify remaining sub-issues before closing parent.**

**Critical Rules:**
1. **NEVER close parent while children remain open**
2. **Always query for sub-issues before closing parent**
3. **Log warnings for orphaned children**
4. **Close children BEFORE closing parent**

### After Closing a Child Issue

**ALWAYS check for remaining open children:**

1. Call `github_issue_read method=get_sub_issues` on the parent issue
2. If the result is NOT empty (children remain open) → STOP, do NOT close parent
3. If the result IS empty (all children closed) → Close parent with summary comment

---

## ⚠️ ENFORCED: Parent Closure Pre-Check (Agent Intelligence Required)

**Before closing ANY parent issue, the agent MUST perform intelligent verification.**

### Pre-Close Checklist

**Before closing a parent `[SPEC]` issue, the agent MUST:**

| Step | Action |
|------|--------|
| **1** | Query sub-issues: `github_issue_read(method="get_sub_issues", issue_number=<parent>)` |
| **2** | Classify each sub-issue (closed/completed/superseded/incomplete) |
| **3** | All children closed/completed/superseded → ✅ Close parent |
| **4** | Any child open + incomplete → 🚫 POST warning, DO NOT close |

### Classification Rules

| Sub-Issue State | Evidence Required |
|-----------------|-------------------|
| Closed as "completed" | `state_reason: "completed"` |
| Closed as "not planned" | `state_reason: "not_planned"` + explanation comment |
| Superseded by another issue | "Superseded by #N" link in comments + verify #N exists |
| Work done but forgot to close | PR linked in body/comments + verify PR merged |

### Warning Post (If Blocked)

```markdown
🤖 ⚠️ **Cannot Close Parent — Open Sub-Issues Detected**

This parent issue cannot be closed because the following sub-issue(s) remain incomplete:

- #N: [Title] — [state, labels, status]

**To close this parent:**
1. Complete the remaining sub-issue(s)
2. Close each sub-issue when work is complete
3. Or close sub-issue as "not planned" with explanation if intentionally skipped

---
🤖 ⚠️ Blocking by <AgentName> (<ModelID>)
```

### False Positive Prevention

**NOT unimplemented (allow parent closure):**

| Sub-Issue State | Evidence Required |
|-----------------|-------------------|
| Closed as "completed" | `state_reason: "completed"` |
| Closed as "not planned" | `state_reason: "not_planned"` + explanation comment |
| Superseded by another issue | "Superseded by #N" link in comments + verify #N exists |
| Work done but forgot to close | PR linked in body/comments + verify PR merged |

**Legitimately unimplemented (block parent closure):**

| Sub-Issue State | Evidence |
|-----------------|----------|
| Open with "needs-approval" label | Awaiting implementation |
| Open with "in-progress" label | Currently being worked |
| Open, no PR, no superseded link | Work not started or incomplete |

---

## ⚠️ ENFORCED: Closed-Issue Remediation (Pre-Authorization Audit)

**When a closed issue is targeted for implementation via `#N approved`, the agent MUST audit before proceeding.**

### Pre-Authorization Audit (MANDATORY)

**When `#N approved` targets a closed issue:**

1. **Query sub-issues immediately**: `github_issue_read(method="get_sub_issues", issue_number=N)`
2. **Detect violations**: Open sub-issues on closed parent = violation
3. **If NO sub-issues or ALL sub-issues closed**: Proceed to implementation
4. **If ANY sub-issue open**: Execute closed-issue remediation workflow (see below)

### Direct Inspection Requirement (CRITICAL)

**NEVER rely on comments, changelogs, or memory.**

| Evidence Type | Inspection Method | What It Proves |
|---------------|-------------------|----------------|
| **Code changes** | Read actual files mentioned in spec | Implementation exists or doesn't |
| **PR merge state** | `github_pull_request_read(method="get")` | PR was merged or wasn't |
| **Branch state** | `git log`, `git branch` | Commits exist in history |
| **Database state** | Query actual database/tables | Schema/data changes applied |

**FORBIDDEN Evidence Sources:**
- Issue comments (indirect, unverified)
- Memory from previous sessions
- Changelogs/README notes
- Issue body claims (only spec requirements are factual)

### Remediation Actions

| Direct Inspection Result | Correct Action |
|-------------------------|----------------|
| Code exists in codebase as specified | Close sub-issue: `completed` |
| PR exists and `merged_at` is set | Close sub-issue: `completed` |
| No code, no PR, nothing implemented | **Reopen parent** (work not done) |
| Parent closed, no merged PR | **Reopen parent** (premature closure) |
| Superseding issue exists with completed work | Verify superseding issue is complete, then close: `not_planned` |

---

## ⚠️ ENFORCED: Superseded Issue Closure (Without Implementation)

**Issues superseded by new issues MUST follow atomic closure workflow.**

### 🚫 PROHIBITED

1. **NEVER claim future action in a closing comment**
   - ❌ "A new spec will be created"
   - ❌ "This will be replaced by a new issue"
   - ❌ "Follow-up work to be done separately"

2. **NEVER close an issue without completing the claimed workflow**
   - If you say "close and create new", you MUST do BOTH NOW
   - If you can't create the new issue immediately, don't claim you will

3. **NEVER reference a replacement issue that doesn't exist yet**
   - ❌ "Replaced by #TBD" (issue not yet created)
   - ❌ "See new spec" (without issue number)

### ✅ REQUIRED ATOMIC WORKFLOW

| Step | Action | Order |
|------|--------|-------|
| Create new issue | Create the replacement issue FIRST | Step 1 |
| Get issue number | Note the new issue number | Step 2 |
| Close old issue | Add closing comment WITH replacement reference | Step 3 |

**Critical: New issue MUST exist BEFORE closing old issue.**

### Closing Summary for Superseded Issues

**When closing an issue without implementation (superseded/cancelled):**

```
🤖 ✅ **Issue Closing Summary**

- **Reason**: Issue superseded by #<number> / cancelled / obsolete approach
- **Replacement**: #<number> (if applicable)
- **Rationale**: [Why the original issue won't be implemented]
- **Work Done**: [Any partial work or investigation completed]
- **Next Steps**: [Where to find the replacement work]

**NOT IMPLEMENTED**: This issue was closed without implementation.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

---

## Closing Summary (Required)

Before closing any issue (SPEC or Task), the AI agent MUST provide a final summary comment.

### Summary Requirements

- **Summary of Changes**: High-level overview of what was implemented
- **Test Results**: Summary of verification steps (tests run, coverage, manual checks)
- **Impacts**: Any impacts on other issues or project components
- **Superseded/Not Implemented**: Explicitly state if any planned items were superseded, deferred, or intentionally skipped

### Example Closing Comment

```
🤖 ✅ **Issue Closing Summary**
- **Changes**: Implemented the new rate limiting middleware in `pubmed_client.py` and updated `110-http-workflow.md`.
- **Test Results**: All 12 unit tests in `test_rate_limit.py` passed. Manual verification confirmed retry logic works.
- **Impacts**: None on existing issues.
- **Superseded/Not Implemented**: The "Phase 3: Circuit breaker" was deferred to a follow-up issue #165.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### When to Close

**Only close after PR merge:**

1. PR has been reviewed
2. PR has been merged by human
3. CI/CD passed (if applicable)
4. THEN close the issue with summary comment

---

*Source: `020-github-workflow.md` and `040-plan-delivery.md` (restructured)*