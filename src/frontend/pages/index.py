# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
"""
def index():
    import streamlit as st
    
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
