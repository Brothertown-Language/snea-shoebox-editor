# Task: extract-analyze

## Purpose

Calculate metrics and rank extraction candidates identified during scan phase.

## Entry Criteria

- Extraction candidates identified by `extract-scan`
- Guideline files available for analysis

## Exit Criteria

- Each candidate has metrics (lines, tokens, duplication, complexity)
- Candidates ranked by priority
- Report updated with analysis results

## Procedure

### Step 1: Calculate Word Counts

For each candidate:
- Count words via `wc -w` (excluding headers/blank lines)
- Code blocks: count words via `wc -w`
- Tables: count words via `wc -w`

### Step 2: Determine Duplication Factor

- `1` = Appears in single file
- `2` = Cross-referenced in 2 files
- `3+` = Cross-referenced in 3+ files

### Step 3: Determine Complexity Score

- `low` = Flat list of steps
- `medium` = Conditional branches
- `high` = Multi-phase workflow with conditions

### Step 4: Apply Priority Ranking

| Factor | Weight | Score |
|--------|--------|-------|
| Duplication factor ≥3 | 3× | HIGH |
| Duplication factor =2 | 2× | MEDIUM |
| Complexity = high | 2× | Priority +1 |
| Word count ≥400 | 2× | Priority +1 |
| Single file, simple | 1× | LOW |

## Context Required

- Related tasks: `extract-scan` (input), `create-report` (output)