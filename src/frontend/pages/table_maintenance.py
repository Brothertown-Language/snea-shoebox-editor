# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st

def render_sources_maintenance():
    from src.services.linguistic_service import LinguisticService
    from src.frontend.ui_utils import handle_ui_error
    # Load data
    sources = LinguisticService.get_sources_with_counts()
    
    if not sources:
        st.info("No sources found.")
        return

    # Table view
    # Using a list of dicts for the table
    # We'll use streamlit columns to simulate a table with actions
    cols = st.columns([3, 4, 1, 2])
    cols[0].write("**Name**")
    cols[1].write("**Description**")
    cols[2].write("**Records**")
    cols[3].write("**Actions**")
    
    st.divider()
    
    for source in sources:
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 4, 1, 2])
            c1.write(source["name"])
            c2.write(source["description"] or "")
            c3.write(str(source["record_count"]))
            
            # Actions
            action_cols = c4.columns(2)
            
            # Edit Button
            if action_cols[0].button("", icon="📝", key=f"edit_{source['id']}", help="Edit source details"):
                st.session_state[f"edit_source_{source['id']}"] = True
            
            # Reassign or Delete (Mutually Exclusive)
            if source["record_count"] > 0:
                # Reassign Button
                if action_cols[1].button("", icon="🔄", key=f"reassign_{source['id']}", help="Reassign records to another source"):
                    st.session_state[f"reassign_source_{source['id']}"] = True
            else:
                # Delete Button
                if action_cols[1].button("", icon="🗑️", key=f"delete_{source['id']}", help="Delete empty source"):
                    if LinguisticService.delete_source(source["id"]):
                        st.success(f"Deleted source: {source['name']}")
                        st.rerun()
                    else:
                        handle_ui_error(Exception("Delete failed"), f"Failed to delete source: {source['name']}", logger_name="snea.pages.table_maintenance")

            # Dialogs (conditional rendering)
            if st.session_state.get(f"edit_source_{source['id']}", False):
                render_edit_dialog(source)
            
            if st.session_state.get(f"reassign_source_{source['id']}", False):
                render_reassign_dialog(source, sources)

@st.dialog("Edit Source")
def render_edit_dialog(source):
    from src.services.linguistic_service import LinguisticService
    from src.frontend.ui_utils import handle_ui_error
    new_name = st.text_input("Name", value=source["name"])
    new_desc = st.text_area("Description", value=source["description"] or "")
    
    col1, col2 = st.columns(2)
    if col1.button("Save Changes", use_container_width=True):
        if LinguisticService.update_source(source["id"], name=new_name, description=new_desc):
            st.success("Source updated successfully!")
            del st.session_state[f"edit_source_{source['id']}"]
            st.rerun()
        else:
            handle_ui_error(Exception("Update failed"), "Failed to update source.", logger_name="snea.pages.table_maintenance")
            
    if col2.button("Cancel", use_container_width=True):
        del st.session_state[f"edit_source_{source['id']}"]
        st.rerun()

@st.dialog("Reassign Records")
def render_reassign_dialog(source, all_sources):
    from src.services.linguistic_service import LinguisticService
    from src.frontend.ui_utils import handle_ui_error
    st.warning(f"This will move all {source['record_count']} records from '{source['name']}' to another source.")
    
    other_sources = [s for s in all_sources if s["id"] != source["id"]]
    target_source = st.selectbox(
        "Select target source",
        options=other_sources,
        format_func=lambda s: s["name"]
    )
    
    if target_source:
        st.info(f"Target: {target_source['name']}")
        
        col1, col2 = st.columns(2)
        if col1.button("Confirm Reassign", type="primary", use_container_width=True):
            count = LinguisticService.reassign_records(source["id"], target_source["id"])
            if count > 0:
                st.success(f"Successfully reassigned {count} records!")
                del st.session_state[f"reassign_source_{source['id']}"]
                st.rerun()
            else:
                handle_ui_error(Exception("Reassignment failed"), "Reassignment failed.", logger_name="snea.pages.table_maintenance")
                
        if col2.button("Cancel", use_container_width=True):
            del st.session_state[f"reassign_source_{source['id']}"]
            st.rerun()

def main():
    from src.frontend.ui_utils import hide_sidebar_nav, apply_standard_layout_css, render_back_to_main_button
    # Role guard — only admin
    user_role = st.session_state.get("user_role")
    if user_role != "admin":
        st.error("You do not have permission to access this page. Admin role required.")
        return

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    # Apply standard SNEA layout CSS
    apply_standard_layout_css()

    # ── Sidebar: header and controls ──────────────────────────────
    with st.sidebar:
        st.markdown("**Table Maintenance**")
        
        # Internal Sidebar Navigation for extensibility
        st.markdown("**Maintenance Tables**")
        table_option = st.radio(
            "Select a table to maintain:",
            ["Sources", "Soft Deleted Records"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        render_back_to_main_button()

    if table_option == "Sources":
        render_sources_maintenance()
    elif table_option == "Soft Deleted Records":
        render_deleted_records_maintenance()
    else:
        st.info(f"Maintenance for {table_option} is not yet implemented.")

def render_deleted_records_maintenance():
    from src.services.linguistic_service import LinguisticService
    from src.frontend.ui_utils import handle_ui_error
    # Load deleted records
    records = LinguisticService.get_deleted_records()
    
    if not records:
        st.info("No soft-deleted records found.")
        return

    # Table view
    cols = st.columns([1, 4, 3, 2])
    cols[0].write("**ID**")
    cols[1].write("**Headword (lx)**")
    cols[2].write("**Deleted By**")
    cols[3].write("**Actions**")
    
    st.divider()
    
    user_email = st.session_state.get("user_email")

    for record in records:
        with st.container():
            c1, c2, c3, c4 = st.columns([1, 4, 3, 2])
            c1.write(str(record["id"]))
            c2.write(record["lx"])
            c3.write(record["deleted_by"] or "Unknown")
            
            # Actions
            action_cols = c4.columns(2)
            
            # Restore Button
            if action_cols[0].button("", icon="↩️", key=f"restore_{record['id']}", help="Restore record"):
                if LinguisticService.restore_record(record["id"], user_email):
                    st.success(f"Restored record: {record['lx']}")
                    st.rerun()
                else:
                    handle_ui_error(Exception("Restore failed"), f"Failed to restore record: {record['lx']}", logger_name="snea.pages.table_maintenance")
            
            # Hard Delete Button
            if action_cols[1].button("", icon="🗑️", key=f"hard_delete_{record['id']}", help="Permanently delete record"):
                st.session_state[f"confirm_hard_delete_{record['id']}"] = True

            # Dialog for Hard Delete Confirmation
            if st.session_state.get(f"confirm_hard_delete_{record['id']}", False):
                render_hard_delete_dialog(record)

@st.dialog("Confirm Permanent Deletion")
def render_hard_delete_dialog(record):
    from src.services.linguistic_service import LinguisticService
    from src.frontend.ui_utils import handle_ui_error
    st.error(f"Are you sure you want to PERMANENTLY delete record #{record['id']} ({record['lx']})?")
    st.warning("This action cannot be undone and will remove all edit history for this record.")
    
    col1, col2 = st.columns(2)
    if col1.button("Yes, Delete Permanently", type="primary", use_container_width=True):
        if LinguisticService.hard_delete_record(record["id"]):
            st.success(f"Permanently deleted record #{record['id']}")
            del st.session_state[f"confirm_hard_delete_{record['id']}"]
            st.rerun()
        else:
            handle_ui_error(Exception("Delete failed"), f"Failed to delete record #{record['id']}", logger_name="snea.pages.table_maintenance")
            
    if col2.button("Cancel", use_container_width=True):
        del st.session_state[f"confirm_hard_delete_{record['id']}"]
        st.rerun()

if __name__ == "__main__":
    main()
