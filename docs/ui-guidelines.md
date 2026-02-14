<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# SNEA UI Guidelines: Sidebar Navigation Pattern

This document dictates the standard UI pattern for all new views in the SNEA Shoebox Editor. All administrative and complex views must follow the pattern established by `upload_mdf.py` and `table_maintenance.py`.

## 1. Sidebar Navigation (The "SNEA Sidebar" Pattern)

To provide a focused workspace and consistent navigation, views must suppress default Streamlit navigation and implement a custom sidebar.

### Implementation Checklist:
- **[ ] Suppress Default Nav**: Call `hide_sidebar_nav()` (from `src.frontend.ui_utils`) at the very top of the main function.
- **[ ] Sidebar Header**: Use `with st.sidebar: st.header("Page Title")` to establish context.
- **[ ] Local Controls**: Move page-specific filters, selectors, and settings into the sidebar.
- **[ ] Back Navigation**: Provide a "Back to Home" or "Back to [Parent]" button at the bottom of the sidebar.
- **[ ] Default Spacing**: DO NOT override `.block-container` padding unless absolutely necessary for record comparison. Use default Streamlit spacing to avoid toolbar overlap.

## 2. Main Panel Optimization (Removal of Redundant Headers)

The main panel should be reserved for data and primary interactions.

### Rules:
- **NO Redundant Titles**: Do not use `st.title()` in the main panel if the title is already present in the sidebar header.
- **Minimize Vertical Waste**: Avoid large `st.header()` blocks for sub-sections if the sidebar state (e.g., radio button or selectbox) already identifies the active view. Use `st.subheader()` or bold text sparingly.
- **Consistent Components**: Use `st.status()` or `st.toast()` for feedback. Ensure `div[data-testid="stStatusWidget"]` has a `margin-bottom: 1rem !important;` style override to maintain spacing.

## 3. Role-Based Access (RBAC)

Every administrative page must start with a role guard.

```python
user_role = st.session_state.get("user_role")
if user_role not in ("editor", "admin"):
    st.error("You do not have permission to access this page. Editor or admin role required.")
    return
```
---
## 4. Validation and Feedback

All validation for linguistic data (MDF tags) must be advisory and non-blocking.
- **Advisory Labels**: Use "Suggestion" or "Note" instead of "Error" for structural MDF issues.
- **Non-blocking**: Validation state must not prevent the user from performing any action (e.g., exporting, navigating, or editing).
- **Remediation-focused**: Tooltips and feedback messages should explain the *suggested* best practice and how to achieve it, without implying the current state is "wrong" or "invalid".

## 5. Iconography and Visual Consistency

Visual elements must maintain strict consistency across all views and components.

### Rules:
- **Group Consistency**: When adding components to a group (e.g., a toolbar, a row of buttons, or a sidebar section), all items MUST match the established style.
    - If existing buttons use icons, new buttons in that group MUST use icons.
    - If existing buttons use labels, new buttons in that group MUST use labels.
    - If a hybrid approach is used (icon + label), maintain it across the group.
- **Icon Semantic Consistency**: Use standard emojis/icons consistently for the same actions across the entire application:
    - 🔍 Search
    - ❌ Clear/Cancel/Close
    - 📥 Download/Export
    - 🗑️ Delete/Discard
    - 📝 Edit/Write
    - 💾 Save
    - 🧺 Add to Selection / View Selection
    - 📚 Show All / Records
- **Mirror Existing Patterns**: Before implementing a new UI element, inspect the surrounding code and existing mocks to identify and replicate established visual patterns.

*Note: This pattern is mandatory for all new views created after February 2026.*
