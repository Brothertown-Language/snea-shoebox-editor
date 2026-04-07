# STRICT DIRECTIVE MODE — startup root (condensed)

## 1. MANDATORY FIRST STEP: SESSION INIT SCRIPT (BEFORE MCP)

**Before ANY other operations, run the session init script:**

```bash
uv run python ai_bin/session_init.py
```

**Script outputs (store for session duration):**
- `DEV_NAME`: Human collaborator name (for commit trailers)
- `DEV_EMAIL`: Human collaborator email (for commit trailers)
- `GIT_OWNER`: Repository owner (for GitHub MCP API calls)
- `GIT_REPO`: Repository name (for GitHub MCP API calls)
- `GIT_HOOKS_PATH`: Git hooks path (to verify hooks installed)
- `GIT_REMOTE_URL`: Full remote URL (for reference)

**Exit codes:**
- 0: Success - proceed with session
- 1: No remote configured or parse error - cannot proceed with GitHub operations
- 2: Non-GitHub remote - GitHub MCP operations unavailable

---

## 1.1. OWNER INFERENCE PROHIBITION (ZERO TOLERANCE)

**⚠️ DO NOT infer GitHub owner from file paths, usernames, or cached values.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Parsing file paths to extract `$USER` | `/home/<user>/git/...` → `owner=<user>` is INCORRECT |
| Using `$USER` environment variable | Returns local username, NOT GitHub owner |
| Using `git config user.name` | Returns human name, NOT GitHub owner |
| Using cached values from previous sessions | Stale data, violates session-bound requirement |
| Making GitHub MCP calls before running session init | No owner/repo values available |

### ✅ REQUIRED OWNER VALUES

**ONLY use values from `ai_bin/session_init.py` output:**

- `GIT_OWNER` and `GIT_REPO` for ALL `github_*` MCP calls
- `DEV_NAME` and `DEV_EMAIL` for commit trailers
- DO NOT re-run `git config` or derive values from other sources

---

## 2. MCP AVAILABILITY PROBE

**After git config check, probe MCP tool availability:**

1. **Test PyCharm MCP**: Call `pycharm_get_project_modules` or similar
2. **Test GitHub MCP**: Call `github_get_me`
3. **Record results**: Note which MCP toolsets are available/unavailable

### MCP Enforcement Gate

| Scenario | Spec Tracking | File Operations | GitHub Operations |
|----------|---------------|-----------------|-------------------|
| **Both available** | GitHub Issues | PyCharm MCP tools ONLY | GitHub MCP tools ONLY |
| **PyCharm only** | GitHub Issues | PyCharm MCP tools ONLY | N/A (no GitHub MCP) |
| **Neither available** | GitHub Issues via `gh` CLI | Direct file tools with fallback comment | `gh` CLI or web UI |

**PROHIBITED violations:**
- Using `read` tool on project files when PyCharm MCP available → Hard stop
- Using `edit` tool for renames instead of `pycharm_rename_refactoring` → Hard stop
- Using `grep` for project search when PyCharm MCP available → Hard stop
- Creating local spec files instead of GitHub Issues → Hard stop

**Do NOT proceed with any task until MCP availability is confirmed.**

---

## 3. NO RESPONSE WITHOUT INIT (MANDATORY)

**⚠️ ZERO TOLERANCE: The agent MUST NOT respond to user questions or execute tasks before completing session init.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Answering questions before running session init | Missing critical context |
| Creating specs before running session init | No owner/repo for GitHub Issues |
| Running git commands before running session init | Missing human identity for trailers |
| Implementing before running session init | All context missing |

### ✅ REQUIRED SEQUENCE

**Before responding to ANY user input:**

1. Run session init FIRST: `uv run python ai_bin/session_init.py`
2. Store ALL outputs for session duration
3. Probe MCP availability (PyCharm, GitHub)
4. Verify hooks installed
5. THEN and ONLY THEN: Respond to user

---

## 4. HOOK VERIFICATION (MANDATORY)

Before proceeding, verify hooks are installed:

```bash
git config core.hooksPath
# Should output: .githooks
```

Session init script automatically verifies hooks and warns if missing.

If hooks are missing:
- ⚠️ AI agent relays warning to developer
- ⚠️ Developer decides: install hooks or proceed
- ⚠️ Risk: Without hooks, local commits to `main` or `dev` are not blocked

---

## 5. Core Behavior

- Follow user instructions exactly; do not add scope.
- Ask questions only for ambiguity/conflict.
- Production-data execution is forbidden unless explicitly instructed in-session.
- **"Check error" means read code and logs — NEVER run scripts against production.**
- Default initial state is interactive discussion; active persona protocol may override.

---

## 6. Boundaries (Always / Ask first / Never)

### ✅ ALWAYS DO

- Use `uv run python` for all commands.
- **Create a feature branch from `dev` BEFORE any implementation** (see 110-git-branch-first.md). This is MANDATORY — the FIRST action before any edit.
- **When GitHub MCP tools available**: Use the Issue-First strategy. See 120-github-issue-first.md.
- **VERIFY SUB-ISSUES BEFORE IMPLEMENTING**: Call `github_issue_read method=get_sub_issues` on parent issue. See 010-approval-gate.md.
- **Always use GitHub Issues for spec tracking.** Even without GitHub MCP, use `gh` CLI.
- **Prefer MCP tools for project operations.** See 015-mcp-preference.md.
- Use `tmp/` for temp files (`T="./tmp/"`).

### ⚠️ ASK FIRST

- Any action that deviates from the approved plan/spec.
- Adding new dependencies to `pyproject.toml`.
- Modifying database schemas or core infrastructure.

### 🚫 NEVER DO

- No unauthorized edits/implementation.
- **NEVER write code without an approved spec.** Bug fixes require a spec BEFORE implementation.
- **NEVER implement without explicit developer authorization.** Creating a spec does NOT authorize implementation.
- **NEVER implement a spec with `needs-approval` label.** SILENTLY HALT and wait for authorization.
- **Questions are NOT authorization to make changes.** Wait for explicit instruction.
- **Analysis and investigation do NOT authorize implementation.** SILENTLY HALT after creating a spec.
- **NEVER create local spec files when GitHub MCP tools are available.**
- **NEVER use direct file tools on project files when PyCharm MCP is available.** See 015-mcp-preference.md.
- **NEVER edit `.ipynb` files directly.** See 061-notebook-rules.md.
- **Commits require direct instruction; merges are HUMAN-ONLY.**
- **NEVER commit directly to main.** Feature-branch workflow is MANDATORY.
- **ZERO TOLERANCE: Never use `/tmp/` (system temp) — ONLY `./tmp/`.**
- **NEVER run scripts against production data.** Production execution requires explicit user instruction.
- **NEVER SWALLOW EXCEPTIONS OR HIDE MISSING DATA.** See 090-data-integrity.md.

---

## 7. Execution Gates (Canonical)

- Any directive starting with `plan` or `spec` is plan-only and never implementation authorization.
- **New specs MUST be created with `needs-approval` label.** SILENTLY HALT and wait for authorization.
- **Before implementing, verify the spec lacks `needs-approval` label.** If present, SILENTLY HALT.
- `revise` means update the issue or plan file ONLY — never make code changes.
- Perform one approved item at a time, then stop.
- Authorization commands: `approved`, `approved: 1`, `approved: 1.2`, `go` — each per-task and revoked after use.
- **`go` means "proceed to the next task or phase" — NOT "merge" or "create PR".**

---

## 8. References (Authoritative Detail)

- `docs/specs/how-to-write-good-spec-ai-agents.md` — master spec methodology
- `docs/specs/spec-flow-control.md` — spec flow control (STATUS format, phases, markers)
- `docs/specs/spec-flow-control-implementation.md` — spec implementation guide