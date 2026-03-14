# Plan: pyproject.toml Dependency Remediation
**Status:** ✔️ Complete  

## Scope
Remove inline PEP 723 `# /// script` dependency block from `ai_bin/guidelines-search` and move
`sentence-transformers` into `pyproject.toml` dev dependencies. Fix the usage docstring to use
`uv run python` (not `uv run --script`). Update guidelines to prohibit inline script deps.

## Steps

### 1. ✔️ Completed — Add `sentence-transformers` to `pyproject.toml` dev group
Add `sentence-transformers` to `[dependency-groups] dev` in `pyproject.toml` so it is managed
exclusively via pyproject.toml.

### 2. ✔️ Completed — Remove `# /// script` block from `ai_bin/guidelines-search`
Remove lines 2–4 (`# /// script` / `# dependencies = [...]` / `# ///`) from the script.

### 3. ✔️ Completed — Fix usage docstring in `ai_bin/guidelines-search`
Change `uv run --script ai_bin/guidelines-search` → `uv run python ai_bin/guidelines-search`
in the docstring (line 9).

### 4. ✔️ Completed — Update guidelines to prohibit inline PEP 723 script deps
Add a rule to `guidelines/03-tool-usage.md` (or `04-environment.md`) explicitly forbidding
`# /// script` inline dependency blocks in `ai_bin/` scripts; all deps must be in `pyproject.toml`.

### 5. ✔️ Completed — Run `uv sync` to install updated deps
Verify `uv sync` succeeds with the new dep in place.

### 6. ✔️ Completed — Smoke-test `guidelines-search` in BM25-only mode (no model download)
Run `uv run python ai_bin/guidelines-search --bm25 approval` to confirm the script runs correctly
without the inline dep block.

### 7. ✔️ Completed — Update memory.md with task outcome

### 8. ✔️ Completed — Archive this plan
