---
name: skill-creator
description: Use when creating a new skill or updating an existing skill that extends AI capabilities with specialized knowledge, workflows, or tool integrations. Triggers on: new skill, update skill, create skill, skill template, skill structure, SKILL.md.
license: Apache-2.0
compatibility: opencode
type: technique
---

# Skill Creator

## Overview

**Creating skills IS Test-Driven Development applied to process documentation.**

Write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**Source attribution:** TDD skill creation methodology, CSO principles, rationalization resistance tables, red flags lists, skill type taxonomy, bulletproofing patterns, and anti-patterns adapted from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md). Pressure scenario testing methodology adapted from [obra/superpowers `writing-skills/anthropic-best-practices.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/anthropic-best-practices.md) and [persuasion-principles.md](https://github.com/obra/superpowers/blob/main/skills/writing-skills/persuasion-principles.md).

## Persona

You are a Skill Design Expert. Your focus is helping users create well-structured skills that extend AI capabilities with specialized knowledge, workflows, and tools.

## Skill Type Taxonomy

Every skill falls into one of four types. Type determines how the skill should be written and tested.

| Type | Description | Follow Rigidity | Test Approach |
|------|-------------|-----------------|---------------|
| **Discipline-enforcing** | Rules that must be followed exactly (TDD, debugging, verification) | Follow exactly, don't adapt away discipline | Pressure scenarios with combined stresses |
| **Technique** | Concrete method with steps (condition-based-waiting, root-cause-tracing) | Follow steps, adapt details | Application scenarios, edge cases |
| **Pattern** | Way of thinking about problems (flatten-with-flags, information-hiding) | Apply principles flexibly | Recognition + application scenarios |
| **Reference** | Lookup tables, API docs, command guides | Find and apply | Retrieval + application scenarios |

**Why type matters:** Discipline-enforcing skills need rationalization resistance tables and red flags lists. Reference skills don't. Applying discipline-level rigor to a reference skill is overengineering; applying reference-level flexibility to a discipline skill invites failure.

**Frontmatter `type` field:** Add `type` to YAML frontmatter to declare the skill type:

```yaml
---
name: my-tdd-skill
description: Use when...
type: discipline-enforcing
---
```

Valid values: `discipline-enforcing`, `technique`, `pattern`, `reference`. Default: `technique`.

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills.

Write skill before testing? Delete it. Start over.
Edit skill without testing? Same violation.

**No exceptions:**
- Not for "simple additions"
- Not for "just adding a section"
- Not for "documentation updates"
- Don't keep untested changes as "reference"
- Don't "adapt" while running tests
- Delete means delete

## TDD Cycle for Skills (RED-GREEN-REFACTOR)

### RED: Write Failing Test (Baseline)

Run pressure scenario with subagent WITHOUT the skill. Document exact behavior:
- What choices did they make?
- What rationalizations did they use (verbatim)?
- Which pressures triggered violations?

This is "watch the test fail" — you MUST see what agents naturally do before writing the skill.

### GREEN: Write Minimal Skill

Write skill that addresses those specific rationalizations. Don't add extra content for hypothetical cases.

Run same scenarios WITH skill. Agent should now comply.

### REFACTOR: Close Loopholes

Agent found new rationalization? Add explicit counter. Re-test until bulletproof.

## Rationalization Resistance

Skills that enforce discipline need to resist rationalization. Agents are smart and will find loopholes when under pressure.

### Close Every Loophole Explicitly

**Source:** Adapted from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) and [`using-superpowers`](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md).

Don't just state the rule — forbid specific workarounds:

```markdown
# ❌ BAD: States rule only
Write code before test? Delete it.

# ✅ GOOD: Closes loopholes explicitly
Write code before test? Delete it. Start over.

No exceptions:
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete
```

### Address "Spirit vs Letter" Arguments

Add foundational principle early:

```markdown
Violating the letter of the rules IS violating the spirit of the rules.
```

This cuts off the entire class of "I'm following the spirit" rationalizations.

### Build Rationalization Table

Capture rationalizations from baseline testing. Every excuse agents make goes in the table:

```markdown
| Excuse | Reality |
|--------|---------|
| "Skill is obviously clear" | Clear to you ≠ clear to other agents. Test it. |
| "It's just a reference" | References can have gaps. Test retrieval. |
| "Testing is overkill" | Untested skills have issues. Always. |
| "I'll test if problems emerge" | Problems = agents can't use skill. Test BEFORE deploying. |
| "Too tedious to test" | Less tedious than debugging bad skill in production. |
| "I'm confident it's good" | Overconfidence guarantees issues. Test anyway. |
| "No time to test" | Deploying untested skill wastes more time fixing it later. |
```

### Create Red Flags List

Self-check for agents rationalizing:

```markdown
## Red Flags — STOP and Invoke the Skill

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
```

### Persuasion Principles for Skill Design

**Source:** Adapted from [obra/superpowers `persuasion-principles.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/persuasion-principles.md). Research foundation: Meincke et al. (2025), N=28,000 AI conversations. Persuasion techniques more than doubled compliance rates (33% → 72%, p < .001).

| Principle | Use For | Example |
|-----------|---------|---------|
| **Authority** | Discipline-enforcing | "YOU MUST", "Never", "Always", "No exceptions" |
| **Commitment** | Multi-step processes | Require announcements, force explicit choices, use tracking |
| **Scarcity** | Immediate verification | "Before proceeding", "Immediately after X" |
| **Social Proof** | Universal practices | "Every time", "Always", failure patterns |
| **Unity** | Collaborative workflows | "our codebase", "we're colleagues" |
| **Reciprocity** | Rarely needed | Use sparingly — can feel manipulative |
| **Liking** | Never for discipline | Conflicts with honest feedback culture |

**Principle combinations by skill type:**

| Skill Type | Use | Avoid |
|------------|-----|-------|
| Discipline-enforcing | Authority + Commitment + Social Proof | Liking, Reciprocity |
| Technique | Moderate Authority + Unity | Heavy authority |
| Pattern | Unity + Clarity | Authority |
| Reference | Clarity only | All persuasion |

## Claude Search Optimization (CSO)

**Source:** Adapted from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md).

### The Description Trap (CRITICAL)

**Description that summarizes workflow causes agents to follow the description instead of reading the full skill.**

When a description says "dispatches subagent per task with code review between tasks," agents follow that shortcut instead of reading the full skill with its flowchart showing two-stage review.

**Description must contain ONLY triggering conditions.**

```yaml
# ❌ BAD: Summarizes workflow — agents follow description, skip skill body
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD: Too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ✅ GOOD: Just triggering conditions, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session

# ✅ GOOD: Triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

### CSO Checklist

1. **Description field:** "Use when..." format, triggering conditions only, NO workflow summaries
2. **Keyword coverage:** Include error messages, symptoms, synonyms, tool names
3. **Descriptive naming:** Active voice, verb-first (`creating-skills` not `skill-creation`)
4. **Gerund convention:** Use gerunds for processes (`creating-skills`, `testing-skills`)
5. **Third person:** Write descriptions in third person (injected into system prompt)
6. **Token efficiency:** Move details to references, use cross-references, compress examples
7. **Target word counts:** getting-started <150, frequently-loaded <200, other skills <500

### What Keywords to Include

- Error messages: "Hook timed out", "ENOTEMPTY", "race condition"
- Symptoms: "flaky", "hanging", "zombie", "pollution"
- Synonyms: "timeout/hang/freeze", "cleanup/teardown/afterEach"
- Tool names: Actual commands, library names, file types

## About Skills

Skills are modular, self-contained packages that extend AI capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks — they transform OpenCode from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   ├── description: (required, max 1024 chars)
│   │   └── type: (optional, default: technique)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

**Metadata Quality:** The `name` and `description` in YAML frontmatter determine when OpenCode will use the skill. Be specific about triggering conditions. Write in third person. Description MUST start with "Use when..." and contain ONLY triggering conditions — NO workflow summaries (see CSO section above).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by OpenCode for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform OpenCode's process and thinking.

- **When to include**: For documentation that OpenCode should reference while working
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output OpenCode produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by OpenCode (Unlimited*)

*Unlimited because scripts can be executed without reading into context window.

## Skill Creation Process

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support?"
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message.

### Step 2: Planning the Reusable Skill Contents

Analyze each example by:
1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

### Step 3: Initializing the Skill

When creating a new skill from scratch, always run the `init_skill.py` script.

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates the skill directory, generates a SKILL.md template with proper frontmatter and TODO placeholders, creates example resource directories, and adds example files.

### Step 4: Edit the Skill

**Writing Style:** Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language.

To complete SKILL.md, answer:
1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. How should OpenCode use the skill? Reference all reusable skill contents.

### Step 5: TDD Testing (MANDATORY for Discipline-Enforcing Skills)

**Source:** Adapted from [obra/superpowers `testing-skills-with-subagents.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/testing-skills-with-subagents.md).

For discipline-enforcing skills, follow the RED-GREEN-REFACTOR cycle documented above. For other skill types, test with:

| Skill Type | Test Approach |
|------------|---------------|
| Discipline-enforcing | Pressure scenarios (3+ combined stresses) |
| Technique | Application scenarios, edge cases |
| Pattern | Recognition + application scenarios |
| Reference | Retrieval scenarios, gap testing |

#### Pressure Scenarios for Discipline Skills

Create scenarios combining 3+ pressure types:

| Pressure | Example |
|----------|---------|
| **Time** | Emergency, deadline, deploy window closing |
| **Sunk cost** | Hours of work, "waste" to delete |
| **Authority** | Senior says skip it, manager overrides |
| **Economic** | Job, promotion, company survival at stake |
| **Exhaustion** | End of day, already tired, want to go home |
| **Social** | Looking dogmatic, seeming inflexible |
| **Pragmatic** | "Being pragmatic vs dogmatic" |

**Best tests combine 3+ pressures.** Force explicit A/B/C choice, not open-ended questions. Make agent act, not hypothesize.

#### Testing Checklist (TDD Adapted)

**RED Phase - Write Failing Test:**
- [ ] Create pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Run scenarios WITHOUT skill - document baseline behavior verbatim
- [ ] Identify patterns in rationalizations/failures

**GREEN Phase - Write Minimal Skill:**
- [ ] Name uses only letters, numbers, hyphens (no parentheses/special chars)
- [ ] YAML frontmatter with required `name` and `description` fields (max 1024 chars)
- [ ] Description starts with "Use when..." and includes specific triggers/symptoms
- [ ] Description written in third person
- [ ] Description contains ONLY triggering conditions (NO workflow summaries)
- [ ] Keywords throughout for search (errors, symptoms, tools)
- [ ] Clear overview with core principle
- [ ] Address specific baseline failures identified in RED phase
- [ ] One excellent example (not multi-language)
- [ ] Run scenarios WITH skill - verify agents now comply

**REFACTOR Phase - Close Loopholes:**
- [ ] Identify NEW rationalizations from testing
- [ ] Add explicit counters (if discipline skill)
- [ ] Build rationalization table from all test iterations
- [ ] Create red flags list
- [ ] Re-test until bulletproof

**Quality Checks:**
- [ ] Small flowchart only if decision non-obvious
- [ ] Quick reference table
- [ ] Common mistakes section
- [ ] No narrative storytelling
- [ ] Supporting files only for tools or heavy reference

### Step 6: Packaging a Skill

```bash
scripts/package_skill.py <path/to/skill-folder>
```

The packaging script validates then creates a distributable zip.

### Step 7: Iterate

After testing the skill, users may request improvements.

### Step 8: Register Fragments (If Applicable)

If the skill contains duplicate content that appears in multiple skills, register fragments using the fragment-manager skill.

```yaml
# In registry.yaml
fragments:
  - id: branch-first-protocol
    master: .opencode/.guidelines/branch-first-protocol.md
    destinations:
      - .opencode/skills/git-workflow/tasks/pre-work.md
```

## Anti-Patterns

**Source:** Adapted from [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md).

| Anti-Pattern | Why Bad | Better |
|-------------|---------|--------|
| Narrative example ("In session 2025-10-03, we found...") | Too specific, not reusable | Generalized pattern |
| Multi-language dilution (example-js, example-py, example-go) | Mediocre quality, maintenance burden | One excellent example |
| Code in flowcharts | Can't copy-paste, hard to read | Markdown code blocks |
| Generic labels (helper1, helper2, step3) | Labels lack semantic meaning | Descriptive names |
| Workflow in description | Agents follow description, skip skill body | Triggering conditions only |

## Skill Creation Checklist (TDD Adapted)

**IMPORTANT:** Use todo tracking for EACH checklist item.

**RED Phase - Write Failing Test:**
- [ ] Create pressure scenarios (3+ combined pressures for discipline skills)
- [ ] Run scenarios WITHOUT skill - document baseline behavior verbatim
- [ ] Identify patterns in rationalizations/failures

**GREEN Phase - Write Minimal Skill:**
- [ ] Name uses only letters, numbers, hyphens
- [ ] YAML frontmatter with `name` and `description` (max 1024 chars)
- [ ] `type` field in frontmatter (discipline-enforcing, technique, pattern, reference)
- [ ] Description starts with "Use when..." and includes specific triggers/symptoms
- [ ] Description written in third person
- [ ] Description contains ONLY triggering conditions (NO workflow summaries)
- [ ] Keywords throughout for search (errors, symptoms, tools)
- [ ] Clear overview with core principle
- [ ] Address specific baseline failures identified in RED phase
- [ ] One excellent example (not multi-language)
- [ ] Run scenarios WITH skill - verify agents now comply

**REFACTOR Phase - Close Loopholes:**
- [ ] Identify NEW rationalizations from testing
- [ ] Add explicit counters (if discipline skill)
- [ ] Build rationalization table (Excuse | Reality format)
- [ ] Create red flags list for self-checking
- [ ] Re-test until bulletproof

**Deployment:**
- [ ] Commit skill to git and push
- [ ] Consider contributing back via PR (if broadly useful)

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `init_skill.py` | Create new skill from template | ~200 |
| `package_skill.py` | Package skill into distributable zip | ~150 |
| `quick_validate.py` | Validate skill structure and format | ~100 |

## Invocation

- `/skill skill-creator` - Overview and skill creation process
- `uv run python .opencode/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>` - Initialize new skill
- `uv run python .opencode/skills/skill-creator/scripts/package_skill.py <skill-folder> [output-dir]` - Package skill
- `uv run python .opencode/skills/skill-creator/scripts/quick_validate.py <skill-folder>` - Validate skill

## Operating Protocol

1. **Understand skill's purpose:** Help users clarify concrete examples of how the skill will be used
2. **Determine skill type:** Classify as discipline-enforcing, technique, pattern, or reference
3. **Plan reusable contents:** Identify scripts, references, and assets
4. **Initialize skill:** Run `init_skill.py` to create skill directory structure
5. **RED: Write failing test (baseline):** Run pressure scenarios WITHOUT skill, document failures
6. **GREEN: Write minimal skill:** Address baseline failures, verify compliance WITH skill
7. **REFACTOR: Close loopholes:** Add rationalization tables and red flags, re-test
8. **Validate skill:** Run `quick_validate.py` to ensure structure is correct
9. **Package skill:** Run `package_skill.py` to create distributable zip

## Cross-References

| Guideline | Section |
|-----------|---------|
| `080-code-standards.md` | Code quality standards |
| `000-critical-rules.md` | Critical violation enforcement |

| External Source | Content Adapted |
|----------------|-----------------|
| [obra/superpowers `writing-skills`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) | TDD methodology, CSO principles, rationalization resistance, skill types, anti-patterns |
| [obra/superpowers `testing-skills-with-subagents.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/testing-skills-with-subagents.md) | Pressure scenario testing methodology |
| [obra/superpowers `persuasion-principles.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/persuasion-principles.md) | Persuasion principles for skill design |
| [obra/superpowers `using-superpowers`](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md) | Red flags table pattern |