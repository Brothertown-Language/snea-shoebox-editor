# Plan: Language Identification — Per-Line ISO 639 Pattern Scan

## Context

Currently `src/mdf/parser.py` extracts language identification only from specific MDF tags
(`\so`, `\ve`, `\ns`). The issue requires scanning **every line** of each record for one or
more occurrences of the pattern `"Full Language Name [xxx]"` (ISO 639 3-letter code).

- The `\lx` bundle (lines before the first structural sub-entry tag: `\se`, `\sn`, `\va`, `\xv`)
  yields **primary** languages (`is_primary=True`).
- Any subsequent bundle (after a structural sub-entry tag) yields **secondary** languages
  (`is_primary=False`).
- No `\lg` tag exists — that reference is removed.
- Duplicate `(name, code)` pairs within a record are deduplicated (first occurrence wins).

---

## Pattern

```
r'([A-Za-z][^\[]*?)\s*\[([a-z]{3})\]'
```

Applied to the **value portion** of every line (after the tag prefix), for every line in the record.

---

## Files to Change

### 0. `src/services/upload_service.py`

- **In `_update_record_languages`**: remove the line `final_name = iso_entry.ref_name`. Use
  `lg_name` (the name as parsed from the MDF) unchanged.
- **Validation rule**: both the parsed `lg_name` **and** `lg_code` must match the ISO 639-3
  record — i.e. `iso_entry.id == lg_code` **and** `iso_entry.ref_name == lg_name` — for the
  entry to be accepted. If either does not match, the entry is silently dropped.

### 1. `src/mdf/parser.py`

- **Remove** the per-tag `\so`, `\ve`, `\ns` language extraction blocks (the `re.search` +
  `record['lg'].append(...)` calls at lines 84–88, 113–117, 126–130).
- **Add** a new private helper `_extract_iso_langs(line_value) -> list[dict]` that applies the
  pattern and returns zero or more `{'name': ..., 'code': ...}` dicts.
- **In `_process_block_into_record`**, after the per-tag dispatch loop, add a second pass:
  iterate every line, determine `is_primary` from `in_headword` state (same structural-tag
  logic already present), call `_extract_iso_langs` on the line value, and append to
  `record['lg']` — deduplicating by `(name, code)`.

### 2. `tests/services/test_ln_parsing.py`

- **Update** `test_legacy_lg_not_parsed` — the `\lg` tag reference is invalid; rename test to
  `test_no_language_pattern_no_record_language` and use MDF with no `Name [xxx]` pattern at all.
- **Add** a new test `test_multi_line_language_detection` that verifies:
  - A record with `\lx` bundle containing `Mohegan-Pequot [xpq]` on a `\so` line → primary.
  - A record with a `\se` sub-entry containing `Wampanoag [wam]` → secondary.
  - Both `RecordLanguage` rows are created with correct `is_primary` values.

---

## Verification

- `uv run python -m pytest tests/services/test_ln_parsing.py -v`
- All existing tests must remain green.

---

**Status**: ✅ COMPLETE

> **Principle**: The service layer validates data; it does not alter it. Names are stored as
> found in the MDF source. Both the ref name **and** the 3-letter code must match the ISO 639-3
> table exactly — if either does not match, the entry is silently dropped.
