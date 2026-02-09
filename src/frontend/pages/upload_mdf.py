# Copyright (c) 2026 Brothertown Language
def upload_mdf():
    import streamlit as st
    from src.database import get_session
    from src.database.models.core import Source
    from src.services.upload_service import UploadService
    from src.frontend.ui_utils import hide_sidebar_nav
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
    if st.session_state.get("show_pending_batches"):
        _render_pending_batches_view()
        return

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    # Collapse default top padding in both sidebar and main panel
    st.html(
        """
        <style>
        .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0px !important; margin-top: 0px !important; }
        header[data-testid="stHeader"] { height: 0px !important; min-height: 0px !important; padding: 0px !important; overflow: visible !important; }
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stSidebarHeader"] { height: 2rem !important; min-height: 2rem !important; padding: 0px !important; }
        div[data-testid="stSidebarUserContent"] { padding-top: 0px !important; }
        </style>
        """
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

        CREATE_NEW_LABEL = "+ Add new source…"
        source_options.append(CREATE_NEW_LABEL)

        selected_source = st.selectbox("Target source collection", source_options)

        # C-4a: Create new source inline
        selected_source_id = None
        if selected_source == CREATE_NEW_LABEL:
            st.markdown("#### Create a new source")
            new_name = st.text_input(
                "Source name",
                placeholder="Natick Dictionary — Trumbull",
            )
            new_description = st.text_input("Description (optional)")
            if st.button("Create Source"):
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
                            st.success(f"Source '{new_name.strip()}' created.")
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

        st.divider()

        # C-6a: Pending uploads — open dedicated view in main panel
        if st.button("Pending Uploads", key="pending_uploads_btn"):
            st.session_state["show_pending_batches"] = True
            st.rerun()

        st.divider()
        if st.button("← Back to Main Menu", key="back_to_main"):
            st.session_state.pop("review_batch_id", None)
            st.switch_page("pages/index.py")

    # ── Main panel: upload content ────────────────────────────────
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")

        with st.expander("Raw file preview", expanded=False):
            st.code(file_content, language=None)

        # C-5: Parse and display upload summary
        try:
            entries = UploadService.parse_upload(file_content)
            st.success(f"**{len(entries)}** entries found in `{uploaded_file.name}`.")

            # Build summary table
            rows = []
            for e in entries:
                rows.append({
                    "lx": e.get("lx", ""),
                    "ps": e.get("ps", ""),
                    "ge": e.get("ge", ""),
                })
            st.dataframe(rows, use_container_width=True, height=300)

            # Store parsed data in session state for later phases
            st.session_state["upload_entries"] = entries
            st.session_state["upload_filename"] = uploaded_file.name
            st.session_state["upload_source_id"] = selected_source_id

            # C-6: Stage & Match button
            if selected_source_id is None:
                st.warning("Select a source collection before staging.")
            else:
                user_email = st.session_state.get("user_email", "")
                # Disable after use until a new file is uploaded
                # Use Streamlit's unique file_id to distinguish re-uploads of the same filename
                current_file_id = uploaded_file.file_id
                already_staged = st.session_state.get("upload_staged_file_id") == current_file_id
                if st.button("Stage & Match", type="primary", disabled=already_staged):
                    try:
                        batch_id = UploadService.stage_entries(
                            user_email=user_email,
                            source_id=selected_source_id,
                            entries=entries,
                            filename=uploaded_file.name,
                        )
                        match_results = UploadService.suggest_matches(batch_id)
                        st.session_state["upload_batch_id"] = batch_id
                        st.session_state["upload_match_results"] = match_results
                        st.session_state["upload_staged_file_id"] = current_file_id
                        # Switch to dedicated review view
                        st.session_state["review_batch_id"] = batch_id
                        st.rerun()
                    except Exception as e:
                        logger.error("Stage & Match failed: %s", e)
                        st.error(f"Stage & Match failed: {e}")

        except ValueError as e:
            st.error(str(e))
    else:
        st.info("Upload an MDF file using the sidebar to get started.")


def _render_pending_batches_view():
    """Dedicated main-panel view listing all pending batches for the current user."""
    import streamlit as st
    from src.services.upload_service import UploadService
    from src.frontend.ui_utils import hide_sidebar_nav
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf.pending")

    hide_sidebar_nav()

    st.html(
        """
        <style>
        .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0px !important; margin-top: 0px !important; }
        header[data-testid="stHeader"] { height: 0px !important; min-height: 0px !important; padding: 0px !important; overflow: visible !important; }
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stSidebarHeader"] { height: 2rem !important; min-height: 2rem !important; padding: 0px !important; }
        div[data-testid="stSidebarUserContent"] { padding-top: 0px !important; }
        </style>
        """
    )

    with st.sidebar:
        st.header("Pending Uploads")
        st.divider()
        if st.button("← Back to MDF Upload", key="pending_back_to_upload"):
            st.session_state.pop("show_pending_batches", None)
            st.rerun()
            return
        if st.button("← Back to Main Menu", key="pending_back_to_main"):
            st.session_state.pop("show_pending_batches", None)
            st.switch_page("pages/index.py")

    # Main panel: list pending batches
    user_email = st.session_state.get("user_email", "")
    if not user_email:
        st.warning("No user session found.")
        return

    batches = UploadService.list_pending_batches(user_email)

    if not batches:
        st.info("No pending upload batches.")
        return

    st.subheader(f"{len(batches)} Pending Batch{'es' if len(batches) != 1 else ''}")

    for b in batches:
        ts = b["uploaded_at"]
        ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "unknown"
        batch_id = b["batch_id"]

        with st.container():
            st.markdown("---")
            col_info, col_review, col_discard = st.columns([5, 1, 1])
            with col_info:
                st.markdown(
                    f"**{b['source_name']}** — {b['filename'] or 'unnamed'}  \n"
                    f"{b['entry_count']} entries · {ts_str}"
                )
            with col_review:
                if st.button("Review", key=f"review_{batch_id}", type="primary"):
                    st.session_state["review_batch_id"] = batch_id
                    st.session_state.pop("show_pending_batches", None)
                    st.rerun()
            with col_discard:
                if st.button("Discard", key=f"discard_{batch_id}"):
                    try:
                        count = UploadService.discard_all(batch_id)
                        st.toast(f"Discarded {count} entries.")
                        st.rerun()
                    except Exception as e:
                        logger.error("Discard batch failed: %s", e)
                        st.error(f"Discard failed: {e}")


def _render_review_view():
    """Dedicated full-width review view for a selected batch.

    All controls live in the sidebar; the main panel is reserved
    exclusively for record comparison content.
    """
    import streamlit as st
    from src.services.upload_service import UploadService
    from src.frontend.ui_utils import hide_sidebar_nav
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf.review")
    batch_id = st.session_state.get("review_batch_id")
    user_email = st.session_state.get("user_email", "")

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    # Collapse default top padding in both sidebar and main panel
    st.html(
        """
        <style>
        .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] .block-container { padding-top: 0px !important; margin-top: 0px !important; }
        section[data-testid="stSidebar"] > div:first-child { padding-top: 0px !important; margin-top: 0px !important; }
        header[data-testid="stHeader"] { height: 0px !important; min-height: 0px !important; padding: 0px !important; overflow: visible !important; }
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stSidebarHeader"] { height: 2rem !important; min-height: 2rem !important; padding: 0px !important; }
        div[data-testid="stSidebarUserContent"] { padding-top: 0px !important; }
        </style>
        """
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

    # ── Sidebar bottom: records per page, re-match & back ─────────
    with st.sidebar:
        st.divider()

        # Records per page selector
        st.selectbox(
            "Records per page",
            [1, 5, 10, 25, 50],
            index=[1, 5, 10, 25, 50].index(st.session_state.get("review_page_size", 1)),
            key="review_page_size",
        )

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
            st.info("No entries in this batch (all applied or discarded).")
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

    # ── Compute pagination ──────────────────────────────────────────
    total_entries = len(rows)
    page_size_options = [1, 5, 10, 25, 50]
    page_size = st.session_state.get("review_page_size", page_size_options[0])
    if page_size not in page_size_options:
        page_size = page_size_options[0]
    total_pages = max(1, (total_entries + page_size - 1) // page_size)
    current_page = st.session_state.get("review_current_page", 1)
    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1

    # ── Sidebar: page nav (top), bulk actions, then records per page at bottom ─
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

        # D-1a: Bulk approval action buttons
        if is_new_source:
            if st.button("Approve All as New Records", key="bulk_approve_new"):
                try:
                    UploadService.approve_all_new_source(batch_id)
                    st.success("All entries approved as new records.")
                    st.rerun()
                except Exception as e:
                    logger.error("Bulk approve failed: %s", e)
                    st.error(f"Bulk approve failed: {e}")
        else:
            if st.button("Approve All Matched", key="bulk_approve_matched"):
                try:
                    UploadService.approve_all_by_record_match(batch_id)
                    st.success("All matched entries approved.")
                    st.rerun()
                except Exception as e:
                    logger.error("Bulk approve matched failed: %s", e)
                    st.error(f"Bulk approve matched failed: {e}")
            if st.button("Approve Non-Matches as New", key="bulk_approve_nonmatch"):
                try:
                    UploadService.approve_non_matches_as_new(batch_id)
                    st.success("Non-matching entries approved as new records.")
                    st.rerun()
                except Exception as e:
                    logger.error("Bulk approve non-matches failed: %s", e)
                    st.error(f"Bulk approve non-matches failed: {e}")

        # Discard Ignored — available regardless of new/existing source
        if st.button("Discard Ignored", key="bulk_discard_ignored"):
            try:
                count = UploadService.discard_ignored(batch_id)
                if count:
                    st.success(f"Discarded {count} ignored entr{'y' if count == 1 else 'ies'}.")
                    st.rerun()
                else:
                    st.info("No ignored entries to discard.")
            except Exception as e:
                logger.error("Discard ignored failed: %s", e)
                st.error(f"Discard ignored failed: {e}")

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
        with st.container():
            st.markdown(f"---")
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
                status_options = ['matched', 'create_new', 'create_homonym', 'ignore']
                # Map current_status to index
                if current_status in status_options:
                    default_idx = status_options.index(current_status)
                else:
                    default_idx = 1  # create_new
                selected_status = st.selectbox(
                    "Status",
                    status_options,
                    index=default_idx,
                    key=f"status_{row.id}",
                    label_visibility="collapsed",
                )
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
                        elif selected_status == 'ignore':
                            UploadService.ignore_entry(row.id)
                    except Exception as e:
                        logger.error("Status change failed: %s", e)

            with hdr_col4:
                # D-1c: Per-record Apply Now button
                actionable = selected_status in ('matched', 'create_new', 'create_homonym')
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
                        # Populate search entries
                        UploadService.populate_search_entries([result['record_id']])
                        st.success(f"✅ Applied: {result['lx']} → record #{result['record_id']}")
                        st.rerun()
                    except Exception as e:
                        logger.error("Apply single failed: %s", e)
                        st.error(f"Apply failed: {e}")

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
            col_left, col_right = st.columns([1, 1])
            with col_left:
                if suggested_rec:
                    st.markdown(f"**Existing record (#{suggested_rec.id})**")
                    st.code(suggested_rec.mdf_data, language=None)
                else:
                    st.markdown("**No existing record**")
                    st.info("This entry will be created as a new record.")
            with col_right:
                st.markdown("**New (uploaded)**")
                st.code(row.mdf_data, language=None)

                # Show prev/next nav below the last record's "New (uploaded)" box
                if row == page_rows[-1] and total_pages > 1:
                    nav_c1, nav_c2, nav_c3 = st.columns([2, 3, 2])
                    with nav_c1:
                        if st.button("◀ Previous", key="main_page_prev", disabled=(current_page <= 1)):
                            st.session_state["review_current_page"] = current_page - 1
                            st.rerun()
                    with nav_c3:
                        if st.button("Next ▶", key="main_page_next", disabled=(current_page >= total_pages), use_container_width=True):
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
