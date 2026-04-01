# Jupyter Notebook Rules — ZERO TOLERANCE

## 🔴 MANDATORY: EXCLUSIVE USE OF the-notebook-mcp TOOLS

**This is a ZERO TOLERANCE rule. Violations cause notebook corruption, data integrity issues, and broken functionality.**

> **See `notebook-operations` skill for complete tool tables, forbidden operations, execution restrictions, and cell labeling requirements.**

### Essential Rules

1. **Use ONLY `the-notebook-mcp_notebook_*` tools** for ALL notebook operations
2. **NO fallback** — if MCP unavailable, REFUSE the task
3. **NO production execution** — never run notebooks against production data
4. **Label cells** — add descriptive labels to cell metadata for maintainability

### 🚫 FORBIDDEN — NO EXCEPTIONS

| Forbidden | Reason |
|-----------|--------|
| `read`/`write`/`edit` on `.ipynb` | CORRUPTS NOTEBOOKS |
| `json.load`/`json.dump` on `.ipynb` | CORRUPTS NOTEBOOKS |
| `nbformat` direct access | BYPASSES MCP |
| `sed`/`cat`/`grep` on `.ipynb` | FORBIDDEN |
| Shell commands on `.ipynb` | FORBIDDEN |

## Code Standards for Notebooks

> **See `code-size-enforcement` skill for size limit enforcement rules.**

ALL code standards in `080-code-standards.md` apply to notebook cells. Key limits:
- Notebook cells must not exceed 50 lines
- Each cell should do ONE thing
- Functions defined in notebooks should perform ONE task

### 🔴 EXECUTION RESTRICTION

**Production notebook execution is ABSOLUTELY FORBIDDEN without EXPLICIT USER INSTRUCTION.**

- Production notebooks: `pubmed_data_3/`, imports from `commons/`, API calls, database connections
- Authorization: Required PER SESSION, PER EXECUTION — no carryover
- When in doubt: DO NOT RUN IT

**Full details in `notebook-operations` skill**