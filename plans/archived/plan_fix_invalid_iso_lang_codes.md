# Plan: Fix Invalid ISO 639-3 Language Code References

## Scope
Audit finding: `[mof]` is not a valid ISO 639-3 code. The correct code for Mohegan-Pequot is `[xpq]`.
All other 380 apparent "invalid" hits are false positives (variable names, pronouns in Bible text, etc.).

---

## Files to Change

### 1. `src/mdf/mdf_tags_metadata.json` — line 494
- Replace `\\so Mohegan-Pequot [mof]; Prince-Speck 1904` → `\\so Mohegan-Pequot [xpq]; Prince-Speck 1904`

### 2. `docs/mdf/mdf-tag-reference.md` — lines 109 and 111
- Line 109: Replace `\so Mohegan-Pequot [mof]; Prince-Speck 1904` → `\so Mohegan-Pequot [xpq]; Prince-Speck 1904`
- Line 111: Replace `\va appece \ve Mohegan-Pequot [mof]` → `\va appece \ve Mohegan-Pequot [xpq]`

---

## Verification
- Re-run `uv run python tmp/audit_iso_langs.py` and confirm `[mof]` no longer appears.

---

**Status**: ✅ DONE
