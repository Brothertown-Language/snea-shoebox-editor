# Plan: Add Right Margin to Toolbar (Option 1 + Option 2)

## Overview

ADD `right: 14px !important` to the existing hover-to-show toolbar CSS block so the toolbar
does not overlap the scrollbar. The hover-to-show behavior is preserved; the toolbar is also
shifted left so the scrollbar remains accessible.

## Affected Files

- `src/frontend/ui_utils.py` — add `right: 14px !important` to existing toolbar CSS block

## Steps

### 1. Add `right` rule to existing toolbar CSS in `apply_standard_layout_css()`

**Before:**
```css
/* Toolbar: hidden by default, visible on hover */
header[data-testid="stHeader"] {
    opacity: 0 !important;
    transition: opacity 0.2s ease;
}
header[data-testid="stHeader"]:hover {
    opacity: 1 !important;
}
```

**After:**
```css
/* Toolbar: hidden by default, visible on hover; shifted left to avoid scrollbar */
header[data-testid="stHeader"] {
    opacity: 0 !important;
    transition: opacity 0.2s ease;
    right: 14px !important;
}
header[data-testid="stHeader"]:hover {
    opacity: 1 !important;
}
```

### 2. Verify lint clean

`uv run python -m py_compile src/frontend/ui_utils.py`
