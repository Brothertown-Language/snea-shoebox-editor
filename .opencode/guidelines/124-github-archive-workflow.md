# GitHub Workflow: Archive & Issue Closure

## Archive Workflow (Completion)

### When to Archive

Archive a spec **immediately** after the final phase is approved and the PR is merged:

1. All steps marked `☑`
2. PR merged (not just created)
3. Add closing summary comment to issue
4. Close the GitHub Issue (state change only)

### Archive Process

#### When GitHub MCP Tools Available

1. **All specs use GitHub Issues as the authoritative source** (no local files needed)
2. **Archive process**: Add closing summary comment, then close the GitHub Issue
3. **Issue reference**: Add `ISSUE: https://github.com/<owner>/<repo>/issues/<number>` to the closed issue body if needed

⚠️ **CRITICAL**: NEVER edit the issue body when closing. Adding `STATUS: completed` or `COMPLETED: YYYY-MM-DD` to the body destroys history. Use comments instead.

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

### 🚫 PROHIBITED

1. **NEVER close a parent `[SPEC]` issue when ANY child `[Task]` issues are still open**
2. **NEVER close a parent after PR merge if other child tasks are incomplete**
3. **NEVER assume "the PR covers everything" when sub-issues exist**

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

### After Closing a Child Issue

**ALWAYS check for remaining open children:**

1. Call `github_issue_read method=get_sub_issues` on the parent issue
2. If the result is NOT empty (children remain open) → STOP, do NOT close parent
3. If the result IS empty (all children closed) → Close parent with summary comment

---

## ⚠️ ENFORCED: Superseded Issue Closure (Without Implementation)

**Issues superseded by new issues MUST follow atomic closure workflow.**

### The Problem

When a user says "close this and create a new spec":

1. Agent closes the old issue
2. Agent claims "a new spec will be created" in closing comment
3. Agent STOPS without creating the new spec
4. The promise "will be created" was never kept

**This is a CRITICAL GUIDELINE VIOLATION.**

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

**"Close and Create New" Workflow:**

| Step | Action | Order |
|------|--------|-------|
| Create new issue | Create the replacement issue FIRST | Step 1 |
| Get issue number | Note the new issue number | Step 2 |
| Close old issue | Add closing comment WITH replacement reference | Step 3 |

**Critical: New issue MUST exist BEFORE closing old issue.**

### Atomic Execution Example

**User request:** "Close this and create a new spec for a 'spec-quality' skill"

**CORRECT WORKFLOW:**
```
1. Create new issue #363 with title "[SPEC] Guidelines: ..."
2. Note issue number: #363
3. Close old issue #333 with comment:
   "AI: OpenCode ollama-cloud/glm-5 on behalf of Michael Conrad 🤖 
    **Replaced By:** #363
    
    This issue is superseded by #363 without implementation.
    The approach (static templates) was determined to be incorrect.
    See #363 for the replacement spec."
```

**INCORRECT WORKFLOW:**
```
1. Close old issue #333 with comment:
   "AI: OpenCode ... 
    A new spec will be created separately"  ← WRONG: forward-looking claim
2. STOP  ← WRONG: incomplete workflow
```

### Closing Summary for Superseded Issues

**When closing an issue without implementation (superseded/cancelled):**

```
AI: <AgentName> <ModelID> on behalf of <HumanName> 🤖
✅ **Issue Closing Summary**

- **Reason**: Issue superseded by #<number> / cancelled / obsolete approach
- **Replacement**: #<number> (if applicable)
- **Rationale**: [Why the original issue won't be implemented]
- **Work Done**: [Any partial work or investigation completed]
- **Next Steps**: [Where to find the replacement work]

**NOT IMPLEMENTED**: This issue was closed without implementation.
```

### Why Atomic Execution Matters

1. **Trust**: Agents must not make promises they don't keep
2. **Traceability**: GitHub issues linked immediately, no lost references
3. **Workflow integrity**: "Close and create" is ONE action, not two separate steps
4. **User experience**: User expects both actions completed, not just one

### Enforcement

**spec-auditor skill checks:**

- Does closing comment claim future action without execution?
- Does issue reference a replacement that doesn't exist?
- Is forward-looking language used ("will be created", "to be done") in closing comments?

**If audit fails:** Reopen the issue, create the replacement, then close properly.

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
AI: <AgentName> <ModelID> ✅ **Issue Closing Summary**
- **Changes**: Implemented the new rate limiting middleware in `pubmed_client.py` and updated `110-http-workflow.md`.
- **Test Results**: All 12 unit tests in `test_rate_limit.py` passed. Manual verification confirmed retry logic works.
- **Impacts**: None on existing issues.
- **Superseded/Not Implemented**: The "Phase 3: Circuit breaker" was deferred to a follow-up issue #165.
```

### When to Close

**Only close after PR merge:**

1. PR has been reviewed
2. PR has been merged by human
3. CI/CD passed (if applicable)
4. THEN close the issue with summary comment

---

## Closing Summary (Required)

---

*Source: `020-github-workflow.md` and `040-plan-delivery.md` (restructured)*