# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
import datetime as _dt
import json
import zipfile
import io
from typing import List, Dict, Any, Optional
from src.services.linguistic_service import LinguisticService
from src.services.upload_service import UploadService
from src.services.identity_service import IdentityService
from src.services.preference_service import PreferenceService
from src.frontend.ui_utils import render_mdf_block, apply_standard_layout_css, hide_sidebar_nav, handle_ui_error
from src.mdf.validator import MDFValidator
from src.logging_config import get_logger

logger = get_logger("snea.pages.records")

def records():
    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()
    apply_standard_layout_css()
    
    user_email = st.session_state.get("user_email")
    user_role = st.session_state.get("user_role", "viewer")
    
    # DEBUG: Show user role to verify access
    # st.sidebar.info(f"DEBUG: Role={user_role}")
    
    # --- 1. Load Initial State from Preferences ---
    # Load persistence preferences
    if user_email:
        if "page_size" not in st.session_state:
            saved_size = PreferenceService.get_preference(user_email, "records", "page_size", "25")
            st.session_state.page_size = int(saved_size)
        
        if "structural_highlighting" not in st.session_state:
            saved_hl = PreferenceService.get_preference(user_email, "records", "structural_highlighting", "True")
            st.session_state.structural_highlighting = saved_hl == "True"
    
    # Defaults if still missing
    if "page_size" not in st.session_state:
        st.session_state.page_size = 25
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_mode" not in st.session_state:
        st.session_state.search_mode = "Lexeme"
    if "selected_source_id" not in st.session_state:
        st.session_state.selected_source_id = "All"
    if "global_edit_mode" not in st.session_state:
        st.session_state.global_edit_mode = False
    if "pending_edits" not in st.session_state:
        st.session_state.pending_edits = {}
    if "local_edits" not in st.session_state:
        st.session_state.local_edits = set()
    if "view_selection_only" not in st.session_state:
        st.session_state.view_selection_only = False
    if "structural_highlighting" not in st.session_state:
        st.session_state.structural_highlighting = True
    if "confirm_delete_id" not in st.session_state:
        st.session_state.confirm_delete_id = None
    if "selection" not in st.session_state:
        # Try to load selection from persistence
        st.session_state.selection = []
        if user_email:
            selection_json = PreferenceService.get_preference(user_email, "global", "selection_contents", "[]")
            try:
                selection_ids = json.loads(selection_json)
                if selection_ids:
                    loaded_records = []
                    for rid in selection_ids:
                        rec = LinguisticService.get_record(rid)
                        if rec:
                            loaded_records.append(rec)
                    st.session_state.selection = loaded_records
            except Exception as e:
                handle_ui_error(e, f"Failed to load selection for {user_email}", logger_name="snea.pages.records")

    def on_search_change():
        st.session_state.search_query = st.session_state.search_query_input
        st.session_state.current_page = 1

    def on_mode_change():
        st.session_state.search_mode = st.session_state.search_mode_radio
        st.session_state.current_page = 1

    def on_source_change():
        sources = LinguisticService.get_sources_with_counts()
        source_id_map = {s['name']: s['id'] for s in sources}
        selected_name = st.session_state.source_select
        st.session_state.selected_source_id = source_id_map.get(selected_name, "All")
        st.session_state.current_page = 1

    # --- 2. Calculate Search Results (Pre-calculate for Header Count) ---
    source_filter_id = None if st.session_state.selected_source_id == "All" else int(st.session_state.selected_source_id)
    search_term = st.session_state.search_query if st.session_state.search_query else None
    
    # Fetch records for current page
    limit = st.session_state.page_size
    offset = (st.session_state.current_page - 1) * limit
    
    selection_record_ids = [r['id'] for r in st.session_state.selection] if st.session_state.view_selection_only else None
    
    search_result = LinguisticService.search_records(
        source_id=source_filter_id,
        search_term=search_term,
        search_mode=st.session_state.search_mode,
        record_ids=selection_record_ids,
        limit=limit,
        offset=offset
    )
    
    records_batch = search_result.records
    total_count = search_result.total_count
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    # Ensure current page is within bounds
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = max(1, total_pages)
        st.rerun()

    has_next = st.session_state.current_page < total_pages

    # --- 3. Sidebar: Filters & Navigation ---
    with st.sidebar:
        # Compact Search Controls
        st.html("""
            <style>
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
                gap: 0.5rem !important;
            }
            </style>
        """)
        
        header_text = f"Search ({total_count} records)" if search_term else "Search"
        if st.session_state.view_selection_only:
            header_text = f"Selection Contents ({total_count} records)"
        st.markdown(f"**{header_text}**")
        
        search_query = st.text_input("Enter text...", value=st.session_state.search_query, 
                                    key="search_query_input", label_visibility="collapsed",
                                    on_change=on_search_change)

        # Lexeme/FTS + Search/Clear Buttons on one line
        c_mode, c_s, c_c = st.columns([0.7, 0.15, 0.15])
        with c_mode:
            st.radio("Search Mode", ["Lexeme", "FTS"], 
                                   index=["Lexeme", "FTS"].index(st.session_state.search_mode), 
                                   horizontal=True, key="search_mode_radio", label_visibility="collapsed",
                                   on_change=on_mode_change)
        with c_s:
            if st.button("", icon="🔍", key="search_trigger", help="Execute Search", use_container_width=True):
                on_search_change()
                st.rerun()
        with c_c:
            if st.button("", icon="❌", key="search_clear", help="Clear Search", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.current_page = 1
                st.rerun()

        sources = LinguisticService.get_sources_with_counts()
        source_options = ["All"] + [s['name'] for s in sources]
        source_name_map = {str(s['id']): s['name'] for s in sources}
        source_name_map["All"] = "All"

        current_source_name = source_name_map.get(str(st.session_state.selected_source_id), "All")
        st.selectbox("Select Source", source_options, 
                                            index=source_options.index(current_source_name), 
                                            key="source_select",
                                            label_visibility="collapsed",
                                            on_change=on_source_change)

        st.markdown("**Pagination**")
        
        c1, c2 = st.columns(2)
        if c1.button("Prev", icon="◀️", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            if st.session_state.global_edit_mode and st.session_state.pending_edits:
                for rid, mdf in st.session_state.pending_edits.items():
                    LinguisticService.update_record(
                        record_id=rid,
                        user_email=user_email,
                        mdf_data=mdf,
                        change_summary="Auto-save via pagination"
                    )
                st.session_state.pending_edits = {}
            st.session_state.current_page -= 1
            st.rerun()
        if c2.button("Next", icon="▶️", disabled=not has_next, use_container_width=True):
            if st.session_state.global_edit_mode and st.session_state.pending_edits:
                for rid, mdf in st.session_state.pending_edits.items():
                    LinguisticService.update_record(
                        record_id=rid,
                        user_email=user_email,
                        mdf_data=mdf,
                        change_summary="Auto-save via pagination"
                    )
                st.session_state.pending_edits = {}
            st.session_state.current_page += 1
            st.rerun()
            
        st.markdown(f"<p style='text-align: center; margin-bottom: 0;'>Page {st.session_state.current_page} of {total_pages}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 0.8em; color: gray;'>Showing {offset + 1}-{min(offset + len(records_batch), total_count)} of {total_count}</p>", unsafe_allow_html=True)
        
        new_page_size = st.selectbox("Results per page", [1, 5, 10, 25, 50, 100], 
                                     index=[1, 5, 10, 25, 50, 100].index(st.session_state.page_size))
        if new_page_size != st.session_state.page_size:
            st.session_state.page_size = new_page_size
            st.session_state.current_page = 1
            if user_email:
                PreferenceService.set_preference(user_email, "records", "page_size", str(new_page_size))
            st.rerun()

        # Moved Editing Controls here
        if user_role in ["editor", "admin"]:
            if not st.session_state.global_edit_mode:
                if st.button("Enter Edit Mode", icon="📝", use_container_width=True):
                    st.session_state.global_edit_mode = True
                    st.rerun()
            else:
                col_e1, col_e2 = st.columns(2)
                if col_e1.button("Cancel All", icon="❌", use_container_width=True):
                    st.session_state.global_edit_mode = False
                    st.session_state.pending_edits = {}
                    st.rerun()
                if col_e2.button("Save All", icon="💾", type="primary", use_container_width=True):
                    for rid, mdf in st.session_state.pending_edits.items():
                        LinguisticService.update_record(
                            record_id=rid,
                            user_email=user_email,
                            mdf_data=mdf,
                            change_summary="Bulk update via global edit mode"
                        )
                    st.session_state.pending_edits = {}
                    st.session_state.global_edit_mode = False
                    st.success("All changes saved!")
                    st.rerun()
        else:
            st.info("View-only mode (Editor access required)")

        st.divider()
        st.markdown("**Preferences**")
        structural_highlighting = st.toggle("Structural Highlighting", value=st.session_state.structural_highlighting)
        if structural_highlighting != st.session_state.structural_highlighting:
            st.session_state.structural_highlighting = structural_highlighting
            if user_email:
                PreferenceService.set_preference(user_email, "records", "structural_highlighting", str(structural_highlighting))
            st.rerun()

        st.divider()
        st.markdown(f"**My Selection** ({len(st.session_state.selection)} records)")
        
        selection_col1, selection_col2, selection_col3 = st.columns(3)
        
        view_icon = "📚" if st.session_state.view_selection_only else "🧺"
        view_help = "Show all records" if st.session_state.view_selection_only else "Filter list to show only selected items"
        if selection_col1.button("", icon=view_icon, use_container_width=True, help=view_help):
            st.session_state.view_selection_only = not st.session_state.view_selection_only
            st.session_state.current_page = 1
            st.rerun()

        if st.session_state.selection:
            # Generate MDF bundle text
            mdf_bundle = LinguisticService.bundle_records_to_mdf(st.session_state.selection)
            
            # Determine source name for filename
            sources = set(r.get('source_name') for r in st.session_state.selection if r.get('source_name'))
            source_name = list(sources)[0] if len(sources) == 1 else "mixed"
            
            github_username = IdentityService.get_github_username(st.session_state.get("user_email"))
            
            fname = UploadService.generate_mdf_filename(
                prefix="selection",
                source_name=source_name,
                timestamp=_dt.datetime.now(),
                github_username=github_username
            )

            selection_col2.download_button(
                label="📥",
                data=mdf_bundle,
                file_name=fname,
                mime="text/plain",
                use_container_width=True,
                help="Download selection as MDF"
            )
            
            if selection_col3.button("🗑️", use_container_width=True, help="Discard selection"):
                st.session_state.selection = []
                if user_email:
                    PreferenceService.set_preference(user_email, "global", "selection_contents", "[]")
                st.session_state.view_selection_only = False
                st.rerun()
        else:
            selection_col2.button("📥", disabled=True, use_container_width=True)
            selection_col3.button("🗑️", disabled=True, use_container_width=True)

        st.divider()
        
        # Determine what to export based on filters
        export_source_id = source_filter_id
        export_search_term = search_term
        export_record_ids = selection_record_ids
        
        # Prepare export data
        all_matching_records = LinguisticService.get_all_records_for_export(
            source_id=export_source_id,
            search_term=export_search_term,
            search_mode=st.session_state.search_mode,
            record_ids=export_record_ids
        )
        
        distinct_sources = sorted(list(set(r['source_name'] for r in all_matching_records if r.get('source_name'))))
        export_header = "Export All Sources" if len(distinct_sources) > 1 else "Export Source"
        st.markdown(f"**{export_header}**")
        
        if all_matching_records:
            github_username = IdentityService.get_github_username(user_email)
            
            if len(distinct_sources) > 1:
                # Multiple sources: Zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for src_name in distinct_sources:
                        src_records = [r for r in all_matching_records if r['source_name'] == src_name]
                        if not src_records:
                            continue
                            
                        mdf_content = LinguisticService.bundle_records_to_mdf(src_records)
                        
                        # Generate individual filename for the entry in zip
                        entry_fname = UploadService.generate_mdf_filename(
                            prefix="export",
                            source_name=src_name,
                            timestamp=_dt.datetime.now(),
                            github_username=github_username
                        )
                        zip_file.writestr(entry_fname, mdf_content)
                
                zip_filename = f"snea_export_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                
                st.download_button(
                    label="Download All (Zip)",
                    data=zip_buffer.getvalue(),
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True,
                    help=f"Download {len(all_matching_records)} records from {len(distinct_sources)} sources as a ZIP of MDF files"
                )
            else:
                # Single source: Direct MDF download via streaming to temp file
                source_name = distinct_sources[0] if distinct_sources else "results"
                
                fname = UploadService.generate_mdf_filename(
                    prefix="export",
                    source_name=source_name,
                    timestamp=_dt.datetime.now(),
                    github_username=github_username
                )

                # Use streaming to temp file for better memory management
                temp_path = LinguisticService.stream_records_to_temp_file(
                    source_id=export_source_id,
                    search_term=export_search_term,
                    search_mode=st.session_state.search_mode,
                    record_ids=export_record_ids
                )
                
                try:
                    with open(temp_path, "rb") as f:
                        file_bytes = f.read()
                        st.download_button(
                            label="Download Source (MDF)",
                            data=file_bytes,
                            file_name=fname,
                            mime="text/plain",
                            use_container_width=True,
                            help=f"Download {len(all_matching_records)} records from {source_name} as MDF (Streamed)"
                        )
                finally:
                    import os
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            st.button("Download (Empty)", disabled=True, use_container_width=True)

        st.divider()
        if st.button("Back to Main Menu", use_container_width=True):
            st.switch_page("pages/index.py")

    # --- 4. Main Panel: Records List ---
    if not records_batch:
        st.info("No records found matching your criteria.")
    else:
        for record in records_batch:
            record_id = record['id']
            mdf_data = record['mdf_data']
            mdf_lines = mdf_data.split('\n')
            
            with st.container(border=True):
                st.markdown(f"**Record #{record_id}** (Source: {record['source_name'] or 'Unknown'})")
                
                is_editing = st.session_state.global_edit_mode or record_id in st.session_state.local_edits
                
                if is_editing:
                    # Edit Mode: Record in text area
                    # Initialize pending_edits from record data if not present
                    initial_val = st.session_state.pending_edits.get(record_id, mdf_data)
                    
                    edited_mdf = st.text_area(
                        "Edit MDF", 
                        value=initial_val, 
                        height=300, 
                        key=f"edit_{record_id}",
                        label_visibility="collapsed"
                    )
                    
                    # Update pending_edits if it changed
                    if edited_mdf != initial_val:
                        st.session_state.pending_edits[record_id] = edited_mdf
                    
                    col_s1, col_s2, _ = st.columns([1, 1, 4])
                    if col_s1.button("Update", key=f"update_{record_id}", type="primary", use_container_width=True):
                        try:
                            summary = "Individual update" if not st.session_state.global_edit_mode else "Individual update in global edit mode"
                            success = LinguisticService.update_record(
                                record_id=record_id,
                                user_email=user_email,
                                mdf_data=edited_mdf,
                                change_summary=summary
                            )
                            if success:
                                if record_id in st.session_state.pending_edits:
                                    del st.session_state.pending_edits[record_id]
                                if record_id in st.session_state.local_edits:
                                    st.session_state.local_edits.remove(record_id)
                                st.success(f"Record #{record_id} saved.")
                                st.rerun()
                            else:
                                st.error(f"Failed to save Record #{record_id}.")
                        except Exception as e:
                            handle_ui_error(e, "Error saving record", logger_name="snea.pages.records")
                    
                    if not st.session_state.global_edit_mode:
                        if col_s2.button("Cancel", key=f"cancel_local_{record_id}", use_container_width=True):
                            if record_id in st.session_state.local_edits:
                                st.session_state.local_edits.remove(record_id)
                            if record_id in st.session_state.pending_edits:
                                del st.session_state.pending_edits[record_id]
                            st.rerun()
                    
                else:
                    # View Mode
                    diagnostics = None
                    if st.session_state.structural_highlighting:
                        diagnostics = MDFValidator.diagnose_record(mdf_lines)
                    
                    render_mdf_block(mdf_data, diagnostics=diagnostics, key=f"render_{record_id}")
                    
                    # Action Toolbar
                    toolbar_cols = [1, 1]
                    if user_role in ["editor", "admin"] and not st.session_state.global_edit_mode:
                        toolbar_cols.append(1)
                    
                    toolbar = st.columns(toolbar_cols)
                    
                    in_selection = record_id in [r['id'] for r in st.session_state.selection]
                    selection_label = "Remove from Selection" if in_selection else "Add to Selection"
                    selection_icon = "🧺" if not in_selection else "❌"
                    
                    if toolbar[0].button(selection_label, use_container_width=True, icon=selection_icon, key=f"selection_{record_id}"):
                        if not in_selection:
                            st.session_state.selection.append(record)
                            st.toast(f"Added Record #{record_id} to selection")
                        else:
                            st.session_state.selection = [r for r in st.session_state.selection if r['id'] != record_id]
                            st.toast(f"Removed Record #{record_id} from selection")
                        
                        if user_email:
                            selection_ids = [r['id'] for r in st.session_state.selection]
                            PreferenceService.set_preference(user_email, "global", "selection_contents", json.dumps(selection_ids))
                        st.rerun()
                    
                    if user_role in ["editor", "admin"]:
                        if st.session_state.confirm_delete_id == record_id:
                            st.warning("Confirm deletion?")
                            c_del1, c_del2, _ = st.columns([1, 1, 4])
                            if c_del1.button("Confirm", key=f"confirm_del_{record_id}", type="primary", use_container_width=True):
                                if LinguisticService.soft_delete_record(record_id, user_email):
                                    st.success(f"Record #{record_id} deleted.")
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                                else:
                                    handle_ui_error(Exception("Delete failed"), f"Failed to delete Record #{record_id}.", logger_name="snea.pages.records")
                            if c_del2.button("Cancel", key=f"cancel_del_{record_id}", use_container_width=True):
                                st.session_state.confirm_delete_id = None
                                st.rerun()
                        else:
                            if toolbar[1].button("Delete", use_container_width=True, icon="🗑️", key=f"del_{record_id}"):
                                st.session_state.confirm_delete_id = record_id
                                st.rerun()
                        
                        if not st.session_state.global_edit_mode:
                            if toolbar[2].button("Edit", use_container_width=True, icon="📝", key=f"edit_btn_{record_id}"):
                                st.session_state.local_edits.add(record_id)
                                st.rerun()

                # Revision History
                with st.expander("Revision History"):
                    history = LinguisticService.get_edit_history(record_id)
                    if not history:
                        st.info("No revision history available.")
                    else:
                        for entry in history:
                            st.markdown(f"**v{entry['version']}** - {entry['user_email']} at {entry['timestamp']}")
                            st.caption(f"Summary: {entry['change_summary']}")
                            if entry != history[-1]:
                                st.divider()

if __name__ == "__main__":
    records()
