# Plan: Test Remediation — `\ln` → `\so` Migration

## Scope
Section 5 of `plans/remediation_mdf_ln_misuse.md`. Two test files only. No `src/` changes.

---

## File 1: `tests/services/test_ln_parsing.py`

### 1.1 Rename class
- `TestLnParsing` → `TestSoParsing`

### 1.2 `test_ln_parsing_bulk_new` → `test_so_parsing_bulk_new`
- Rename method.
- Update docstring: `\ln tag` → `\so tag`.
- Line 74: `mdf_data` fixture — replace `\\ln Mohegan [moh]` with `\\so Mohegan [moh]`.
- Assertions unchanged (still expect `lang.name == "Mohegan"`, `lang.code == "moh"`).

### 1.3 `test_legacy_lg_not_parsed` — no fixture change needed
- Comment on line 135 says `\ln is missing` — update to `\so is missing`.

### 1.4 `test_no_ln_tag_no_exception_no_default` → `test_no_so_tag_no_exception_no_default`
- Rename method.
- Update docstring: `\ln tag` → `\so tag`.
- Line 166 assertion message: `\ln is missing` → `\so is missing`.

---

## File 2: `tests/integration/test_language_assignment.py`

### 2.1 `test_scenario_1_headword_ln_only` → `test_scenario_1_headword_so_only`
- Rename method.
- Update docstring: `\ln` → `\so`.
- Line 84: replace `\\ln Mohegan [moh]` with `\\so Mohegan [moh]`.

### 2.2 `test_scenario_2_headword_and_subentry_ln` → `test_scenario_2_headword_and_subentry_so`
- Rename method.
- Update docstring: `\ln` → `\so`.
- Line 96: replace both `\\ln Mohegan [moh]` and `\\ln English [eng]` with `\\so`.

### 2.3 `test_scenario_3_subentry_ln_only` → `test_scenario_3_subentry_so_only`
- Rename method.
- Update docstring: `\ln` → `\so`.
- Line 114: replace `\\ln Mohegan [moh]` with `\\so Mohegan [moh]`.

### 2.4 `test_scenario_4_no_ln` → `test_scenario_4_no_so`
- Rename method.
- Update docstring: `\ln` → `\so`.

---

## Verification
- Run `uv run python -m pytest tests/services/test_ln_parsing.py tests/integration/test_language_assignment.py -v`
- All tests must be green.
- Update `plans/remediation_mdf_ln_misuse.md` Section 5 to ✅ DONE.

---

**Status**: ⏳ Awaiting Approval
