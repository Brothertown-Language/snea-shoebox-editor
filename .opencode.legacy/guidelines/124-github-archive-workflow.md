# GitHub Workflow: Archive & Issue Closure

> **See `git-workflow` skill → `cleanup` task for issue closure procedure.**

## ⚠️ ENFORCED: Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

### 🚫 PROHIBITED (ZERO TOLERANCE)

| Prohibition | Why It's Wrong |
|-------------|----------------|
| Close issue immediately after implementation | PR might be rejected |
| Close issue when PR created but not merged | PR might be rejected |
| Close issue when PR submitted for review | PR might be rejected |
| Close issue based on `git pull` | Local fast-forward ≠ GitHub merge |
| Close parent while children open | Child tasks incomplete |

### ✅ REQUIRED: API-Based Merge Verification

**Before closing ANY issue:** Call `github_pull_request_read(method="get")` to verify `merged_at` field exists.

**Before closing ANY parent issue:** Call `github_issue_read(method="get_sub_issues")` to verify all children closed or complete.

**Why `git pull` is insufficient:** Local fast-forward shows `git pull` succeeded — does NOT verify GitHub PR merge status.

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

**Verification fields:**
- `merged_at` (timestamp) — PR was merged
- `state: "closed"` with `merged` attribute — PR closed via merge

**If API shows PR not merged:** Do NOT close the issue. Report and wait for confirmation.

---

## ⚠️ ENFORCED: Parent/Child Issue Closure

> **See `git-workflow` skill → `cleanup` task for complete workflow including sub-issue verification.**

**Parent issues MUST NOT be closed while ANY child issues remain open.**

### 🚫 PROHIBITED (ZERO TOLERANCE)

| Prohibition | Why It's Wrong |
|-------------|----------------|
| Close parent while children open | Child tasks incomplete |
| Close parent after PR merge if other children incomplete | Work not done |
| Assume "PR covers everything" when sub-issues exist | Sub-issues may be separate |
| Assume parent status reflects sub-issue status | Must query sub-issues directly |

### ✅ REQUIRED: Sub-Issue Verification

**Before closing ANY parent:** Call `github_issue_read(method="get_sub_issues")` to verify all children closed.

**After closing child addressed by PR:** Verify remaining sub-issues. If empty, close parent. If not empty, STOP and report.

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

## ⚠️ ENFORCED: Closed-Issue Remediation

> **See `git-workflow` skill → `cleanup` task for complete remediation workflow.**

**When a closed issue is targeted for implementation, the agent MUST audit before proceeding.**

### Direct Inspection Required (CRITICAL)

**NEVER rely on comments, changelogs, or memory.**

| Evidence Type | Inspection Method |
|---------------|-------------------|
| Code changes | Read actual files mentioned in spec |
| PR merge state | `github_pull_request_read(method="get")` |
| Branch state | `git log`, `git branch` |
| Database state | Query actual database/tables |

---

## ⚠️ ENFORCED: Superseded Issue Closure

> **See `git-workflow` skill → `cleanup` task for complete superseded workflow.**

**Issues superseded by new issues MUST follow atomic closure workflow.**

### 🚫 PROHIBITED

| Prohibition | Why It's Wrong |
|-------------|----------------|
| Claim future action in closing comment | "New spec will be created" = never created |
| Close without completing workflow | "Close and create new" = must do BOTH NOW |
| Reference issue that doesn't exist | "Replaced by #TBD" = no tracking |

### ✅ REQUIRED: Atomic Workflow

1. Create replacement issue FIRST
2. Note the new issue number
3. Close old issue WITH replacement reference

**New issue MUST exist BEFORE closing old issue.**

---

## Closing Summary (Required)

Before closing any issue (SPEC or Task), the AI agent MUST provide a final summary comment.

### Summary Requirements

- **Summary of Changes**: High-level overview of what was implemented
- **Test Results**: Summary of verification steps (tests run, coverage, manual checks)
- **Impacts**: Any impacts on other issues or project components
- **Superseded/Not Implemented**: Explicitly state if any planned items were superseded, deferred, or intentionally skipped

### When to Close

**Only close after PR merge:**

1. PR has been reviewed
2. PR has been merged by human
3. CI/CD passed (if applicable)
4. THEN close the issue with summary comment

---

*Source: `020-github-workflow.md` and `040-plan-delivery.md` (restructured)*