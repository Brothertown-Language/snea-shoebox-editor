---
name: mcp-tool-usage
description: Use when selecting tools for file operations, code search, or any task that could use multiple tool options. Triggers on: which tool, tool priority, MCP, PyCharm, JetBrains, read file, write file, search code, tool selection.
type: reference
license: MIT
compatibility: opencode
---

# MCP Tool Usage

## Overview

Tool Priority Enforcer ensuring all operations use the correct tool according to the five-tier hierarchy. Defines PRIMARY, FALLBACK, and PROHIBITED tools for each operation type. Zero tolerance for `.ipynb` files.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `selection-guide` | Decision trees for Python code, file ops, notebooks | ~500 |

## Invocation

- `/skill mcp-tool-usage --task selection-guide` - Tool selection decision trees
- `/skill mcp-tool-usage` - Overview only

## Five-Tier Tool Priority Hierarchy

```
TIER 1 — PRIMARY: opencode built-in tools (read/write/edit/glob/grep)
TIER 2 — PRIMARY: Domain MCP (srclight, the-notebook-mcp, GitHub MCP)
TIER 3 — PRIMARY: .opencode/tools/ (guidelines, md, memory, py ls/mkpkg)
TIER 4 — FALLBACK: JetBrains MCP (pycharm_*) — only for unique capabilities
TIER 5 — LAST RESORT: Direct CLI (bash)

ABSOLUTE EXCEPTION: .ipynb files → the-notebook-mcp MANDATORY (zero tolerance, no fallback)
```

### TIER 1: opencode Built-in Tools (PRIMARY for basic file ops)

| Operation | Tool |
|-----------|------|
| Read file | `read` |
| Write file | `write` |
| Edit file | `edit` |
| Find files | `glob` |
| Search text | `grep` |

**Exception:** `.ipynb` files — use `the-notebook-mcp` exclusively.

### TIER 2: Domain MCP (PRIMARY for their specialties)

- **srclight**: Python code analysis (search symbols, callers, callees, type hierarchy, tests)
- **the-notebook-mcp**: All notebook operations (zero tolerance, no fallback)
- **GitHub MCP**: Issue/PR operations, branch management, file contents

### TIER 3: .opencode/tools/ Scripts (PRIMARY for their domains)

| Tool | Domain |
|------|--------|
| `guidelines` | Guideline search/read (only tool that parses `.opencode/guidelines/` correctly) |
| `md` | Markdown section operations |
| `py ls` | Python package listing |
| `py mkpkg` | Python package creation |
| `memory` | Session memory management |

### TIER 4: JetBrains MCP (FALLBACK — unique capabilities only)

Semantic rename, code reformat, build project, inspections, run configs, directory tree, create file.

**NOT used for:** basic file reads, writes, edits, searches, or globs — TIER 1 handles those.

### TIER 5: Direct CLI (LAST RESORT)

Bash/shell commands ONLY when no other tool covers the operation or it's inherently a shell operation (git, docker, package management).

## ABSOLUTE EXCEPTION: .ipynb Files

`.ipynb` files are MANDATORY via `the-notebook-mcp`. Zero tolerance, no fallback. Direct access via `read`/`write`/`edit`/`json`/`nbformat`/`sed`/`cat`/`grep`/`jq`/`python` on `.ipynb` files is PROHIBITED and causes corruption.

## Owner Inference Prohibition (ZERO TOLERANCE)

**DO NOT infer GitHub owner from file paths, usernames, or cached values.** Use ONLY values from session-enforcement plugin output (`<github.owner>`, `<github.repo>`).

## Worktree Path Resolution

When `worktree.path` is set, ALL file operations MUST prefix paths with the worktree path. TIER 1 tools (`read`, `edit`, `write`, `glob`, `grep`) resolve relative paths to the **main repo**, NOT the worktree.

| Tool | Wrong (main repo) | Correct (worktree) |
|------|-------------------|---------------------|
| `read` | `read(filePath="src/main.py")` | `read(filePath=f"{worktree.path}/src/main.py")` |
| `edit` | `edit(filePath="src/main.py", ...)` | `edit(filePath=f"{worktree.path}/src/main.py", ...)` |
| `write` | `write(filePath="src/new.py", ...)` | `write(filePath=f"{worktree.path}/src/new.py", ...)` |
| `glob` | `glob(pattern="src/**/*.py")` | `glob(pattern="src/**/*.py", path=worktree.path)` |
| `grep` | `grep(pattern="TODO", path="src/")` | `grep(pattern="TODO", path=f"{worktree.path}/src/")` |

For `bash` tool calls, continue using the `workdir` parameter.

## Cross-References

| Guideline | Section |
|-----------|---------|
| `016-srclight-preference.md` | Srclight vs .opencode/tools hierarchy |
| `060-tool-usage.md` | Tool usage and terminal rules |
| `notebook-operations` skill | Complete notebook zero-tolerance rules |
| Session enforcement plugin | MCP probe at startup |