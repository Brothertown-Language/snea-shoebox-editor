# Task: extract-scan

## Purpose

Scan all `.opencode/guidelines/*.md` files to identify skill extraction candidates during extraction mode.

## Entry Criteria

- Skill invoked with `--mode extraction`
- Guidelines directory exists and is readable

## Exit Criteria

- All guideline files scanned
- Extraction candidates identified and ranked
- Audit report created in `./tmp/coherence-audit-YYYYMMDD-extraction.md`

## Procedure

### Step 1: Scan Guideline Files

Use `pycharm_get_file_text_by_path` to read each guideline file.

### Step 2: Identify Candidates

Scan for:
- Numbered procedural steps (≥4 steps in sequence)
- Directive blocks (✅ ALWAYS / 🚫 NEVER / ⚠️ ASK FIRST / CRITICAL)
- Multi-phase workflows (Phase 1, Phase 2, etc.)
- Cross-references to other procedures
- Tables of workflow steps or decision trees
- Long code example blocks (≥20 lines)

### Step 3: Calculate Metrics

For each candidate:
- Lines of content (excluding headers)
- Estimated token count (≈4 tokens per line)
- Duplication factor (1=single-file, 2=cross-referenced, 3+=multi-file)
- Complexity score (low/medium/high)

### Step 4: Rank Candidates

- **HIGH**: Duplication factor ≥2 AND (complexity ≥medium OR token count ≥200)
- **MEDIUM**: Duplication factor ≥2 OR (single-file with complexity ≥medium)
- **LOW**: Single-file, low complexity, small token count

### Step 5: Output Audit Report

Write to `./tmp/coherence-audit-YYYYMMDD-extraction.md` with:
- Total candidates found
- Priority breakdown (HIGH/MEDIUM/LOW)
- Estimated token savings
- Detailed candidate listing

## Context Required

- Guidelines: `.opencode/guidelines/*.md`
- Related tasks: `extract-analyze` (calculate metrics), `create-report` (attach to issue)