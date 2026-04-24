# Task: explore/exploration-workflow

## Purpose

Explore project context, check scope, potentially decompose project, and conduct interactive Q&A to gather requirements before spec creation.

## Entry Criteria

- Pre-spec inspection completed (or exempt)
- No full-supersession conflicts identified

## Exit Criteria

- Project context explored and documented
- Scope assessed and decomposition decided (if applicable)
- Design incrementally approved by user
- `spec-creation` skill invoked as terminal state

## Procedure

### Step 1: Explore Project Context

Check current project state:
- Files, docs, recent commits (`srclight_recent_changes(n=10)`)
- Existing patterns, reusable components
- README, CHANGELOG, relevant documentation
- **Reference code inspection results from Step 0** — do not re-investigate

### Step 2: Scope Check

**Multi-subsystem request:** e.g., "build a platform with chat, file storage, billing, and analytics"
- Flag immediately
- Help decompose into sub-projects
- Brainstorm the first sub-project through normal flow

**Agent intelligence decision (autonomous, NOT asking user):**
- One clear concern → single-task spec, no question
- Clear sequential phases → multi-task with phases, no question
- Ambiguous trade-offs only (3+ subsystems with unclear boundaries) → ask user

### Step 3: Offer Visual Companion (CONDITIONAL)

**STRICTLY CONDITIONAL** — only when topic involves visual/Spatial decisions (UI layouts, mockups, diagrams).

> "Want to try a web-based companion for mockups and diagrams?"

If declined: proceed text-only. For backend/Python projects, rarely applies.

### Step 4: Ask Clarifying Questions — ONE AT A TIME

**STRICTLY ONE question per message.**

Rules:
- One question per message — NEVER multiple questions
- Prefer multiple choice when possible
- Questions follow from user's answers
- Dimensions are INTERNAL mental checklist only — never exposed as output sections
- Simple fixes skip straight to design

### Per-Item Developer Confirmation Gate (MANDATORY)

After each significant finding discovered during Q&A, the agent MUST:
1. **Present the finding** — clearly state what was discovered
2. **Ask for confirmation** — "Does this align with your intent?"
3. **Wait for developer response** — must confirm, modify, or reject
4. **Track confirmation state** — confirmed items become part of exploration output

**Prohibited patterns:**
- Listing multiple findings then asking "Does this all look right?"
- Presenting complete investigation without confirmed individual findings

**Turn tracking:** Each substantial Q&A exchange (one agent question + one developer response with real content) = one interactive turn. **Minimum threshold: 2 interactive turns.** "Yes"/"No"/"OK" without substance do NOT count.

**Deep analysis expectation:** Explore pros, cons, what-ifs, however, counterpoints. Brainstorming is thorough back-and-forth including:
- Challenge assumptions ("What happens if this fails?")
- Edge cases and second-order effects
- Counterarguments to proposals
- Trade-offs explicitly discussed

### Step 5: Propose 2-3 Approaches (Significant Decisions Only)

- **Significant decisions:** Multiple approaches with meaningful trade-offs → propose 2-3
- **Simple fixes:** One obvious approach → skip alternatives, go straight to design

Present conversationally with recommendation and reasoning. Lead with recommended option.

### Step 6: Present Design Incrementally

- Present section by section, asking after each whether it looks right
- Scale each section: a few sentences if straightforward, 200-300 words if nuanced
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify

**Working in existing codebases:**
- Explore current structure first
- Follow existing patterns
- Targeted improvements only where they serve the current goal
- No unrelated refactoring

⚠️ **HARD GATE:** Design approval is NOT spec completion. The design is raw input TO `spec-creation`.

### Step 7: Transition to spec-creation

**Terminal state: invoking spec-creation.**

> "Exploration complete. I'll now invoke the spec-creation skill to structure and write the spec from our investigation results."

`spec-creation` handles:
- Requirements extraction, problem decomposition
- Interface-first thinking, traceability mapping
- Spec writing, self-review, user review

**Separation:** Exploration and structuring are distinct concerns with distinct discipline.

## Top-Down Analysis Output

When exploration is complete, output MUST include top-down decomposition for `writing-plans --task create`:

| Scope | Starting Point |
| -- | -- |
| GREENFIELD | Project spec (no existing code) |
| NEW_FEATURE | Existing code + feature request |
| FIX | Existing code + bug report |
| ENHANCEMENT | Existing code + change request |

**Required output:**
1. Item enumeration — each implementation unit with name, scope, deliverable
2. Dependency graph — which items depend on which
3. Acceptance criteria per item — testable criteria
4. Concern boundary annotations — flag crossing-architectural-concern items

## Verification-Mechanics Prompting (Conversational)

When a requirement is identified during Q&A, prompt about verifiability:

- Developer: "The script should exit with an error code when validation fails."
- Agent: "Got it. What would you check to confirm this? For instance, would you run a specific command and check for a particular exit code?"

This is conversational — follows from developer's answer, not a predetermined checklist.

## Context Required

- Related skill: `spec-creation` (terminal step)
- Related task: `explore/pre-spec-inspection`