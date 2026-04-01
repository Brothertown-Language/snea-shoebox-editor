# Task: maintenance-detect

## Purpose

Detect drift between guidelines and skills during maintenance mode by comparing current state to baseline.

## Entry Criteria

- Skill invoked with `--mode maintenance`
- Previous baseline exists (from prior audit log)
- Current guidelines and skills available

## Exit Criteria

- Token drift calculated (±% from baseline)
- Duplicate content flagged
- Missing skill references identified
- Report created in `./tmp/coherence-audit-YYYYMMDD-maintenance.md`

## Procedure

### Step 1: Load Baseline

- Previous token count
- Previous skill list
- Previous guideline-skill reference map

### Step 2: Compare Current State

For each skill:
- Verify file exists at `.opencode/skills/<name>/SKILL.md`
- Verify YAML frontmatter valid
- Check for duplicate content in guidelines
- Test reference path from guideline to skill

For each guideline:
- Find all `> **See:** /skill <name>` references
- Verify referenced skill exists
- Verify skill content matches guideline expectation
- Check for missing references (procedures without skill refs)

### Step 3: Identify Drift Patterns

- DUPLICATE-CONTENT: Same procedure in guideline AND skill
- MISSING-SKILL-REF: Complex procedure without skill reference
- STALE-SKILL: Skill references outdated guideline section
- DRIFT-DETECTED: Guideline changed independently of skill
- ORPHANED-PROCEDURE: Procedure removed from guideline but still in skill

### Step 4: Calculate Token Drift

- Previous baseline: N tokens
- Current total: M tokens
- Drift: M - N tokens, percentage: (M-N)/N × 100%
- Flag if deviation >10%

## Context Required

- Guidelines: `.opencode/guidelines/*.md`
- Skills: `.opencode/skills/*/SKILL.md`
- Related tasks: `maintenance-verify` (verify references), `create-report` (output)