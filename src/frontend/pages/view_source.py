# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
- Local Development: MANDATORY use of "uv run --extra local" to ensure pgserver is available.
"""
def view_source():
    import streamlit as st
    
    source_id = st.query_params.get("id")
    if not source_id:
        st.error("No source ID provided")
        if st.button("Back to Home"):
            st.switch_page("pages/index.py")
        return

    st.title(f"Source View: {source_id}")
    st.write(f"Displaying details for source ID: {source_id}")
    
    # Placeholder for DB fetch
    st.info(f"In a future update, this will pull source {source_id} from the database.")
    
    if st.button("Back to Home"):
        st.switch_page("pages/index.py")

if __name__ == "__main__":
    view_source()
