# Task: clean-room

## Purpose

Generate a clean-room implementation plan from a problem statement only, using prose-driven exploration rather than template structure. Used by the spec-auditor's fidelity subtask to create an independent plan for comparison against the existing spec.

## Operating Protocol

1. **Invoked by:** `spec-auditor` fidelity subtask (not by users directly)
2. **Bypasses:** Approval gate (clean-room plans don't need approval — they're comparison artifacts)
3. **Does NOT reference:** Any existing plan, spec phases, or spec steps

## Entry Criteria

- Problem statement input file exists at `./tmp/clean-room-input-N.md`
- Problem statement contains: Objective, Problem Statement, Context, Constraints, Success Criteria
- The writing-plans skill is available

## Exit Criteria

- Clean-room plan generated as prose structured markdown
- Plan returned to the invoking subtask context
- No issue created (clean-room plans are comparison artifacts, not tracked in GitHub)

## Key Differences from Standard Plan Creation

| Aspect | Standard Plan (`--task create`) | Clean-Room Plan (`--task clean-room`) |
| -- | -- | -- |
| Input source | Approved spec issue | Problem statement only (from temp file) |
| References existing plan | May reference spec phases | **NEVER references existing plan** |
| Creates GitHub issue | Yes | **No** — returned as markdown only |
| Requires approval | Yes (`needs-approval` label) | **No** — comparison artifact |
| Skip approval gate | No | **Yes** — not an implementation plan |
| Structure | Agent-chosen prose | Agent-chosen prose (no template) |
| Persists after comparison | Yes (tracked) | **No** — deleted after comparison |

## Procedure

### Step 1: Read Problem Statement

**Read the clean-room input file:**

```
Read: ./tmp/clean-room-input-N.md
```

**Extract what's available:**

- Objective
- Problem Statement
- Context
- Constraints
- Assumptions (if present)
- Success Criteria
- Edge Cases (if present)
- Dependencies (if present)
- Risk Assessment (if present)

**Note:** Not all sections will be present. Work with what's available.

### Step 2: Explore Codebase (If Applicable)

**For files and patterns mentioned in the problem statement:**

- Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant code
- Identify affected files, modules, and patterns
- Note existing patterns that should be followed

**Important:** This exploration uses ONLY the problem statement, not the existing spec's phases or steps.

### Step 3: Generate Independent Plan (Prose-Driven)

**Generate a plan based solely on the problem statement and codebase exploration.**

**Prose-driven approach:** The agent writes the plan naturally, deciding what sections and what structure makes sense for this specific problem. No template is imposed.

**Quality requirements:**

- Phase names describe **specific concerns**, NOT generic activities
- Each step is **actionable** (not abstract goals)
- Verification methods included where appropriate
- Affected files listed based on codebase exploration
- Edge cases from problem statement are addressed
- **No TBD, TODO, or placeholder content**

**When significant gaps emerge:** Recommend brainstorming rather than just flagging the gap. A gap in understanding means the problem statement needs more exploration, not that the clean-room plan should have a placeholder.

### Step 4: Validate Plan

**Check for prohibited patterns:**

- No `TBD`, `TODO`, `[to be determined]`, `[placeholder]`
- All phases have specific concern names (not "Implementation", "Testing")
- All steps are actionable
- Success criteria are testable

**If validation fails:**

- Re-generate the missing sections
- Do NOT leave placeholders

### Step 5: Yield Results

**Return the plan as structured markdown to the invoking subtask:**

```yaml
# Yield-back context
status: success|failure
plan: <complete plan markdown>    # If success
error: <error message>    # If failure
phases_count: N
steps_count: M
affected_files_count: K
```

**If failure:**

- Return error message
- Do NOT create a partial plan
- Do NOT create a GitHub Issue

**If significant gaps found:**

- Include recommendation for brainstorming in the yield-back context
- The fidelity subtask can use this recommendation when reporting findings

## Scope Boundaries

- **NO** GitHub Issue creation — plan is returned as markdown only
- **NO** approval gate — clean-room plans are comparison artifacts
- **NO** reference to existing plan — independent generation only
- **YES** codebase exploration — to identify affected files and patterns
- **YES** prose-driven output — agent decides structure, not template
- **YES** brainstorming recommendation — when gaps are significant

## Cross-References

- Invoked by: `spec-auditor` fidelity subtask
- Related tasks: `create` (standard plan creation), `validate` (plan validation)
- Related skills: `spec-auditor` (orchestrator), `brainstorming` (recommended when gaps found)

Co-authored with AI: <AI-Name> (<model-id>)
