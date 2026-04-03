---
name: concern-separation-auditor
description: Analyzes spec phase structure for concern separation quality - deployment independence, risk profile, blast radius. Auto-fixes phases by analyzing actual concerns. Posts findings to GitHub.
license: MIT
compatibility: opencode
---

# Concern Separation Auditor

Analyzes spec phase structures to identify concern quality issues and apply smart fixes. Posts findings to GitHub comments.

## When to Use

- Creating new spec issues (MANDATORY - runs first)
- Reviewing existing specs for phase quality
- Auditing multi-phase implementations

## Available Tasks

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

## Why Concern Separation Matters

**Beyond deployment and rollback, concern separation prevents:**

1. **Feature Creep**: Clear boundaries prevent "while we're here" additions
2. **Vibe Coding**: Without boundaries, implementation drifts from spec
3. **Roadmap Driving**: Phase boundaries shouldn't follow roadmap priorities

## Mandatory Audit Chain (All Skills Run)

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, BOILERPLATE-TITLE, concern analysis |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality |

**CRITICAL: If you run ONE auditor, you MUST run BOTH in order.**

## Mandatory Invocation for AI Agents

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:

1. Create the spec issue with phases and steps
1. **Invoke `/skill concern-separation-auditor --issue N`** (auto-fix phase structure)
1. **Invoke `/skill spec-auditor --issue N`** (check content quality)
1. Fixes applied automatically by both auditors
1. Add `needs-approval` label
1. Post "ready for review" comment

**Skipping this auditor is a CRITICAL GUIDELINE VIOLATION.**

## Quick Start

Use `/skill concern-separation-auditor --task overview` for complete workflow.