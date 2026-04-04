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
| `ruff` for Python linting | `AGENTS.md` - Build / Lint / Test Commands |
| `pymarkdownlnt` for Markdown linting | `080-code-standards.md` - Tool Selection |

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

## Invocation

```
/skill implementation-quality --task environment
```

Invoke before:
- Running Python commands
- Installing dependencies
- Running linters/formatters
- Creating temp files
- Running scripts

## Pre-Command Checklist

- [ ] Using `uv run python` (not bare `python`)
- [ ] Not using Node.js in Python project
- [ ] Not using absolute paths
- [ ] Temp files go to `./tmp/`
- [ ] Using correct tool for file type (Python vs Markdown)

## Cross-References

- `070-environment.md` - Environment setup rules
- `060-tool-usage.md` - Tool usage and path rules
- `AGENTS.md` - Build/lint/test commands