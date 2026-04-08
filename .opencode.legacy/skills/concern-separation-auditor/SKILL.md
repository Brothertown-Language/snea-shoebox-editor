---
name: concern-separation-auditor
description: Analyzes spec phase structure for concern separation quality - deployment independence, risk profile, blast radius. Auto-fixes phases by analyzing actual concerns. Posts findings to GitHub.
license: MIT
compatibility: opencode
---

# Concern Separation Auditor

Analyzes spec phase structures to identify concern quality issues and apply smart fixes. Posts findings to GitHub comments.

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Creating new spec issues | `/skill concern-separation-auditor --issue N` | First auditor in mandatory chain |
| Reviewing spec quality | `/skill concern-separation-auditor --issue N` | Phase structure analysis |
| Auditing multi-phase implementations | `/skill concern-separation-auditor --issue N` | Concern separation check |

## This Skill's Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete audit workflow with auto-fix |

## What Gets Auto-Fixed

| Issue Type | Auto-Fix? | Why |
|------------|-----------|-----|
| BOILERPLATE-TITLE | YES | 100% objective - generic vs concern names |
| CONCERN_MIXING | YES | Smart split based on concern analysis |
| DEPENDENCY_REVERSAL | YES | Reorder to fix dependencies |
| HIGH_RISK_GROUPING | YES | Separate high-risk from low-risk |

## ⚠️ MANDATORY: Sub-Issue Discovery and Auditing

**Before auditing the parent, discover and audit ALL sub-issues.**

### Sub-Issue Discovery Workflow

```
1. Query: github_issue_read(method="get_sub_issues", issue_number=N)
2. If empty → audit parent only (current behavior)
3. If sub-issues exist:
   a. Audit parent first (phase structure, BOILERPLATE-TITLE)
   b. For each sub-issue: audit phase structure
   c. Check cross-issue consistency (parent-sub-issue consistency)
   d. Aggregate all findings in single report
```

### Sub-Issue Phase Structure Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Phase naming | `BOILERPLATE-TITLE` | Sub-issue phase names like "Implementation" |
| Concern separation | `CONCERN_MIXING` | Sub-issue phases mix concerns |
| Parent-sub-issue consistency | `INCONSISTENT-HIERARCHY` | Sub-issue contradicts parent objective |
| Sub-issue overlap | `OVERLAPPING-SUB-ISSUES` | Multiple sub-issues claim same work |

## AUTO-FIX BY DEFAULT (No Asking Permission)

**Auditors AUTO-FIX identified issues by default.**

- Apply fixes immediately without waiting for user confirmation
- Post GitHub Issue comment documenting each fix
- Continue to next issue
- Only HALT if user explicitly says "don't fix" or "just report"

## ⚠️ MANDATORY: Sub-Issue Discovery and Auditing

**Before auditing the parent, discover and audit ALL sub-issues.**

### Sub-Issue Discovery Workflow

```
1. Query: github_issue_read(method="get_sub_issues", issue_number=N)
2. If empty → audit parent only (current behavior)
3. If sub-issues exist:
   a. Audit parent first (phase structure, BOILERPLATE-TITLE)
   b. For each sub-issue: audit phase structure
   c. Check cross-issue consistency (parent-sub-issue consistency)
   d. Aggregate all findings in single report
```

### Sub-Issue Phase Structure Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Phase naming | `BOILERPLATE-TITLE` | Sub-issue phase names like "Implementation" |
| Concern separation | `CONCERN_MIXING` | Sub-issue phases mix concerns |
| Parent-sub-issue consistency | `INCONSISTENT-HIERARCHY` | Sub-issue contradicts parent objective |
| Sub-issue overlap | `OVERLAPPING-SUB-ISSUES` | Multiple sub-issues claim same work |

## Why Concern Separation Matters

**Beyond deployment and rollback, concern separation prevents:**

1. **Feature Creep**: Clear boundaries prevent "while we're here" additions
2. **Vibe Coding**: Without boundaries, implementation drifts from spec
3. **Roadmap Driving**: Phase boundaries shouldn't follow roadmap priorities

## Risk Level and Blast Radius Validation

**Each phase MUST declare its risk profile:**

### Required Phase Structure

```markdown
## Phase N: [Concern Name] (Risk: [LOW|MEDIUM|HIGH], Blast Radius: [SMALL|MEDIUM|LARGE])

**Interdependencies**: [NONE|Phase M (what it requires)]

**Why this order**: [Explanation of phase ordering]
```

### Risk Level Definitions

| Risk | Characteristics | Examples |
|------|-----------------|----------|
| **LOW** | Read-only, additive, localized, easily reversible | Adding a new query, adding a test file, documentation |
| **MEDIUM** | Modifies existing code, affects one module, moderate rollback complexity | Refactoring a service, adding API endpoint, modifying schema |
| **HIGH** | Breaking changes, affects multiple modules, hard to rollback, production-critical | Database migration, authentication rewrite, API versioning, deployment changes |

### Blast Radius Definitions

| Blast Radius | Scope | Rollback Difficulty |
|--------------|-------|---------------------|
| **SMALL** | Single file/module, no dependencies | Easy (simple revert) |
| **MEDIUM** | Multiple files, internal dependencies | Moderate (may need data migration) |
| **LARGE** | Cross-module, external dependencies, production systems | Difficult (may need data rollback, coordination) |

### Validation Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| Risk level missing | `MISSING-ELEMENT` | Phase lacks `(Risk: ...)` declaration |
| Blast radius missing | `MISSING-ELEMENT` | Phase lacks `(Blast Radius: ...)` declaration |
| Invalid format | `STRUCTURE-VIOLATION` | Risk/blast radius not in expected format (e.g., missing parentheses) |

**Risk levels and blast radius are DECLARATIVE - the author declares what they are, the auditor does NOT enforce what they should be.**

The auditor checks that:
- Each phase HAS a risk level and blast radius declaration
- The format is correct (parentheses, proper syntax)

The auditor does NOT check that:
- Risk level matches phase characteristics (author's judgment)
- Blast radius matches scope (author's judgment)
- Specific phases should have specific risk levels (no prescriptive structure)

## Mandatory Audit Chain (All Skills Run)

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, BOILERPLATE-TITLE, concern analysis |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality |
| **3rd** | `dev-architect --task review-spec` | Architectural correctness, compliance, interdependencies |

**CRITICAL: If you run ONE auditor, you MUST run ALL THREE in order.**

## Mandatory Invocation for AI Agents

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:

1. Create the spec issue with phases and steps
1. **Invoke `/skill concern-separation-auditor --issue N`** (auto-fix phase structure)
1. **Invoke `/skill spec-auditor --issue N`** (check content quality)
1. **Invoke `/skill dev-architect --task review-spec`** (review architectural correctness)
1. Fixes applied automatically by all three auditors
1. Add `needs-approval` label
1. Post "ready for review" comment

**Skipping this auditor is a CRITICAL GUIDELINE VIOLATION.**

## Two-Channel Comment Rules

**CRITICAL: Distinguish between chat (developer coordination) and GitHub Issues (revision history).**

### Chat (Developer Coordination)

| When to Post | Content |
|--------------|---------|
| ALWAYS (success OR fixes) | Executive summary: pass/fail status, fixes applied |

**Chat Executive Summary Format:**

```
**Audit Complete:** [audit type] [passed/failed]

**Issues Found:** N
**Issues Fixed:** M (if any)
**Status:** [No concerns detected | N issues fixed]

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### GitHub Issues (Revision History)

| When to Post | Content |
|--------------|---------|
| ONLY on revision | WHY revision needed, WHAT changed - for future developer context |

**GitHub Issue Revision Comment Format:**

```
Fixed [issue description]

**Why:** [reason for revision]
**What:** [what changed]

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Examples

**Audit passed (no issues):**

- Chat: Post executive summary with "passed" status
- GitHub Issues: NO COMMENT (no revision made)

**Audit found issues and fixed them:**

- Chat: Post executive summary with issues found and fixes applied
- GitHub Issues: Post revision comment explaining WHY and WHAT changed

**Audit found catastrophic issue (HALT):**

- Chat: Post summary explaining blocker
- GitHub Issues: NO COMMENT (issue is blocking, not fixed)

### ⚠️ CRITICAL: Never Post Full Audit Reports to GitHub Issues

**FORBIDDEN:**

- Posting checklist-style pass/fail results as GitHub comments
- Posting complete audit findings when no revision was made
- Posting audit logs/scores without revision context

**CORRECT:**

- Chat: Always post executive summary (pass or fix)
- GitHub Issues: Only post when revision made (WHY/WHAT context)

## Quick Start

Use `/skill concern-separation-auditor --task overview` for complete workflow.