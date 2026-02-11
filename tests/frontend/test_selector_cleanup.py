# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
from unittest.mock import patch, MagicMock
import streamlit as st

class TestSelectorCleanup(unittest.TestCase):
    @patch("src.database.get_session")
    @patch("streamlit.session_state", {"user_role": "editor"})
    @patch("streamlit.selectbox")
    @patch("streamlit.header")
    @patch("streamlit.file_uploader", return_value=None)
    def test_no_autoswitch_logic_remains(self, _fu, _header, mock_selectbox, mock_session):
        # 1. Setup mock sources
        src1 = MagicMock()
        src1.name = "Alpha"
        src1.id = 1
        
        mock_sess = MagicMock()
        mock_sess.query.return_value.order_by.return_value.all.return_value = [src1]
        mock_session.return_value = mock_sess
        
        # 2. Simulate state that would have triggered auto-switch
        # Previously, newly_created_source_name would be used to override the selection.
        st.session_state["newly_created_source_name"] = "Beta"
        st.session_state["upload_active_source_name"] = "+ Add new source…"
        
        from src.frontend.pages.upload_mdf import upload_mdf
        
        # We need to capture what index is passed to st.selectbox
        mock_selectbox.return_value = "+ Add new source…"
        upload_mdf()
        
        args, kwargs = mock_selectbox.call_args
        index = kwargs.get("index")
        options = args[1]
        
        # Beta is NOT in options because it's not in our mock DB yet, 
        # but the point is we want to see if it even TRIED to select it.
        # In the new simplified logic, it should just look at upload_active_source_name.
        
        # Index of "+ Add new source…" in ["Select a source...", "Alpha", "+ Add new source…"] is 2.
        self.assertEqual(index, 2, f"Should remain on current selection (+ Add new source…), got index {index}")
        
        # newly_created_source_name should NOT have been popped because the logic is gone
        self.assertIn("newly_created_source_name", st.session_state)

if __name__ == "__main__":
    unittest.main()
