# Copyright (c) 2026 Brothertown Language
import streamlit as st
import pandas as pd
from src.services.statistics_service import StatisticsService

def index():
    # Handle logout reload if coming from logout page
    if st.session_state.get("trigger_logout_reload"):
        del st.session_state["trigger_logout_reload"]
        from src.frontend.ui_utils import reload_page_at_root
        reload_page_at_root()
        st.stop()

    st.title("SNEA Shoebox Editor")
    st.write("Welcome to the SNEA Online Shoebox Editor.")
    
    # --- Statistics Section ---
    st.header("Database Statistics")
    
    # Summary Metrics
    stats = StatisticsService.get_summary_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", stats["records"])
    col2.metric("Sources", stats["sources"])
    col3.metric("Languages", stats["languages"])
    
    st.divider()
    
    # Distribution Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Records by Status")
        status_data = StatisticsService.get_status_distribution()
        if status_data:
            df_status = pd.DataFrame(list(status_data.items()), columns=["Status", "Count"])
            st.bar_chart(df_status.set_index("Status"))
        else:
            st.info("No status data available.")
            
    with chart_col2:
        st.subheader("Language Distribution")
        lang_data = StatisticsService.get_language_distribution()
        if lang_data:
            df_lang = pd.DataFrame(list(lang_data.items()), columns=["Language", "Count"])
            st.bar_chart(df_lang.set_index("Language"))
        else:
            st.info("No language data available.")

    st.subheader("Top Parts of Speech")
    pos_data = StatisticsService.get_top_parts_of_speech()
    if pos_data:
        df_pos = pd.DataFrame(list(pos_data.items()), columns=["POS", "Count"])
        st.bar_chart(df_pos.set_index("POS"))
    else:
        st.info("No POS data available.")

    st.subheader("Records per Source")
    source_data = StatisticsService.get_source_distribution()
    if source_data:
        df_source = pd.DataFrame(list(source_data.items()), columns=["Source", "Count"])
        st.bar_chart(df_source.set_index("Source"))
    else:
        st.info("No source data available.")

    st.divider()
    
    # Recent Activity
    st.subheader("Recent Activity")
    activity = StatisticsService.get_recent_activity()
    if activity:
        for item in activity:
            with st.expander(f"Record {item['record_id']} ({item['lx']}) edited by {item['user']}"):
                st.write(f"**Time:** {item['timestamp']}")
                st.write(f"**Change:** {item['summary']}")
                if st.button(f"View Record {item['record_id']}", key=f"btn_{item['record_id']}_{item['timestamp']}"):
                    st.query_params["id"] = item['record_id']
                    st.switch_page("pages/view_record.py")
    else:
        st.info("No recent activity recorded.")

    st.divider()
    st.subheader("Navigation")
    if st.button("Go to System Status"):
        st.switch_page("pages/system_status.py")

if __name__ == "__main__":
    index()
