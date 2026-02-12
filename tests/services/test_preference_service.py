# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
from unittest.mock import patch, MagicMock
from src.services.preference_service import PreferenceService
from src.database import UserPreference

class TestPreferenceService(unittest.TestCase):
    """Unit tests for PreferenceService."""

    @patch("src.services.preference_service.get_session")
    def test_get_preference_found(self, mock_get_session):
        # Setup mock session and record
        mock_session = MagicMock()
        mock_pref = MagicMock(spec=UserPreference)
        mock_pref.preference_value = "25"
        
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_pref
        mock_get_session.return_value = mock_session

        val = PreferenceService.get_preference("test@test.com", "view1", "key1", "default")
        
        self.assertEqual(val, "25")
        mock_session.close.assert_called_once()

    @patch("src.services.preference_service.get_session")
    def test_get_preference_not_found_returns_default(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_get_session.return_value = mock_session

        val = PreferenceService.get_preference("test@test.com", "view1", "key1", "default")
        
        self.assertEqual(val, "default")
        mock_session.close.assert_called_once()

    @patch("src.services.preference_service.get_session")
    def test_get_preference_exception_returns_default(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("DB error")
        mock_get_session.return_value = mock_session

        val = PreferenceService.get_preference("test@test.com", "view1", "key1", "default")
        
        self.assertEqual(val, "default")
        mock_session.close.assert_called_once()

    @patch("src.services.preference_service.get_session")
    def test_set_preference_update_existing(self, mock_get_session):
        mock_session = MagicMock()
        mock_pref = MagicMock(spec=UserPreference)
        
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_pref
        mock_get_session.return_value = mock_session

        success = PreferenceService.set_preference("test@test.com", "view1", "key1", "new_val")
        
        self.assertTrue(success)
        self.assertEqual(mock_pref.preference_value, "new_val")
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("src.services.preference_service.get_session")
    @patch("src.services.preference_service.UserPreference")
    def test_set_preference_insert_new(self, mock_user_pref_class, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_get_session.return_value = mock_session

        success = PreferenceService.set_preference("test@test.com", "view1", "key1", "val1")
        
        self.assertTrue(success)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("src.services.preference_service.get_session")
    def test_set_preference_exception_rolls_back(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception("Commit failed")
        mock_get_session.return_value = mock_session

        # Setup find existing to trigger commit
        mock_pref = MagicMock(spec=UserPreference)
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_pref

        success = PreferenceService.set_preference("test@test.com", "view1", "key1", "val1")
        
        self.assertFalse(success)
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
