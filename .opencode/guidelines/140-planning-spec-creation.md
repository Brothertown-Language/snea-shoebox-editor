# Planning: Spec Creation

## Spec-Driven Development Workflow

AI agents MUST follow the **Spec-Driven Development** (Gated Workflow) approach:

1. **Specify Phase**: Define **What & Why**. Kick off with a high-level vision (product brief), then expand it into a detailed specification focusing on user journeys, experiences, and success criteria.
2. **Plan Phase**: Define **How**. Draft the technical plan (architecture, technical stack, and constraints). **Invoke `/skill dev-architect --task design-plan` at Plan phase.**
3. **Tasks Phase**: Break the plan into **small, reviewable chunks** (tasks) that can be implemented and tested in isolation.
4. **Implement Phase**: **Execute** tasks and **verify** results.

**CRITICAL**: Investigation and Planning phases are AUTO-COMPLETED before the spec is created. The spec file ONLY contains implementation and verification phases.

**INVESTIGATION CHECKPOINT**: Before creating a spec, the agent MUST verify investigation is complete. See `142-planning-archive-workflow.md` for investigation completion criteria and permissible test activities.

---

## 1.4. Concern-Based Phases with Interdependencies (MANDATORY)

**All specs MUST define phases based on separation of concerns, risk, blast radius, and interdependencies.**

### Phase Ordering Principles

**Phases MUST be ordered using these principles (in priority order):**

| Priority | Principle | Description |
|----------|-----------|-------------|
| **1 (HIGHEST)** | **Interdependencies First** | If Phase B depends on Phase A, then A MUST be implemented before B |
| **2** | **Smallest Blast Radius** | Data layer changes before business logic before API/UI |
| **3** | **Low Risk Before High Risk** | Read-only changes before mutations; additive before modifications |
| **4** | **Single Concern Per Phase** | One layer, one module, or one responsibility per phase |

### Interdependency Ordering (Critical)

**TOP PRIORITY: Dependencies before dependents (topological order)**

The interdependency ordering principle ensures:
- **Cherry-pick safety**: Any single commit can be cherry-picked without breaking builds (dependencies are already present)
- **Revert safety**: Reverting a commit won't leave orphaned dependents (dependents come later)
- **Independent units**: Each discrete unit is independently buildable at its concern-level
- **Atomic changes**: Each phase focuses on one concern boundary

**Declaration Format:**

Every phase MUST declare its interdependencies:

```markdown
## Phase N: [Concern Name] (Risk: LEVEL, Blast Radius: SIZE)

**Interdependencies**: [NONE | Phase M (what it requires)]

**Why this order**: [Explanation of why this phase depends on previous phases]

### Steps
1. ☐ [first step]
2. ☐ [second step]
```

**Example:**

```markdown
## Phase 3: Business Logic (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies**: Phase 1 (user table schema must exist)

**Why this order**: AuthRepository depends on user table. Cannot implement business logic without data foundation.

### Steps
1. ☐ Create AuthRepository class
2. ☐ Implement password hashing
3. ☐ Add session management
```

### Topological Ordering Algorithm

**When ordering phases, use this algorithm:**

1. **Build dependency graph**: For each phase, identify all phases it depends on
2. **Detect cycles**: If circular dependency found, refactor or combine phases
3. **Topological sort**: Order phases so all dependencies come before dependents
4. **Apply secondary principles**: Within dependency constraints, order by blast radius (smallest first), then risk (lowest first)

**Conflict Resolution:**

When ordering principles conflict, resolve in this order:
1. **Interdependencies** (must be satisfied first - CYCLIC DEPENDENCIES ARE BLOCKING)
2. **Blast Radius** (smaller scope preferred when no dependency conflict)
3. **Risk** (lower risk preferred when blast radius is equal)
4. **Concern Separation** (automatically satisfied if 1-3 are satisfied)

### Separation of Concerns for Phases

**What is a "concern" for phase definition?**

A concern is a bounded area of responsibility with:
- **Single layer**: Data, Business Logic, API, Presentation, Infrastructure
- **Single module**: Authentication, Search, Notifications, Reporting
- **Single responsibility**: Query optimization, Error handling, Caching

**Phase should modify ONE concern:**

| Phase Concern Type | Examples | What It Includes |
|-------------------|----------|-----------------|
| **Data Layer** | Database schema, migrations, repositories | Tables, indexes, data access code |
| **Business Logic** | Services, domain models, validation rules | Core algorithms, business rules |
| **API Layer** | Endpoints, request/response handling | HTTP handling, routing, serialization |
| **Presentation** | UI components, views, templates | Frontend code, user interface |
| **Infrastructure** | Caching, logging, monitoring | Cross-cutting concerns |
| **Testing** | Unit tests, integration tests, E2E tests | Verification for a specific concern |

**Phase isolation rules:**
- Data layer changes should NOT touch API code
- Business logic changes should NOT touch presentation layer
- Each phase should be reviewable in isolation

### Risk Profiles

**Each phase MUST have a risk profile:**

| Risk Level | Characteristics | Examples |
|------------|-----------------|----------|
| **LOW** | Read-only, additive, localized, easily reversible | Adding a new query, adding a new test file, documentation |
| **MEDIUM** | Modifies existing code, affects one module, moderate rollback complexity | Refactoring a service, adding a new API endpoint, modifying schema |
| **HIGH** | Breaking changes, affects multiple modules, hard to rollback, production-critical | Database migration, authentication rewrite, API versioning, deployment changes |

### Blast Radius Assessment

**Each phase MUST have a blast radius assessment:**

| Blast Radius | Scope | Testing Required | Rollback Difficulty |
|--------------|-------|------------------|---------------------|
| **SMALL** | Single file/module, no dependencies | Unit tests only | Easy (simple revert) |
| **MEDIUM** | Multiple files, internal dependencies | Integration tests | Moderate (may need data migration) |
| **LARGE** | Cross-module, external dependencies | Full test suite | Difficult (may need data rollback, coordination) |

### Cherry-Pick and Revert Guarantees

**With interdependency ordering, the following guarantees apply:**

**Cherry-Pick Guarantees:**
- Any phase's commits can be cherry-picked independently (dependencies already present)
- Build will not break from cherry-picking a single phase
- Tests for that phase will pass without additional phases

**Revert Guarantees:**
- Reverting a phase won't break dependent phases (they don't exist yet)
- No orphaned code or incomplete dependencies after revert
- Clean rollback to previous phase boundary

**Interactive Rebase Guarantees:**
- Phases can be reordered within dependency constraints
- Dropping a phase won't break later phases (dependency check required)
- Squashing phases preserves interdependency ordering

### Phase Template with Interdependencies

**Required template for every phase:**

```markdown
## Phase N: [Concern Name] (Risk: [LOW|MEDIUM|HIGH], Blast Radius: [SMALL|MEDIUM|ARGE])

**Interdependencies**: [NONE|Phase M (what must exist before this phase)]

**Why this order**: [One-sentence explanation of dependency]

### Steps
1. ☐ [Specific, atomic step - one git commit]
2. ☐ [Specific, atomic step - one git commit]
3. ☐ [Specific, atomic step - one git commit]

### Success Criteria
1. ✅ [Measurable, testable criterion]
2. ✅ [Measurable, testable criterion]
```

**Example - Complete Feature:**

```markdown
## Phase 1: User Table Schema (Risk: LOW, Blast Radius: SMALL)

**Interdependencies**: NONE

**Why this order**: Foundation - no dependencies on other phases.

### Steps
1. ☐ Add users table with authentication columns
2. ☐ Create user repository class
3. ☐ Write migration script

---

## Phase 2: Authentication Service (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies**: Phase 1 (user table must exist)

**Why this order**: Authentication service depends on user table for credential storage.

### Steps
1. ☐ Implement password hashing with bcrypt
2. ☐ Add session token generation
3. ☐ Create login/logout methods

---

## Phase 3: API Endpoints (Risk: MEDIUM, Blast Radius: MEDIUM)

**Interdependencies**: Phase 2 (authentication service must exist)

**Why this order**: API endpoints expose authentication service through HTTP layer.

### Steps
1. ☐ Add /login endpoint
2. ☐ Add /logout endpoint
3. ☐ Add /refresh-token endpoint

---

## Phase 4: Integration Tests (Risk: LOW, Blast Radius: MEDIUM)

**Interdependencies**: Phases 1-3 (all functionality must exist)

**Why this order**: Integration tests verify all components work together end-to-end.

### Steps
1. ☐ Write login flow test
2. ☐ Write token refresh test
3. ☐ Write logout flow test
```

### Circular Dependency Detection

**If circular dependencies are detected, resolve by:**

1. **Refactoring**: Split shared responsibilities into separate phases
2. **Combining**: Merge interdependent phases into single larger phase
3. **Extracting**: Create shared dependency that both phases can depend on

**Example - Circular Dependency:**

```
Phase A depends on Phase B
Phase B depends on Phase C
Phase C depends on Phase A  ← CIRCULAR

Solutions:
1. Extract shared code into Phase D that A, B, C all depend on
2. Combine A, B, C into a single phase
3. Redesign to break circular dependency in architecture
```

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

## 1.2. User Prompt Preservation (MANDATORY)

**When creating or revising a spec, the agent MUST preserve the user's original prompt as context.**

### Why Prompt Preservation Matters

The user's original prompt contains:
- The initial intent and motivation behind the request
- Nuanced context that may not be captured in the spec body
- Specific constraints, preferences, or edge cases the user mentioned
- Background information that informed the decision

Without the original prompt context:
- Future agents lose critical information about the user's intent
- Decision rationale may be unclear
- Subtle requirements may be missed in implementation

### Prompt Capture Requirement

**ALWAYS capture the user prompt as a comment on the spec issue:**

1. **When creating a new spec:**
   - After creating the GitHub Issue, immediately post a comment with the user prompt
   - Format: See "User Prompt Comment Format" in `github-comments` skill

2. **When revising an existing spec:**
   - After updating the issue body, post a comment with the revision prompt
   - Include both the new prompt and any additional context provided

3. **Multiple prompts:**
   - If the user provides multiple messages before spec creation, capture the triggering prompt
   - Optionally capture key context messages as separate comments

### What to Capture

| Prompt Element | Capture? | Format |
|----------------|----------|--------|
| Exact user prompt text | ✅ YES | Verbatim or minimal editing |
| Key context from conversation | ✅ YES | Summarized in separate section |
| Decision to create spec | ✅ YES | Brief note on why spec was created |
| Code snippets in prompt | ✅ YES | Include verbatim |

### Edge Cases

| Scenario | Action |
|----------|--------|
| Prompt is very long | Summarize key points, link to full conversation if available |
| User provides clarifications | Add clarification comments separately |
| Confidential/sensitive info | Allow user to redact before posting |

### Integration with Fresh-Start Context

User prompt preservation COMPLEMENTS the fresh-start context rules:

| Context Type | Location |
|--------------|----------|
| User's original prompt | First comment on issue |
| Detailed analysis | Issue body (Problem Statement, Context, etc.) |
| Related issues | Issue body (Related Issues section) |
| User clarifications | Follow-up comments |

**The prompt comment provides the "WHY" — the issue body provides the "WHAT" and "HOW".**

---

## 1.3. Fresh-Start Context Requirements

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
   - Include URLs: `https://github.com/<owner>/<repo>/issues/123`
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