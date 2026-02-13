# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from src.logging_config import get_logger
from src.services.upload_service import UploadService
from src.database import get_session, UserActivityLog, EditHistory
from sqlalchemy import desc

logger = get_logger("snea.pages.batch_rollback")

def get_recent_sessions():
    """Fetch recent upload sessions that can be rolled back."""
    session = get_session()
    try:
        # 1. Get all upload_committed actions
        uploads = (
            session.query(UserActivityLog)
            .filter_by(action="upload_committed")
            .order_by(desc(UserActivityLog.timestamp))
            .limit(50)
            .all()
        )
        
        # 2. Get all rollback actions to filter out already rolled back sessions
        rollbacks = (
            session.query(UserActivityLog)
            .filter_by(action="batch_rollback")
            .all()
        )
        rolled_back_ids = {r.session_id for r in rollbacks if r.session_id}
        
        available_sessions = []
        for u in uploads:
            if u.session_id and u.session_id not in rolled_back_ids:
                # Count affected records from EditHistory
                count = (
                    session.query(EditHistory)
                    .filter_by(session_id=u.session_id)
                    .distinct(EditHistory.record_id)
                    .count()
                )
                if count > 0:
                    available_sessions.append({
                        "session_id": u.session_id,
                        "timestamp": u.timestamp,
                        "user": u.user_email,
                        "details": u.details,
                        "record_count": count
                    })
        return available_sessions
    finally:
        session.close()

@st.dialog("Confirm Rollback")
def confirm_rollback_dialog(session_data):
    st.warning(f"Are you sure you want to rollback session **{session_data['session_id'][:8]}...**?")
    st.write(f"- **User:** {session_data['user']}")
    st.write(f"- **Date:** {session_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"- **Affected Records:** {session_data['record_count']}")
    st.write(f"- **Details:** {session_data['details']}")
    
    st.error("This action will restore records to their previous state and delete newly created records. This cannot be undone.")
    
    if st.button("Yes, Rollback Session", type="primary", use_container_width=True):
        with st.spinner("Rolling back..."):
            try:
                result = UploadService.rollback_session(
                    session_data['session_id'], 
                    user_email=st.session_state.get("user_email", "system")
                )
                st.success(f"Rollback successful! {result['rolled_back_count']} updated, {result['deleted_count']} deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Rollback failed: {e}")
                logger.error("Rollback failed for session %s: %s", session_data['session_id'], e)

def main():
    """
    UI for Phase E-2: Batch Rollback Support.
    Allows administrators to rollback upload sessions.
    """
    st.title("🔙 Batch Rollback")
    
    st.write("Administrators can use this page to undo entire upload sessions. "
             "Only sessions that haven't been previously rolled back are shown.")
    
    sessions = get_recent_sessions()
    
    if not sessions:
        st.info("No reversible upload sessions found.")
        return

    # Display sessions in a table-like view
    st.subheader("Recent Upload Sessions")
    
    cols = st.columns([2, 2, 3, 1, 1])
    cols[0].write("**Date**")
    cols[1].write("**User**")
    cols[2].write("**Details**")
    cols[3].write("**Records**")
    cols[4].write("**Action**")
    
    st.divider()
    
    for s in sessions:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 1, 1])
            c1.write(s["timestamp"].strftime("%Y-%m-%d %H:%M"))
            c2.write(s["user"])
            c3.write(s["details"])
            c4.write(str(s["record_count"]))
            
            if c5.button("Undo", key=f"undo_{s['session_id']}", help="Rollback this session"):
                confirm_rollback_dialog(s)

if __name__ == "__main__":
    main()
