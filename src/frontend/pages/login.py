# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
"""
def login():
    import streamlit as st
    st.title("SNEA Shoebox Editor - Login")
    
    st.write("Please sign in to access the editor.")

    if not st.user.is_logged_in:
        if st.button("Log in with GITHUB"):
            st.login()
        st.stop()

    if st.button("Log out"):
        st.logout()
    st.markdown(f"Welcome! {st.user.name}")

    # Dummy login logic
    # if st.button("Login with GitHub", icon="👤", type="primary"):
    #     st.session_state.logged_in = True
    #     st.success("Logged in successfully (dummy)!")
    #     st.rerun()
    #
    # st.divider()
    # st.info("Development Mode: Clicking 'Login with GitHub' will grant access without actual authentication.")

if __name__ == "__main__":
    login()
