---
name: code-size-enforcement
description: Enforce size limits on functions, notebook cells, and files using word counts. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.
license: MIT
compatibility: opencode
---

# Skill: code-size-enforcement

Enforce size limits on functions, notebook cells, and files using word counts as the primary measure of complexity. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.

**Why Word Counts:** Word counts provide a more accurate measure of LLM context usage and cognitive load than line counts. A dense short function may have more complexity than a verbose long one.

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Writing or modifying code | `/skill code-size-enforcement --task overview` | Check size limits |
| Before merge/PR | `/skill code-size-enforcement --task overview` | Verify compliance |
| Size limit violations | `/skill code-size-enforcement --task overview` | Get remediation guidance |

## This Skill's Tasks

| Task | Description | Words |
|------|-------------|-------|
| `--task overview` | Size limits, detection methods, grandfather policy, word count migration | ~350 |

## Quick Start

Invoke the overview task for complete enforcement rules:

```
/skill code-size-enforcement --task overview
```

## Role

Code Size Enforcer ensuring code artifacts stay within size limits for maintainability and readability.

## Workflow

**Automatic by default — no manual invocation needed.**

1. Automatically enforced when code is written or modified
2. Check limits before merge/PR
3. Use permitted detection tools
4. Grandfather existing files, enforce on new/modified

---

🤖 Co-authored with AI: <AgentName> (<ModelID>)