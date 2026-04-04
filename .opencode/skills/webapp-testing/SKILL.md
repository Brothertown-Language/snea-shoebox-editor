---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
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
- This skill EXEMPT from codebase verification (web app testing)
- This skill EXEMPT from issue conflict check (testing only)

# Skill: webapp-testing

Web application testing toolkit using Playwright for local app verification, debugging, UI behavior validation, screenshots, and browser logs.

## Available Tasks

| Task | Description | Lines |
|------|-------------|-------|
| `--task overview` | Testing patterns, decision tree, with_server.py usage | ~130 |

## Quick Start

Invoke the overview task for comprehensive testing guidance:

```
/skill webapp-testing --task overview
```

---

🤖 Co-authored with AI: <AgentName> (<ModelID>)