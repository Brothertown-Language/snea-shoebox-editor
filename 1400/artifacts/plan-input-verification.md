# Plan Input Verification Ledger — Issue #1400

Written once from verified sources (spec.md, structure.yaml, issue.yaml read 2026-10-02). Subsequent plan work re-reads THIS ledger, not the sources.

## Issue State

- Issue: 1400, status open
- Local labels (canonical, `issue.yaml`): `approved-for-pr`, `spec-cleared` — both present
- Remote: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400
- Authorization scope: `for_pr`; PR strategy: stacked

## Spec Facts (post-revision, 11 SCs)

- SC count: 11 (SC-1..SC-10 + SC-8a)
- Floor interval: strictly (0.9018, 0.9753) — OOC max "light bulb" 0.9018 < floor < smallest floor-clearing anchor beaver 0.9753
- SC-5 pinned message (exact): `No gloss results meet the sensitivity floor.`
- In-corpus anchors: water 1.0000, beaver 0.9753, how many 0.8917 (below floor → SC-5 empty outcome), money 0.9970, gun 0.9959, book 0.9936 — all rank 1
- Probe evidence: `tmp/1400/artifacts/verification-probe.yaml` (2026-10-02, production replica 6,681 embedded glosses, pin `thenlper/gte-small`, 20-query battery)
- All SCs are `behavioral` evidence type
- R-3: seam signature + status enum (`ok`/`empty_query`/`no_embeddings`/`stale_model`) unchanged; below-floor maps to `ok` + empty + message
- SC-9/SC-10 require Playwright real-browser evidence per `docs/development/ui_testing_standard.md` (AppTest smoke-only auxiliary; E2E skips reported as skipped)

## SC → Phase Mapping (structure.yaml)

| Phase | Name | SCs |
|---|---|---|
| 1 | calibration | SC-1, SC-8, SC-8a |
| 2 | seam-default-floor | SC-2, SC-3, SC-4, SC-5, SC-6, SC-7 |
| 3 | ui-threshold-plumbing | SC-9, SC-10 |

- DAG: 1 → 2 → 3 (linear, acyclic; triplet colocation PASS)
- Per-SC items: 11 items, one TDD cycle each (spec Missing Items table matches structure.yaml items)

## Files

- `src/services/semantic_search_service.py` (seam + calibration constant, phases 1–2)
- `src/frontend/pages/records.py` (UI default + override passthrough, phase 3)
- `test/ui/test_semantic_search_ui_flow_e2e.py` (Playwright, SC-9/SC-10)
- New calibration/seam pytest modules; calibration evidence artifact under `tmp/1400/artifacts/`

## CLI Surface

- Label writes: `./.opencode/tools/local-issues update snea-shoebox-editor#1400 --labels <all labels comma-joined>` (replaces entire labels array — always include existing labels)
- Z3 check: `./.opencode/tools/solve check --state-path ... --contract-path ...`
- Labels already contain `spec-cleared` — no label write needed for this plan run

## Plan State on Rewrite Entry

- plan.md exists with frontmatter, phase table (step ranges 3-17 / 18-47 / 48-57 / 58-65), pre-implementation steps 1-2, post-implementation steps 58-65, exit criteria C1-C8 (incl. C5a), Pre-Flight Guard, lifecycle events — already matches the 11-SC spec and this structure artifact
- Phase files plan-01/02/03.md exist and match phase SCs/items/step ranges
- dependency-contract.yaml matches structure DAG edges

## Co-authored

🤖 Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
