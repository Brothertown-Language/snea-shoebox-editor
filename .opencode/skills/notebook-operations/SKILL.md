---
name: notebook-operations
description: Use when working with .ipynb Jupyter notebook files for reading, writing, or executing cells. Triggers on: notebook, ipynb, Jupyter, cell, execute cell, kernel, zero tolerance, forbidden operations.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Notebook Operations

## Overview

Ensures ALL notebook operations use `the-notebook-mcp` tools exclusively. This is a ZERO TOLERANCE rule — violations cause notebook corruption, data integrity issues, and broken functionality. If `the-notebook-mcp` is unavailable, ALL notebook operations are FORBIDDEN.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `permitted-operations` | Complete tool reference table (all 25 operations) | ~500 |
| `cell-labels` | Cell labeling convention and metadata handling | ~250 |
| `swap-reorder` | Composed workflows for swap and reorder operations | ~300 |
| `production-data` | Execution restrictions and production data prohibition | ~350 |

## Invocation

- `/skill notebook-operations --task permitted-operations` - Complete tool reference
- `/skill notebook-operations --task cell-labels` - Cell labeling requirements
- `/skill notebook-operations --task swap-reorder` - Cell swap and reorder procedures
- `/skill notebook-operations --task production-data` - Execution restrictions
- `/skill notebook-operations` - Overview only

## Zero Tolerance Rule

ALL notebook operations require `the-notebook-mcp`. Direct file access (read/write/edit/json/nbformat/shell) is PROHIBITED and causes corruption. There is NO fallback.

## Operating Protocol

1. **MCP Required:** Notebook operations are ONLY permitted when `the-notebook-mcp` is available.
2. **No Fallback:** If unavailable, refuse all notebook operations and report to user.
3. **Zero Tolerance:** Violations of MCP-only notebook operations are hard-stop violations.

## ABSOLUTELY FORBIDDEN — NO EXCEPTIONS

| Method | Forbidden Because |
|--------|-------------------|
| `read` tool on `.ipynb` | CORRUPTS NOTEBOOKS |
| `write` tool on `.ipynb` | CORRUPTS NOTEBOOKS |
| `edit` tool on `.ipynb` | CORRUPTS NOTEBOOKS |
| `nbformat` direct access | Bypasses MCP |
| ANY Python one-liner on `.ipynb` | FORBIDDEN |
| ANY Bash command accessing `.ipynb` | FORBIDDEN |
| `json.dump/load` on `.ipynb` | CORRUPTS NOTEBOOKS |
| `sed`/`cat`/`grep`/`jq` on `.ipynb` | FORBIDDEN — use MCP tools |

## Core Tool Mappings

| Operation | Tool |
|-----------|------|
| Read notebook | `the-notebook-mcp_notebook_read` |
| Read cell | `the-notebook-mcp_notebook_read_cell` |
| Edit cell | `the-notebook-mcp_notebook_edit_cell` |
| Add cell | `the-notebook-mcp_notebook_add_cell` |
| Delete cell | `the-notebook-mcp_notebook_delete_cell` |
| Search | `the-notebook-mcp_notebook_search` |
| Get outline | `the-notebook-mcp_notebook_get_outline` |
| Execute cell | `the-notebook-mcp_notebook_execute_cell` ⚠️ |

**⚠️ EXECUTION RESTRICTION:** Notebook execution requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

## When MCP Unavailable

1. STOP immediately
2. REFUSE the task — explain the-notebook-mcp is required
3. No fallback exists — there is NO safe alternative

## Code Standards for Notebooks

ALL code standards in `080-code-standards.md` apply to notebook cells: KISS/DRY, non-monolithic cells (max 50 lines), single-function methods, modularity (complex logic in `.py` modules, not inline).

## Cross-References

| Guideline | Section |
|-----------|---------|
| `061-notebook-rules.md` | Essential directive referencing this skill |
| `060-tool-usage.md` | Tool usage and terminal rules |
| `000-critical-rules.md` | Violation enforcement |