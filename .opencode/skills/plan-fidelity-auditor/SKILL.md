---
name: plan-fidelity-auditor
description: Generates a clean-room plan from scratch and compares it against the existing spec plan to identify discrepancies. Auto-updates the issue with corrections unless invoked with --check-only. Runs FIRST in the mandatory audit chain.
license: MIT
compatibility: opencode
---

# Skill: plan-fidelity-auditor

## Overview

Plan Fidelity Auditor generates a clean-room plan from scratch using only the problem statement from a spec issue, then compares it against the existing plan to identify discrepancies. Uses AI agent intelligence to differentiate simple auto-fixes from substantive changes requiring human review. Runs FIRST in the mandatory audit chain.

**Source Attribution:** New skill for the snea-shoebox-editor audit chain.

## Persona

You are a Plan Fidelity Auditor. Your focus is validating that spec plans faithfully and completely address the stated problem by generating an independent clean-room plan and comparing it against the existing plan.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `audit` | Full audit workflow (default) | ~800 |
| `compare` | Compare clean-room plan against existing plan | ~600 |
| `auto-fix` | Apply corrections to the issue | ~500 |

## Invocation

- `/skill plan-fidelity-auditor --issue N` — Full audit with auto-fix (default)
- `/skill plan-fidelity-auditor --issue N --check-only` — Audit without auto-fix (report only)
- `/skill plan-fidelity-auditor` — Overview only

## ⚠️ MANDATORY AUDIT CHAIN (ALL SKILLS RUN)

**When ANY request comes for spec/issue/task audit/review/revisit, ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `plan-fidelity-auditor` | Clean-room plan comparison, substantive gap detection |
| **2nd** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation |
| **3rd** | `spec-auditor` | Fresh-start context, completeness, content quality |

**CRITICAL: If you run ONE auditor, you MUST run ALL auditors in order.**

## What This Auditor Does

### Audit Workflow

1. **Read the spec issue** — Extract problem statement, context, constraints, success criteria
2. **Assess problem statement clarity** — If vague, trigger brainstorming (one question at a time)
3. **Generate clean-room plan** — Invoke `writing-plans --task clean-room` via subtask
4. **Compare plans** — Compare clean-room plan against existing issue plan
5. **Apply intelligence** — Differentiate simple fixes from substantive changes
6. **Auto-update or report** — Fix simple discrepancies, flag substantive ones, post findings

### Comparison Levels

| Level | What's Compared | Example |
|-------|----------------|---------|
| **Phase-level** | Missing phases, extra phases, phase ordering | Clean-room has "Database Schema" phase not in original |
| **Step-level** | Missing steps, extra steps, step ordering | Clean-room has "Add index" step not in original |
| **Content-level** | Different approaches, missing edge cases, wrong assumptions | Clean-room covers pagination edge case not in original |

### Semantic Matching

The auditor attempts **semantic matching** before reporting differences:
- "User Schema" vs "Database Tables" → **matching** (same concept, different naming)
- "Authentication Setup" vs "OAuth2 Integration" → **matching** if OAuth2 is the auth method
- "API Endpoints" vs "REST API" → **matching** (same concept)

Only **substantive differences** after semantic matching are reported.

### Auto-Fix Intelligence

| Discrepancy Type | Action | Rationale |
|-----------------|--------|-----------|
| Missing file references | **Auto-fix** | Simple addition, no scope expansion |
| Discovered repo changes | **Auto-fix** | Spec needs updating for current codebase |
| Additional affected files | **Auto-fix** | Completeness improvement |
| Missing phases | **Flag for human** | Substantive scope change |
| Different approaches | **Flag for human** | Architectural decision needed |
| Ordering differences | **Flag for human** | May be intentional dependency order |
| Extra scope | **Flag for human** | Scope expansion requires approval |

### Vague Problem Statement Handling

If the problem statement extracted from the spec is vague:

1. **Trigger brainstorming** — Invoke `/skill brainstorming` in one-question-at-a-time mode
2. **Resolve vagueness** — Ask questions until the problem is clearly stated
3. **Proceed** — Use the clarified problem statement for clean-room generation
4. **Document** — Post the clarified problem statement as a comment on the issue

### Operating Modes

#### Mode 1: Auto-fix (default)

Run without `--check-only`. Automatically:
1. Generate clean-room plan
2. Compare against existing plan
3. Auto-fix simple discrepancies (additional files, discovered changes)
4. Flag substantive discrepancies for human review
5. Post GitHub comment with executive summary and link

#### Mode 2: Check-only (`--check-only`)

Run with `--check-only` flag. Generate comparison report only:
1. Generate clean-room plan
2. Compare against existing plan
3. Post findings as GitHub comment (no issue updates)
4. **Do NOT modify the issue**

## Clean-Room Plan Generation

### Process

1. **Extract problem statement** from the spec issue (Objective, Problem Statement, Context, Constraints, Success Criteria sections only)
2. **Write extracted content** to `./tmp/clean-room-input.md`
3. **Invoke writing-plans subtask:**
   ```
   task(
     subagent_type="general",
     description="Generate clean-room plan for issue N",
     prompt="Use the writing-plans skill --task clean-room to generate a plan from the problem statement in ./tmp/clean-room-input.md. The plan should address ONLY the problem stated, with no knowledge of the existing plan. Return the generated plan as structured markdown."
   )
   ```
4. **Read the clean-room plan** from subtask output
5. **Compare** against existing plan using the `compare` task

### Clean-Room Input Isolation

The clean-room plan MUST be generated from:
- **ONLY** the problem statement, context, constraints, and success criteria from the issue
- **NOT** the existing phases, steps, or implementation details
- **NOT** any other issues, comments, or external context

This ensures the clean-room plan is truly independent and can catch gaps the original author missed.

### Subtask Context

```yaml
# Context received by writing-plans subtask
problem_statement: "<extracted from issue>"
context: "<extracted from issue>"
constraints: "<extracted from issue>"
success_criteria: "<extracted from issue>"
existing_files: "<from codebase exploration>"
clean_room: true  # Flag: skip approval gate, skip existing plan reference

# Context yielded by the subtask
status: "success|failure"
plan: "<generated plan markdown>"  # If success
error: "<error message>"  # If failure
```

## Division of Responsibility

| Auditor | Scope | Runs When |
|---------|-------|----------|
| **plan-fidelity-auditor** | Substantive correctness, missing content, scope alignment | **FIRST** - before structure/content |
| **concern-separation-auditor** | Phase structure, deployment independence, risk isolation | **SECOND** - after content fidelity |
| **spec-auditor** | Fresh-start context, completeness, content quality | **THIRD** - after structure passes |

## What This Auditor Owns

| Check | Problem Class | Auto-Fix? | Description |
|-------|---------------|-----------|-------------|
| Missing phases | `MISSING_PHASE` | Flag for human | Clean-room identifies phase not in original |
| Extra phases | `EXTRA_PHASE` | Flag for human | Original has phase not in clean-room (may be scope creep) |
| Missing steps | `MISSING_STEP` | Auto-fix if simple | Clean-room identifies step not in original |
| Extra steps | `EXTRA_STEP` | Flag for human | Original has step not in clean-room |
| Different approaches | `APPROACH_DIFFERENCE` | Flag for human | Same goal, different implementation approach |
| Missing edge cases | `MISSING_EDGE_CASE` | Flag for human | Clean-room covers edge case not in original |
| Missing file references | `MISSING_FILE_REF` | Auto-fix | Clean-room identifies affected files not in original |
| Ordering differences | `ORDERING_DIFFERENCE` | Flag for human | Steps in different order |
| Scope expansion | `SCOPE_EXPANSION` | Flag for human | Clean-room is significantly larger than original |
| Vague problem statement | `VAGUE_PROBLEM` | Trigger brainstorming | Problem statement is too vague for comparison |

## GitHub Comment Format

### Auto-fix Mode (Executive Summary)

```
## Plan Fidelity Audit

**Summary:** <1-2 sentences describing findings and impact>

**Outcome:** <What changed for stakeholders — link to revised spec or "no changes needed">

### Auto-Fixed
- <list of simple fixes applied>

### Flagged for Review
- <list of substantive changes requiring human decision>

---
🤖 ✅ Completed by <AgentName> (<ModelID>): Plan Fidelity Auto-Audit
```

### Check-Only Mode

```
## Plan Fidelity Check (Report Only)

**Summary:** <1-2 sentences describing findings>

**Outcome:** No changes applied (--check-only mode)

### Discrepancies Found
- <list of all discrepancies>

---
🤖 📝 Updated by <AgentName> (<ModelID>): Plan Fidelity Check
```

## Integration with writing-plans

The plan-fidelity-auditor invokes `writing-plans --task clean-room` as a subtask:

```yaml
# Subtask invocation
skill: writing-plans
task: clean-room
input: ./tmp/clean-room-input.md  # Problem statement only
output: structured plan markdown
skip_approval: true  # Clean-room plans don't need approval
skip_existing_plan: true  # Don't reference existing plan
```

The `clean-room` task in writing-plans MUST:
- Read only the problem statement from the provided input
- Not reference any existing plan or spec details
- Generate an independent plan based solely on the stated problem
- Return structured markdown that can be parsed for comparison

## Edge Cases

| Scenario | Action |
|----------|--------|
| Clean-room generation fails | Report failure, continue with remaining auditors (don't block chain) |
| No existing plan (new spec) | Compare clean-room against spec's phase structure directly |
| `--check-only` mode | Report findings as comment only, do NOT update issue |
| Clean-room identical to existing | Report "no discrepancies found" and proceed |
| Existing plan superior | Report as negative discrepancy (original has more coverage) |
| Vague problem statement | Trigger brainstorming (one question at a time), then proceed |
| Clean-room much larger | Report as "scope concern" in executive summary, don't auto-expand |

## Mandatory Invocation (NO SKIPPING)

**AI agents creating or auditing specs MUST invoke this auditor. NO EXCEPTIONS.**

Updated workflow:

```
1. Create/audit spec issue
2. Invoke /skill plan-fidelity-auditor --issue N (FIRST - plan fidelity)
3. Invoke /skill concern-separation-auditor --issue N (SECOND - phase structure)
4. Invoke /skill spec-auditor --issue N (THIRD - content quality)
5. Apply fixes from all auditors
6. Add needs-approval label
7. Post "ready for review" comment
```

**Skipping this auditor is a CRITICAL GUIDELINE VIOLATION.**

## Failure Recovery

If the writing-plans subtask fails:

1. **Log the failure** in the audit comment
2. **Post a warning** that plan fidelity could not be verified
3. **Continue** with remaining auditors (concern-separation, spec-auditor)
4. **Do NOT block** the audit chain on clean-room generation failure

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs (unless auto-fix mode)
- Edits limited to spec content via GitHub Issue updates
- No changes to project source code
- No new specs or expansions beyond what auto-fix requires
- Must use GitHub MCP tools for all issue operations

## Cross-References

- Related skills: `writing-plans` (clean-room generation), `brainstorming` (vague input resolution), `concern-separation-auditor` (2nd in chain), `spec-auditor` (3rd in chain)
- Related guidelines: `000-critical-rules.md` (auditor enforcement), `140-planning-spec-creation.md` (spec structure)