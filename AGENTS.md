# AGENTS.md — Repository Guidelines for Coding Agents

## 🚨 MANDATORY STARTUP SEQUENCE (Try/Catch/Finally)

**⚠️ ZERO TOLERANCE: Complete ALL steps before ANY tool calls.**

### TRY BLOCK: Session Init (MUST COMPLETE FIRST)

```bash
uv run python ai_bin/session_init.py
```

**Store outputs for session duration:**
- `DEV_NAME`, `DEV_EMAIL` → Commit trailers
- `GIT_OWNER`, `GIT_REPO` → GitHub MCP calls
- `GIT_HOOKS_PATH` → Hook verification
- `GIT_REMOTE_URL` → Reference

**Exit codes:**
- `0`: Success → Proceed to Finally block
- `1`: No remote configured → Report error, HALT (developer must configure)
- `2`: Non-GitHub remote → GitHub MCP unavailable

### CATCH BLOCK: Error Handling

| Exit Code | Problem | Action |
|-----------|---------|--------|
| 1 | No remote configured | Report error → HALT (developer must configure remote) |
| 2 | Non-GitHub remote | GitHub MCP unavailable → Use `gh` CLI fallback |
| Script not found | Report error | HALT — cannot proceed |

### FINALLY BLOCK: MCP Probe (ALWAYS RUNS AFTER TRY)

**Probe MCP availability:**
1. PyCharm MCP: `pycharm_get_project_modules`
2. GitHub MCP: `github_get_me`
3. Record availability for tool selection

### CIRCUIT BREAKER: Enforcement Gate

🚫 **NO tool calls** before Try block completes successfully
🚫 **NO MCP calls** before Finally block completes
🚫 **NO implementation** before authorization verified

---

## Core Workflow (References)

| Topic | Guideline File |
|-------|----------------|
| Branch Before Edit | `110-git-branch-first.md` |
| Stash External Changes | `110-git-branch-first.md` §1.1 |
| WIP Commit Before HALT | `111-git-commit-workflow.md` §5 |
| Todo Tracking | `111-git-commit-workflow.md` §5.5 |
| MCP Tool Usage | `015-mcp-preference.md`, `mcp-tool-usage` skill |
| Notebook Operations | `061-notebook-rules.md`, `notebook-operations` skill |
| Authorization Gate | `010-approval-gate.md`, `approval-gate` skill |
| Spec Creation | `140-planning-spec-creation.md` |
| Issue Closure | `124-github-archive-workflow.md` |
| Critical Rules | `000-critical-rules.md` |
| Engineering Approach | `085-engineering-approach.md` |
| Environment | `070-environment.md` |
| Code Standards | `080-code-standards.md` |
| Data Integrity | `090-data-integrity.md` |
| Error Handling | `090-data-integrity.md` (see `implementation-quality` skill for data patterns) |

---

## Build / Lint / Test Commands

| Task | Command | File Types |
|------|---------|------------|
| Sync dependencies | `uv sync` | - |
| Run all tests | `uv run pytest test/` | - |
| Lint + auto-fix | `uvx ruff check --fix src/ test/` | Python ONLY |
| Format | `uvx ruff format src/ test/` | Python ONLY |
| Type check | `uvx pyright src/` | Python ONLY |
| Markdown lint | `uvx pymarkdownlnt scan -r .opencode/guidelines/ docs/` | Markdown ONLY |
| Markdown format | `uvx mdformat --number --wrap keep --end-of-line lf .opencode/guidelines/ docs/` | Markdown ONLY |

**NEVER**: `python`, `python3`, `pip`, `uv add`, `ruff` on markdown

---

## Authorization Recognition

| Pattern | Example | Action |
|---------|---------|--------|
| Direct command | "implement #227" | ✅ Continue |
| Compound command | "implement #227 and include in branch" | ✅ Continue |
| Question | "should I implement #227?" | 🚫 HALT |
| Conditional | "if you think #227 is needed..." | 🚫 HALT |

**Multi-phase authorization:**
- `approved` or `go` → ALL phases authorized
- `approved: 1` → Phase 1 only
- `approved: 2.3` → Phase 2, Step 3 only

**Revision revokes approval:** Any spec change requires fresh authorization.

---

## Skills (Mandatory Invocation)

**Master Trigger Table:**

| Workflow Trigger | Invocation |
|------------------|------------|
| Before ANY file edit | `/skill approval-gate --task verify-authorization` |
| Before implementation | `/skill approval-gate --task verify-sub-issues` |
| After authorization | `/skill git-workflow --task pre-work` |
| After implementation | `/skill git-workflow --task review-prep` (AUTOMATIC) |
| "create a PR" | `/skill git-workflow --task pr-creation` |
| "PR merged" | `/skill git-workflow --task cleanup` |
| Before creating file | `/skill implementation-quality --task file-locations` |
| At implementation start | `/skill implementation-quality --task code-structure` |
| Before running commands | `/skill implementation-quality --task environment` |
| Before handling data | `/skill implementation-quality --task data-integrity` |
| Writing code | `/skill code-size-enforcement` |
| After ANY code/guideline/skill/task change | `/skill code-review` (MANDATORY) |
| Before spec approval | `/skill concern-separation-auditor --issue N` (FIRST) |
| After concern auditor | `/skill spec-auditor --issue N` (SECOND) |
| After spec auditor | `/skill dev-architect --task review-spec` (THIRD) |

**See full skill list in `.opencode/skills/`**

---

## 🚫 NEVER (Zero Tolerance)

- Write code without approved spec
- Interpret questions as authorization
- Proceed after completing task — **SILENTLY HALT**
- Create PRs without explicit "create a PR" instruction
- Bypass `git-workflow` skill for PR/cleanup operations
- Use `/tmp/` — only `./tmp/`
- Delete merged branches — delete **IMMEDIATELY** after merge
- Prompt via issue comments — no "awaiting authorization" dialogs
- Run notebooks with production data without explicit authorization
- Implement scope creep — ONLY what spec requests
- Use shell redirects on notebooks — use `the-notebook-mcp` exclusively
- `git restore` on external changes — **`git stash` FIRST**
- Copy hardcoded identity examples — **extract from system prompt**
- Make code/guideline/skill/task changes without running `/skill code-review` AFTER changes
- **Post session summaries, chit-chat, or interactive questions to GitHub Issues** — ALL chat session communication goes to CHAT ONLY, NEVER to GitHub Issues

---

## Guideline Violations

**If agent violates guideline:**

1. STOP task
2. Update this file "NEVER" list
3. Update relevant `.opencode/guidelines/` file
4. Document fix in issue comment (FACTUAL ONLY)
5. Wait for confirmation before resuming

---

## Session Communication

**Chat vs. GitHub Issues:**

| Output Type | Destination |
|-------------|-------------|
| Session summaries, progress updates | CHAT ONLY |
| Interactive questions, chit-chat | CHAT ONLY |
| Audit logs | Internal (`./tmp/`) — NOT posted anywhere |
| Investigation artifacts | GitHub Issues (only when substantive) |
| Closure summaries | GitHub Issues (historical record) |

**CRITICAL:** ALL chat session communication goes to CHAT ONLY, NEVER to GitHub Issues. Audit logs are internal artifacts — do NOT post to chat or GitHub unless explicitly requested.

---

## Identity Detection (CRITICAL)

**🚫 FORBIDDEN: Copy hardcoded identity examples from guidelines.**

**✅ REQUIRED: Extract identity from system prompt at runtime:**
- `<AgentName>` → Your actual name (e.g., "OpenCode Desktop")
- `<ModelID>` → Backing model (e.g., "ollama-cloud/qwen3.5:397b")
- `<ai-email>` → Agent's noreply email

**Example values in guidelines are ILLUSTRATIVE ONLY — substitute your actual identity.**

---

**Run session init FIRST:**
```bash
uv run python ai_bin/session_init.py
```

---
🤖 ✨ Created by OpenCode Desktop (ollama-cloud/qwen3.5:397b)
