# Plan: Fix Rows-Per-Page Reset on Next Navigation (MDF Upload Match View)

## Overview

**What:** When the user selects rows-per-page > 1 and then clicks Next, the view resets to rows-per-page = 1 and the page does not advance.

**Why:** There are two `st.selectbox` widgets for rows-per-page in `_render_review_table`:
- Line 505: inside the first `with st.sidebar:` block (lines 470–528), **no `key=`**. Streamlit assigns a positional key. On rerun (triggered by Next), Streamlit re-evaluates the widget positionally and may resolve it to index 0 (value `1`). The change-detection at line 506 then fires, sets `review_page_size = 1`, resets `review_current_page = 1` (implicitly via rerun before the Next increment is committed), and reruns again — clobbering the navigation.
- Line 669: inside a second `with st.sidebar:` block, has `key="review_page_size_widget"`. This widget is stable across reruns but its change-detection at line 676 also resets `review_current_page = 1`.

**Fix:** Add a stable `key=` to the widget at line 505 (e.g., `key="review_page_size_widget"`) and remove the duplicate widget block at lines 667–681. The first widget (now keyed) already handles preference persistence; the second is fully redundant.

## Steps

1. 🔄 Pending — Add `key="review_page_size_widget"` to the `st.selectbox` at line 505 in `_render_review_table`.
2. 🔄 Pending — Remove the duplicate rows-per-page block (lines 667–681: the `st.divider()`, comment, `st.selectbox`, and `if selected_page_size != ...` block) from the second `with st.sidebar:` block.
3. 🔄 Pending — Verify: confirm no remaining keyless rows-per-page widget exists; confirm the keyed widget at its new location correctly reads/writes `review_page_size` session state and persists to `PreferenceService`.
4. 🔄 Pending — Update this plan to reflect actual completion status.
