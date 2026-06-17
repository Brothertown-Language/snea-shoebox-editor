---
issue_number: 1323
created_at: "2026-06-17T00:00:00Z"
synced_from: "https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1323"
---

# [BUG] records.py has 12 pre-existing ruff lint errors

During implementation of #1321, `uvx ruff check src/frontend/pages/records.py` revealed 12 lint errors that pre-existed before any changes:

| Rule | Count | Example |
|------|-------|---------|
| F841 | 2 | `logger` and `search_query` assigned but never used |
| E741 | 4 | Ambiguous variable name `l` in list comprehensions |
| E501 | 4 | Line too long (>120 chars) |
| C401 | 2 | Unnecessary generator (rewrite as set comprehension) |
| C414 | 1 | Unnecessary `list()` call within `sorted()` |

**File:** `src/frontend/pages/records.py`
**Impact:** Technical debt — no runtime impact, but violates code standards and IDE navigation
**Risk:** Low — purely cleanup

🤖 Co-authored with AI: OpenCode (ollama-cloud/kimi-k2.6)
