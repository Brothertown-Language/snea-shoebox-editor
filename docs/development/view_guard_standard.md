<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# View Guard & Security Standard

This document defines the mandatory patterns for role-based access control (RBAC) and page protection within the SNEA Shoebox Editor.

## 1. Page-Level Role Guards

Every page that is restricted to specific roles (e.g., `admin`, `editor`) **MUST** implement an explicit role guard at the beginning of its main execution function (usually `main()` or the primary page function).

### The Standard Pattern

```python
def main():
    # Role guard — only authorized roles
    user_role = st.session_state.get("user_role")
    if user_role not in ("editor", "admin"):
        st.error("You do not have permission to access this page. Editor or admin role required.")
        return

    # ... rest of the page logic
```

### Role Definitions
- **`admin`**: Full access to all resources and administrative functions (e.g., `batch_rollback.py`).
- **`editor`**: Access to edit, update, and manage MDF records (e.g., `upload_mdf.py`, `table_maintenance.py`).
- **`viewer`**: Read-only access. May see search results and status, but never modification forms.

## 2. Conditional UI Modes (View vs. Edit)

For views that support both read-only and edit modes, use a single page that toggles UI components based on the `user_role` and an optional `edit_mode` state.

### The Standard Implementation

```python
# 1. Determine permission level
can_edit = user_role in ("editor", "admin")

# 2. Render Sidebar Toggle for Editors/Admins
if can_edit:
    st.sidebar.toggle("Enable Editing", key="edit_mode")

# 3. Logic to swap components
if st.session_state.get("edit_mode") and can_edit:
    # Render Edit UI (e.g., st.text_area for MDF)
    show_edit_form(record)
else:
    # Render View UI (e.g., render_mdf_block)
    render_mdf_block(record.mdf_data)
```

## 3. Defense-in-Depth Checklist

To ensure a page is fully secured, verify the following:

1.  **Navigation Guard**: Ensure the page is only added to the navigation tree for authorized roles in `src/services/navigation_service.py`.
2.  **Page Guard**: Implement the explicit `user_role` check at the top of the page file.
3.  **Service-Level Check**: For critical operations, re-verify permissions in the service layer before committing changes to the database.
4.  **Audit Trail**: Ensure all data-modifying service calls require and log the `user_email`.
