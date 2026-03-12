# Plan: Archive Completed Plans (2026-03-11)

**Status:** ✅ Complete  
**Created:** 2026-03-11  
**Scope:** `plans/` — move completed plans to `plans/archive/`

---

## Summary of Findings

Each active plan was checked against production code. Results:

| Plan | Status | Evidence |
|------|--------|----------|
| `plan-fix-rows-per-page-reset.md` | ✅ Complete | All 4 steps marked ✔️; `key="review_page_size_widget"` present, single occurrence in production |
| `plan-ignore-jetbrains-default-system-prompt.md` | ✅ Complete | Both steps marked ✅ Done; directive present at top of `guidelines.md` |
| `plan-match-review-page-bulk-actions.md` | ✅ Complete | All 4 steps marked ✔️; `queue_ids` param and `page_bulk_*` buttons confirmed in production |
| `plan-hide-streamlit-toolbar.md` | ✅ Superseded | Called for `display: none`; production uses hover-show approach (later plans replaced this) |
| `plan-scrollbar-accessibility.md` | ✅ Superseded | Called for always-visible scrollbars; replaced by remove + hover-only approach |
| `plan-fix-scrollbar-hover-disappear.md` | ✅ Superseded | Called for `opacity: 1` on thumb; entire scrollbar block was later removed and replaced |
| `plan-remove-scrollbar-css.md` | ✅ Complete | CSS block it described removing is gone from production; hover-only CSS is in place |
| `plan-toolbar-right-margin.md` | ✅ Complete | `right: 14px !important` and `pointer-events` rules confirmed in production |
| `plan-bottom-bulk-buttons-layout.md` | ❌ Incomplete | `use_container_width=True` still present on all bottom bulk buttons (lines 1005–1035); no status markers |
| `plan-remove-redundant-labels.md` | ❌ Incomplete | Explicitly marked 🔄 Pending; all 4 target `st.markdown` labels still in production |

---

## Steps

### Phase 1 — Archive completed/superseded plans (no code changes)

1. ✅ Moved to `plans/archive/`:
   - `plan-fix-rows-per-page-reset.md`
   - `plan-ignore-jetbrains-default-system-prompt.md`
   - `plan-match-review-page-bulk-actions.md`
   - `plan-hide-streamlit-toolbar.md`
   - `plan-scrollbar-accessibility.md`
   - `plan-fix-scrollbar-hover-disappear.md`
   - `plan-remove-scrollbar-css.md`
   - `plan-toolbar-right-margin.md`

### Phase 2 — Leave in place (incomplete)

- `plan-bottom-bulk-buttons-layout.md` — remains active; work not done
- `plan-remove-redundant-labels.md` — remains active; explicitly pending

---

## Notes

- `plan_standards.md` and `TODO.md` are not plans to archive — they are standing reference files.
- Superseded plans are archived (not deleted) per project convention.
