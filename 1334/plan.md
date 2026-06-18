# Implementation Plan — #1334

**Spec:** [[SPEC-FIX] Remove undocumented file extension filter from MDF uploader](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1334)

## Goal

Remove the restrictive `type` parameter from `st.file_uploader` in the MDF upload page so any file (regardless of extension) can be uploaded and validated by the MDF parser, not by the uploader filter.

## Architecture

Two file changes: `src/frontend/pages/upload_mdf.py` (remove `type` param, update `help` text) and `tests/frontend/test_upload_mdf_page.py` (update existing test assertion that checks for `type`). No backend or schema changes.

The `st.file_uploader` call currently passes `type=["txt", "mdf"]` — this must be removed entirely. The `help` text must be updated to document common MDF extensions without implying restriction. The test `test_file_uploader_accepts_txt_mdf` asserts `kwargs[1]["type"] == ["txt", "mdf"]` — this must be changed to assert `type` is absent.

## Tech Stack

- Python 3.12+, Streamlit (`st.file_uploader`)

## File Structure

| File | Responsibility |
|------|---------------|
| `src/frontend/pages/upload_mdf.py` | Contains the `upload_mdf()` function with the `st.file_uploader` call to modify |
| `tests/frontend/test_upload_mdf_page.py` | Contains `test_file_uploader_accepts_txt_mdf` which asserts `type` is present — must be updated |

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

---

## Phase 1: Remove file extension restriction from MDF uploader

**Concern:** Remove `type` parameter from `st.file_uploader`, update `help` text to document common MDF extensions without implying server-side restriction.

**Files:** `src/frontend/pages/upload_mdf.py` (lines 49-54), `tests/frontend/test_upload_mdf_page.py` (line 132)

**SCs covered:** SC-1, SC-2, SC-3, SC-4

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "execute sc-coherence-gate from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "execute pre-red-baseline from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "execute red-phase from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "execute red-doublecheck from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-red-enforcement from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "execute green-phase from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "execute post-green-enforcement from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1 |
| G8: checkpoint-commit | inline | N/A | N/A | — | SC-1, SC-2, SC-3, SC-4 |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "execute structural-checks from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1 |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "execute green-doublecheck from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-2, SC-3, SC-4 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "execute green-vbc from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "execute adversarial-audit from implementation-pipeline", "issue_number": 1334, "phase": 1, "audit_phase": "plan-fidelity", "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "execute cross-validate from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "execute regression-check from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-4 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "execute review-prep from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "execute exec-summary from implementation-pipeline", "issue_number": 1334, "phase": 1, "github.owner": "Brothertown-Language", "github.repo": "snea-shoebox-editor"}` | SC-1, SC-2, SC-3, SC-4 |

### TDD Items

#### Item 1: Remove `type` parameter and update `help` text in upload_mdf.py

| Step | Action |
|------|--------|
| **RED** | Update `test_file_uploader_accepts_txt_mdf` in `tests/frontend/test_upload_mdf_page.py` — change `self.assertEqual(kwargs[1]["type"], ["txt", "mdf"])` to `self.assertNotIn("type", kwargs[1])`. Run the test: `uv run pytest tests/frontend/test_upload_mdf_page.py::TestUploadMdfFileUploader::test_file_uploader_accepts_txt_mdf -xvs` — must FAIL because `type` is still present. |
| **GREEN** | Remove `type=["txt", "mdf"]` parameter from `st.file_uploader` in `upload_mdf.py`. Update `help` text to: `"Select an MDF file (.txt, .mdf, .db, or other extension) containing MDF-formatted dictionary entries."` |
| **REFACTOR** | Run the test again — must PASS. Run `ruff` and `pyright` on both modified files. Verify `type=` is gone with grep. |

#### Item 2: Behavioral verification for SC-2 (`.db` accepted) and SC-3 (non-MDF rejected by parser)

| Step | Action |
|------|--------|
| **RED** | Create `./tmp/test_sc2_sc3.sh` that simulates uploading a `.db` file with valid MDF content and a `.png` file. Verify current behavior: `.db` rejected by `st.file_uploader` (SC-2 FAIL), `.png` rejected by `st.file_uploader` (SC-3 FAIL). Run and confirm both fail. |
| **GREEN** | After Item 1 GREEN is complete, re-run the same script. Verify `.db` is now accepted by the uploader (SC-2 PASS) and `.png` is rejected by the MDF parser with `ValueError` (SC-3 PASS). |
| **REFACTOR** | Document the behavioral test results in `./tmp/behavioral-evidence-1334.log`. |

---

> **Compliance Requirement:** All steps and sub-steps in this document MUST be followed in order. Failure to comply with any step — including but not limited to verification gates, test phases, audit checkpoints, and review steps — will result in the feature branch being rejected and discarded, requiring a full rework from scratch and loss of all prior work. There is no valid reason to skip, compress, reorder, or omit any step. If a step appears redundant or unnecessary, follow it anyway — the cost of following an extra step is negligible compared to the cost of rework from a skipped step.

## Exit Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| EC-1 | Plan stored at `.issues/1334/plan.md` | `ls .issues/1334/plan.md` |
| EC-2 | All SCs from spec mapped to plan items | SC-1 through SC-4 in Phase 1 |
| EC-3 | Plan passes validation (no placeholders, actionable steps) | Self-review |
| EC-4 | Dispatch table uses canonical 16-gate format | Verification against implementation-pipeline SKILL.md |
