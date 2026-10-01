# Plan Input Verification Ledger — issue #1392

Written once by `writing-plans/tasks/create.md` Step 3a. Subsequent steps re-read THIS ledger,
not the sources. Do not re-verify anything recorded here.

## Issue state (from `.issues/1392/issue.yaml`)

- number: 1392
- title: `[SPEC-FIX] Unrendered <MAINTAINER_CONTACT> Placeholder Leaks Into UI`
- state: open
- labels: `[approved-for-for_pr]`
- remote_issue: 1392 (github.com / Brothertown-Language/snea-shoebox-editor)
- authorized scope: `for_pr` (label `approved-for-for_pr`) → plan frontmatter carries
  `authorization_scope: for_pr`, `pr_strategy: stacked`

## SC list with evidence types (from `spec.md` §3)

| SC | Evidence type | Verification method (summary) |
|----|---------------|-------------------------------|
| SC-1 | behavioral | Playwright real-browser test, `test/ui/`, `playwright_e2e`, `SNEA_E2E=1`, live app on :8501 |
| SC-2 | string | `grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py` → 0 matches |
| SC-3 | semantic | Clean-room sub-agent reads the 3 former call sites, confirms shared resolution path |
| SC-4 | behavioral | Startup-path test with key absent → error naming `contact.maintainer_label` raised from startup; `uv run pytest test/` |
| SC-5 | string | AST sweep test over user-facing Streamlit render-call string literals; `uv run pytest test/`; zero `<[A-Z][A-Z0-9_]{2,}>` |
| SC-6 | string | `grep -n "maintainer_label" .streamlit/secrets.toml .streamlit/secrets.toml.production` → ≥1 hit each |
| SC-7 | string | `grep -n "maintainer_label" docs/development/local-development.md` → ≥1 hit |

Total: 7 SCs, 7 items (1:1, item numbers track SC numbers).

## Structure artifact phase/SC mappings (from `artifacts/structure.yaml`)

- Phase 1 — "Configuration & documentation enablement": SC-6, SC-7. depends_on: []
- Phase 2 — "Secrets-based resolution, fail-fast validation & placeholder sweep":
  SC-3, SC-1, SC-2, SC-5, SC-4. depends_on: [1]
- Phase 2 intra-phase execution order (must be preserved in the plan):
  1. Item 3 (SC-3) full cycle
  2. Item 1 (SC-1) full cycle
  3. Item 2 (SC-2) RED
  4. Item 5 (SC-5) RED
  5. Item 2 (SC-2) GREEN → verify → commit
  6. Item 5 (SC-5) GREEN → verify → commit
  7. Item 4 (SC-4) full cycle
- DAG: single edge 1→2; acyclicity PASS; triplet co-location PASS (7/7 SCs);
  cross-phase dependency PASS.
- Per-phase workflow: implementation-workflow reference card
  (`skills/writing-plans/reference/implementation-workflow.md`).
- Per-phase pre-implementation: `pre-regression` (test-driven-development),
  `pre-regression-verify` (verification-before-completion).
- Per-item cycle: `red`, `green`, `post-regression`, `verify` (all task-card),
  `commit-inline` (direct — orchestrator).
- Post-implementation: audit, z3-check, structural-checks, pre-pr-gate,
  regression-check, review-prep, create-pr, exec-summary.
- z3-check command: `.opencode/tools/solve check --state-path
  .issues/1392/artifacts/state-analysis.yaml --contract-path
  .issues/1392/dependency-contract.yaml`

## Supporting artifacts confirmed present in `.issues/1392/artifacts/`

blast-radius.yaml, code-path-inventory.yaml, cross-cutting-matrix.yaml,
interface-compatibility.yaml, state-analysis.yaml, concern-map.yaml,
analysis-summary.yaml, structure.yaml, testability-assessment.yaml,
solve-output.yaml, plan-output.yaml (Z3: SOLVED_SATISFICING, plan length 9).

## CLI surface needed (live probed `local-issues --help` / `update --help`)

- Label write (Step 9, PRIMARY canonical local write):
  `./.opencode/tools/local-issues update --number .issues#1392 --labels approved-for-for_pr spec-cleared`
  - `--labels` takes space- or comma-separated values and REPLACES the entire labels array —
    every existing label MUST be passed alongside the new one (existing: `approved-for-for_pr`).
  - Failure of this local write → BLOCKED with `LOCAL_LABEL_WRITE_FAILED`.
- Remote write (Step 9, SECONDARY best-effort): GitHub label API, never blocking.

## Notes carried from structure.yaml source_notes

- `sc-summary.yaml` never existed for this issue; SC set comes from
  `analysis-summary.yaml` sc_inventory + spec §3 table + spec §7 Traceability +
  concern-map.yaml. No SC data synthesized.
