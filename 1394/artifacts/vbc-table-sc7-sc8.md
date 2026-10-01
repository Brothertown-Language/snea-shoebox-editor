# VbC Table — Issue 1394, Items I-7 (SC7) and I-8 (SC8)

**Verification type:** structural (declared evidence type per spec — non-testable invariants on script contract and migrations source)
**Trunk tip baseline:** `eb467b8`
**Date:** 2026-10-01
**Verification method:** re-ran the diff checks directly (sub-agent execution, per issue_context)

## Per-SC Evidence Table

| SC ID | Success Criterion | Evidence Type | Verification Command Run | Exact Output Observed | Pass/Fail |
| -- | -- | -- | -- | -- | -- |
| SC7 | After the fix, the `scripts/sync_prod_to_local.sh` invocation contract and CLI surface are unchanged — no command, argument, environment variable, or exit-code contract present at trunk tip `eb467b8` is altered by this fix. | structural | `git diff eb467b8 -- scripts/sync_prod_to_local.sh` (from `/home/muksihs/git/snea-shoebox-editor`) | empty diff (no output), exit code 0 | PASS |
| SC8 | After the fix, `src/database/migrations.py` and the production schema are untouched — no modification to migrations source or any production DDL artifact attributable to this fix. | structural | `git diff eb467b8 -- src/database/` (from `/home/muksihs/git/snea-shoebox-editor`) | empty diff (no output), exit code 0 | PASS |

## VbC Table (4-column, PR-body consumption)

| SC ID | Success Criterion | Test | Result |
| -- | -- | -- | -- |
| SC7 | `scripts/sync_prod_to_local.sh` invocation contract and CLI surface unchanged vs trunk tip `eb467b8` | `git diff eb467b8 -- scripts/sync_prod_to_local.sh` (structural) | PASS |
| SC8 | `src/database/migrations.py` and production schema untouched vs trunk tip `eb467b8` | `git diff eb467b8 -- src/database/` (structural) | PASS |

## Notes

- Both SCs are structural invariants (I-7, I-8); structural evidence is the declared evidence type in the spec, so structural verification here is not EVIDENCE_TYPE_MISMATCH — the changes verify absence of modification, not runtime behavior.
- Commands were executed in the repo working directory at `/home/muksihs/git/snea-shoebox-editor`; both returned empty diffs (no hunks) with exit code 0.

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
