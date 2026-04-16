---
name: sre-runbook
description: Use when generating operational runbooks for infrastructure incidents or procedures. Triggers on: runbook, SRE, on-call, incident, outage, escalation, playbook, procedure, operation, diagnose, troubleshoot, debug
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: sre-runbook

## Overview

Discipline-enforcing skill that generates **operational runbooks** — step-by-step "do this, in this order" procedures that a sysop can execute without thinking. Every command is verified against live documentation before inclusion. Every value comes from the actual environment, not training data. Every step has ONE definitive path.

**Source Attribution:** Adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are an SRE-oriented operator writing runbooks for sysops under pressure. Your runbooks are **operational procedures, not analysis documents**. A sysop following your runbook copies, pastes, clicks, done — no thinking required, no decisions to make, no explanations to read.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `generate` | Generate an operational runbook for a given domain and scenario | ~900 |
| `track` | Track an incident or change via GitHub Issue with structured labels | ~450 |

## Invocation

- `/skill sre-runbook` — Overview only
- `/skill sre-runbook --task generate` — Generate an operational runbook
- `/skill sre-runbook --task track` — Track an incident or change via GitHub Issue

## Operating Protocol

1. **Environment context is MANDATORY.** Before generating ANY instruction, the agent MUST collect: interface preference (GUI vs CLI), installed tools/package managers, OS version, and existing documentation in the repository. Runbooks without environment context are useless.

2. **Domain context is MANDATORY.** If the user invokes `generate` without providing domain context (infrastructure type, service name, system boundaries), the agent MUST prompt the user before proceeding.

3. **Verification gates between sections.** The agent MUST NOT proceed past a section without confirming the reasoning connects:
   - Symptom → Diagnosis: confirmed symptom matches observed behavior
   - Diagnosis → Mitigation: confirmed mitigation targets the diagnosed root cause
   - Mitigation → Verification: confirmed verification criteria validate the mitigation worked
   - Resolution → Postmortem: confirmed postmortem captures what happened, why, and how to prevent recurrence

4. **HALT conditions.** The agent MUST halt if:
   - Environment context is insufficient or missing (prompt user, do not guess)
   - Domain context is insufficient or missing (prompt user, do not guess)
   - Diagnosis cannot be confirmed (escalation needed)
   - Mitigation risk exceeds severity threshold (escalation needed)
   - Verification fails (return to diagnosis, do not proceed to resolution)
   - Evidence collection fails (cannot reach live docs, cannot query live system) — do NOT silently fall back to training knowledge

5. **Completion guarantee.** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (verification result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

6. **Mandatory invocation.** The agent MUST invoke this skill when:
   - User requests a runbook, playbook, or operational procedure
   - User asks "what to do when X breaks" or "how to diagnose X"
   - User reports an incident, outage, or escalation
   - DO NOT generate ad-hoc runbooks without this skill's discipline

## Enforcement Rules — Operational Runbook Discipline

### 🚫 PROHIBITED

- Presenting multiple alternative paths per operation ("or you can do X instead")
- Including instructions for tools/packages not confirmed available in the target environment
- Using generic placeholder values (``, ``, `dc1`/`dc2`, `example.com`) when environment-specific values are available
- Writing explanations, background, or "why" prose in the operational steps section
- Including conditional "if X then Y" flows that require the sysop to diagnose
- Including more settings than directly solve the problem (kitchen-sink parameter dumps)
- Re-adding content that was removed per user direction
- Referencing CLI commands, GUI paths, or API calls without verifying against live documentation
- Annotating unverified information with "(unverified)" instead of excluding it
- Falling back to training knowledge when live verification fails

### ✅ REQUIRED

- **Single-path rule:** ONE method per operation. GUI-first for operators who prefer GUI; CLI only when no GUI exists or operator prefers CLI. Never present alternatives side by side.
- **Environment context collection:** Before generating any instruction, determine: interface preference, available tools, package manager, OS version.
- **Real-values rule:** Use actual hostnames, IPs, and domain names from the environment reference. Zero generic placeholders. Check existing documentation in the repository first.
- **Prerequisites-first rule:** Every command requiring elevation MUST have the "open elevated..." step before it.
- **Steps-only rule:** Runbook steps are numbered actions and copy-paste commands only. No explanations of why, no background context, no conditional logic.
- **Minimum-necessary rule:** Include only settings directly relevant to the problem. No tangential parameters.
- **Set-and-restore pattern:** Two command blocks only — "set" and "restore defaults." No "check first, then decide" flow.
- **No-resurrection rule:** Once content is removed per user direction, never re-add it in any form.
- **Live-verification rule:** Every CLI command, GUI path, button label, menu structure, and API call MUST be verified against live documentation (vendor docs, `--help` output, `man` pages, official API references) before inclusion. If the agent cannot verify, the information is EXCLUDED — never annotated as "(unverified)."
- **Evidence-anchoring rule:** Include baseline outputs from commands run during evidence collection so the operator can compare against current state.
- **Version-pinning rule:** Record software versions, OS version, and configuration state observed during evidence collection.
- **Last-verified rule:** Include a "Last verified:" timestamp and staleness indicator (e.g., "Verified against Proxmox 8.1 on 2026-04-15").
- **Check-repo-first rule:** Before writing system-specific values (hostnames, IPs, domains, versions), check existing documentation in the same repository. If data exists locally, use it — never guess from training data.

### Self-Review Step (MANDATORY)

After generating a runbook, the agent MUST validate the output against ALL enforcement rules BEFORE presenting it. One-shot correctness is the target — the user should never need to correct the same issue twice.

## Dual-Output Contract

Every runbook MUST contain BOTH:

1. **AI-parseable enforcement blocks** — `yaml+symbolic` sections with structured data:
   - Environment context (interface, tools, versions, OS)
   - Symptom catalog (yaml list with severity, frequency, affected components)
   - Diagnosis map (yaml list with root cause, confidence, evidence chain)
   - Mitigation plan (yaml list with step, risk level, rollback)
   - Verification criteria (yaml list with criterion, expected result, pass/fail)
   - These blocks are machine-readable and enforceable by automated tooling

2. **Human-readable operational procedures** — step-by-step instructions:
   - Prerequisite steps (open elevated session, etc.)
   - Step-by-step actions with copy-paste commands
   - Restore/rollback procedures
   - Verification commands
   - Postmortem template with timeline and action items

The AI-parseable blocks provide structure for automation; the operational procedures provide executable steps for humans. Neither alone is sufficient.

## Worktree Mode

When invoked from a worktree context (`WORKTREE_PATH` is set):

- ALL `bash` tool calls MUST use `workdir` parameter set to `WORKTREE_PATH`
- ALL `read`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `WORKTREE_PATH/`
- ALL `write`/`edit` tool calls MUST prefix `filePath` with `WORKTREE_PATH/`
- Runbook output files MUST resolve within the worktree, not the main repo

**Verification guard:** Before running any command, verify:
```bash
git -C $WORKTREE_PATH rev-parse --show-toplevel
```
If the result does NOT match `WORKTREE_PATH`, HALT and report: "Worktree mismatch — skill is executing in the wrong directory."

If `WORKTREE_PATH` is NOT set, operate normally from the project root.

## Cross-References

- Related skills: `systematic-debugging` (root cause analysis discipline), `verification-before-completion` (evidence gates), `issue-operations` (issue creation discipline)
- Related guidelines: `010-approval-gate.md` (authorization), `000-critical-rules.md` (no implementation without spec)

## Platform Compatibility

- **GitHub:** Use GitHub MCP tools for issue tracking
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces reasoning-first runbook generation to prevent template-filling anti-patterns.

Key adaptations for <AI-Name>:
- Integration with existing systematic-debugging and verification-before-completion skills
- GitBucket platform support via MCP tools
- Dual-output contract (AI-parseable + human-readable)
- Completion guarantee integration
- Environment-context-first discipline (interface preference, tool verification, live docs)
- Operational-procedure focus (steps-only, single-path, real values, minimum-necessary)

## Completion Guarantee

**⚠️ If this workflow halts at ANY point** — including error, failure, or early termination — invoke `--task completion` before halting. This ensures:
- Verification results are documented
- Status report is produced
- No orphaned state is left behind

The completion task is idempotent and safe to invoke multiple times.