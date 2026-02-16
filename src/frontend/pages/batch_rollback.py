# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from sqlalchemy import desc, text

def get_recent_sessions():
    """Fetch recent upload sessions that can be rolled back using discrete steps."""
    from src.database import get_session
    session = get_session()
    try:
        # Step 1: Discover sessions that had more than 1 record initially.
        # This query is kept simple and focused on discovery.
        sessions_query = text("""
            SELECT session_id, min(timestamp) as earliest_ts, 
                   min(user_email) as user_email, min(source_name) as source_name,
                   min(full_name) as full_name
            FROM (
                SELECT eh.session_id, eh.timestamp, eh.user_email,
                       s.name as source_name, u.full_name
                FROM edit_history eh
                JOIN records r ON r.id = eh.record_id
                JOIN sources s ON s.id = r.source_id
                LEFT JOIN users u ON u.email = eh.user_email
                WHERE r.is_deleted = False
            ) AS history
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY earliest_ts DESC
            LIMIT 50;
        """)
        
        raw_sessions = session.execute(sessions_query).all()
        
        available_sessions = []
        for row in raw_sessions:
            sid = row.session_id
            
            # Step 2: Discrete count - Total records touched by this session
            total_q = text("SELECT count(DISTINCT record_id) FROM edit_history WHERE session_id = :sid")
            total_count = session.execute(total_q, {"sid": sid}).scalar()
            
            if total_count <= 1:
                continue # Skip non-batch sessions

            # Step 3: Discrete count - Records where this session is still the LATEST (leaf)
            reversible_q = text("""
                SELECT count(*) 
                FROM (
                    SELECT DISTINCT ON (record_id) session_id
                    FROM edit_history
                    WHERE record_id IN (SELECT record_id FROM edit_history WHERE session_id = :sid)
                    ORDER BY record_id, timestamp DESC, id DESC
                ) as latest
                WHERE session_id = :sid
            """)
            reversible_count = session.execute(reversible_q, {"sid": sid}).scalar()

            if reversible_count == 0:
                continue # Skip sessions where all records have been superseded

            full_name = row.full_name
            email = row.user_email
            display_user = f"{full_name} ({email})" if full_name else email

            available_sessions.append({
                "session_id": sid,
                "timestamp": row.earliest_ts,
                "user": display_user,
                "source_name": row.source_name,
                "record_count": f"{reversible_count} / {total_count}",
                "reversible_count": reversible_count
            })

        return available_sessions
    finally:
        session.close()

@st.dialog("Download Rollback MDF")
def download_mdf_dialog(session_data):
    """Prompt the user to download the MDF data for a session."""
    from src.services.upload_service import UploadService
    from src.services.identity_service import IdentityService
    session_id = session_data.get('session_id')
    st.write(f"Preparing records from session **{session_id[:8]}** for download.")
    st.info("This will include all records that are currently eligible for rollback.")
    
    with st.spinner("Generating MDF content..."):
        mdf_content = UploadService.get_session_rollback_mdf(session_id)
    
    if mdf_content:
        github_username = IdentityService.get_github_username(st.session_state.get("user_email"))
        filename = UploadService.generate_mdf_filename(
            "rollback", 
            session_data.get('source_name', 'unknown'), 
            session_data.get('timestamp'),
            github_username=github_username
        )
        st.download_button(
            label="Download MDF File",
            data=mdf_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
        st.caption("Click the button above to save the file to your computer.")
    else:
        st.error("No records found that can be rolled back for this session.")
        if st.button("Close"):
            st.rerun()

@st.dialog("Confirm Rollback")
def confirm_rollback_dialog(session_data):
    from src.services.upload_service import UploadService
    from src.logging_config import get_logger
    logger = get_logger("snea.pages.batch_rollback")
    session_id = session_data.get('session_id')
    st.warning(f"Are you sure you want to rollback session **{session_id[:8]}...**?")
    st.write(f"- **Source:** {session_data['source_name']}")
    st.write(f"- **User:** {session_data['user']}")
    st.write(f"- **Date:** {session_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"- **Records (reversible/total):** {session_data['record_count']}")
    
    st.error("This action will restore records to their previous state and delete newly created records. Superseded records will be skipped. This cannot be undone.")
    
    if st.button("Yes, Rollback Session", type="primary", use_container_width=True):
        from src.frontend.ui_utils import handle_ui_error
        # We'll use a placeholder in the dialog for progress
        progress_container = st.container()
        with progress_container:
            status = st.status("Initializing rollback...", expanded=True)
            progress_bar = st.progress(0.0)
            
            def update_progress(curr, total):
                status.update(label=f"Rolling back: {curr}/{total} records...")
                progress_bar.progress(curr / total if total > 0 else 1.0)
            
            try:
                result = UploadService.rollback_session(
                    session_id, 
                    user_email=st.session_state.get("user_email", "system"),
                    progress_callback=update_progress
                )
                
                msg = f"Rollback successful! {result['rolled_back_count']} updated, {result['deleted_count']} deleted."
                if result['skipped_count'] > 0:
                    msg += f" {result['skipped_count']} records skipped (already modified later)."
                
                status.update(label="Rollback Complete", state="complete")
                st.success(msg)
                
                import time
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                status.update(label="Rollback Failed", state="error")
                handle_ui_error(e, "Rollback failed.", logger_name="snea.pages.batch_rollback")

def main():
    """
    UI for Phase E-2: Batch Rollback Support.
    Allows administrators to rollback upload sessions.
    """
    from src.frontend.ui_utils import apply_standard_layout_css, handle_ui_error, hide_sidebar_nav, render_back_to_main_button
    from src.services.identity_service import IdentityService
    # Role guard — only admin
    user_role = st.session_state.get("user_role")
    if user_role not in ("admin",):
        st.error("You do not have permission to access this page. Administrator role required.")
        return

    # Hide the main navigation menu — this view owns the sidebar entirely
    hide_sidebar_nav()

    apply_standard_layout_css()
    
    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("**Batch Rollback**")
        st.divider()
        render_back_to_main_button()

    # ── Main Content ──────────────────────────────────────────────
    st.write("Undo entire upload sessions. "
             "Only reversible sessions are shown below.")
    
    sessions = get_recent_sessions()
    
    if not sessions:
        st.info("No reversible upload sessions found.")
        return

    # Display sessions in a table-like view
    st.subheader("Recent Upload Sessions")
    
    # Pagination configuration
    PAGE_SIZE = 5
    if "rollback_page_idx" not in st.session_state:
        st.session_state.rollback_page_idx = 0
    
    total_sessions = len(sessions)
    total_pages = (total_sessions + PAGE_SIZE - 1) // PAGE_SIZE
    
    # Safety check for page index after rollbacks/refresh
    if st.session_state.rollback_page_idx >= total_pages:
        st.session_state.rollback_page_idx = max(0, total_pages - 1)
        
    start_idx = st.session_state.rollback_page_idx * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_sessions)
    page_sessions = sessions[start_idx:end_idx]

    cols = st.columns([2, 2, 3, 1, 1.5])
    cols[0].write("**Date**")
    cols[1].write("**User**")
    cols[2].write("**Source**")
    cols[3].write("**Records**")
    cols[4].write("**Actions**")
    
    st.divider()
    
    for s in page_sessions:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 1, 1.5])
            c1.write(s["timestamp"].strftime("%Y-%m-%d %H:%M"))
            c2.write(s["user"])
            c3.write(s["source_name"])
            c4.write(str(s["record_count"]))
            
            # Action buttons
            btn_cols = c5.columns(2)
            
            # 1. Download MDF (Deferred via Dialog)
            if btn_cols[0].button("📥", key=f"dl_{s['session_id']}", help="Download MDF of records"):
                # Use a specific key in session_state to store the full session_id for the dialog
                st.session_state.current_dl_session = s['session_id']
                download_mdf_dialog(s)
            
            # 2. Undo
            if btn_cols[1].button("🔙", key=f"undo_{s['session_id']}", help="Rollback this session"):
                st.session_state.current_rollback_session = s['session_id']
                confirm_rollback_dialog(s)

    # Pagination controls
    if total_pages > 1:
        st.divider()
        nav_cols = st.columns([1, 2, 1])
        
        with nav_cols[0]:
            if st.button("Previous", icon="⬅️", disabled=st.session_state.rollback_page_idx == 0, use_container_width=True):
                st.session_state.rollback_page_idx -= 1
                st.rerun()
                
        with nav_cols[1]:
            st.markdown(f"<p style='text-align: center;'>Page {st.session_state.rollback_page_idx + 1} of {total_pages}</p>", unsafe_allow_html=True)
            
        with nav_cols[2]:
            if st.button("Next", icon="➡️", disabled=st.session_state.rollback_page_idx >= total_pages - 1, use_container_width=True):
                st.session_state.rollback_page_idx += 1
                st.rerun()

if __name__ == "__main__":
    main()
