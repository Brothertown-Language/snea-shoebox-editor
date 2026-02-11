<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Phase A — MDF Parser Enhancements ✅

**Status:** Complete (2026-02-08)

### A-1. Extract `\nt Record:` tag from MDF data ✅
Update `src/mdf/parser.py` so `parse_mdf()` extracts the `\nt Record: <id>`
tag from each entry and returns it as an optional `record_id` integer field
in the parsed dict (None when absent).

### A-2. Extract searchable sub-entry fields ✅
Update `src/mdf/parser.py` so `parse_mdf()` also extracts `\va` (variant),
`\se` (sub-entry), `\cf` (cross-reference), and `\ve` (English of sub-entry)
fields.  Return them as lists of strings in the parsed dict.

### A-3. Add `\nt Record:` deduplication / normalization helper ✅
Create a standalone function `normalize_nt_record(mdf_text: str, record_id: int) -> str`
in `src/mdf/parser.py` that:
- Removes all existing `\nt Record: …` lines from the text.
- Appends exactly one `\nt Record: <record_id>` line at the end.

### A-4. Write unit tests for parser enhancements ✅
Add tests in `tests/` covering:
- Parsing entries with and without `\nt Record:`.
- Parsing entries with `\va`, `\se`, `\cf`, `\ve`.
- `normalize_nt_record` adding, replacing, and deduplicating the tag.

Use `src/seed_data/natick_sample_100.txt` (150 randomly selected records,
larger than median size, from the full Natick dictionary) as the test fixture
for all parser tests.

### Phase A — Implementation Summary

**Source files changed:**
- `src/mdf/parser.py` — Rewrote parser using simple line-oriented parsing
  (no regex).  Added helper functions `_extract_tag()` and
  `_is_nt_record_line()`.  Added `normalize_nt_record()`.
- `src/seed_data/natick_sample_100.txt` — Regenerated with 150 randomly
  selected records (seed=42) from the full Natick dictionary.

**Test files added:**
- `tests/mdf/test_parser_phase_a.py` — 19 unit tests:
  - 6 tests for `record_id` extraction (present, absent, extra spaces,
    other `\nt` lines, sample file).
  - 7 tests for sub-entry field extraction (`\va`, `\se`, `\cf`, `\ve`,
    empty lists, sample file validation).
  - 6 tests for `normalize_nt_record` (add, replace, deduplicate, preserve
    other `\nt`, append position, content preservation).

**Test results:** All 53 tests pass (19 new + 34 existing) with zero
regressions.
