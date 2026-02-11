# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from src.services.linguistic_service import LinguisticService
from src.logging_config import get_logger

logger = get_logger("snea.pages.table_maintenance")

def render_sources_maintenance():
    st.header("Sources Maintenance")
    
    # Load data
    sources = LinguisticService.get_sources_with_counts()
    
    if not sources:
        st.info("No sources found.")
        return

    # Table view
    st.subheader("Existing Sources")
    
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
            if action_cols[0].button("📝", key=f"edit_{source['id']}", help="Edit source details"):
                st.session_state[f"edit_source_{source['id']}"] = True
            
            # Reassign or Delete (Mutually Exclusive)
            if source["record_count"] > 0:
                # Reassign Button
                if action_cols[1].button("🔄", key=f"reassign_{source['id']}", help="Reassign records to another source"):
                    st.session_state[f"reassign_source_{source['id']}"] = True
            else:
                # Delete Button
                if action_cols[1].button("🗑️", key=f"delete_{source['id']}", help="Delete empty source"):
                    if LinguisticService.delete_source(source["id"]):
                        st.success(f"Deleted source: {source['name']}")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete source: {source['name']}")

            # Dialogs (conditional rendering)
            if st.session_state.get(f"edit_source_{source['id']}", False):
                render_edit_dialog(source)
            
            if st.session_state.get(f"reassign_source_{source['id']}", False):
                render_reassign_dialog(source, sources)

@st.dialog("Edit Source")
def render_edit_dialog(source):
    new_name = st.text_input("Name", value=source["name"])
    new_desc = st.text_area("Description", value=source["description"] or "")
    
    col1, col2 = st.columns(2)
    if col1.button("Save Changes", use_container_width=True):
        if LinguisticService.update_source(source["id"], name=new_name, description=new_desc):
            st.success("Source updated successfully!")
            del st.session_state[f"edit_source_{source['id']}"]
            st.rerun()
        else:
            st.error("Failed to update source.")
            
    if col2.button("Cancel", use_container_width=True):
        del st.session_state[f"edit_source_{source['id']}"]
        st.rerun()

@st.dialog("Reassign Records")
def render_reassign_dialog(source, all_sources):
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
                st.error("Reassignment failed.")
                
        if col2.button("Cancel", use_container_width=True):
            del st.session_state[f"reassign_source_{source['id']}"]
            st.rerun()

def main():
    st.title("Table Maintenance")
    
    # Internal Sidebar Navigation for extensibility
    st.sidebar.title("Maintenance Tables")
    table_option = st.sidebar.radio(
        "Select a table to maintain:",
        ["Sources"],
        index=0
    )
    
    if table_option == "Sources":
        render_sources_maintenance()
    else:
        st.info(f"Maintenance for {table_option} is not yet implemented.")

if __name__ == "__main__":
    main()
