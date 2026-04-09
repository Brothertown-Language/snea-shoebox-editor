# Planning: Spec Creation

## Spec-Driven Development Workflow

AI agents MUST follow the **Spec-Driven Development** (Gated Workflow) approach:

1. **Specify Phase**: Define **What & Why**. Kick off with a high-level vision (product brief), then expand it into a detailed specification focusing on user journeys, experiences, and success criteria.
2. **Plan Phase**: Define **How**. Draft the technical plan (architecture, technical stack, and constraints).
3. **Tasks Phase**: Break the plan into **small, reviewable chunks** (tasks) that can be implemented and tested in isolation.
4. **Implement Phase**: **Execute** tasks and **verify** results.

**CRITICAL**: Investigation and Planning phases are AUTO-COMPLETED before the spec is created. The spec file ONLY contains implementation and verification phases.

**INVESTIGATION CHECKPOINT**: Before creating a spec, the agent MUST verify investigation is complete. See `142-planning-archive-workflow.md` for investigation completion criteria and permissible test activities.

---

## Terminology: Spec vs. Guideline Files

- **"Create a new spec"** = Create a GitHub Issue with `[SPEC]` prefix (Mandatory when GitHub MCP available)
- **"Create a guideline file"** = Create/modify files in `.opencode/guidelines/` (Implementation task)
- **SPEC = GitHub Issue** — Specs are planning/tracking artifacts, not file system artifacts

---

## 1. Listing Available Specs

When the user issues commands `specs` or `pending`:

1. **Gather all top-level specs**:
   - Query open GitHub Issues with `[SPEC]` prefix in title
 2. **Check for superseding issues AND staleness**:
    - Before implementing OR revising a spec, query for later `[SPEC]` or `[SPEC-FIX]` or `[SPEC-ENHANCEMENT]` issues
    - If a later issue supersedes, invalidates, or contradicts the active spec, HALT and report
    - Implementation of a superseded spec is wasted work
    - Check if other specs were implemented while this spec was pending (staleness)
    - If stale, REVISE the spec to reflect current reality before proceeding
    - Report the revision and HALT — wait for approval before proceeding
3. **Present a multi-choice user query**:
   - Use the `question` tool with a list of available specs
   - Include spec title/name and current STATUS for each option
   - Add a "Type your own answer" option for creating a new spec
4. **Response format**:
   ```
   Available Specs:
   - [SPEC] Feature A (STATUS: 1.2)
   - [SPEC] Feature B (STATUS: 2.1)
   - [SPEC] Bug Fix C (STATUS: 1.1)
   ```
5. **After user selection**:
   - Load the selected spec content
   - Show the spec details and current status
   - Report that the spec is ready and HALT. Do NOT prompt for approval or "GO".

---

## 1.1. GitHub MCP Required — No Fallback

**When GitHub MCP tools are NOT available, the agent MUST refuse planning work entirely.**

### 🚫 NO FALLBACK TO LOCAL FILES
- **PROHIBITED**: Using `plans/SPEC-*.md` files as fallback when GitHub MCP is unavailable
- **PROHIBITED**: Creating local plan files when GitHub MCP is unavailable
- **PROHIBITED**: Proceeding with implementation without GitHub Issue tracking

### ✅ REQUIRED ACTION
- If GitHub MCP is unavailable, STOP immediately
- Report: "GitHub MCP tools unavailable. Cannot create or track specs without GitHub Issues."
- Wait for GitHub MCP to be restored before proceeding

---

## 1. Spec Reality Sync

**Specs must reflect current code/implementation state.** If drift is detected between a spec and the actual code:

1. **Code is authoritative** — the spec is secondary
2. **Update the spec to match reality** — this is administrative sync, not implementation
3. **Report the synchronization and HALT**
4. **This exemption applies ONLY to spec files in GitHub Issues**
5. **`.opencode/guidelines/` modifications require full spec-first workflow**

---

## 1.1. Engineering Requirements for Specs

**Every specification MUST include thorough requirements analysis.**

### Full Requirements Analysis Required

Before any implementation, every spec must document:

| Requirement | Description |
|-------------|-------------|
| **Problem Statement** | What is the problem? Why does it need solving? |
| **Context** | Background, stakeholders, affected systems |
| **Constraints** | Technical, resource, time, compatibility constraints |
| **Assumptions** | What are we assuming that may not be true? |
| **Success Criteria** | Testable, measurable criteria for completion |
| **Edge Cases** | Boundary conditions and corner cases identified |
| **Dependencies** | External systems, libraries, other teams affected |
| **Integrations** | How does this integrate with existing code? |
| **Risk Assessment** | What could go wrong? Mitigation strategies? |

### Design Phase Required

**No direct-to-implementation.** Before coding:

1. **Explore codebase** for existing patterns and reusable components
2. **Document design decisions** in the spec
3. **Consider alternatives** and their tradeoffs
4. **Get approval on approach** before starting implementation

### Anti-Patterns in Specifications

**🚫 FORBIDDEN in Specs:**
- Vague requirements ("make it better")
- Missing success criteria
- Unstated assumptions
- Ignored edge cases
- No risk assessment
- Skipping design phase
- Proceeding without approval

---

## 1.2. Fresh-Start Context Requirements

**All specs, bug reports, and issues MUST be self-contained for agents with NO memory context.**

A different AI agent (or the same agent after a context reset) may pick up this spec without:
- Prior conversation history
- Mental context from discovery phases
- Background knowledge of why decisions were made

### Mandatory Self-Containment Rules

**Specs MUST include ALL context inline:**

1. **No "see above" or "as discussed" references**
   - ❌ "As discussed above..."
   - ❌ "See the previous comment..."
   - ❌ "As mentioned in the chat..."
   - ✅ RESTATE all information inline in the spec

2. **Explicit file/line references**
   - Include exact file paths: `src/module/file.py`
   - Use STABLE ANCHORS: function names `process_data()`, class names `ClassName`, or section headers `"Section Name"`
   - ⚠️ AVOID line numbers `file.py:42` — they break on every edit
   - Include relevant code snippets (if short, <20 lines)

3. **Cross-references with context**
   - When referencing other issues/specs: include issue number AND brief summary
   - Include URLs: `https://github.com/owner/repo/issues/123`
   - State WHY the reference matters

4. **Decision rationale documented**
   - Why was this approach chosen?
   - What alternatives were considered?
   - What constraints drove the decision?

### Fresh-Start Context Checklist

Before submitting any spec, verify ALL of the following:

| Element | Required Content |
|---------|------------------|
| **Problem Statement** | What is broken/needed and WHY (with context) |
| **Affected Files** | List of files with function/section anchors and snippets |
| **Related Issues** | Links + summaries + relevance explanation |
| **Context** | Background on affected systems, prior decisions |
| **Constraints** | Technical, resource, time, compatibility limits |
| **Assumptions** | What we're assuming that may not be true |
| **Success Criteria** | Testable, measurable completion criteria |
| **Edge Cases** | Identified boundary conditions |
| **Dependencies** | External systems, libraries, affected teams |
| **Risk Assessment** | What could go wrong and mitigations |
| **Decision Rationale** | Why this approach was chosen |

### Example: Bad vs Good Spec Context

**❌ BAD (assumes memory context):**
> Fix the bug in the authentication module as discussed.

**✅ GOOD (self-contained):**
> **Problem:** The OAuth2 token refresh fails when the refresh token expires (issue #123).
>
> **Location:** `src/auth/oauth_client.py` in `refresh_token()` function:
> ```python
> def refresh_token(self):
>     # BUG: Does not handle expired refresh_token
>     response = self._request_token(...)
>     # Raises TokenExpiredError instead of re-authenticating
> ```
>
> **Context:** Users reported being logged out after 7 days (token expiry). Related to #100 (persistent sessions).
>
> **Decision:** Re-authenticate using stored credentials rather than failing.

---

## 2. Spec Persistence

### GitHub Issues Are the Authoritative Source

**GitHub Issues are ALWAYS the spec tracking mechanism, regardless of MCP availability:**

- **When GitHub MCP tools available**: Use GitHub MCP tools for all GitHub operations
- **When GitHub MCP unavailable**: Use `gh` CLI for GitHub operations
- **NO LOCAL PLAN FILES**: There is no fallback to `plans/SPEC-*.md` files

This ensures consistent workflow and prevents context fragmentation.

---

*Source: Content migrated from `040-plan-delivery.md`*