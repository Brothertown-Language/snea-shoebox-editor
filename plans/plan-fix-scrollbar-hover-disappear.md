# Plan: Fix Scrollbar Disappears on Hover (Match Review View)

## Overview

The right-hand scrollbar on the MDF record match review view is visible at rest but disappears
when moused over. This is caused by Streamlit's own CSS setting scrollbar opacity to 0 on hover
with higher specificity than our custom rules. The fix adds `opacity: 1 !important` to both the
base thumb rule and the hover rule in `apply_standard_layout_css()`.

---

## Affected Files

- `src/frontend/ui_utils.py` — update `::-webkit-scrollbar-thumb` and `::-webkit-scrollbar-thumb:hover` CSS rules

---

## Steps

### 1. Update scrollbar CSS in `apply_standard_layout_css()`

In `src/frontend/ui_utils.py`, lines 467–474, update the two thumb rules:

**Before:**
```css
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 8px;
    border: 3px solid #e0e0e0;
}
::-webkit-scrollbar-thumb:hover {
    background: #555;
}
```

**After:**
```css
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 8px;
    border: 3px solid #e0e0e0;
    opacity: 1 !important;
}
::-webkit-scrollbar-thumb:hover {
    background: #555;
    opacity: 1 !important;
}
```

### 2. Verify lint clean
