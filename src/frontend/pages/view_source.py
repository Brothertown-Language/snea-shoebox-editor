# Copyright (c) 2026 Brothertown Language
import streamlit as st

def view_source():
    source_id = st.query_params.get("id")
    if not source_id:
        st.error("No source ID provided")
        if st.button("Back to Home"):
            st.switch_page("Home")
        return

    st.title(f"Source View: {source_id}")
    st.write(f"Displaying details for source ID: {source_id}")
    
    # Placeholder for DB fetch
    st.info(f"In a future update, this will pull source {source_id} from the database.")
    
    if st.button("Back to Home"):
        st.switch_page("Home")
