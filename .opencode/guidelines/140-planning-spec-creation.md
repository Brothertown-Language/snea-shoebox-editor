# Planning: Spec Creation

> **See `dev-architect` skill for complete spec design workflow.**

## Spec-Driven Development Workflow

AI agents MUST follow the **Spec-Driven Development** (Gated Workflow) approach:

1. **Specify Phase**: Define **What & Why**. High-level vision → detailed specification.
2. **Plan Phase**: Define **How**. Technical plan with architecture and constraints. **Invoke `/skill dev-architect --task design-plan` at Plan phase.**
3. **Tasks Phase**: Break plan into **small, reviewable chunks**.
4. **Implement Phase**: **Execute** tasks and **verify** results.

**CRITICAL**: Investigation and Planning phases are AUTO-COMPLETED before spec creation.

**INVESTIGATION CHECKPOINT**: Before creating a spec, verify investigation is complete:
- Problem understood with context
- Codebase explored for existing patterns
- Hypotheses tested with isolated test scripts
- Alternatives considered with tradeoffs
- Risks identified with mitigation strategies
- Success criteria defined (testable, measurable)

---

## Concern-Based Phases with Interdependencies (MANDATORY)

**All specs MUST define phases based on separation of concerns, risk, blast radius, and interdependencies.**

### Phase Ordering Principles

| Priority | Principle | Description |
|----------|-----------|-------------|
| **1 (HIGHEST)** | **Interdependencies First** | If Phase B depends on Phase A, A MUST be implemented first |
| **2** | **Smallest Blast Radius** | Data layer before business logic before API/UI |
| **3** | **Low Risk Before High Risk** | Read-only before mutations; additive before modifications |
| **4** | **Single Concern Per Phase** | One layer, one module, or one responsibility per phase |

### Interdependency Declaration (Required)

Every phase MUST declare its interdependencies:

```markdown
## Phase N: [Concern Name] (Risk: LEVEL, Blast Radius: SIZE)

**Interdependencies**: [NONE | Phase M (what it requires)]

**Why this order**: [One-sentence explanation]

### Steps
1. ☐ [Specific, atomic step - one git commit]
```

> **See `concern-separation-auditor` skill for complete phase structure validation.**

---

## Spec Requirements (MANDATORY)

**Every specification MUST include:**

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

**🚫 FORBIDDEN in Specs:**
- Vague requirements ("make it better")
- Missing success criteria
- Unstated assumptions
- Ignored edge cases
- No risk assessment
- Skipping design phase
- Proceeding without approval

---

## User Prompt Preservation (MANDATORY)

**When creating or revising a spec, the agent MUST preserve the user's original prompt as context.**

### Prompt Capture Requirement

1. **When creating a new spec:**
   - After creating the GitHub Issue, immediately post a comment with the user prompt
   - Format: See "User Prompt Comment Format" in `github-comments` skill

2. **When revising an existing spec:**
   - After updating the issue body, post a comment with the revision prompt

3. **Multiple prompts:**
   - Capture the triggering prompt
   - Optionally capture key context messages as separate comments

### What to Capture

| Prompt Element | Capture? |
|----------------|----------|
| Exact user prompt text | ✅ YES |
| Key context from conversation | ✅ YES |
| Decision to create spec | ✅ YES |
| Code snippets in prompt | ✅ YES |

> **See `github-comments` skill → "User Prompt Comment Format" section.**

---

## Fresh-Start Context Requirements (MANDATORY)

**All specs MUST be self-contained for agents with NO memory context.**

A different AI agent may pick up this spec without:
- Prior conversation history
- Mental context from discovery phases
- Background knowledge of why decisions were made

### Mandatory Self-Containment Rules

1. **No "see above" or "as discussed" references**
   - ✅ RESTATE all information inline in the spec

2. **Explicit file/line references**
   - Include exact file paths: `src/module/file.py`
   - Use STABLE ANCHORS: function names, class names, section headers
   - ⚠️ AVOID line numbers `file.py:42` — they break on every edit

3. **Cross-references with context**
   - Include issue number AND brief summary
   - Include URLs: `https://github.com/<owner>/<repo>/issues/123`
   - State WHY the reference matters

4. **Decision rationale documented**
   - Why was this approach chosen?
   - What alternatives were considered?
   - What constraints drove the decision?

### Fresh-Start Context Checklist

| Element | Required Content |
|---------|------------------|
| **Problem Statement** | What is broken/needed and WHY (with context) |
| **Affected Files** | List of files with function/section anchors |
| **Related Issues** | Links + summaries + relevance explanation |
| **Context** | Background on affected systems, prior decisions |
| **Constraints** | Technical, resource, time, compatibility limits |
| **Assumptions** | What we're assuming that may not be true |
| **Success Criteria** | Testable, measurable completion criteria |
| **Edge Cases** | Identified boundary conditions |
| **Dependencies** | External systems, libraries, affected teams |
| **Risk Assessment** | What could go wrong and mitigations |
| **Decision Rationale** | Why this approach was chosen |

---

## Spec Reality Sync

**Specs must reflect current code/implementation state.** If drift is detected:

1. **Code is authoritative** — the spec is secondary
2. **Update the spec to match reality** — this is administrative sync, not implementation
3. **Report the synchronization and HALT**
4. **This exemption applies ONLY to spec files in GitHub Issues**
5. **`.opencode/guidelines/` modifications require full spec-first workflow**

---

## GitHub MCP Required — No Fallback

**When GitHub MCP tools are NOT available, the agent MUST refuse planning work entirely.**

### 🚫 NO FALLBACK TO LOCAL FILES
- **PROHIBITED**: Using `plans/SPEC-*.md` files as fallback
- **PROHIBITED**: Creating local plan files when GitHub MCP unavailable
- **PROHIBITED**: Proceeding with implementation without GitHub Issue tracking

### ✅ REQUIRED ACTION
- If GitHub MCP is unavailable, STOP immediately
- Report: "GitHub MCP tools unavailable. Cannot create or track specs without GitHub Issues."
- Wait for GitHub MCP to be restored before proceeding

---

## Terminology: Spec vs. Guideline Files

- **"Create a new spec"** = Create a GitHub Issue with `[SPEC]` prefix
- **"Create a guideline file"** = Create/modify files in `.opencode/guidelines/`
- **SPEC = GitHub Issue** — Specs are planning/tracking artifacts, not file system artifacts

---

## Listing Available Specs

When the user issues commands `specs` or `pending`:

1. **Gather all top-level specs**: Query open GitHub Issues with `[SPEC]` prefix in title
2. **Check for superseding issues AND staleness**: Query for later `[SPEC]`/`[SPEC-FIX]`/`[SPEC-ENHANCEMENT]` issues
3. **Present a multi-choice user query**: Use `question` tool with spec titles and STATUS
4. **After user selection**: Load spec content, show current status, HALT

**Response format:**
```
Available Specs:
- [SPEC] Feature A (STATUS: 1.2)
- [SPEC] Feature B (STATUS: 2.1)
```