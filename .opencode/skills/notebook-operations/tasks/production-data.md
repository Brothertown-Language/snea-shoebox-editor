# Task: production-data

## Purpose

Execution restrictions and absolute production data prohibition for notebook cell execution.

## ABSOLUTE PROHIBITION

**THE AI AGENT IS NEVER PERMITTED TO RUN CODE AGAINST PRODUCTION DATA OR DATABASES.**

## FORBIDDEN Execution Methods (Production Data)

| Method | Forbidden For |
|--------|---------------|
| `the-notebook-mcp_notebook_execute_cell` | ALL production notebooks |
| `pycharm_runNotebookCell` | ALL production notebooks |
| ANY execution method | Production notebooks |

## What Counts as Production Data

- **ALL notebooks in `pubmed_data_3/`** — connects to PubMed API and production databases
- **ANY notebook that imports from `commons/`** — likely uses production database connections
- **ANY notebook with `send_html_email`, `SMTP`, or email functionality** — sends real emails
- **ANY notebook with API calls** (`requests`, `Entrez`, `PubMedClient`) — production services
- **When in doubt, ASSUME production data**

## Permissible Verification Methods (Read-Only)

| Method | When Allowed |
|--------|--------------|
| `the-notebook-mcp_notebook_read` | ✅ ANYTIME — read-only |
| `the-notebook-mcp_notebook_read_cell` | ✅ ANYTIME — read-only |
| `the-notebook-mcp_notebook_search` | ✅ ANYTIME — read-only |
| `the-notebook-mcp_notebook_get_info` | ✅ ANYTIME — read-only |
| `the-notebook-mcp_notebook_get_outline` | ✅ ANYTIME — read-only |
| Create `./tmp/test_*.py` with mock data | ✅ ANYTIME — isolated testing |

## Authorization Requirements

- **A plan item "Re-run the notebook" does NOT authorize execution.**
- **Authorization for execution requires EXPLICIT USER INSTRUCTION in the current chat session.**
- **Each execution requires separate explicit authorization — previous authorizations do not carry over.**
- **When in doubt, DO NOT RUN IT.**

## Violation Recovery

If you accidentally execute a production notebook:

1. STOP immediately
2. Document the violation in a comment on the associated issue
3. Notify the user of what was executed
4. Wait for user guidance before proceeding