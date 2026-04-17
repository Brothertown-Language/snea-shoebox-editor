# Task: create

## Purpose

Create an implementation plan from an approved spec. For single-task specs the agent may combine the plan into the spec issue body instead of creating a separate [PLAN] issue.

## Prerequisites

1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

## Creation Steps

### Pre-Step: Verification Gate (MANDATORY FIRST)

Before reading the approved spec, invoke `verification-enforcement --task verify`. This gate dispatches section-based sub-agents to collect evidence artifacts for the factual claims the plan will make — file references, skill invocations, architectural decisions, and dependency assertions. Evidence artifacts collected here ensure that the plan's claims about the codebase and skill ecosystem are grounded in live sources. Claims that cannot be verified at this stage are marked with `⚠️ UNVERIFIED` for resolution in the post-generation revisit pass.

1. **Read approved spec:**

   - Query GitHub Issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

1.5. **Combined vs Separate Plan Decision Gate:**

   Before mapping file structure, evaluate whether to combine the plan into the spec issue body or create a separate [PLAN] issue. This decision must be made early because it affects how the plan content is structured and where it is stored.

   **Input:** The `single_task_determination` passed from `issue-operations/tasks/post-creation` (values: `single-task` or `multi-task`). If not provided, evaluate using the same criteria as `single-task-check` (one phase, single concern, no decomposition needed).

   **Decision logic — agent intelligence, no hardcoded thresholds:**

   | Condition | Outcome |
   |-----------|---------|
   | Multi-task spec (multiple phases, mixed concerns, deployment independence) | **Always separate** — create [PLAN] issue with sub-issues (current behavior) |
   | Single-task spec AND spec body can absorb plan content without becoming unwieldy | **Candidate for combined** — agent evaluates readability and coherence |
   | Single-task spec AND combining would make document hard to read or mix concerns | **Separate** — create [PLAN] issue (current behavior) |

   **Agent evaluation for combined candidates — consider:**

   - How many TDD steps the plan would add
   - Whether the spec body is already long or dense
   - Whether the plan content flows naturally after the spec content
   - Whether keeping everything in one document aids or hinders review

   **Decision output (MANDATORY):** The agent MUST document its decision in chat before proceeding:

   ```
   Plan structure decision: combined/separate
   Reason: <brief justification referencing the evaluation criteria>
   ```

   **If COMBINED:**

   - Append `## Implementation Plan` section to the spec issue body
   - The section contains the plan header, file structure, and TDD tasks
   - The issue retains its `[SPEC]` title prefix (not changed to `[PLAN]`)
   - No sub-issues needed (single-task by definition)
   - Remove `needs-approval` label if the spec was already approved (plan inherits approval via spec-to-plan cascade)
   - Proceed to Step 2 (Map file structure) — plan content will be appended to spec body after all steps complete

   **If SEPARATE:**

   - Proceed to Step 2 (Map file structure) — plan content will be stored in a separate [PLAN] issue created at Step 6a

### Step 1.6: Duplicate Plan Check

Before mapping file structure, check whether existing plans already reference the same spec. This prevents accidental plan duplication and ensures the developer is aware of overlapping implementation tracking.

**Procedure:**

1. Using `github_search_issues`, search for issues labeled `plan` in the repository:
   ```
   github_search_issues(query="label:plan", owner=<github.owner>, repo=<github.repo>, state="open")
   ```
2. Filter results for those whose body contains `Spec: #<spec_number>` referencing the current spec number.
3. If one or more existing plans are found:
   - Collect each existing plan's issue number, title, and URL
   - Read each existing plan's body to extract its phase scope (phase names, file structure, and concern boundaries)
   - Present the overlap to the developer in chat: list each existing plan with its URL and a scope summary
   - Offer the developer a choice:
     - **"proceed with new plan (will add reference to existing plan)"** — record the existing plan reference and add an explicit `Supersedes/replaces #N` or `Parallel track to #N` statement in the new plan body
     - **"halt and review existing plan first"** — HALT and present the existing plan for review
4. If the developer chooses to proceed, include the relationship statement in the new plan body at the top, immediately after the spec reference:
   - If the new plan replaces an existing plan: `Supersedes/replaces #N` where N is the existing plan issue number
   - If the new plan covers a parallel concern: `Parallel track to #N` where N is the existing plan issue number
5. If no existing plans are found for the same spec, proceed without modification.

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

6. **Store plan document (depends on Step 1.5 decision):**

   **If COMBINED (decision from Step 1.5):**

   - Append `## Implementation Plan` section to the spec issue body
   - Proceed to Step 7 (Self-review)

   **If SEPARATE (decision from Step 1.5):**

   - Continue to Step 6a (Create separate plan issue)

6a. **Create separate plan issue (only if SEPARATE):**

   - Title: `[PLAN] <Feature Name>`
      - Labels: `plan` + `needs-approval`
      - Body: Spec reference as prose (e.g., `Spec: #784`), then plan with header, file structure, phases with TDD tasks
      - Initial STATUS: Use prose-driven format. Set `STATUS: in progress — {first concern}, Step 1` (or backward-compatible `STATUS: 1.1` if the spec uses numeric STATUS convention). The STATUS concern name should match the first phase's concern name.
      - Do NOT link plan as sub-issue of spec — the plan references the spec via body text only

   **Phase body requirements (critical):** Each phase in the plan body MUST include the information a sub-agent needs to implement the phase independently, without re-reading the plan. This means each phase section must contain:

      - Why this phase exists — the concern it addresses and its place in the overall design
      - What it must accomplish — tasks, deliverables, and behavioral requirements
      - How to verify completion — success criteria and testable outcomes
      - What could go wrong — edge cases, known risks, and failure modes
      - What must be done first — dependencies on prior phases or external prerequisites

      This is a prose-driven requirement: state what information must be present, not what section headers to use. The agent writing the plan decides how to organize this content naturally within the phase description.

      **Concern boundary annotations (prose-driven):** When a phase transitions from one architectural concern to another — for example, from data modelling to enforcement logic, from orchestration to error handling, from schema definition to runtime behavior — the plan MUST annotate this transition. The annotation is prose, not a rigid marker. It should describe:

      - What concern the phase is leaving (the prior concern's scope)
      - What concern the phase is entering (the new concern's scope)
      - What information the new concern needs from the prior concern (the handoff point)

      These annotations enable `assemble-work` to compose accurate `concern_boundaries_crossed` in the dispatch context, so sub-agents understand the architectural transitions they are participating in. Concern boundary annotations should be woven into the phase description naturally, not as separate structured fields.

      After plan issue is created, create sub-issues under the plan (not the spec) for each phase via `issue-operations --task link-sub-issue`.

7. **Self-review:**

   - Spec coverage check
   - Placeholder scan
   - Type consistency check
   - Fix any issues found

8. **Validate plan:**

   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable

   **Prose-structure check:** Phase descriptions and plan headers should remain prose. TDD steps within tasks are naturally structured and exempt — their numbered format serves direct implementation guidance, not narrative communication. If a phase description reads as a rigid checklist rather than an explanation of the concern it addresses, rewrite it as flowing prose.

9. **Post-Validation: Verification Revisit (MANDATORY):**

   Invoke `verification-enforcement --task revisit`. This pass scans the plan for any remaining `⚠️ UNVERIFIED` markers and attempts to resolve them using domain-appropriate tools. Claims that cannot be resolved are escalated to the developer. The plan must not be stored or reported as complete while unverified claims remain without developer acknowledgment.

10. **Report plan creation in chat (MANDATORY):**

     Produce chat output in the mandatory format per `000-critical-rules.md`:

      1. **Executive summary**: 1-2 sentences describing what plan was created and for which spec. Include combined/separate designation.
      2. **URL**: The plan issue URL (separate plan) or the spec issue URL (combined plan)
      3. **AI byline**: `🤖 <AgentName> (<ModelId>)` — ALWAYS LAST

      Example (separate plan):

      Created separate implementation plan for #771 (branch stacking prerequisite). 7 tasks across 6 files (3 skills + 3 guidelines).
      https://github.com/<github.owner>/<github.repo>/issues/772
      🤖 <AgentName> (<ModelId>)

      Example (combined spec+plan):

      Created combined spec+plan for #771 (simple configuration change). Plan appended under `## Implementation Plan`.
      https://github.com/<github.owner>/<github.repo>/issues/771
      🤖 <AgentName> (<ModelId>)

      Sub-issues are linked under the plan issue for separate plans, NOT under the spec. Combined plans have no sub-issues.

10. **Cross-reference verification (MANDATORY before plan creation):**

    Before creating the plan issue, verify that all referenced skills exist and their described behaviors match actual skill content:

    ```bash
    # Verify approval-gate dispatch chain
    ls .opencode/skills/approval-gate/SKILL.md && grep -c "verify-authorization" .opencode/skills/approval-gate/SKILL.md
    # Verify issue-operations task
    ls .opencode/skills/issue-operations/SKILL.md && grep -c "link-sub-issue" .opencode/skills/issue-operations/SKILL.md
    # Verify spec-creation exists
    ls .opencode/skills/spec-creation/SKILL.md
    # Verify brainstorming exists
    ls .opencode/skills/brainstorming/SKILL.md
    # Verify spec-auditor clean-room invocation
    ls .opencode/skills/spec-auditor/SKILL.md && grep -c "clean-room\|fidelity" .opencode/skills/spec-auditor/SKILL.md
    ```

    If any verification fails: flag as MISSING-TRACEABILITY or CONFLICTING and note in plan creation output.

11. **Post-creation approval cascade check (MANDATORY):**

     After the plan is created (either combined or separate), check whether the spec that triggered plan creation was already approved. If yes, the plan inherits the spec's approval status.

     **For combined spec+plan:** The spec issue already has the plan content appended. If the spec was already approved, no further approval action is needed — the combined document inherits the spec's approval. Do NOT remove `needs-approval` if it is still present on the spec (the spec itself may still be pending approval). If the spec was already approved AND `needs-approval` is absent, the combined plan is auto-approved.

     **For separate plan:** Apply the existing cascade logic:

     ```python
     spec_issue = github_issue_read(method="get", issue_number=spec_number)
     spec_comments = github_issue_read(method="get_comments", issue_number=spec_number)

     has_approval = any(
         "approved" in comment["body"].lower() or comment["body"].strip().lower() == "go"
         for comment in spec_comments
         if comment["author_association"] in ("MEMBER", "OWNER", "COLLABORATOR")
     )

     spec_labels = [l["name"] for l in spec_issue["labels"]]
     label_already_removed = "needs-approval" not in spec_labels

     if has_approval or label_already_removed:
         github_issue_write(
             method="update",
             issue_number=plan_issue_number,
             labels=[l for l in plan_labels if l != "needs-approval"],
         )
         github_add_issue_comment(
             issue_number=plan_issue_number,
             body=f"Approval cascaded from spec #{spec_number}. Plan created for an already-approved spec — plan inherits approval status automatically.",
         )
     ```

      This handles the case where plan creation happens AFTER spec approval in the same session. If the spec still has `needs-approval`, the new plan retains its `needs-approval` label and follows the standard flow (requires explicit plan approval).

## Live Verification: Plan Creation Evidence (MANDATORY)

**Each factual claim in the plan MUST be verified via tool call before storing. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Spec #N is approved" | Verify spec has approval comment or no `needs-approval` label | `github_issue_read(method="get_comments", issue_number=N)` + `github_issue_read(method="get", issue_number=N)` | VERIFICATION-GAP |
| "File X exists in codebase" | Verify file path | `glob(pattern="**/X")` | MISSING-ELEMENT |
| "Function Y has signature Z" | Verify signature against live code | `srclight_get_signature(name="Y")` | VERIFICATION-GAP |
| "Spec requires multi-task plan" | Verify spec has multiple phases | `github_issue_read(method="get", issue_number=N)` → parse body for phase sections | CONFLICTING |
| "Skill X supports operation Y" | Verify skill declares the operation | `grep(pattern="Y", path=".opencode/skills/X/SKILL.md")` | CONFLICTING |
| "Sub-issue linked to plan" | Verify sub-issue parent is plan (not spec) | `github_issue_read(method="get_sub_issues", issue_number=plan_number)` | STRUCTURE-VIOLATION |
| "Plan issue has `plan` label" | Verify label present | `github_issue_read(method="get", issue_number=plan_number)` → check labels | MISSING-ELEMENT |

**Evidence artifact:** Tool call results for each verification claim, stored in plan creation context.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Spec not actually approved | VERIFICATION-GAP | flag-for-review | HALT — do not create plan without approved spec |
| Referenced file not found | MISSING-ELEMENT | conditional | Remove from plan or mark `⚠️ UNVERIFIED` |
| Function signature mismatch | VERIFICATION-GAP | conditional | Correct claim or mark `⚠️ UNVERIFIED` |
| Skill doesn't support operation | CONFLICTING | flag-for-review | Remove reference, find alternative |
| Sub-issues under spec instead of plan | STRUCTURE-VIOLATION | auto-fix | Re-link under plan |
| Plan missing `plan` label | MISSING-ELEMENT | auto-fix | Add label immediately |
