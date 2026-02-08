# Copyright (c) 2026 Brothertown Language
def index():
    import streamlit as st
    
    # Handle logout reload if coming from logout page
    if st.session_state.get("trigger_logout_reload"):
        del st.session_state["trigger_logout_reload"]
        from src.frontend.ui_utils import reload_page_at_root
        reload_page_at_root()
        st.stop()

    st.title("SNEA Shoebox Editor")
    st.write("Welcome to the SNEA Online Shoebox Editor.")
    st.info("This is the main entry point.")
    
    st.subheader("Navigation")
    if st.button("Go to System Status"):
        st.switch_page("pages/system_status.py")
        
    st.divider()
    st.subheader("Record Links (Examples)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Record 1"):
            st.query_params["id"] = 1
            st.switch_page("pages/view_record.py")
    with col2:
        if st.button("View Record 42"):
            st.query_params["id"] = 42
            st.switch_page("pages/view_record.py")

if __name__ == "__main__":
    index()
