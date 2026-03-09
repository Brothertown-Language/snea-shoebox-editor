# Plan: Add Bundle Spacing to MDF Records

## Context

`format_mdf_record` in `src/mdf/parser.py` currently inserts a blank line before `\se`, `\xv`,
and `\nt Record:` lines using an incremental approach. The issue provides a reference implementation
(`add_bundle_spacing`) from another project that uses a normalize-then-insert pattern, which is
idempotent and more robust.

---

## Approach

Replace the blank-line logic in `format_mdf_record` with the normalize-then-insert pattern:

1. **Normalize**: strip all existing blank lines from the record lines.
2. **Insert**: add exactly one blank line before each bundle-start tag (except the very first line).
3. **Idempotent**: running the function multiple times produces the same result.

### Bundle-start tags (per reference implementation)

| Tag   | Bundle                  |
|-------|-------------------------|
| `\sn` | Sense number section    |
| `\se` | Subentry section        |
| `\xv` | Example bundle          |
| `\et` | Etymology bundle        |

**Not included** (removed from prior plan): `\ps`, `\pn`, `\va`, `\cf`

### Regex

```
^(\s*)\\(?:sn|se|xv|et)(?:\s+|$)
```

---

## File to Change

### `src/mdf/parser.py` — `format_mdf_record`

- Replace the current incremental blank-line logic with:
  1. Split input into lines; strip all blank lines.
  2. Iterate lines; for each line at index > 0 that matches the bundle regex, prepend a blank line.
  3. Also prepend a blank line before `\nt Record:` lines (existing behaviour, preserved).
  4. Update the docstring to reflect the new approach and tag list.
- The function signature and return type (`str`) remain unchanged.

---

## Verification

- `uv run python -m pytest tests/ -v -k "format_mdf"` (or full suite if no targeted tests exist)
- Manual spot-check: confirm blank lines appear before `\sn`, `\se`, `\xv`, `\et` in a sample record,
  and that running the function twice produces the same output (idempotency).

---

**Status**: 🔲 PENDING APPROVAL
