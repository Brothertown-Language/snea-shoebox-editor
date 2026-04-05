# AGENTS.md — Repository Guidelines for Coding Agents

## Session Init (MANDATORY FIRST)

**Run BEFORE any other operations:**

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

**Store these values for session duration.**

**Exit codes:**
- 0: Success — proceed with session
- 1: No remote configured — cannot proceed with GitHub operations
- 2: Non-GitHub remote — GitHub MCP operations unavailable

---

## MCP Capability Testing (Universal)

After session init, probe MCP availability:

1. **PyCharm MCP**: Call `pycharm_get_project_modules` — if works, use PyCharm tools for file ops
2. **GitHub MCP**: Call `github_get_me` — if works, use GitHub Issues for specs
3. **Owner/Repo**: Use values from session init script (already extracted from remote)

### MCP Enforcement Gate

| Scenario | Spec Tracking | File Operations | GitHub Operations |
|----------|---------------|-----------------|-------------------|
| Both available | GitHub Issues | PyCharm MCP tools ONLY | GitHub MCP tools ONLY |
| PyCharm only | GitHub Issues | PyCharm MCP tools ONLY | N/A (no GitHub MCP) |
| Neither available | GitHub Issues via `gh` CLI | Direct file tools + `# FALLBACK: PyCharm MCP unavailable` comment | `gh` CLI or web UI |

🚫 **PROHIBITED**: Using `read`/`write`/`edit`/`glob`/`grep` on **ANY files** when PyCharm MCP is available.

## Branch Before Edit

**FIRST action before ANY filesystem change:**

```
git checkout dev && git pull origin dev
git checkout -b feature/<description>
```

🚫 **NEVER**: Edit, create, delete, or rename files while on `main` or `dev`. No exceptions.

## Preserve Pending Changes

**Before ANY branch operation, check for pending changes:**

```
git status
```

If ANY files modified, staged, or untracked:
```
git stash push -m "WIP: before <branch-name>"
git stash list  # VERIFY the stash exists
git status      # VERIFY clean working tree
```

🚫 **NEVER**: `git branch -D <branch>` or `git push --delete` without explicit developer request.
🚫 **NEVER**: Delete stashes without explicit developer request.
🚫 **NEVER**: Assume branches are "disposable" — always preserve until explicitly asked to delete.

---

## Guidelines Structure

OpenCode loads guidelines from:
- `AGENTS.md` (this file)
- `.opencode/guidelines/*.md` (all guideline files)

**Guideline file numbering:**

| Series | Range | Category |
|--------|-------|----------|
| 000-099 | Core | Session init, critical rules, approval |
| 100-109 | MCP/Scope | Tool usage, scope autonomy |
| 110-119 | Git | Branch, commit, merge, PR, cleanup |
| 120-129 | GitHub | Issue workflow, MCP ops, AI identity, archive |
| 130-139 | Authority | Code as source |
| 140-149 | Planning | Spec creation, approval gates, status tracking, archive |
| 200-209 | Errors | Exception handling, missing data, domain exceptions, logging |
| 210-219 | Standards | Code standards, HTTP, engineering |

**Key guidelines:**

| Topic | File |
|-------|------|
| Critical Rules | `000-critical-rules.md` |
| Docs Verification | `075-docs-verification.md` |
| Session Init | `000-session-init.md` |
| Approval Gate | `010-approval-gate.md` |
| MCP Preference | `015-mcp-preference.md` |
| Srclight Preference | `016-srclight-preference.md` |
| GO Prohibitions | `020-go-prohibitions.md` |
| Open Questions | `045-open-questions.md` |
| Scope Autonomy | `050-scope-autonomy.md` |
| Tool Usage | `060-tool-usage.md` |
| Notebook Rules | `061-notebook-rules.md` |
| Environment | `070-environment.md` |
| Code Standards | `080-code-standards.md` |
| Engineering Approach | `085-engineering-approach.md` |
| HTTP Requests | `086-http-requests.md` |
| Data Integrity | `090-data-integrity.md` |
| Persistence | `100-persistence.md` |
| Scripting | `120-scripting.md` |
| Authority Source | `130-authority-source.md` |

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
| Markdown format | `uvx mdformat --number --wrap keep --end-of-line lf .opencode/guidelines/ docs/` | Markdown ONLY |

**Never** use bare `python`, `python3`, or `pip`. Always prefix with `uv run` for project commands.
**Standalone tools** (ruff, pyright, vulture) use `uvx` or `uv tool install` — NOT `uv run`.
**Never** use `ruff`, `pyright`, or `vulture` on markdown files — use `pymarkdownlnt` and `mdformat` instead.

## Tool Installation (Optional)

For frequently-used tools, developers can install them persistently:

```bash
uv tool install ruff pyright vulture pymarkdownlnt mdformat
```

This allows direct invocation without `uvx` prefix:

```bash
ruff check --fix src/ test/
pyright src/
pymarkdownlnt scan -r .opencode/guidelines/ docs/
mdformat .opencode/guidelines/ docs/
```

To upgrade installed tools:

```bash
uv tool upgrade --all
```
**Never** use `uv add`; edit `pyproject.toml` directly, then `uv sync`.

## Project Structure

- `src/`: Application source code
- `test/`: Unit and integration tests
- `docs/`: Documentation and specifications
- `ai_bin/`: Agent utility scripts

## Code Style

See `.opencode/guidelines/080-code-standards.md` for details. Key points:
- Follow PEP 8 for Python
- Use `ruff` for linting and formatting
- Mirror existing patterns in the codebase

## Git Workflow

See `.opencode/guidelines/110-git-branch-first.md` through `115-git-hotfix-workflow.md` for full workflow. Key points:
- **Branch Hierarchy**: `main` (production) ← `dev` (integration) ← `feature/*` (development)
- **Feature PRs**: Squash-merge to `dev` (one commit per PR)
- **Release PRs**: Merge commit from `dev` to `main` (preserves PR history)
- **Hotfixes**: Branch from `main`, merge back to both `main` and `dev`
- PRs require explicit developer instruction — agent does NOT auto-create PRs
- Human-only merge — agent never merges PRs
- Delete merged branches after PR merge

## Boundaries (Critical)

See `.opencode/guidelines/000-critical-rules.md` for complete list.

## Engineering Approach (Critical)

ALL work must follow proper engineering methodology:

1. **Understand** → Read and analyze before proposing
2. **Design** → Document approach before implementing  
3. **Implement** → Execute with attention to quality
4. **Verify** → Test thoroughly before declaring complete

**Scope Discipline:**
- No feature creep - implement ONLY what is specified
- No unapproved work - wait for explicit authorization

See `.opencode/guidelines/085-engineering-approach.md` for complete requirements.

**✅ ALWAYS:**
- **Run session init script at session start** — Run `uv run python ai_bin/session_init.py` before any other operations. Store the output values (DEV_NAME, DEV_EMAIL, GIT_OWNER, GIT_REPO, GIT_HOOKS_PATH, GIT_REMOTE_URL) for session duration. See `000-session-init.md`.
- Create feature branch BEFORE any filesystem change
- Create PRs for all merges (when tooling available)
- Reference the Authoritative Spec for planning
- Create specs in GitHub Issues BEFORE implementing
- **Check all comments and subissues BEFORE implementation** (see `010-approval-gate.md`)
- **Respond to GitHub issue comments via GitHub issue comments** — users cannot read your mind (see `000-critical-rules.md`)
- Wait for explicit authorization before writing code
- Get individual authorization for each task in multi-task plans
- **SILENTLY HALT after completing a task**
- **Commit WIP before ANY HALT** — Before halting (awaiting approval, clarification, error, session end), commit all changes with WIP message. See `111-git-commit-workflow.md`.
- Use PyCharm MCP tools for all file operations when available
- **STASH EXTERNAL CHANGES FIRST** — Before ANY branch creation, `git status`. If ANY files modified, `git stash push -m "WIP: before <branch>"`, then VERIFY with `git stash list` and clean `git status`.

**🚫 NEVER:**
- Write code/notebooks/configs/tests without approved spec
- Interpret questions as authorization ("Should I do X?" = asking permission)
- Proceed to next task after completing a task — HALT
- Create plans inline in message body
- **Implement a revised spec without fresh approval** — Spec changes revoke authorization. See `010-approval-gate.md` "Revision Revokes Approval"
- **Create PRs without EXPLICIT developer instruction** — "approved" and "go" authorize implementation ONLY. PRs require explicit "create a PR" instruction. Completing implementation does NOT authorize PR creation.
- **Submit unsquashed PRs** — ALL PRs must have exactly ONE commit (squashed). Multiple commits in a PR will be rejected. Always `git reset --soft origin/dev && git commit` before pushing.
- **Create PRs after implementation** — The developer must run human tests and may require adjustments BEFORE any PR. Wait for explicit "create a PR" after developer has tested.
- **BYPASS PR WORKFLOW SKILL** — When user says "pr", "create a PR", "update PR", or ANY PR-related command, MUST invoke `/skill git-workflow --task <appropriate-task>`. NEVER manually create/update/close PRs. The skill handles existing PR detection (Step 0 checks for open/merged PRs).
- **PR MERGE CONFIRMATION REQUIRES SKILL** — When user says "pr merged", "merged", or similar, MUST invoke `/skill git-workflow --task cleanup`. NEVER manually handle PR merge confirmation, issue closure, or branch cleanup. The skill handles ALL post-merge operations including GitHub API verification and branch deletion.
- Use `/tmp/` — only use `./tmp/`
- **DELETE MERGED BRANCHES IMMEDIATELY** — After PR merge confirmation, delete the branch immediately. No asking, no waiting. Unmerged branches with work ARE preserved until explicit delete request.
- **ANALYZE ISSUE COMMENTS SILENTLY** — Always respond to user comments via GitHub issue comment. Users cannot see your internal reasoning.
- **PROMPT VIA ISSUE COMMENTS** — Never add "awaiting authorization", "let me know when ready", or any dialog prompts to GitHub issue comments. Comments are record-keeping, not chat.
- **USE MCP TOOLS FOR NOTEBOOKS** — Always use `the-notebook-mcp` tools for ALL notebook operations (read, edit, create, delete). Never use `read`/`edit`/`write` tools on `.ipynb` files.
- Install Node.js/NPX in Python-only environments — Node.js is detestable in Python/Java projects; use native alternatives (`uv`, `ruff`, `pytest` for Python; Maven/Gradle for Java)
- Ask to run production code without explicit authorization
- Use direct file tools when PyCharm MCP available
- **RUN NOTEBOOKS WITH PRODUCTION DATA** — `the-notebook-mcp_notebook_execute_cell`, `pycharm_runNotebookCell`, and ANY execution method on production notebooks (see `061-notebook-rules.md`) is FORBIDDEN without explicit per-execution user authorization
- **IMPLEMENT SCOPE CREEP** — Only implement what the spec explicitly requests. Never refactor "nearby" code, add "helper" functions, or fix "similar issues" not in the spec
- **USE PROPER NOTEBOOK TOOLING** — Always use `the-notebook-mcp` tools (e.g., `the-notebook-mcp_notebook_read`, `the-notebook-mcp_notebook_edit_cell`). Never use shell redirects (`sed`, `>`, `cat`) on notebook content — this causes edit failures and corrupted state.
- **USE GIT RESTORE ON EXTERNAL CHANGES** — `git restore` on externally-modified files destroys changes permanently. Always `git stash` first.

## Guideline Violations

**If the agent violates a guideline, update guidelines to close the gap.**

1. STOP the current task
2. Update AGENTS.md "NEVER" list
3. Update relevant guideline file in `.opencode/guidelines/`
4. Document the fix in a comment on the associated issue — FACTUAL ONLY
5. Wait for user confirmation before resuming

---

## Authorization Recognition Protocol

**These patterns ARE explicit authorization (agent MUST continue):**

| Pattern | Example | Why It's Authorization |
|---------|---------|----------------------|
| Direct command | "implement #227" | Explicit instruction to implement |
| Include in branch | "include in this feature branch" | Explicit scope expansion authorization |
| Compound command | "implement #227 and include in #223 branch" | Authorization for both implementation AND branch inclusion |
| Fix this too | "fix the URL order while you're at it" | Explicit authorization for additional work |

**These are NOT authorization (agent must HALT):**

| Pattern | Example | Why It's NOT Authorization |
|---------|---------|---------------------------|
| Question | "should I implement #227?" | Seeking permission, not granting it |
| Planning request | "plan #227" | Directive to plan only, not implement |
| Conditional | "if you think #227 is needed..." | Conditional, requires judgment |
| Observation | "#227 looks related" | Not a command to implement |

**Authorization Rules:**

✅ **MUST continue immediately when:**
- User says "implement #N and include in this branch"
- User says "fix X while you're at it"
- User says "also fix the typo" (unrelated fix)
- User provides multiple explicit commands in one message

🚫 **MUST HALT when:**
- User asks a question ("should I...?", "would you like...?")
- User uses conditionals ("if you think...", "maybe...")
- User makes observations without commands
- Authorization is ambiguous or unclear

---

## Guidelines Access

| Command | Purpose |
|---------|---------|
| `srclight_search_symbols` or `pycharm_search_in_files_by_text` | Search guidelines for topic |
| `pycharm_get_file_text_by_path` | Read specific guideline file |
| `pycharm_list_directory_tree` | List guideline directory structure |

---

## Skills

OpenCode skills are available in `.opencode/skills/`. Each skill has a `SKILL.md` file with:
- `name`: Skill identifier
- `description`: What the skill does
- `license`: License type
- `compatibility`: opencode

**⚠️ MANDATORY: All skills MUST have a `tasks/` subdirectory with at least one task file.**

Skills without tasks cannot be invoked as subtasks and will fail silently. See `skill-creator` skill for complete requirements.

To use a skill, the agent loads it when relevant to the current task.

### Skill Invocation Guidance

**Master Trigger Table — AGENTS.md is the single source of truth.**
Allskill trigger definitions are in this table. SKILL.md files reference this table.

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Before ANY file edit | `/skill approval-gate --task verify-authorization` | Confirm spec + approval exist |
| Before implementation | `/skill approval-gate --task verify-sub-issues` | Check sub-issue structure for multi-task specs |
| After approval ("approved" or "go") | `/skill git-workflow --task pre-work` | Stash changes, create feature branch |
| After implementation completes | `/skill git-workflow --task review-prep` | Push branch, generate compare URL, HALT |
| User says "create a PR" | `/skill git-workflow --task pr-creation` | Squash to single commit, push, create PR, HALT |
| User says "PR merged" | `/skill git-workflow --task cleanup` | Close issues, delete branches |
| Before creating ANY file | `/skill implementation-quality --task file-locations` | Verify file location patterns |
| At implementation start | `/skill implementation-quality --task code-structure` | Verify code structure patterns |
| Before running commands | `/skill implementation-quality --task environment` | Verify environment patterns |
| Before handling data | `/skill implementation-quality --task data-integrity` | Verify data integrity patterns |
| Writing or modifying code | `/skill code-size-enforcement` | Enforce size limits on functions, cells, files |
| Before approving guideline changes | `/skill guideline-auditor` | Verify guideline quality, find ambiguities/conflicts |
| Before approving spec implementation | `/skill concern-separation-auditor --issue N` | FIRST: phase structure, concern analysis |
| After concern-separation-auditor | `/skill spec-auditor --issue N` | SECOND: content quality, fresh-start context |
| After spec-auditor | `/skill dev-architect --task review-spec` | THIRD: architectural correctness |
| User says "approved" or "go" | `/skill approval-gate --task verify-authorization` | Verify auth + needs-approval label status |
| Before implementing any task | `/skill approval-gate --task verify-sub-issues` | Verify sub-issue structure |
| Periodic guideline maintenance | `/skill guideline-auditor` | Check for guideline drift |
| Post-implementation verification | `/skill spec-auditor --issue N` | Verify spec was implemented correctly |
| Before skill extraction | `/skill coherence-auditor --mode extraction` | Identify skill candidates from guidelines |
| Periodic coherence maintenance | `/skill coherence-auditor --mode maintenance` | Detect guideline-skill drift |
| Designing architecture | `/skill dev-architect --task design-plan` | Create architecture design plans |
| Plan phase of spec creation | `/skill dev-architect --task design-plan` | Invoke at Plan phase |
| Encountering errors/bugs | `/skill debugger` | Analyze errors and debug issues |
| Preparing commit messages | `/skill commit-writer` | Generate commit messages |
| Creating task descriptions | `/skill task-writer` | Draft task descriptions |
| Preparing PR descriptions | `/skill pr-writer` | Create pull request descriptions |
| Publishing releases | `/skill release-notes` | Publish release notes |
| Checking Git conventions | `/skill git-conventions` | Reference Git convention knowledge |
| Looking up documentation | `/skill context7-lookup` | Look up Context7 documentation |

**When task names are specified:** Use `/skill <name> --task <task>` for specific workflow phases.
**When task names are NOT specified:** Use `/skill <name>` for skill overview only.

**Skill Invocation:**
- `git-workflow` skill is invoked at these triggers:
  1. User authorizes implementation ("approved", "go", "proceed") → `pre-work` task
  2. Implementation completes → **`review-prep` task (no decision point)**
  3. User requests PR creation ("create a PR", "make a PR", "push and create PR") → `pr-creation` task
- The skill handles all git operations (branch, stash, commit, squash, push, PR creation) according to guidelines.
- `pr-creation-workflow` skill defines when PRs can be created and what authorizes PR creation. It is NOT automatically invoked - it documents the rules.
- `implementation-quality` skill is invoked at implementation gates:
  1. Before creating ANY file → `file-locations` task
  2. At implementation start → `code-structure` task (load once, reference continuously)
  3. Before running commands → `environment` task
  4. Before handling data → `data-integrity` task
- `dev-architect` skill is invoked at Plan phase:
  1. When creating a new spec → `design-plan` task
  2. When reviewing specs → `review-spec` task

**Sub-Task Invocation:**
- Skills with `tasks/` subdirectory support `--task` parameter for loading specific tasks:
  - `/skill git-workflow --task pre-work` - Load only pre-work task (~80 lines)
  - `/skill git-workflow --task pr-creation` - Load only PR creation task (~80 lines)
- This reduces context window pollution by loading only relevant workflow phases.
- Use `/skill <skill-name> --task <task-name>` for sub-task invocation.
- Use `/skill <skill-name>` (no `--task`) for skill overview only.

**Integration with Approval Gates:**
- See `.opencode/skills/approval-gate/SKILL.md` for spec+authorization workflow
- See `010-approval-gate.md` for critical rules (zero tolerance violations)
- See `000-critical-rules.md` for auditor skill references
- Both auditors create audit logs in `./tmp/` for tracking

### Sub-Task Architecture for Context Efficiency

**Problem:** Monolithic skills load 500+ lines into context when only 50-100 lines are needed for a specific workflow phase.

**Solution:** Skills with lengthy procedural workflows use sub-task architecture:

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

**When to Use Sub-Task Invocation:**

| Situation | Invocation | Lines Loaded |
|-----------|------------|---------------|
| Need overview only | `/skill git-workflow` | ~100 |
| Before implementation starts | `/skill git-workflow --task pre-work` | ~80 |
| **After implementation completes** | `/skill git-workflow --task review-prep` | ~70 |
| Creating a PR | `/skill git-workflow --task pr-creation` | ~80 |
| After PR merged | `/skill git-workflow --task cleanup` | ~120 |

**Sub-Task Skill Detection:**
- Check if skill directory has `tasks/` subdirectory
- If yes, prefer `--task` invocation for specific workflow phases
- If no, load full skill

**Parent Issue / Sub-Issue Architecture:**

Multi-task specs use parent orchestrator issues with child sub-issues:

| Issue Type | Purpose | Size |
|------------|---------|------|
| Parent (`[SPEC]`) | Orchestrator with task table | ~700 words |
| Child (`[Task: #N]`) | Self-contained implementation details | ~450-1100 words |

**Single-Subtask-at-a-Time:**
- Only ONE subtask executes at a time (enforced by STATUS gate)
- STATUS in parent matches active subtask number
- Prevents git conflicts, file races, and stash collisions
- Sequential advancement: STATUS advances only after subtask completion

**Templates:**
- Parent Issue: `.opencode/skills/templates/PARENT-ISSUE-TEMPLATE.md`
- Sub-Issue: `.opencode/skills/templates/SUB-ISSUE-TEMPLATE.md`

## Session Output Attachment (MANDATORY)

**All session outputs (audit logs, reports, investigation artifacts) MUST be attached to GitHub Issues.**

### Why This Matters

Fresh-start AI agents have no memory of previous sessions. Outputs stored locally in `./tmp/` are NOT preserved between sessions. GitHub Issues are the persistent tracking mechanism.

### Workflow

1. **Generate output in `./tmp/`:**
   - Audit logs: `./tmp/audit-YYYYMMDD.md`, `./tmp/audit-spec-YYYYMMDD.md`, `./tmp/coherence-audit-YYYYMMDD-*.md`
   - Investigation reports: `./tmp/investigation-*.md`
   - Tool outputs: Any files created during session work

2. **After creating output:**
   - Read the full content
   - Attach to appropriate GitHub Issue via `github_add_issue_comment`
   - Delete the temp file

3. **Target Issue Selection:**
   - Attach to the issue that NEEDS the outputs for context
   - NOT necessarily the issue that created the outputs
   - If working on #100 but audit is needed for #200 → attach to #200

4. **Comment Format:**
   ```
   AI: <AgentName> <ModelID> 📝 <output-type>: <title>
   
   ## Summary
   <brief summary>
   
   <full content or key findings>
   ```

### Skills with Built-in Attachment

These skills automatically attach outputs to issues:

| Skill | Attachment Target |
|-------|-------------------|
| `guideline-auditor` | Issue being discussed or summary issue |
| `coherence-auditor` | Issue being discussed or summary issue |
| `spec-auditor` | Issue specified by `--issue N` |

### Manual Attachment

For investigation reports, test results, or other session artifacts:

```python
# Read the output
output_path = "./tmp/investigation-20260328.md"
with open(output_path) as f:
    content = f.read()

# Attach to target issue
github_add_issue_comment(
    owner=owner, repo=repo, issue_number=target_issue,
    body=f"AI: OpenCode ollama-cloud/glm-5 📝 Investigation: <title>\n\n{content}"
)

# Delete temp file
os.remove(output_path)
```

### Examples

| Scenario | Output Location | Attachment Target |
|----------|-----------------|-------------------|
| Guideline audit for spec #200 | `./tmp/audit-20260328.md` | Spec #200 |
| Coherence audit for guideline changes | `./tmp/coherence-audit-20260328-*.md` | Guideline change issue |
| Spec audit | `./tmp/audit-spec-20260328.md` | Spec being audited (`--issue N`) |
| Investigation for issue #50 | `./tmp/investigation-*.md` | Issue #50 |

**⚠️ CRITICAL: Always attach to GitHub Issue, then delete temp file. No exceptions.**