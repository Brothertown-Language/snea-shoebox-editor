# Task: maintenance-verify

## Purpose

Verify guideline-skill references remain valid and detect missing references during maintenance mode.

## Entry Criteria

- Drift patterns identified by `maintenance-detect`
- Skills and guidelines available for cross-reference check

## Exit Criteria

- All skill references verified
- Missing references identified
- Report updated with verification results

## Procedure

### Step 1: Find Skill References

For each guideline file:
- Find all `> **See:** /skill <name>` patterns
- Extract skill names from references
- Document reference locations

### Step 2: Verify Referenced Skills Exist

For each reference:
- Check if `.opencode/skills/<name>/SKILL.md` exists
- Check if skill loads correctly (valid YAML frontmatter)
- Flag missing or broken skills

### Step 3: Verify Skill-Content Match

For each reference:
- Check if referenced section exists in skill
- Check if skill content aligns with guideline context
- Flag mismatches or drift

### Step 4: Find Missing References

For procedures without skill refs:
- Identify complex procedures (≥4 steps or ≥3 directives)
- Check if they warrant skill extraction
- Flag as MISSING-SKILL-REF if appropriate

## Context Required

- Related tasks: `maintenance-detect` (input), `create-report` (output)