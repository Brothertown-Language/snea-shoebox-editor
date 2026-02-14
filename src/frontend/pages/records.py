# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from src.services.linguistic_service import LinguisticService
from src.services.preference_service import PreferenceService
from src.services.statistics_service import StatisticsService
from src.frontend.ui_utils import render_mdf_block
from src.mdf.validator import MDFValidator
from src.logging_config import get_logger

logger = get_logger("snea.pages.records")

def records():
    st.title("Records View")
    
    user_email = st.session_state.get("user_email")
    user_role = st.session_state.get("user_role", "viewer")
    
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
    if "edit_records" not in st.session_state:
        st.session_state.edit_records = set()
    if "cart" not in st.session_state:
        st.session_state.cart = []

    def update_url_params():
        st.query_params["search"] = st.session_state.search_query
        st.query_params["search_mode"] = st.session_state.search_mode
        st.query_params["source"] = str(st.session_state.selected_source_id)
        st.query_params["page"] = st.session_state.current_page
        st.query_params["page_size"] = st.session_state.page_size

    # --- 2. Sidebar: Filters & Navigation ---
    with st.sidebar:
        st.subheader("Search")
        search_query = st.text_input("Enter text...", value=st.session_state.search_query, key="search_query_input")
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        search_mode = st.radio("Search Mode", ["Lexeme", "FTS"], 
                               index=["Lexeme", "FTS"].index(st.session_state.search_mode), 
                               horizontal=True, key="search_mode_radio")
        if search_mode != st.session_state.search_mode:
            st.session_state.search_mode = search_mode
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        st.subheader("Source Collection")
        sources = LinguisticService.get_sources_with_counts()
        source_options = ["All"] + [s['name'] for s in sources]
        source_id_map = {s['name']: s['id'] for s in sources}
        source_name_map = {str(s['id']): s['name'] for s in sources}
        source_name_map["All"] = "All"

        current_source_name = source_name_map.get(str(st.session_state.selected_source_id), "All")
        selected_source_name = st.selectbox("Select Source", source_options, 
                                            index=source_options.index(current_source_name), 
                                            key="source_select")
        selected_source_id = source_id_map.get(selected_source_name, "All")
        if selected_source_id != st.session_state.selected_source_id:
            st.session_state.selected_source_id = selected_source_id
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

        st.divider()
        st.subheader("Pagination")
        
        # We need the count to render pagination correctly
        source_filter_id = None if st.session_state.selected_source_id == "All" else int(st.session_state.selected_source_id)
        
        # Search parameters
        search_term = st.session_state.search_query if st.session_state.search_query else None
        
        # Fetch records for current page
        limit = st.session_state.page_size
        offset = (st.session_state.current_page - 1) * limit
        
        # TODO: search_records currently doesn't return total count. 
        # For now, we'll fetch a larger set to estimate or just show Next if we got 'limit' records.
        # Ideally LinguisticService should return (records, total_count).
        # Temporary workaround: Use statistics or a separate count query if needed.
        # But searching makes count tricky.
        
        records_batch = LinguisticService.search_records(
            source_id=source_filter_id,
            search_term=search_term,
            limit=limit,
            offset=offset
        )
        
        has_next = len(records_batch) == limit
        
        c1, c2 = st.columns(2)
        if c1.button("◀ Prev", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            st.session_state.current_page -= 1
            update_url_params()
            st.rerun()
        if c2.button("Next ▶", disabled=not has_next, use_container_width=True):
            st.session_state.current_page += 1
            update_url_params()
            st.rerun()
            
        st.markdown(f"<p style='text-align: center; margin-bottom: 0;'>Page {st.session_state.current_page}</p>", unsafe_allow_html=True)
        
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
        st.subheader("Preferences")
        structural_highlighting = st.toggle("Structural Highlighting", value=st.session_state.structural_highlighting)
        if structural_highlighting != st.session_state.structural_highlighting:
            st.session_state.structural_highlighting = structural_highlighting
            if user_email:
                PreferenceService.set_preference(user_email, "records", "structural_highlighting", str(structural_highlighting))
            st.rerun()

        st.divider()
        st.subheader("Download Cart")
        st.write(f"**{len(st.session_state.cart)} records** tagged")
        if st.session_state.cart:
            if st.button("Download Bundle", use_container_width=True):
                st.info("Download logic not yet implemented (Production)")
            if st.button("Discard Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

    # --- 3. Main Panel: Records List ---
    if not records_batch:
        st.info("No records found matching your criteria.")
    else:
        for record in records_batch:
            record_id = record['id']
            mdf_data = record['mdf_data']
            mdf_lines = mdf_data.split('\n')
            
            with st.container(border=True):
                st.markdown(f"**Record #{record_id}** (Source: {record['source_name'] or 'Unknown'})")
                
                if record_id in st.session_state.edit_records:
                    # Edit Mode
                    edited_mdf = st.text_area("Edit MDF", value=mdf_data, height=300, key=f"edit_{record_id}")
                    col_s1, col_s2, _ = st.columns([1, 1, 4])
                    if col_s1.button("Save", key=f"save_{record_id}", type="primary"):
                        # TODO: Call LinguisticService.update_record
                        st.session_state.edit_records.remove(record_id)
                        st.success(f"Record #{record_id} saved (Stub)")
                        st.rerun()
                    if col_s2.button("Cancel", key=f"cancel_{record_id}"):
                        st.session_state.edit_records.remove(record_id)
                        st.rerun()
                else:
                    # View Mode
                    diagnostics = None
                    if st.session_state.structural_highlighting:
                        diagnostics = MDFValidator.diagnose_record(mdf_lines)
                    
                    render_mdf_block(mdf_data, diagnostics=diagnostics, key=f"render_{record_id}")
                    
                    # Action Toolbar
                    toolbar = st.columns([0.5, 0.5, 1, 1, 1, 0.5, 0.5])
                    
                    # Navigation (Mocking the relative indices within the current batch)
                    batch_idx = records_batch.index(record)
                    
                    if toolbar[0].button("◀", use_container_width=True, help="Previous Record", key=f"prev_{record_id}", disabled=(batch_idx == 0 and st.session_state.current_page == 1)):
                        # Simple logic: if in batch, just toast. If first in batch, would need to go back a page.
                        st.toast("Record navigation (Prev)")
                    
                    if toolbar[1].button("▶", use_container_width=True, help="Next Record", key=f"next_{record_id}", disabled=(batch_idx == len(records_batch)-1 and not has_next)):
                        st.toast("Record navigation (Next)")
                    
                    if toolbar[2].button("Copy Plain", use_container_width=True, key=f"cp_{record_id}"):
                        st.toast(f"Copied Record #{record_id}!")
                    
                    if toolbar[3].button("Copy Rich", use_container_width=True, key=f"cr_{record_id}"):
                        st.toast(f"Copied Record #{record_id} (Rich)!")
                        
                    if toolbar[4].button("Add to Cart", use_container_width=True, key=f"cart_{record_id}"):
                        if record_id not in [r['id'] for r in st.session_state.cart]:
                            st.session_state.cart.append(record)
                            st.toast(f"Added Record #{record_id} to cart")
                            st.rerun()
                        else:
                            st.toast(f"Record #{record_id} already in cart")
                    
                    if user_role in ["editor", "admin"]:
                        if toolbar[5].button("✎", use_container_width=True, help="Edit", key=f"edit_btn_{record_id}"):
                            st.session_state.edit_records.add(record_id)
                            st.rerun()
                        if toolbar[6].button("✖", use_container_width=True, help="Delete", key=f"del_{record_id}"):
                            st.warning("Delete not yet implemented")

                # Revision History
                with st.expander("Revision History"):
                    # TODO: Fetch from EditHistory
                    st.write("Fetch revision history for record...")

if __name__ == "__main__":
    records()
