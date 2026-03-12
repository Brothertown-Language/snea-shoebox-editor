# Plan: Fix: Apply Now honors dropdown selection on MDF verify page

**Status:** ✔️ Completed
**Created:** 2026-03-11  
**Scope:** `src/services/upload_service.py`, `src/frontend/pages/upload_mdf.py`

---

## Background

On the MDF verify/review page, the "Apply Now" button does not reliably honor the dropdown
selection. The current design uses a fragile two-step pattern:

1. Status-update block (line 849 of `upload_mdf.py`): if `selected_status != row.status`,
   call the appropriate service method to update the DB status.
2. Apply Now handler (line 879): call `apply_single`, which re-fetches the row from DB and
   acts on `row.status`.

**The broken case**: when `selected_status == 'matched'` but `has_suggestion == False`
(line 851 guard), the status-update block silently skips all branches — nothing is called,
DB stays `'pending'`. Then `apply_single` raises `ValueError("Cannot apply entry with
status 'pending'")`, caught and shown as an error. The button appears to do nothing.

More broadly, any silent failure in the status-update block leaves the DB stale, causing
`apply_single` to act on the wrong status.

**Fix**: Pass `selected_status` directly into `apply_single` as `override_status`. When
provided, `apply_single` uses it instead of `row.status` and updates `row.status` in the
same transaction. Apply Now becomes authoritative — it always acts on what the dropdown
says, regardless of prior DB state.

---

## Steps

1. ✔️ Completed — Add `override_status: str | None = None` parameter to
   `UploadService.apply_single` in `src/services/upload_service.py`. When provided, set
   `row.status = override_status` before the action dispatch. Update the `pending`/`ignored`
   guard to use the effective status.

2. ✔️ Completed — Update the Apply Now handler in `src/frontend/pages/upload_mdf.py` (line 882)
   to pass `override_status=selected_status` to `apply_single`.

3. ✔️ Completed — Run existing tests to confirm no regressions:
   `uv run pytest tests/services/test_upload_service.py -x -q`

4. ✔️ Completed — Verify completion by code inspection: confirm Apply Now correctly dispatches
   for all dropdown values (`matched`, `create_new`, `create_homonym`, `discard`).

5. ✔️ Completed — Archive plan immediately upon completion.

