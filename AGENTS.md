# AGENTS.md — Repository Guidelines for Coding Agents

## Identity Detection (MANDATORY FIRST)

The AI agent must determine its identity from the system prompt on EVERY session:

1. **Detect AI agent and model** from your system context
2. **Report identity** in byline format: `<AgentName> (<ModelID>)`
3. **Examples**: `OpenCode (ollama-cloud/glm-5)`, `OpenCode Desktop (ollama-cloud/glm-5)`, `Claude (claude-3-5-sonnet)`

**WHY**: Different agents/loaders provide different context. System prompt tells you what you are.

---

## Session Init (Automatic)

Session initialization and skill enforcement are handled automatically by the `session-enforcement` OpenCode plugin (`.opencode/plugins/session-enforcement.ts`). The plugin:

1. Runs `.opencode/scripts/session_init.py` once per session (cached for 5 minutes)
2. Injects session context into the LLM system prompt via `experimental.chat.system.transform`
3. Sets key-value pairs as shell environment variables via `shell.env`
4. Loads skill descriptions from YAML frontmatter in each SKILL.md file at startup (via `loadSkillDescriptions()`)
5. Injects skill enforcement content (1% rule, red-flags table, skill list with "Use when..." descriptions) into the first user message via `experimental.chat.messages.transform`, ensuring agents invoke mandatory workflow skills

**No manual step is required.** The script outputs all values as `KEY=value` pairs — extract them directly, no mapping or interpretation needed. Use `GIT_OWNER` and `GIT_REPO` for EVERY API call.

- `DEV_NAME`: Human collaborator name (for commit trailers)
- `DEV_EMAIL`: Human collaborator email (for commit trailers)
- `GIT_OWNER`: Repository owner (for API calls)
- `GIT_REPO`: Repository name (for API calls)
- `GIT_HOOKS_PATH`: Git hooks path (to verify hooks installed)
- `GIT_REMOTE_URL`: Full remote URL (for reference)
- `GIT_PLATFORM`: Platform type (`github` or `gitbucket`)
- `GITHUB_HTML_URL`: GitHub web UI base URL (if GitHub)
- `GITBUCKET_HTML_URL`: GitBucket web UI base URL (if GitBucket, non-secret)
- `GITBUCKET_HAS_CREDENTIALS`: `true` if credentials configured in `.env`

The output includes a prominent platform banner (`# GITHUB REPOSITORY DETECTED` or `# GITBUCKET REPOSITORY DETECTED`) that makes the platform type unambiguous.

---

## Platform Detection and API Access

The session init script detects git platform from remote URL:

| Platform | Detection | API Access |
|----------|-----------|-----------| 
| GitHub | `github.com` in URL | GitHub MCP tools or `gh` CLI |
| GitBucket | Any other SSH/HTTPS remote | Direct API via `.env` credentials |

### GitBucket API Access

For GitBucket repositories, invoke `gitbucket-api` skill BEFORE using GitBucket Python API.

**GitBucket-specific patterns:**
- Token authentication only (no basic auth)
- Auto-create labels when adding to issues
- GitHub-compatible API v3

---

## MCP Enforcement Gate

**After session init, probe MCP availability:**

1. **PyCharm MCP**: Call `pycharm_get_project_modules`
2. **GitHub MCP**: Call `github_get_me` (if GitHub platform)
3. **Record results**: Note which toolsets are available

| Scenario | Spec Tracking | File Operations | API Operations |
|----------|---------------|-----------------|----------------|
| PyCharm + GitHub MCP + GitHub repo | GitHub Issues | opencode built-in PRIMARY, PyCharm FALLBACK | GitHub MCP ONLY |
| PyCharm + GitHub MCP + GitBucket repo | GitBucket API via `.env` | opencode built-in PRIMARY, PyCharm FALLBACK | Direct API calls |
| PyCharm only | GitBucket API via `.env` | opencode built-in PRIMARY, PyCharm FALLBACK | N/A |
| Neither available | Issues via API | opencode built-in tools | Direct API calls |

> **See `mcp-tool-usage` skill for the complete five-tier hierarchy with tool selection tables.**

---

## Skill Self-Discovery (Automatic)

Skills are discovered automatically via YAML frontmatter in each `SKILL.md` file. The `session-enforcement` plugin reads each skill's `description` field at startup and injects them into the first user message.

**Each skill description uses "Use when..." format** with triggering conditions and keyword coverage, NOT workflow summaries. This ensures the agent can self-discover which skill to invoke based on the current task context.

**The plugin handles:**
- Loading skill descriptions from YAML frontmatter at session start
- Sorting process skills before implementation skills
- Injecting enforcement content (1% rule, red-flags table, skill list) into the first user message

**The dispatch table is deprecated** — see `.opencode/dispatch-table.yaml` for historical reference only. Skill invocation is now driven by self-discovery via frontmatter descriptions.

**DO NOT embed skill invocation rules in AGENTS.md. They are discovered dynamically from SKILL.md frontmatter.**

---

## Skills

OpenCode skills are available in `.opencode/skills/`. Each skill has a `SKILL.md` file.

**To use a skill**, invoke it when relevant to the current task:

```
/skill <skill-name>
/skill <skill-name> --task <task-name>
```

**Skill invocation is driven by self-discovery** — see "Skill Self-Discovery" section above. Each SKILL.md frontmatter `description` field uses "Use when..." format with triggering conditions for automatic discovery.

### Sub-Task Architecture

Skills with `tasks/` subdirectory support `--task` parameter for loading specific workflow phases:

```
.opencode/skills/git-workflow/
├── SKILL.md              (~100 lines - overview + task table)
└── tasks/
    ├── pre-work.md       (~80 lines - Phase 0)
    ├── implementation.md (~80 lines - Phase 1)
    ├── review-prep.md    (~70 lines - Phase 2)
    ├── commit-prep.md    (~90 lines - Phase 3)
    ├── pr-creation.md    (~80 lines - Phase 4)
    └── cleanup.md        (~120 lines - Phase 5)
```

**Context Savings:** 75%+ reduction (load ~100 lines instead of ~500 lines)

**Usage:**
- `/skill git-workflow --task pre-work` - Load only pre-work task
- `/skill git-workflow --task pr-creation` - Load only PR creation task
- `/skill git-workflow` (no --task) - Skill overview only

### Integration with Approval Gates

- `approval-gate` skill: spec + authorization workflow
- `010-approval-gate.md`: critical rules (zero tolerance violations)
- `000-critical-rules.md`: auditor skill references
- Both auditors create audit logs in `./tmp/` for tracking

### Workflow Skills

Skill invocation is driven by self-discovery from SKILL.md frontmatter (see "Skill Self-Discovery" section). Key workflow skills:

| Skill | Purpose | Dispatch Trigger |
|-------|---------|------------------|
| `brainstorming` | Pre-spec requirements exploration | Before any spec creation |
| `writing-plans` | Transform approved specs into action plans | After spec approval |
| `executing-plans` | Step-by-step plan execution | After plan approval |
| `verification-before-completion` | Evidence gates before completion claims | Before marking tasks complete |
| `implementation-workflow` | Orchestration layer with yield-back context | After approval-gate confirms auth |
| `systematic-debugging` | Root cause analysis before bug fixes | Bug or error encountered |
| `finishing-a-development-branch` | Branch completion checklist | Implementation completes |
| `test-driven-development` | TDD red-green-refactor workflow | User requests TDD approach |
| `receiving-code-review` | Address review feedback precisely | PR receives review comments |
| `requesting-code-review` | Prepare and submit review requests | User says "request review" |
| `issue-review` | Unified review command for GitHub Issues | Review issue, audit spec, check issue |

**Implementation-workflow** coordinates git-workflow tasks (pre-work, review-prep, pr-creation) and yields structured context between stages. Authorization is checked once by `approval-gate`, then passed through the orchestration chain — no redundant re-checks.

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
| Markdown format | `uvx mdformat .opencode/guidelines/ docs/` | Markdown ONLY |
| Skill enforcement test | `bash .opencode/tests/test-enforcement.sh` | opencode-cli |
| Isolated opencode-cli run | `bash .opencode/tests/with-test-home opencode-cli run '<message>'` | opencode-cli |
| Clean test artifacts | `bash .opencode/tests/with-test-home --clean` | opencode-cli |

**Never** use bare `python`, `python3`, or `pip`. Always prefix with `uv run` for project commands.

**Isolated test environment:** The `with-test-home` wrapper isolates opencode-cli XDG state into a project-relative temporary home (`./opencode/tmp/test-home-<timestamp>`), eliminating SQLite session conflicts with the desktop app. This allows skill enforcement tests to run from within an active opencode session.

---

## Project Structure

- `src/`: Application source code
- `test/`: Unit and integration tests
- `docs/`: Documentation and specifications
- `.opencode/`: Skills, guidelines, and agent tools
  - `tools/`: Agent utility scripts (guidelines, md, memory, py, jupyter, etc.)
  - `skills/`: Self-contained skills (no guideline dependencies)
  - `guidelines/`: Core zero-tolerance rules only
  - `.guidelines/registry.yaml`: Registry of migrated content

---

## Code Style

See `.opencode/guidelines/080-code-standards.md` for details.

---

## Git Workflow

See `git-workflow` skill for complete workflow including:
- **Three-branch architecture:**
  - Feature branches (`spec/*` or `feature/*`) → Dev branch (`dev`)
  - Dev branch (`dev`) → Main branch (`main` or `master`)
  - AI commits blocked on `main`/`master`/`dev` by git hooks
- Branch before edit (MANDATORY)
- Branch from `dev` for features (sync first)
- Stash before branch creation
- Squash before PR (target `dev`, not `main`)
- Human-only merge
- Cleanup after merge

**Branch naming:** `spec/<short-name>` or `feature/<description>`

---

## Boundaries (Critical)

**✅ ALWAYS:**
- Run session init script at session start
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

---

## Q/A Mode

After session init and skill discovery, switch to Q/A mode:

1. **Report identity**: `<AgentName> (<ModelID>)`
2. **Report init results**: Platform, MCP availability
3. **Switch to Q/A**: "Ready. What would you like me to do?"
4. **Wait for user input**

**DO NOT proactively suggest tasks or ask leading questions.**

---

## Reference Files

| File | Purpose |
|------|---------|
| `.opencode/dispatch-table.yaml` | Skill invocation rules (DEPRECATED — kept for reference only) |
| `.opencode/.guidelines/registry.yaml` | Registry of migrated content blocks |
| `000-critical-rules.md` | Zero-tolerance violations |
| `010-approval-gate.md` | Authorization workflow |
| `020-go-prohibitions.md` | GO command restrictions |
| `git-workflow` skill | Complete git workflow |
| `approval-gate` skill | Authorization verification |