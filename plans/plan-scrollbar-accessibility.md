# Plan: Fix CSS Scrollbar Accessibility

**Status:** ✅ Complete  
**Created:** 2026-03-11  
**Scope:** `src/frontend/ui_utils.py`

---

## Background

Streamlit's default scrollbar styling is nearly invisible, creating an accessibility issue. The fix adds standard `::-webkit-scrollbar` CSS (Chrome/Safari/Edge) and Firefox `scrollbar-width`/`scrollbar-color` properties to make scrollbars visible and usable.

---

## Steps

1. ✅ Added scrollbar CSS to `apply_standard_layout_css()` in `src/frontend/ui_utils.py`.
2. ✅ Lint verified — no errors.
3. ✅ Plan updated.
