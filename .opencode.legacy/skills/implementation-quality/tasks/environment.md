# Task: environment

Pattern verification for WHAT runtime. Blast radius: LOW. Invoke before running commands.

## Pattern Table

| Requirement | Guideline Reference |
|-------------|-------------------|
| No Node.js in Python projects | `070-environment.md` - Node.js Prohibition |
| Use `uv run python` for Python | `070-environment.md` - Python Environment |
| Edit `pyproject.toml` directly, then `uv sync` | `070-environment.md` - Package Management |
| No absolute paths in commands | `060-tool-usage.md` - Path Rules |
| Use `./tmp/` for temp files | `060-tool-usage.md` - Temp Files |
| Use `uvx` for standalone tools | `AGENTS.md` - Build / Lint / Test Commands |
| `ruff` for Python linting ONLY | `AGENTS.md` - Build / Lint / Test Commands |
| `pymarkdownlnt` for Markdown linting ONLY | `080-code-standards.md` - Tool Selection |

## Violation Table

| Violation | Correct Action |
|-----------|---------------|
| `npm install` in Python project | Use Python alternatives (`uv`, `ruff`, `pytest`) |
| `python script.py` | Use `uv run python script.py` |
| `pip install package` | Edit `pyproject.toml`, run `uv sync` |
| `cd /home/user/git/repo && command` | Use workdir or relative paths |
| File path `/tmp/file.txt` | Use `./tmp/file.txt` |
| Using `ruff` on `.md` files | Use `pymarkdownlnt` and `mdformat` instead |
| Using `pyright` on `.md` files | Use `pymarkdownlnt` and `mdformat` instead |

## Pre-Lint File Type Verification (MANDATORY)

**⚠️ CRITICAL: Check target files BEFORE running ANY linter.**

**Before running `ruff`, `pyright`, or `vulture`:**

```bash
# Check if target contains markdown files
if echo "$TARGET" | grep -qE '\.md$|guidelines/|\.opencode/'; then
    echo "VIOLATION: Python linters cannot run on markdown files"
    echo "Use: uvx pymarkdownlnt scan -r <path>"
    echo "Use: uvx mdformat <path>"
    exit 1
fi
```

**Before running `pymarkdownlnt` or `mdformat`:**

```bash
# Check if target contains Python files
if echo "$TARGET" | grep -qE '\.py$|src/|test/'; then
    echo "VIOLATION: Markdown linters cannot run on Python files"
    echo "Use: uvx ruff check --fix src/ test/"
    echo "Use: uvx ruff format src/ test/"
    exit 1
fi
```

**Enforcement Pattern:**

1. **ALWAYS check file type before running linter**
2. **ALWAYS run `ruff` ONLY on `.py` files or `src/` and `test/` directories**
3. **ALWAYS run `pymarkdownlnt` and `mdformat` ONLY on `.md` files or documentation directories**
4. **NEVER run both tool types on the same target**

## Invocation

```
/skill implementation-quality --task environment
```

Invoke before:
- Running Python commands
- Installing dependencies
- Running linters/formatters (MANDATORY ENFORCEMENT POINT)
- Creating temp files
- Running scripts

## Pre-Command Checklist

- [ ] Using `uv run python` (not bare `python`)
- [ ] Not using Node.js in Python project
- [ ] Not using absolute paths
- [ ] Temp files go to `./tmp/`
- [ ] Using correct tool for file type (Python vs Markdown) ← **MANDATORY CHECK BEFORE LINT**
- [ ] Target verified: `ruff` only on `.py` files ← **MANDATORY CHECK BEFORE LINT**
- [ ] Target verified: `pymarkdownlnt` only on `.md` files ← **MANDATORY CHECK BEFORE LINT**

## Cross-References

- `070-environment.md` - Environment setup rules
- `060-tool-usage.md` - Tool usage and path rules
- `AGENTS.md` - Build/lint/test commands
- `080-code-standards.md` - Tool Selection by File Type