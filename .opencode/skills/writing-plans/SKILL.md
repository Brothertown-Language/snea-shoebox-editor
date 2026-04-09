---
name: writing-plans
description: Use when creating an implementation plan from an approved spec. Produces prose plans with zero placeholders. Triggers on: write plan, create plan, implementation plan, plan spec, approved plan, plan creation.
license: MIT
compatibility: opencode
---

# Skill: writing-plans

## Overview

Plan creation workflow that transforms approved specs into actionable implementation plans. Plans use a hybrid structure: **phases** for sub-issue tracking and cross-phase visibility, **TDD steps** within each task for granular execution guidance. Every step is one action (2-5 minutes) with exact code and commands. Placeholders are forbidden in plans.

**Source attribution:** TDD step granularity, no-placeholders rule, plan document header, file structure section, and self-review checklist are adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

**Core shift from v2:** Plans are prose at the phase/section level, but each task within a phase uses TDD step granularity with exact code, exact commands, and checkbox tracking. Phase structure is maintained for sub-issue alignment.

## Persona

You are an Implementation Planner. Your focus is transforming approved design specs into complete, actionable implementation plans with TDD steps, testability, and verification evidence — phases for tracking, steps for execution.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `create` | Create plan from approved spec | ~800 |
| `validate` | Check for placeholders and completeness | ~500 |
| `retroactive` | Create plan for existing spec | ~600 |
| `clean-room` | Generate independent plan from problem statement only (prose-driven) | ~500 |

## Invocation

- `/skill writing-plans` — Overview only
- `/skill writing-plans --task create` — Create plan from current spec
- `/skill writing-plans --task validate` — Validate existing plan
- `/skill writing-plans --task retroactive` — Create plan for existing spec
- `/skill writing-plans --task clean-room` — Generate clean-room plan (for comparison by spec-auditor)

## Hybrid Structure: Phases + TDD Steps

Plans use a **hybrid structure** that preserves phase-based organization (for sub-issue tracking) while adding TDD step granularity within each task:

- **Phases** align with sub-issues for tracking and progress visibility
- **Tasks** within phases are concrete implementation units
- **TDD Steps** within tasks are bite-sized (2-5 minutes each) with exact code and commands

```
Phase 1: [Concern Name]
  Task 1: [Component Name]
    Step 1: Write the failing test
    Step 2: Run test to verify it fails
    Step 3: Write minimal implementation
    Step 4: Run test to verify it passes
    Step 5: Commit
  Task 2: [Component Name]
    ...

Phase 2: [Concern Name]
  ...
```

### Prose-Driven at Phase Level, Precise at Step Level

- **Phase-level sections** are prose — agent decides section names and content
- **Task-level steps** are TDD-granular with exact code and commands
- The agent decides which sections the plan needs at the phase level
- Within tasks, the TDD step structure is required, not optional

### What the Agent Decides

1. **Phase organization** — Based on concern flow and dependency
2. **Section order** — Based on dependency flow, not template order
3. **Level of detail per phase** — Complex phases need more tasks, simple ones need fewer
4. **Additional sections** — Operational requirements, data migration, etc.

## Plan Document Header

Every plan MUST start with this header:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use writing-plans skill for plan creation, executing-plans skill for implementation.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

Adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## File Structure Section

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This locks in decomposition decisions.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility
- Prefer smaller, focused files over large ones that do too much
- Files that change together should live together. Split by responsibility, not by technical layer
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure — but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

Adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## Task Structure

Each task within a phase follows this TDD step structure:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

Adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

### Step Granularity Rules

- Each step is **one action** (2-5 minutes)
- "Write the failing test" is a step, not "set up testing"
- "Run test to verify it fails" is a step — never skip verification
- "Write minimal implementation" means the **smallest code** that makes the test pass
- Every code step shows **complete code**, not descriptions of code
- Every command step shows **exact command** with expected output
- Commit steps show **exact git commands** with meaningful messages

## No-Placeholders Rule (CRITICAL)

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:

### Prohibited Placeholder Patterns

| Pattern | Why Prohibited |
|---------|----------------|
| `TBD` | Incomplete plan |
| `TODO` | Incomplete plan |
| `[to be determined]` | Incomplete plan |
| `[needs investigation]` | Investigation should be in spec |
| `[placeholder]` | Incomplete plan |
| `[requires research]` | Research should be in spec |
| `implement later` | Plan not actionable |
| `fill in details` | Details must be specified |
| `Add appropriate error handling` | Must specify actual code (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |
| `Add validation` / `Handle edge cases` | Must specify actual code (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |
| `Write tests for the above` | Must include actual test code (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |
| `Similar to Task N` | Must repeat the code — engineer may read tasks out of order (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |
| Steps describing what to do without showing how | Code blocks required for code steps (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |
| References to types/functions not defined in any task | All referenced symbols must be defined (adapted from [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)) |

### Specs vs Plans

| Artifact | Placeholders Allowed? | Examples |
|----------|----------------------|----------|
| Spec (GitHub Issue) | YES, during iterative development | TBD, TODO, [needs investigation], [placeholder] |
| Plan (for implementation) | NO — zero tolerance | None allowed before implementation begins |

### Validation Logic

```python
INVALID_PATTERNS = [
    "TBD", "TODO", "tbd", "todo",
    "[to be determined]", "[needs investigation]",
    "[placeholder]", "[requires research]",
    "implement later", "fill in details",
]

def validate_plan(plan_content: str) -> bool:
    for pattern in INVALID_PATTERNS:
        if pattern in plan_content:
            return False
    return True
```

Adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## Self-Review Checklist

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red-flag patterns (TBD, TODO, vague instructions). Fix them.

**3. Type consistency:** Do types, method signatures, and property names used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

Adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## Task: create

### Prerequisites
1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

### Creation Steps

1. **Read approved spec:**
   - Query GitHub Issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

2. **Map file structure:**
   - List all files that will be created or modified
   - Define each file's responsibility
   - Ensure decomposition has clear boundaries

3. **Plan phase structure by judgment:**
   - Determine which phases the plan needs
   - Organize by concern flow, not template order
   - Write prose for phase descriptions

4. **Define tasks within each phase:**
   - Each task uses the TDD step structure
   - Each step is one action (2-5 minutes)
   - Exact code, exact commands, exact file paths

5. **Write plan document header:**
   - Goal, Architecture, Tech Stack

6. **Create plan issue:**
   - Title: `[PLAN] <Feature Name>`
   - Body: Plan with header, file structure, phases with TDD tasks
   - Link to parent spec (sub-issue)

7. **Self-review:**
   - Spec coverage check
   - Placeholder scan
   - Type consistency check
   - Fix any issues found

8. **Validate plan:**
   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable

## Task: validate

Check an existing plan for:

1. **Placeholder detection** — Zero TBD/TODO tolerance
2. **Completeness** — Plan addresses the stated problem
3. **Actionability** — Steps are concrete, not abstract goals
4. **Testability** — Success criteria are measurable
5. **TDD structure** — Each task has failing test → implement → passing test steps
6. **File structure** — All files are listed with responsibilities
7. **Self-review evidence** — Agent has performed spec coverage, placeholder, and type consistency checks

Does NOT enforce a specific section order. A plan without "Risks" is valid if risks are addressed elsewhere or are not relevant.

## Task: retroactive

For existing specs without plans:

1. **Query existing spec:**
   - Get spec from GitHub Issue
   - Check for linked plan (sub-issues)

2. **If no plan exists:**
   - Create plan from spec using hybrid approach (phases + TDD steps)
   - Include header, file structure, self-review
   - Link as sub-issue
   - HALT and wait for plan approval

3. **If plan exists:**
   - Validate plan (check for placeholders, TDD structure)
   - If invalid → Report issues
   - If valid → Proceed to implementation

## Task: clean-room

### Purpose

Generate an independent plan from the problem statement only, with no knowledge of any existing plan. Used by spec-auditor's fidelity subtask for comparison against the existing spec.

**Key v3 change:** Clean-room generation uses hybrid approach (phases + TDD steps within each task) but still uses prose-driven organization at the phase level.

### Entry Criteria

- Problem statement input file exists at `./tmp/clean-room-input-N.md`
- Problem statement contains: Objective, Problem Statement, Context, Constraints, Success Criteria
- The writing-plans skill is available

### Exit Criteria

- Clean-room plan generated with header, file structure, phases, and TDD tasks
- Plan returned to the invoking subtask context
- No issue created (clean-room plans are comparison artifacts, not tracked in GitHub)

### Key Differences

| Aspect | Standard Plan (`--task create`) | Clean-Room Plan (`--task clean-room`) |
|--------|-------------------------------|--------------------------------------|
| Input source | Approved spec issue | Problem statement only (from temp file) |
| References existing plan | May reference spec phases | NEVER references existing plan |
| Creates GitHub issue | Yes | No — returned as markdown only |
| Requires approval | Yes (`needs-approval` label) | No — comparison artifact |
| Structure | Phases + TDD tasks | Phases + TDD tasks (hybrid) |
| Skip approval gate | No | Yes — not an implementation plan |

### Procedural Steps

1. **Read problem statement** from `./tmp/clean-room-input-N.md`
2. **Explore codebase** (if applicable) — find relevant files and patterns
3. **Map file structure** — list files, responsibilities, interfaces
4. **Generate independent plan** using hybrid approach — phases with TDD tasks
5. **When significant gaps emerge**, recommend brainstorming rather than just flagging
6. **Validate** — no placeholders, TDD steps, specific concern names, actionable code
7. **Self-review** — spec coverage, placeholder scan, type consistency
8. **Yield results** — return as structured markdown

### Clean-Room Output Format

- Plan document header (goal, architecture, tech stack)
- File structure section
- Phases with concern-specific names (NOT generic activities)
- Each task within phases uses TDD step structure
- Success criteria are testable
- No TBD, TODO, or placeholder content

### Scope Boundaries

- **NO** GitHub Issue creation
- **NO** approval gate
- **NO** reference to existing plan
- **YES** codebase exploration
- **YES** hybrid phase + TDD task output

## Enforcement Mechanism

**Skills MUST enforce plan completeness — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before implementation:**
   - Does plan exist?
   - Is plan approved?
   - Is plan valid (no placeholders)?
   - Does plan have TDD step structure (failing test → implement → passing test)?
   - Does plan have file structure section?
   - Does plan have header (goal, architecture, tech stack)?

2. **Enforcement matrix:**
   - No plan → CREATE plan (writing-plans skill)
   - Plan exists but unapproved → HALT, wait for approval
   - Plan approved but has placeholders → REJECT plan, require completion
   - Plan approved but missing TDD steps → REJECT plan, require TDD structure
   - Plan approved and complete → PROCEED to implementation

## Integration with Existing Workflow

### Dispatch Order
```
approval-gate → writing-plans (create) → approval-gate (plan) → git-workflow
```

### Approval Gate Integration
- Plan creation happens AFTER spec approval
- Plan requires separate approval (`approved: plan`)
- Implementation cannot start until BOTH spec AND plan are approved

## Cross-References

- Related skills: `brainstorming` (pre-spec), `approval-gate` (authorization), `executing-plans` (implementation), `spec-auditor` (fidelity subtask uses clean-room)
- Source attribution: TDD step structure, no-placeholders rule, plan document header, file structure section, and self-review checklist adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)

## Key Differences from v2

| v2 (Prose-Driven) | v3 (Hybrid: Phases + TDD Steps) |
|----------------------|-------------------|
| Prose-only plans | Phases with prose descriptions, tasks with TDD steps |
| No step granularity | Each step is one action (2-5 minutes) |
| Template reference only | Required task structure with TDD steps |
| No file structure section | File structure required before tasks |
| No plan document header | Header with goal, architecture, tech stack required |
| No self-review checklist | Self-review (coverage, placeholders, types) required |
| Validation checks placeholders only | Validation checks placeholders + TDD structure + file structure |
| Clean-room uses prose-only | Clean-room uses hybrid phase + TDD structure |

Co-authored with AI: OpenCode (ollama-cloud/glm-5)