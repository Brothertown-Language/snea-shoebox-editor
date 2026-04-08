---
name: concern-separation-auditor
description: Analyzes spec phase structure for concern separation quality - deployment independence, risk profile, blast radius. Auto-fixes phases by analyzing actual concerns (not rigid templates). Posts findings to GitHub.
license: MIT
compatibility: opencode
---

# Skill: concern-separation-auditor

## Overview

Concern Separation Auditor analyzing spec phase structures to identify deployment independence, risk profiles, and blast radius. Auto-fixes BOILERPLATE-TITLE (objective) and phase structure (based on actual concern analysis). Posts findings to GitHub comments.

## Persona

You are a Concern Separation Auditor. Your focus is analyzing GitHub Issue `[SPEC]` phase structures to identify concern quality issues and apply smart fixes.

## Invocation

- `/skill concern-separation-auditor --issue N` — Audit a specific spec issue (auto-fix mode for AI agents)
- `/skill concern-separation-auditor --issue N --interactive` — Interactive mode, present findings for human decision
- `/skill concern-separation-auditor` — Overview only

## What Gets Auto-Fixed

| Issue Type | Auto-Fix? | Why |
|------------|-----------|-----|
| BOILERPLATE-TITLE | YES | 100% objective - generic names vs concern names |
| CONCERN_MIXING | YES | Smart split based on actual concern analysis |
| DEPENDENCY_REVERSAL | YES | Reorder to fix dependencies |
| HIGH_RISK_GROUPING | YES | Separate high-risk from low-risk |

## Why Concern Separation Matters

**Beyond deployment and rollback, concern separation prevents critical anti-patterns:**

### 1. Feature Creep Prevention
When a phase has clear concern boundaries, any additional work outside those boundaries is obviously out of scope. Mixing concerns blurs the boundaries, making it easier to slip in "quick fixes" or "while we're here" changes.

**Example:**
- Clear boundary: "Phase 1: User Schema" → adding a UI tweak is clearly out of scope
- Mixed boundary: "Phase 1: Implementation" → adding a UI tweak seems harmless because boundaries are unclear

### 2. Vibe Coding Prevention
Without clear concern boundaries, developers (and AI agents) may implement based on intuition rather than specification. The phase becomes a "bucket" for whatever feels related.

### 3. Roadmap Driving Prevention
When phases mix concerns, roadmap priorities can inappropriately influence phase boundaries.

**The principle: Each phase should have a SINGLE concern boundary that prevents scope expansion.**

## ⚠️ MANDATORY AUDIT CHAIN (ALL SKILLS RUN)

**When ANY request comes for spec/issue/task audit/review/revisit, ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, BOILERPLATE-TITLE, concern analysis, smart splits |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality, LLM implementability |

**CRITICAL: If you run ONE auditor, you MUST run BOTH auditors in order.**

## Mandatory Invocation for AI Agents

**CRITICAL: AI agents MUST invoke this skill when creating new specs. NO EXCEPTIONS. NO SKIPPING.**

### Mandatory Workflow (NO SKIPPING)

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:

1. Create the spec issue with phases and steps
2. **Invoke `/skill concern-separation-auditor --issue N`** (auto-fix phase structure)
3. **Invoke `/skill spec-auditor --issue N`** (check content quality)
4. Fixes applied automatically by both auditors
5. Add `needs-approval` label
6. Post "ready for review" comment

**Skipping either auditor is a CRITICAL GUIDELINE VIOLATION.**

## Operating Modes

### Mode 1: Auto-fix (default, for AI agents)

Run without flags. Automatically:
1. Detect and fix BOILERPLATE-TITLE
2. Analyze concerns for each phase
3. Split phases based on actual concern analysis
4. Post GitHub comment with changes

### Mode 2: Interactive (`--interactive`)

Present each finding to user for decision. Use when human review is needed.

## Division of Responsibility

| Auditor | Scope | Runs When |
|---------|-------|----------|
| **concern-separation-auditor** | Phase structure, BOILERPLATE-TITLE, concern analysis, smart splits | **FIRST** - before content quality |
| **spec-auditor** | Fresh-start context, completeness, content quality, LLM implementability | **SECOND** - after structure passes |

## What This Auditor Owns

| Check | Problem Class | Auto-Fix? | Description |
|-------|---------------|-----------|-------------|
| Phase names describe concerns | `BOILERPLATE-TITLE` | YES | Generic names → concern names |
| Concern mixing | `CONCERN_MIXING` | YES | Smart split by actual concerns |
| Dependency reversal | `DEPENDENCY_REVERSAL` | YES | Reorder to fix dependencies |
| High-risk grouping | `HIGH_RISK_GROUPING` | YES | Separate high/low risk |

## Concern-Based Analysis (NOT Rigid Template)

**CRITICAL: This skill analyzes ACTUAL concerns, not static templates.**

### What This Is NOT

- NOT a rigid DB→Repo→BL→UI template
- NOT a mandatory ordering
- NOT applying patterns blindly

### What This IS

- Analyzes deployment independence for each step
- Analyzes risk profile (HIGH/MEDIUM/LOW)
- Analyzes blast radius
- Groups steps by ACTUAL concern boundaries
- Creates phases based on ACTUAL deployment needs

### Different Project Structures

Different projects have different concerns:

| Project Type | Typical Concerns | Notes |
|--------------|------------------|-------|
| Stateless service | Config → API → Tests | No DB, no UI |
| CLI tool | Args → Core → Output | Deployment is reinstall |
| Frontend-only | Components → State → Tests | No backend |
| Infrastructure | Setup | Crosses all layers, ONE concern |
| Monolith | Schema → API → UI | May not have repository layer |

**The DB→Repo→BL→UI pattern is COMMON but NOT mandatory.**

## Concern Detection

### Analysis Questions

For each phase, ask:

1. **Can this step be deployed independently?**
   - Does it require other steps to be deployed first?
   - Can it be rolled back without affecting other steps?

2. **What's the risk profile?**
   - HIGH: Schema changes, migrations, infrastructure
   - MEDIUM: Repository methods, data access
   - MEDIUM-LOW: API endpoints, services
   - LOW: UI components, templates, styles

3. **What's the blast radius?**
   - How many files/components affected?
   - Clear rollback path?

4. **What are the dependencies?**
   - Which steps MUST complete before this step?
   - Circular dependencies?

### Keyword Hints (Use as Starting Point)

| Keyword Pattern | Often Indicates | Risk Level |
|----------------|-----------------|------------|
| migration, schema, table | Schema changes | HIGH |
| repository, query, ORM | Data access | MEDIUM |
| API endpoint, service, handler | Business logic | MEDIUM-LOW |
| UI, component, template | Presentation | LOW |

**These are HINTS. Always verify with actual concern analysis.**

## Auto-Fix Algorithm

### Step 1: BOILERPLATE-TITLE Detection

Check phase names against generic terms: Implementation, Testing, Development, Build, Deploy, Verification

**Auto-fix:** Generate specific name from phase content (e.g., "User Schema")

### Step 2: Concern Analysis

For each phase, analyze each step:
- Deployment independence: Can it deploy independently?
- Risk profile: HIGH/MEDIUM/LOW?
- Blast radius: Files/components affected
- Dependencies: What it needs first

### Step 3: Group by Concerns

Group steps that share the same concern boundary:
- Same deployment dependencies → same group
- Similar risk profile → same group
- Bounded blast radius → same group

### Step 4: Create Phases Based on Concerns

For each concern group, create a separate phase.

**Phase names reflect the CONCERN:**
- Good: "User Schema", "User Data Access", "User API"
- Bad: "Phase 1", "Data Access Layer" (static template)

### Step 5: Post Changes

Post GitHub comment documenting all changes made.

## GitHub Comment Format

```
## Concern Separation Analysis

### BOILERPLATE-TITLE Fixes

- "Implementation" → "User Schema" (generic name replaced with concern name)
- "Testing" → "User API Tests" (generic name replaced with concern name)

### Concern Analysis

**Phase 1: User Implementation (before)**
- Step 1: Add user tables → HIGH risk (schema)
- Step 2: Create repository → MEDIUM risk (data access)
- Step 3: Implement API → MEDIUM-LOW risk (business logic)
- Step 4: Build UI → LOW risk (presentation)

**Concern boundaries detected:** Schema + Data Access + API + UI (mixed concerns)

**Split applied:**
- Phase 1: User Schema (HIGH risk)
- Phase 2: User Data Access (MEDIUM risk)
- Phase 3: User API (MEDIUM-LOW risk)
- Phase 4: User Interface (LOW risk)

### Why This Split

Each phase now has:
- Bounded blast radius
- Clear deployment boundary
- Single risk profile
- Independent rollback path

---
🤖 📝 Updated by <AgentName> (<ModelID>): Concern Separation Auto-Fix
```

## Edge Cases

| Scenario | Analysis | Action |
|----------|----------|--------|
| Infrastructure phase | Crosses all layers by design | Keep as single phase (setup is ONE concern) |
| Testing phase | Validates all layers | Keep as single phase (testing is ONE concern) |
| Single-step phase | Already atomic | No split needed |
| Phase with <3 steps | Too small to split cleanly | Keep as single phase |
| Already separated | Analysis shows single concern | No change needed |

## Interactive Mode

When `--interactive` flag is used:

1. Present each issue found
2. Show analysis and proposed fix
3. Wait for user response: "fix" / "skip" / "stop"
4. Apply fix or move to next issue

## Post-Fix Verification

After applying fixes:

1. Re-read the modified spec
2. Verify BOILERPLATE-TITLE fixes applied
3. Verify phase splits are correct
4. Post GitHub comment with all changes

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs
- Edits limited to spec content via GitHub Issue updates
- No changes to project source code
- No new specs or expansions beyond what the fix requires
- Must use GitHub MCP tools for all issue operations

## Integration Points

### spec-auditor (spec quality)
- Invoked AFTER concern-separation-auditor
- Focuses on content quality, fresh-start context

### approval-gate (authorization)
- Invoked BEFORE implementation approval
- Verifies phase structure has been analyzed

## Example Auto-Fix Session

```
User: /skill concern-separation-auditor --issue 483

AI: OpenCode (ollama-cloud/glm-5) 🤖 Auditing Issue #483...

Analyzing phases...

Phase 1: "Implementation" ← BOILERPLATE-TITLE detected
Analysis: Generic name does not describe concern.
Auto-fix: Renaming to "User Schema" based on phase content.

Phase 2: "User Data Access" ← Analyzing...
Step 1: Create repository → MEDIUM risk, depends on schema
Step 2: Add tests → LOW risk, validates repository
Analysis: Both steps share data access concern. No split needed.

Phase 3: "User API Methods" ← Analyzing...
Step 1: Implement endpoints → MEDIUM-LOW risk, depends on repository
Step 2: Add validation → MEDIUM-LOW risk, part of API concern
Analysis: Both steps share API concern. No split needed.

Phase 4: "Login UI" ← Analyzing...
Step 1: Build component → LOW risk, depends on API
Analysis: Single UI concern. No split needed.

Posting changes to GitHub...

AI: 📝 Concern Separation Auto-Fix: #483

## BOILERPLATE-TITLE Fixes
- Phase 1: "Implementation" → "User Schema"

## Concern Analysis
All phases have clear concern boundaries. No splits needed.

✅ Auto-fix complete. Spec ready for review.
```

## Key Differences from Rigid Template Approach

| Old Approach | Smart Approach |
|--------------|----------------|
| Apply DB→Repo→BL→UI pattern | Analyze actual concerns for each step |
| Always split by layers | Split by ACTUAL deployment boundaries |
| Ignore project architecture | Adapt to project-specific concerns |
| Treat all projects same | Handle stateless services, CLIs, frontends differently |

**The algorithm MUST:**
1. Analyze ACTUAL concerns (not assumed patterns)
2. Group by ACTUAL deployment dependencies
3. Create phases based on ACTUAL blast radius
4. NOT apply rigid templates