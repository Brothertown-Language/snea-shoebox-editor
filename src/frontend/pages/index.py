# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import pandas as pd
from src.services.statistics_service import StatisticsService
from src.frontend.ui_utils import apply_standard_layout_css

def index():
    apply_standard_layout_css()
    # Handle logout reload if coming from logout page
    if st.session_state.get("trigger_logout_reload"):
        del st.session_state["trigger_logout_reload"]
        from src.frontend.ui_utils import reload_page_at_root
        reload_page_at_root()
        st.stop()

    # --- Statistics Section ---
    st.markdown("### Database Statistics")
    
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
        st.subheader("Primary Language Distribution")
        primary_lang_data = StatisticsService.get_language_distribution(primary_only=True)
        if primary_lang_data:
            df_primary = pd.DataFrame(list(primary_lang_data.items()), columns=["Language", "Count"])
            st.bar_chart(df_primary.set_index("Language"))
        else:
            st.info("No primary language data available.")
            
    with chart_col2:
        st.subheader("All Languages Distribution")
        all_lang_data = StatisticsService.get_language_distribution(primary_only=False)
        if all_lang_data:
            df_all = pd.DataFrame(list(all_lang_data.items()), columns=["Language", "Count"])
            st.bar_chart(df_all.set_index("Language"))
            
            # UX Note: Explain if distributions are identical
            if all_lang_data == primary_lang_data:
                st.caption("ℹ️ Currently identical to Primary distribution (no secondary languages assigned).")
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
    source_distribution = StatisticsService.get_source_distribution()
    if source_distribution:
        # Get source IDs to create links
        from src.services.linguistic_service import LinguisticService
        sources = LinguisticService.get_sources_with_counts()
        source_id_map = {s['name']: s['id'] for s in sources}
        
        df_source = pd.DataFrame(list(source_distribution.items()), columns=["Source", "Count"])
        st.bar_chart(df_source.set_index("Source"))
        
        # Add links to sources
        st.write("**Explore by Source:**")
        cols = st.columns(3)
        for i, (source_name, count) in enumerate(source_distribution.items()):
            source_id = source_id_map.get(source_name)
            if source_id:
                if cols[i % 3].button(f"{source_name} ({count})", key=f"src_btn_{source_id}", use_container_width=True):
                    st.query_params["source"] = str(source_id)
                    st.query_params["page"] = "1"
                    st.switch_page("pages/records.py")
    else:
        st.info("No source data available.")

    st.subheader("Records by Status")
    status_data = StatisticsService.get_status_distribution()
    if status_data:
        df_status = pd.DataFrame(list(status_data.items()), columns=["Status", "Count"])
        st.bar_chart(df_status.set_index("Status"))
    else:
        st.info("No status data available.")

    st.divider()
    
    # Recent Activity
    st.subheader("Recent Activity")
    activity = StatisticsService.get_recent_activity()
    if activity:
        for i, item in enumerate(activity):
            with st.expander(f"Record {item['record_id']} ({item['lx']}) edited by {item['user']}"):
                st.write(f"**Time:** {item['timestamp']}")
                st.write(f"**Change:** {item['summary']}")
                
                if st.button("View in Records", icon="🔍", key=f"view_rec_{item['record_id']}_{i}"):
                    st.query_params["search"] = f"#{item['record_id']}"
                    st.query_params["search_mode"] = "FTS"
                    st.switch_page("pages/records.py")
    else:
        st.info("No recent activity recorded.")


if __name__ == "__main__":
    index()
