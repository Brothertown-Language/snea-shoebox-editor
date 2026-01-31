<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task Tracking

Current focus area as of 2026-01-31:
- **Task:** Embedding Model Selection & Roadmap Refinement
- **Description:** Finalize the selection of `@cf/baai/bge-m3` as the embedding model based on its multilingual capabilities and sparse retrieval support for Algonquian-English code-switching.
- **Status:** COMPLETE
- **Completed Requirements:**
    - Analyzed `docs/development/roadmap.md` and `docs/database/SCHEMA.md`.
    - Identified and resolved ambiguities in Concurrency, Search, Audit, and Environment workflows.
    - Confirmed `@cf/baai/bge-m3` as the model for better search quality across Indigenous languages.
    - Updated `roadmap.md` with:
        - Strict Optimistic Locking (no explicit locks).
        - Detailed Conflict Resolution Workflow.
        - Hybrid Search with combined weighted scores.
        - **Embedding Model Selection:** `@cf/baai/bge-m3`.
        - Inline/Background vector recalculation strategy.
        - Full snapshot edit history.
        - Permission details for 'Approved' records.
    - Updated `SCHEMA.md` to reference `@cf/baai/bge-m3` and 1024-dimension requirement.
- **In Progress:**
    - None
