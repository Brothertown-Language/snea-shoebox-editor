---
name: receiving-code-review
description: Use when receiving code review feedback on a PR, or when addressing review comments. Triggers on: code review, PR feedback, review comment, address feedback, fix review, respond to review.
type: technique
license: MIT
compatibility: opencode
---

# Skill: receiving-code-review

## Overview

Workflow for responding to code review feedback on pull requests. Ensures all reviewer comments are addressed systematically, changes are minimal and targeted, and no scope creep occurs during review response. Adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `address` | Address all review comments | ≈350 |
| `respond` | Reply to review comments | ≈250 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill receiving-code-review` — Overview only
- `/skill receiving-code-review --task address` — Address review feedback
- `/skill receiving-code-review --task respond` — Reply to comments
- `/skill receiving-code-review --task completion` — Invoke when workflow halts at any point

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when PR receives review comments, user says "address review" or "fix review feedback", or agent detects review comments on PR. NOT automatic — requires user instruction.
2. **Scoping discipline:** Address ONLY what the reviewer requested. No "while I'm here" changes. No refactoring beyond what was asked. No new features added during review.
3. **Exit conditions:** Review response is COMPLETE when all reviewer comments addressed, all replies posted, tests still pass, and branch pushed with changes.

## Anti-Patterns

### 🚫 Scope Creep During Review

```python
# ❌ WRONG: Refactoring while addressing review
# Reviewer asked: "Rename this variable"
# Agent also: Refactored the entire function, changed return type, added logging
```

### ✅ Targeted Review Response

```python
# ✅ CORRECT: Address only what was requested
# Reviewer asked: "Rename this variable"
# Agent: Renamed the variable, nothing else
```

## Integration with Existing Workflow

### Dispatch Order

```
PR review received → receiving-code-review (address) → push changes → (reviewer re-reviews)
```

### Git-Workflow Integration

- Address review comments on existing branch
- Push additional commits (do NOT squash review fixes)
- PR is updated automatically on push

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `issue-operations` (implied by PR comment responses) | File exists at `.opencode/skills/issue-operations/SKILL.md` | MISSING-TRACEABILITY if missing |
| `requesting-code-review` in Cross-References section | File exists at `.opencode/skills/requesting-code-review/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` in Cross-References section | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `address` | File exists at `.opencode/skills/receiving-code-review/tasks/address.md` | MISSING-TRACEABILITY if missing |
| Task table entry `respond` | File exists at `.opencode/skills/receiving-code-review/tasks/respond.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` branch management behavior | Matches actual SKILL.md: push additional commits, no squash of review fixes | CONFLICTING if mismatched |
| `requesting-code-review` review request behavior | Matches actual SKILL.md: `prepare` and `request` tasks | CONFLICTING if mismatched |

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
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |
| Invocation mismatch | CONFLICTING | flag-for-review | Skill may have been updated |

## Cross-References

- Related skills: `requesting-code-review` (requesting review), `git-workflow` (branch management), `issue-operations` (PR comment format and routing via `comment` task)
- Related guidelines: `050-scope-autonomy.md` (no scope creep), `060-tool-usage.md` (commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `github.platform` environment variable

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.