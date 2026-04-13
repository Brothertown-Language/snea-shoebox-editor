---
name: systematic-debugging
description: Use when encountering a bug, error, or unexpected behavior, or before making code changes to fix an issue. Triggers on: bug, error, fix, debug, diagnose, crash, failure, unexpected behavior, vibe debugging.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: systematic-debugging

## Overview

Systematic debugging process that enforces root cause analysis, hypothesis testing, and minimal fixes. Prevents "vibe debugging" — making random changes without understanding the problem. All bugs must be diagnosed before fixing, and fixes must be minimal and targeted.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `diagnose` | Systematic bug diagnosis workflow | ~400 |
| `fix` | Minimal targeted fix after diagnosis | ~350 |

## Invocation

- `/skill systematic-debugging` — Overview only
- `/skill systematic-debugging --task diagnose` — Diagnose a bug
- `/skill systematic-debugging --task fix` — Apply minimal fix

## Operating Protocol

1. **Diagnosis-first approach:** All bugs require diagnosis before fix. Diagnosis must identify root cause. Fix must target root cause, not symptoms. Fix must be minimal — no scope creep.
2. **Mandatory invocation:** The agent MUST invoke this skill when a bug or error is encountered during implementation, or when user reports a bug or says "fix this" or "debug this."
3. **Exit conditions:** Debugging is COMPLETE when root cause identified and documented, fix applied targeting root cause only, verification confirms fix resolves issue, and no new issues introduced.
4. **Authorization separation:** Bug diagnosis does NOT require approval (read-only). Bug FIX requires approval (code change). See `approval-gate` skill for authorization workflow.
5. **Self-correction:** If the agent catches itself editing code without an approved spec, immediately `git checkout -- <affected-files>` and HALT.

## Bug Discovery Guardrail

**⚠️ Finding a bug during diagnosis does NOT authorize fixing it.**

| Action | Requires Authorization? |
|--------|------------------------|
| Diagnosis (read-only analysis) | ❌ No |
| Fix (code change) | ✅ Yes — requires approved spec or explicit "approved"/"go" |
| Creating bug report issue | ❌ No — always permitted |
| Invoking `analyze-and-spec` after bug report | ❌ No — auto-proceeds to fix spec creation |

**After creating a bug report issue, invoke `issue-review --task analyze-and-spec` to perform root cause analysis and create a fix spec sub-issue.** This ensures every bug report has a corresponding fix spec before closure.

### Bug Report → Fix Spec Flow

When the `diagnose` task creates a bug report:

1. Bug report issue created (permitted without authorization)
2. Invoke `/skill issue-review --issue N --task analyze-and-spec` automatically
3. Root cause analysis performed
4. Fix spec sub-issue created and linked to bug report
5. Fix spec requires explicit authorization before code changes proceed

## Enforcement Matrix

| Situation | Action |
|-----------|--------|
| Bug reported, no diagnosis | REQUIRE diagnosis first |
| Diagnosis incomplete | COMPLETE diagnosis before fix |
| Fix targets symptoms, not root cause | REJECT fix, require root cause fix |
| Fix includes unrelated changes | REJECT scope creep |
| Fix is refactoring disguised as bug fix | REJECT, require spec |

## Cross-References

- Related skills: `verification-before-completion` (evidence), `approval-gate` (authorization), `git-workflow` (branch)
- Related guidelines: `050-scope-autonomy.md` (no vibe coding), `090-data-integrity.md` (no synthetic data)
- Related task files: `diagnose.md`, `fix.md`

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable