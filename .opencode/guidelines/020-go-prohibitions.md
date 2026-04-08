# GO Prohibitions

## 1. What GO Is Not & Self-Authorization Prohibitions

### 🚫 NEVER DO
- **ABSOLUTE PROHIBITION: The agent must never write the word "GO" as a standalone token, line, or heading in any response.** This includes standalone lines (`GO`), Markdown headings (`## GO`), phase labels (`GO - Phase 2`), acknowledgements, transition markers, or narrative labels. Any use of "GO" in agent output (including `<UPDATE>` blocks, tool parameters, or chat text) is a protocol violation and does NOT constitute authorization. The only permitted use is inside a quoted/code-fenced example illustrating a prohibited pattern. To acknowledge authorization, use a full sentence (e.g., "Authorization received.") — never a bare "GO".
- **No `echo` or `printf` commands — ever.** The agent is absolutely prohibited from running `echo`, `printf`, or any equivalent shell output command for any purpose. This includes:
  - **Output for Narration**: Signalling waiting states, confirming completion, or self-narration.
  - **File Operations**: Bypassing `ai_bin` tools via `printf "..." > file.md` or `echo "..." >> file.md`.
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
- **Questions are NOT authorization.** "Should I do X?" and "Would you like me to X?" are questions seeking permission, not receiving it. Never act on a question — wait for explicit authorization.
- **SILENTLY HALT after every task/report.** Factual reporting is permitted, but it must NEVER be followed by a prompt for next steps.
- **Never name the next phase or action in a halt message.** Halt messages must be factual statements about what was completed — never forward-looking references to what comes next.
- **Never self-answer a solicitation.** Pose no questions that you then answer yourself to bypass authorization.

### ⚠️ ASK FIRST
- **"GO" requires unambiguous scope; clarify only when ambiguous.** If the user types "GO" (or equivalent), treat it as valid authorization ONLY when the immediate session context identifies exactly one plan/scope target.
- **Clarification gate for ambiguous "GO" only.** Ask for scope clarification only when more than one plausible plan file, phase, or implementation scope is active.

### ✅ ALWAYS DO
- **Verify actual codebase state before acting.** When a GO names a specific phase, verify the actual codebase state of that phase's deliverables before taking any action — regardless of plan markers.
- **SILENTLY HALT after a verified-complete phase.** If verification confirms a named phase is already fully and correctly implemented, report the verified findings and HALT without prompting.

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

---

## 5. Multi-task Spec Without Sub-issues — CRITICAL VIOLATION

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 ABSOLUTE PROHIBITION
- **NEVER implement a multi-task spec without verified sub-issue structure**
- **NEVER proceed when `get_sub_issues` returns empty array for multi-task specs**
- **NEVER assume markdown checkboxes = task tracking**

### ✅ MANDATORY WORKFLOW

**Before implementing ANY multi-task spec:**

```
1. Call github_issue_read(method="get_sub_issues", issue_number=N)
2. If empty AND multi-task:
   a. AUTO-CREATE sub-issues at PHASE level
   b. Link each via github_sub_issue_write(method="add")
   c. Post comment: "Created X sub-issues for phase tracking"
   d. THEN proceed to implementation
3. If sub-issues exist:
   - Verify phase being implemented is among them
   - Proceed with implementation
```

### 📋 CHECKLIST

| Action | Required? |
|--------|-----------|
| `get_sub_issues` check | ✅ ALWAYS |
| AUTO-CREATE if empty | ✅ YES (multi-task only) |
| Verify task linked | ✅ ALWAYS |
| Single-task exemption | ✅ YES (no sub-issues needed) |

### ⚠️ SINGLE-TASK EXCEPTION

Single-task specs (one implementation task, no decomposition needed) do NOT require sub-issues. All multi-task specs MUST have sub-issues before implementation begins.
