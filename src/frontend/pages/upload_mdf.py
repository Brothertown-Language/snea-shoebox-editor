# Copyright (c) 2026 Brothertown Language
def upload_mdf():
    import streamlit as st
    from src.database import get_session
    from src.database.models.core import Source
    from src.services.upload_service import UploadService
    from src.logging_config import get_logger

    logger = get_logger("snea.upload_mdf")

    # C-2: Role guard — only editor or admin
    user_role = st.session_state.get("user_role")
    if user_role not in ("editor", "admin"):
        st.error("You do not have permission to access this page. Editor or admin role required.")
        return

    st.title("Upload MDF File")

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
                if st.button("Stage & Match", type="primary"):
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
                        st.success(f"Staged **{len(entries)}** entries (batch `{batch_id[:8]}…`). "
                                   f"**{sum(1 for m in match_results if m.get('suggested_record_id') is not None)}** "
                                   f"matches suggested.")
                    except Exception as e:
                        logger.error("Stage & Match failed: %s", e)
                        st.error(f"Stage & Match failed: {e}")

        except ValueError as e:
            st.error(str(e))

    # C-6a: Pending upload batch selector
    st.divider()
    st.subheader("Pending Uploads")
    user_email = st.session_state.get("user_email", "")
    if user_email:
        batches = UploadService.list_pending_batches(user_email)
    else:
        batches = []

    if batches:
        batch_labels = []
        batch_map = {}
        for b in batches:
            ts = b["uploaded_at"]
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "unknown"
            label = f"{b['source_name']} — {b['filename'] or 'unnamed'} ({b['entry_count']} entries, {ts_str})"
            batch_labels.append(label)
            batch_map[label] = b["batch_id"]

        col_sel, col_btn = st.columns([4, 1])
        with col_sel:
            selected_label = st.selectbox("Select a pending batch", batch_labels, key="batch_selector")
        selected_batch_id = batch_map.get(selected_label)

        # C-6b: Re-Match button
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Re-Match", key="rematch_btn"):
                try:
                    match_results = UploadService.rematch_batch(selected_batch_id)
                    st.session_state["upload_batch_id"] = selected_batch_id
                    st.session_state["upload_match_results"] = match_results
                    st.success(f"Re-matched batch `{selected_batch_id[:8]}…`. "
                               f"**{sum(1 for m in match_results if m.get('suggested_record_id') is not None)}** "
                               f"matches found.")
                except Exception as e:
                    logger.error("Re-Match failed: %s", e)
                    st.error(f"Re-Match failed: {e}")

        # Store selected batch for downstream phases
        st.session_state["upload_batch_id"] = selected_batch_id
    else:
        st.info("No pending upload batches.")


if __name__ == "__main__":
    upload_mdf()
