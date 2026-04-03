---
name: sync-guidelines
description: Intelligently synchronize guidelines, skills, and tools between repositories through GitHub issues. Classifies files by semantic analysis and creates sync issues for human review.
license: MIT
compatibility: opencode
---

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

🤖 Co-authored with AI: OpenCode Desktop (ollama-cloud/glm-5)