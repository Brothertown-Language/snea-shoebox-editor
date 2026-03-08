# REVIEW PLAN: Record Match HM/NT Scoring Fix

## Problem

`_score_candidate` in `upload_service.py` returns `(hm_match, ge_score, nt_score)`.

In the failing case:
- Upload: `\lx Ewo \hm 3 \ge He \nt Section: CHAP. I.; Context: names, but |Keen|, You, |Ewo|, He &c.`
- rec_a: `Ewò hm=1` — `hm_match = (parsed_hm=3 == c.hm=3)` → **wait, rec_a has hm=1, not 3**

Re-examining: upload has `\hm 3`. rec_a has `hm=1`. So `hm_match` for rec_a = `(3 == 1)` = False.
rec_b has `hm=1` (default). So `hm_match` for rec_b = `(3 == 1)` = False too.

Both have `hm_match=False`. Both have `ge='He'` → `ge_score ≈ 1.0` for both.
Tiebreaker is `nt_score`. rec_b has the CHAP. I. context matching the upload → higher nt_score.

**So why does it fail?** The base-form fallback (section C) queries with `func.lower(func.translate(...))`.
The translate string maps diacritics but may not include `ò` → `o`. Let me verify the translate covers `ò`.

The translate call: `'áàâäãåāéèêëēíìîïīóòôöõøōúùûüū'` → `'aaaaaaaeeeeeiiiiiooooooouuuuu'`
Count source chars: á à â ä ã å ā é è ê ë ē í ì î ï ī ó ò ô ö õ ø ō ú ù û ü ū = 29 chars
Count target chars: a a a a a a a e e e e e i i i i i o o o o o o o u u u u u = 29 chars ✓

`ò` is in position 19 (0-indexed 18) → maps to `o`. So `Ewò` → `ewo` = `Ewo` → `ewo`. Section C DOES find both candidates.

**Actual root cause**: Both candidates have `hm_match=False` and `ge_score=1.0`. The `nt_score` for rec_a
uses `_extract_first_nt(candidate_mdf_map.get(c.id, ''))`. rec_a has TWO `\nt` fields; `_extract_first_nt`
returns the first one: `"Section: <[A8r.]>; Context: example..."`. rec_b has one `\nt`:
`"Section: CHAP. I.; Context: Names, but |Keen|..."`.

Upload `\nt`: `"Section: CHAP. I.; Context: names, but |Keen|, You, |Ewo|, He &c. Tahéna"`

nt_score rec_b vs upload should be higher than rec_a vs upload. But `candidate_mdf_map` is built from
`chunk_exact_map` — which only contains records with **exact lx match**. Since upload lx is `Ewo` and
DB records are `Ewò`, there is NO exact lx match → `chunk_exact_map` is empty for `Ewo` →
`candidate_mdf_map.get(c.id, '')` returns `''` for ALL base-form candidates → `nt_score = 0.0` for all.

With `nt_score=0.0` for both and `ge_score=1.0` for both and `hm_match=False` for both, the result is
a tie → `max()` returns whichever comes first (rec_a, added first) → **wrong match**.

## Root Cause Summary

In section C (base-form fallback), `candidate_mdf_map` is not populated for base-form candidates
(only exact-lx candidates are in the map). So `nt_score` is always 0.0 for all base-form candidates,
making `nt_score` useless as a tiebreaker in section C.

## Proposed Fix

Build a **separate MDF map for base-form candidates** in section C, fetching their MDF text from the
DB (or from a pre-built full map), so `_score_candidate` can compute a real `nt_score`.

### Option A — Fetch MDF for base-form candidates on demand (targeted, minimal change)
In section C, after fetching `base_candidates`, fetch their MDF text from `MatchupQueue` or a
`candidate_mdf_map` built from all records in the source chunk. Then `_score_candidate` will have
real `nt_score` values.

### Option B — Extend `candidate_mdf_map` to cover all source records (broader, safer)
Build `candidate_mdf_map` from all records in the source (not just exact-lx matches), so it's
available for both section B and section C.

**Recommendation: Option B** — it's a one-line change to the map-building query scope, fixes the
issue cleanly, and makes `nt_score` reliable for all fallback paths.

## Files to Change

- `src/services/upload_service.py` — extend `candidate_mdf_map` to cover all source records

## Test

`test_suggest_matches_base_form_hm_ge_nt_tiebreak` already exists and already fails. No new test needed.
After fix, run the full `TestMatchAndCommitOperations` suite to confirm no regressions.

## Steps

1. Locate where `candidate_mdf_map` is built in `upload_service.py`
2. Extend its query to cover all records in the source (not just exact-lx matches)
3. Run `test_suggest_matches_base_form_hm_ge_nt_tiebreak` — expect PASS
4. Run full `TestMatchAndCommitOperations` — expect all pass
