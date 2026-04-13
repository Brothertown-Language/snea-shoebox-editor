# Tool Usage & Terminal Rules

## 0. Lazy-Loaded Guidelines

The following guidelines are loaded on-demand by skills, not permanently in context:

- `065-verification-honesty.md` — Loaded by verification-dependent skills when invoked
- `067-context-completeness.md` — Loaded by issue/PR review skills when invoked

When a skill indicates "Load guideline:" in its pre-conditions, use the `read` tool or `uv run python .opencode/tools/guidelines read` command to load it before proceeding.

## 1. Tool Priority Hierarchy

> **See `mcp-tool-usage` skill for the complete five-tier hierarchy with tool selection tables.**

### Tier Summary

```
TIER 1 — PRIMARY: opencode built-in tools (read/write/edit/glob/grep)
TIER 2 — PRIMARY: Domain MCP (srclight, the-notebook-mcp, GitHub MCP)
TIER 3 — PRIMARY: .opencode/tools/ (guidelines, md, memory, py ls/mkpkg)
TIER 4 — FALLBACK: JetBrains MCP (pycharm_*) — only for unique capabilities
TIER 5 — LAST RESORT: Direct CLI (bash)

ABSOLUTE EXCEPTION: .ipynb files → the-notebook-mcp MANDATORY (zero tolerance, no fallback)
```

### 🚫 PROHIBITED (Hard stop violation)

- ANY direct access to `.ipynb` files (use `the-notebook-mcp` exclusively)
- JetBrains MCP for basic file operations that opencode built-in tools handle (TIER 1 covers read/write/edit/glob/grep for all non-notebook files)

## 1. Guidelines Lookup

### ✅ ALWAYS DO

- **Reading or searching guideline files MUST use `uv run python .opencode/tools/guidelines`** — never raw `open`, `cat`, or `grep` on `.opencode/guidelines/` files.
- `uv run python .opencode/tools/guidelines read <filename>` — print a single guideline file.
- `uv run python .opencode/tools/guidelines search <term>` — search all guideline files for a term.
- `uv run python .opencode/tools/guidelines search <term> --file <filename>` — search within one file.

### ⚠️ ASK FIRST

- Significant edits to core guideline files.

### 🚫 NEVER DO

- Use `open`, `cat`, or `grep` on `.opencode/guidelines/` files directly.

## 2. Path Rules (ZERO TOLERANCE)

### 🚫 NEVER DO

- **ABSOLUTE PATHS ARE FORBIDDEN IN ALL AGENT TERMINAL COMMANDS.** Never pass a path beginning with `/` to any terminal command or tool parameter.
- Never issue a `cd` command. Run all commands from project root using relative paths.
- **NEVER prefix commands with `cd /home/<user>/git/<repo> &&` or any variant.**

### ⚠️ Worktree Path Resolution for File Operation Tools (CRITICAL)

When working in a git worktree (`WORKTREE_PATH` is set), TIER 1 file operation tools (`read`, `edit`, `write`, `glob`, `grep`) do **NOT** have a `workdir` parameter. Relative paths like `src/main.py` resolve to the **main repo**, not the worktree. This causes silent file operation errors — edits go to the wrong file.

**When `WORKTREE_PATH` is set, ALL file operations MUST prefix paths with the worktree path:**

| Tool | Wrong (operates on main repo) | Correct (targets worktree) |
| -- | -- | -- |
| `read` | `read(filePath="src/main.py")` | `read(filePath=f"{WORKTREE_PATH}/src/main.py")` |
| `edit` | `edit(filePath="src/main.py", ...)` | `edit(filePath=f"{WORKTREE_PATH}/src/main.py", ...)` |
| `write` | `write(filePath="src/new.py", ...)` | `write(filePath=f"{WORKTREE_PATH}/src/new.py", ...)` |
| `glob` | `glob(pattern="src/**/*.py")` | `glob(pattern="src/**/*.py", path=WORKTREE_PATH)` |
| `grep` | `grep(pattern="TODO", path="src/")` | `grep(pattern="TODO", path=f"{WORKTREE_PATH}/src/")` |

**When NOT in a worktree** (working in main repo): Relative paths are correct and function as expected.

**For `bash` tool:** Continue using `workdir` parameter (already documented in `using-git-worktrees` skill and `000-critical-rules.md`).

## 3. Temp Files & Cleanliness

### ✅ ALWAYS DO

- All temporary scripts and output files MUST be written ONLY to `./tmp/` (project root). NO OTHER FOLDERS OR PATHS ARE PERMITTED.
- Create the directory if needed: `mkdir -p ./tmp`.
- **Mandatory pre-submit root cleanliness check:** Before calling `submit`, run `uv run python .opencode/tools/file-exists .output.txt` and confirm it is MISSING. If it exists, move it to `./tmp/.output.txt` immediately.
- **ALWAYS clean up temp files after modification tasks are complete.**

### 🚫 NEVER DO

- **ZERO TOLERANCE — NEVER use or access any other folder (e.g., `/tmp/`, `.tmp/`, etc.) for any reason.** Only `./tmp/` is permitted.

## 4. Command Restrictions & Quality

### ✅ ALWAYS DO

- **ALWAYS use `uv run python` to invoke Python.**
- **Fixed sleep value for polling**: Always use a fixed value of `15`.
- **One clear command per invocation.** A short `&&` guard is acceptable.
- **Use built-in Edit/Write tools for file modifications.** For Jupyter notebooks, use `the-notebook-mcp` tools exclusively — see `061-notebook-rules.md`.

### 🚫 NEVER DO

- No `stty` (hangs non-interactive sessions).
- No destructive checkouts (`git checkout` files).
- No embedded scripts via heredocs — use standalone script files in `./tmp/`.
- No repeated or iterative `grep`/`zgrep`/`egrep`/`sed` searches. Use `search_project`.
- **ZERO TOLERANCE — `sed -i`, `printf` (for editing or creation), `echo` redirection, and heredocs are absolutely forbidden.**
- **ZERO TOLERANCE — NEVER edit or modify production data or database seed files.** All changes to production data MUST be performed by a human developer.
- **Multi-line shell loops are strictly forbidden.** Never use `for`, `while`, or `until`.
- **NEVER use `sed` for file edits — it is unreliable for structured formats.** The Edit tool handles escaping and encoding correctly; sed does not.
- **NEVER use `--recursive` with any git submodule command** (e.g., `git submodule update --init --recursive`, `git clone --recursive`). The `--recursive` flag can pull in unintended nested submodules, cause unexpected network traffic, break reproducibility by implicitly resolving submodule chains, and conflict with explicit submodule management. Always use `git submodule update --init` (without `--recursive`) or explicit per-submodule operations.

## 5. Verification & Audit

### ✅ ALWAYS DO

- Verify file/path claims with a tool call (`ls`, `open`, `search_project`).
- If a tool call fails or is inconclusive, retry with a different tool.
- For plan audits, validate only the specific anchor needed for the current phase/step/checklist item.

### 🚫 NEVER DO

- Do not run bulk path-audit sweeps.

## 6. File Renaming

- When renaming a file and the developer does not specify the new name, infer the best semantic name based on the file's actual content and purpose — do not ask for clarification.
