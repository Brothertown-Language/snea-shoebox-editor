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
| `diagnose` | Systematic bug diagnosis workflow | ≈400 |
| `fix` | Minimal targeted fix after diagnosis | ≈350 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill systematic-debugging` — Overview only
- `/skill systematic-debugging --task diagnose` — Diagnose a bug
- `/skill systematic-debugging --task fix` — Apply minimal fix
- `/skill systematic-debugging --task completion` — Invoke when workflow halts at any point

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

## Live Verification: Hypothesis Evidence (MANDATORY)

**🚫 CRITICAL: When this skill forms a hypothesis about a bug's root cause, it MUST verify the hypothesis against live code/runtime evidence before proceeding. Hypotheses without verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Hypothesis Claim | Verification Action | Tool Call | Problem Class |
|-----------------|-------------------|-----------|---------------|
| "Bug is in function X" | Verify function X actually exhibits the buggy behavior (trace execution, read source) | `srclight_get_symbol(name="X")` → read implementation | VERIFICATION-GAP |
| "Error caused by missing dependency Y" | Verify dependency Y is actually missing or misconfigured | `srclight_get_callers(symbol_name="Y")` → check usage | CONFLICTING |
| "Code path reaches Z" | Verify actual call path via call graph | `srclight_get_callees(symbol_name="caller")` → trace execution | VERIFICATION-GAP |
| "Fix is minimal — only change file F" | Verify no other files depend on the changed code | `srclight_get_dependents(symbol_name="symbol")` → check blast radius | CONFLICTING |
| "No new issues introduced" | Verify by running tests after fix | `bash` to run `uv run pytest test/` → confirm pass | VERIFICATION-GAP |

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
| Bug not in assumed function | VERIFICATION-GAP | conditional | Broaden search, form new hypothesis |
| Dependency not actually missing | CONFLICTING | conditional | Re-hypothesize root cause |
| Call path doesn't reach target | VERIFICATION-GAP | conditional | Re-trace actual execution path |
| Fix has larger blast radius | CONFLICTING | flag-for-review | HALT — fix may need broader scope |
| Tests fail after fix | VERIFICATION-GAP | flag-for-review | HALT — revert and re-diagnose |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `verification-before-completion` in Cross-References | File exists at `.opencode/skills/verification-before-completion/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` in Cross-References | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-review` in Bug Discovery Guardrail | File exists at `.opencode/skills/issue-review/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `diagnose` | File exists at `.opencode/skills/systematic-debugging/tasks/diagnose.md` | MISSING-TRACEABILITY if missing |
| Task table entry `fix` | File exists at `.opencode/skills/systematic-debugging/tasks/fix.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/systematic-debugging/tasks/completion.md` | MISSING-TRACEABILITY if missing |

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

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including authorization currency and code reference existence. When this skill forms a hypothesis about code behavior, ground-truth verification ensures the referenced code actually exists and behaves as claimed. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

- Related skills: `verification-before-completion` (evidence), `approval-gate` (authorization), `git-workflow` (branch), `issue-review` (analyze-and-spec for bug reports), `spec-auditor` (ground-truth adversarial verification)
- Related guidelines: `050-scope-autonomy.md` (no vibe coding), `090-data-integrity.md` (no synthetic data), `065-verification-honesty.md` (metadata verification extension)
- Related task files: `diagnose.md`, `fix.md`

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `github.platform` environment variable

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.