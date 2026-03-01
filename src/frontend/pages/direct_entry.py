# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
import datetime
from src.services.upload_service import UploadService
from src.services.linguistic_service import LinguisticService
from src.services.navigation_service import NavigationService
from src.services.identity_service import IdentityService
from src.services.preference_service import PreferenceService
from src.mdf.parser import parse_mdf
from src.frontend.ui_utils import apply_standard_layout_css
from src.logging_config import get_logger

logger = get_logger("snea.direct_entry")

def direct_entry():
    apply_standard_layout_css()
    
    st.title("Direct Record Entry")
    st.markdown("""
    Enter MDF records manually below. Each field can contain one or more records.
    Multiple records in a single field will be automatically split using the `\\lx` marker.
    """)

    # --- Sidebar Configuration ---
    st.sidebar.header("Configuration")
    
    # 1. Source Selection
    sources = LinguisticService.get_sources_with_counts()
    source_names = [s['name'] for s in sources]
    
    # Try to find user's default source
    user_email = st.session_state.get("user_email")
    github_username = IdentityService.get_github_username(user_email)
    default_index = 0
    if github_username and github_username in source_names:
        default_index = source_names.index(github_username)
    
    selected_source_name = st.sidebar.selectbox(
        "Source",
        options=source_names,
        index=default_index,
        help="Select the source for these records. Defaults to your linguist source."
    )
    selected_source_id = next(s['id'] for s in sources if s['name'] == selected_source_name)

    # 2. Number of Fields
    if "num_fields" not in st.session_state and user_email:
        saved_num = PreferenceService.get_preference(user_email, "direct_entry", "num_fields", "1")
        st.session_state.num_fields = int(saved_num)
    
    if "num_fields" not in st.session_state:
        st.session_state.num_fields = 1

    num_fields = st.sidebar.number_input(
        "Number of input fields", 
        min_value=1, 
        max_value=20, 
        value=st.session_state.num_fields,
        key="num_fields_input"
    )
    
    if num_fields != st.session_state.num_fields:
        st.session_state.num_fields = num_fields
        if user_email:
            PreferenceService.set_preference(user_email, "direct_entry", "num_fields", str(num_fields))
        st.rerun()

    # --- Main Input Form ---
    # We use a helper list to initialize text_area values to avoid modifying widget state after instantiation
    current_entries = []
    for i in range(num_fields):
        # We use a different key prefix for the source of truth to avoid conflict with widget keys
        state_key = f"direct_entry_val_{i}"
        val = st.session_state.get(state_key, "")
        current_entries.append(val)

    with st.form("direct_entry_form", clear_on_submit=False):
        entries_text = []
        for i in range(num_fields):
            # Widget key is separate from our state key
            text = st.text_area(f"Record(s) {i+1}", height=150, key=f"entry_widget_{i}", value=current_entries[i])
            entries_text.append(text)
        
        submit_col1, submit_col2 = st.columns([1, 4])
        with submit_col1:
            submitted = st.form_submit_button("Submit Records", type="primary")

    if submitted:
        all_parsed_records = []
        errors = [] # List of error messages for fields that failed validation
        is_all_valid = True
        
        # 1. Pre-validate ALL fields
        for i, text in enumerate(entries_text):
            # Sync the session state values to reflect what the user typed in the widgets
            st.session_state[f"direct_entry_val_{i}"] = text
            
            if not text.strip():
                continue
                
            # Validation A: Must start with \lx (ignoring whitespace and blank lines at the top)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if not lines or not lines[0].startswith("\\lx "):
                error_msg = f"Field {i+1} must start with the required `\\lx` marker."
                errors.append(error_msg)
                is_all_valid = False
                continue

            # Validation B: Check for \lemma records
            if "\\lemma " in text:
                error_msg = f"Field {i+1} contains invalid `\\lemma` marker. Please use `\\se` for sub-entries or `\\lx` to start a new separate record."
                errors.append(error_msg)
                is_all_valid = False
                continue

            try:
                # Basic dry-run parse to ensure it's valid MDF
                records = parse_mdf(text)
                if not records:
                    error_msg = f"Field {i+1} could not be parsed as valid MDF."
                    errors.append(error_msg)
                    is_all_valid = False
            except Exception as e:
                error_msg = f"Error in field {i+1}: {str(e)}"
                errors.append(error_msg)
                is_all_valid = False

        # 2. If ALL are valid (and there's something to stage), proceed with staging
        if is_all_valid:
            # Re-parse to collect all records
            for text in entries_text:
                if text.strip():
                    all_parsed_records.extend(parse_mdf(text))

            if all_parsed_records:
                try:
                    # Prepare batch metadata
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    batch_name = f"Direct Entry - {timestamp}"
                    user_email = st.session_state.get("user_email", "unknown")
                    
                    # Stage entries for review
                    batch_id = UploadService.stage_entries(
                        entries=all_parsed_records,
                        source_id=selected_source_id,
                        filename=batch_name,
                        user_email=user_email
                    )
                    
                    if batch_id:
                        # Clear all fields for clean state upon successful staging
                        for i in range(num_fields):
                            st.session_state[f"direct_entry_val_{i}"] = ""
                            try:
                                st.session_state[f"entry_widget_{i}"] = ""
                            except Exception:
                                pass
                            
                        st.session_state.review_batch_id = batch_id
                        st.switch_page(NavigationService.PAGE_UPLOAD)
                    else:
                        st.error("Failed to create upload batch.")
                except Exception as e:
                    st.error(f"Failed to stage records: {e}")
                    logger.error("Direct entry staging failed: %s", e)
            else:
                st.warning("No records were entered.")
        else:
            # 3. If any record is invalid, do NOT stage and show errors
            st.session_state.direct_entry_errors = errors
            st.rerun()

    # --- Post-Rerun Feedback ---
    if "direct_entry_success" in st.session_state:
        st.success(st.session_state.pop("direct_entry_success"))
    if "direct_entry_errors" in st.session_state:
        for error in st.session_state.pop("direct_entry_errors"):
            st.error(error)
        st.info("Submission aborted. Please fix the invalid records and re-submit.")

if __name__ == "__main__":
    direct_entry()
