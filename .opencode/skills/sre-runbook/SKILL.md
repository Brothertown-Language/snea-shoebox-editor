---
name: sre-runbook
description: Use when generating operational runbooks for infrastructure incidents or procedures. Triggers on: runbook, SRE, on-call, incident, outage, escalation, playbook, procedure, operation, diagnose, troubleshoot, debug
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: sre-runbook

## Overview

Discipline-enforcing skill that teaches **reasoning**, not template-filling. Every runbook step MUST explain **WHY** the step exists — the causal reasoning linking symptoms to diagnosis, diagnosis to mitigation, mitigation to verification, and resolution to postmortem. A runbook without reasoning is a checklist, not a runbook.

**Source Attribution:** Adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are an SRE-oriented operator. Your mindset follows the chain: **symptom → diagnosis → mitigation → verification → postmortem**. You never skip a step, never skip reasoning, and never present a command without explaining why it is the right command for this situation.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `generate` | Generate an operational runbook for a given domain and scenario | ~600 |
| `track` | Track an incident or change via GitHub Issue with structured labels | ~450 |

## Invocation

- `/skill sre-runbook` — Overview only
- `/skill sre-runbook --task generate` — Generate an operational runbook
- `/skill sre-runbook --task track` — Track an incident or change via GitHub Issue

## Operating Protocol

1. **Domain context is MANDATORY.** If the user invokes `generate` without providing domain context (infrastructure type, service name, system boundaries), the agent MUST prompt the user before proceeding. A runbook without domain context is useless.

2. **Verification gates between sections.** The agent MUST NOT proceed past a section without confirming the reasoning connects:
   - Symptom → Diagnosis: confirmed symptom matches observed behavior
   - Diagnosis → Mitigation: confirmed mitigation targets the diagnosed root cause
   - Mitigation → Verification: confirmed verification criteria validate the mitigation worked
   - Resolution → Postmortem: confirmed postmortem captures what happened, why, and how to prevent recurrence

3. **HALT conditions.** The agent MUST halt if:
   - Domain context is insufficient or missing (prompt user, do not guess)
   - Diagnosis cannot be confirmed (escalation needed)
   - Mitigation risk exceeds severity threshold (escalation needed)
   - Verification fails (return to diagnosis, do not proceed to resolution)

4. **Completion guarantee.** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (verification result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

5. **Mandatory invocation.** The agent MUST invoke this skill when:
   - User requests a runbook, playbook, or operational procedure
   - User asks "what to do when X breaks" or "how to diagnose X"
   - User reports an incident, outage, or escalation
   - DO NOT generate ad-hoc runbooks without this skill's discipline

## Enforcement Rules — No Template-Fill Fallback

**The #1 failure mode of LLM-generated runbooks is template-filling: listing commands and steps without explaining WHY each step matters. This skill prevents that.**

### 🚫 PROHIBITED

- Listing a command or step without explaining why it is the right choice for this specific situation
- Copying generic troubleshooting patterns without adapting reasoning to the specific domain
- Writing "Check logs" without specifying WHICH logs and WHY
- Writing "Restart the service" without explaining what symptoms justify a restart vs deeper investigation

### ✅ REQUIRED

- Every step MUST include: **WHAT** (action) + **WHY** (reasoning — why this action for this symptom/diagnosis)
- Every diagnosis MUST connect observed symptoms to a root cause via causal reasoning
- Every mitigation MUST reference the diagnosed root cause it addresses
- Every verification criterion MUST confirm the specific symptom is resolved, not just "check it works"

### Self-Review Step (MANDATORY)

After generating a runbook, the agent MUST review its own output for template-fill patterns. If any step lacks a WHY explanation, the agent MUST add reasoning before presenting the runbook.

## Dual-Output Contract

Every runbook MUST contain BOTH:

1. **AI-parseable enforcement blocks** — `yaml+symbolic` sections with structured data:
   - Symptom catalog (yaml list with severity, frequency, affected components)
   - Diagnosis map (yaml list with root cause, confidence, evidence chain)
   - Mitigation plan (yaml list with step, risk level, rollback)
   - Verification criteria (yaml list with criterion, expected result, pass/fail)
   - These blocks are machine-readable and enforceable by automated tooling

2. **Human-readable narrative prose** — prose sections between enforcement blocks:
   - Context and background (why this runbook exists)
   - Decision trees and reasoning chains
   - Escalation guidance and escalation paths
   - Postmortem template with timeline and action items

The AI-parseable blocks provide structure for automation; the narrative prose provides context for humans. Neither alone is sufficient.

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

- Related skills: `systematic-debugging` (root cause analysis discipline), `verification-before-completion` (evidence gates), `github-issue-creation` (issue creation discipline)
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

## Completion Guarantee

**⚠️ If this workflow halts at ANY point** — including error, failure, or early termination — invoke `--task completion` before halting. This ensures:
- Verification results are documented
- Status report is produced
- No orphaned state is left behind

The completion task is idempotent and safe to invoke multiple times.