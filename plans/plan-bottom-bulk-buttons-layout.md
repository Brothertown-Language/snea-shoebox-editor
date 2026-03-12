# Plan: Bottom Bulk Buttons — Right-Justified Compact Layout

## Overview

The bottom "Page Actions" buttons currently use `use_container_width=True`, rendering each as a
full-width stacked block. They should appear as normal-sized buttons in a right-justified group.

## Affected Files

- `src/frontend/pages/upload_mdf.py` — bottom bulk action block (lines 1000–1030)

## Approach

Use `st.columns` to push buttons to the right. A spacer column on the left absorbs remaining
width; button columns on the right are sized to fit their labels naturally.

- `is_new_source` branch (1 action button + always-present Discard): `[4, 1, 1]`
- `else` branch (2 action buttons + Discard): `[3, 1, 1, 1]`
- Remove `use_container_width=True` from all buttons
- Widget keys unchanged

## Steps

### 1. Replace bottom bulk action block layout

### 2. Lint verify
