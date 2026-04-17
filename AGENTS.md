# AGENTS.md — Repository Guidelines for Coding Agents

## Identity Detection (MANDATORY FIRST)

The AI agent must determine its identity from the system prompt on EVERY session:

1. **Detect AI agent and model** from your system context
2. **Report identity** in byline format: `🤖 <AgentName> (<ModelId>) <status-icon> <status>`
3. **Examples**: `🤖 OpenCode (ollama-cloud/glm-5) ✅ completed`, `🤖 OpenCode (ollama-cloud/glm-5) 🔄 working`

**WHY**: Different agents/loaders provide different context. System prompt tells you what you are.

---

## Guidelines Structure

Guidelines are pruned to the absolute minimum. See `.opencode/guidelines/` for:

| Series | Category | Files |
|--------|----------|-------|
| 000-099 | Core Rules | critical-rules, session-enforcement, approval-gate, go-prohibitions, scope-autonomy, tool-usage, environment |
| 200-209 | Error Handling | exception-handling, missing-data, logging-vs-raising |

**Registry of migrated content**: `.opencode/.guidelines/registry.yaml` tracks content moved from guidelines to skills.

---

## Build / Lint / Test Commands

| Task | Command | File Types |
|------|---------|------------|
| Sync dependencies | `uv sync` | - |
| Run all tests | `uv run pytest test/` | - |
| Run one test file | `uv run pytest test/test_filename.py` | - |
| Run one test | `uv run pytest test/test_filename.py::test_function_name` | - |
| Lint + auto-fix | `uvx ruff check --fix src/ test/` | Python ONLY |
| Format | `uvx ruff format src/ test/` | Python ONLY |
| Type check | `uvx pyright src/` | Python ONLY |
| Coverage | `uv run coverage run -m pytest test/ && uv run coverage report` | - |
| Dead code scan | `uvx vulture src/` | Python ONLY |
| Markdown lint | `uvx pymarkdownlnt scan -r .opencode/guidelines/ docs/` | Markdown ONLY |
| Markdown format | `uvx --with mdformat-frontmatter --with mdformat-tables --with mdformat-config --with mdformat-gfm mdformat --number --compact-tables --check .opencode/guidelines/ docs/` | Markdown ONLY |
| Skill enforcement test | `bash .opencode/tests/test-enforcement.sh` | opencode-cli |
| Isolated opencode-cli run | `bash .opencode/tests/with-test-home opencode-cli run '<message>'` | opencode-cli |
| Clean test artifacts | `bash .opencode/tests/with-test-home --clean` | opencode-cli |

**Never** use bare `python`, `python3`, or `pip`. Always prefix with `uv run` for project commands.

**Ruff version sync:** When bumping the ruff version, update BOTH `pyproject.toml` (`[dependency-groups] dev` and `[tool.ruff] required-version`) AND `.pre-commit-config.yaml` (`rev:` for `ruff-pre-commit`) to keep them in sync. The `ruff-pre-commit` rev maps 1:1 to ruff releases (e.g., `v0.11.0` → ruff `0.11.0`).

**Isolated test environment:** The `with-test-home` wrapper isolates opencode-cli XDG state into a project-relative temporary home (`./opencode/tmp/test-home-<timestamp>`), eliminating SQLite session conflicts with the desktop app. This allows skill enforcement tests to run from within an active opencode session.

---

## Project Structure

- `src/`: Application source code
- `test/`: Unit and integration tests
- `docs/`: Documentation and specifications
- `.opencode/`: Skills, guidelines, and agent tools
  - `tools/`: Agent utility scripts (guidelines, md, memory, py, jupyter, etc.)
  - `scripts/`: Session context scripts (session_context.py)
  - `skills/`: Self-contained skills (no guideline dependencies)
  - `guidelines/`: Core zero-tolerance rules only
  - `hooks/`: Git hooks (copied to .git/hooks/ by install-hooks.sh)
  - `plugins/`: TypeScript plugins (session-enforcement.ts, env-loader.ts)
  - `.guidelines/registry.yaml`: Registry of migrated content

---

## Session Context

Two plugins run at session start:

1. **session-init** (`tools/session-init`): Emits session variables silently (owner, repo, platform, hooks)
2. **session_context.py** (`scripts/session_context.py`): Conditionally emits identity + trigger alerts

Session context output includes:

- **Identity section** (always): `GIT_OWNER`, `GIT_REPO`, `GIT_PLATFORM`, credential status
- **Trigger alerts** (when detected): `on_main_branch`, `protected_branch_with_changes`, `pair_mode_resume`, `uncommitted_work`, `stale_stash`, `merge_conflict`, `unpushed_commits`, `orphaned_worktrees`
- **Tier 3 probes** (opt-in via `.opencode-issue-probe`): `open_pr_on_branch`, `ci_failure`, `stale_pr`

Credential status values: `verified` (token exists + API ping succeeds), `present` (token exists, liveness unchecked), `missing` (no token found), `stale` (token rejected by API), `unavailable` (platform unknown).

---

## Pair Mode

When the current branch starts with `pair-`, the agent operates in **dev-pair mode**: working directly in the main project directory alongside the developer, using WIP-commit switching instead of worktrees.

| Branch Pattern | Mode | Working Directory |
|---|---|---|
| `pair-feature/123-xyz` | Dev-pair | Main project dir |
| `pair-spec/456-abc` | Dev-pair | Main project dir |
| `feature/789-xyz` | Autonomous | `.worktrees/` |
| `spec/789-abc` | Autonomous | `.worktrees/` |

Pair mode tasks: `pair-pre-work`, `pair-commit`, `pair-pr-creation`, `pair-cleanup`, `pair-mode-resume`. See `git-workflow` skill for full task documentation.

---

## Boundaries (Critical)

**✅ ALWAYS:**
- Create feature branch BEFORE any filesystem change
- Wait for explicit authorization ("approved" or "go") before implementing
- SILENTLY HALT after completing a task
- Use appropriate tools per five-tier hierarchy (see `mcp-tool-usage` skill)

**✅ Multi-Task Spec Workflow (CRITICAL):**
When parent issue has sub-issues, authorization cascades to ALL sub-issues:

- [ ] User authorizes parent issue
- [ ] Verify parent has sub-issues
- [ ] Authorization cascades to ALL sub-issues
- [ ] Complete ALL phases in sequence (NO HALT between phases)
- [ ] Report ONCE after ALL phases complete
- [ ] HALT ONCE at the end

**Exception:** User explicitly names a phase (e.g., "approved: Phase 2 only") → complete that phase ONLY, then HALT

**🚫 NEVER:**
- Write code/notebooks/configs/tests without approved spec
- Interpret questions as authorization
- Proceed to next task after completing a task — HALT
- Create PRs without explicit "create a PR" instruction
- Use `/tmp/` — only use `./tmp/`
- Assume cached values from previous sessions
- HALT after each phase of multi-task spec (see Multi-Task Spec Workflow above)