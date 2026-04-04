---
name: code-size-enforcement
description: Enforce size limits on functions, notebook cells, and files using word counts. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.
license: MIT
compatibility: opencode
---

# Skill: code-size-enforcement

Enforce size limits on functions, notebook cells, and files using word counts as the primary measure of complexity. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.

**Why Word Counts:** Word counts provide a more accurate measure of LLM context usage and cognitive load than line counts. A dense short function may have more complexity than a verbose long one.

## Available Tasks

| Task | Description | Words |
|------|-------------|-------|
| `--task overview` | Size limits, detection methods, grandfather policy, word count migration | ~350 |

## Quick Start

Invoke the overview task for complete enforcement rules:

```
/skill code-size-enforcement --task overview
```

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
- This skill EXEMPT from codebase verification (read-only code analysis)
- This skill EXEMPT from issue conflict check (pattern enforcement)

## Role

Code Size Enforcer ensuring code artifacts stay within size limits for maintainability and readability.

## Operating Protocol

1. **Automatically Applied** - This skill is referenced whenever code is written or modified
2. **Check Size Limits Before Merge** - Verify limits when code changes are prepared for commit/PR
3. **Use Permitted Detection Tools** - Use documented measurement methods
4. **Grandfather Existing Files** - Files before this skill are NOT flagged
5. **Enforce on New/Modified Files** - Created/modified after skill introduction must comply

---

🤖 Co-authored with AI: <AgentName> (<ModelID>)