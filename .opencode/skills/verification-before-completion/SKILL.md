---
name: verification-before-completion
description: Use when claiming a task is complete, marking a step done, or closing an issue. Triggers on: task complete, done, finished, step complete, mark done, verify completion, success criteria.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: verification-before-completion

## Overview

Evidence-based verification workflow that prevents premature completion claims. This skill ensures ALL success criteria are verified with actual evidence before ANY task or phase is marked complete.

**Source Attribution:** Adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are a Verification Gatekeeper. Your focus is ensuring NO completion claim without verified evidence.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify` | Verify all success criteria have evidence | ~700 |
| `collect` | Collect evidence for incomplete criteria | ~500 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~150 |

## Invocation

- `/skill verification-before-completion` — Overview only
- `/skill verification-before-completion --task verify` — Verify completion readiness
- `/skill verification-before-completion --task collect` — Collect missing evidence
- `/skill verification-before-completion --task completion` — Invoke when workflow halts at any point

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (verification result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when:
   - Agent claims "task complete" or "step complete"
   - Agent marks step as ☑ in plan
   - Agent attempts to close issue or create PR
   - DO NOT allow completion claims without evidence

2. **Evidence Requirements:**
   - Every success criterion must have evidence
   - Evidence must be verifiable (logs, test outputs, screenshots)
   - Evidence must be posted to issue or in `./tmp/`
   - No placeholders or "trust me" claims

3. **Exit conditions:** Verification is COMPLETE when:
   - All success criteria have evidence
   - Evidence is posted to plan issue or stored in `./tmp/`
   - HALT and report verification results

## Enforcement Mechanism

Skills MUST enforce evidence before completion — guidelines alone are insufficient.

Before marking complete:
- Are ALL success criteria defined?
- Do ALL criteria have evidence?
- Is evidence verifiable?

Enforcement matrix:
- All criteria verified → ALLOW completion claim
- Some criteria unverified → HALT, require evidence
- No criteria defined → HALT, require success criteria
- Evidence placeholder → HALT, require real evidence

## Lazy-Loaded Guidelines

When invoked, this skill requires the following guidelines to be loaded on-demand (they are not permanently loaded):

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` — Required before any verification claim (mandatory per verification honesty rule)

## Worktree Mode

When invoked from a worktree context (`WORKTREE_PATH` is set):

- ALL `bash` tool calls MUST use `workdir` parameter set to `WORKTREE_PATH`
- ALL `read`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `WORKTREE_PATH/`
- Test/lint/typecheck commands MUST run from the worktree directory
- `./tmp/` paths MUST resolve within the worktree, not the main repo

**Verification guard:** Before running any command, verify:
```bash
git -C $WORKTREE_PATH rev-parse --show-toplevel
```
If the result does NOT match `WORKTREE_PATH`, HALT and report: "Worktree mismatch — skill is executing in the wrong directory."

If `WORKTREE_PATH` is NOT set, operate normally from the project root.

## Live Verification: Completion Claims (MANDATORY)

**🚫 CRITICAL: When this skill verifies completion, it MUST check against live state (not cached or claimed). Completion claims without live verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Completion Claim | Verification Action | Tool Call | Problem Class |
|-----------------|-------------------|-----------|---------------|
| "All success criteria met" | Verify each criterion against actual test/implementation state | `bash` to run tests; `srclight_get_symbol(name="symbol")` for code existence | VERIFICATION-GAP |
| "Tests pass" | Verify by actually running tests, not from memory | `bash` to run `uv run pytest test/` | VERIFICATION-GAP |
| "Files implemented per spec" | Verify files exist and contain expected changes | `glob(pattern="**/file")` + `srclight_get_symbol(name="symbol")` | MISSING-ELEMENT |
| "Issue ready to close" | Verify PR actually merged via GitHub API, not just claimed | `github_pull_request_read(method=get)` → check `merged` field | CONFLICTING |

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
| Criterion claimed met but test fails | VERIFICATION-GAP | conditional | Re-verify, fix implementation if needed |
| Tests claimed passing but actually failing | CONFLICTING | flag-for-review | HALT — do not mark complete |
| Expected files missing | MISSING-ELEMENT | conditional | Implement missing files before completion |
| PR not actually merged | CONFLICTING | flag-for-review | HALT — wait for merge confirmation |

## Cross-References

- Related skills: `executing-plans` (implementation), `git-workflow` (branch push), `approval-gate` (authorization)
- Related guidelines: `000-critical-rules.md` (evidence requirements), `142-planning-archive-workflow.md` (success criteria)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces evidence-based verification to prevent premature completion claims.

Key adaptations for <AI-Name>:
- Integration with existing executing-plans and git-workflow skills
- GitBucket platform support via MCP tools
- Dispatch table integration for mandatory invocation
- Structured evidence collection and verification gates