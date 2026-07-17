# Implementation Plan — [#1359](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1359) — Document Local PostgreSQL Setup

- **Goal:** Create a comprehensive lesson-learned document covering local PostgreSQL setup, sync, and query patterns, then update the catalog index and AGENTS.md to reference it.
- **Architecture:** Three file modifications — one new lesson-learned markdown file (`docs/lessons-learned/2026-07-16-local-postgresql-setup.md`), one update to the catalog index (`docs/lessons-learned/index.md`), one update to AGENTS.md Research Catalog section.
- **Files:** `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` (new), `docs/lessons-learned/index.md` (edit), `AGENTS.md` (edit)
- **Dispatch:** `git-workflow` → `writing-plans` (this plan) → `git-workflow-commit` → `finishing-a-development-branch` → `git-workflow-pr`

## Blast Radius

| File | Change Type | Impact |
|------|-------------|--------|
| `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` | Create | New documentation — no existing consumers |
| `docs/lessons-learned/index.md` | Edit | Add one row to catalog table — no structural change |
| `AGENTS.md` | Edit | Add one line to Research Catalog table — no structural change |

## Concern Map Reference

| Concern | Phase |
|---------|-------|
| Author and persist the new lesson-learned document | Phase 1 |
| Register the new document in both navigation indexes | Phase 1 |

> **⚠️ COMPLIANCE REQUIREMENT:** This plan is an AI-agent-facing artifact. Every step must be executed as written. No step may be skipped, combined, reordered, or deemed "unnecessary" by the executing agent. If a step references a skill or tool call, that call must be made. If a verification step expects output, that output must be produced. The executing agent is not permitted to judge whether a step is needed — only whether it has been completed correctly. If a step cannot be executed as written, the agent must halt and report the discrepancy before proceeding.

> **⚠️ ONE-STEP-AT-A-TIME PROTOCOL:** Execute exactly ONE step per response. After completing a step, report the result and wait for acknowledgment before proceeding to the next step. Do not batch, pipeline, or parallelize steps. Each step is an atomic unit.

### Step Status

- `- [ ]` — Not started
- `- [/]` — In progress
- `- [x]` — Complete

## Phase Table

| Phase | Name | SCs | Dependencies | Steps |
|-------|------|-----|--------------|-------|
| 1 | Create lesson-learned doc + update indexes | SC-1, SC-2, SC-3, SC-4 | None | 1–9 |

## Phase 1 — Create lesson-learned doc + update indexes

**Concern:** Author and persist the new lesson-learned document and register it in both navigation indexes.

**Files:** `docs/lessons-learned/2026-07-16-local-postgresql-setup.md`, `docs/lessons-learned/index.md`, `AGENTS.md`

**SCs:** SC-1, SC-2, SC-3, SC-4

**Dependencies:** None

**Entry Conditions:** Feature branch `feature/1359-document-local-postgresql-setup` exists and is current.

**Exit Conditions:**
- New lesson-learned file exists at `docs/lessons-learned/2026-07-16-local-postgresql-setup.md`
- File covers pgserver location, sync mechanism, start/stop, and query patterns
- `docs/lessons-learned/index.md` has new entry row
- `AGENTS.md` Research Catalog has new reference row

### Step-by-step

- [ ] 1. (**inline**) **Coherence gate.** Verify the spec is internally consistent against the codebase: confirm all referenced files (`scripts/sync_prod_to_local.py`, `src/database/connection.py`, `AGENTS.md`, `docs/lessons-learned/2026-06-14-pg-catalog-schema-replication.md`) exist on disk and that the lesson filename date matches today. **→ SC-1, SC-2, SC-3, SC-4**

- [ ] 2. (**inline**) **Pre-RED baseline.** Run `git status` and `git diff --stat` to confirm clean working tree on the feature branch. Log state.

- [ ] 3. (**sub-agent**) **RED — Write lesson-learned document.** Create `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` covering:
  - Local PostgreSQL runs via pgserver in `tmp/local_db/`
  - Synced from production via `scripts/sync_prod_to_local.py` (cross-ref the existing schema-replication lesson)
  - Used for development and regression testing
  - Connection: `postgresql://postgres:@localhost:5432/postgres`
  - Query patterns using SQLAlchemy and `get_session()`
  - Example: searching for `\ph` in `mdf_data` column (430 entries found)
  - Start/stop patterns, common troubleshooting
  - Format follows existing lesson-learned convention (Date, Context, Findings, Recommendation, Files Referenced sections)
  **→ SC-1, SC-2**

- [ ] 4. (**sub-agent**) **GREEN — Verify document exists.** Run `ls docs/lessons-learned/2026-07-16-local-postgresql-setup.md` and confirm non-empty. **→ SC-1**

- [ ] 5. (**sub-agent**) **GREEN — Verify content coverage.** Grep for key section headers: `pgserver`, `sync`, `start`, `query`, `connection`. **→ SC-2**

- [ ] 6. (**sub-agent**) **RED — Update index.md.** Add new row to `docs/lessons-learned/index.md` catalog table. **→ SC-3**

- [ ] 7. (**sub-agent**) **GREEN — Verify index.md update.** Grep `docs/lessons-learned/index.md` for the new entry filename. **→ SC-3**

- [ ] 8. (**sub-agent**) **RED — Update AGENTS.md.** Add new row to AGENTS.md Research Catalog section referencing the new lesson-learned file. **→ SC-4**

- [ ] 9. (**sub-agent**) **GREEN — Verify AGENTS.md update.** Grep `AGENTS.md` for the new lesson-learned filename reference. **→ SC-4**

- [ ] 10. (**inline**) **Checkpoint commit (**inline**).** `git add docs/lessons-learned/2026-07-16-local-postgresql-setup.md docs/lessons-learned/index.md AGENTS.md && git commit -m "#1359 Document local PostgreSQL setup"` with Co-authored-by attribution.

- [ ] 11. (**inline**) **Push.** `git push -u origin feature/1359-document-local-postgresql-setup`

#### Phase 1 VbC

- [ ] 12. (**clean-room**) **VbC.** Verify all four SCs against live file state:
  - SC-1: `ls docs/lessons-learned/2026-07-16-local-postgresql-setup.md` → file exists
  - SC-2: `grep` for key sections → content covers pgserver, sync, start/stop, query patterns
  - SC-3: `grep` index.md for new entry → row present
  - SC-4: `grep` AGENTS.md for new reference → row present

**Concern transition:** Documentation authored and registered — plan complete. No further phases.

---

> **⚠️ COMPLIANCE REQUIREMENT:** This plan is an AI-agent-facing artifact. Every step must be executed as written. No step may be skipped, combined, reordered, or deemed "unnecessary" by the executing agent. If a step references a skill or tool call, that call must be made. If a verification step expects output, that output must be produced. The executing agent is not permitted to judge whether a step is needed — only whether it has been completed correctly. If a step cannot be executed as written, the agent must halt and report the discrepancy before proceeding.

> **⚠️ SELF-REMEDIATION PROTOCOL:** When verification fails, the agent MUST remediate autonomously before escalating. Fix the issue and re-run the verification step. Only escalate after 3+ remediation attempts have failed. All failures are agent-owned — "pre-existing failure" is NOT a valid rationalization to skip or soft-pass a verification gate.

### Exit Criteria

- [ ] C1. `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` exists and is non-empty
- [ ] C2. File covers pgserver location, sync mechanism, start/stop, and query patterns
- [ ] C3. `docs/lessons-learned/index.md` contains new row referencing the new lesson
- [ ] C4. `AGENTS.md` Research Catalog contains new row referencing the new lesson
- [ ] C5. All changes committed and pushed to feature branch
