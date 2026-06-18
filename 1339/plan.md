# [SPEC-FIX] Use ISO 639-3 code alone for language identification in _update_record_languages

**Spec:** #1339
**Authorization Scope:** `for_plan` (auto-approves plan)
**Halt At:** `plan_created`
**PR Strategy:** `none` (spec-fix, single-PR at implementation time)

---

## Phase 1: Language Identification Fix

**Concern boundary:** Database persistence layer — `_update_record_languages()` method in upload service.

**Summary:** Remove the `ref_name != lg_name` guard and use `iso_entry.ref_name` as the canonical `Language.name` value, so ISO 639-3 codes become the sole identifier for language matching. Add a Jaro-Winkler fuzzy check to catch wrong-code entries (e.g., `French [mjy]`) where the name doesn't plausibly match the code.

**Files affected:**
- `src/services/upload_service.py` — `_update_record_languages()` (lines 1225-1236)
- `pyproject.toml` — add `rapidfuzz` dependency

### Dispatch Table

| Gate | Dispatch Type | Blind? | Sub-Agent Type | Receives Context | SCs |
|------|--------------|--------|----------------|-----------------|-----|
| G1: sc-coherence-gate | sub-task | yes (blind) | general | `{"task": "sc-coherence-gate", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G2: pre-red-baseline | sub-task | yes (blind) | general | `{"task": "pre-red-baseline", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G3: red-phase | sub-task | yes (blind) | general | `{"task": "red-phase", "issue_number": 1339, "phase": 1, "change_summary": "Remove ref_name != lg_name guard, add JaroWinkler plausibility check, change Language(name=lg_name) to Language(name=iso_entry.ref_name)"}` | SC-1, SC-2, SC-3, SC-4 |
| G4: red-doublecheck | sub-task | yes (blind) | general | `{"task": "red-doublecheck", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G5: post-red-enforcement | sub-task | yes (blind) | general | `{"task": "post-red-enforcement", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G6: green-phase | sub-task | yes (blind) | general | `{"task": "green-phase", "issue_number": 1339, "phase": 1, "change_summary": "Remove ref_name != lg_name guard, add JaroWinkler plausibility check, change Language(name=lg_name) to Language(name=iso_entry.ref_name)"}` | SC-1, SC-2, SC-3, SC-4 |
| G7: post-green-enforcement | sub-task | yes (blind) | general | `{"task": "post-green-enforcement", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G8: checkpoint-commit | inline | N/A | N/A | — | — |
| G9: structural-checks | sub-task | yes (blind) | general | `{"task": "structural-checks", "issue_number": 1339, "phase": 1}` | — |
| G10: green-doublecheck | sub-task | yes (blind) | general | `{"task": "green-doublecheck", "issue_number": 1339, "phase": 1, "sc_ids": ["SC-1", "SC-2", "SC-3", "SC-4"]}` | SC-1, SC-2, SC-3, SC-4 |
| G11: green-vbc | sub-task | yes (blind) | general | `{"task": "green-vbc", "issue_number": 1339, "phase": 1}` | SC-1, SC-2, SC-3, SC-4 |
| G12: adversarial-audit | sub-task | yes (blind) | general | `{"task": "adversarial-audit", "issue_number": 1339, "phase": 1, "audit_type": "verification-audit"}` | SC-1, SC-2, SC-3, SC-4 |
| G13: cross-validate | sub-task | yes (blind) | general | `{"task": "cross-validate", "issue_number": 1339, "phase": 1, "auditor_artifact_paths": "<from G12>"}` | SC-1, SC-2, SC-3, SC-4 |
| G14: regression-check | sub-task | yes (blind) | general | `{"task": "regression-check", "issue_number": 1339, "phase": 1}` | SC-2, SC-4 |
| G15: review-prep | sub-task | yes (blind) | general | `{"task": "review-prep", "issue_number": 1339, "phase": 1}` | — |
| G16: exec-summary | sub-task | yes (blind) | general | `{"task": "exec-summary", "issue_number": 1339, "phase": 1}` | — |

---

### TDD Step Details

#### RED Phase (G3)

Write a behavioral test that demonstrates the bug. Create `test/test_upload_service/test_language_identification.py` (or add to an existing file):

```python
# RED: Import a file with Mohican [mjy], verify Language row has code=mjy, name=Mahican
# This test MUST FAIL because the ref_name != lg_name guard blocks it

def test_mohican_mjy_creates_correct_language():
    """SC-1: Mohican [mjy] creates Language(code=mjy, name=Mahican)."""
    # Import Edwards_1787_Mohican.txt
    # Query Language table for code=mjy
    # Assert name == "Mahican" (ISO canonical) — NOT "Mohican" (source variant)
    # Assert record_languages association exists
```

```python
def test_english_eng_still_works():
    """SC-2: English [eng] still associates correctly (regression)."""
    # Import a file with English [eng]
    # Confirm RecordLanguage association is created
```

```python
def test_unknown_zzz_skipped():
    """SC-3: Unknown [zzz] is still skipped."""
    # Import a file with Unknown [zzz]
    # Confirm no Language row for code=zzz
    # Confirm no RecordLanguage row for code=zzz
```

```python
def test_french_mjy_skipped():
    """SC-4: French [mjy] does NOT create Language/RecordLanguage rows."""
    # Import a file with French [mjy]
    # Confirm no Language row is created for code=mjy (existing row untouched)
    # Confirm no RecordLanguage row for code=mjy
```

**RED baseline:** Run `uv run pytest test/test_upload_service/ -x -k test_mohican` — test MUST FAIL (Mohican != Mahican mismatch from `ref_name != lg_name` guard).

#### GREEN Phase (G6)

Modify `_update_record_languages()` in `src/services/upload_service.py`:

**Change 1:** Add `rapidfuzz` to dependencies (`pyproject.toml`).

**Change 2:** Line 1226 — replace `iso_entry.ref_name != lg_name` guard with Jaro-Winkler plausibility check.
```python
# Before:
if not iso_entry or iso_entry.ref_name != lg_name:
    continue

# After:
if not iso_entry:
    continue

if JaroWinkler.normalized_similarity(lg_name, iso_entry.ref_name) < 0.75:
    # Name doesn't plausibly match the code — don't create language association
    continue
```

**Change 3:** Line 1234 — use `iso_entry.ref_name` instead of `lg_name`.
```python
# Before:
lang = Language(name=lg_name, code=lg_code)

# After:
lang = Language(name=iso_entry.ref_name, code=lg_code)
```

#### REFACTOR Phase

- Run `uv run pytest test/test_upload_service/ -x` — all tests MUST PASS
- Run `uvx pyright src/services/upload_service.py` — no type errors
- Verify test coverage is adequate

---

### Verification Checklist

| SC | Assertion | Command |
|----|-----------|---------|
| SC-1 | Mohican [mjy] → Language(code=mjy, name="Mahican") | `uv run pytest test/ -x -k test_mohican_mjy` |
| SC-2 | English [eng] → RecordLanguage association created | `uv run pytest test/ -x -k test_english_eng` |
| SC-3 | Unknown [zzz] → no Language/RecordLanguage row | `uv run pytest test/ -x -k test_unknown_zzz` |
| SC-4 | French [mjy] → no Language/RecordLanguage row for mjy | `uv run pytest test/ -x -k test_french_mjy` |
| — | All tests pass (no regression) | `uv run pytest test/test_upload_service/ -x` |
| — | Type check passes | `uvx pyright src/services/upload_service.py` |
| — | Lint passes | `uvx ruff check src/services/upload_service.py` |
