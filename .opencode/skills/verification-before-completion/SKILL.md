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

## Invocation

- `/skill verification-before-completion` — Overview only
- `/skill verification-before-completion --task verify` — Verify completion readiness
- `/skill verification-before-completion --task collect` — Collect missing evidence

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked when:
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

## Cross-References

- Related skills: `executing-plans` (implementation), `git-workflow` (branch push), `approval-gate` (authorization)
- Related guidelines: `000-critical-rules.md` (evidence requirements), `142-planning-archive-workflow.md` (success criteria)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces evidence-based verification to prevent premature completion claims.

Key adaptations for OpenCode:
- Integration with existing executing-plans and git-workflow skills
- GitBucket platform support via MCP tools
- Dispatch table integration for automatic invocation
- Structured evidence collection and verification gates