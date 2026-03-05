# Environment, Testing & Temporary Files

## Python Environment

- Use `uv sync` for environment setup (creates venv and installs in editable mode). All Python execution via
  `uv run python`. Package ops only via `uv` (`uv sync`, `uv add`) — `pip` prohibited. No `sys.path` hacks or manual
  path additions.
- When `pyproject.toml` changes, purge `.venv` (`rm -rf .venv`) and run `uv sync` as a standalone command (never
  embedded in git hooks, commit scripts, or automated pipelines).
- **Database Safety**: See Production Schema Protection in `03-tool-usage.md` and test schema isolation in
  `07-persistence.md`. NEVER run test/experimental code against the production schema.
- Reusable agent scripts live in `ai_bin/` (project root). Invoke with `uv run python ai_bin/<script>`. See
  `03-tool-usage.md` § `ai_bin/` Agent Tools for conventions.


## Testing

- Use `unittest`. Run from root: `uv run python -m unittest tests/test_filename.py`.
- No regression tests unless explicitly requested. A regression test is a test added to prevent a previously fixed bug
  from reappearing; this rule does not prohibit new unit tests or reproduction scripts required by the current task.
  Temp test artifacts in `tmp/` only.
- Reproduction scripts required by the current task and new unit tests directly supporting an approved task do not
  require a separate GO. Regression tests require explicit user request before creation.
- If `SyntaxWarning: invalid escape sequence` appears in output, stop execution and fix the offending code before
  proceeding.

## Temporary Files

- All temp scripts/data/artifacts in `project_root/tmp/`. Never pollute other directories.
- Project root must stay clean — no root-level temp files.

## Markdown Formatting

- Use triple backtick fenced code blocks for all examples. No backslash escapes or HTML entities for backticks within
  fenced blocks.
