# Plan: Remove All Scrollbar CSS Overrides

## Overview

All previous scrollbar CSS overrides have failed to fix the accessibility issue.
Remove the entire scrollbar CSS block from `apply_standard_layout_css()` to start fresh.

---

## Affected Files

- `src/frontend/ui_utils.py` — delete scrollbar CSS block (lines ~458–482)

---

## Steps

### 1. Remove scrollbar CSS block

Delete the following block from `apply_standard_layout_css()`:

```css
/* Scrollbar accessibility — webkit (Chrome/Safari/Edge) */
::-webkit-scrollbar {
    width: 14px;
    height: 14px;
}
::-webkit-scrollbar-track {
    background: #e0e0e0;
    border-radius: 8px;
}
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

/* Scrollbar accessibility — Firefox */
* {
    scrollbar-width: auto;
    scrollbar-color: #888 #e0e0e0;
}
```

### 2. Verify lint clean
