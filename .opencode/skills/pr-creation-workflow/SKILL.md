---
name: pr-creation-workflow
description: Use when asking about when to create a PR or whether PR creation is authorized. Triggers on: create PR, make PR, pull request, PR timing, when to PR, PR authorized.
type: technique
license: MIT
compatibility: opencode
---

# PR Creation Workflow Skill

## Overview

PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation. "Approved" and "go" authorize implementation ONLY, not PR creation. The developer MUST explicitly say "create a PR" or equivalent.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-pr-checklist` | Mandatory checks before PR creation (squash, changelog, branch state) | ~500 |
| `sub-issue-collection` | Fetch and include sub-issues in PR body for autoclose | ~300 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ~200 |

## Invocation

- `/skill pr-creation-workflow --task pre-pr-checklist` - Run mandatory pre-PR checks
- `/skill pr-creation-workflow --task sub-issue-collection` - Collect sub-issues for PR body
- `/skill pr-creation-workflow --task completion` - Invoke when workflow halts at any point
- `/skill pr-creation-workflow` - Overview only

## Authorization Boundary (CRITICAL)

### What Authorizes Implementation (BUT NOT PR)

| Authorization | Meaning | PR Authorized? |
|---------------|---------|----------------|
| `approved` | Begin implementation | ❌ NO |
| `go` | Proceed to next task | ❌ NO |
| `approved: 1` | Implement Phase 1 | ❌ NO |
| `proceed` | Continue with plan | ❌ NO |

### What Authorizes PR Creation

"create a PR", "make a PR", "push and create PR", "let's get a PR up", "create a pull request", "PR" (bare), "PR #NNN"

## Operating Protocol

1. **After implementation completes:** Report completion, HALT. Do NOT ask about PRs.
2. **When developer says "create a PR":** Run pre-PR checklist, squash, push, create PR, report URL, HALT.
3. **Never merge PRs:** Merging is HUMAN-ONLY operation.
4. **Never create PR without explicit instruction:** "approved" does NOT authorize PR creation.

## Pre-PR Creation Checklist (MANDATORY)

- Squash verification: ONE commit for single-issue branches; N commits (one per item) for work branches
- Work branch detection: Check for `.opencode/tmp/work-*.md` — if present, skip re-squashing
- Work state guard: If `.opencode/tmp/work-*.md` exists, individual feature branch PRs are FORBIDDEN. Only the work branch may have a PR created. HALT if attempting to create an individual PR during work execution.
- Changelog generated (all platforms, no exceptions)
- Branch state: working tree clean
- Push verification: no unpushed commits
- Co-author trailers: both AI and human trailers included
- Issue references: `Fixes #<parent>` for single-task, `Fixes #<parent>` AND `Fixes #<child>` for each sub-issue; for work PRs include `## Work Issues` section listing all implemented issues

## After PR Creation

1. Report URL in chat (NEVER to GitHub Issues)
2. HALT — wait for human to merge
3. Never merge PRs — HUMAN-ONLY operation
4. Delete merged branches AFTER merge confirmation

## Prohibitions

- Create PRs autonomously or after "approved"/"go"
- Ask "Ready for a PR?" or "Should I create a PR?"
- Merge PRs
- Submit PR without squashing to single commit
- Close issues before PR merge

## Live Verification: PR State Claims (MANDATORY)

**🚫 CRITICAL: When this skill verifies PR readiness, it MUST check against live git/GitHub state (not cached or claimed). PR readiness claims without live verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| PR Readiness Claim | Verification Action | Tool Call | Problem Class |
|--------------------|-------------------|-----------|---------------|
| "All changes committed" | Verify working tree is clean | `bash` to run `git status` → confirm "nothing to commit" | VERIFICATION-GAP |
| "Branch pushed to remote" | Verify remote tracking branch exists | `bash` to run `git log origin/<branch>..HEAD` → confirm empty | MISSING-ELEMENT |
| "Squash is clean (single commit)" | Verify commit count on branch | `bash` to run `git log --oneline dev..HEAD \| wc -l` | STRUCTURE-VIOLATION |
| "Changelog generated" | Verify changelog file exists and is current | `glob(pattern="**/CHANGELOG*")` | MISSING-ELEMENT |
| "Co-author trailers present" | Verify commit message contains trailers | `bash` to run `git log -1 --format="%B"` → check trailers | MISSING-ELEMENT |
| "Sub-issues included in PR body" | Verify PR body after creation references sub-issues | `github_pull_request_read(method=get)` → check body | VERIFICATION-GAP |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Uncommitted changes | VERIFICATION-GAP | auto-fix | Commit remaining changes |
| Branch not pushed | MISSING-ELEMENT | auto-fix | Push branch and re-verify |
| Multiple commits not squashed | STRUCTURE-VIOLATION | auto-fix | Squash commits |
| Changelog missing | MISSING-ELEMENT | auto-fix | Generate changelog |
| Co-author trailers missing | MISSING-ELEMENT | auto-fix | Amend commit with trailers |
| Sub-issues not in PR body | VERIFICATION-GAP | auto-fix | Update PR body |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `git-workflow` in Cross-References | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` pr-creation task | Task exists at `.opencode/skills/git-workflow/tasks/pr-creation.md` | MISSING-TRACEABILITY if missing |
| `000-critical-rules.md` in Cross-References | Guideline exists at `.opencode/guidelines/000-critical-rules.md` | MISSING-TRACEABILITY if missing |
| `020-go-prohibitions.md` in Cross-References | Guideline exists at `.opencode/guidelines/020-go-prohibitions.md` | MISSING-TRACEABILITY if missing |
| `010-approval-gate.md` in Cross-References | Guideline exists at `.opencode/guidelines/010-approval-gate.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `pre-pr-checklist` | File exists at `.opencode/skills/pr-creation-workflow/tasks/pre-pr-checklist.md` | MISSING-TRACEABILITY if missing |
| Task table entry `sub-issue-collection` | File exists at `.opencode/skills/pr-creation-workflow/tasks/sub-issue-collection.md` | MISSING-TRACEABILITY if missing |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced task file missing | MISSING-TRACEABILITY | flag-for-review | Task may have been renamed |
| Referenced guideline missing | MISSING-TRACEABILITY | flag-for-review | Guideline may have been renumbered |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including authorization currency. When this skill encounters PR readiness claims that may be based on stale state (e.g., claiming "all changes committed" based on a previous check), it MUST verify against live git state. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

| Guideline | Content |
|-----------|---------|
| `git-workflow` skill `pr-creation` task | Full PR workflow |
| `000-critical-rules.md` | Critical violation: PRs without instruction |
| `020-go-prohibitions.md` | GO does not authorize PR |
| `010-approval-gate.md` | PR timing requirements |
| `git-workflow` skill | Post-merge workflow including issue closure |
| `spec-auditor` (ground-truth subtask) | Adversarial verification of authorization and PR state claims |
| `065-verification-honesty.md` | Metadata verification extension for PR readiness claims |

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.