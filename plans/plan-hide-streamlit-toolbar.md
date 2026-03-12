# Plan: Hide Streamlit Top Toolbar

## Overview

The Streamlit top-right toolbar (Deploy + ⋯ menu) overlaps the scrollbar, making it inaccessible.
The toolbar is not used in this app. Fix: hide it via CSS in `apply_standard_layout_css()`.

## Affected Files

- `src/frontend/ui_utils.py` — add one CSS rule to the existing `<style>` block

## Steps

### 1. Add toolbar-hide CSS to `apply_standard_layout_css()`

Add inside the existing `<style>` block (after the `stStatusWidget` rule):

```css
/* Hide unused Streamlit top toolbar (Deploy / ⋯) — overlaps scrollbar */
header[data-testid="stHeader"] {
    display: none !important;
}
```

### 2. Verify lint clean

`uv run python -m py_compile src/frontend/ui_utils.py`
