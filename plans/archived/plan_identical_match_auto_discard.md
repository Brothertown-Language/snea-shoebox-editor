# Plan: Auto-Discard Identical Records During MDF Upload Match Phase

## Context

During `suggest_matches` in `src/services/upload_service.py`, once a `suggested_record_id` is
found for a queue row, there is no check for content identity. A separate post-step
(`auto_remove_exact_duplicates`) exists but deletes rows outright and runs independently.

The issue asks that **during the match phase itself**, if the uploaded record's content is
identical to the matched existing record, the queue row should be marked `status = 'discard'`
and `match_type = 'identical'` — so the UI can surface it clearly and `discard_marked` can
clean it up in bulk.

### Identity Rule

A record is considered a **100% match** (identical / discardable) when:

1. A `suggested_record_id` has been resolved (steps A, B, or C in the existing logic).
2. The uploaded `mdf_data`, after stripping its `\nt Record:` line (if present) **and all
   blank lines**, equals the existing record's `mdf_data` after the same normalization.
3. **If the uploaded record has no `\nt Record:` line**, it is treated as if it matches
   whatever `\nt Record:` line the existing record carries — i.e., the existing record's
   `\nt Record:` line is ignored on both sides for the comparison.

`_strip_nt_record_lines` handles rule 3 implicitly. Blank-line normalization is added
inline at the call site by filtering out empty/whitespace-only lines after stripping
`\nt Record:` lines. No new helper is needed.

---

## File to Change

### `src/services/upload_service.py` — `suggest_matches`

**Location**: inside the chunk loop, after step E (record-id conflict check), before
`row.suggested_record_id = suggested_record_id` is written.

**What to add**:

After a `suggested_record_id` is resolved, fetch the existing record's `mdf_data` from the
already-populated `record_map`-equivalent. Because `suggest_matches` does **not** currently
bulk-fetch `mdf_data`, a targeted per-chunk bulk fetch must be added.

#### Detailed Steps

1. **After building `chunk_id_map`** (line ~329), add a second bulk query to fetch `mdf_data`
   for all `same_source_candidates` IDs:
   ```python
   candidate_ids = {rec.id for rec in same_source_candidates}
   candidate_mdf_map = {}
   if candidate_ids:
       mdf_rows = (
           session.query(Record.id, Record.mdf_data)
           .filter(Record.id.in_(candidate_ids))
           .all()
       )
       candidate_mdf_map = {r.id: r.mdf_data for r in mdf_rows}
   ```

2. **After step E** (record-id conflict check), before writing `row.suggested_record_id`,
   add the identity check:
   ```python
   def _normalize(mdf_text: str) -> str:
       stripped = UploadService._strip_nt_record_lines(mdf_text)
       return '\n'.join(line for line in stripped.split('\n') if line.strip())

   # F. Identical-content check → auto-discard
   is_identical = False
   if suggested_record_id is not None:
       existing_mdf = candidate_mdf_map.get(suggested_record_id)
       if existing_mdf is not None:
           if _normalize(row.mdf_data) == _normalize(existing_mdf):
               is_identical = True
   ```

   > `_normalize` is a local inline helper defined once before the per-row loop.

3. **When writing queue row fields**, apply the identical outcome:
   ```python
   if is_identical:
       match_type = 'identical'
       row.status = 'discard'
   ```
   This must be set **before** the `if suggested_is_locked` branch so that locked conflicts
   still take precedence (locked check overwrites status if needed — review ordering).

4. **Add `is_identical` to the result dict** returned per row:
   ```python
   'is_identical': is_identical,
   ```

#### Ordering / Priority Note

- If `suggested_is_locked` is `True`, `status = 'locked_conflict'` should still win over
  `'discard'`. Apply identical check first, then let the locked branch overwrite if needed
  (existing code already does `if suggested_is_locked: row.status = 'locked_conflict'` after
  `match_type` is set — this ordering is preserved).

---

## Out of Scope

- `auto_remove_exact_duplicates` is **not modified**. It remains a separate utility.
- No UI changes in this plan.
- No changes to `_strip_nt_record_lines`.
- `auto_remove_exact_duplicates` uses the same `_strip_nt_record_lines` helper but does **not**
  strip blank lines — that function is out of scope for this plan and is left unchanged.

---

## Verification

```
uv run python -m pytest tests/ -v -k "upload" --tb=short
```

Manual spot-check: stage a batch where one uploaded record is byte-for-byte identical to an
existing record (with and without a `\nt Record:` line in the upload). After `suggest_matches`,
confirm `status = 'discard'` and `match_type = 'identical'` on those rows.

---

**Status**: ✅ APPROVED — blank-line normalization added to identity check
