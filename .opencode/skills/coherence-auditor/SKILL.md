---
name: coherence-auditor
description: Audit coherence between guidelines, skills, and AI agent behavior to ensure they work together effectively. Can be used for extraction (identifying skill candidates) and maintenance (detecting drift).
license: MIT
compatibility: opencode
---

# Skill: coherence-auditor

Audits coherence between `.opencode/guidelines/`, `.opencode/skills/`, and AI agent behavior. Identifies procedural workflows for extraction and detects drift over time.

## When to Use

- Creating new skills from guideline content (extraction)
- Ongoing drift detection and verification (maintenance)
- Before approving guideline/skill changes

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

### ⚠️ VERIFICATION STEPS (MANDATORY FIRST)

**Before ANY skill operation, verify:**

1. **Session Init Check:**
   - Has `ai_bin/session_init.py` run?
   - Store: `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL`
   - If NOT run → STOP, run session init FIRST

2. **Codebase Verification:**
   - Is codebase state current?
   - Run: `srclight_codebase_map` or `srclight_index_status`
   - Verify: No stale assumptions from previous sessions

3. **Issue Conflict Check:**
   - Query open `[SPEC]` issues for conflicts
   - Check for superseding/invalidating issues
   - If conflict found → HALT, report conflict

**Exemption Conditions:**
- extract-scan: EXEMPT from issue check (guidelines analysis)
- extract-analyze: EXEMPT from issue check (ranking analysis)
- maintenance-detect: REQUIRES all checks (guidelines/skills modification)
- maintenance-verify: REQUIRES all checks (guidelines/skills modification)

1. **Automatic invocation (mandatory):** This skill is invoked when auditing guideline/skill coherence or when user requests extraction/maintenance audit.

1. **Mode selection:**

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
| HIGH | Duplication ≥2 AND (complexity ≥medium OR tokens ≥200) |
| MEDIUM | Duplication ≥2 OR single-file complexity ≥medium |
| LOW | Single-file, low complexity, small tokens |

## Token Estimation

- Text: ~1.3 tokens per word
- Code blocks: ~1.5 tokens per code token
- Tables: ~4 tokens per cell + structure tokens

## Critical: Fresh-Start Context Preservation

**Temp files are NOT preserved between sessions.**

After creating audit log:

1. Write to `./tmp/coherence-audit-YYYYMMDD-<mode>.md`
1. Attach full content as GitHub Issue comment
1. Delete temp file

**Why:** Fresh-start AI agents cannot access `./tmp/` from previous sessions. GitHub Issue comments ARE preserved.

## Cross-References

- Related skills: `git-workflow` (PR with changes), `guideline-auditor` (verify guideline quality)
- Related guidelines: `.opencode/guidelines/*.md`

## Parent Spec

GitHub Issue #316: Guidelines Audit: Extract Complex Workflows to Skills

## Maintenance Schedule

| Trigger | Mode |
|---------|------|
| Weekly/monthly | maintenance |
| After guideline update | maintenance |
| After skill creation | maintenance |
| Before major release | maintenance |
