# Plan: Codebase Audit — 2026-03-04

## Summary

Audit of active plans, TODO items, and source code as of 2026-03-04.

---

## 1. Active Plans Status

| Plan File | Title | Status |
|---|---|---|
| `plan_extend_existing_table_args.md` | Add `extend_existing=True` to All SQLAlchemy Model `__table_args__` | ✅ COMPLETE |
| `plan_fix_invalid_iso_lang_codes.md` | Fix Invalid ISO 639-3 Language Code References | ✅ DONE |
| `plan_identical_match_auto_discard.md` | Auto-Discard Identical Records During MDF Upload Match Phase | ✅ APPROVED |
| `plan_identical_match_discard_ordering.md` | Fix Identical-Match Records Not Being Auto-Discarded | ✅ IMPLEMENTED |
| `plan_language_id_per_line_scan.md` | Language Identification — Per-Line ISO 639 Pattern Scan | ✅ COMPLETE |
| `plan_rematch_progress_bar.md` | Re-Match Button — Progress Bar & UI Disable | ✅ COMPLETE |
| `remediation_mdf_ln_misuse.md` | Remediation of MDF `\ln` Tag Misuse | ✅ All sections complete |
| `plan_mdf_bundle_start_blank_lines.md` | Add Bundle Spacing to MDF Records | 🔲 PENDING APPROVAL |
| `plan_test_remediation_ln_to_so.md` | Test Remediation — `\ln` → `\so` Migration | ⏳ AWAITING APPROVAL |

### Recommended Actions
- Archive all ✅ complete plans to `plans/archived/`.
- `plan_mdf_bundle_start_blank_lines.md` and `plan_test_remediation_ln_to_so.md` remain active — no action until user approves.

---

## 2. TODO.md Audit

### Item 1 & 3: Exception capture + error dialog with Mastodon contact
**Finding**: Broadly implemented. `st.error()` is used throughout the codebase (30+ call sites). `src/frontend/ui_utils.py` provides a `show_error()` helper. `connection.py:init_db()` catches exceptions and shows `st.error()` with Mastodon contact info from secrets. One bare `except: pass` remains at `connection.py:372` (pgserver lock-file cleanup — intentional swallow, low risk).

**Verdict**: ✅ Substantially complete. The bare `except: pass` at line 372 is a minor code-quality issue (should be `except OSError: pass`), not a functional gap.

### Item 2: Logging to SQL table (round-robin)
**Finding**: `src/database/migrations.py` and `src/frontend/pages/table_maintenance.py` reference log-related patterns, but no dedicated round-robin SQL log table implementation was found. Standard Python `logging` is used (`_logger = logging.getLogger(...)`).

**Verdict**: ❌ NOT IMPLEMENTED. Requires a new plan.

### Item 4: SQL injection audit
**Finding**: One f-string inside `text()` at `connection.py:600`:
```python
text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table.name}), 1))")
```
Both `seq` and `table.name` are derived from SQLAlchemy `MetaData` introspection (not user input), so this is **not exploitable via user input**. No other raw-string query construction found in `src/`.

**Verdict**: ✅ No user-facing SQL injection risk. The one f-string query uses only internal metadata values. Recommend adding a comment to document this intentional pattern.

---

## 3. Recommended TODO.md Updates

- Items 1 & 3 (exception/error dialog): mark ✅ complete — 2026-03-04.
- Item 4 (SQL injection audit): mark ✅ complete — 2026-03-04 (no exploitable risk found).
- Item 2 (logging to SQL table): remains open; add note that a new plan is needed.
- Add new TODO: fix bare `except: pass` → `except OSError: pass` at `connection.py:372`.

---

## 4. Archive Candidates

The following completed plans should be moved to `plans/archived/`:
- `plan_extend_existing_table_args.md`
- `plan_fix_invalid_iso_lang_codes.md`
- `plan_identical_match_auto_discard.md`
- `plan_identical_match_discard_ordering.md`
- `plan_language_id_per_line_scan.md`
- `plan_rematch_progress_bar.md`
- `remediation_mdf_ln_misuse.md`

---

**Status**: 🔲 PENDING APPROVAL
