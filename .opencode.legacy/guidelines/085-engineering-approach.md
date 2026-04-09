# Engineering Approach Mandate

> **See:** `/skill implementation-quality` for pattern verification tasks and `/skill engineering-approach` for detailed checklists.

## Core Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes. Understand the "why" not just "what". Identify stakeholders and their needs.

2. **Design Before Implementing** — Document the approach in the spec. Consider multiple solutions and tradeoffs. Get approval on approach before coding.

3. **Verify Before Declaring Complete** — Run all tests manually. Check for edge cases. Verify against all success criteria. Update documentation.

4. **Communicate Changes** — Provide updates in CHAT when changes happen (PR created, task completed). DO NOT post comments to GitHub for implementation progress. DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates).

## Scope Discipline (Critical)

### No Feature Creep

- Implement ONLY what is specified in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- No unrelated fixes discovered during work (file separate issue)

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "proceed" or "yes" before starting
- If unclear, ask - do not assume

## Pattern Compliance Verification (Critical)

**⚠️ CRITICAL: All implementation MUST verify pattern compliance against documented guidelines.**

### Pattern Categories

#### File Location Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Temp files | `./tmp/` directory only | `070-environment.md` |
| Test files | `test/` directory only | `070-environment.md` |
| Migrations | `_Migration` entries in `schema.py` only | `100-persistence.md` |
| Agent scripts | `ai_bin/` directory | `AGENTS.md` |
| Standalone scripts | `scripts/` directory | `070-environment.md` |
| Notebooks | Notebooks directory only | `061-notebook-rules.md` |

| Violation | Correct Action |
|-----------|----------------|
| Standalone migration file | Move to `_Migration` entry in `src/commons/persistence/pg/schema.py` |
| Temp file at project root | Delete, recreate in `./tmp/` |
| Test file in `src/` | Move to `test/` directory |
| Agent script outside `ai_bin/` | Move to `ai_bin/` |

#### Code Structure Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| DB operations | Must use Repository classes | `100-persistence.md` |
| Direct DB access | FORBIDDEN in `src/` | `100-persistence.md` |
| Re-exports in `__init__.py` | FORBIDDEN | `080-code-standards.md` |
| Notebook file operations | Must use `the-notebook-mcp` tools | `061-notebook-rules.md` |
| MCP tool usage | Mandatory when available | `015-mcp-preference.md` |

| Violation | Correct Action |
|-----------|----------------|
| `session.execute()` in `src/` | Create/use Repository class, move DB logic there |
| `session.query()` in `src/` | Create/use Repository class, move query there |
| `from X import Y` in `__init__.py` | Use direct import (`from X import Y`) at call site |
| `read`/`edit`/`write` on `.ipynb` | Use `the-notebook-mcp_notebook_*` tools |
| `edit` tool on project file with PyCharm MCP | Use `pycharm_*` tools |

#### Environment Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Node.js in Python projects | FORBIDDEN | `070-environment.md` |
| Python execution | `uv run python` only | `070-environment.md` |
| Package management | `uv sync` only, never `uv add` | `070-environment.md` |
| Absolute paths in commands | FORBIDDEN | `060-tool-usage.md` |
| System temp `/tmp/` | FORBIDDEN, use `./tmp/` only | `060-tool-usage.md` |

| Violation | Correct Action |
|-----------|----------------|
| `npm install` in Python project | Use Python-native equivalents (`uv`, `ruff`, `pytest`) |
| `python script.py` | Use `uv run python script.py` |
| `pip install package` | Edit `pyproject.toml`, run `uv sync` |
| `cd /home/user/git/repo && command` | Use workdir or relative paths |
| File path `/tmp/file.txt` | Use `./tmp/file.txt` |

#### Data Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Synthetic/fabricated data | FORBIDDEN | `090-data-integrity.md` |
| Defaults for missing required data | FORBIDDEN | `090-data-integrity.md` |
| Silent exception swallowing | FORBIDDEN | `090-data-integrity.md` |
| `None` return for required data | FORBIDDEN | `090-data-integrity.md` |

| Violation | Correct Action |
|-----------|----------------|
| `data.get("field", "default")` for required field | Raise error if missing |
| `try: ... except: pass` | Log AND re-raise, never swallow |
| `return None` for required data | Raise error instead |
| Fabricated test data in production code | Use real data sources |

---

## Verification-First Response Protocol (MANDATORY)

**⚠️ ZERO TOLERANCE: The agent MUST NOT respond to user input before completing verification steps.**

### The Problem

Agents frequently respond to questions without:

- Completing session init
- Checking for superseding issues
- Verifying codebase state
- Running mandatory verification skills
2. **Implementation workflow**: Verify files follow patterns
3. **Review-prep task**: Post-implementation pattern verification

**See `engineering-approach` skill for complete workflow.**

---

## Verification-First Response Protocol (MANDATORY)

**⚠️ ZERO TOLERANCE: The agent MUST NOT respond to user input before completing verification steps.**

### The Problem

Agents frequently respond to questions without:

- Completing session init
- Checking for superseding issues
- Verifying codebase state
- Running mandatory verification skills

This leads to incorrect responses based on outdated information.

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Answering questions without session init | Missing critical context (owner, repo, MCP availability) |
| Creating specs without checking conflicts | Duplicate/superseded specs waste work |
| Implementing without verification | Stale specs, changed codebase |
| Using question-answering as bypass | Questions are NOT authorization to skip checks |

### ✅ REQUIRED SEQUENCE

**Before responding to ANY user input (question, task, request):**

1. **Run session init if not already done**: `uv run python ai_bin/session_init.py`
2. **Check for superseding/conflicting issues**: Query all `[SPEC]` issues
3. **Verify codebase state matches spec assumptions**: Read files, check current state
4. **Verify sub-issues for multi-task specs**: Call `github_issue_read(method=get_sub_issues)`
5. **Confirm authorization**: Check for `approved`/`go` or `needs-approval` label
6. **THEN and ONLY THEN**: Respond to user

### Question-Response Flowchart

```
User asks question
    ↓
Has session init run?
    ├─ NO → Run `ai_bin/session_init.py` FIRST
    └─ YES ↓
Check for superseding issues?
    ├─ Found conflict → HALT, report conflict
    └─ No conflict ↓
Verify codebase state?
    ├─ Stale spec → HALT, report staleness
    └─ Current ↓
Question requires implementation?
    ├─ YES → Check authorization
    │        ├─ Not authorized → HALT, wait for "approved"/"go"
    │        └─ Authorized → Proceed
    └─ NO (informational) → Verify answer, then respond
```

### Integration Points

| Workflow Stage | Guideline Reference |
|----------------|---------------------|
| Session init verification | `000-session-init.md` "Session Init Verification" |
| Superseding issue check | `130-authority-source.md` "Code as Authoritative Source" |
| Sub-issue verification | `010-approval-gate.md` Sub-issue Verification Gate |
| Codebase state verification | `085-engineering-approach.md` Verify Before Declaring Complete |

### Why This Matters

- Agent skipping session init → wrong GIT_OWNER, broken GitHub MCP calls
- Agent creating duplicate specs → wasted work, confusion
- Agent implementing stale specs → code that doesn't match requirements
- Agent answering questions without checks → incorrect responses based on outdated assumptions**
