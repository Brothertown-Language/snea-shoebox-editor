---
name: issue-review
description: Use when reviewing a GitHub issue for comments, audits, or Q/A. Triggers on: review issue, review spec, check issue, issue review, audit issue.
type: orchestrator
license: MIT
compatibility: opencode
---

# Skill: issue-review

## Overview

Unified "review" command for GitHub Issues. Gathers issue data, classifies the review path via content analysis (not label conventions), delegates to appropriate downstream skills, and handles Q/A for non-spec issues. One entry point replaces manual orchestration of comment reading, audit detection, and audit execution.

## Persona

You are an Issue Review Orchestrator. Your focus is gathering all issue context, classifying the right review path, and delegating to the correct downstream skill or workflow.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `gather` | Collect all issue data (body, comments, labels, sub-issues, auth status) | ≈500 |
| `triage` | Two-pass classification: pattern signals + AI verification | ≈600 |
| `audit` | Delegate to `spec-auditor` with triage hints | ≈350 |
| `qa` | Ask clarifying questions one at a time for non-bug, non-spec issues | ≈500 |
| `analyze-and-spec` | Root cause analysis → fix spec auto-creation for bug reports | ≈600 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill issue-review --issue N` — Full review (gather → triage → dispatch)
- `/skill issue-review --issue N --task gather` — Data collection only
- `/skill issue-review --issue N --task triage` — Classification only (requires prior gather)
- `/skill issue-review --issue N --task audit` — Audit delegation only (requires prior triage)
- `/skill issue-review --issue N --task qa` — Q/A mode for non-bug, non-spec issues
- `/skill issue-review --issue N --task analyze-and-spec` — Root cause analysis + fix spec for bug reports
- `/skill issue-review --issue N --task completion` — Invoke when workflow halts at any point
- `/skill issue-review` — Overview only

## Operating Protocol

1. **Mandatory issue parameter:** This skill MUST be invoked with `--issue N` where N is the GitHub Issue number to review.

2. **Automatic workflow:** When invoked without `--task`, the full workflow runs:
   - `gather` → `triage` → path dispatch → recursive sub-issue handling

3. **Comments read first (CRITICAL):** `gather` reads ALL comments before any triage decision, per `067-context-completeness.md`.

4. **No label dependency:** Triage uses content analysis, not `[SPEC]` prefix or other label conventions.

5. **Sub-issue recursion:** When sub-issues exist, the full workflow runs on each sub-issue independently.

## Orchestration Flow

```
review #N
  ├── gather (issue + sub-issues data)
  ├── triage (pattern signals + AI verification → path decision)
  ├── path dispatch:
  │   ├── audit → spec-auditor with hints → exec summary to chat
  │   ├── analyze-and-spec → root cause analysis → fix spec sub-issue → exec summary to chat
  │   ├── qa → one-at-a-time questions in chat → exec summary to issue
  │   ├── just-review → exec summary of current state to chat
  │   └── already-handled → full re-verification → status to chat
  └── recurse for sub-issues (gather → triage → dispatch for each)
```

## Triage Paths

| Path | When | Output Target |
|------|------|---------------|
| `audit` | Content looks like a spec (phases/steps, success criteria, edge cases) | Chat exec summary |
| `analyze-and-spec` | Bug report (crash, error, broken, steps to reproduce) | Fix spec sub-issue linked to bug report |
| `qa` | Non-bug, non-spec issue needing clarification (feature ideas, vague requests) | Chat questions, then issue exec summary |
| `just-review` | Already-audited spec with no new relevant comments | Chat exec summary |
| `already-handled` | Issue appears complete (approved + implemented) | Chat re-verification status |

## Path Dispatch Details

### Audit Path

Invoke `spec-auditor --issue N` with triage hints about which subtasks are relevant:

| Spec Type | Hint |
|-----------|------|
| Simple bug-fix spec | "likely baseline only" |
| Feature with phases | "baseline + concerns likely relevant" |
| Complex multi-phase spec | "all subtasks likely relevant" |

Hints inform but do not override — `spec-auditor` retains its own subtask selection logic.

**CRITICAL:** Audit findings are internal agent guidance — DO NOT post to GitHub comments (per `000-critical-rules.md`). Produce prose exec summary for chat only.

### Analyze-and-Spec Path

Invoke `analyze-and-spec` task for root cause analysis and fix spec auto-creation. See `tasks/analyze-and-spec.md` for full procedure.

**Key behavior:**
- Bug language triggers this path (NOT `qa` anymore)
- Root cause analysis is read-only
- Fix spec sub-issue created and linked to bug report parent
- Smart checkpoint: auto-proceed if clear, HALT if ambiguous
- Fix spec still requires explicit authorization before code changes

### Q/A Path

Ask questions one at a time in chat. Q/A is for non-bug, non-spec issues only.

| Content Type | Q/A Depth |
|--------------|-----------|
| Feature with technical implications | Scope + feasibility |
| Feature idea that could become a spec | Scope + feasibility + offer to scaffold spec |
| Vague or unclear request (not a bug) | Scope clarification only |

On resolution, post exec summary to issue (durable outcomes only, not Q&A chatter). HALT after posting.

### Just-Review Path

Produce prose exec summary of current state including: authorization status, last audit summary, open questions, overall health assessment.

### Already-Handled Path

**Full re-verification — NEVER rely on history, comments, or memory.**

1. Verify GitHub state: issue closed, PR merged, sub-issues status
2. Verify implementation: check that files mentioned in spec exist in codebase
3. Verify tests: check test status for affected areas
4. For bug reports: check if fix spec sub-issue exists and is resolved
5. If fully verified: report "confirmed complete"
6. If gaps found: report what needs attention, suggest re-triage

## Final Report Format (CRITICAL)

All outputs follow prose format per `000-critical-rules.md`:

```
<optional details and analysis>

<exec summary>

<URL if relevant>

🤖 <AgentName> (<ModelId>) <status>
```

No template files. No structured schema output. Prose throughout.

## Lazy-Loaded Guidelines

When invoked, this skill requires the following guidelines to be loaded on-demand (they are not permanently loaded):

- **Load guideline:** `.opencode/guidelines/067-context-completeness.md` — Required before reading issue comments (mandatory per context completeness rule)

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `spec-auditor` in Cross-References and Audit Path | File exists at `.opencode/skills/spec-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References and gather task | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-operations` comment task in Cross-References section | File exists at `.opencode/skills/issue-operations/SKILL.md` | MISSING-TRACEABILITY if missing |
| `systematic-debugging` in Cross-References section | File exists at `.opencode/skills/systematic-debugging/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-operations` in Cross-References section | File exists at `.opencode/skills/issue-operations/SKILL.md` | MISSING-TRACEABILITY if missing |
| `programming-principles` in Cross-References section | File exists at `.opencode/skills/programming-principles/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `gather` | File exists at `.opencode/skills/issue-review/tasks/gather.md` | MISSING-TRACEABILITY if missing |
| Task table entry `triage` | File exists at `.opencode/skills/issue-review/tasks/triage.md` | MISSING-TRACEABILITY if missing |
| Task table entry `audit` | File exists at `.opencode/skills/issue-review/tasks/audit.md` | MISSING-TRACEABILITY if missing |
| Task table entry `qa` | File exists at `.opencode/skills/issue-review/tasks/qa.md` | MISSING-TRACEABILITY if missing |
| Task table entry `analyze-and-spec` | File exists at `.opencode/skills/issue-review/tasks/analyze-and-spec.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` audit delegation behavior | Matches actual SKILL.md: `audit` task delegates to spec-auditor with triage hints | CONFLICTING if mismatched |
| `approval-gate` authorization check behavior | Matches actual SKILL.md: `verify-authorization` task for authorization status | CONFLICTING if mismatched |
| `issue-operations` comment posting behavior | Matches actual SKILL.md: `comment` task format and routing rules | CONFLICTING if mismatched |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |

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
| Ground-truth subtask missing | MISSING-TRACEABILITY | flag-for-review | spec-auditor may not have Phase 1 changes |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including STATUS markers, label accuracy, comment verification, and authorization currency. When this skill's triage relies on comment claims or metadata state, ground-truth verification ensures those claims are accurate. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Live Verification: Comment Claims (MANDATORY)

**🚫 CRITICAL: When this skill reads issue comments and other metadata to make triage decisions, claims found in comments MUST be verified against live GitHub state. Trusting comment assertions without verification is a VERIFICATION-GAP finding per `065-verification-honesty.md`.**

| Metadata Trust Point | Verification Action | Tool Call | Problem Class |
|---------------------|-------------------|-----------|---------------|
| Comment claims "approved" | Verify authorization comment author is developer, scope matches current issue, not superseded | `github_issue_read(method=get_comments)` → filter by `author_association` | CONFLICTING |
| Comment claims "already implemented" | Verify referenced files exist and contain claimed implementation | `glob(pattern="**/file")` or `srclight_get_symbol(name="symbol")` | VERIFICATION-GAP |
| Comment claims "related to #N" | Verify issue #N exists and is relevant | `github_issue_read(method=get, issue_number=N)` | MISSING-TRACEABILITY |
| Comment claims issue status (closed, merged) | Verify actual state via GitHub API | `github_issue_read(method=get)` → check `state`, `state_reason` | CONFLICTING |
| Triage classification based on content claims | Verify content actually matches classification (e.g., "bug report" has bug language) | `github_issue_read(method=get)` → scan body for bug signals | STRUCTURE-VIOLATION |

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
| Authorization from non-developer | CONFLICTING | flag-for-review | HALT — requires real developer authorization |
| Claimed implementation not found | VERIFICATION-GAP | conditional | Re-triage based on actual state |
| Referenced issue does not exist | MISSING-TRACEABILITY | auto-fix | Remove broken reference |
| Claimed status contradicts actual | CONFLICTING | auto-fix | Use actual state for triage |
| Content does not match claimed type | STRUCTURE-VIOLATION | auto-fix | Re-classify based on actual content |

## Cross-References

- `spec-auditor`: Called by `audit` task for spec quality checks (including `ground-truth` adversarial verification subtask)
- `approval-gate`: Referenced for authorization status in `gather`; verifies fix spec for bug reports
- `systematic-debugging`: Invokes `analyze-and-spec` after bug report creation
- `issue-operations`: Called by `analyze-and-spec` for fix spec creation
- `programming-principles`: Principle context for audit path delegation
- `065-verification-honesty.md` (metadata verification extension): Extended "don't trust — verify" principle covering issue metadata

Base directory for this skill: `.opencode/skills/issue-review/`

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.