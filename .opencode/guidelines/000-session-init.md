# STRICT DIRECTIVE MODE — startup root (condensed)

## 1. MANDATORY FIRST STEP: SESSION INIT SCRIPT (BEFORE MCP)

**Before ANY other operations, run the session init script:**

### Step 1.1: Run Session Init Script

**ALWAYS run this script FIRST:**

```bash
uv run python ai_bin/session_init.py
```

**Script outputs:**
- `DEV_NAME`: Human collaborator name (for commit trailers)
- `DEV_EMAIL`: Human collaborator email (for commit trailers)
- `GIT_OWNER`: Repository owner (for GitHub MCP API calls)
- `GIT_REPO`: Repository name (for GitHub MCP API calls)
- `GIT_HOOKS_PATH`: Git hooks path (to verify hooks installed)
- `GIT_REMOTE_URL`: Full remote URL (for reference)

**Store these values for the session duration.**

**Exit codes:**
- 0: Success - proceed with session
- 1: No remote configured or parse error - cannot proceed with GitHub operations
- 2: Non-GitHub remote - GitHub MCP operations unavailable

**Error handling:**
- Exit code 1: Verify git remote is configured (`git remote add origin <url>`)
- Exit code 2: GitHub MCP operations will not work with non-GitHub remotes

**Why script FIRST:**
- Ensures correct owner extraction from remote URL
- Provides structured output ready for use
- Fails fast before MCP operations begin
- Prevents incorrect owner assumptions in GitHub API calls

---

## 1.1. OWNER INFERENCE PROHIBITION (ZERO TOLERANCE)

**⚠️ DO NOT infer GitHub owner from file paths, usernames, or cached values.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

**These actions are CRITICAL GUIDELINE VIOLATIONS:**

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Parsing file paths to extract `$USER` | `/home/<user>/git/...` → `owner=<user>` is INCORRECT |
| Using `$USER` environment variable | Returns local username, NOT GitHub owner |
| Using `git config user.name` | Returns human name, NOT GitHub owner |
| Using cached values from previous sessions | Stale data, violates session-bound requirement |
| Making GitHub MCP calls before running session init | No owner/repo values available |

### ✅ REQUIRED OWNER VALUES

**ONLY use values from `ai_bin/session_init.py` output:**

```bash
# REQUIRED: Run this FIRST
uv run python ai_bin/session_init.py

# Expected output format:
# DEV_NAME=<human-name>        # For commit trailers
# DEV_EMAIL=<human-email>     # For commit trailers
# GIT_OWNER=<github-owner>          # For GitHub MCP API calls
# GIT_REPO=<github-repo>            # For GitHub MCP API calls
# GIT_HOOKS_PATH=<hooks-path>        # Git hooks location
# GIT_REMOTE_URL=<remote-url>        # Full remote URL
```

**Use these values for SESSION DURATION:**
- `GIT_OWNER` and `GIT_REPO` for ALL `github_*` MCP calls
- `DEV_NAME` and `DEV_EMAIL` for commit trailers
- DO NOT re-run `git config` or derive values from other sources

### Why This Matters

| Incorrect Source | Example | Result |
|------------------|---------|--------|
| File path parsing | `/home/<user>/git/...` | Owner=`<user>` (WRONG) |
| `$USER` variable | `echo $USER` → `<local-user>` | Owner=`<local-user>` (WRONG) |
| `git config user.name` | `git config user.name` → `<human-name>` | Owner=`<human-name>` (WRONG) |
| Hardcoded value | `owner="<hardcoded>"` | Wrong on different machines |
| Cached from previous session | Previous session's `GIT_OWNER` | May be stale |

**CORRECT:** `GIT_OWNER=<owner>` from session init (for `<owner>/<repo>`)

---

---

## 2. MCP AVAILABILITY PROBE

**After git config check, probe MCP tool availability:**

1. **Test PyCharm MCP**: Call `pycharm_get_project_modules` or similar to verify PyCharm tools work
2. **Test GitHub MCP**: Call `github_get_me` to verify GitHub tools work
3. **Discover repository**: Run `git remote -v` to get correct owner/repo from origin. Extract owner/repo from the origin URL and store for all subsequent GitHub API calls. NEVER assume or hardcode repository owner/name.
4. **Record results**: Note which MCP toolsets are available/unavailable and store owner/repo values
5. **Loop Detection Check**: If MCP probe succeeds but no subsequent tool invocation occurs within 2 message turns, HALT and report potential task loop (see `150-task-loop-prevention.md`)

### Repository Discovery (MANDATORY)

**Use values from session init script:**

The `ai_bin/session_init.py` script extracts owner and repo from the remote URL and stores them for use in GitHub MCP calls.

**Script output:**
```
GIT_OWNER=<owner>
GIT_REPO=<repo>
```

**Error handling (handled by script):**
- If `git remote -v` fails or returns no output → Script exits with code 1
- If remote is not GitHub (e.g., GitLab, Bitbucket) → Script exits with code 2
- If origin remote doesn't exist → Script exits with code 1

### MCP Enforcement Gate

**After MCP probe, enforce tool selection based on availability:**

| Scenario | Spec Tracking | File Operations | GitHub Operations |
|----------|---------------|-----------------|-------------------|
| **Both available** | GitHub Issues | PyCharm MCP tools ONLY | GitHub MCP tools ONLY |
| **PyCharm only** | GitHub Issues | PyCharm MCP tools ONLY | N/A (no GitHub MCP) |
| **Neither available** | GitHub Issues via `gh` CLI | Direct file tools with `# FALLBACK: PyCharm MCP unavailable` comment | `gh` CLI or web UI |

**PROHIBITED violations:**
- Using `read` tool on project files when PyCharm MCP is available → Hard stop
- Using `edit` tool for renames instead of `pycharm_rename_refactoring` → Hard stop
- Using `grep` for project search when PyCharm MCP is available → Hard stop
- Creating local spec files instead of GitHub Issues → Hard stop
- Proceeding past session init without confirming MCP availability

**Fallback acknowledgment**: If PyCharm MCP is unavailable, must explicitly acknowledge fallback mode before using direct file tools.

This probe determines workflow:
- **Both available**: Use GitHub Issues for specs, PyCharm tools for file operations
- **Only PyCharm**: Use GitHub Issues via `gh` CLI for specs, PyCharm tools for files
- **Neither available**: Use direct file tools, GitHub Issues via `gh` CLI for specs

**Do NOT proceed with any task until MCP availability is confirmed AND repository discovered (if GitHub MCP available).**

---

## 3. HOOK VERIFICATION (MANDATORY)

Before proceeding, verify hooks are installed:

```bash
git config core.hooksPath
# Should output: .githooks
```

**Hook Verification in `ai_bin/session_init.py`:**

Session init script automatically verifies hooks and warns if missing:

- **Hooks installed**: Silent (no output)
- **Hooks missing**: Warning to AI agent, includes remediation instructions
- **Behavior**: Continue execution — developer decides remediation

If hooks are missing:
- ⚠️ AI agent relays warning to developer
- ⚠️ Developer decides: install hooks (`./scripts/install-hooks.sh`) or proceed
- ⚠️ Risk: Without hooks, local commits to `main` or `dev` are not blocked

---

## 1. Core behavior

* Follow user instructions exactly; do not add scope.
* Ask questions only for ambiguity/conflict.
* Production-data execution is forbidden unless explicitly instructed in-session.
* **"Check error" means read code and logs — NEVER run scripts against production.** Bug reports, error logs, and diagnostics are for static analysis only. Running the failing script, reproducing the error, or verifying fixes against production is prohibited without explicit authorization.
* Default initial state is interactive discussion; active persona protocol may override.

## 2. Boundaries (Always / Ask first / Never)

### ✅ ALWAYS DO
* Use `uv run python` for all commands.
* **Create a feature branch from `dev` BEFORE any implementation** (see 110-git-branch-first.md). This is MANDATORY — the FIRST action before any edit. NEVER edit files while on `main` or `dev`. No exceptions for "small" changes, docs, tests, or configs.
* **When GitHub MCP tools available**: Use the **Issue-First** strategy. Create GitHub Issues for specs. Use **Sub-issues (Task Lists)** for atomic tasks to establish parent-child hierarchy. **MANDATORY**: All implementation tasks MUST be their own issues, linked via `github_sub_issue_write` using the **Database ID** (not the issue number). See 120-github-issue-first.md.
* **VERIFY SUB-ISSUES BEFORE IMPLEMENTING**: When authorized to implement a SPEC, first call `github_issue_read method=get_sub_issues` on the parent issue. If empty, STOP and report "Cannot implement — no sub-issues found." See 010-approval-gate.md Sub-issue Verification Gate.
* **Always use GitHub Issues for spec tracking.** Even without GitHub MCP, use `gh` CLI for GitHub operations.
* **Prefer MCP tools for project operations.** Use PyCharm MCP tools for file operations, GitHub MCP tools for git/GitHub operations. See 015-mcp-preference.md.
* For Python source analysis, use `ai_bin/py structure`.
* Use `tmp/` for temp files (`T="./tmp/"`).
* Follow the **Spec-Driven Development** methodology (Specify -> Plan -> Tasks -> Implement).
* **Prefer GitHub workflow when MCP tools available.** Use GitHub Issues for planning and PRs for code integration. See `121-github-pr-workflow.md`.

### ⚠️ ASK FIRST
* Any action that deviates from the approved plan/spec.
* Adding new dependencies to `pyproject.toml`.
* Modifying database schemas or core infrastructure.

### 🚫 NEVER DO
* No unauthorized edits/implementation.
* **NEVER write code without an approved spec.** Bug fixes, guideline violations, and any code changes require a spec (GitHub Issue or local file if MCP unavailable) BEFORE implementation. Immediate code fixes are violations.
* **NEVER implement without explicit developer authorization.** Creating a spec does NOT authorize implementation. You MUST receive explicit authorization from the developer before writing any code. No exceptions.
* **NEVER implement a spec with `needs-approval` label.** Check the issue labels before implementing. If `needs-approval` is present, SILENTLY HALT and wait for authorization.
* **Questions are NOT authorization to make changes.** A question like "should I do X?" or "would you like me to X?" is seeking permission, not receiving it. Wait for explicit instruction before acting.
* **Analysis and investigation do NOT authorize implementation.** After creating a spec, SILENTLY HALT and wait for explicit authorization. Do not proceed to implementation automatically.
* **NEVER create local spec files when GitHub MCP tools are available.** Use GitHub Issues as the primary spec tracking mechanism.
* **NEVER use direct file tools (read/write/edit/glob/grep) on project files when PyCharm MCP is available.** See `015-mcp-preference.md` for mandatory PyCharm MCP tool usage.
* **NEVER use bash for file operations (cat/sed/echo) on project files when PyCharm MCP is available.** Use PyCharm MCP tools instead.
* **NEVER edit `.ipynb` files directly.** Raw JSON manipulation, `json.dump`, `write` tool, `sed`, `re.sub`, or any non-MCP method will CORRUPT notebooks. ALWAYS use `the-notebook-mcp` tools. If MCP unavailable, REFUSE notebook operations entirely. See `061-notebook-rules.md`.
* **Commits require direct instruction from the developer; merges are HUMAN-ONLY.** The agent may commit when authorized, but must NEVER merge PRs. "go" means "proceed to the next task or phase" — NOT "merge" or "create PR".
* **NEVER commit directly to main.** The feature-branch workflow is MANDATORY. Even if user says "commit to main", create a feature branch, commit there. Merging is HUMAN-ONLY — even if user says "go" with an open PR, the agent must NOT merge. If all tasks are complete, report summary and HALT.
* **ZERO TOLERANCE: Never use or access `/tmp/` (system temp directory) for any reason — ONLY use or access `./tmp/` for temporary outputs, scripts, and files.**
* **ZERO TOLERANCE: Never access `~/.local/` or tool output files.** Tool outputs are internal artifacts — use MCP tools directly to paginate large results instead of reading cached files.
* **NEVER run scripts, commands, or code against production data or production databases.** "Check error log" means look for log files — never run the script to reproduce or diagnose. "Fix a bug" means fix the code — never test or verify against production. Production execution requires explicit user instruction in-session.
* Do not use shell text-writes (`echo`/`printf`/`tee`/heredoc) for file edits.
* Do not use `sed -i`.
* Do not use `uv run python ai_bin/memory`.
* Never deliver plans inline in the message body.
* Never implement while open questions remain unanswered.
* **NEVER SWALLOW EXCEPTIONS OR HIDE MISSING DATA.** See `090-data-integrity.md` and `200-errors-exception-handling.md` for zero-tolerance rules.

## 3. Execution gates (canonical)

* Any directive starting with `plan` or `spec` is plan-only and never implementation authorization.
* **New specs MUST be created with `needs-approval` label.** The agent must SILENTLY HALT and wait for explicit authorization before implementing.
* **Before implementing, verify the spec lacks `needs-approval` label.** If present, SILENTLY HALT and wait for authorization.
* Plan/Spec directives must produce or update a GitHub Issue, then notify reference + brief summary, then halt.
* Existing plans/specs do not carry authorization across sessions.
* `revise` means update the issue or plan file ONLY — never make code changes for a `revise` command
* Perform one approved item at a time, then stop.
* Plans with open questions must have all questions answered before implementation (see 045-open-questions.md).
* Authorization commands: `approved`, `approved: 1`, `approved: 1.2`, `go` — each authorization is per-task and revoked after use.
* **`go` means "proceed to the next task or phase" — NOT "merge" or "create PR".** If tasks/phases remain in the spec, proceed to the next one. If all tasks are complete, report a summary of changes and HALT. Merging PRs is HUMAN-ONLY. The agent must NEVER merge, even after user says "go" or "approved".
* Directives `specs`, `plans`, or `pending` must list all available top-level specs (GitHub Issues with `[SPEC]` prefix or local `plans/SPEC-*.md` files with STATUS not `completed`), then present a multi-choice user query for selecting which one to implement.

## 4. References (authoritative detail)

* `docs/specs/how-to-write-good-spec-ai-agents.md` — master spec methodology (essay/approach guide).
* `docs/specs/spec-flow-control.md` — spec flow control (STATUS format, phases, markers).
* `docs/specs/spec-flow-control-implementation.md` — spec implementation guide.
* `.opencode/guidelines/045-open-questions.md` — open questions Q&A protocol.