# Copyright (c) 2026 Brothertown Language
import streamlit as st

def login():
    st.title("SNEA Shoebox Editor - Login")
    
    st.write("Please sign in to access the editor.")
    
    # Dummy login logic
    if st.button("Login with GitHub", icon="👤", type="primary"):
        st.session_state.logged_in = True
        st.success("Logged in successfully (dummy)!")
        st.rerun()
    
    st.divider()
    st.info("Development Mode: Clicking 'Login with GitHub' will grant access without actual authentication.")
