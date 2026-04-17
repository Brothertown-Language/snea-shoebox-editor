# Planning: Spec Creation

## Spec-Driven Development Workflow

AI agents MUST follow the **Spec-Driven Development** (Gated Workflow) approach with the **Plan-Bridge Hierarchy**:

1. **Specify Phase**: Define **What & Why**. Kick off with a high-level vision (product brief), then expand it into a detailed specification focusing on user journeys, experiences, and success criteria.
2. **Plan Phase** (Bridge): Define **How**. Create a plan issue (`[PLAN]` prefix, `plan` label) that references the spec via body linked reference. The plan bridges spec → tasks. **Spec approval authorizes plan creation; plan approval authorizes implementation.**
3. **Tasks Phase**: Break the plan into **small, reviewable chunks** (sub-issues under the plan, not the spec) that can be implemented and tested in isolation.
4. **Implement Phase**: **Execute** tasks and **verify** results.

**Two-Gate Model:**
- **Gate 1 — Spec Approval → Plan Creation**: Spec approval authorizes creating the plan issue. The spec references the plan via body text (linked reference, e.g., `Related Plan: #NNN`), NOT via GitHub sub-issue link.
- **Gate 2 — Plan Approval → Implementation**: Plan approval authorizes implementation. Authorization cascades from the plan to all its sub-issues.

**Plan-Bridge Hierarchy:** Spec → (body linked reference) → Plan → Sub-issues

**CRITICAL**: Investigation and Planning phases are AUTO-COMPLETED before the spec is created. The spec file ONLY contains implementation and verification phases.

**INVESTIGATION CHECKPOINT**: Before creating a spec, the agent MUST verify investigation is complete. See `142-planning-archive-workflow.md` for investigation completion criteria and permissible test activities.

**SPEC REVISION**: When a spec is revised, all linked plan approvals are revoked. The old plan is closed and a new plan must be created and approved. See `010-approval-gate.md` §"Revision Revokes Approval" and §"Re-implementation Workflow".

______________________________________________________________________

## Terminology: Spec vs. Plan vs. Guideline Files

- **"Create a new spec"** = Create a GitHub Issue with `[SPEC]` prefix (Mandatory when GitHub MCP available)
- **"Create a plan"** = Create a GitHub Issue with `[PLAN]` prefix and `plan` label, referencing the spec via body linked reference
- **"Create a guideline file"** = Create/modify files in `.opencode/guidelines/` (Implementation task)
- **SPEC = GitHub Issue** — Specs are planning/tracking artifacts, not file system artifacts
- **PLAN = GitHub Issue** — Plans are separate issues that bridge specs to implementation sub-issues; sub-issues are children of the plan, not the spec

______________________________________________________________________

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

______________________________________________________________________

## 1.1. Issue Tracking Required — Platform Routing

**When issue tracking tools are NOT available, the agent MUST refuse planning work entirely.**

### NO FALLBACK TO LOCAL FILES

- **PROHIBITED**: Using `plans/SPEC-*.md` files as fallback when issue tracking is unavailable
- **PROHIBITED**: Creating local plan files when issue tracking is unavailable
- **PROHIBITED**: Proceeding with implementation without issue tracking

### REQUIRED ACTION

- If issue tracking tools are unavailable, STOP immediately
- Report: "Issue tracking tools unavailable. Cannot create or track specs without issue tracking."
- Wait for issue tracking to be restored before proceeding

### Platform Routing

| `github.platform` | Platform Sub-Skill |
|----------------|-------------------|
| `github` | `issue-operations/platforms/github-mcp/` |
| `gitbucket` | `issue-operations/platforms/gitbucket-api/` |
| (unset) | `issue-operations/platforms/github-mcp/` (default) |

______________________________________________________________________

## 1. Spec Reality Sync

**Specs must reflect current code/implementation state.** If drift is detected between a spec and the actual code:

1. **Code is authoritative** — the spec is secondary
2. **Update the spec to match reality** — this is administrative sync, not implementation
3. **Report the synchronization and HALT**
4. **This exemption applies ONLY to spec files in GitHub Issues**
5. **`.opencode/guidelines/` modifications require full spec-first workflow**

______________________________________________________________________

## 1.1. Spec Content Requirements

**Every specification MUST cover these content areas.** The format is up to the agent — a simple spec may cover several areas in a single paragraph, while a complex spec may use separate sections.

### Content Coverage Questions

| Question | Why It Matters |
|----------|---------------|
| Does the spec clearly state the problem it solves and why? | Without this, the reader doesn't know what they're solving or whether the solution addresses the right thing |
| Does the spec provide enough context for someone with no prior knowledge? | Agents lack memory context; the spec must be self-contained |
| Does the spec identify what constraints and assumptions apply? | Constraints shape the solution space; assumptions may be wrong and need verification |
| Does the spec define testable success criteria? | Binary pass/fail criteria are the only reliable way to verify completion |
| Does the spec address edge cases and risks? | Unhandled edge cases become production bugs |
| Does the spec explain why the chosen approach was selected? | Without rationale, the implementer might make different assumptions |
| Does the spec identify affected files with stable anchors? | File paths and function names (not line numbers) enable targeted implementation |
| Does the spec reference related issues with context? | Cross-references prevent duplicate work and ensure consistency |
| Does the spec define what is explicitly out of scope? | Non-requirements prevent scope creep |

### Anti-Patterns in Specifications

**🚫 FORBIDDEN in Specs:**

- Vague requirements ("make it better")
- Missing success criteria
- Unstated assumptions
- Ignored edge cases
- No risk assessment
- Skipping design phase
- Proceeding without approval

### Simple vs Complex Specs

**Simple specs** (bug fixes, one-file changes, obvious solutions) may address all required content areas in a few paragraphs. A minimal spec can be as short as:

> Problem → Context → Fix approach → Success criteria → Edge cases

**Complex specs** (multi-file changes, cross-cutting concerns, architectural decisions) typically use separate sections for each content area. The `brainstorming` skill and `spec-creation` skill tasks provide prompts for thinking through each area.

**The key principle: every content area must be addressed, but agents choose the format that matches the spec's complexity.**

______________________________________________________________________

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
   - Include relevant code snippets (if short, \<20 lines)

3. **Cross-references with context**

   - When referencing other issues/specs: include issue number AND brief summary
   - Include URLs: `https://github.com/owner/repo/issues/123`
   - State WHY the reference matters

4. **Decision rationale documented**

   - Why was this approach chosen?
   - What alternatives were considered?
   - What constraints drove the decision?

### Context Coverage Checklist

Before submitting any spec, verify these self-containment questions:

| Question | Why It Matters |
|----------|---------------|
| Does the spec describe the problem with full context, not just "as discussed"? | A fresh agent has no memory of earlier conversation |
| Does the spec include file paths with stable anchors (not line numbers)? | Line numbers break on every edit |
| Does the spec include code snippets for key changes (<20 lines)? | Code context prevents misunderstandings |
| Does the spec include URLs and summaries for all related issues? | Bare links without context are useless |
| Does the spec document decision rationale? | Without it, implementers may choose different approaches |

______________________________________________________________________

## 2. Spec Persistence

### GitHub Issues Are the Authoritative Source

**GitHub Issues are ALWAYS the spec tracking mechanism, regardless of MCP availability:**

- **When GitHub MCP tools available**: Use GitHub MCP tools for all GitHub operations
- **When GitHub MCP unavailable**: Use `gh` CLI for GitHub operations
- **NO LOCAL PLAN FILES**: There is no fallback to `plans/SPEC-*.md` files

This ensures consistent workflow and prevents context fragmentation.

______________________________________________________________________

*Source: Content migrated from `040-plan-delivery.md`, restructured per spec #821*