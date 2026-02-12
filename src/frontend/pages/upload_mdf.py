# Copyright (c) 2026 Brothertown Language
# 🚨 SUPREME DIRECTIVE: NO EDITS WITHOUT EXPLICIT APPROVAL ("Go", "Proceed", "Approved") 🚨
def upload_mdf():
    import streamlit as st
    import datetime as _dt
    from src.database import get_session
    from src.database.models.core import Source
    from src.services.upload_service import UploadService
    from src.frontend.ui_utils import hide_sidebar_nav, render_mdf_block
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf")

    # C-2: Role guard — only editor or admin
    user_role = st.session_state.get("user_role")
    if user_role not in ("editor", "admin"):
        st.error("You do not have permission to access this page. Editor or admin role required.")
        return

    # View switching
    if st.session_state.get("review_batch_id"):
        _render_review_view()
        return

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    # Collapse default top padding in both sidebar and main panel
    st.markdown(
        """
        <style>
        .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0px !important; margin-top: 0px !important; }
        header[data-testid="stHeader"] { height: 0px !important; min-height: 0px !important; padding: 0px !important; overflow: visible !important; }
        [data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stSidebarHeader"] { height: 2rem !important; min-height: 2rem !important; padding: 0px !important; }
        div[data-testid="stSidebarUserContent"] { padding-top: 0px !important; }
        
        /* st.status widget default styling - no overlay */
        div[data-testid="stStatusWidget"] {
            margin-bottom: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ── Sidebar: header and controls ──────────────────────────────
    with st.sidebar:
        st.header("Upload MDF File")

        # C-4: Source selector
        session = get_session()
        try:
            sources = session.query(Source).order_by(Source.name).all()
        finally:
            session.close()

        source_options = [s.name for s in sources]
        source_ids = {s.name: s.id for s in sources}

        SELECT_SOURCE_LABEL = "Select a source..."
        CREATE_NEW_LABEL = "+ Add new source…"
        
        # Build options: placeholder first, then create new, then sources
        final_options = [SELECT_SOURCE_LABEL, CREATE_NEW_LABEL] + source_options

        # Initialize default from session state or placeholder.
        current_selection = st.session_state.get("upload_active_source_name", SELECT_SOURCE_LABEL)
        
        try:
            default_index = final_options.index(current_selection)
        except ValueError:
            default_index = 0

        selected_source = st.selectbox(
            "Target source collection", 
            final_options, 
            index=default_index,
            key="upload_active_source_name"
        )

        # Clear focus flag and success state if we are NOT on the create new source label
        if selected_source != CREATE_NEW_LABEL:
            st.session_state.pop("source_focus_done", None)
            st.session_state.pop("source_creation_success_name", None)

        # C-4a: Create new source inline
        selected_source_id = None
        if selected_source == CREATE_NEW_LABEL:
            # Only trigger focus once per selection
            if not st.session_state.get("source_focus_done"):
                st.toast("Add New Source Selected")
                # Inject focus script for the name input using components.html for better JS execution
                import streamlit.components.v1 as components
                components.html("""
                    <script>
                    (function() {
                        const TARGET_PLACEHOLDER = "Book/Document — Author/Linguist";
                        const TARGET_LABEL = "Source name";
                        const log = (msg) => {
                            const m = "[SNEA Focus] " + msg;
                            console.log(m);
                            if (window.parent && window.parent.console) window.parent.console.log(m);
                        };
                        
                        const focusInput = () => {
                            try {
                                const doc = window.parent.document || window.top.document;
                                // 1. Try by placeholder
                                const inputs = doc.querySelectorAll('input');
                                for (const input of inputs) {
                                    if (input.placeholder === TARGET_PLACEHOLDER) {
                                        log("Found input by placeholder. Focusing...");
                                        input.focus();
                                        return true;
                                    }
                                }
                                // 2. Try by label
                                const labels = doc.querySelectorAll('label');
                                for (const label of labels) {
                                    if (label.innerText.includes(TARGET_LABEL)) {
                                        const inputId = label.getAttribute('for');
                                        const input = inputId ? doc.getElementById(inputId) : null;
                                        if (input) {
                                            log("Found input by label. Focusing...");
                                            input.focus();
                                            return true;
                                        }
                                    }
                                }
                            } catch (e) {
                                log("Error accessing parent: " + e.message);
                            }
                            return false;
                        };
                        
                        log("Focus script starting...");
                        if (!focusInput()) {
                            const observer = new MutationObserver(() => {
                                if (focusInput()) observer.disconnect();
                            });
                            try {
                                observer.observe(window.parent.document.body, { childList: true, subtree: true });
                                setTimeout(() => { observer.disconnect(); log("Timeout reached."); }, 5000);
                            } catch (e) { log("Observer failed: " + e.message); }
                        }
                    })();
                    </script>
                """, height=0)
                st.session_state["source_focus_done"] = True
            st.markdown("#### Create a new source")
            
            # Persistent success indicator
            success_name = st.session_state.get("source_creation_success_name")
            if success_name:
                st.success(f"Source '{success_name}' created successfully. Please select it from the dropdown above.")
            
            is_disabled = bool(success_name)
            
            new_name = st.text_input(
                "Source name",
                placeholder="Book/Document — Author/Linguist",
                key="new_source_name_input",
                disabled=is_disabled
            )
            new_description = st.text_input(
                "Description (optional)",
                key="new_source_description_input",
                disabled=is_disabled
            )
            if st.button("Create Source", disabled=is_disabled):
                if not new_name or not new_name.strip():
                    st.error("Source name is required.")
                else:
                    session = get_session()
                    try:
                        existing = session.query(Source).filter(Source.name == new_name.strip()).first()
                        if existing:
                            st.error(f"A source named '{new_name.strip()}' already exists.")
                        else:
                            new_source = Source(
                                name=new_name.strip(),
                                description=new_description.strip() if new_description else None,
                            )
                            session.add(new_source)
                            session.commit()
                            # Track success for persistence across rerun
                            st.session_state["source_creation_success_name"] = new_name.strip()
                            # Clear input fields state
                            st.session_state.pop("new_source_name_input", None)
                            st.session_state.pop("new_source_description_input", None)
                            st.rerun()
                    except Exception as e:
                        session.rollback()
                        logger.error("Failed to create source: %s", e)
                        st.error(f"Failed to create source: {e}")
                    finally:
                        session.close()
        else:
            selected_source_id = source_ids.get(selected_source)

        # C-3: File uploader
        uploaded_file = st.file_uploader(
            "Upload an MDF file",
            type=["txt", "mdf"],
            help="Select a .txt or .mdf file containing MDF-formatted dictionary entries.",
        )
        
        # Persistence: If a file is uploaded, store it. If not, check if we have one in state.
        if uploaded_file is not None:
            st.session_state["pending_upload_content"] = uploaded_file.getvalue().decode("utf-8")
            st.session_state["pending_upload_name"] = uploaded_file.name
            st.session_state["pending_upload_file_id"] = uploaded_file.file_id
        
        # Use state if available
        active_content = st.session_state.get("pending_upload_content")
        active_name = st.session_state.get("pending_upload_name")
        active_file_id = st.session_state.get("pending_upload_file_id")

        st.divider()
        if st.button("← Back to Main Menu", key="back_to_main"):
            st.session_state.pop("review_batch_id", None)
            st.session_state.pop("upload_active_source_name", None)
            st.switch_page("pages/index.py")

    # ── Main panel: upload content ────────────────────────────────
    # Display flash message from batch completion or other bulk actions
    flash = st.session_state.pop("bulk_flash", None)
    if flash:
        level, msg = flash
        getattr(st, level)(msg)

    # ── Pending batches list ─────────────────────────────────────
    user_email = st.session_state.get("user_email", "")
    batches = UploadService.list_pending_batches(user_email) if user_email else []
    if batches:
        st.subheader(f"{len(batches)} Pending Batch{'es' if len(batches) != 1 else ''}")
        for b in batches:
            ts = b["uploaded_at"]
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "unknown"
            batch_id = b["batch_id"]
            with st.container():
                st.markdown("---")
                col_info, col_review, col_download, col_discard = st.columns([4, 1, 1, 1])
                with col_info:
                    st.markdown(
                        f"**{b['source_name']}** — {b['filename'] or 'unnamed'}  \n"
                        f"{b['entry_count']} entries · {ts_str}"
                    )
                with col_review:
                    if st.button("Review", key=f"review_{batch_id}", type="primary"):
                        st.session_state["review_batch_id"] = batch_id
                        st.rerun()
                with col_download:
                    try:
                        mdf_blob = UploadService.get_pending_batch_mdf(batch_id)
                        # Build cross-OS compatible filename for pending records:
                        # Format: pending_<Source>_<YYYY-MM-DD>_<SSSSS>.txt
                        # - pending_: prefix to distinguish from committed records.
                        # - <Source>: Alphanumeric only (non-alphanumeric replaced by underscores).
                        # - <YYYY-MM-DD>: Date of upload or current date.
                        # - <SSSSS>: Seconds since midnight, zero-padded to 5 digits.
                        safe_source = "".join(c if c.isalnum() else "_" for c in b['source_name'])
                        now = b["uploaded_at"] or _dt.datetime.now()
                        seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
                        fname = f"pending_{safe_source}_{now.strftime('%Y-%m-%d')}_{seconds_since_midnight:05d}.txt"

                        st.download_button(
                            label="Download",
                            data=mdf_blob,
                            file_name=fname,
                            mime="text/plain",
                            key=f"download_{batch_id}"
                        )
                    except Exception as e:
                        st.error("Error preparing download")
                with col_discard:
                    if st.button("Discard", key=f"discard_{batch_id}"):
                        try:
                            count = UploadService.discard_all(batch_id)
                            st.toast(f"Discarded {count} entries.")
                            st.rerun()
                        except Exception as e:
                            logger.error("Discard batch failed: %s", e)
                            st.error(f"Discard failed: {e}")
        st.divider()

    # Track whether pending batches exist for the prompt message
    has_pending_batches = bool(batches)

    if active_content:
        with st.expander("Raw file preview", expanded=False):
            st.code(active_content, language=None)

        # C-5: Parse and display upload summary
        try:
            entries = UploadService.parse_upload(active_content)
            st.success(f"**{len(entries)}** entries found in `{active_name}`.")

            # Build summary table
            rows = []
            for e in entries:
                rows.append({
                    "lx": e.get("lx", ""),
                    "ps": e.get("ps", ""),
                    "ge": e.get("ge", ""),
                })
            st.dataframe(rows, width="stretch", height=300)

            # Store parsed data in session state for later phases
            st.session_state["upload_entries"] = entries
            st.session_state["upload_filename"] = active_name
            st.session_state["upload_source_id"] = selected_source_id

            # C-6: Stage & Match button
            if selected_source_id is None:
                st.warning("Select a source collection before staging.")
                st.button("Stage & Match", type="primary", disabled=True, help="You must select a source collection first.")
            else:
                user_email = st.session_state.get("user_email", "")
                # Disable after use until a new file is uploaded
                # Use Streamlit's unique file_id to distinguish re-uploads of the same filename
                already_staged = st.session_state.get("upload_staged_file_id") == active_file_id
                if st.button("Stage & Match", type="primary", disabled=already_staged):
                    try:
                        batch_id = UploadService.stage_entries(
                            user_email=user_email,
                            source_id=selected_source_id,
                            entries=entries,
                            filename=active_name,
                        )
                        match_results = UploadService.suggest_matches(batch_id)
                        st.session_state["upload_batch_id"] = batch_id
                        st.session_state["upload_staged_file_id"] = active_file_id
                        
                        # Clear pending upload after successful staging
                        st.session_state.pop("pending_upload_content", None)
                        st.session_state.pop("pending_upload_name", None)
                        st.session_state.pop("pending_upload_file_id", None)
                        st.session_state.pop("upload_active_source_name", None)
                        # Switch to dedicated review view
                        st.session_state["review_batch_id"] = batch_id
                        st.rerun()
                    except Exception as e:
                        logger.error("Stage & Match failed: %s", e)
                        st.error(f"Stage & Match failed: {e}")

        except ValueError as e:
            st.error(str(e))
    elif not has_pending_batches:
        st.info("Upload an MDF file using the sidebar to get started.")
    else:
        st.info("Upload another MDF file using the sidebar, or review a pending batch above.")


def _render_review_view():
    """Dedicated full-width review view for a selected batch.

    All controls live in the sidebar; the main panel is reserved
    exclusively for record comparison content.
    """
    import streamlit as st
    from src.services.upload_service import UploadService
    from src.frontend.ui_utils import hide_sidebar_nav, render_mdf_block
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf.review")
    batch_id = st.session_state.get("review_batch_id")
    user_email = st.session_state.get("user_email", "")

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    # Collapse default top padding in both sidebar and main panel
    st.markdown(
        """
        <style>
        .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        
        /* Custom class for ultra-tight horizontal padding */
        @media (min-width: calc(736px + 8rem)) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }
        
        section[data-testid="stSidebar"] .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0px !important; margin-top: 0px !important; }
        header[data-testid="stHeader"] { height: 0px !important; min-height: 0px !important; padding: 0px !important; overflow: visible !important; }
        [data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stSidebarHeader"] { height: 2rem !important; min-height: 2rem !important; padding: 0px !important; }
        div[data-testid="stSidebarUserContent"] { padding-top: 0px !important; }

        /* st.status widget default styling - no overlay */
        div[data-testid="stStatusWidget"] {
            margin-bottom: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Scroll to top when page changes (triggered by rerun after page nav)
    st.html('<script>window.parent.document.querySelector(".main").scrollTo(0, 0);</script>')

    # ── Sidebar: header ───────────────────────────────────────────
    with st.sidebar:
        st.header("Review Staged Entries")

    # ── Main panel: record comparisons only ───────────────────────
    _render_review_table(batch_id, session_deps={
        'user_email': user_email,
    })

    # ── Sidebar bottom: re-match & back ─────────
    with st.sidebar:
        st.divider()

        # C-6b: Re-Match button
        if st.button("Re-Match", key="rematch_btn"):
            try:
                match_results = UploadService.rematch_batch(batch_id)
                st.session_state["upload_batch_id"] = batch_id
                st.session_state["upload_match_results"] = match_results
                st.success(f"Re-matched batch. "
                           f"**{sum(1 for m in match_results if m.get('suggested_record_id') is not None)}** "
                           f"matches found.")
            except Exception as e:
                logger.error("Re-Match failed: %s", e)
                st.error(f"Re-Match failed: {e}")

        # Back button to return to upload view
        if st.button("← Back to MDF Upload", key="back_to_upload"):
            st.session_state.pop("review_batch_id", None)
            st.rerun()
            return


def _render_review_table(batch_id, session_deps):
    """Render the D-1 review table for a given batch_id."""
    import streamlit as st
    import uuid as _uuid
    from src.database import get_session
    from src.database.models.workflow import MatchupQueue
    from src.database.models.core import Record, Language, Source
    from src.services.upload_service import UploadService
    from src.services.preference_service import PreferenceService
    from src.frontend.ui_utils import render_mdf_block
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf.review")
    user_email = session_deps['user_email']

    session = get_session()
    try:
        rows = (
            session.query(MatchupQueue)
            .filter_by(batch_id=batch_id)
            .order_by(MatchupQueue.id)
            .all()
        )
        if not rows:
            st.session_state.pop("review_batch_id", None)
            st.session_state["bulk_flash"] = ("success", "Batch complete — all entries have been applied or discarded.")
            st.rerun()
            return

        # Determine source context for bulk buttons
        source_id = rows[0].source_id
        existing_record_count = (
            session.query(Record)
            .filter_by(source_id=source_id, is_deleted=False)
            .count()
        )
        is_new_source = existing_record_count == 0

        # Get language_id (use first available language)
        lang = session.query(Language).first()
        language_id = lang.id if lang else 1

        # Pre-fetch suggested records for comparison view
        suggested_ids = [r.suggested_record_id for r in rows if r.suggested_record_id]
        suggested_records = {}
        if suggested_ids:
            recs = session.query(Record).filter(Record.id.in_(suggested_ids)).all()
            suggested_records = {r.id: r for r in recs}

        # Get source name for cross-source info
        source_obj = session.get(Source, source_id)
        source_name = source_obj.name if source_obj else str(source_id)

    finally:
        session.close()

    # ── Filtering ───────────────────────────────────────────────────
    filter_options = {
        "All Records": (None, None),
        "Matched (Exact)": ("matched", "exact"),
        "Matched (Base-form)": ("matched", "base_form"),
        "Create New Record": ("create_new", None),
        "Create Homonym": ("create_homonym", None),
        "Discard Entry": ("discard", None),
        "Ignored": ("ignored", None),
    }
    
    with st.sidebar:
        st.subheader("Filters")
        
        # ── Pagination State ───────────────────────────────────────────
        page_size_options = [1, 5, 10, 25, 50]
        
        # Initialize review_page_size from database if not set in session
        if "review_page_size" not in st.session_state:
            saved_pref = PreferenceService.get_preference(
                user_email, "upload_review", "page_size", str(page_size_options[1]) # Default 5
            )
            st.session_state["review_page_size"] = int(saved_pref) if saved_pref and saved_pref.isdigit() else page_size_options[1]

        page_size = st.session_state.get("review_page_size", page_size_options[1])
        if page_size not in page_size_options:
            page_size = page_size_options[1]

        # Get current selection from session state
        saved_filter = st.session_state.get("review_filter_status", "All Records")
        filter_labels = list(filter_options.keys())
        try:
            default_ix = filter_labels.index(saved_filter)
        except ValueError:
            default_ix = 0

        selected_filter = st.selectbox(
            "Filter by Status",
            options=filter_labels,
            index=default_ix,
            key="review_filter_status_widget"
        )
        # Update session state for persistence
        if selected_filter != st.session_state.get("review_filter_status"):
            st.session_state["review_filter_status"] = selected_filter
            st.session_state["review_current_page"] = 1 # Reset to page 1 on filter change
            st.rerun()

    # Apply filters to rows
    if selected_filter != "All Records":
        filtered_rows = []
        f_status, f_match_type = filter_options[selected_filter]
        for row in rows:
            # Determine row's effective status/match_type pair
            # (Matches D-1 logic used later for default status)
            has_suggestion = row.suggested_record_id is not None
            row_match_type = row.match_type if has_suggestion else None
            
            if row.status not in ('pending',):
                eff_status = row.status
                eff_match_type = row.match_type if eff_status == 'matched' else None
            else:
                # Recommendation logic (simplification for filtering)
                # Note: record_id_conflict is not re-calculated here for performance,
                # but it defaults to create_new anyway if not matched.
                if has_suggestion:
                    eff_status = 'matched'
                    eff_match_type = row.match_type
                else:
                    eff_status = 'create_new'
                    eff_match_type = None
            
            if eff_status == f_status:
                if f_match_type is None or eff_match_type == f_match_type:
                    filtered_rows.append(row)
        rows = filtered_rows

    # ── Compute pagination ──────────────────────────────────────────
    total_entries = len(rows)
    page_size = st.session_state.get("review_page_size", 1)
    total_pages = max(1, (total_entries + page_size - 1) // page_size)
    current_page = st.session_state.get("review_current_page", 1)
    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1

    # ── Sidebar: page nav (top), bulk actions ─────────
    with st.sidebar:
        # Page navigation at top
        st.markdown(f"Page **{current_page}** of **{total_pages}** ({total_entries} entries)")
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("◀ Previous", key="page_prev", disabled=(current_page <= 1)):
                st.session_state["review_current_page"] = current_page - 1
                st.rerun()
        with nav_col2:
            if st.button("Next ▶", key="page_next", disabled=(current_page >= total_pages)):
                st.session_state["review_current_page"] = current_page + 1
                st.rerun()

        st.divider()
        st.subheader("Bulk Actions")

        # Display flash message from previous bulk action
        flash = st.session_state.pop("bulk_flash", None)
        if flash:
            level, msg = flash
            getattr(st, level)(msg)

        # D-1a: Bulk approval action buttons
        if is_new_source:
            if st.button("Approve All as New Records", key="bulk_approve_new"):
                with st.status("Approving all as new...", expanded=True) as status:
                    progress_bar = st.progress(0.0)
                    def update_progress(curr, tot):
                        progress_bar.progress(curr / tot if tot > 0 else 1.0)
                    try:
                        import uuid as _bulk_uuid_new
                        count = UploadService.approve_all_new_source(
                            batch_id,
                            user_email=user_email,
                            language_id=language_id,
                            session_id=str(_bulk_uuid_new.uuid4()),
                            progress_callback=update_progress
                        )
                        status.update(label=f"Applied {count} new records!", state="complete", expanded=False)
                        st.session_state["bulk_flash"] = ("success", f"All {count} entries applied as new records.")
                        import time as _time
                        _time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        logger.error("Bulk approve failed: %s", e)
                        st.error(f"Bulk approve failed: {e}")
        else:
            if st.button("Approve All Matched", key="bulk_approve_matched"):
                with st.status("Applying matched entries...", expanded=True) as status:
                    progress_bar = st.progress(0.0)
                    def update_progress(curr, tot):
                        progress_bar.progress(curr / tot if tot > 0 else 1.0)
                    try:
                        import uuid as _bulk_uuid
                        count = UploadService.approve_all_by_record_match(
                            batch_id,
                            user_email=user_email,
                            language_id=language_id,
                            session_id=str(_bulk_uuid.uuid4()),
                            progress_callback=update_progress
                        )
                        if count:
                            status.update(label=f"Applied {count} matched entries!", state="complete", expanded=False)
                            st.session_state["bulk_flash"] = ("success", f"{count} matched entr{'y' if count == 1 else 'ies'} applied.")
                            import time as _time
                            _time.sleep(0.5)
                            st.rerun()
                        else:
                            status.update(label="No matched entries found.", state="complete", expanded=False)
                            st.info("No matched entries to apply.")
                    except Exception as e:
                        logger.error("Bulk approve matched failed: %s", e)
                        st.error(f"Bulk approve matched failed: {e}")

            if st.button("Approve Non-Matches as New", key="bulk_approve_nonmatch"):
                with st.status("Approving non-matches as new records...", expanded=True) as status:
                    progress_bar = st.progress(0.0)
                    def update_progress(curr, tot):
                        progress_bar.progress(curr / tot if tot > 0 else 1.0)
                    try:
                        import uuid as _bulk_uuid2
                        count = UploadService.approve_non_matches_as_new(
                            batch_id,
                            user_email=user_email,
                            language_id=language_id,
                            session_id=str(_bulk_uuid2.uuid4()),
                            progress_callback=update_progress
                        )
                        if count:
                            status.update(label=f"Approved {count} new records!", state="complete", expanded=False)
                            st.session_state["bulk_flash"] = ("success", f"{count} non-matching entr{'y' if count == 1 else 'ies'} approved as new records.")
                            import time as _time
                            _time.sleep(0.5)
                            st.rerun()
                        else:
                            status.update(label="No non-matching entries found.", state="complete", expanded=False)
                            st.info("No non-matching entries to approve.")
                    except Exception as e:
                        logger.error("Bulk approve non-matches failed: %s", e)
                        st.error(f"Bulk approve non-matches failed: {e}")

        # Discard Marked — available regardless of new/existing source
        if st.button("Discard All Marked", key="bulk_discard_marked"):
            with st.status("Discarding marked entries...", expanded=True) as status:
                progress_bar = st.progress(0.0)
                def update_progress(curr, tot):
                    progress_bar.progress(curr / tot if tot > 0 else 1.0)
                try:
                    count = UploadService.discard_marked(batch_id, progress_callback=update_progress)
                    if count:
                        status.update(label=f"Discarded {count} entries!", state="complete", expanded=False)
                        st.session_state["bulk_flash"] = ("success", f"Discarded {count} entr{'y' if count == 1 else 'ies'} marked for discard.")
                        import time as _time
                        _time.sleep(0.5)
                        st.rerun()
                    else:
                        status.update(label="No entries marked for discard.", state="complete", expanded=False)
                        st.info("No entries marked for discard.")
                except Exception as e:
                    logger.error("Discard ignored failed: %s", e)
                    st.error(f"Discard ignored failed: {e}")

        st.divider()
        # Records per page selector (at bottom)
        selected_page_size = st.selectbox(
            "Records per page",
            options=page_size_options,
            index=page_size_options.index(page_size),
            key="review_page_size_widget"
        )
        if selected_page_size != st.session_state.get("review_page_size"):
            st.session_state["review_page_size"] = selected_page_size
            st.session_state["review_current_page"] = 1
            # Persist to database
            PreferenceService.set_preference(user_email, "upload_review", "page_size", str(selected_page_size))
            st.rerun()

    # Slice rows for current page
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    page_rows = rows[start_idx:end_idx]

    # D-1: Render each entry (paginated)
    for row in page_rows:
        # Compute default status based on D-1 logic
        # Re-run suggest_matches data from the DB row itself
        has_suggestion = row.suggested_record_id is not None
        match_type = row.match_type or ""

        # Cross-source info would require re-querying; use stored match_type
        # record_id_conflict is detected by checking if suggested_record belongs to different source
        record_id_conflict = False
        conflict_sources = []

        # Parse record_id from mdf_data for conflict check
        uploaded_record_id = None
        for line in row.mdf_data.split('\n'):
            stripped = line.lstrip()
            if stripped.startswith('\\nt Record:'):
                val = stripped[len('\\nt Record:'):].strip()
                if val.isdigit():
                    uploaded_record_id = int(val)

        # Determine default status
        if row.status not in ('pending',):
            current_status = row.status
        elif record_id_conflict:
            current_status = 'create_new'
        elif has_suggestion and match_type == 'exact':
            current_status = 'matched'
        elif has_suggestion and match_type == 'base_form':
            current_status = 'matched'
        else:
            current_status = 'create_new'

        # Build display
        suggested_rec = suggested_records.get(row.suggested_record_id)
        suggested_display = ""
        if suggested_rec:
            suggested_display = f"{suggested_rec.lx} — {suggested_rec.ge or ''}"

        badge = ""
        if match_type == 'exact':
            badge = "🟢 exact"
        elif match_type == 'base_form':
            badge = "🟡 base_form"

        # Entry header
        with st.container(border=True):
            hdr_col1, hdr_col2, hdr_col3, hdr_col4 = st.columns([2, 3, 2, 3])
            with hdr_col1:
                st.markdown(f"**{row.lx}**")
            with hdr_col2:
                if suggested_display:
                    st.markdown(f"→ {suggested_display} {badge}")
                else:
                    st.markdown("→ *No match*")
            with hdr_col3:
                # Status selector
                status_map = {
                    "Matched": "matched",
                    "Create New Record": "create_new",
                    "Create Homonym": "create_homonym",
                    "Discard Entry": "discard",
                    "Ignored": "ignored",
                }
                status_options = list(status_map.keys())
                # Internal status to display name
                rev_status_map = {v: k for k, v in status_map.items()}
                
                display_status = rev_status_map.get(current_status, "Create New Record")
                default_idx = status_options.index(display_status)

                selected_label = st.selectbox(
                    "Status",
                    status_options,
                    index=default_idx,
                    key=f"status_{row.id}",
                    label_visibility="collapsed",
                )
                selected_status = status_map[selected_label]

                # Apply status change if different from DB
                if selected_status != row.status:
                    try:
                        if selected_status == 'matched' and has_suggestion:
                            UploadService.confirm_match(row.id)
                        elif selected_status == 'create_new':
                            # Set status directly
                            _set_queue_status(row.id, 'create_new')
                        elif selected_status == 'create_homonym':
                            UploadService.mark_as_homonym(row.id)
                        elif selected_status == 'discard':
                            UploadService.mark_as_discard(row.id)
                        elif selected_status == 'ignored':
                            UploadService.ignore_entry(row.id)
                    except Exception as e:
                        logger.error("Status change failed: %s", e)

            with hdr_col4:
                # D-1c: Per-record Apply Now button
                actionable = selected_status in ('matched', 'create_new', 'create_homonym', 'discard')
                if st.button(
                    "Apply Now",
                    key=f"apply_{row.id}",
                    disabled=not actionable,
                ):
                    try:
                        session_id = str(_uuid.uuid4())
                        result = UploadService.apply_single(
                            queue_id=row.id,
                            user_email=user_email,
                            language_id=language_id,
                            session_id=session_id,
                        )
                        # Populate search entries (skip for discards)
                        if result.get('record_id'):
                            UploadService.populate_search_entries([result['record_id']])
                            st.success(f"✅ Applied: {result['lx']} → record #{result['record_id']}")
                        else:
                            st.success(f"✅ Discarded: {result['lx']}")
                        st.rerun()
                    except Exception as e:
                        logger.error("Apply single failed: %s", e)
                        st.error(f"Apply failed: {e}")

            # Dynamic cross-source informational note
            cross_sources = UploadService.get_cross_source_info(row.lx, source_id)
            if cross_sources:
                st.caption(f"Also in: {', '.join(cross_sources)}")

            # Record-id conflict warning
            if record_id_conflict and conflict_sources:
                st.warning(
                    f"⚠️ Record #{uploaded_record_id} belongs to "
                    f"{', '.join(conflict_sources)} — mark as 'create new' "
                    f"to avoid cross-source conflict"
                )

            # D-2: Manual match override
            with st.expander("🔍 Change match", expanded=False):
                search_query = st.text_input(
                    "Search existing records (by headword or gloss)",
                    key=f"match_search_{row.id}",
                    label_visibility="collapsed",
                    placeholder="Search by headword or gloss…",
                )
                if search_query:
                    candidates = UploadService.search_records_for_override(
                        source_id, search_query
                    )
                    if candidates:
                        options = [
                            f"#{c['id']} — {c['lx']} (hm {c['hm']}) — {c['ge']}"
                            for c in candidates
                        ]
                        chosen = st.selectbox(
                            "Select record",
                            options,
                            key=f"match_select_{row.id}",
                            label_visibility="collapsed",
                        )
                        chosen_idx = options.index(chosen)
                        chosen_record_id = candidates[chosen_idx]["id"]
                        if st.button("Confirm Override", key=f"match_confirm_{row.id}"):
                            try:
                                UploadService.confirm_match(row.id, chosen_record_id)
                                # Clear the cached selectbox value so it picks up
                                # the new 'matched' status from the DB on rerun.
                                st.session_state.pop(f"status_{row.id}", None)
                                st.success(
                                    f"✅ Match overridden to record #{chosen_record_id}"
                                )
                                st.rerun()
                            except Exception as e:
                                logger.error("Match override failed: %s", e)
                                st.error(f"Override failed: {e}")
                    else:
                        st.info("No matching records found.")

            # D-1b: Full-width side-by-side comparison (always visible)
            st.html(
                """
                <style>
                /* Target only columns inside the bordered container to avoid affecting sidebar or headers */
                [data-testid="stElementContainer"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"] {
                    padding-left: 0rem !important;
                    padding-right: 0rem !important;
                }
                /* Add back spacing between columns EXCEPT the first one in any row */
                [data-testid="stElementContainer"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"] + [data-testid="column"] {
                    padding-left: 1rem !important;
                }
                </style>
                """
            )
            col_left, col_right = st.columns([1, 1])
            with col_left:
                if suggested_rec:
                    st.markdown(f"**Existing record (#{suggested_rec.id})**")
                    render_mdf_block(suggested_rec.mdf_data)
                else:
                    st.markdown("**No existing record**")
                    st.info("This entry will be created as a new record.")
            with col_right:
                st.markdown("**New (uploaded)**")
                render_mdf_block(row.mdf_data)

                # Show prev/next nav below the last record's "New (uploaded)" box
                if row == page_rows[-1] and total_pages > 1:
                    nav_c1, nav_c2, nav_c3 = st.columns([2, 3, 2])
                    with nav_c1:
                        if st.button("◀ Previous", key="main_page_prev", disabled=(current_page <= 1)):
                            st.session_state["review_current_page"] = current_page - 1
                            st.rerun()
                    with nav_c3:
                        if st.button("Next ▶", key="main_page_next", disabled=(current_page >= total_pages), width="stretch"):
                            st.session_state["review_current_page"] = current_page + 1
                            st.rerun()


def _set_queue_status(queue_id, status):
    """Directly set a matchup_queue row's status."""
    from src.database import get_session
    from src.database.models.workflow import MatchupQueue
    session = get_session()
    try:
        row = session.get(MatchupQueue, queue_id)
        if row:
            row.status = status
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    upload_mdf()
