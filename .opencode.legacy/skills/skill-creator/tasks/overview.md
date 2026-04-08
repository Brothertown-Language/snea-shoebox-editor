# Task: overview

Guide for creating effective skills that extend AI capabilities with specialized knowledge, workflows, or tool integrations.

## When to Invoke

Use when:
- Users want to create a new skill
- Users want to update an existing skill
- Planning skill architecture for specialized domains

## Skill Anatomy

Every skill consists of:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation to load as needed
    └── assets/           - Files used in output
```

## Progressive Disclosure Design

Skills use three-level loading:
1. **Metadata** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed (unlimited)

## Creation Process

Follow in order:

### Step 1: Understanding with Examples

Understand concrete examples of usage:
- What functionality should the skill support?
- What would users say to trigger this skill?
- What are example use cases?

### Step 2: Planning Reusable Contents

Analyze each example:
- Identify what scripts, references, assets would help
- Example: PDF rotation → `scripts/rotate_pdf.py`
- Example: Webapp building → `assets/frontend-template/`
- Example: BigQuery → `references/schema.md`

### Step 3: Initializing the Skill

Run the init script:
```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates:
- SKILL.md template with TODO placeholders
- Example resource directories: scripts/, references/, assets/

### Step 4: Edit the Skill

Write in **imperative/infinitive form** (verb-first), not second person.

Complete SKILL.md by answering:
1. What is the purpose (few sentences)?
2. When should the skill be used?
3. How should OpenCode use the reusable contents?

Delete unused example files from scripts/, references/, assets/.

### Step 5: Packaging

Package into distributable zip:
```bash
scripts/package_skill.py <path/to/skill-folder>
```

Auto-validates before packaging:
- YAML frontmatter format
- Required fields (name, description)
- Naming conventions
- File organization

### Step 6: Iterate

Test on real tasks → notice struggles → improve SKILL.md or resources → repeat

## Resource Guidelines

### Scripts (scripts/)
- **Use**: Deterministic reliability, repeatedly rewritten code
- **Benefit**: Token efficient, may execute without context load
- **Note**: May need reading for patching

### References (references/)
- **Use**: Documentation to inform thinking
- **Examples**: schemas, API docs, domain knowledge, policies
- **Best practice**: Keep SKILL.md lean, move details to references
- **Avoid duplication**: Information lives in SKILL.md OR references, not both

### Assets (assets/)
- **Use**: Files used in output (templates, images, boilerplate)
- **Examples**: logos, PPT templates, HTML templates, fonts
- **Benefit**: Use without loading into context

## Cross-References

- Related: `implementation-quality` skill (for skill quality)
- Related: AGENTS.md (skill invocation)
- Tools: `scripts/init_skill.py`, `scripts/package_skill.py`