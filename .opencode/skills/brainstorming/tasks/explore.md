# Task: explore

Full conversational exploration workflow for requirements gathering before spec creation.

## Process Flow

<!-- Original dot digraph below is superseded by the yaml+symbolic state machine block at the end of this file. -->

```dot
digraph brainstorming {
    "Explore project context" -> "Scope check";
    "Scope check" -> "Decompose project" [label="multi-subsystem"];
    "Scope check" -> "Visual questions ahead?" [label="single scope"];
    "Decompose project" -> "Visual questions ahead?";
    "Visual questions ahead?" -> "Offer Visual Companion\n(own message)" [label="yes"];
    "Visual questions ahead?" -> "Ask clarifying questions\n(one at a time)" [label="no"];
    "Offer Visual Companion" -> "Ask clarifying questions\n(one at a time)";
    "Ask clarifying questions" -> "Propose 2-3 approaches\n(significant decisions only)";
    "Propose 2-3 approaches" -> "Present design incrementally\n(section by section)";
    "Present design incrementally" -> "User approves?";
    "User approves?" -> "Present design incrementally" [label="no, revise"];
    "User approves?" -> "Invoke spec-creation" [label="yes"];
}
```

## Step 1: Explore Project Context

Check current project state before asking any questions:

- Files, docs, recent commits
- Existing patterns, reusable components
- README, CHANGELOG, and relevant documentation

## Step 2: Scope Check

Before asking detailed questions, assess scope:

- If the request describes **multiple independent subsystems** (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately
- Help the user **decompose into sub-projects**: what are the independent pieces, how do they relate, what order should they be built?
- Then brainstorm the first sub-project through the normal flow
- Each sub-project gets its own spec → plan → implementation cycle

### Autonomous Structural Classification (MANDATORY)

Structural classification — single-task vs multi-task, phase decomposition — is an **agent intelligence concern**. Resolve it autonomously. Do NOT ask the user to make this decision.

**Ask the user when**: Multiple valid structures exist with meaningful trade-offs that only the user can resolve:
- 3+ subsystems with unclear boundaries or interdependencies
- Ambiguity about whether a subsystem is in-scope or out-of-scope
- Multiple valid decomposition orders where business priority is genuinely unclear

**Do NOT ask the user when**: One structure is clearly appropriate:
- Focused rule addition, single-file change, or bug fix with obvious scope → single-task, no question
- Request naturally decomposes into sequential phases with clear boundaries → multi-task with phased structure, no question
- The agent can determine scope from context, codebase, or the request itself → autonomous decision, no question

**Prohibited questions** (examples of what NOT to ask):
- "Should this be a single-task spec or broken into phases?"
- "Is this a small change or a big one?"
- "Do you want this as one spec or multiple?"

When in doubt, classify autonomously and state the classification as part of your design proposal. The user can override during design review — but the default is agent-resolved.

## Step 3: Offer Visual Companion (Conditional)

**STRICTLY CONDITIONAL** — only when the topic clearly involves visual decisions (UI layouts, visual mockups, architecture diagrams).

If you anticipate visual questions ahead, offer the companion as **its own message**, combined with nothing else:

> "Some of what we're working on might be easier to explain if I can show it to you in a web browser — mockups, diagrams, comparisons. Want to try that?"

Wait for the user's response. If they decline, proceed with text-only brainstorming.

**For this project** (backend/Python), visual companion will rarely apply. Do NOT offer it by default.

## Step 4: Ask Clarifying Questions — ONE AT A TIME

**STRICTLY ONE question per message.** This is the core behavioral change.

Rules:

- One question per message — NEVER ask multiple questions in one message
- Prefer multiple choice when possible, but open-ended is fine
- Questions follow from the user's answers, not from a predetermined dimension list
- Dimensions are an INTERNAL mental checklist only — never exposed as structured output sections
- Simple fixes skip straight to design without requiring alternatives analysis
- YAGNI ruthlessly — remove unnecessary features from all designs

**Internal Dimensions Checklist** (reference only, never exposed as output sections):

| Dimension | When to Think About It | When to Skip |
| -- | -- | -- |
| Problem Understanding | Always | Never |
| User Requirements | When there are end users | Bug fixes with no user-facing change |
| Alternatives Analysis | When multiple approaches exist | Simple fixes with one obvious fix |
| Success Criteria | When outcomes are measurable | Exploratory research |
| Impact Assessment | When change affects other systems | Isolated changes with no blast radius |
| Operational Requirements | Non-trivial systems | Simple scripts or one-off changes |
| Interface Investigation | When APIs/UIs are involved | Internal-only refactors |

You use these dimensions internally to decide what to ask about. The user never sees "Dimensions Explored" or "Dimensions Skipped" as output sections.

## Step 5: Propose 2-3 Approaches (Significant Decisions Only)

- For **significant decisions** where multiple approaches exist with meaningful trade-offs, propose 2-3 approaches
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why
- For **simple fixes** with one obvious approach, skip alternatives and go straight to design
- YAGNI — remove unnecessary features from all designs

## Step 6: Present Design Incrementally

- Present design section by section, asking after each whether it looks right
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense
- Design for isolation and clarity: each unit should have one clear purpose, well-defined interfaces, independently understandable

**Working in existing codebases:**

- Explore current structure before proposing changes
- Follow existing patterns
- Include targeted improvements only where they serve the current goal
- Don't propose unrelated refactoring

## Step 7: Transition to spec-creation

**The terminal state is invoking spec-creation.** Do NOT write the spec in brainstorming — that is the responsibility of the `spec-creation` skill.

> "Exploration complete. I'll now invoke the spec-creation skill to structure and write the spec from our investigation results."

The `spec-creation` skill handles:

- Requirements extraction, problem decomposition, interface-first thinking
- Traceability mapping, risk & operational analysis
- Spec writing, self-review, and user review
- Change control for revisions

This separation ensures exploration (brainstorming) and structuring (spec-creation) are distinct concerns with distinct discipline.

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-12T12:00:00Z"
rules: []
state_machines:
  - id: brainstorming-flow
    states:
      - "Explore project context"
      - "Scope check"
      - "Decompose project"
      - "Visual questions ahead?"
      - "Offer Visual Companion"
      - "Ask clarifying questions"
      - "Propose 2-3 approaches"
      - "Present design incrementally"
      - "User approves?"
      - "Invoke spec-creation"
    start_state: "Explore project context"
    transitions:
      - from: "Explore project context"
        to: "Scope check"
        guard: "context_gathered == true"
        action: PROCEED
      - from: "Scope check"
        to: "Decompose project"
        guard: "scope_type == 'multi-subsystem'"
        action: PROCEED
      - from: "Scope check"
        to: "Visual questions ahead?"
        guard: "scope_type == 'single'"
        action: PROCEED
      - from: "Decompose project"
        to: "Visual questions ahead?"
        guard: "decomposition_complete == true"
        action: PROCEED
      - from: "Visual questions ahead?"
        to: "Offer Visual Companion"
        guard: "visual_questions == true"
        action: PROCEED
      - from: "Visual questions ahead?"
        to: "Ask clarifying questions"
        guard: "visual_questions == false"
        action: PROCEED
      - from: "Offer Visual Companion"
        to: "Ask clarifying questions"
        guard: "companion_offered == true"
        action: PROCEED
      - from: "Ask clarifying questions"
        to: "Propose 2-3 approaches"
        guard: "clarification_complete == true"
        action: PROCEED
      - from: "Propose 2-3 approaches"
        to: "Present design incrementally"
        guard: "approach_selected == true"
        action: PROCEED
      - from: "Present design incrementally"
        to: "User approves?"
        guard: "design_presented == true"
        action: PROCEED
      - from: "User approves?"
        to: "Present design incrementally"
        guard: "user_approved == false"
        action: WARN
      - from: "User approves?"
        to: "Invoke spec-creation"
        guard: "user_approved == true"
        action: INVOKE(spec-creation)
```
