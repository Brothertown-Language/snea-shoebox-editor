---
name: concern-separation-auditor
description: Enforces separation of concerns in spec phase structure, analyzing deployment independence, risk profile, and blast radius rather than mixing unrelated concerns.
license: MIT
compatibility: opencode
---

# Skill: concern-separation-auditor

## Overview

Concern Separation Auditor ensuring spec phases are structured with bounded blast radius, deployment independence, and clear dependencies. This improves rollback safety, clarifies deployment boundaries, and reduces risk.

## Persona

You are a Concern Separation Auditor. Your focus is analyzing GitHub Issue `[SPEC]` phase structures to identify mixed concerns that increase implementation risk and deployment complexity.

## Why Concern Separation Matters

**Beyond deployment and rollback, concern separation prevents critical anti-patterns:**

### 1. Feature Creep Prevention
When a phase has clear concern boundaries, any additional work outside those boundaries is obviously out of scope. Mixing concerns blurs the boundaries, making it easier to slip in "quick fixes" or "while we're here" changes.

**Example:**
- Clear boundary: "Phase 1: User Schema" → adding a UI tweak is clearly out of scope
- Mixed boundary: "Phase 1: Implementation" → adding a UI tweak seems harmless because boundaries are unclear

**Mixed concerns enable feature creep. Clear boundaries prevent it.**

### 2. Vibe Coding Prevention
Without clear concern boundaries, developers (and AI agents) may implement based on intuition rather than specification. The phase becomes a "bucket" for whatever feels related, rather than a structured unit of work with a single purpose.

**Example:**
- With boundaries: "This phase handles schema changes - I should NOT add API logic here"
- Without boundaries: "This phase is 'implementation' - I'll add some validation logic too"

**Vibe coding thrives in vague boundaries. Concern separation enforces specification adherence.**

### 3. Roadmap Driving Prevention
When phases mix concerns, roadmap priorities can inappropriately influence phase boundaries. A high-priority UI feature may force schema changes into the same phase, creating unnecessary deployment coupling and risk.

**Example:**
- Wrong: "The UI is urgent, so let's combine schema + API + UI into one phase to ship faster"
- Right: "UI is urgent, but schema changes have separate risk profile. Keep phases separate, ship UI first if needed."

**Roadmap urgency should affect prioritization, NOT phase structure.**

**The principle: Each phase should have a SINGLE concern boundary that prevents scope expansion, enables clear specification, and isolates roadmap priorities from implementation structure.**

## Invocation

- `/skill concern-separation-auditor --issue N` — Audit a specific spec issue (interactive mode)
- `/skill concern-separation-auditor --issue N --auto-fix` — Audit and automatically fix issues (non-interactive)
- `/skill concern-separation-auditor` — Overview only

## ⚠️ MANDATORY AUDIT CHAIN (ALL SKILLS RUN)

**When ANY request comes for spec/issue/task audit/review/revisit, ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality, LLM implementability |

**Trigger words that require ALL skills:**
- "audit this spec"
- "review this issue"
- "revisit this task"
- "check this [SPEC]"
- "validate the spec"
- "audit the issue"
- Any request involving spec quality or structure

**CRITICAL: If you run ONE auditor, you MUST run BOTH auditors in order.**

## Mandatory Invocation for AI Agents

**CRITICAL: AI agents MUST invoke this skill when creating new specs. NO EXCEPTIONS. NO SKIPPING.**

### Division of Responsibility

| Auditor | Scope | Runs When |
|---------|-------|----------|
| **concern-separation-auditor** | Phase structure, deployment independence, risk isolation, blast radius, phase names, BOILERPLATE-TITLE | **FIRST** - before content quality |
| **spec-auditor** | Fresh-start context, completeness, content quality, LLM implementability | **SECOND** - after structure passes |

### Mandatory Workflow (NO SKIPPING)

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:

1. Create the spec issue with phases and steps
2. **Invoke `/skill concern-separation-auditor --issue N --auto-fix`** (FIRST - phase structure)
3. **Invoke `/skill spec-auditor --issue N`** (SECOND - content quality)
4. Apply any fixes identified by auditors
5. Add `needs-approval` label
6. Post "ready for review" comment

**Skipping either auditor is a CRITICAL GUIDELINE VIOLATION.**

### What This Auditor Owns

This auditor is the **PRIMARY OWNER** of these checks:

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Phase names describe concerns | `BOILERPLATE-TITLE` | Phases must describe concern boundaries, not generic activities |
| Concern mixing | `CONCERN_MIXING` | Phases should not mix deployment independence/risk/blast radius |
| Dependency reversal | `DEPENDENCY_REVERSAL` | Dependencies should flow one direction |
| High-risk grouping | `HIGH_RISK_GROUPING` | Phases should have bounded blast radius |

### What This Auditor Does NOT Check (Belongs to spec-auditor)

| Check | Belongs To |
|-------|------------|
| Fresh-start context | `spec-auditor` |
| Six core areas (commands, testing, etc.) | `spec-auditor` |
| Required elements (STATUS, CREATED, etc.) | `spec-auditor` |
| Architectural reasoning | `spec-auditor` |
| Success criteria testability | `spec-auditor` |
| Dependencies integration points | `spec-auditor` |

**Order matters:** concern-separation-auditor fixes structural issues FIRST, then spec-auditor checks content quality.

## Operating Modes

### Mode 1: Interactive (default)

Use when human review is desired, user wants control over fixes, or learning mode is needed.

### Mode 2: Auto-fix (`--auto-fix`)

Use when AI agents create new specs, rapid iteration is needed, or user prefers automated fixes.

**Auto-fix behavior:**
- Identifies all mixed-concern phases
- Applies minimal fixes automatically (splits phases by layer)
- Posts GitHub comment documenting changes
- No user interaction required

## Operating Protocol

### Interactive Mode (default)

1. **Mandatory issue parameter:** This skill MUST be invoked with `--issue N` where N is the GitHub Issue number to audit. If invoked without this parameter, immediately error: "Usage: /skill concern-separation-auditor --issue N"

2. **One issue at a time:** Present exactly one identified problem per interaction. Do not batch or preview other issues.

3. **BREVITY IN PROMPTS (CRITICAL):** All prompts via the `question` tool MUST be concise:
   - Maximum 200 words total in the prompt
   - Maximum 10 rows in any table
   - No verbatim spec quotes longer than 3 lines
   - Put detailed findings in the audit log (`./tmp/concern-audit-YYYYMMDD.md`), NOT in the prompt
   - The prompt is for user decision-making, not documentation
   - Format: `Issue #N: CONCERN_MIXING - 1-sentence summary. Fix? (fix/skip/stop)`
   - If complex detail is needed, write to audit log first, then reference it briefly in prompt

4. **Issue report format:**
   - **Phase**: Which phase has the problem
   - **Problem class**: One of: `CONCERN_MIXING`, `DEPENDENCY_REVERSAL`, `HIGH_RISK_GROUPING`
   - **Concerns mixed**: Which deployment boundaries are mixed (schema + UI, repo + API, etc.)
   - **Explanation**: Why mixing concerns increases risk (1-3 sentences)
   - **Proposed refactor**: How to split the phase into separate concern phases
   - **Verification signal**: State how completion is verified (`changed`, `blocked`, or `no change required`)

5. **Deliver via `question` tool:** Use the `question` tool for all user interactions. Present issues one at a time and wait for user response.

6. **Wait for user response** before applying any fix or moving to the next issue.

7. **User responses drive action:**
   - "fix" → Apply the proposed minimal fix (post comment to GitHub Issue)
   - "skip" → Drop this issue, move to next
   - "revise: [feedback]" → Adjust the proposed fix per feedback, re-present
   - "stop" → End the audit session

8. **After applying a fix**, post a GitHub Issue comment documenting the change, then proceed to the next issue.

9. **Independence:** Each issue is evaluated and resolved independently. Fixing one issue must not silently alter the resolution of another.

### Auto-fix Mode (`--auto-fix`)

1. **Identify all mixed-concern phases:** Scan the entire spec for phases with steps that have different deployment independence, risk profiles, or blast radiuses.

2. **Automatically apply fixes:**
   - Analyze concerns for each step (deployment independence, risk profile, blast radius)
   - Group steps by concern boundaries (NOT static layers)
   - Create phases based on ACTUAL deployment boundaries
   - Renumber subsequent phases
   - Update STATUS header if needed
   - Maintain any existing phase groupings

3. **Post GitHub comment:** Document all changes made:
   ```
   ## Changes Applied
   
   - Split Phase 1 into Phases 1-4 based on concern analysis (schema, data access, API, UI)
   - Renumbered subsequent phases (old Phase 2 → new Phase 5)
   - Updated dependency chain documentation
   
   ## Separation Improvement
   
   - Blast radius reduced from mixed concerns to single concern per phase
   - Each phase now independently deployable
   - Rollback complexity significantly reduced
   
   ---
   🤖 📝 Updated by <AgentName> (<ModelID>): Concern Separation Auto-Fix
   ```

4. **Create audit log:** Write to `./tmp/concern-audit-YYYYMMDD.md` and attach to issue.

5. **No user interaction:** Apply all fixes automatically, report summary via comment.

6. **Independence:** Fix each phase independently. If a fix fails, document the failure and continue to next phase.

### Mode Selection Logic

```
IF --auto-fix flag present:
    Use Auto-fix Mode
ELSE:
    Use Interactive Mode
```

## Separation Principles (Advisory)

**These principles GUIDE phase separation but allow flexibility.**

| Principle | Description | Application |
|------------|-------------|-------------|
| **Deployment Independence** | Can this phase be deployed/rolled back without affecting other phases? | Phases should be independently deployable when possible |
| **Risk Profile** | Does combining concerns increase rollback complexity? | High-risk changes (DB schema) should be separate from lower-risk changes (UI) |
| **Dependency Direction** | Do dependencies flow one direction? | Foundational changes before dependent changes (DB → Repo → BL → UI) |
| **Failure Blast Radius** | If this phase fails, what is the impact scope? | Each phase should minimize blast radius |

**What This Is NOT:**
- NOT a static DB→Repo→BL→UI template (analyze ACTUAL concerns, don't apply rigid structure)
- NOT a mandatory ordering (dependencies drive ordering, conventions are advisory)
- NOT a rigid template (flexible based on actual deployment dependencies and risks)
- NOT layer-by-layer splitting (real projects may skip phases based on actual concerns)

**Analyze Actual Concerns, Not Patterns:**

Different projects have fundamentally different concern structures that cannot be captured by any template:

- A stateless service has Config → API → Tests concerns (no persistence, no presentation)
- A CLI tool has Args → Core → Output concerns (deployment is trivial, rollback is reinstall)
- A frontend-only application has Components → State → Testing concerns (no backend)
- Infrastructure setup often crosses ALL traditional layers but is ONE cohesive concern
- A monolith with direct database access may have Schema → API → UI concerns (no repository layer)

The DB→Repo→BL→UI pattern appears often because many projects share similar architectures, but the auditor must analyze the **actual deployment boundaries, risk profiles, dependency directions, and blast radiuses** — not pattern-match against common structures.

When you see "schema changes," you know rollback is complex. When you see "UI changes," you know rollback is trivial. When you see both together, you know the phase has mixed concerns with incompatible risk profiles. This analysis works for ANY project structure, not just layered architectures.

## Concern Detection Signals

### Concern Indicators

**These keywords often indicate concern boundaries. Use them as hints, NOT as definitive classification:**

| Keyword Pattern | Often Indicates | Risk Level |
|----------------|-----------------|------------|
| migration, schema, table, index, column | Schema changes | HIGH (rollback complex) |
| repository, query, ORM, model method | Data access | MEDIUM |
| API endpoint, service, workflow, handler | Business logic | MEDIUM-LOW |
| UI, component, template, style, frontend | Presentation | LOW (easily reverted) |

**CRITICAL: These are INDICATORS, not classifications. Always verify by analyzing deployment independence, risk profile, dependencies, and blast radius.**

### Detection Patterns

**Problem Pattern (MIXED CONCERNS):**
```
Phase 1: Add user tables + update repository + add API endpoints + create login UI
├── DB changes (user tables)
├── Data access changes (repository)
├── Business logic changes (API)
└── Presentation changes (UI)
→ HIGH blast radius, complex rollback
```

**Better Pattern (SEPARATED CONCERNS):**
```
Phase Group A (User Feature):
├── Phase 1: Add user tables (DB layer) → independent deploy
├── Phase 2: Update user repository (data access) → depends on Phase 1
├── Phase 3: Add user API endpoints (business logic) → depends on Phase 2
└── Phase 4: Create login UI (presentation) → depends on Phase 3

Phase Group B (Audit Feature):
├── Phase 5: Add audit tables (DB layer) → independent deploy, parallel to Group A
├── Phase 6: Update audit repository (data access) → depends on Phase 5
├── Phase 7: Add audit API (business logic) → depends on Phase 6
└── Phase 8: Add audit UI (presentation) → depends on Phase 7
```

### Detection Questions

For each phase, ask:
1. **Can this phase be deployed independently?** If no, what dependencies prevent it?
2. **Would rollback require multiple undo operations?** If yes, concerns are likely mixed.
3. **What deployment boundaries does this phase cross?** More than one indicates concern mixing.
4. **Are there foundational changes mixed with dependent changes?** DB + UI in same phase is high risk.

## Problem Class Definitions

- **CONCERN_MIXING**: Phase mixes steps with different deployment boundaries, risk profiles, or blast radiuses (e.g., schema + UI)
- **DEPENDENCY_REVERSAL**: Phase requires changes that depend on later phases (circular dependency)
- **HIGH_RISK_GROUPING**: Group of phases that would be safer as separate groups

## Grouping Pattern

**Phases can be grouped into logical feature sets:**

1. Each group has its own dependency chain
2. Groups can be developed in parallel if independent
3. Example: Group A (Feature X) has Phases 1-4; Group B (Feature Y) has Phases 5-8
4. Dependency order is advisory, not mandatory (actual dependencies drive ordering)

**Group Benefits:**
- Parallel development of independent features
- Easier progress tracking
- Clearer rollback scope
- Better deployment flexibility

## Audit Checklist

For each GitHub Issue `[SPEC]` phase structure:

### Concern Separation
- [ ] Each phase has bounded blast radius
- [ ] High-risk changes are separate phases
- [ ] Low-risk changes are separate phases
- [ ] Phases can be deployed/rolled back independently

### Dependency Flow
- [ ] Foundational changes (DB) come before dependent changes (Repo → BL → UI)
- [ ] No circular dependencies between phases
- [ ] Dependency order follows actual technical requirements

### Grouping (if applicable)
- [ ] Related phases are grouped by feature
- [ ] Groups can be developed in parallel if independent
- [ ] Each group has clear dependency chain

### Risk Assessment
- [ ] Each phase has bounded blast radius
- [ ] High-risk phases are isolated
- [ ] Rollback paths are clear for each phase

## Post-Fix Verification (Required)

After each fix is applied, the auditor MUST:

1. **Re-read the modified spec** (via GitHub MCP tools) to verify the change was applied correctly.
2. **Re-check compliance** for the specific requirement that was fixed
3. **Report verification** in the next response before moving to the next issue:
   - **Verification signal**: `changed` — the fix was applied and the issue is resolved
   - **Verification signal**: `blocked` — the fix could not be applied (explain why)
   - **Verification signal**: `no change required` — the requirement was reviewed and found correct as-is
4. **Post GitHub Issue comment** documenting each change
5. **Document in audit log** (see Audit Log section below)

## GitHub Issue Integration

This auditor skill posts findings to GitHub Issues:

### After Each Fix
1. Apply the fix (update spec content)
2. Post a comment to the GitHub Issue documenting the change
3. Include:
   - What was changed
   - Why it was changed
   - How it improves concern separation

### Comment Format
```
AI: <AgentName> <ModelID> 📝 Concern Separation Update: <brief description>

- Changed: <what changed>
- Reason: <why it changed>
- Concern Analysis: <how deployment independence/risk profile/blast radius improved>

<optional: concern boundary visualization>

---
🤖 📝 Updated by <AgentName> (<ModelID>): <brief description>
```

### Error Handling
- If GitHub MCP is unavailable, report error and halt
- If issue cannot be read, report error and skip to next
- If issue cannot be updated, document in audit log and continue

## Audit Log (Required)

After the audit session completes (user says "stop" or no more issues found), the auditor MUST create an audit log:

**Location:** `./tmp/concern-audit-YYYYMMDD.md` (where YYYYMMDD is today's date)

**Format:**
```markdown
# Audit Log: Concern Separation

Date: YYYY-MM-DD
Auditor: concern-separation-auditor
Issue: #N (URL to issue)
Scope: GitHub Issue [SPEC] phase structure

## Summary
- Issues Found: N
- Issues Fixed: M
- Issues Skipped: K
- Remaining: L (issues identified but not yet resolved)

## Issues Processed

### Issue 1
Phase: <phase number>
Problem class: <CONCERN_MIXING|DEPENDENCY_REVERSAL|HIGH_RISK_GROUPING>
Concerns mixed: <deployment boundaries, risk levels, or blast radiuses>
Status: <fixed|skipped|pending>
Fix applied: <description of fix or "skipped per user request">
GitHub Comment: <URL to comment>

### Issue 2
...

## Unresolved Issues
<List any issues identified but not resolved during this session>

## Phase Structure Assessment
- Concern separation: <PASS|FAIL| NEEDS_IMPROVEMENT> (reason if fail)
- Dependency flow: <PASS|FAIL|NEEDS_IMPROVEMENT> (reason if fail)
- Grouping quality: <PASS|FAIL|N/A> (reason if fail)
- Risk distribution: <PASS|FAIL|NEEDS_IMPROVEMENT> (reason if fail)
```

**Requirements:**
- Log MUST be created after every audit session
- Log MUST include all issues identified (fixed, skipped, or pending)
- Log MUST be written to `./tmp/` directory
- Log file MUST NOT be committed to version control (tmp files are excluded)

## Fresh-Start Context Preservation (CRITICAL)

**After creating the audit log, ATTACH the content to the spec issue being audited.**

### Attachment Workflow

1. **After writing audit log to `./tmp/concern-audit-YYYYMMDD.md`:**
   - Read the full audit log content
   - Post as comment on the GitHub Issue specified by `--issue N`
   - Delete the temp file: `rm ./tmp/concern-audit-YYYYMMDD.md`

2. **Target Issue:**
   - ALWAYS attach to the issue specified by `--issue N` parameter
   - This is the spec being audited, so it needs the audit results

3. **Comment Format:**
   ```
   ## Summary
   - Issues Found: N
   - Issues Fixed: M
   - Issues Skipped: K
   
   <full audit log content>
   
   ---
   🤖 📝 Updated by <AgentName> (<ModelID>): Concern Audit
   ```

4. **Why This Matters:**
   - Temp files (`./tmp/`) are NOT preserved between sessions
   - Fresh-start agents have no memory of previous sessions
   - The spec issue needs the audit results for context in future sessions
   - Ensures phase structure quality is visible to anyone reviewing the spec

## Integration Points

This auditor skill coordinates with:

### spec-auditor (spec quality)
- **invoked after** spec-auditor checks spec quality
- **focuses on** phase structure rather than spec content
- **workflow**: Create spec → spec-auditor → concern-separation-auditor → ready for approval

### approval-gate (authorization)
- **invoked before** implementation approval
- **verifies** phase structure is properly separated
- **ensures** all new specs have passed concern separation check

### AI Agent Workflow (MANDATORY)

**When AI agent creates a new spec:**

```
1. Create GitHub Issue [SPEC] with phases and steps
2. Invoke spec-auditor --issue N (check spec quality, apply fixes)
3. Invoke concern-separation-auditor --issue N --auto-fix (check phase separation, apply fixes)
4. Add needs-approval label
5. Post "ready for review" comment
```

**Why this order:**
- spec-auditor ensures fresh-start context, required elements, structure
- concern-separation-auditor ensures deployment independence, low blast radius
- Both checks must pass before human review
- Auto-fix mode ensures fixes are applied without waiting for user intervention

## When to Invoke

### For AI Agents Creating New Specs (MANDATORY)

**AI agents MUST invoke this skill after creating any new [SPEC] issue:**

1. After writing the spec with phases and steps
2. BEFORE posting "ready for review" or adding `needs-approval` label
3. Use auto-fix mode: `/skill concern-separation-auditor --issue N --auto-fix`

**Integration with spec-auditor:**
```
Create spec issue #N →
Invoke spec-auditor --issue N (fix spec quality issues) →
Invoke concern-separation-auditor --issue N --auto-fix (fix phase separation) →
Add needs-approval label →
Post "ready for review" comment
```

### For Human Review (On-Demand)

- **During spec creation**: Prevent bad phase structures before approval
- **Before implementation approval**: Review phase structure for concern separation
- **Periodic review**: Check existing specs for deployment independence

### When NOT to Invoke

- Non-spec issues (bug reports, tasks without implementation phases)
- Specs with single phases (no concern mixing possible)
- Administrative specs (documentation-only, no code phases)

## Automatic Fixing Algorithm

### CRITICAL: Concern-Based Analysis, NOT Static Layers

**This algorithm analyzes CONCERNS (deployment independence, risk profile, blast radius), not static architectural layers.**

The DB→Repo→BL→UI ordering is ADVISORY - it describes a COMMON pattern, not a MANDATORY structure.

**DO NOT apply a static template. Real projects have different concern structures:**
- Stateless service: Config → API → Tests (no DB, no UI)
- CLI tool: Args → Core → Output (no persistence)
- Frontend-only: UI Components → State → Tests (no backend)
- Infrastructure: Setup (crosses all layers, ONE concern)

### Phase Analysis Algorithm (Concern-Based)

When auto-fix analyzes a phase, it asks concern-based questions for each step:

**Question 1: Deployment Independence**

Can this step be deployed independently?
- "Does it require other steps to be deployed first?"
- "Can it be rolled back without affecting other steps?"
- "Is it a self-contained unit of work?"

**Question 2: Risk Profile**

What's the rollback complexity if this step fails?
- HIGH: Schema changes, data migrations, infrastructure modifications
- MEDIUM: Repository methods, data access logic
- LOW-MEDIUM: API endpoints, services, business logic
- LOW: UI components, templates, styles

**Question 3: Dependency Direction**

What does this step depend on?
- "Which other steps MUST be complete before this step?"
- "Which steps depend on THIS step?"
- "Are there circular dependencies?"

**Question 4: Blast Radius**

What's the failure impact?
- "If this step fails, what else breaks?"
- "How many files/components are affected?"
- "Is there a clear rollback path?"

### Grouping by Concern Boundaries

**Step 1: Analyze Each Step**

For each step in the phase, answer the four questions and classify by concern:

| Concern | Characteristics | Example |
|---------|-----------------|---------|
| **Schema changes** | HIGH risk, affects persistence layer, complex rollback | "Add user tables" |
| **Data access** | MEDIUM risk, depends on schema, provides abstraction | "Create user repository" |
| **Business logic** | MEDIUM-LOW risk, depends on data access, provides API | "Implement user API" |
| **Presentation** | LOW risk, depends on business logic, UI-facing | "Build login component" |

**Step 2: Group by Concern Boundaries**

Group steps that share the same concern boundary:
- Steps with same deployment dependencies → same group
- Steps with similar risk profiles → same group
- Steps with bounded blast radius → same group
- Steps that must be deployed together → same group

**Step 3: Identify Separation Opportunities**

Look for phases with steps that have:
- DIFFERENT risk profiles (mixing HIGH and LOW)
- DIFFERENT deployment dependencies
- DIFFERENT blast radiuses
- CIRCULAR dependencies

**Step 4: Create New Phases Based on Concerns**

For each concern group identified, create a separate phase:

```
Phase N: <Concern Name> (Gated)

### Steps

1. ☐ <step from concern group>
2. ☐ <step from concern group>
...
```

Phase names should reflect the CONCERN, not a static layer:
- Good: "Database Schema" (describes the concern)
- Good: "User Data Access" (describes the concern)
- Bad: "Phase 1: Data Access Layer" (static template)

### Example Analysis (Concern-Based)

**Before (One Mixed-Concern Phase):**
```markdown
## Phase 1: Implementation (Gated)

### Steps

1. ☐ Add user tables to database schema
2. ☐ Create user repository class with CRUD methods
3. ☐ Implement user API endpoints (login, logout, register)
4. ☐ Build login UI component with form validation
```

**Analysis:**

| Step | Deployment Independence | Risk Profile | Dependencies | Blast Radius |
|------|------------------------|--------------|--------------|--------------|
| Add user tables | HIGH (requires migration) | HIGH (complex rollback) | None | Schema, migrations |
| Create repository | MEDIUM (depends on tables) | MEDIUM (requires schema) | Step 1 | Repository files |
| Implement API | MEDIUM-LOW | MEDIUM-LOW | Step 2 | API files |
| Build UI | HIGH (can develop independently) | LOW | Step 3 | UI files |

**Concern Boundaries Identified:**
- Group A (Schema): Step 1 - HIGH risk, deployment dependency for others
- Group B (Data Access): Step 2 - MEDIUM risk, depends on Group A
- Group C (API): Step 3 - MEDIUM-LOW risk, depends on Group B
- Group D (UI): Step 4 - LOW risk, depends on Group C

**Separation Rationale:**
- Schema changes (HIGH risk) should be separate from UI changes (LOW risk)
- Each group has bounded blast radius
- Clear dependency chain: A → B → C → D

**After (Split by Concerns):**
```markdown
## Phase 1: User Schema (Gated)

### Steps

1. ☐ Add user tables to database schema
2. ☐ Create migration scripts

---

## Phase 2: User Data Access (Gated)

### Steps

1. ☐ Create user repository class with CRUD methods
2. ☐ Add repository unit tests

---

## Phase 3: User API (Gated)

### Steps

1. ☐ Implement user API endpoints (login, logout, register)
2. ☐ Add API integration tests

---

## Phase 4: User Interface (Gated)

### Steps

1. ☐ Build login UI component with form validation
2. ☐ Add component tests
```

### Critical: NOT a Static Template

**The DB→Repo→BL→UI ordering is advisory, NOT mandatory.**

Real projects may have:
- No database (stateless services) → skip DB phase
- Direct API without repository → merge Data Access and Business Logic
- Frontend-first development → start with UI phases
- Infrastructure phases that cross all layers → keep as single phase

**The algorithm MUST:**
1. Analyze the ACTUAL concerns in each step
2. Group by ACTUAL dependencies and risks
3. Create phases based on ACTUAL deployment boundaries
4. NOT apply a rigid DB→Repo→BL→UI template

### Fix Decision Tree (Concern-Based)

```
For each phase:
  Analyze concerns for each step:
    - Deployment independence (HIGH/MEDIUM/LOW)
    - Risk profile (HIGH/MEDIUM/LOW)
    - Dependencies (list of step numbers)
    - Blast radius (list of affected components)

  Group steps by concern boundaries:
    - Steps with same deployment profile → same group
    - Steps with similar risk → same group
    - Steps with bounded blast radius → same group

  If all steps in phase share same concern:
    → No fix needed (PASS)
  Elif phase crosses concern boundaries AND steps can be cleanly separated:
    → Split into N phases (one per concern group) (APPLY FIX)
  Elif steps are tightly coupled across concerns:
    → Document coupling, flag as NEEDS_IMPROVEMENT
  Else:
    → Flag as UNKNOWN, escalate to human review
```

### Edge Cases (Concern-Based Handling)

| Scenario | Analysis | Action |
|----------|----------|--------|
| Infrastructure/setup phase | Crosses all layers by design | Keep as single phase (setup is ONE concern) |
| Testing phase | Validates all layers | Keep as single phase (testing is ONE concern) |
| Refactoring phase | Analyze each step's concern | Split by concern, not by "refactoring" |
| Configuration changes | LOW risk, high deployment independence | Single phase if bounded blast radius |
| Single-step phase | Already atomic | No split needed |
| Phase with <3 steps | Too small to split concerningly | Keep as single phase (over-splitting risk) |

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs
- Edits limited to spec content via GitHub Issue updates
- No changes to project source code, scripts, notebooks, or non-spec files
- No new specs, expansions, or "improvements" beyond what the fix requires
- Must use GitHub MCP tools for all issue operations

## Example Sessions

### Interactive Mode Session

```
User: /skill concern-separation-auditor --issue 483

AI: OpenCode ollama-cloud/glm-5 🤖 Auditing Issue #483 for concern separation...

Phase: Phase 1
Problem class: CONCERN_MIXING
Concerns mixed: Schema changes (HIGH risk) + Data Access (MEDIUM risk) + Business Logic (MEDIUM-LOW risk) + UI (LOW risk) - mixing different deployment boundaries
Explanation: Combining HIGH risk schema changes with LOW risk UI changes creates complex deployment and rollback scenarios. Each concern should be isolated.
Proposed refactor: Split into phases by concern: Schema (HIGH risk) → Data Access (MEDIUM risk) → API (MEDIUM-LOW risk) → UI (LOW risk).
Verification signal: no change required — awaiting user decision

[User responds: fix]

AI: Applying fix...

AI: OpenCode ollama-cloud/glm-5 📝 Concern Separation Update: Split Phase 1

- Changed: Split Phase 1 into 4 phases based on concern analysis (schema, data access, API, UI)
- Reason: Mixed concerns create high blast radius and deployment risk
- Separation Improvement: Each phase has bounded blast radius and clear deployment boundaries

GitHub Comment: https://github.com/NewsRx/newsrx-genai-python/issues/483#issuecomment-xxxxx

Moving to next issue...

Phase: Phase 2
Problem class: DEPENDENCY_REVERSAL
...

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Auto-fix Mode Session

```
User: /skill concern-separation-auditor --issue 483 --auto-fix

AI: OpenCode ollama-cloud/glm-5 🤖 Auditing Issue #483 with auto-fix...

Analyzing concerns for each phase...

Phase 1 Analysis:
  Step 1: Add user tables → Risk: HIGH (schema), Blast radius: migrations, Dependencies: None
  Step 2: Create repository → Risk: MEDIUM, Blast radius: repo files, Dependencies: Step 1
  Step 3: Implement API → Risk: MEDIUM-LOW, Blast radius: API files, Dependencies: Step 2
  Step 4: Build UI → Risk: LOW, Blast radius: UI files, Dependencies: Step 3
  
Concern boundaries detected:
  - Schema changes (HIGH risk) should be separate from UI (LOW risk)
  - Clear deployment dependencies: Schema → Repo → API → UI
  - Each group has bounded blast radius

Applying fixes...

✓ Phase 1 → Phase 1: User Schema (concern: HIGH risk schema changes)
✓ Phase 1 → Phase 2: User Data Access (concern: MEDIUM risk data access)
✓ Phase 1 → Phase 3: User API (concern: MEDIUM-LOW risk business logic)
✓ Phase 1 → Phase 4: User Interface (concern: LOW risk presentation)
✓ Renumbered subsequent phases
✓ Preserved phase groupings

AI: OpenCode ollama-cloud/glm-5 📝 Concern Separation Auto-Fix: #483

## Changes Applied

- Split Phase 1 into 4 phases based on concern analysis:
  - Phase 1: User Schema (HIGH risk, deployment dependency for others)
  - Phase 2: User Data Access (MEDIUM risk, depends on Phase 1)
  - Phase 3: User API (MEDIUM-LOW risk, depends on Phase 2)
  - Phase 4: User Interface (LOW risk, depends on Phase 3)
- Renumbered subsequent phases
- Updated dependency chain documentation

## Separation Improvement

- Blast radius reduced: Each phase has bounded blast radius
- Deployment independence: Schema changes isolated from UI changes
- Risk isolation: HIGH risk separated from LOW risk
- Rollback complexity: Each phase has clear rollback path

GitHub Comment: https://github.com/NewsRx/newsrx-genai-python/issues/483#issuecomment-xxxxx

Audit log attached to issue.

---
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Concern Separation Auto-Fix

✅ Auto-fix complete. Spec is now ready for review.
```

**Note:** The algorithm analyzed CONCERNS (deployment independence, risk profile, blast radius), not static layers. Real projects may skip phases (no database) or merge concerns (direct API without repository) based on ACTUAL dependencies.