---
name: code-size-enforcement
description: Enforce size limits on functions, notebook cells, and files. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.
license: MIT
compatibility: opencode
---

# Skill: code-size-enforcement

Enforce size limits on functions, notebook cells, and files. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.

## Available Tasks

| Task | Description | Lines |
|------|-------------|-------|
| `--task overview` | Size limits, detection methods, grandfather policy | ~200 |

## Quick Start

Invoke the overview task for complete enforcement rules:

```
/skill code-size-enforcement --task overview
```

## Role

Code Size Enforcer ensuring code artifacts stay within size limits for maintainability and readability.

## Operating Protocol

1. **Automatically Applied** - This skill is referenced whenever code is written or modified
2. **Check Size Limits Before Merge** - Verify limits when code changes are prepared for commit/PR
3. **Use Permitted Detection Tools** - Use documented measurement methods
4. **Grandfather Existing Files** - Files before this skill are NOT flagged
5. **Enforce on New/Modified Files** - Created/modified after skill introduction must comply

---

🤖 Co-authored with AI: OpenCode Desktop (ollama-cloud/glm-5)