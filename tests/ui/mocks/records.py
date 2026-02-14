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
if "pending_edits" not in st.session_state:
    st.session_state.pending_edits = {}
if "global_edit_mode" not in st.session_state:
    st.session_state.global_edit_mode = False
if "local_edits" not in st.session_state:
    st.session_state.local_edits = set()
if "view_selection_only" not in st.session_state:
    st.session_state.view_selection_only = query_params.get("view_selection", "False") == "True"
if "selection" not in st.session_state:
    st.session_state.selection = []
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
    st.query_params["view_selection"] = str(st.session_state.get("view_selection_only", False))

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
    # Compact Search Controls
    st.html("""
        <style>
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        </style>
""")
    
    st.markdown("**Search**")
    
    search_query = st.text_input("Enter text...", value=st.session_state.get("search_query", ""), 
                                key="search_query_input", label_visibility="collapsed")

    # Lexeme/FTS + Search/Clear Buttons on one line
    c_mode, c_s, c_c = st.columns([0.7, 0.15, 0.15])
    with c_mode:
        search_mode = st.radio("Search Mode", ["Lexeme", "FTS"], 
                               index=["Lexeme", "FTS"].index(st.session_state.get("search_mode", "Lexeme")), 
                               horizontal=True, key="search_mode_radio", label_visibility="collapsed")
    with c_s:
        if st.button("", icon="🔍", key="search_trigger", help="Execute Search", use_container_width=True):
            if search_query != st.session_state.search_query:
                st.session_state.search_query = search_query
                st.session_state.current_page = 1
                update_url_params()
                st.rerun()
    with c_c:
        if st.button("", icon="❌", key="search_clear", help="Clear Search", use_container_width=True):
            st.session_state.search_query = ""
            st.session_state.current_page = 1
            update_url_params()
            st.rerun()

    # Handle Enter key in text_input
    if search_query != st.session_state.get("search_query", ""):
        st.session_state.search_query = search_query
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()

    if search_mode != st.session_state.get("search_mode", "Lexeme"):
        st.session_state.search_mode = search_mode
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()

    # 2. Source Selection
    current_source = st.session_state.get("selected_source", "All Sources")
    selected_source = st.selectbox("Select Source", MOCK_SOURCES, 
                                   index=MOCK_SOURCES.index(current_source), 
                                   key="source_select",
                                   label_visibility="collapsed")
    if selected_source != current_source:
        st.session_state.selected_source = selected_source
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()
    
    # Filter Records
    filtered_records = MOCK_RECORDS
    
    if st.session_state.get("view_selection_only", False):
        filtered_records = st.session_state.selection
    else:
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

    st.markdown("**Pagination**")
    
    # 3. Pagination Control
    c1, c2 = st.columns(2)
    if c1.button("Prev", icon="◀", disabled=(st.session_state.current_page <= 1), use_container_width=True, key="sidebar_prev"):
        if st.session_state.global_edit_mode and st.session_state.pending_edits:
            for rid, mdf in st.session_state.pending_edits.items():
                for r in MOCK_RECORDS:
                    if r["id"] == rid:
                        r["mdf"] = mdf
            st.session_state.pending_edits = {}
            st.info("Auto-saved changes (Mock)")
        st.session_state.current_page -= 1
        update_url_params()
        st.rerun()
    if c2.button("Next", icon="▶", disabled=(st.session_state.current_page >= num_pages), use_container_width=True, key="sidebar_next"):
        if st.session_state.global_edit_mode and st.session_state.pending_edits:
            for rid, mdf in st.session_state.pending_edits.items():
                for r in MOCK_RECORDS:
                    if r["id"] == rid:
                        r["mdf"] = mdf
            st.session_state.pending_edits = {}
            st.info("Auto-saved changes (Mock)")
        st.session_state.current_page += 1
        update_url_params()
        st.rerun()
    
    st.markdown(f"<p style='text-align: center; margin-bottom: 0;'>Page {st.session_state.current_page} of {num_pages}</p>", unsafe_allow_html=True)
    
    new_page_size = st.selectbox("Results per page", [1, 5, 10, 25, 50, 100], index=[1, 5, 10, 25, 50, 100].index(st.session_state.page_size), key="sidebar_page_size")
    if new_page_size != st.session_state.page_size:
        st.session_state.page_size = new_page_size
        st.session_state.current_page = 1
        update_url_params()
        st.info("Preference saved to DB (Mock)")
        st.rerun()

    # Moved Editing Controls here
    if st.session_state.user_role == "Editor":
        if not st.session_state.global_edit_mode:
            if st.button("Enter Edit Mode", icon="📝", use_container_width=True, key="sidebar_enter_edit"):
                st.session_state.global_edit_mode = True
                st.rerun()
        else:
            col_e1, col_e2 = st.columns(2)
            if col_e1.button("Cancel All", icon="❌", use_container_width=True, key="sidebar_cancel_all"):
                st.session_state.global_edit_mode = False
                st.session_state.pending_edits = {}
                st.rerun()
            if col_e2.button("Save All", icon="💾", type="primary", use_container_width=True, key="sidebar_save_all"):
                # Mock Save all pending edits
                for rid, mdf in st.session_state.pending_edits.items():
                    # Update MOCK_RECORDS
                    for r in MOCK_RECORDS:
                        if r["id"] == rid:
                            r["mdf"] = mdf
                st.session_state.pending_edits = {}
                st.session_state.global_edit_mode = False
                st.success("All changes saved! (Mock)")
                st.rerun()
    else:
        st.info("View-only mode (Editor access required)")

    st.divider()
    
    # 5. My Selection
    header_text = f"My Selection ({len(st.session_state.selection)} records)"
    st.markdown(f"**{header_text}**")
    
    selection_col1, selection_col2, selection_col3 = st.columns(3)
    
    view_icon = "📚" if st.session_state.get("view_selection_only", False) else "🧺"
    view_help = "Show all records" if st.session_state.get("view_selection_only", False) else "Filter list to show only selected items"
    if selection_col1.button("", icon=view_icon, use_container_width=True, key="view_selection_toggle", help=view_help):
        st.session_state.view_selection_only = not st.session_state.get("view_selection_only", False)
        st.session_state.current_page = 1
        update_url_params()
        st.rerun()

    if st.session_state.selection:
        if selection_col2.button("📥", use_container_width=True, key="download_selection_mock", help="Download (Mock)"):
            st.success("Downloading...")
        if selection_col3.button("🗑️", use_container_width=True, key="discard_selection_mock", help="Discard (Mock)"):
            st.session_state.selection = []
            st.session_state.view_selection_only = False
            st.rerun()
    else:
        selection_col2.button("📥", disabled=True, use_container_width=True, key="download_selection_mock_disabled")
        selection_col3.button("🗑️", disabled=True, use_container_width=True, key="discard_selection_mock_disabled")

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
            
            is_editing = st.session_state.global_edit_mode or record_id in st.session_state.local_edits
            
            if is_editing:
                # EDIT MODE
                initial_val = st.session_state.pending_edits.get(record_id, record["mdf"])
                edited_mdf = st.text_area(
                    "MDF Editor", 
                    value=initial_val, 
                    height=200, 
                    key=f"edit_{record_id}",
                    label_visibility="collapsed"
                )
                
                if edited_mdf != initial_val:
                    st.session_state.pending_edits[record_id] = edited_mdf

                col_s1, col_s2, _ = st.columns([1, 1, 3])
                if col_s1.button("Update", type="primary", key=f"update_{record_id}", use_container_width=True):
                    # Update the mock data in session
                    for r in MOCK_RECORDS:
                        if r["id"] == record_id:
                            r["mdf"] = edited_mdf
                    if record_id in st.session_state.pending_edits:
                        del st.session_state.pending_edits[record_id]
                    if record_id in st.session_state.local_edits:
                        st.session_state.local_edits.remove(record_id)
                    st.success(f"Saved Record #{record_id}! (Mock)")
                    st.rerun()
                
                if not st.session_state.global_edit_mode:
                    if col_s2.button("Cancel", key=f"cancel_local_{record_id}", use_container_width=True):
                        if record_id in st.session_state.local_edits:
                            st.session_state.local_edits.remove(record_id)
                        if record_id in st.session_state.pending_edits:
                            del st.session_state.pending_edits[record_id]
                        st.rerun()
            else:
                # VIEW MODE
                mdf_lines = record["mdf"].split('\n')
                diagnostics = None
                if st.session_state.structural_highlighting:
                    diagnostics = MDFValidator.diagnose_record(mdf_lines)
                
                render_mdf_block(record["mdf"], diagnostics=diagnostics)
            
                # Action Toolbar for each record
                toolbar_cols = [1, 1]
                if st.session_state.user_role == "Editor" and not st.session_state.global_edit_mode:
                    toolbar_cols.append(1)
                
                toolbar = st.columns(toolbar_cols)
                
                # 1. Actions
                in_selection = record in st.session_state.selection
                selection_label = "Remove from Selection" if in_selection else "Add to Selection"
                selection_icon = "🧺" if not in_selection else "❌"
                
                if toolbar[0].button(selection_label, use_container_width=True, icon=selection_icon, key=f"add_selection_{record_id}"):
                    if not in_selection:
                        st.session_state.selection.append(record)
                        st.toast(f"Record #{record_id} added to selection!")
                    else:
                        st.session_state.selection.remove(record)
                        st.toast(f"Record #{record_id} removed from selection!")
                    st.rerun()
            
                if st.session_state.user_role == "Editor":
                    if toolbar[1].button("Delete", use_container_width=True, icon="🗑️", key=f"del_{record_id}"):
                        st.error(f"Delete clicked for Record #{record_id} (Mock)")
                    
                    if not st.session_state.global_edit_mode:
                        if toolbar[2].button("Edit", use_container_width=True, icon="📝", key=f"edit_btn_{record_id}"):
                            st.session_state.local_edits.add(record_id)
                            st.rerun()
            
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
                        if st.session_state.global_edit_mode:
                            if st.button("Restore to Editor", key=f"restore_{record_id}"):
                                # Update MOCK_RECORDS so it reflects in the next render.
                                for r in MOCK_RECORDS:
                                    if r["id"] == record_id:
                                        r["mdf"] = prev_mdf
                                        # Also update pending edits if present
                                        if record_id in st.session_state.pending_edits:
                                            st.session_state.pending_edits[record_id] = prev_mdf
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
