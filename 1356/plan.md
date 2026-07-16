# Plan: #1356 — Retire dev branch (purge references from docs/guidelines)

## Metadata

- **Spec**: #1356
- **Authorization scope**: `for_pr`
- **Plan phases**: 3 (sequential)
- **Cross-cutting SCs**: SC-6 (anti-lobotomization — verified in Phase 1)
- **Created**: 2026-07-16

## Phase Table

| Phase | File | SCs | Steps | Scope |
|-------|------|-----|-------|-------|
| 1 — Delete stale documentation | `plan-01.md` | SC-1, SC-2 | 3 | Delete two dead `.md` files referencing `dev` workflow |
| 2 — Edit remaining references | `plan-02.md` | SC-3, SC-4 | 3 | Remove/edit inline `dev` branch references in AGENTS.md and credential doc |
| 3 — Verification sweep | `plan-03.md` | SC-5, SC-6 | 3 | Grep sweep `docs/` + anti-lobotomization review |

## Dependency Chain

```
Phase 1 (delete) → Phase 2 (edit) → Phase 3 (sweep)
```

Phase 2 depends on Phase 1: confirms docs are gone before editing inline refs.
Phase 3 depends on both: sweep must capture all Phase 1 and Phase 2 changes.

## Authorization

- `approved-for-pr` label present
- Scope `for_pr` — autopilot through implementation, PR creation allowed
- Spec-to-plan auto-approval cascade applies per `for_pr` scope

## Pipeline Gate Steps

The following implementation-pipeline gates are enumerated in each phase's exit criteria:
- `git-workflow --task pre-work` (branch + submodule validation)
- `implementation-pipeline` (dispatch RED/GREEN sub-agents per step)
- `verification-before-completion` (verify SCs against evidence)
- `finishing-a-development-branch` (pre-PR checklist)
- `review-prep` (verification artifact assembly)
- `git-workflow --task pr-creation` (PR with correct body)
- `git-workflow --task cleanup` (post-merge)
