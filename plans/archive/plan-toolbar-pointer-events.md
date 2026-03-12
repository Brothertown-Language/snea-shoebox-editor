# Plan: Fix Toolbar Child pointer-events (Scrollbar Access)

**Status:** ✔️ Completed

## Overview

The Streamlit header's child elements override `pointer-events: none` set on the parent,
so the scrollbar at the top of the view is still blocked. Fix: add descendant selectors
to propagate `pointer-events: none` to all child elements when the toolbar is hidden,
and restore `pointer-events: auto` on hover.

## Affected Files

- `src/frontend/ui_utils.py` — add two descendant CSS rules to `apply_standard_layout_css()`

## Steps

### 1. 🔄 Add descendant pointer-events rules

In `apply_standard_layout_css()`, after the existing `:hover` rule, add:

```css
header[data-testid="stHeader"] * {
    pointer-events: none !important;
}
header[data-testid="stHeader"]:hover * {
    pointer-events: auto !important;
}
```

### 2. 🔄 Verify lint clean

`uv run python -m py_compile src/frontend/ui_utils.py`

### 3. 🔄 Verify completion and archive
