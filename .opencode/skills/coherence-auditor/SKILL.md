---
name: coherence-auditor
description: Use when guidelines or skills are updated, to check consistency between rules and behavior. Triggers on: coherence, consistency, audit guidelines, skill extraction, drift detection, guideline update, skill update.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: coherence-auditor

## Overview

LLM Coherence Auditor ensuring guidelines, skills, and AI agent behavior work together effectively. Identifies procedural workflows for extraction and detects drift over time.

## Persona


## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `extract-scan` | Scan guidelines for skill candidates | ~450 |
| `extract-analyze` | Calculate metrics and rank candidates | ~380 |
| `maintenance-detect` | Detect drift from baseline | ~370 |
| `maintenance-verify` | Verify guideline-skill references | ~310 |
| `create-report` | Generate and attach audit report | ~400 |

## Invocation

- `/skill coherence-auditor --mode extraction` — Scan for extraction candidates
- `/skill coherence-auditor --mode maintenance` — Detect drift from baseline
- `/skill coherence-auditor --task extract-scan` — Load specific task
- `/skill coherence-auditor --task extract-analyze` — Load specific task
- `/skill coherence-auditor --task maintenance-detect` — Load specific task
- `/skill coherence-auditor --task maintenance-verify` — Load specific task
- `/skill coherence-auditor --task create-report` — Load specific task
- `/skill coherence-auditor` — Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is invoked when auditing guideline/skill coherence or when user requests extraction/maintenance audit.

2. **Mode selection:**
   - **Extraction mode**: Use when creating new skills from guideline content
   - **Maintenance mode**: Use for ongoing drift detection and verification

## Drift Patterns

| Pattern | Description |
|---------|------------|
| DUPLICATE-CONTENT | Same procedure in guideline AND skill |
| MISSING-SKILL-REF | Complex procedure without skill reference |
| STALE-SKILL | Skill references outdated guideline section |
| DRIFT-DETECTED | Guideline changed independently of skill |
| ORPHANED-PROCEDURE | Procedure removed from guideline but still in skill |

## Priority Ranking

| Priority | Criteria |
|----------|----------|
| HIGH | Duplication ≥2 AND (complexity ≥medium OR words ≥150) |
| MEDIUM | Duplication ≥2 OR single-file complexity ≥medium |
| LOW | Single-file, low complexity, small word count |

## Word Count Measurement

- Use `wc -w` as the canonical measurement method
- Text: word count via `wc -w`
- Code blocks: word count via `wc -w` (includes code tokens as words)
- Tables: word count via `wc -w`

## Critical: Fresh-Start Context Preservation

**Temp files are NOT preserved between sessions.**

After creating audit log:
1. Write to `./tmp/coherence-audit-YYYYMMDD-<mode>.md`
2. Attach full content as GitHub Issue comment
3. Delete temp file

**Why:** Fresh-start AI agents cannot access `./tmp/` from previous sessions. GitHub Issue comments ARE preserved.

## Cross-References

- Related skills: `git-workflow` (PR with changes), `guideline-auditor` (verify guideline quality)

## Parent Spec

GitHub Issue #316: Guidelines Audit: Extract Complex Workflows to Skills

## Maintenance Schedule

| Trigger | Mode |
|---------|------|
| Weekly/monthly | maintenance |
| After guideline update | maintenance |
| After skill creation | maintenance |
| Before major release | maintenance |