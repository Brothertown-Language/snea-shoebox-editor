# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
from src.frontend.ui_utils import render_mdf_block
from src.mdf.validator import MDFValidator

# --- MOCK DATA ---
MOCK_SOURCES = ["All Sources", "Mohegan", "Natick", "SNEA-General"]
MOCK_RECORDS = [
    {
        "id": 1,
        "source": "Mohegan",
        "mdf": "\\lx example\n\\ps n\n\\ge translation\n\\inf examples"
    },
    {
        "id": 2,
        "source": "Natick",
        "mdf": "\\lx second\n\\ps v\n\\ge to follow"
    },
    {
        "id": 3,
        "source": "Mohegan",
        "mdf": "\\ps out-of-order\n\\lx broken\n\\ge check validation"
    },
    {
        "id": 4,
        "source": "SNEA-General",
        "mdf": "\\lx incomplete\n\\ps n"
    }
]

# --- SESSION STATE ---
if "record_index" not in st.session_state:
    st.session_state.record_index = 0
if "cart" not in st.session_state:
    st.session_state.cart = []
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Editor"
if "structural_highlighting" not in st.session_state:
    st.session_state.structural_highlighting = True

# --- SIDEBAR ---
with st.sidebar:
    st.title("Records (Mock)")
    
    # 1. Search
    st.subheader("Search")
    search_query = st.text_input("Enter text...", key="search_query")
    search_mode = st.radio("Search Mode", ["Lexeme", "FTS"], horizontal=True)
    
    # 2. Source Selection
    st.subheader("Source Collection")
    selected_source = st.selectbox("Select Source", MOCK_SOURCES)
    
    # Filter Records
    filtered_records = MOCK_RECORDS
    if selected_source != "All Sources":
        filtered_records = [r for r in filtered_records if r["source"] == selected_source]
    if search_query:
        # Simple mock search logic
        if search_mode == "Lexeme":
            filtered_records = [r for r in filtered_records if search_query.lower() in r["mdf"].split('\n')[0].lower()]
        else:
            filtered_records = [r for r in filtered_records if search_query.lower() in r["mdf"].lower()]

    # Bounds check
    if st.session_state.record_index >= len(filtered_records):
        st.session_state.record_index = 0
        
    st.divider()
    
    # 5. Download Cart
    st.subheader("Download Cart")
    cart_container = st.container(border=True)
    with cart_container:
        st.write(f"**{len(st.session_state.cart)} records** tagged")
        sources_in_cart = set(r["source"] for r in st.session_state.cart)
        if len(sources_in_cart) > 1:
            st.info("Bundle: ZIP archive")
        
        c1, c2 = st.columns(2)
        if c1.button("Download", use_container_width=True, type="primary"):
            st.success("Downloading...")
        if c2.button("Discard", use_container_width=True):
            st.session_state.cart = []
            st.rerun()

    st.divider()
    st.session_state.user_role = st.selectbox("Role Simulation", ["Viewer", "Editor"])

# --- MAIN PANEL ---
st.header("Record View")

if not filtered_records:
    st.warning("No records found matching filters.")
else:
    current_record = filtered_records[st.session_state.record_index]
    
    if st.session_state.edit_mode:
        # EDIT MODE
        st.subheader(f"Editing Record #{current_record['id']} [{current_record['source']}]")
        edited_mdf = st.text_area("MDF Editor", value=current_record["mdf"], height=300)
        
        c1, c2 = st.columns([1, 4])
        if c1.button("Save", type="primary"):
            # Update the mock data in session (for this run)
            for r in MOCK_RECORDS:
                if r["id"] == current_record["id"]:
                    r["mdf"] = edited_mdf
            st.session_state.edit_mode = False
            st.success("Saved!")
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.edit_mode = False
            st.rerun()
            
    else:
        # VIEW MODE
        st.subheader(f"Record #{current_record['id']} [{current_record['source']}]")
        
        # Diagnostics
        mdf_lines = current_record["mdf"].split('\n')
        diagnostics = None
        if st.session_state.structural_highlighting:
            diagnostics = MDFValidator.diagnose_record(mdf_lines)
        
        render_mdf_block(current_record["mdf"], diagnostics=diagnostics)
        
        # Navigation
        st.subheader("Navigation")
        nav_cols = st.columns([1, 1, 2])
        if nav_cols[0].button("Prev", use_container_width=True):
            st.session_state.record_index = max(0, st.session_state.record_index - 1)
        if nav_cols[1].button("Next", use_container_width=True):
            st.session_state.record_index = min(len(filtered_records) - 1, st.session_state.record_index + 1)
        
        # Copy Buttons
        copy_cols = st.columns([1, 1, 2])
        if copy_cols[0].button("Copy Plain", use_container_width=True):
            st.write(f'<script>navigator.clipboard.writeText(`{current_record["mdf"]}`);</script>', unsafe_allow_html=True)
            st.toast("Copied plain text!")
        if copy_cols[1].button("Copy Rich", use_container_width=True):
            st.toast("Copied rich text (Mock: with highlighting)!")
        
        st.divider()

        # Action Buttons
        cols = st.columns([1.5, 1, 1, 1])
        if cols[0].button("Add to Cart", use_container_width=True):
            if current_record not in st.session_state.cart:
                st.session_state.cart.append(current_record)
                st.toast("Added to cart!")
                st.rerun()
            else:
                st.toast("Already in cart!")
        
        if st.session_state.user_role == "Editor":
            if cols[1].button("edit", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
            if cols[2].button("delete", use_container_width=True):
                st.error("Delete clicked (Mock)")
        
        st.checkbox("Structural Highlighting", key="structural_highlighting_toggle", value=st.session_state.structural_highlighting)
        if st.session_state.structural_highlighting_toggle != st.session_state.structural_highlighting:
            st.session_state.structural_highlighting = st.session_state.structural_highlighting_toggle
            st.info("Preference saved to DB (Mock)")
            st.rerun()

        # Revision History
        with st.expander("Revision History", expanded=False):
            st.write("- 2026-02-13: Created by system")
            st.write("- 2026-02-13: Initial import")

st.markdown("---")
st.caption("Mock View: Records")
