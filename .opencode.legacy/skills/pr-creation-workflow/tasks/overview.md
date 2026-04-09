# Task: overview

PR creation workflow enforcer ensuring PRs are created ONLY with explicit developer instruction.

## Core Principle

**PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation.**

## Authorization Boundary (CRITICAL)

### What Authorizes Implementation (BUT NOT PR)

| Authorization   | Meaning                   | PR Authorized? |
|-----------------|---------------------------|----------------|
| `approved`      | Begin implementation      | ❌ NO           |
| `go`            | Proceed to next task      | ❌ NO           |
| `approved: 1`   | Implement Phase 1         | ❌ NO           |
| `approved: 2.3` | Implement Phase 2, Step 3 | ❌ NO           |
| `proceed`       | Continue with plan        | ❌ NO           |

**None of these authorize PR creation.** They authorize implementation only.

### What Authorizes PR Creation

| Authorization           | Valid? |
|-------------------------|--------|
| "create a PR"           | ✅ YES  |
| "pr"                    | ✅ YES  |
| "make a PR"             | ✅ YES  |
| "push and create PR"    | ✅ YES  |
| "let's get a PR up"     | ✅ YES  |
| "create a pull request" | ✅ YES  |

**The developer MUST explicitly say one of these phrases (or unambiguous equivalent).**

## PR Creation Workflow

### After Implementation Completes

1. ✅ Report completion (concise summary)
2. ✅ HALT — do NOT ask about PRs
3. ✅ WAIT for explicit "create a PR" instruction
4. ❌ Do NOT ask "Ready for a PR?" or "Should I create a PR?"
5. ❌ Do NOT create PR automatically

### When Developer Says "create a PR"

1. Rebase on dev
2. Squash commits to SINGLE COMMIT
3. Force push cleaned branch
4. Create PR with `Fixes #N` in description
5. Post PR URL and HALT
6. Wait for human to merge

## Critical Rules

### 🚫 NEVER DO

- Create PR without explicit "create a PR" instruction
- Create PR after "approved" or "go" (those authorize implementation only)
- Create PR after completing implementation (completion does NOT authorize PR creation)
- Ask "Ready for a PR?" or "Should I create a PR?" — just STOP and report completion
- Merge PRs (HUMAN-ONLY)

### ✅ ALWAYS DO

- After completing implementation: report completion concisely, then STOP
- Wait for EXPLICIT "create a PR" instruction
- Only then: squash, push, create PR, report URL, STOP

## After PR Created

1. Post PR URL to issue comment
2. Report completion
3. HALT — wait for human review and merge
4. DO NOT merge PRs (human-only action)

## Cross-References

- Related: `git-workflow` skill (complete git workflow)
- Related: `approval-gate` skill (authorization boundaries)
- Related: AGENTS.md §113 (PR workflow rules)
