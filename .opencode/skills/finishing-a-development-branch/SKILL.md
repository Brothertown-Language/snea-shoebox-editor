---
name: finishing-a-development-branch
description: Use when implementation is complete and branch needs final checks before PR. Triggers on: done, finished, ready for PR, implementation complete, branch ready, push changes, final check.
type: technique
license: MIT
compatibility: opencode
---

# Skill: finishing-a-development-branch

## Overview

Branch completion workflow that ensures a feature branch is fully ready for PR creation. Verifies all changes are committed, tested, pushed, and reviewed before the developer creates a PR. Implementation tracks against plan sub-issues, not spec sub-issues. Adapted from the \<UPSTREAM_ORG>/\<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from \<UPSTREAM_ORG>/\<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `prepare` | Prepare branch for PR creation | ~450 |
| `checklist` | Run completion checklist | ~350 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill finishing-a-development-branch` — Overview only
- `/skill finishing-a-development-branch --task prepare` — Prepare branch for PR
- `/skill finishing-a-development-branch --task checklist` — Run completion checklist
- `/skill finishing-a-development-branch --task completion` — Invoke when workflow halts at any point

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (push, compare URL, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when implementation completes on a feature branch, when the user says "done" or "finished" or "ready for PR", or before review-prep task in git-workflow.
2. **Verification-first approach:** All changes must be committed. All tests must pass. All lint/typecheck must pass. Branch must be pushed to remote.
3. **Exit conditions:** Branch is READY when all checklist items pass, compare URL is generated, and agent HALTs to report readiness.
4. **Worktree mandatory:** All feature branches operate in worktrees. If `WORKTREE_PATH` is not set: FATAL ERROR → FLAG DEV → HALT.

## Worktree Mode (MANDATORY)

If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT.** Do not proceed without a valid worktree path.

- All `bash` tool calls use `workdir="{{WORKTREE_PATH}}"`
- All `read`/`edit`/`write`/`glob`/`grep` tool calls prefix paths with `{{WORKTREE_PATH}}/`
- NEVER operate in the main working directory during implementation

## Lazy-Loaded Guidelines

When invoked, this skill requires the following guidelines to be loaded on-demand (they are not permanently loaded):

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` — Required before branch completion verification claims

## Integration with Existing Workflow

### Dispatch Order

```
executing-plans → verification-before-completion → finishing-a-development-branch → review-prep → (PR creation by user)
```

### Plan Hierarchy Context

Implementation tracks against **plan sub-issues**, not spec sub-issues. The hierarchy is: Spec → (linked reference in body) → Plan → Sub-issues. When verifying branch completion, reference the plan issue for tracking status and the spec issue for requirements.

### Git-Workflow Integration

- This skill runs BEFORE review-prep
- review-prep handles squash and push
- finishing-a-development-branch handles quality verification

### PR Creation

- This skill does NOT create PRs
- PR creation requires explicit "create a PR" instruction
- After checklist passes, report readiness and HALT

## Live Verification: Checklist Evidence (MANDATORY)

**🚫 CRITICAL: Each checklist item in the `checklist` task MUST produce a tool-call artifact demonstrating the check was actually performed, not just checked off. Checklist assertions without tool-call evidence are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Checklist Item | Verification Action | Tool Call | Problem Class |
|---------------|-------------------|-----------|---------------|
| "All changes committed" | Verify working tree is clean | `bash` to run `git status` → confirm "nothing to commit" | VERIFICATION-GAP |
| "Tests pass" | Verify by running tests | `bash` to run `uv run pytest test/` → confirm exit code 0 | VERIFICATION-GAP |
| "Lint passes" | Verify by running linter | `bash` to run `uvx ruff check src/ test/` → confirm no errors | VERIFICATION-GAP |
| "Branch pushed to remote" | Verify remote branch exists | `bash` to run `git log origin/<branch>..HEAD` → confirm empty | MISSING-ELEMENT |
| "All files in worktree" | Verify all changed files are under WORKTREE_PATH | `bash` to run `git diff --name-only HEAD~1` → check paths | STRUCTURE-VIOLATION |

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
| Uncommitted changes found | VERIFICATION-GAP | auto-fix | Commit remaining changes |
| Tests failing | VERIFICATION-GAP | flag-for-review | HALT — fix test failures before proceeding |
| Lint errors found | VERIFICATION-GAP | auto-fix | Run `ruff check --fix` and re-verify |
| Branch not pushed | MISSING-ELEMENT | auto-fix | Push branch and re-verify |
| Changes outside worktree | STRUCTURE-VIOLATION | flag-for-review | HALT — investigate, may need worktree re-creation |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `git-workflow` in Cross-References | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `verification-before-completion` in Cross-References | File exists at `.opencode/skills/verification-before-completion/SKILL.md` | MISSING-TRACEABILITY if missing |
| `pr-creation-workflow` in Cross-References | File exists at `.opencode/skills/pr-creation-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `prepare` | File exists at `.opencode/skills/finishing-a-development-branch/tasks/prepare.md` | MISSING-TRACEABILITY if missing |
| Task table entry `checklist` | File exists at `.opencode/skills/finishing-a-development-branch/tasks/checklist.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/finishing-a-development-branch/tasks/completion.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` review-prep task | Task exists at `.opencode/skills/git-workflow/tasks/review-prep.md` | MISSING-TRACEABILITY if missing |

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
| review-prep task missing | MISSING-TRACEABILITY | flag-for-review | git-workflow may have been restructured |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including STATUS markers, labels, and authorization currency. When this skill encounters a checklist "all clear" but the ground-truth model suggests the branch state may be inconsistent, invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

- Related skills: `git-workflow` (branch management), `verification-before-completion` (evidence), `pr-creation-workflow` (PR timing), `spec-auditor` (ground-truth adversarial verification)
- Related guidelines: `000-critical-rules.md` (review-prep required), `060-tool-usage.md` (build/lint commands), `065-verification-honesty.md` (metadata verification extension)
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Fully supported — uses GitBucket compare URL format
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable
