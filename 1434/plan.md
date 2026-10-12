# Plan — #1434: stabilize test_split_independent_scrolling_on_navigation

Source: `.issues/1434/spec.md` (validated 2026-10-11 — PASS, zero findings, one dispatch). Branch `feature/1434-stable-rail-scroll-establishment` (base tip 655d078).

SC validity: all three SCs judged against the validation standards — no invented, untestable, either/or, ambiguous, misclassified, or trivially-true criteria. No BLOCKED.

## Item 1 — SC-2 + SC-3 (closed-loop scroll establishment in the test)
- Deliverable: rewrite `test_split_independent_scrolling_on_navigation`'s scroll-establishment sequence in `test/ui/test_mdf_reference_e2e.py` (lines 755-781): replace the fixed `wait_for_timeout(400)` between set and read-back with a closed loop — set `scrollTop` (and a same-node probe marker) on the rail element; wait on a Playwright condition for stability (the set position persisting on the same DOM node across a probe window); read back `s0`; on an observed reset (read-back not showing the set position) re-establish and repeat, bounded at 2 re-sets after the initial attempt; exhausting the bound fails the test loudly; the `s0 > 400` assertion fires only on a persistent read-back. The navigation-side 1500 ms settle, the `abs(s1 - s0) < 60` and `dtop < 10` assertions, and the screenshot stay untouched.
- RED: the race is present in current code — fixed 400 ms sleep, no stability gate (inspection); the recorded flake (2 failures in 4 runs on `main` at 1be2185, issue filing) is the red-in-history evidence. A flake cannot be deterministically reproduced on demand, so RED is recorded evidence + code inspection, not a scripted failing run.
- GREEN: the closed loop as above.
- Verify: fact-decidable inspection of the diff — SC-2's clauses (no fixed sleep before the read-back; stability-gated on the rail itself; bounded at 2 re-sets; loud exhaustion) and SC-3 (thresholds 400 / 60 / 10 unchanged and present).

## Item 2 — SC-1 (determinism bar, executed evidence)
- Deliverable: 10 consecutive green single-test invocations of `test_split_independent_scrolling_on_navigation` against the live app.
- RED/GREEN: no code change in this item — the executed green chain is the deliverable (the spec's SC-1 instrument).
- Verify: regression protocol first — `bash scripts/sync_prod_to_local.sh` (the feature branch's script); app live on :8501 (`SNEA_E2E=1`, headless); then 10× `SNEA_E2E=1 uv run pytest test/ui/test_mdf_reference_e2e.py::test_split_independent_scrolling_on_navigation`, all green; outputs recorded under `tmp/1434/artifacts/`. Guard for the spec's unchanged-sibling clause: one `SNEA_E2E=1 uv run pytest test/ui/test_mdf_reference_e2e.py -k "split and not independent"` run of the sibling split tests, green.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
