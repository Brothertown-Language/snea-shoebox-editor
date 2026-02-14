# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from src.services.linguistic_service import LinguisticService
from src.services.preference_service import PreferenceService
from src.frontend.ui_utils import render_mdf_block, apply_standard_layout_css, hide_sidebar_nav
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
    
    # --- 1. Load Initial State from URL / Preferences ---
    query_params = st.query_params
    
    # Sync search from URL
    if "search" in query_params:
        st.session_state.search_query = query_params["search"]
    if "search_mode" in query_params:
        st.session_state.search_mode = query_params["search_mode"]
    if "source" in query_params:
        st.session_state.selected_source_id = query_params["source"]
    if "page" in query_params:
        try:
            st.session_state.current_page = int(query_params["page"])
        except ValueError:
            pass
    
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
    if "cart" not in st.session_state:
        st.session_state.cart = []

    def update_url_params():
        st.query_params["search"] = st.session_state.search_query
        st.query_params["search_mode"] = st.session_state.search_mode
        st.query_params["source"] = str(st.session_state.selected_source_id)
        st.query_params["page"] = st.session_state.current_page
        st.query_params["page_size"] = st.session_state.page_size

    # --- 2. Calculate Search Results (Pre-calculate for Header Count) ---
    source_filter_id = None if st.session_state.selected_source_id == "All" else int(st.session_state.selected_source_id)
    search_term = st.session_state.search_query if st.session_state.search_query else None
    
    # Fetch records for current page
    limit = st.session_state.page_size
    offset = (st.session_state.current_page - 1) * limit
    
    search_result = LinguisticService.search_records(
        source_id=source_filter_id,
        search_term=search_term,
        search_mode=st.session_state.search_mode,
        limit=limit,
        offset=offset
    )
    
    records_batch = search_result.records
    total_count = search_result.total_count
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    # Ensure current page is within bounds
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = max(1, total_pages)
        update_url_params()
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
            [data-testid="stSidebar"] .stButton > button {
                padding-left: 0;
                padding-right: 0;
            }
            </style>
        """)
        
        header_text = f"Search ({total_count} records)" if search_term else "Search"
        st.markdown(f"**{header_text}**")
        
        c_in, c_s, c_c = st.columns([0.7, 0.15, 0.15])
        with c_in:
            search_query = st.text_input("Enter text...", value=st.session_state.search_query, 
                                        key="search_query_input", label_visibility="collapsed")
        with c_s:
            if st.button("🔍", key="search_trigger", help="Execute Search", use_container_width=True):
                if search_query != st.session_state.search_query:
                    st.session_state.search_query = search_query
                    st.session_state.current_page = 1
                    update_url_params()
                    st.rerun()
        with c_c:
            if st.button("❌", key="search_clear", help="Clear Search", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.current_page = 1
                update_url_params()
                st.rerun()

        # Handle Enter key in text_input
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        search_mode = st.radio("Search Mode", ["Lexeme", "FTS"], 
                               index=["Lexeme", "FTS"].index(st.session_state.search_mode), 
                               horizontal=True, key="search_mode_radio", label_visibility="collapsed")
        if search_mode != st.session_state.search_mode:
            st.session_state.search_mode = search_mode
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        sources = LinguisticService.get_sources_with_counts()
        source_options = ["All"] + [s['name'] for s in sources]
        source_id_map = {s['name']: s['id'] for s in sources}
        source_name_map = {str(s['id']): s['name'] for s in sources}
        source_name_map["All"] = "All"

        current_source_name = source_name_map.get(str(st.session_state.selected_source_id), "All")
        selected_source_name = st.selectbox("Select Source", source_options, 
                                            index=source_options.index(current_source_name), 
                                            key="source_select",
                                            label_visibility="collapsed")
        selected_source_id = source_id_map.get(selected_source_name, "All")
        if selected_source_id != st.session_state.selected_source_id:
            st.session_state.selected_source_id = selected_source_id
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        st.divider()
        st.markdown("**Editing**")
        if user_role in ["editor", "admin"]:
            if not st.session_state.global_edit_mode:
                if st.button("📝 Enter Edit Mode", use_container_width=True):
                    st.session_state.global_edit_mode = True
                    st.rerun()
            else:
                col_e1, col_e2 = st.columns(2)
                if col_e1.button("❌ Cancel All", use_container_width=True):
                    st.session_state.global_edit_mode = False
                    st.session_state.pending_edits = {}
                    st.rerun()
                if col_e2.button("💾 Save All", type="primary", use_container_width=True):
                    # Save all pending edits
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
        st.markdown("**Pagination**")
        
        c1, c2 = st.columns(2)
        if c1.button("◀ Prev", disabled=(st.session_state.current_page <= 1), use_container_width=True):
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
            update_url_params()
            st.rerun()
        if c2.button("Next ▶", disabled=not has_next, use_container_width=True):
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
            update_url_params()
            st.rerun()
            
        st.markdown(f"<p style='text-align: center; margin-bottom: 0;'>Page {st.session_state.current_page} of {total_pages}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 0.8em; color: gray;'>Showing {offset + 1}-{min(offset + len(records_batch), total_count)} of {total_count}</p>", unsafe_allow_html=True)
        
        new_page_size = st.selectbox("Results per page", [10, 25, 50, 100], 
                                     index=[10, 25, 50, 100].index(st.session_state.page_size))
        if new_page_size != st.session_state.page_size:
            st.session_state.page_size = new_page_size
            st.session_state.current_page = 1
            if user_email:
                PreferenceService.set_preference(user_email, "records", "page_size", str(new_page_size))
            update_url_params()
            st.rerun()

        st.divider()
        st.markdown("**Preferences**")
        structural_highlighting = st.toggle("Structural Highlighting", value=st.session_state.structural_highlighting)
        if structural_highlighting != st.session_state.structural_highlighting:
            st.session_state.structural_highlighting = structural_highlighting
            if user_email:
                PreferenceService.set_preference(user_email, "records", "structural_highlighting", str(structural_highlighting))
            st.rerun()

        st.divider()
        st.markdown("**Download Cart**")
        st.write(f"**{len(st.session_state.cart)} records** tagged")
        if st.session_state.cart:
            # Generate MDF bundle text
            mdf_bundle = LinguisticService.bundle_records_to_mdf(st.session_state.cart)
            
            st.download_button(
                label="📥 Download Bundle",
                data=mdf_bundle,
                file_name=f"snea_bundle_{len(st.session_state.cart)}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            if st.button("Discard Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

        st.divider()
        if st.button("Back to Home", use_container_width=True):
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
                
                if st.session_state.global_edit_mode:
                    # Global Edit Mode: All records in text areas
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
                    
                    col_s1, _ = st.columns([1, 5])
                    if col_s1.button("Update", key=f"update_{record_id}", type="primary", use_container_width=True):
                        try:
                            success = LinguisticService.update_record(
                                record_id=record_id,
                                user_email=user_email,
                                mdf_data=edited_mdf,
                                change_summary="Individual update in global edit mode"
                            )
                            if success:
                                if record_id in st.session_state.pending_edits:
                                    del st.session_state.pending_edits[record_id]
                                st.success(f"Record #{record_id} saved.")
                                st.rerun()
                            else:
                                st.error(f"Failed to save Record #{record_id}.")
                        except Exception as e:
                            st.error(f"Error saving record: {e}")
                    
                elif st.session_state.global_edit_mode is False:
                    # View Mode
                    diagnostics = None
                    if st.session_state.structural_highlighting:
                        diagnostics = MDFValidator.diagnose_record(mdf_lines)
                    
                    render_mdf_block(mdf_data, diagnostics=diagnostics, key=f"render_{record_id}")
                    
                    # Action Toolbar
                    toolbar = st.columns([1, 1, 1, 1])
                    
                    if toolbar[0].button("Copy Plain", use_container_width=True, key=f"cp_{record_id}"):
                        # Copy plain text to clipboard via JS injection
                        import html as _html
                        escaped_mdf = _html.escape(mdf_data).replace("`", "\\`").replace("$", "\\$")
                        st.components.v1.html(f"""
                            <script>
                            const text = `{escaped_mdf}`;
                            navigator.clipboard.writeText(text).then(() => {{
                                window.parent.postMessage({{type: 'streamlit:message', message: 'Copied Record #{record_id} to clipboard!'}}, '*');
                            }});
                            </script>
                        """, height=0)
                        st.toast(f"Copied Record #{record_id}!")
                    
                    if toolbar[1].button("Copy Rich", use_container_width=True, key=f"cr_{record_id}"):
                        # Copy rich text (HTML) to clipboard via JS injection
                        from src.frontend.ui_utils import get_mdf_rich_html
                        rich_html = get_mdf_rich_html(mdf_data)
                        escaped_html = rich_html.replace("`", "\\`").replace("$", "\\$")
                        
                        st.components.v1.html(f"""
                            <script>
                            const html = `{escaped_html}`;
                            const type = "text/html";
                            const blob = new Blob([html], {{ type }});
                            const data = [new ClipboardItem({{ [type]: blob }})];
                            navigator.clipboard.write(data).then(() => {{
                                window.parent.postMessage({{type: 'streamlit:message', message: 'Copied Record #{record_id} (Rich) to clipboard!'}}, '*');
                            }});
                            </script>
                        """, height=0)
                        st.toast(f"Copied Record #{record_id} (Rich)!")
                        
                    if toolbar[2].button("Add to Cart", use_container_width=True, key=f"cart_{record_id}"):
                        if record_id not in [r['id'] for r in st.session_state.cart]:
                            st.session_state.cart.append(record)
                            st.toast(f"Added Record #{record_id} to cart")
                            st.rerun()
                        else:
                            st.toast(f"Record #{record_id} already in cart")
                    
                    if user_role in ["editor", "admin"]:
                        if toolbar[3].button("Delete", use_container_width=True, icon="🗑️", key=f"del_{record_id}"):
                            if LinguisticService.soft_delete_record(record_id, user_email):
                                st.success(f"Record #{record_id} deleted.")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete Record #{record_id}.")

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
