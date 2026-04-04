---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends AI capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
compatibility: opencode
---

## Operating Protocol

### ⚠️ VERIFICATION STEPS (MANDATORY FIRST)

**Before ANY skill operation, verify:**

1. **Session Init Check:**
   - Has `ai_bin/session_init.py` run?
   - Store: `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL`
   - If NOT run → STOP, run session init FIRST

2. **Codebase Verification:**
   - Is codebase state current?
   - Run: `srclight_codebase_map` or `srclight_index_status`
   - Verify: No stale assumptions from previous sessions

3. **Issue Conflict Check:**
   - Query open `[SPEC]` issues for conflicts
   - Check for superseding/invalidating issues
   - If conflict found → HALT, report conflict

**Exemption Conditions:**
- This skill REQUIRES codebase verification (creates/modifies project files)
- This skill REQUIRES issue conflict check (creates specs)

# Skill Creator

Guide for creating effective skills that extend AI capabilities with specialized knowledge, workflows, and tool integrations.

## When to Use

- Creating a new skill for specialized domain knowledge
- Updating an existing skill with new workflows
- Bundling scripts, references, or assets for complex tasks

## Available Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete skill creation workflow with templates |

## Skill Anatomy

**⚠️ MANDATORY: All skills MUST have a `tasks/` subdirectory with at least one task file.**

Every skill consists of a required SKILL.md file, a required tasks/ subdirectory, and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description, license, compatibility)
│   ├── "Available Tasks" table (required)
│   └── Markdown instructions
└── tasks/ (required)
    └── overview.md (minimum required task)
```

Or with additional resources:

```
skill-name/
├── SKILL.md
│   ├── YAML frontmatter
│   ├── Available Tasks table
│   └── Overview content
├── tasks/
│   ├── overview.md (required)
│   └── other-task.md (optional additional tasks)
├── scripts/      # Python/Bash scripts
├── references/   # Reference documentation
└── assets/       # Templates, images, etc.
```

### Required Elements

| Element | Requirement | Location |
|---------|-------------|----------|
| YAML frontmatter | Required | Top of SKILL.md |
| "Available Tasks" table | Required | In SKILL.md |
| `tasks/` directory | Required | Skill directory |
| `tasks/overview.md` | Required | Minimum task |

### YAML Frontmatter Format

```yaml
---
name: skill-name
description: One-line description of skill purpose
license: MIT
compatibility: opencode
---
```

### Available Tasks Table Format

```markdown
## Available Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `overview` | Full skill content | ~500 |
| `task-name` | Specific task purpose | ~300 |
```

**Word counts help LLMs estimate context usage and complexity.**

## Bundled Resources

### Scripts (`scripts/`)

Executable code for tasks requiring deterministic reliability.

- **When to include**: Repeatedly rewritten code or deterministic operations
- **Example**: `scripts/rotate_pdf.py`
- **Note**: May still be read for patching

### References (`references/`)

Documentation loaded as needed into context.

- **When to include**: Detailed schemas, API docs, domain knowledge
- **Example**: `references/api_docs.md`

### Assets (`assets/`)

Files used in output, not loaded into context.

- **When to include**: Templates, images, boilerplate
- **Example**: `assets/logo.png`

## Progressive Disclosure

Skills use a three-level loading system:

1. **Overview loading**: SKILL.md loaded when `/skill <name>` invoked
2. **Task loading**: `tasks/<task>.md` loaded when `/skill <name> --task <task>`
3. **Reference loading**: Referenced files loaded as needed during skill execution

## Quick Start

Use `/skill skill-creator --task overview` for the complete creation workflow.