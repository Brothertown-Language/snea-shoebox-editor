# Copyright (c) 2026 Brothertown Language
import streamlit as st
import os
from pathlib import Path

def main():
    st.set_page_config(page_title="SNEA Mock Viewer", layout="wide")

    # Get the directory of the current script
    mock_dir = Path(__file__).parent
    
    # Discover all .py files in the directory, excluding this file
    this_file = Path(__file__).name
    mock_files = sorted([f for f in mock_dir.glob("*.py") if f.name != this_file])
    
    if not mock_files:
        st.error(f"No mocks found in {mock_dir}")
        return

    # Create a mapping of display names to file paths
    mock_options = {f.stem.replace('_', ' ').title(): f for f in mock_files}
    
    with st.sidebar:
        st.title("SNEA Mock Viewer")
        selected_name = st.selectbox("Select Mock", list(mock_options.keys()))
        
        if st.button("Reload Mock", use_container_width=True):
            st.rerun()

        st.divider()
        st.info(f"Running: {selected_name}")

    # Run the selected mock
    selected_path = mock_options[selected_name]
    
    try:
        with open(selected_path, "r") as f:
            code = f.read()
            # Execute the mock code
            # We use a clean dictionary for globals to avoid pollution, 
            # but include streamlit so it works.
            exec(code, {"st": st, "__name__": "__main__", "__file__": str(selected_path)})
    except Exception as e:
        st.error(f"Error running mock {selected_name}: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
