# Task: create

## Purpose

Create an implementation plan from an approved spec.

## Prerequisites

1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

## Creation Steps

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

      These annotations enable `assemble-batch` to compose accurate `concern_boundaries_crossed` in the dispatch context, so sub-agents understand the architectural transitions they are participating in. Concern boundary annotations should be woven into the phase description naturally, not as separate structured fields.

      After plan issue is created, create sub-issues under the plan (not the spec) for each phase via `github-sub-issues --task create-sub-issue`.

7. **Self-review:**

   - Spec coverage check
   - Placeholder scan
   - Type consistency check
   - Fix any issues found

8. **Validate plan:**

   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable

9. **Report plan creation in chat (MANDATORY):**

    Produce chat output in the mandatory format per `000-critical-rules.md`:

     1. **Executive summary**: 1-2 sentences describing what plan was created and for which spec
     2. **URL**: The plan issue URL (e.g., `https://github.com/<GIT_OWNER>/<GIT_REPO>/issues/<N>`)
     3. **AI byline**: `🤖 <AgentName> (<ModelID>)` — ALWAYS LAST

     Example:

     Created implementation plan for #771 (branch stacking prerequisite). 7 tasks across 6 files (3 skills + 3 guidelines).
     https://github.com/<GIT_OWNER>/<GIT_REPO>/issues/772
     🤖 <AgentName> (<ModelID>)

     Sub-issues are linked under the plan issue, NOT under the spec.

10. **Cross-reference verification (MANDATORY before plan creation):**

    Before creating the plan issue, verify that all referenced skills exist and their described behaviors match actual skill content:

    ```bash
    # Verify approval-gate dispatch chain
    ls .opencode/skills/approval-gate/SKILL.md && grep -c "verify-authorization" .opencode/skills/approval-gate/SKILL.md
    # Verify github-sub-issues task
    ls .opencode/skills/github-sub-issues/SKILL.md && grep -c "create-sub-issue" .opencode/skills/github-sub-issues/SKILL.md
    # Verify spec-creation exists
    ls .opencode/skills/spec-creation/SKILL.md
    # Verify brainstorming exists
    ls .opencode/skills/brainstorming/SKILL.md
    # Verify spec-auditor clean-room invocation
    ls .opencode/skills/spec-auditor/SKILL.md && grep -c "clean-room\|fidelity" .opencode/skills/spec-auditor/SKILL.md
    ```

    If any verification fails: flag as MISSING-TRACEABILITY or CONFLICTING and note in plan creation output.

11. **Post-creation approval cascade check (MANDATORY):**

    After the plan issue is created, check whether the spec that triggered plan creation was already approved. If yes, the new plan inherits the spec's approval status.

    ```python
    # Check if the spec was already approved
    spec_issue = github_issue_read(method="get", issue_number=spec_number)
    spec_comments = github_issue_read(method="get_comments", issue_number=spec_number)

    # Look for explicit approval in spec comments
    has_approval = any(
        "approved" in comment["body"].lower() or comment["body"].strip().lower() == "go"
        for comment in spec_comments
        if comment["author_association"] in ("MEMBER", "OWNER", "COLLABORATOR")
    )

    # Check if needs-approval label is absent from spec (indicates prior approval)
    spec_labels = [l["name"] for l in spec_issue["labels"]]
    label_already_removed = "needs-approval" not in spec_labels

    if has_approval or label_already_removed:
        # Spec was already approved — cascade approval to the new plan
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
