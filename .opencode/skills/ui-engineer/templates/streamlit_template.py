# SNEA Streamlit Page Template
#
# This is a TEMPLATE file, not directly executable. Replace placeholder
# markers (<PAGE_TITLE>, <ROLE_REQUIREMENT>, etc.) with actual values.
#
# Reference: docs/ui-guidelines.md for the SNEA Sidebar Pattern

import streamlit as st

from src.frontend.ui_utils import hide_sidebar_nav


def main():
    hide_sidebar_nav()

    user_role = st.session_state.get("user_role")
    if user_role not in ("<ROLE_REQUIREMENT>",):
        st.error("You do not have permission to access this page. <ROLE_DESCRIPTION> role required.")
        return

    with st.sidebar:
        st.header("<PAGE_TITLE>")

        # <SIDEBAR_FILTERS> — page-specific filters, selectors, settings

        if st.button("← Back to Main Menu"):
            st.switch_page("Home.py")

    # Main panel — data display and primary interactions
    st.markdown("### <PAGE_TITLE>")

    # <DATA_DISPLAY_AREA> — primary content using st.dataframe, st.columns, etc.

    # <PER_RECORD_CONTROLS> — inline with data, not in sidebar or global toolbar

    # Status feedback — use st.status() or st.toast() for non-blocking messages
    # with st.status("<STATUS_MESSAGE>", expanded=False) as status:
    #     st.write("<STATUS_DETAIL>")
    #     status.update(label="<STATUS_LABEL>", state="complete")


if __name__ == "__main__":
    main()
