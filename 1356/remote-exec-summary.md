> **Full spec and artifacts: [`.issues/1356/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1356)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1356/` — implementation plan, card catalogue, dependency contracts, research, designs, audit findings

## Problem

The `dev` branch has been merged into `main` (PR #1354) and is being retired. Documentation still references `dev` as a workflow target, creating confusion for developers who will target the wrong branch.

## Goals

- Delete two documents that describe the retired `feature → dev → main` workflow
- Remove the `dev` exception from agent guidelines
- Update the one remaining valid doc reference from `dev` → `main`
- Verify zero stale `dev` branch workflow references remain

## Non-Goals

- No changes to `.opencode/` directory (off-limits per policy)
- No changes to `src/` code files (documentation-only change)
- No changes to generic "dev" in prose ("development", "dev machine")
- The `dev` git branch itself is not deleted (preserved for history)

## Scope

- DELETE: `docs/git-workflow-migration-guide.md` (entire file)
- DELETE: `docs/streamlit-dev-workflow.md` (entire file)
- REMOVE: `AGENTS.md` line 52 (dev exception for PRs)
- UPDATE: `docs/security/credential-leakage-remediation.md` line 84 (`origin dev` → `origin main`)

## Approach

Delete the two workflow docs that describe a retired workflow. Remove the agent-facing exception from AGENTS.md. Update the branch reference in the remaining valid doc. Run a verification grep across `docs/` to confirm no stale `dev` branch references remain.

## Impact

| Risk | Mitigation |
|------|-----------|
| Missed `dev` references | Verification grep covers all `docs/` files |
| `.opencode/` contains `dev` refs | Excluded by policy — documented in non-goals |
| Generic "dev" in prose captured | Sweep targets `` `dev` `` backtick patterns only, excluding plain "dev" |

**Key dependencies:** PR #1354 (already merged — `dev` → `main` migration complete)

---

Co-authored with AI: OpenCode (deepseek-v4-flash-free)
