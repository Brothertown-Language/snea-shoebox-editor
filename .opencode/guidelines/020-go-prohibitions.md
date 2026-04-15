# GO Prohibitions

## 1. What GO Is Not & Self-Authorization Prohibitions

### 🚫 NEVER DO

- **ABSOLUTE PROHIBITION: The agent must never write the word "GO" as a standalone token, line, or heading in any response.** This includes standalone lines (`GO`), Markdown headings (`## GO`), phase labels (`GO - Phase 2`), acknowledgements, transition markers, or narrative labels. Any use of "GO" in agent output (including `<UPDATE>` blocks, tool parameters, or chat text) is a protocol violation and does NOT constitute authorization. The only permitted use is inside a quoted/code-fenced example illustrating a prohibited pattern. To acknowledge authorization, use a full sentence (e.g., "Authorization received.") — never a bare "GO".
- **No `echo` or `printf` commands — ever.** The agent is absolutely prohibited from running `echo`, `printf`, or any equivalent shell output command for any purpose. This includes:
  - **Output for Narration**: Signalling waiting states, confirming completion, or self-narration.
  - **File Operations**: Bypassing `.opencode/tools` tools via `printf "..." > file.md` or `echo "..." >> file.md`.
  - **Script Injection**: Writing logic into temp scripts via shell redirection.
- **No "awaiting GO" or pending-state markers — anywhere, ever.** The agent is absolutely prohibited from using the phrase "awaiting GO", "waiting for GO", "pending GO", "awaiting explicit phase approval", "awaiting approval", "pending approval", or any equivalent pending-state marker.
- **NEVER prompt or solicitation for authorization.** The agent is absolutely prohibited from asking, prompting, nudging, or inviting the user to issue "GO", "approved", or any other approval token in any form.
- **NEVER prompt the user with THINKING and expect an answer of any kind.** Internal reasoning must never be surfaced as a user-facing prompt.
- **No leading or pushy authorization questions.** The agent must not ask "May I proceed?", "Shall I continue?", "Ready for me to start?", or any similar request for permission to begin implementation.
- **OFFENSIVE TEXT EXAMPLES — NEVER USE:**
  - "Ready for authorization to implement?"
  - "Ready to proceed with implementation?"
  - "Shall I begin implementation?"
  - "Waiting for approval to continue."
  - "Let me know when you're ready for me to start."
  - "Say 'approved' or 'go' when ready."
  - "Awaiting authorization to implement."
  - "**Awaiting authorization to begin Phase X.** Say 'approved' or 'go' when ready."
  - "Awaiting your approval."
  - "Ready when you are."
- **Discussion conclusions are NOT authorization.** Verbal agreement, consensus, or opinion expressed in discussion does NOT constitute explicit authorization:
  - "Sounds like we need to X" → discussion consensus, NOT "do X"
  - "I think the answer is Y" → opinion, NOT "implement Y"
  - "So we're going with approach Z" → conclusion, NOT "start Z"
  - "That makes sense, let's do it" → verbal agreement, NOT explicit authorization
  - "This looks like it should be X" → observation, NOT "make it X"
- **Questions are NOT authorization.** "Should I do X?" and "Would you like me to X?" are questions seeking permission, not receiving it. Never act on a question — wait for explicit authorization.
- **SILENTLY HALT after every task/report.** Factual reporting is permitted, but it must NEVER be followed by a prompt for next steps.
- **Never name the next phase or action in a halt message.** Halt messages must be factual statements about what was completed — never forward-looking references to what comes next.
- **No "offer to edit" patterns.** The agent MUST NOT offer to edit, update, modify, or fix a file directly. Instead, create a spec or bug report. Patterns like "Want me to update X?", "Shall I fix this?", "I can change X to Y" are PROHIBITED — they bypass the spec-first workflow.
- **Never self-answer a solicitation.** Pose no questions that you then answer yourself to bypass authorization.
- **NEVER suggest parallel execution as a valid default approach.** Stacking is prerequisite; parallel is opportunistic. Agents must not present parallelism as an equally valid option.
- **No silent halt without search+prompt.** When no spec/plan exists for an implementation request, the agent MUST NOT simply halt. It must search GitHub Issues for existing candidates, present them with URLs, and offer create-or-select before halting. A silent halt with no search and no candidate presentation is a critical violation — see `000-critical-rules.md` §Silent Halt Without Prompt.

### ⚠️ ASK FIRST

- **"GO" requires unambiguous scope; clarify only when ambiguous.** If the user types "GO" (or equivalent), treat it as valid authorization ONLY when the immediate session context identifies exactly one plan/scope target.
- **Clarification gate for ambiguous "GO" only.** Ask for scope clarification only when more than one plausible plan file, phase, or implementation scope is active.

### ✅ ALWAYS DO

- **Verify actual codebase state before acting.** When a GO names a specific phase, verify the actual codebase state of that phase's deliverables before taking any action — regardless of plan markers.
- **SILENTLY HALT after a verified-complete phase.** If verification confirms a named phase is already fully and correctly implemented, report the verified findings and HALT without prompting.
- **Every halt MUST produce a status message.** If the agent stops, it MUST output what was completed, what was attempted, and why it stopped. Zero output before stopping is a critical violation.
- **Search issues before halting on missing spec/plan.** When an implementation request lacks a matching spec or plan:
  1. Search GitHub Issues using label filters: `[SPEC]`, `[PLAN]`, `[SPEC-FIX]`
  2. Search GitHub Issues using keyword matching against the request target
  3. If candidates found: present all candidates with URLs, offer user a choice to select one or create a new spec
  4. If no candidates found: present the failure state ("No existing spec/plan found for [topic]"), offer to create a new spec
  5. Only after search+presentation: HALT, but the halt message now includes the search results

## 2. Iterative Feedback & Plan Revision

- **Discussion and analysis sessions do not grant GO.** Each session starts with zero authorization for code changes.
- **GO must be explicit and literal.** Only the exact word "GO" (or unambiguous equivalent) constitutes authorization.
- **"Revise" and "update" are plan-only directives.** Requests containing "revise" (or synonyms) refer exclusively to updating the GitHub Issue spec. They never authorize code changes. "Revise plan" means update an existing issue — never make code changes for a "revise plan" or similar.
- **Plan revision invalidates all prior approvals.** Any change to an issue invalidates all previous GOs for that plan. A new explicit GO is required.
- **Plan creation after GO invalidates authorization.** If a plan is created after receiving a GO, the prior GO is invalidated. Wait for a new GO for the documented plan.

## 3. Specialized Execution Gates

## 4. Node.js Prohibition in Python/Java Projects

**DETESTABLE**: Installing Node.js in a Python-only or Java-only environment is absolutely prohibited. This introduces an unnecessary runtime dependency that pollutes the ecosystem and creates maintenance burden.

### 🚫 NEVER DO

- **NEVER install Node.js globally or locally** on Python-only or Java-only projects.
- **NEVER use NPX** to run packages — NPX requires Node.js runtime.
- **NEVER add Node.js-based tools to project dependencies.**
- **NEVER suggest npm packages as solutions** in Python/Java contexts.
- **NEVER use Node.js-based formatters, linters, or tooling** when native alternatives exist.

### Context

This rule applies universally to:

- **Python projects**: Use `uv`, `pip`, `ruff`, `pytest` — never npm/pnpm/yarn.
- **Java projects**: Use Maven/Gradle, JVM tooling — never npm/pnpm/yarn.
- **Projects with mixed languages**: Isolate Node.js to its designated frontend/service layer.

### ✅ ALLOWED

- **Docker containers that internally use Node.js** — Node.js runs inside container, not on host.
- **Pure Python alternatives** — `githubkit` instead of `@octokit/rest`, `httpx` instead of `axios`.
- **Dedicated frontend repositories** where Node.js IS the correct tool for that codebase.
- **MCP servers via Docker** — Node.js isolated in container only.

### Why This Is Critical

- **Security**: Node.js ecosystem has known supply-chain attack vectors.
- **Dependency bloat**: Adds unnecessary runtime and package manager complexity.
- **Maintenance burden**: Mixed language projects require additional CI/CD configuration.
- **Ecosystem mismatch**: npm packages don't integrate with Python/Java tooling chains.
- **Team friction**: Requires developers to install/maintain Node.js on their machines.

______________________________________________________________________

## 5. Multi-task Plan Without Sub-issues — CRITICAL VIOLATION

**⚠️ Implementing a multi-task plan without sub-issues is a CRITICAL GUIDELINE VIOLATION.** Sub-issues are children of the plan, not the spec.

### 🚫 ABSOLUTE PROHIBITION

- **NEVER implement a multi-task plan without verified sub-issue structure**
- **NEVER proceed **to implementation** when `get_sub_issues` on the plan returns empty array for multi-task plans **without auto-creating sub-issues first****
- **NEVER assume markdown checkboxes = task tracking**
- **NEVER create sub-issues under the spec** — sub-issues belong to the plan

### ✅ MANDATORY

**See `github-sub-issues` skill for the complete auto-create workflow, single-task exemption, database ID requirement, and phase-level structure. Sub-issue verification is consolidated into `approval-gate --task verify-authorization` Step 5 as the single readiness check.**

Key points:

- Sub-issues at PHASE level under the plan, not step level
- Single-task plans are exempt from sub-issue requirement
- All multi-task plans MUST have sub-issues before implementation begins
- Auto-creating sub-issues for an approved multi-task plan is a pre-implementation setup step covered by the plan's authorization. No separate authorization is required.
- After auto-creating sub-issues, the agent proceeds with implementation immediately (no re-authorization needed).

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-13T12:00:00Z"
rules:
  - id: go-prohibitions-001
    title: "Agent must never write GO as standalone token"
    conditions:
      all:
        - "agent_output_contains == 'GO'"
        - "context != 'quoted_example'"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "020-go-prohibitions.md §1 NEVER DO"

  - id: go-prohibitions-002
    title: "No echo or printf commands ever"
    conditions:
      all:
        - "command_includes == 'echo'"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "020-go-prohibitions.md §1 NEVER DO"

  - id: go-prohibitions-003
    title: "No awaiting-GO or pending-state markers"
    conditions:
      all:
        - "agent_output_contains == 'awaiting'"
        - "agent_output_contains == 'approval'"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "020-go-prohibitions.md §1 NEVER DO"

  - id: go-prohibitions-004
    title: "Never prompt for authorization"
    conditions:
      any:
        - "agent_output_matches == 'May I proceed?'"
        - "agent_output_matches == 'Shall I continue?'"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "020-go-prohibitions.md §1 NEVER DO"

  - id: go-prohibitions-005
    title: "Questions are NOT authorization"
    conditions:
      all:
        - "user_input_format == 'question'"
    actions:
      - SKIP
    conflicts_with: [approval-gate-002]
    requires: []
    triggers: []
    source: "020-go-prohibitions.md §1 NEVER DO"

  - id: go-prohibitions-006
    title: "Multi-task plan requires sub-issues under plan"
    conditions:
      all:
        - "plan_has_phases == true"
        - "plan_sub_issues_count == 0"
    actions:
      - HALT
    conflicts_with: []
    requires: [approval-gate-001]
    triggers: [github-sub-issues]
    source: "020-go-prohibitions.md §5"

  - id: go-prohibitions-007
    title: "No silent halt without search+prompt for missing spec/plan"
    conditions:
      all:
        - "implementation_requested == true"
        - "matching_spec_exists == false"
        - "matching_plan_exists == false"
        - "search_performed == false"
    actions:
      - SEARCH(github_issues)
      - PRESENT(candidates)
      - HALT
    conflicts_with: []
    requires: [approval-gate-010]
    triggers: [approval-gate, brainstorming]
    source: "020-go-prohibitions.md §1 NEVER DO, ALWAYS DO"
```
