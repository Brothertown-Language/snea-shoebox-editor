# Plan: Fix ∞ Sort Order — Treat as Letter After "oo"

**File:** `src/services/linguistic_service.py` (only)

## Problem
`∞` (U+221E) is a math symbol in Unicode, so PostgreSQL sorts it before ASCII letters.
In this Algonquian dictionary it is a letter representing a long rounded vowel, and should
sort immediately after all `oo*` entries and before any `op*` entries.

`✔` (U+2714, 7 occurrences) is an annotation mark and should be stripped for sort purposes.

## Approach
In `generate_sort_lx`, after step 3 (straighten quotes) and before step 4 (lowercase),
add a symbol-substitution step that maps:
- `∞` → `oozzz` (sorts after `oo` and all `oo*` entries, before `op`)
- `✔` → `""` (stripped — annotation mark, not a letter)

`oozzz` is chosen because:
- It sorts after `oo` and all `ooa`…`ooy` entries in ASCII/Unicode collation.
- It sorts before `op`.
- The extra `zzz` suffix eliminates any collision risk with real `ooz*` lemmas.

## Steps

1. **Add symbol substitution step in `generate_sort_lx`** — after the quotes_map replacement
   loop (step 3), add a `symbol_map` dict mapping `∞` → `oozzz` and `✔` → `""`, and apply it.

2. **Add unit tests** — in `tests/services/test_linguistic_normalization.py`, add a new test
   method `test_generate_sort_lx_special_symbols` covering:
   - `∞` alone → `"oozzz"`
   - `-∞-` → `"oozzz-"` (leading punct stripped, trailing kept)
   - `o∞p` → `"ooozzzp"` (mid-word substitution)
   - `✔word` → `"word"` (check mark stripped)
   - Verify sort order: `generate_sort_lx("oo") < generate_sort_lx("∞") < generate_sort_lx("op")`
   - Verify sort order: `generate_sort_lx("ooy") < generate_sort_lx("∞") < generate_sort_lx("op")`

3. **Add a migration** to re-normalize `records.sort_lx` and `search_entries.normalized_term`
   using the updated `generate_sort_lx`. Migration version: `20260303` + seconds-since-midnight
   at actual creation time.
   - Pattern: same as `_migrate_renormalize_sort_lx` and `_migrate_ignore_leading_numerals`.
   - Register in the migrations table with description:
     `"Re-normalize sort_lx and normalized_term for ∞ and ✔ symbol sort order"`.

---

## Files Changed
- `src/services/linguistic_service.py`
- `tests/services/test_linguistic_normalization.py`
- `src/database/migrations.py`

## Status: IMPLEMENTED
