# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
import difflib
import time
import html as _html
from urllib.parse import quote
from src.frontend.ui_utils import render_mdf_block
from src.mdf.validator import MDFValidator

# --- MOCK DATA ---
MOCK_SOURCES = ["All Sources", "Mohegan", "Natick", "SNEA-General"]
MOCK_RECORDS = [
    {"id": i, "source": ["Mohegan", "Natick", "SNEA-General"][i % 3], "mdf": f"\\lx record {i}\n\\ps n\n\\ge gloss {i}\n\\inf inflection {i}"}
    for i in range(1, 1001)
]

# --- SESSION STATE ---
# Sync from URL params
query_params = st.query_params
if "search" in query_params:
    st.session_state.search_query = query_params["search"]
if "search_mode" in query_params:
    st.session_state.search_mode = query_params["search_mode"]
if "source" in query_params:
    st.session_state.selected_source = query_params["source"]
if "page" in query_params:
    try:
        st.session_state.current_page = int(query_params["page"])
    except ValueError:
        pass
if "page_size" in query_params:
    try:
        st.session_state.page_size = int(query_params["page_size"])
    except ValueError:
        pass

if "page_size" not in st.session_state:
    st.session_state.page_size = 25
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "cart" not in st.session_state:
    st.session_state.cart = []
if "edit_records" not in st.session_state:
    st.session_state.edit_records = set()  # Set of record IDs in edit mode
if "user_role" not in st.session_state:
    st.session_state.user_role = "Editor"
if "structural_highlighting" not in st.session_state:
    st.session_state.structural_highlighting = True
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = {}  # {record_id: previous_mdf}

def update_url_params():
    """Sync session state back to URL query params."""
    st.query_params["search"] = st.session_state.get("search_query", "")
    st.query_params["search_mode"] = st.session_state.get("search_mode", "Lexeme")
    st.query_params["source"] = st.session_state.get("selected_source", "All Sources")
    st.query_params["page"] = st.session_state.get("current_page", 1)
    st.query_params["page_size"] = st.session_state.get("page_size", 25)

def _diff_icon_svg(symbol: str, color: str) -> str:
    """Return a percent-encoded SVG for diff indicators."""
    # Large format icon filling the viewbox
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
        f'<text x="24" y="40" font-size="48" font-weight="bold" fill="{color}" text-anchor="middle">{symbol}</text>'
        f'</svg>'
    )
    return f"data:image/svg+xml,{quote(svg, safe='')}"

def render_diff_view(prev_mdf: str, curr_mdf: str):
    """Render a tightened diff view with linguistic-optimized gutter icons."""
    diff = list(difflib.ndiff(prev_mdf.splitlines(), curr_mdf.splitlines()))
    
    # Process diff to group contiguous - and + as transformations (→)
    processed_diff = []
    i = 0
    while i < len(diff):
        line = diff[i]
        marker = line[0]
        content = line[2:]
        
        if marker == '-' and i + 1 < len(diff) and diff[i+1][0] == '+':
            # This is a transformation: Old line replaced by New line
            processed_diff.append(('×', content, 'diff-removed')) # The old line
            processed_diff.append(('→', diff[i+1][2:], 'diff-transformed')) # The new line
            i += 2
        elif marker == '-':
            processed_diff.append(('×', content, 'diff-removed'))
            i += 1
        elif marker == '+':
            processed_diff.append(('+', content, 'diff-added'))
            i += 1
        elif marker == ' ':
            processed_diff.append((' ', content, 'diff-unchanged'))
            i += 1
        else:
            i += 1
            
    line_html_parts = []
    for symbol, content, status_cls in processed_diff:
        icon_url = ""
        if symbol == '+':
            icon_url = _diff_icon_svg("+", "#28a745") # Green
        elif symbol == '×':
            icon_url = _diff_icon_svg("×", "#d73a49") # Red
        elif symbol == '→':
            icon_url = _diff_icon_svg("→", "#005cc5") # Blue
            
        escaped_content = _html.escape(content) if content else "&nbsp;"
        bg_style = f"background-image: url('{icon_url}');" if icon_url else ""
        
        line_html_parts.append(
            f'<div class="diff-line {status_cls}" style="{bg_style}">{escaped_content}</div>'
        )
    
    line_divs = "".join(line_html_parts)
    
    st.html(f"""
        <style>
        .diff-container {{
            font-family: 'Source Code Pro', monospace;
            font-size: 0.85rem;
            line-height: 1.0;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            background-color: #f8f9fa;
        }}
        .diff-line {{
            white-space: pre-wrap;
            padding-left: 2.5rem;
            background-repeat: no-repeat;
            background-position: 0.1rem center;
            background-size: 2.2rem 1.0em;
            min-height: 1.0rem;
        }}
        .diff-added {{
            background-color: rgba(40, 167, 69, 0.1);
        }}
        .diff-removed {{
            background-color: rgba(215, 58, 73, 0.1);
            text-decoration: line-through;
            color: #777;
        }}
        .diff-transformed {{
            background-color: rgba(0, 92, 197, 0.1);
            font-weight: 500;
        }}
        @media (prefers-color-scheme: dark) {{
            .diff-container {{ background-color: #1e1e1e; border-color: #444; }}
            .diff-added {{ background-color: rgba(40, 167, 69, 0.2); }}
            .diff-removed {{ background-color: rgba(215, 58, 73, 0.2); }}
            .diff-transformed {{ background-color: rgba(0, 92, 197, 0.2); }}
        }}
        </style>
        <div class="diff-container">{line_divs}</div>
    """)

# --- SIDEBAR ---
with st.sidebar:
    
    # 1. Search
    st.subheader("Search")
    old_query = st.session_state.get("search_query", "")
    search_query = st.text_input("Enter text...", value=old_query, key="search_query_input")
    if search_query != old_query:
        st.session_state.search_query = search_query
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()

    old_mode = st.session_state.get("search_mode", "Lexeme")
    search_mode = st.radio("Search Mode", ["Lexeme", "FTS"], index=["Lexeme", "FTS"].index(old_mode), horizontal=True, key="search_mode_radio")
    if search_mode != old_mode:
        st.session_state.search_mode = search_mode
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()
    
    # 2. Source Selection
    st.subheader("Source Collection")
    old_source = st.session_state.get("selected_source", "All Sources")
    selected_source = st.selectbox("Select Source", MOCK_SOURCES, index=MOCK_SOURCES.index(old_source), key="source_select")
    if selected_source != old_source:
        st.session_state.selected_source = selected_source
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()
    
    # Filter Records
    filtered_records = MOCK_RECORDS
    if st.session_state.get("selected_source", "All Sources") != "All Sources":
        filtered_records = [r for r in filtered_records if r["source"] == st.session_state.selected_source]
    
    search_q = st.session_state.get("search_query", "")
    if search_q:
        # Simple mock search logic
        if st.session_state.get("search_mode", "Lexeme") == "Lexeme":
            filtered_records = [r for r in filtered_records if search_q.lower() in r["mdf"].split('\n')[0].lower()]
        else:
            filtered_records = [r for r in filtered_records if search_q.lower() in r["mdf"].lower()]

    # Pagination calculation
    total_records = len(filtered_records)
    num_pages = (total_records + st.session_state.page_size - 1) // st.session_state.page_size if total_records > 0 else 1
    
    # Bounds check for current page
    if st.session_state.current_page > num_pages:
        st.session_state.current_page = num_pages
    if st.session_state.current_page < 1:
        st.session_state.current_page = 1
        
    start_idx = (st.session_state.current_page - 1) * st.session_state.page_size
    end_idx = start_idx + st.session_state.page_size
    page_records = filtered_records[start_idx:end_idx]

    st.divider()

    # 3. Pagination Control
    st.subheader("Pagination")
    c1, c2 = st.columns(2)
    if c1.button("◀ Prev", disabled=(st.session_state.current_page <= 1), use_container_width=True, key="sidebar_prev"):
        st.session_state.current_page -= 1
        update_url_params()
        st.rerun()
    if c2.button("Next ▶", disabled=(st.session_state.current_page >= num_pages), use_container_width=True, key="sidebar_next"):
        st.session_state.current_page += 1
        update_url_params()
        st.rerun()
    
    st.markdown(f"<p style='text-align: center; margin-bottom: 0;'>Page {st.session_state.current_page} of {num_pages}</p>", unsafe_allow_html=True)
    
    new_page_size = st.selectbox("Results per page", [10, 25, 50, 100], index=[10, 25, 50, 100].index(st.session_state.page_size), key="sidebar_page_size")
    if new_page_size != st.session_state.page_size:
        st.session_state.page_size = new_page_size
        st.session_state.current_page = 1
        update_url_params()
        st.info("Preference saved to DB (Mock)")
        st.rerun()

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
st.markdown(
    """
    <style>
    /* Standard ultra-tight horizontal padding for main container on wide screens */
    @media (min-width: calc(736px + 8rem)) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not filtered_records:
    st.warning("No records found matching filters.")
else:
    st.subheader(f"Records List ({total_records} found)")
    
    for record in page_records:
        record_id = record["id"]
        with st.container(border=True):
            st.markdown(f"**Record #{record_id} [{record['source']}]**")
            
            if record_id in st.session_state.edit_records:
                # EDIT MODE
                edited_mdf = st.text_area("MDF Editor", value=record["mdf"], height=200, key=f"edit_{record_id}")
                
                c1, c2 = st.columns([1, 4])
                if c1.button("Save", type="primary", key=f"save_{record_id}"):
                    # Update the mock data in session
                    for r in MOCK_RECORDS:
                        if r["id"] == record_id:
                            r["mdf"] = edited_mdf
                    st.session_state.edit_records.remove(record_id)
                    st.success(f"Saved Record #{record_id}!")
                    st.rerun()
                if c2.button("Cancel", key=f"cancel_{record_id}"):
                    st.session_state.edit_records.remove(record_id)
                    st.rerun()
            else:
                # VIEW MODE
                mdf_lines = record["mdf"].split('\n')
                diagnostics = None
                if st.session_state.structural_highlighting:
                    diagnostics = MDFValidator.diagnose_record(mdf_lines)
                
                if st.session_state.user_role == "Editor":
                    if st.button("✎ Click to Edit Record", use_container_width=True, key=f"btn_edit_{record_id}"):
                        st.session_state.edit_records.add(record_id)
                        st.rerun()

                render_mdf_block(record["mdf"], diagnostics=diagnostics)
            
            # Action Toolbar for each record
            toolbar = st.columns([0.5, 0.5, 1, 1, 1, 0.5, 0.5])
            
            # 0. Navigation Buttons
            # Find index of current record in filtered list
            current_idx_in_filtered = filtered_records.index(record)
            
            if toolbar[0].button("◀", use_container_width=True, help="Previous Record", key=f"prev_rec_{record_id}"):
                if current_idx_in_filtered > 0:
                    prev_rec = filtered_records[current_idx_in_filtered - 1]
                    # Pagination logic: Jump to the page containing the previous record
                    new_page = (current_idx_in_filtered - 1) // st.session_state.page_size + 1
                    st.session_state.current_page = new_page
                    update_url_params()
                    st.toast(f"Navigated to Record #{prev_rec['id']}")
                    st.rerun()

            if toolbar[1].button("▶", use_container_width=True, help="Next Record", key=f"next_rec_{record_id}"):
                if current_idx_in_filtered < len(filtered_records) - 1:
                    next_rec = filtered_records[current_idx_in_filtered + 1]
                    # Pagination logic: Jump to the page containing the next record
                    new_page = (current_idx_in_filtered + 1) // st.session_state.page_size + 1
                    st.session_state.current_page = new_page
                    update_url_params()
                    st.toast(f"Navigated to Record #{next_rec['id']}")
                    st.rerun()

            # 1. Copy Buttons
            if toolbar[2].button("Copy Plain", use_container_width=True, key=f"copy_plain_{record_id}"):
                st.write(f'<script>navigator.clipboard.writeText(`{record["mdf"]}`);</script>', unsafe_allow_html=True)
                st.toast(f"Copied Record #{record_id} (Plain)!")
            if toolbar[3].button("Copy Rich", use_container_width=True, key=f"copy_rich_{record_id}"):
                st.toast(f"Copied Record #{record_id} (Rich)!")

            # 2. Actions
            if toolbar[4].button("Add to Cart", use_container_width=True, key=f"add_cart_{record_id}"):
                if record not in st.session_state.cart:
                    st.session_state.cart.append(record)
                    st.toast(f"Record #{record_id} added to cart!")
                    st.rerun()
                else:
                    st.toast(f"Record #{record_id} already in cart!")

            if st.session_state.user_role == "Editor":
                if toolbar[5].button("✎", use_container_width=True, help="Edit", key=f"icon_edit_{record_id}"):
                    st.session_state.edit_records.add(record_id)
                    st.rerun()
                if toolbar[6].button("✖", use_container_width=True, help="Delete", key=f"icon_del_{record_id}"):
                    st.error(f"Delete clicked for Record #{record_id} (Mock)")

            # Revision History (compact per record)
            with st.expander("Revision History", expanded=False):
                st.write("- 2026-02-13: Created by system")
                
                if record_id not in st.session_state.history_loaded:
                    if st.button("Load Previous Version", key=f"load_hist_{record_id}"):
                        with st.spinner("Fetching version from archive..."):
                            time.sleep(1)  # Simulate lazy load
                            # Create a mock previous version with slight difference
                            prev_mdf = record["mdf"].replace("record", "entry").replace("gloss", "translation")
                            st.session_state.history_loaded[record_id] = prev_mdf
                            st.rerun()
                else:
                    st.markdown("**Historical Version (2026-02-12)**")
                    prev_mdf = st.session_state.history_loaded[record_id]
                    
                    # Diff Visualization
                    st.markdown("---")
                    st.markdown("*Enhanced Diff View (Gutter Icons):*")
                    
                    render_diff_view(prev_mdf, record["mdf"])
                    
                    st.markdown("---")
                    
                    # Restore Action
                    if record_id in st.session_state.edit_records:
                        if st.button("Restore to Editor", key=f"restore_{record_id}"):
                            # In a real app, we'd update the session state variable tied to the text_area
                            # For the mock, we can update the record in MOCK_RECORDS temporarily 
                            # or use a specific state key if we had one.
                            # Here we'll update MOCK_RECORDS so it reflects in the next render.
                            for r in MOCK_RECORDS:
                                if r["id"] == record_id:
                                    r["mdf"] = prev_mdf
                            st.toast("Restored historical version to editor!")
                            st.rerun()
                    
                    if st.button("Hide History Detail", key=f"hide_hist_{record_id}"):
                        del st.session_state.history_loaded[record_id]
                        st.rerun()

    st.divider()
    
    st.checkbox("Structural Highlighting", key="structural_highlighting_toggle", value=st.session_state.structural_highlighting)
    if st.session_state.structural_highlighting_toggle != st.session_state.structural_highlighting:
        st.session_state.structural_highlighting = st.session_state.structural_highlighting_toggle
        st.info("Preference saved to DB (Mock)")
        st.rerun()

st.markdown("---")
st.caption("Mock View: Records")
