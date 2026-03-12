# Plan: Add Scrollbar Accessibility CSS

## Overview

Add webkit + Firefox scrollbar CSS to `apply_standard_layout_css()` in `src/frontend/ui_utils.py`
to make scrollbars always visible, thicker, and with accessible contrast.

---

## Affected Files

- `src/frontend/ui_utils.py` — insert scrollbar CSS block inside `apply_standard_layout_css()`

---

## Steps

### 1. Insert scrollbar CSS into `apply_standard_layout_css()`

In `src/frontend/ui_utils.py`, inside the `<style>` block in `apply_standard_layout_css()`
(before the closing `</style>` tag, after the existing rules), add:

```css
/* Make scrollbars always visible and thicker */
*::-webkit-scrollbar {
    width: 14px;
    height: 14px;
}

*::-webkit-scrollbar-track {
    background: #e0e0e0;
}

*::-webkit-scrollbar-thumb {
    background-color: #888;
    border-radius: 8px;
    border: 3px solid #e0e0e0;
}

*::-webkit-scrollbar-thumb:hover {
    background-color: #555;
}

/* Firefox */
* {
    scrollbar-width: auto;
    scrollbar-color: #888 #e0e0e0;
}
```

### 2. Verify lint clean

Run `uv run python -m py_compile src/frontend/ui_utils.py`
