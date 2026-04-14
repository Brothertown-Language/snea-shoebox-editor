---
name: code-size-enforcement
description: Use when writing or modifying code and function length, file size, or cell size may exceed limits. Triggers on: long function, big file, too many lines, size limit, code size, function length, cell size.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Code Size Enforcement

## Overview

Ensures code artifacts stay within size limits for maintainability and readability. Covers Python functions (~100 words), notebook cells (~120 words), and source files (~750 words). Grandfather policy exempts existing files; only new and modified files must comply.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `check-limits` | Measure and verify size limits before commit | ~300 |
| `decompose` | Decompose oversized functions, cells, or files | ~400 |

## Invocation

- `/skill code-size-enforcement --task check-limits` - Check size limits before merge
- `/skill code-size-enforcement --task decompose` - Get decomposition guidance
- `/skill code-size-enforcement` - Overview only

## Size Limits

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | ~100 words | `wc -w` on function body, excluding docstrings, imports, blank lines |
| **Notebook cells** | ~120 words | `wc -w` on cell source, excluding cell header |
| **Source files** | ~750 words | `wc -w` on file, excluding blank lines and file-start comments |

## What Counts and Doesn't Count

**Functions count:** Function body words (code + inline comments), nested functions/classes, multi-line non-docstring string literals.
**Functions don't count:** Docstrings, import statements outside the function, blank lines, type hints on their own lines.

**Notebook cells count:** All words in cell source, comments. NOT: cell metadata or outputs.

**Source files count:** Total words excluding blank lines, module-level docstrings, file-start copyright/license comments.

## Permitted Detection Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `wc -w <file>` | File word count | `wc -w src/module.py` |
| `srclight_symbols_in_file` | Function/class listing | Shows symbol structure and word counts |
| `the-notebook-mcp_notebook_get_outline` | Notebook cell structure | See cell indices and word counts |
| `git diff --stat` | Change size | For modified files |

## Forbidden Patterns

| Pattern | Limit |
|---------|-------|
| Monolithic functions | > ~100 words |
| Monolithic notebook cells | > ~120 words |
| Monolithic files | > ~750 words |
| Deep nesting | > 3 levels |
| God classes/files | Single file importing many unrelated modules |

## Grandfather Policy

Existing files that predate this skill are EXEMPT. New files and modified code in grandfathered files must comply. When modifying a grandfathered file, only the new/modified code is checked.

| Scenario | Enforcement |
|----------|-------------|
| New file created | Must comply with all limits |
| Modified grandfathered file | Only modified code checked |
| Renamed file | Retains grandfather status |
| Deleted and recreated | Treated as NEW file |

## Violation Recovery

1. STOP — do not proceed with the commit/PR
2. Identify the violation (which function/cell/file, current size, limit)
3. Decompose: Extract helpers for functions, split cells, split files into packages
4. Re-check: Verify new structure meets limits
5. Document significant changes in commit/PR message

## Operating Protocol

1. MUST be applied whenever code is written or modified
2. Check size limits before merge/commit
3. Grandfather existing files; enforce on new/modified files only
4. If violation detected: stop, decompose, re-check, then proceed

## Cross-References

| Guideline/Skill | Section | Relationship |
|-----------------|---------|--------------|
| `080-code-standards.md` | Design Principles — ENFORCED UNIVERSALLY | Project-specific conventions |
| `061-notebook-rules.md` | Code Standards for Notebooks | Notebook-specific standards |
| `000-critical-rules.md` | General violation enforcement | Violation handling |
| `programming-principles` skill | SRP, KISS, "No Monoliths" | Decomposition principle guidance — authoritative source for principle definitions |