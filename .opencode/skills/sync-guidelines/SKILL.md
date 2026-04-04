---
name: sync-guidelines
description: Intelligently synchronize guidelines, skills, and tools between repositories through GitHub issues. Classifies files by semantic analysis and creates sync issues for human review.
license: MIT
compatibility: opencode
---

## Operating Protocol

### ⚠️ VERIFICATION STEPS (MANDATORY FIRST)

**Before ANY skill operation, verify:**

1. **Session Init Check:**
   - Has `ai_bin/session_init.py` run?
   - Store: `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL`
   - If NOT run → STOP, run session init FIRST

2. **Codebase Verification:**
   - Is codebase state current?
   - Run: `srclight_codebase_map` or `srclight_index_status`
   - Verify: No stale assumptions from previous sessions

3. **Issue Conflict Check:**
   - Query open `[SPEC]` issues for conflicts
   - Check for superseding/invalidating issues
   - If conflict found → HALT, report conflict

**Exemption Conditions:**
- This skill REQUIRES codebase verification (syncs files between repositories)
- This skill REQUIRES issue conflict check (creates GitHub issues)

# Skill: sync-guidelines

Intelligently synchronize guidelines, skills, and tools between repositories through GitHub issues. Classifies files by semantic analysis and creates sync issues for human review.

## Available Tasks

| Task | Description | Lines |
|------|-------------|-------|
| `--task overview` | Sync workflow, classification, and issue creation | ~120 |

## Quick Start

Invoke the overview task for synchronization workflow:

```
/skill sync-guidelines --task overview
```

## When to Invoke

- User runs `/skill sync-guidelines`
- Automated workflow detects changes in `.opencode/guidelines/`, `.opencode/skills/`, or `ai_bin/`

---

🤖 Co-authored with AI: <AgentName> (<ModelID>)