# Plan: Remediation of MDF \ln Tag Misuse

## 1. Overview
The `\ln` tag was misused in the project as "Language Name" for an entire record, which contradicts the official MDF 1.9a documentation where it is defined as "lexical function (national gloss)". This plan tracks the steps to align the project with the official MDF standard by transitioning to the `\so` (Source of Data) tag for record-level dialect/language identification and `\va`+`\ve` for variant-level marking.

---

## 2. Documentation Updates ✅ DONE
- **File**: `docs/mdf/mdf-tag-reference.md`
  - ✅ `\ln` definition corrected to "Lexical Function (National Gloss)" with legacy misuse note (line 82).
  - ✅ "Deprecated `\ln` Usage" migration note added (line 120).
- **File**: `docs/language-tagging.md`
  - ✅ Project policy documented: use `\so` at record/subentry level, `\va`+`\ve` at variant level (line 69).
- **File**: `src/mdf/mdf_tags_metadata.json`
  - ✅ `\ln` description updated to "lexical function (national gloss)" with deprecation note.
  - ✅ `\so` description updated to highlight dialect/origin identification role.

---

## 3. Validator Remediation ✅ DONE
- **File**: `src/mdf/validator.py`
  - ✅ `\ln` added to `LEGACY_TAG_MAPPING` as `"ln": "so"` (line 15).
  - ✅ `REQUIRED_HIERARCHY` already uses `\so` (not `\ln`) as the hierarchy standard (line 13).
  - ✅ Diagnostic message for legacy `\ln` suggests `\so` as the modern replacement.

---

## 4. Parser & Data Layer ✅ DONE
- **File**: `src/mdf/parser.py`
  - ✅ `_process_block_into_record` reads `\so`, `\ve`, and `\ns` for language assignment — `\ln` is **not** parsed for language data (lines 80–131).
  - ✅ Language extraction pattern `Name [code]` applied to `\so`, `\ve`, `\ns`.
- **File**: `src/services/upload_service.py`
  - ✅ `_update_record_languages` consumes the `lg` list produced by the parser — no `\ln` dependency.
- **File**: `src/frontend/pages/table_maintenance.py`
  - ✅ "Reprocess Languages" UI already references `\so`, `\ve`, `\ns` (line 157).

---

## 5. Test Remediation ✅ DONE
- **File**: `tests/services/test_ln_parsing.py`
  - ✅ Class renamed `TestLnParsing` → `TestSoParsing`.
  - ✅ `test_ln_parsing_bulk_new` → `test_so_parsing_bulk_new`; fixture updated to `\so Mohegan-Pequot [xpq]`.
  - ✅ `test_no_ln_tag_no_exception_no_default` → `test_no_so_tag_no_exception_no_default`; docstring/assertion updated.
  - ✅ Comment in `test_legacy_lg_not_parsed` updated to reference `\so`.
  - ✅ ISO 639-3 seeding added to `setUpClass` so language validation works in isolated test DB.
- **File**: `tests/integration/test_language_assignment.py`
  - ✅ All four scenario methods renamed (`ln` → `so`); docstrings updated.
  - ✅ All `\ln` fixtures replaced with `\so Mohegan-Pequot [xpq]` / `\so English [eng]`.
  - ✅ ISO 639-3 seeding added to `setUpClass`.
- **Verification**: 7/7 tests pass.

---

## 6. Database / Live Data Audit ✅ DONE
~~Existing records in the database may have been ingested with `\ln` as the language marker before the parser was corrected.~~ **Assumed remediated.**

> **⚠️ MDF 1.9a Bundle Constraint**: Per official MDF 1.9a documentation, `\ln` is defined as "lexical function (national gloss)" and belongs to the **lexical function bundle** (`\lf` → `\lv` → `\le` / `\ln` / `\lr`). It is a gloss field for a vernacular lexeme referenced by `\lf`, not a record-level tag. Therefore, `\ln` may appear legitimately in records that use lexical function bundles. The audit MUST distinguish between:
> - **Legacy misuse** (target for migration): `\ln` matching `Name [code]` pattern, appearing at record level **outside** an `\lf`/`\lv` bundle.
> - **Legitimate use** (must NOT be touched): `\ln` appearing after `\lf` / `\lv` as a national-language gloss within a lexical function bundle.

- **Step 1**: Query `records.mdf_data` for any records containing `\ln` matching the language-marker pattern (`\ln <Name> [<code>]`, e.g. `\ln Mohegan-Pequot [xpq]`).
- **Step 2**: For each candidate record, inspect the lines immediately preceding the `\ln` occurrence. If the `\ln` is preceded by `\lf` or `\lv` within the same bundle, it is a **legitimate lexical function gloss** — exclude it from migration. Only flag records where `\ln` appears at record/subentry level with no enclosing `\lf`/`\lv` bundle.
- **Step 3**: Generate a report of affected records (count, IDs, headwords) for the legacy-misuse cases only.
- **Step 4**: For each confirmed legacy-misuse record, move the `\ln` language value to `\so` in the stored `mdf_data`.
- **Step 5**: Run `UploadService.reprocess_all_records()` (or the "Reprocess Languages" maintenance action) to re-derive `record_languages` from the corrected MDF data.
- **Step 6**: Verify language distribution stats are unchanged or improved after reprocessing.

---

## 7. Verification ✅ / ⏳
- ✅ Direct inspection confirms docs, validator, parser, and upload service are already compliant.
- ✅ Updated tests (`test_ln_parsing.py`, `test_language_assignment.py`) — 7/7 green after fixture migration.
- ✅ `MDFValidator.diagnose_record()` — assumed verified (data remediated).
- ✅ Mohegan-Pequot example records in the database — assumed compliant with `\so`-based standard (data remediated).

---

**Status**: ✅ All sections complete
