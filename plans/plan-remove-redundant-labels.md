# Plan: Remove Redundant Section Labels from upload_mdf.py

**Status:** 🔄 Pending  
**Created:** 2026-03-11  
**Scope:** `src/frontend/pages/upload_mdf.py`

---

## Background

Four `st.markdown` section labels in the sidebar and main panel are redundant — they consume space without adding information the user doesn't already have from context. Removing them tightens the UI.

---

## Steps

1. 🔄 Delete line 408: `st.markdown("**Review Staged Entries**")` — sidebar header label, redundant with page context.
2. 🔄 Delete line 471: `st.markdown("**Filters**")` — sidebar filters label, redundant with the controls below it.
3. 🔄 Delete line 632: `st.markdown("**Bulk Actions**")` — sidebar bulk actions label, redundant with the buttons below it.
4. 🔄 Delete line 1004: `st.markdown("**Page Actions** — applies to displayed records only")` — bottom panel label, redundant with button labels.
5. 🔄 Lint verify — confirm no errors after deletions.
6. 🔄 Update this plan to reflect completion and archive.
