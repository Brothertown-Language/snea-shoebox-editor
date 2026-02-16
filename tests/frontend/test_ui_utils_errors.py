import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from src.frontend.ui_utils import handle_ui_error

class TestUIErrorHandling(unittest.TestCase):
    def setUp(self):
        # Clear st.session_state and other mocks if needed
        pass

    @patch("src.logging_config.get_logger")
    @patch("src.database.connection.is_production")
    @patch("streamlit.error")
    def test_handle_ui_error_production(self, mock_st_error, mock_is_production, mock_get_logger):
        # Setup
        mock_is_production.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        test_exception = ValueError("Secret database path")
        user_message = "A safe message for users."
        
        # Execute
        handle_ui_error(test_exception, user_message, logger_name="test_logger")
        
        # Verify logging (Internal details SHOULD be logged)
        mock_get_logger.assert_called_with("test_logger")
        mock_logger.error.assert_called()
        log_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Secret database path", log_call_args)
        self.assertIn(user_message, log_call_args)
        
        # Verify UI (Internal details SHOULD NOT be shown)
        mock_st_error.assert_called_once_with(user_message)

    @patch("src.logging_config.get_logger")
    @patch("src.database.connection.is_production")
    @patch("streamlit.error")
    @patch("streamlit.expander")
    @patch("streamlit.info")
    def test_handle_ui_error_development(self, mock_st_info, mock_st_expander, mock_st_error, mock_is_production, mock_get_logger):
        # Setup
        mock_is_production.return_value = False
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock expander as context manager
        mock_expander_cm = MagicMock()
        mock_st_expander.return_value = mock_expander_cm
        
        test_exception = ValueError("Internal dev error")
        user_message = "Development mode message."
        
        # Execute
        handle_ui_error(test_exception, user_message, logger_name="test_logger_dev")
        
        # Verify logging
        mock_logger.error.assert_called()
        
        # Verify UI (In dev, we show an expander with details)
        mock_st_expander.assert_called_once_with(user_message, expanded=True)
        mock_st_error.assert_called()
        error_call_args = mock_st_error.call_args[0][0]
        self.assertIn("ValueError", error_call_args)
        self.assertIn("Internal dev error", error_call_args)
        mock_st_info.assert_called()

if __name__ == "__main__":
    unittest.main()
