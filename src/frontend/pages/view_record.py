# Copyright (c) 2026 Brothertown Language
import streamlit as st

def view_record():
    record_id = st.query_params.get("id")
    if not record_id:
        st.error("No record ID provided")
        if st.button("Back to Home"):
            st.switch_page("Home")
        return

    st.title(f"Record View: {record_id}")
    st.write(f"Displaying details for record ID: {record_id}")
    
    # Placeholder for DB fetch
    st.info(f"In a future update, this will pull record {record_id} from the database.")
    
    if st.button("Back to Home"):
        st.switch_page("Home")
