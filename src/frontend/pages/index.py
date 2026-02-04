# Copyright (c) 2026 Brothertown Language
import streamlit as st

def index():
    st.title("SNEA Shoebox Editor")
    st.write("Welcome to the SNEA Online Shoebox Editor.")
    st.info("This is the main entry point.")
    
    st.subheader("Navigation")
    if st.button("Go to System Status"):
        st.switch_page("System Status")
        
    st.divider()
    st.subheader("Record Links (Examples)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Record 1"):
            st.query_params["id"] = 1
            st.switch_page("Record View")
    with col2:
        if st.button("View Record 42"):
            st.query_params["id"] = 42
            st.switch_page("Record View")
